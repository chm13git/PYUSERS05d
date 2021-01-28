#!/home/pyusers/anaconda3/envs/s111/bin/python
# -*- coding: utf-8 -*-
# -*- coding: iso-8859-1 -*-

# ==================================================================> 
#
# Script para converter os dados .nc do HYCOM no formato S111 (.h5) 
# Autor: 1T (T) Liana
# Criado em: 27OUT2021
# Ultima atualizacao: 11JAN2021
# 
# ==================================================================>

from s100py import s111
from thyme.model import hycom
from netCDF4 import Dataset
import os, sys, shutil
import datetime

##########################################################################
#                                                                        #
# ESTE SCRIPT ESTÁ FUNCIONANDO APENAS PARA ARQUIVOS COM 1 PASSO DE TEMPO #
#                                                                        #
##########################################################################

# tentar gerar o index file apenas uma vez


### DATA
if len(sys.argv)==4: # usuário entra com a data desejada
        year  = int(sys.argv[1])
        mon   = int(sys.argv[2])
        day   = int(sys.argv[3])
else: # usuário não entra com a data desejada. roda a data corrente
        # ~ fdata = open('/home/operador/datas/datacorrente00')
        fdata = open('/home/pyusers/ch131/liana/ADCIRC/datas/datacorrente00')
        datacorrente = fdata.readlines()
        datacorrente = datacorrente[0][0:-1]
        year  = int(datacorrente[0:4])
        mon   = int(datacorrente[4:6])
        day   = int(datacorrente[6:])


### DIRETORIOS
s111dir  = '/home/pyusers/ch131/liana/S111'
shapedir = '{0}/shapes'.format(s111dir)
hdf5dir  = '{0}/hdf5'  .format(s111dir)
hycomdir = '{0}/netcdf'.format(s111dir)


### CARACTERISTICAS DO DADO
data_coding_format = 2    # regular grid
target_depth       = 0    # meters below sea surface (0 = at/near surface), default = 4.5 m
target_resolution  = 4625 # meters


### DEFININDO METADADO
file_metadata = s111.S111Metadata(
        "METAREA_V",                          # region
        "HYCOM_Hydrodynamic_Model_Forecasts", # product type description
        6,                                    # current data type for hydrodynamic forecast
        "BR",                                 # producer code
        None,                                 # station id
        "HYCOM")                              # model identifier


### CRIANDO INDEX FILE
try:
    # Create an index file object from the the model index file 
    model_index_file  = hycom.HYCOMIndexFile('{0}/hycom_index_file.nc'.format(s111dir)) # arquivo a ser criado (só precisa criar uma vez)

    # Create a file object from the input HYCOM model NetCDF file
    native_model_file = hycom.HYCOMFile('{0}/hycom124_{1}{2:02d}{3:02d}.nc'.format(hycomdir, year, mon, day)) # output utilizado (hycom 1/24 grade nova)
    #native_model_file = hycom.HYCOMFile('{0}/teste_s111.nc'.format(hycomdir, year, mon, day)) # output utilizado (hycom 1/24 grade nova)
    model_index_file.open()
    native_model_file.open()
    model_index_file.init_nc(native_model_file, target_resolution, 'HYCOM', '{0}/Countries_WGS84.shp'.format(shapedir)) # shape 

finally:
    native_model_file.close()
    model_index_file.close()


### CONVERTENDO PARA O FORMATO S111
s111.model_to_s111(
        model_index_file,
        [native_model_file],
        '{0}'.format(s111dir),
        datetime.datetime(year, mon, day, 0, 0),
        file_metadata,
        data_coding_format,
        target_depth)
print('s111 model to s111   --> ok')
