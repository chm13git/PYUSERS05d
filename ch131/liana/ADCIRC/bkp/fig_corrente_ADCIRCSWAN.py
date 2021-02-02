#!/home/operador/anaconda3/envs/auxdechycom/bin/python
# -*- coding: utf-8 -*-
# -*- coding: iso-8859-1 -*-

# =================================================================>
# Script que gera as figuras de corrente do experimento ADCIRC+SWAN.
# Resolucao: 1/24 grau.
#
# Autoras: 1T (T) LIANA
#	       1T (RM2-T) ANDRESSA D'AGOSTINI
#
# Exemplo: python fig_corrente_ADCIRCSWAN.py year mon day
#		   python fig_corrente_ADCIRCSWAN.py 2020 05 17 curr
# =================================================================>

# IMPORTACAO DE BIBLIOTECAS E DEFINICAO DE DIRETORIOS:
import datetime, time
import os, sys, shutil
import numpy as np
import numpy as np
import matplotlib as mpl
#mpl.use('Agg') # Force matplotlib to not use any Xwindows backend.
import matplotlib.pylab as plab
import matplotlib.pyplot as plt
import scipy
import os
import warnings
warnings.filterwarnings("ignore")
from netCDF4 import Dataset
from numpy import ma
from ww3Funcs import alteraStr, alteraDia, horarios
from mpl_toolkits.basemap import Basemap


year = sys.argv[1]
mon  = sys.argv[2]
day  = sys.argv[3]
#data = horarios('20190314')
data = horarios('{0}{1}{2}'.format(year, mon, day))
base = datetime.date(int(data[0]),int(data[1]),int(data[2]))
# ~ numdays   = 20
numdays   = 2
date_list = [base + datetime.timedelta(days=x) for x in range(0, numdays)]
datai = date_list[0];  datai=datai.strftime('%Y%m%d')
dataf = date_list[-1]; dataf=dataf.strftime('%Y%m%d')
prog  = numdays*8

# =============================================================>
# DADOS FORNECIDOS PELO USUARIO:

# Lista de variaveis a serem utilizadas:
# (Os comentarios representam os produtos que as utilizam.)
nome      = 'Correntes' 
# ~ lat_sul   = '-23.042'
# ~ lat_norte = '-22.995'
# ~ lon_oeste = '-43.317'
# ~ lon_leste = '-43.266'
# ~ pNome1    = 'Praia da Joatinga'
# ~ plon1     = '-43.2903'
# ~ plat1     = '-23.0144'
skip      = 35
# =============================================================>


# Criando arrays de datas e prog para as figuras
tit_horas=['00','06','12','18']

# ----------------------------------------
# Extraindo as variaveis do ADCIRC

## CORRENTE SUPERFICIAL
if sys.argv[4] == "curr":
	print('Plotando --> Correntes superficiais')
	for dd in range(0,numdays):
	   aux    = date_list[dd]
	   dt     = aux.strftime('%Y%m%d')
	   DIR    = '/mnt/nfs/dpns32/data1/operador/Aplicativos_REMO/ADCIRC/adcirc_novacomp/adcircswan_BG_operacional/'+dt+'/'
	   # ~ nc_f   = DIR+'ADCIRC_BG_uv_'+dt+'_graderegular.nc'
	   nc_f   = DIR+'ADCSWAN_BG_uv_'+dt+'.nc'
	   nc_fid = Dataset(nc_f, 'r')
	   lat    = nc_fid.variables['lat'][:]
	   lon    = nc_fid.variables['lon'][:]
	   lat_sul   = np.nanmin(lat) #'-23.042'
	   lat_norte = np.nanmax(lat) #'-22.995'
	   lon_oeste = np.nanmin(lon) #'-43.317'
	   lon_leste = np.nanmax(lon) #'-43.266'
	   lat_s  = float(lat_sul)
	   lat_n  = float(lat_norte)
	   lat_media = -((-lat_s)+(-lat_n))/2
	   lat_media = str(lat_media)
	   u    = nc_fid.variables['u'][0:48,:,:]
	   v    = nc_fid.variables['v'][0:48,:,:]
	   u    = np.squeeze(u); v  = np.squeeze(v)
	   u0   = np.copy(u);    v0 = np.copy(v)  
	   tmax = np.size(u[:,0,0])

	   ttt = 0   
	   for ii in range(0,tmax,12):
		   print('-----------------------------------------')
		   print(' Processando figura da data:',(dt+tit_horas[ttt]))
		   print('-----------------------------------------')
		   uu = (u0[ii,:,:]); uu = np.squeeze(uu)
		   vv = (v0[ii,:,:]); vv = np.squeeze(vv)

		   # Retirando flags
		   for i in range(0,1298):
			   for j in range(0,1335):
				   if uu[i,j]>1.0e+5: 					   
					   uu[i,j]=np.nan
				   if vv[i,j]>1.0e+5:
					   vv[i,j]=np.nan
	#      M = np.sqrt(uu**2+vv**2) # magnitude correntes m/s  
		   M = np.sqrt(uu**2+vv**2)*1.94384 # magnitude correntes nós 
		   U = np.zeros((1298,1335))
		   V = np.zeros((1298,1335))
		   for i in range(0,1298):
			   for j in range(0,1335):
				   try:
					   U[i,j] = uu[i,j]/M[i,j]
					   V[i,j] = vv[i,j]/M[i,j]
				   except:
					   pass

		   fig = plt.figure() 
		   m   = Basemap(projection='merc',llcrnrlat=lat_s,urcrnrlat=lat_n,\
		   llcrnrlon = float(lon_oeste),urcrnrlon=float(lon_leste),lat_ts=float(lat_media),resolution='h')
		   x,y   = m(lon,lat)
	 #      cores=scipy.linspace(0,0.25,num=9)
		   cores = np.linspace(0,0.4,num=9)
		   CS    = m.contourf(x,y,M,levels=cores,cmap=plt.cm.Blues)

		   # Opções de formatação do mapa
		   m.drawcoastlines(linewidth=0.5, color='k')
		   m.fillcontinents(color='gray')
		   m.drawparallels(np.arange(float(lat_sul),  float(lat_norte),0.10), labels=[1,0,0,0],fmt='%g')
		   m.drawmeridians(np.arange(float(lon_oeste),float(lon_leste),0.16), labels=[0,0,0,1])    

		   # Incluindo os vetores de corrente na figura
		   Q    = m.quiver(x[::skip, ::skip], y[::skip, ::skip], U[::skip, ::skip], V[::skip, ::skip], scale=4, units='inches', scale_units='inches', width=0.008, headlength=5, headwidth=3.5,headaxislength=5, pivot='tail', color='k', minshaft=2, minlength=1)
		   plt.title('ADCIRC+SWAN CHM/REMO '+dt+' '+tit_horas[ttt]+'Z') 
		   cbar = plt.colorbar(CS, format='%.2f')
	 #     cbar.ax.set_ylabel('corrente [m/s]')
		   cbar.ax.set_ylabel('corrente [n'u'ós]')
	#      plt.savefig('/home/operador/AuxDec_HYCOM/corrente_hycom/Fig_HYCOM_manual/Figuras_ADCIRC/ADCIRC_'+nome+'_'+dt+'_'+tit_horas[ttt]+'Z.png')
	#      plt.savefig('/home/operador/AuxDec_HYCOM/corrente_hycom/Fig_HYCOM_manual/Figuras_ADCIRC/ADCIRC_'+nome+'_nos_'+dt+'_'+tit_horas[ttt]+'Z.png')
		   plt.savefig('/home/pyusers/ch131/liana/ADCIRC/figuras_ADCIRC/ADCSWAN_'+nome+'_nos_'+dt+'_'+tit_horas[ttt]+'Z.png')

		   ttt=ttt+1
		   plt.show()
		   plt.close()

elif sys.argv[4] == "hs":
	print('Plotando --> Hs')
	for dd in range(0,numdays):
	   aux    = date_list[dd]
	   dt     = aux.strftime('%Y%m%d')
	   DIR    = '/mnt/nfs/dpns32/data1/operador/Aplicativos_REMO/ADCIRC/adcirc_novacomp/adcircswan_BG_operacional/'+dt+'/'
	   nc_f   = DIR+'ADCIRC_BG_uv_'+dt+'_graderegular.nc'
#ADCSWAN_BG_hs_20200518.nc
	   nc_fid = Dataset(nc_f, 'r')
	   lat    = nc_fid.variables['lat'][:]
	   lon    = nc_fid.variables['lon'][:]
	   
	   lat_sul   = np.nanmin(lat) #'-23.042'
	   lat_norte = np.nanmax(lat) #'-22.995'
	   lon_oeste = np.nanmin(lon) #'-43.317'
	   lon_leste = np.nanmax(lon) #'-43.266'

	   lat_s  = float(lat_sul)
	   lat_n  = float(lat_norte)
	   lat_media = -((-lat_s)+(-lat_n))/2
	   lat_media = str(lat_media)
	   u    = nc_fid.variables['u'][0:48,:,:]
	   v    = nc_fid.variables['v'][0:48,:,:]
	   u    = np.squeeze(u); v  = np.squeeze(v)
	   u0   = np.copy(u);    v0 = np.copy(v)  
	   tmax = np.size(u[:,0,0])

	   ttt = 0   
	   for ii in range(0,tmax,12):
		   print('-----------------------------------------')
		   print(' Processando figura da data:',(dt+tit_horas[ttt]))
		   print('-----------------------------------------')
		   uu = (u0[ii,:,:]); uu = np.squeeze(uu)
		   vv = (v0[ii,:,:]); vv = np.squeeze(vv)
		   # Retirando flags
		   for i in range(0,1298):
			   for j in range(0,1335):
				   if uu[i,j]>1.0e+5: 					   
					   uu[i,j]=np.nan
				   if vv[i,j]>1.0e+5:
					   vv[i,j]=np.nan

	#      M = np.sqrt(uu**2+vv**2) # magnitude correntes m/s  
		   M = np.sqrt(uu**2+vv**2)*1.94384 # magnitude correntes nós 
		   U = np.zeros((1298,1335))
		   V = np.zeros((1298,1335))
		   for i in range(0,1298):
			   for j in range(0,1335):
				   try:
					   U[i,j] = uu[i,j]/M[i,j]
					   V[i,j] = vv[i,j]/M[i,j]
				   except:
					   pass

		   fig = plt.figure() 
		   # ~ m   = Basemap(projection='merc',llcrnrlat=float(lat_sul),urcrnrlat=float(lat_norte),\
		   # ~ llcrnrlon = float(lon_oeste),urcrnrlon=float(lon_leste),lat_ts=float(lat_media),resolution='h')
		   m   = Basemap(projection='merc',llcrnrlat=lat_s,urcrnrlat=lat_n,\
		   llcrnrlon = float(lon_oeste),urcrnrlon=float(lon_leste),lat_ts=float(lat_media),resolution='h')
		   # ~ x,y   = m(lons,lats)
		   x,y   = m(lon,lat)
	 #      cores=scipy.linspace(0,0.25,num=9)
		   cores = np.linspace(0,0.4,num=9)
		   CS    = m.contourf(x,y,M,levels=cores,cmap=plt.cm.Blues)
		   # Opções de formatação do mapa
		   m.drawcoastlines(linewidth=0.5, color='k')
		   m.fillcontinents(color='gray')
		   m.drawparallels(np.arange(float(lat_sul),  float(lat_norte),0.10), labels=[1,0,0,0],fmt='%g')
		   m.drawmeridians(np.arange(float(lon_oeste),float(lon_leste),0.16), labels=[0,0,0,1])    
		   # Incluindo os vetores de corrente na figura
		   Q   = m.quiver(x[::skip, ::skip], y[::skip, ::skip], U[::skip, ::skip], V[::skip, ::skip], scale=4, units='inches', scale_units='inches', width=0.008, headlength=5, headwidth=3.5,headaxislength=5, pivot='tail', color='k', minshaft=2, minlength=1)
		   # ~ A,B = m(float(plon1), float(plat1))
		   # ~ m.plot(A, B, 'k*', markersize=10)
		   # ~ plt.text(A,B,' '+pNome1+'', ha='left', color='k')
		   plt.title('ADCIRC+SWAN CHM/REMO '+dt+' '+tit_horas[ttt]+'Z') 
		   #plt.hold(True)
		   cbar = plt.colorbar(CS, format='%.2f')
	 #     cbar.ax.set_ylabel('corrente [m/s]')
		   cbar.ax.set_ylabel('corrente [n'u'ós]')
	#      plt.savefig('/home/operador/AuxDec_HYCOM/corrente_hycom/Fig_HYCOM_manual/Figuras_ADCIRC/ADCIRC_'+nome+'_'+dt+'_'+tit_horas[ttt]+'Z.png')
	#      plt.savefig('/home/operador/AuxDec_HYCOM/corrente_hycom/Fig_HYCOM_manual/Figuras_ADCIRC/ADCIRC_'+nome+'_nos_'+dt+'_'+tit_horas[ttt]+'Z.png')
		   plt.savefig('/home/pyusers/ch131/liana/ADCIRC/figuras_ADCIRC/ADCSWAN_'+nome+'_nos_'+dt+'_'+tit_horas[ttt]+'Z.png')

		   ttt=ttt+1
		   # ~ plt.show()
		   plt.close()


	
quit()
