############################################################################################
## Programa para plotar resultados de direcao de onda e altura significativa da rodada do modelo ADCIRC+SWAN
# Desenvolvido por Flavia Previero (Oceanografa) # flaviapreviero@gmail.com
# Este programa pertence a REMO e ao Centro de Hidrografia da Marinha
############################################################################################
# para rodar ---  pyenv shell anaconda3-2018.12
###			ipython plota_dir.py YYYYMMDD
# as figuras ficam salvas na pasta da data selecionada 
##############################
from IPython import get_ipython
## Limpar workspace ##########
get_ipython().magic('reset -sf')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.io import netcdf
import netCDF4
from datetime import datetime
import os
import sys
import datetime
#os.environ['PROJ_LIB'] = '/usr/local/lib/.pyenv/versions/anaconda3-2018.12/share/proj'
os.environ['PROJ_LIB'] = '/usr/local/lib/.pyenv/versions/anaconda3-2018.12/pkgs/proj4-5.2.0-h14c3975_1001/share/proj/'
from mpl_toolkits.basemap import Basemap
plt.close('all')

data=20200605
data = int(sys.argv[1])

# este programa deve ser rodado no diretório '/data1/operador/Aplicativos_REMO/ADCIRC/adcirc_novacomp/adcircswan_BG_operacional'
# senão precisa alterar o caminho dos arquivos abaixo
swandir = netcdf.netcdf_file(str(data)+'/ADCIRC_BG_dir_'+str(data)+'_graderegular.nc','r')
swanhs  = netcdf.netcdf_file(str(data)+'/ADCIRC_BG_hs_'+str(data)+'_graderegular.nc','r')

# pegando as variaveis somente do dia atual
dire   = swandir.variables['dir'][0:48,:,:]
hs     = swanhs.variables['hs'][0:48,:,:]
lat    = swandir.variables['lat'][:]
lon    = swandir.variables['lon'][:]
horasAD= swandir.variables['time'][0:48] 

tempoAD=[]
for j in range(0,len(horasAD)):
 hora    = np.floor(horasAD[j])
 minutos = (horasAD[j]-hora)*60
 ttt1    = str(data)+str("%.2i" %hora)+str("%.2i" %minutos)
 tempoAD = np.append(tempoAD,datetime.datetime.strptime(ttt1,'%Y%m%d%H%M'))

#### limites da figura - pode ser editado...
lat_S   = -23.35
lat_N   = -22.67
lon_O   = -43.56
lon_L   = -42.7
lat_MED = -22.95
####

for i in range (0, dire.shape[0],2): # tempo = hora em hora
	print('i='+str(i))
	a = dire[i,:,:]+180
	x = np.cos(a*np.pi/180)
	y = np.sin(a*np.pi/180)

	fig, ax = plt.subplots()
	# lat_S / lat_N / lon_O / lon_L / lat_MED
	m   = Basemap(projection='merc',llcrnrlat=float(lat_S),urcrnrlat=float(lat_N),llcrnrlon=float(lon_O),urcrnrlon=float(lon_L),lat_ts=float(lat_MED),resolution='h')
	X,Y = m(lon, lat)	
	m.drawcoastlines(linewidth=0.5, color='k')
	m.fillcontinents(color='gray')
	m.drawparallels(np.arange(float(lat_S),float(lat_N),0.2), labels=[1,0,0,0],fmt='%g')
	m.drawmeridians(np.arange(float(lon_O),float(lon_L),0.2), labels=[0,0,0,1])   

	HS   = ax.contourf(X[::5,::5],Y[::5,::5],hs[i,::5,::5],cmap=plt.cm.Blues)
	cbar = plt.colorbar(HS, format='%.2f')
	cbar.ax.set_ylabel('HS [m]')
	#q = m.quiver(lon[::30,::30],lat[::30,::30],y[::30,::30],x[::30,::30],angles='xy',scale_units='xy',scale=40,width=0.0010)	
	Q    = ax.quiver(X[::30, ::30], Y[::30, ::30], y[::30, ::30], x[::30, ::30], scale=40, width=0.008, headlength=5, headwidth=3.5,headaxislength=5, pivot='tail', color='k', minshaft=2, minlength=1)	

	plt.title('ADCSWAN - DIR / HS - dia='+str(data)+' - hora='+str(horasAD[i]))
	print('hora='+str(horasAD[i]))	
	#fig.show(i)
	plt.savefig(str(data)+'/ADCSWAN_dir_hs_'+str(data)+'_'+str(horasAD[i])+'.png')
	plt.close('all')
