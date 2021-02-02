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
from datetime import timedelta
import os, sys, shutil, glob
import numpy as np
import datetime
import h5py

d_names  = glob.glob('S111*.h5')
d_struct = {} #Here we will store the database structure

for i in d_names:
    f = h5py.File(i,'r+')
    d_struct[i] = f.keys()
    f.close()
#print(d_struct)
#exit()
for i in d_names:
    print('i -->', i) 
    for j in d_struct[i]:
        print('j -->', j)
        os.system('h5copy -i {0} -o output.h5 -s {1} -d {1}'.format(i, j))
        #!h5copy -i '{i}' -o 'output.h5' -s {j} -d {j}
