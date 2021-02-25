#!/home/pyusers/anaconda3/envs/s111/bin/python
# -*- coding: utf-8 -*-
# -*- coding: iso-8859-1 -*-

# ==============================================================================================> 
#
# Script para converter os dados .nc do HYCOM no formato S111 (.h5) usando a versão nova da NOAA
# Autor: 1T (T) Liana
# Criado em: 18FEV021
# Ultima atualizacao: 25FEV2021
# 
# ==============================================================================================>

from s100py import s111
from netCDF4 import Dataset
from datetime import timedelta
import os, sys, shutil
import datetime
import numpy as np
import warnings
warnings.filterwarnings("ignore")
os.environ['PROJ_LIB']  = '/home/pyusers/anaconda3/envs/s111/share/proj/'
os.environ['GDAL_DATA'] = '/home/pyusers/anaconda3/envs/s111/share/'


### Data
if len(sys.argv)==4: # usuário entra com a data desejada
        year  = int(sys.argv[1])
        mon   = int(sys.argv[2])
        day   = int(sys.argv[3])
else: # usuário não entra com a data desejada. roda a data corrente
        fdata = open('/home/pyusers/datas/datacorrente00')
        datacorrente = fdata.readlines()
        datacorrente = datacorrente[0][0:-1]
        year  = int(datacorrente[0:4])
        mon   = int(datacorrente[4:6])
        day   = int(datacorrente[6:])


### Diretorios
s111dir   = '/home/pyusers/ch131/liana/S111'
shapedir  = f'{s111dir}/shapes'
h5dir     = f'{s111dir}/hdf5'   
ncdir     = f'{s111dir}/netcdf' 
gtiffdir  = f'{s111dir}/geotiff'
hycomfile = f'{ncdir}/Metarea_{year}{mon:02d}{day:02d}.nc'


### Arquivo e variaveis
ncfile     = Dataset(hycomfile, 'r')
u_cor      = ncfile.variables['u'][:, 0, :, :]
v_cor      = ncfile.variables['v'][:, 0, :, :]
lat        = ncfile.variables['latitude'][:, :]
lon        = ncfile.variables['longitude'][:, :]
nx         = ncfile.variables['X'].size
ny         = ncfile.variables['Y'].size
nctime     = np.size(ncfile.variables['time'][12:-1])   # o dado é salvo a partir do dia anterior --> cortando do dia atual pra frente
speed_cor  = np.sqrt(u_cor**2+v_cor**2)*1.94384         # magnitude correntes nós 
dir_cor    = (np.arctan2(u_cor, v_cor)*(180/np.pi))+180 # direção em graus


## Datas
start_date = datetime.datetime(year, mon, day, 0, 0, 0) # dia inicial da previsão 
datelist   = []
for x in range (0, nctime, 3): # gerar dados de 3 em 3h
    datelist.append(start_date + datetime.timedelta(hours=x)) # criando lista de datas para gerar os .tiff
end_date = datelist[-1] # dia final da previsão


### Configurações
## Propriedades da grade
grid_properties = {'maxx':       np.nanmax(lon),
                   'minx':       np.nanmin(lon),
                   'miny':       np.nanmin(lat),
                   'maxy':       np.nanmax(lat),
                   'cellsize_x': 4625,
                   'cellsize_y': 4625,
                   'nx':         nx,
                   'ny':         ny}

## Metadados
metadata = {'horizontalDatumReference':      'EPSG',
            'horizontalDatumValue':          4326,
            'metadata':                      f'MD_test_s111.XML',
            'epoch': '                       G1762',
            'geographicIdentifier':          'METAREA_V',
            'speedUncertainty':              -3.0, # Default or Unknown values (original: -1.0)
            'directionUncertainty':          -1.0, # Default or Unknown values
            'verticalUncertainty':           -1.0, # Default or Unknown values
            'horizontalPositionUncertainty': -1.0, # Default or Unknown values
            'timeUncertainty':               -1.0, # Default or Unknown values
            'surfaceCurrentDepth':              0,
            'depthTypeIndex':                   2, # 'Sea surface'
            'commonPointRule':                  3, # 'high'
            'interpolationType':               10, # 'discrete'
            'typeOfCurrentData':                6, # Hydrodynamic model forecast (F)
            'methodCurrentsProduct':         'HYCOM_Hydrodynamic_Model_Forecasts',
            'datetimeOfFirstRecord':         f'{start_date}'} 


## Outros
data_coding_format = 2
update_meta        = {'dateTimeOfLastRecord': f'{end_date}',
                      'numberOfGroups':       np.size(datelist),
                      'numberOfTimes':        np.size(datelist),
                      'timeRecordInterval':   1440, # in seconds
                      'num_instances':        1}


## Criando arquivo .h5 vazio para preencher com os dados
data_file = s111.utils.create_s111(f"{h5dir}/S111BR_{year}{mon:02d}{day:02d}T00Z_HYCOM_TYP2.h5")


### Convertendo para o formato S111
print('Convertendo para S111...')
s111.utils.add_metadata(metadata, data_file)

for speed, direction, datetime_value in zip(speed_cor, dir_cor, datelist):
    s111.utils.add_data_from_arrays(speed, direction, data_file, grid_properties, datetime_value, data_coding_format)
s111.utils.update_metadata(data_file, grid_properties, update_meta)
s111.utils.write_data_file(data_file)

print('HYCOM model to S111 --> ok')


### Convertendo para GeoTIFF
print('Making GeoTIFF...')
s111.utils.to_geotiff(f"{h5dir}", f"{gtiffdir}")

print('Making GeoTIFF      --> ok')

