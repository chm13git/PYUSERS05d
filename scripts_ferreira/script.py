#!/home/operador/anaconda3/envs/oilmap/bin/python
# -*- coding: utf-8 -*-
'''
Autor: 1T (RM2-T) Ferreira
Criado em:
Modificações por:
Ultima atualizacao:
'''
# =============================================================>
# IMPORTACAO DE BIBLIOTECAS E SCRIPTS:
import os, sys
from datetime import date
import netCDF4 as nc
import xarray as xr
import warnings #***
# scripts no mesmo diretorio:
import conversor
#=============================================================

def def_read(arquivo):
    '''Leitura do arquivo txt e definicao das variaveis'''
    f     = open(arquivo, 'r', encoding = "utf8")
    x     = f.readlines()
    comissao = x[2][x[2].find('=')+1:].strip().replace(" ","")
    latn  =  float(x[3][x[3].find('=')+1:].strip())
    lats  =  float(x[4][x[4].find('=')+1:].strip())
    lone  =  float(x[5][x[5].find('=')+1:].strip())
    lonw  =  float(x[6][x[6].find('=')+1:].strip())
    level =  float(x[7][x[7].find('=')+1:].strip())
    
    # verifica se os valores foram preenchidos corretamente:
    if latn > lats:
       latmax = latn
       latmin = lats
    else:
       print(u'ERRO: Os valores da latitude estao invertidos!!!\nAtencao aos sinais das variaveis.\nO script corrigiu automaticamente!')
       latmax = lats
       latmin = latn

    if lone > lonw:
       lonmax = lone
       lonmin = lonw
    else:
       print(u'ERRO: Os valores da longitude estão invertidos!!!\nAtencao aos sinais das variaveis.\nO script corrigiu automaticamente!')
       lonmax = lonw
       lonmin = lone
 
    return comissao,latmax,latmin,lonmax,lonmin,level

def def_area(latmax,latmin,lonmax,lonmin,level):
    '''Calcula o limite das coordenadas e define qual grade do HYCOM deve utilizar'''
    # Define se a area esta dentro da nova grade 1/24 do HYCOM:
    if latmax <= 10.19576  and latmin >= -45.17722 and lonmax <= -24 and lonmin >= -68:
        subdiretorio = 'Previsao_1_24_nova/Ncdf/'#time=1 #Intervalo de 1h para cada prognostico
        if level==0:
            sufixo = '2du.nc'
        else:
            sufixo = '3zu.nc'
    # Define se a area esta dentro da nova grade 1/12 do HYCOM:
    elif latmax <= 50.27270 and latmin >= -79.54071 and lonmax <= 45 and lonmin >= -98:
        subdiretorio = 'Previsao_1_12_nova/Ncdf/'#time=12 #Intervalo de 1h para cada prognostico
        sufixo = '3zu.nc'
    else:
        print('Area fora das grades do HYCOM')
        exit()
    return  subdiretorio, sufixo

# ============================================================

# DEFINICAO DE DIRETORIOS:
diretorio = '/mnt/nfs/dpns32/data1/operador/previsao/hycom_2_2/output/' #diretorio de montagem dos dados HYCOM

# LEITURA DO ARQUIVO TXT DE CONFIGURACAO:

if len(sys.argv)  == 1:
    print(""" \n ########## ERRO:##########\nDigite o nome do arquivo txt como argumento após o script. Ex: ./scritp.py arquivo.txt \nCaso queira calcular uma data diferente da atual, digite a data no formato %YYYY%MM%DD. Ex. /scritp.py arquivo.txt 20201123 \n """)
    exit()
else:
    arquivo = sys.argv[1]

print('Lendo arquivo txt...')
comissao,latmax,latmin,lonmax,lonmin,level = def_read(arquivo) #chama funcao de leitura

print('Definindo a grade HYCOM ...')
subdiretorio, sufixo = def_area(latmax,latmin,lonmax,lonmin,level) #chama funcao de def grade

# Definicao da data:

if len(sys.argv) <= 3:
    dia = date.today() #data do dia atual
    d   = dia.strftime('%Y%m%d')
else:
    d   = sys.argv[2]

# DEFINICAO DO NOME E DIRETORIO DOS DADOS:

nome    = '{0}_{1}.nc'.format(comissao, d) # nome do arquivo final
subnome = 'archv.{0}_*_{1}'.format(dia.year, sufixo) # busca dos arquivos .nc. Ex: archv.2020_*_brt.nc
indir   = '{0}{1}{2}/'.format(diretorio, subdiretorio, d) # diretorio completo dos dados de entrada
#outdir  = '/home/pyusers/ch131/oleo/' # diretorio que salva os arquivos
outdir  = '/home/pyusers/ch131/liana/S111/netcdf/' # diretorio que salva os arquivos


# CONCATENA OS ARQUIVOS NETCDF:

print('Concatenando arquivos...')

if sufixo == '3zu.nc':
    os.system('cdo -f nc4 mergetime {0}{1} {2}concatenado.nc'.format(indir,subnome,outdir))
    os.system('cdo -v sellevel,{0} concatenado.nc arquivo.nc'.format(level))
else:
    os.system('cdo -f nc4 mergetime {0}{1} {2}arquivo.nc'.format(indir,subnome,outdir))

# CONVERTE O ARQUIVO NETCDF DA COMISSAO:

print('Convertendo o arquivo NetCDF...')

conversor.process(latmax, latmin, lonmax, lonmin, outdir, outdir, nome) #altera para formato compativel com oilmap

# FINALIZACAO DO SCRIPT
#os.system('rm concatenado.nc arquivo.nc') #apaga arquivos temporarios
quit()
