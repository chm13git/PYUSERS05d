#!/home/operador/anaconda3/envs/oilmap/bin/python
# -*- coding: utf-8 -*-

# Convert REMO HYCOM to OilMap format.
# Author: Marcelo Andrioni
# v1: 2019-10-31
#########/usr/bin/env python3
# from IPython import embed as keyboard
import numpy as np
import pandas as pd
import netCDF4 as nc
import xarray as xr


class VarMeta:
    """
    Variable Metadata.
    Attributes
    ----------
    name : str
        Variable name.
    attrs : dict, optional
        Attributes of the variable.
    encoding: dict, optional
        Encoding of the variable.
    """

    def __init__(self, name, attrs, encoding):

        self.name = name
        self.attrs = attrs
        self.encoding = encoding


def vars_metadata():

    vsm = []

    # time
    # ATTENTION: if 'units': 'hours since 1970-01-01T00:00:00Z' xarray/nc
    #            writes the file as "hours since 2001-01-01T00:00:00+00:00"
    #            following ISO 8601 format. But this format is not recognized
    #            by OilMap so it should not be used. Valid OilMap formats are:
    #            yyyy-mm-dd, yyyy-mm-dd HH:MM, etc

    # MT
    vsm.append(VarMeta(
        'time',
        {'long_name': 'time', 'standard_name': 'time', 'axis': 'T',
         '_CoordinateAxisType': 'Time'},
        {'dtype': 'f4', '_FillValue': None,
         'units': 'hours since 1970-01-01 00:00:00'}))

    # date - array (S111)
    vsm.append(VarMeta(
        'Date',
        {'long_name': 'date', 'standard_name': 'date',
         '_CoordinateAxisType': 'Time'},
        {'dtype': 'f4', '_FillValue': None,
         'units': 'day as %Y%m%d.%f'}))

    # depth
    vsm.append(VarMeta(
        'depth',
        {'long_name': 'depth', 'standard_name': 'depth', 'axis': 'Z',
         'positive': 'down', '_CoordinateAxisType': 'Height',
         '_CoordinateZisPositive': 'down', 'units': 'm'},
        {'dtype': 'f4', '_FillValue': None}))
    
    # longitude - array (S111)
    vsm.append(VarMeta(
        'X',
        {'long_name': 'longitude_X', 'standard_name': 'LX', 'axis': 'X',
        '_CoordinateAxisType': 'Lon','units': 'degrees_north'},
        {'dtype': 'f4', '_FillValue': None}))

    # latitude - array (S111)
    vsm.append(VarMeta(
        'Y',
        {'long_name': 'latitude_Y', 'standard_name': 'LY', 'axis': 'Y',
        '_CoordinateAxisType': 'Lat','units': 'degrees_north'},
        {'dtype': 'f4', '_FillValue': None}))

    # latitude - grad (oilmap)
    vsm.append(VarMeta(
        'latitude',
        {'long_name': 'latitude', 'standard_name': 'latitude',
         'axis': 'Y', '_CoordinateAxisType': 'Lat', 'units': 'degrees_north'},
        {'dtype': 'f4', '_FillValue': None}))

    # longitude - grad (oilmap)
    vsm.append(VarMeta(
        'longitude',
        {'long_name': 'longitude', 'standard_name': 'longitude',
         'axis': 'X', '_CoordinateAxisType': 'Lon', 'units': 'degrees_east'},
        {'dtype': 'f4', '_FillValue': None}))

    # current u
    vsm.append(VarMeta(
        'u',
        {'long_name': 'u component of current',
         'standard_name': 'eastward_sea_water_velocity',
         'units': 'm s-1',
         'coordinates': 'time depth latitude longitude'},
        {'dtype': 'i2', '_FillValue': nc.default_fillvals['i2'],
         'scale_factor': 0.001, 'add_offset': 0.0}))

    # current v
    vsm.append(VarMeta(
        'v',
        {'long_name': 'v component of current',
         'standard_name': 'northward_sea_water_velocity',
         'units': 'm s-1',
         'coordinates': 'time depth latitude longitude'},
        {'dtype': 'i2', '_FillValue': nc.default_fillvals['i2'],
         'scale_factor': 0.001, 'add_offset': 0.0}))

    return vsm


def process(latmax, latmin, lonmax, lonmin, indir, outdir, nome):

    # -------------------------------------------------------------------------
    # user input:
    infile  = indir + 'arquivo.nc'
    outfile = outdir + nome # --------------

    # select geographic region:

    lat = slice(latmin, latmax) # ---- corta para a area de interesse - latitude definida na entrada 
    lon = slice(lonmin, lonmax) # ---- corta para a area de interesse - longitude definida na entrada

    # -------------------------------------------------------------------------
    
    ds = xr.open_dataset(infile, drop_variables='Date')

    s0 = list(set(list(ds.dims)).intersection(['MT','Time','time']))
    s1 = list(set(list(ds.dims)).intersection(['Layer','layer','Depth','depth']))
    s2 = list(set(list(ds.dims)).intersection(['Latitude','latitude','lat','y']))
    s3 = list(set(list(ds.dims)).intersection(['Longitude','longitude','lon','x']))
    s4 = list(set(list(ds.data_vars)).intersection(['u_velocity','U','u']))
    s5 = list(set(list(ds.data_vars)).intersection(['v_velocity','V','v']))

    ds = ds.rename({s0[0]: 'time',
                    s1[0]: 'depth',
                    s2[0]: 'Y',
                    s3[0]: 'X',
                    s4[0]: 'u',
                    s5[0]: 'v'})

    dss = ds.sel(Y = lat, X = lon) # ===== ENTRADA DOS VALORES DE LAT/LON DA GRADE ==== #

    # lon,lat must be 2d
    mlon, mlat = np.meshgrid(dss['X'], dss['Y'])

    dss['latitude']  = (('Y', 'X'), mlat)
    dss['longitude'] = (('Y', 'X'), mlon)

    # replace layer value with depth = surface = 0.0m
    #dss['depth'].values = [0.0]

    vsm = vars_metadata() # ===== ENTRADA DA FUNCAO ANTERIOR ==== #

    for vm in vsm:
        dss[vm.name].attrs = vm.attrs
        dss[vm.name].encoding = vm.encoding

    dss.attrs = {}

    dss = dss[[vm.name for vm in vsm]]
    

    # time as unlimited
    dss.encoding['unlimited_dims'] = 'time'

    # size of outfile
    # must be NETCDF3_CLASSIC less than 2GB
    # size * 2 variables (u and v) * 2 bytes (encoding 'dtype': 'i2')
    size = np.r_[dss['u'].shape]
    if (size.prod() * 2 * 2) > (2 * 1024**3):
        raise ValueError('Outfile will be greater than 2GB.')

    dt_start = pd.to_datetime(dss['time'].min().values).strftime('%Y%m%d')
    dt_end   = pd.to_datetime(dss['time'].max().values).strftime('%Y%m%d')

    outfile  = outfile.format(dt_start=dt_start, dt_end=dt_end)
    #print(f'Outfile: {outfile}')
    print(dss)
    dss.to_netcdf(outfile, format = 'NETCDF3_CLASSIC')


if __name__ == "__main__":# ==== TESTA SE O SCRIPT FOI IMPORTADO COMO MODULO ===
    process()
