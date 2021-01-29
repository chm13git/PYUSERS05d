#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- coding: iso-8859-1 -*-
# =====================================================================>
# Script que gera as figuras do modelo ADCIRC.
# Resolucao: 1/24 graus.
#
# Autora: 1T(T) LIANA
#
# Data corrente: python ftp_adcirc.py variável prognóstico_final área
#                python ftp_adcirc.py hs 48 bg
#
# Outras datas:  python ftp_adcirc.py variável prognóstico_final área ano mês dia 
#                python ftp_adcirc.py hs 48 bg 2020 05 15 
#
# variáveis: hs, tp, tmm, curr, zeta
# prognóstico_final: até 138 (saídas de 30 em 30 min; não pode ser 144 porque o último horário disponível é 23:30 e não 00:00)
# áreas: bg, sig, ssib
# =====================================================================>


# IMPORTACAO DE BIBLIOTECAS
import datetime, time
import os, sys, shutil
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
from mpl_toolkits.basemap import Basemap
from ww3Funcs import alteraStr, alteraDia, horarios


# =====================================================================>
### ARGUMENTOS
if len(sys.argv)<3:
	print('-------------------------------------------------')
	print('|     Você deve entrar com os argumentos:       |')
	print('|     variavel(hs,tp,tmm,curr,zeta), prog,      |') 
	print('|     area(bg,sig,ssib), data(OPCIONAL)         |')
	print('|                                               |')
	print('| Ex1: python ftp_adcirc.py hs 48 bg            |')
	print('| Ex2: python ftp_adcirc.py hs 48 bg 2020 08 20 |')
	print('-------------------------------------------------')
	exit()

	
### PERÍODO ESCOLHIDO
if len(sys.argv)==7: # usuário entra com a data desejada
	year  = sys.argv[4]
	mon   = sys.argv[5]
	day   = sys.argv[6]
else: # usuário não entra com a data desejada. roda a data corrente
	fdata = open('/home/operador/datas/datacorrente00')
	datacorrente = fdata.readlines()
	datacorrente = datacorrente[0][0:-1]
	year  = datacorrente[0:4]
	mon   = datacorrente[4:6]
	day   = datacorrente[6:]
data      = horarios('{0}{1}{2}'.format(year, mon, day))
base      = datetime.date(int(data[0]),int(data[1]),int(data[2]))
iprog     = 0 				 # prognostico inicial
fprog     = int(sys.argv[2]) # prognostico final
numdays   = int((fprog - iprog)/(2*24)) # número de dias (2*24 pq é de 30 em 30 min)
date_list = [base + datetime.timedelta(days=x) for x in range(0, numdays+2)] # +2 pra garantir que vai plotar o 00Z do dia seguinte
datai     = date_list[0];  datai=datai.strftime('%Y%m%d')
dataf     = date_list[-1]; dataf=dataf.strftime('%Y%m%d')


### Prognóstico final
if fprog > 138:
	print('----------------------------------------')
	print('|  O prognóstico final só vai até 138. |')
	print('|  Você deve escolher um valor menor.  |')
	print('----------------------------------------')
	exit()


# =====================================================================>
### DADOS FORNECIDOS PELO USUARIO:
## Variáveis a serem utilizadas:
dict_var  = {'hs':'Hs', 'tp':'Tp', 'tmm':'Tmm', 'zeta':'Zeta', 'curr':'Correntes'}

## Áreas a serem utilizadas:
dict_area = {'bg':'BG', 'sig':'SIG', 'ssib':'SSIB'}

## Nomes para o gráfico
dict_title_pt  = {'hs':'Alt. Sig. Ondas(m)', 'tp':'Per. Pico Ondas(seg)', 'tmm':'Per Med. Ondas(seg)', 
				  'zeta':'Nivel do Mar(m)', 'curr':'velocidade das correntes(nos)'}
dict_title_en  = {'hs':'Sig. Wave Heigth(m)', 'tp':'Wave Peak Per.(seg)',  'tmm':'Wave Avg. Per.(seg)',
				  'zeta':'Sea Level(m)', 'curr':'Currents Velocity(knots)'}
dict_title_mon = {'01':'JAN', '02':'FEV','03':'MAR', '04':'ABR', '05':'MAR', '06':'JUN', 
                  '07':'JUL', '08':'AGO','09':'SET', '10':'OUT', '11':'NOV', '12':'DEZ'}
dict_title_day = {r'Sunday':'Dom', 'Monday':'Seg', 'Tuesday':'Ter', 'Wednesday':'Qua', 'Thursday':'Qui', 'Friday':'Sex', 'Saturday':'Sab',
			      'domingo':'Dom', 'segunda':'Seg', 'terça':'Ter', 'quarta':'Qua', 'quinta':'Qui','sexta':'Sex','sábado':'Sab'}
var_cbar       = {r'hs':'altura significativa [m]', 'tp':'período de pico [s]', 'tmm':'período médio [s]', 
				  'curr':'velocidade da corrente [nos]', 'zeta':'nível do mar [m]'}
figname        = {'hs':'ondas', 'tp':'periopeak', 'tmm':'periondas', 'zeta':'nivel', 'curr':'correntes'}

## Características do gráfico
# Espaçamento do quiver 
skip = 40

# Range de valores da escala (contourf e contour)
if sys.argv[1]   == "hs":
	label_bar_cntrf = np.linspace(0,4,num=9)
	label_bar_cntr  = [0.5, 1.5, 3.0, 4.0]
elif sys.argv[1] == "tp": # não tem Dp
	label_bar_cntrf = np.linspace(4,22,num=19)
	label_bar_cntr  = [12.0, 14.0, 16.0]
elif sys.argv[1] == "tmm": 
	label_bar_cntrf = np.linspace(4,22,num=19)
	label_bar_cntr  = [12.0, 14.0, 16.0]
elif sys.argv[1] == "curr":
	label_bar_cntrf = np.linspace(0,1,num=11)
	label_bar_cntr  = [0.2, 0.5, 0.8, 1.0]
elif sys.argv[1] == "zeta":
	label_bar_cntrf = np.linspace(0,1.5,num=11)
	label_bar_cntr  = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5]

# Range de valores das coordenadas
if sys.argv[3]   == "bg":
	range_lat = 0.20
	range_lon = 0.20
	plot_area = plt.figure()
elif sys.argv[3] == "sig":
	range_lat = 0.20
	range_lon = 0.40
	plot_area = plt.figure(figsize=(8,5))
elif sys.argv[3] == "ssib":
	range_lat = 0.20
	range_lon = 0.20
	plot_area = plt.figure(figsize=(8,5))


## Diretórios 
filepath = '/mnt/nfs/dpns32/data1/operador/Aplicativos_REMO/ADCIRC/adcirc_novacomp/adcircswan_{0}_operacional/'.format(dict_area[sys.argv[3]])
adcpath  = '/home/operador/grads/gif/adcirc/'
if not os.path.exists(adcpath):			
	os.makedirs(adcpath) 


# =====================================================================>
### Plotando as variaveis do ADCIRC

## ALTURA SIGNIFICATIVA E DIREÇÃO MEDIA ================================
if sys.argv[1] == "hs":
	print('---------------------------------------')
	print('Plotando --> Altura significativa ({0})'.format(dict_area[sys.argv[3]]))
	print('---------------------------------------')
	day     = date_list[0] # dia da rodada
	dayname = day.strftime('%A') # nome do dia da semana para o dia da rodada (ex: seg, ter)

	# Arquivo de Hs
	nc_file   = filepath+datai+'/'+'ADCIRC_{0}_hs_'.format(dict_area[sys.argv[3]])+datai+'_graderegular.nc'
	nc_fid    = Dataset(nc_file, 'r')
	lat       = nc_fid.variables['lat'][:]
	lon       = nc_fid.variables['lon'][:]
	lat_sul   = np.nanmin(lat) 
	lat_norte = np.nanmax(lat) 
	lon_oeste = np.nanmin(lon) 
	lon_leste = np.nanmax(lon) 
	lat_s     = float(lat_sul)
	lat_n     = float(lat_norte)
	lat_media = -((-lat_s)+(-lat_n))/2
	lat_media = str(lat_media)
	hs        = nc_fid.variables['hs'][iprog:fprog+1,:,:] 
	hs        = np.squeeze(hs)
	
	# Arquivo de direção média de onda 
	nc_dire   = filepath+datai+'/'+'ADCIRC_{0}_dir_'.format(dict_area[sys.argv[3]])+datai+'_graderegular.nc'
	nc_fid    = Dataset(nc_dire, 'r')
	wdir      = nc_fid.variables['dir'][iprog:fprog+1,:,:]
	wdir      = 270-wdir # direção de convenção do SWAN (270-direção)
	wdir      = np.squeeze(wdir)
	u         = np.cos(wdir*np.pi/180)
	v         = np.sin(wdir*np.pi/180)

	hh=0 # HH
	dd=0 # dia do prognóstico
	for prog in range(0,fprog+1,6): # range de 6 em 6 = range de 3 em 3 horas
		print(' Processando figura da data:',datai+',', 'prog:', '{0:03d}'.format(prog), '({0:02d}Z{1})'.format(hh, date_list[dd].strftime('%Y%m%d')))
		
		# Data do prognóstico	
		dayprog     = date_list[dd] # dia do prognóstico
		dt          = dayprog.strftime('%Y%m%d')
		daynameprog = dayprog.strftime('%A') # nome do dia da semana para o dia do prognóstico (ex: seg, ter)

		# Selecionando dados para plot
		hss = (hs[prog,:,:]); hss = np.squeeze(hss)
		uu  = (u[prog,:,:]);  uu  = np.squeeze(uu)
		vv  = (v[prog,:,:]);  vv  = np.squeeze(vv)

		# Retirando flags Hs
		for i in range(0,np.shape(uu)[0]):
			for j in range(0,np.shape(uu)[1]):
				if hss[i,j]>1.0e+5:
					hss[i,j]=np.nan

		# Iniciando o plot
		fig   = plot_area 
		m     = Basemap(projection='merc', llcrnrlat=lat_s, urcrnrlat=lat_n, llcrnrlon = float(lon_oeste), urcrnrlon=float(lon_leste), lat_ts=float(lat_media), resolution='h')
		x,y   = m(lon,lat)
		
		# Linhas de contorno
		cntrf = m.contourf(x,y,hss,levels=label_bar_cntrf,cmap=plt.cm.jet)
		cntr  = m.contour(x,y,hss, levels=label_bar_cntr, colors='k')			
		plt.clabel(cntr, colors='k', fontsize=8, fmt = '%2.1f')
		
		# Destacar linha de 2.5m
		label_25 = [2.5]
		cntr25   = m.contour(x,y,hss, levels=label_25, colors='r')
		plt.clabel(cntr25, colors='r', fontsize=8, fmt = '%2.1f') 
		
		# Escala
		cbar = plt.colorbar(cntrf, format='%.2f')
		cbar.ax.set_ylabel(var_cbar[sys.argv[1]])

		# Paralelos e meridianos
		m.drawcoastlines(linewidth=0.5, color='k')
		m.fillcontinents(color='gray')
		m.drawparallels(np.arange(float(lat_sul),  float(lat_norte), range_lat), labels=[1,0,0,0],fmt='%.2f')
		m.drawmeridians(np.arange(float(lon_oeste),float(lon_leste), range_lon), labels=[0,0,0,1],fmt='%.2f')    
		
		# Incluindo os vetores de direção de onda na figura
		Q = m.quiver(x[::skip, ::skip], y[::skip, ::skip], uu[::skip, ::skip], vv[::skip, ::skip], scale=40, width=0.008, headlength=5, headwidth=3.5, headaxislength=5, pivot='tail', color='k', minshaft=2, minlength=1)
		
		# Título
		if prog == 0: # prog 00
			progname = '00Z{0}{1}{2} ({3}) - Analise'.format(datai[6:8], dict_title_mon[datai[4:6]], datai[0:4], dict_title_day[dayname])
		else:         # prog > 00
			progname = 'Ref: 00Z{0}{1}{2} ({3}) +PROG{4:02d}/Val:{5:02d}Z{6}{7}{8} ({9}) '.format(datai[6:8], dict_title_mon[datai[4:6]], datai[0:4], dict_title_day[dayname], 
																						   prog, hh, dt[6:8], dict_title_mon[dt[4:6]], dt[0:4], dict_title_day[daynameprog]) 
		plt.title('MODELO ADCIRC/SWAN - '+'{0} '.format(dict_title_pt[sys.argv[1]])+' - ADCIRC/SWAN Model - '+ \
				  '{0} \n'.format(dict_title_en[sys.argv[1]]) + progname, fontsize=8)
		
		# Salvando as figuras
		figpath = os.path.join(adcpath, sys.argv[3]) 
		if not os.path.exists(figpath):			
			os.makedirs(figpath) 
		figpng = '{0}/{1}_{2}'.format(figpath, figname[sys.argv[1]], '{0:03d}.png'.format(prog))
		figgif = '{0}/{1}_{2}'.format(figpath, figname[sys.argv[1]], '{0:03d}.gif'.format(prog))
		convert_fig = '/usr/bin/convert {0} {1}'.format(figpng, figgif) # converter .png em .gif
		plt.savefig(figpng, dpi=300)
		os.system(convert_fig) # converter .png em .gif
		plt.close()
		# ~ plt.show()
		
		hh=hh+3
		if hh==24:  # hh = 24h --> muda o dia
			hh=0    # zera a contagem dos prognósticos do dia
			dd=dd+1 # muda de dia



## PERÍODO DE PICO =====================================================
elif sys.argv[1] == "tp":
	print()
	print('----------------------------------')
	print('Plotando --> Periodo de pico ({0})'.format(dict_area[sys.argv[3]]))
	print('----------------------------------')
	day     = date_list[0]  # dia da rodada
	dayname = day.strftime('%A') # nome do dia da semana para o dia da rodada (ex: seg, ter)

	# Arquivo de Tp
	nc_file   = filepath+datai+'/'+'ADCIRC_{0}_tps_'.format(dict_area[sys.argv[3]])+datai+'_graderegular.nc'
	nc_fid    = Dataset(nc_file, 'r')
	lat       = nc_fid.variables['lat'][:]
	lon       = nc_fid.variables['lon'][:]
	lat_sul   = np.nanmin(lat) 
	lat_norte = np.nanmax(lat) 
	lon_oeste = np.nanmin(lon) 
	lon_leste = np.nanmax(lon) 
	lat_s     = float(lat_sul)
	lat_n     = float(lat_norte)
	lat_media = -((-lat_s)+(-lat_n))/2
	lat_media = str(lat_media)
	tp        = nc_fid.variables['tps'][iprog:fprog+1,:,:] 
	tp        = np.squeeze(tp)

	hh=0 # HH
	dd=0 # dia do prognóstico
	for prog in range(0,fprog+1,6): # range de 6 em 6 = range de 3 em 3 horas
		print(' Processando figura da data:',datai+',', 'prog:', '{0:03d}'.format(prog), '({0:02d}Z{1})'.format(hh, date_list[dd].strftime('%Y%m%d')))
		
		# Data do prognóstico	
		dayprog     = date_list[dd] # dia do prognóstico
		dt          = dayprog.strftime('%Y%m%d')
		daynameprog = dayprog.strftime('%A') # nome do dia da semana para o dia do prognóstico (ex: seg, ter)

		# Selecionando dados para plot
		tpp = (tp[prog,:,:]); tpp = np.squeeze(tpp)

		# Retirando flags Tp
		for i in range(0,np.shape(tpp)[0]):
			for j in range(0,np.shape(tpp)[1]):
				if tpp[i,j]>1.0e+5:
					tpp[i,j]=np.nan

		# Iniciando o plot
		fig   = plot_area 
		m     = Basemap(projection='merc', llcrnrlat=lat_s, urcrnrlat=lat_n, llcrnrlon = float(lon_oeste), urcrnrlon=float(lon_leste), lat_ts=float(lat_media), resolution='h')
		x,y   = m(lon,lat)
		
		# Linhas de contorno
		cntrf = m.contourf(x,y,tpp,levels=label_bar_cntrf,cmap=plt.cm.jet)
		cntr  = m.contour(x,y,tpp, levels=label_bar_cntr, colors='k')			
		plt.clabel(cntr, colors='k', fontsize=8, fmt = '%2.1f')
		
		# Escala
		cbar = plt.colorbar(cntrf, format='%.2f')
		cbar.ax.set_ylabel(var_cbar[sys.argv[1]])

		# Paralelos e meridianos
		m.drawcoastlines(linewidth=0.5, color='k')
		m.fillcontinents(color='gray')
		m.drawparallels(np.arange(float(lat_sul),  float(lat_norte), range_lat), labels=[1,0,0,0],fmt='%.2f')
		m.drawmeridians(np.arange(float(lon_oeste),float(lon_leste), range_lon), labels=[0,0,0,1],fmt='%.2f')    
		
		# Título
		if prog == 0: # prog 00
			progname = '00Z{0}{1}{2} ({3}) - Analise'.format(datai[6:8], dict_title_mon[datai[4:6]], datai[0:4], dict_title_day[dayname])
		else:         # prog > 00
			progname = 'Ref: 00Z{0}{1}{2} ({3}) +PROG{4:02d}/Val:{5:02d}Z{6}{7}{8} ({9}) '.format(datai[6:8], dict_title_mon[datai[4:6]], datai[0:4], dict_title_day[dayname], 
																						   prog, hh, dt[6:8], dict_title_mon[dt[4:6]], dt[0:4], dict_title_day[daynameprog]) 
		plt.title('MODELO ADCIRC/SWAN - '+'{0} '.format(dict_title_pt[sys.argv[1]])+' - ADCIRC/SWAN Model - '+ \
				  '{0} \n'.format(dict_title_en[sys.argv[1]]) + progname, fontsize=8)
		
		# Salvando as figuras
		figpath = os.path.join(adcpath, sys.argv[3]) 
		if not os.path.exists(figpath):			
			os.makedirs(figpath) 
		figpng = '{0}/{1}_{2}'.format(figpath, figname[sys.argv[1]], '{0:03d}.png'.format(prog))
		figgif = '{0}/{1}_{2}'.format(figpath, figname[sys.argv[1]], '{0:03d}.gif'.format(prog))
		convert_fig = '/usr/bin/convert {0} {1}'.format(figpng, figgif) # converter .png em .gif
		plt.savefig(figpng, dpi=300)
		os.system(convert_fig) # converter .png em .gif
		plt.close()
		# ~ plt.show()
		
		hh=hh+3
		if hh==24:  # hh = 24h --> muda o dia
			hh=0    # zera a contagem dos prognósticos do dia
			dd=dd+1 # muda de dia



## PERÍODO MÉDIO =======================================================
elif sys.argv[1] == "tmm":
	print()
	print('---------------------------------')
	print(r'Plotando --> Periodo médio ({0})'.format(dict_area[sys.argv[3]]))
	print('---------------------------------')
	day     = date_list[0]  # dia da rodada
	dayname = day.strftime('%A') # nome do dia da semana para o dia da rodada (ex: seg, ter)

	# Arquivo de Tmm
	nc_file   = filepath+datai+'/'+'ADCIRC_{0}_tmm10_'.format(dict_area[sys.argv[3]])+datai+'_graderegular.nc'
	nc_fid    = Dataset(nc_file, 'r')
	lat       = nc_fid.variables['lat'][:]
	lon       = nc_fid.variables['lon'][:]
	lat_sul   = np.nanmin(lat) 
	lat_norte = np.nanmax(lat) 
	lon_oeste = np.nanmin(lon) 
	lon_leste = np.nanmax(lon) 
	lat_s     = float(lat_sul)
	lat_n     = float(lat_norte)
	lat_media = -((-lat_s)+(-lat_n))/2
	lat_media = str(lat_media)
	tm        = nc_fid.variables['tmm10'][iprog:fprog+1,:,:] 
	tm        = np.squeeze(tm)

	# Arquivo de direção média de onda 
	nc_dire   = filepath+datai+'/'+'ADCIRC_{0}_dir_'.format(dict_area[sys.argv[3]])+datai+'_graderegular.nc'
	nc_fid    = Dataset(nc_dire, 'r')
	wdir      = nc_fid.variables['dir'][iprog:fprog+1,:,:]
	wdir      = 270-wdir # direção de convenção do SWAN (270-direção)
	wdir      = np.squeeze(wdir)
	u         = np.cos(wdir*np.pi/180)
	v         = np.sin(wdir*np.pi/180)

	hh=0 # HH
	dd=0 # dia do prognóstico
	for prog in range(0,fprog+1,6): # range de 6 em 6 = range de 3 em 3 horas
		print(' Processando figura da data:',datai+',', 'prog:', '{0:03d}'.format(prog), '({0:02d}Z{1})'.format(hh, date_list[dd].strftime('%Y%m%d')))
		
		# Data do prognóstico	
		dayprog     = date_list[dd] # dia do prognóstico
		dt          = dayprog.strftime('%Y%m%d')
		daynameprog = dayprog.strftime('%A') # nome do dia da semana para o dia do prognóstico (ex: seg, ter)

		# Selecionando dados para plot
		tmm = (tm[prog,:,:]); tmm = np.squeeze(tmm)
		uu  = (u[prog,:,:]);  uu  = np.squeeze(uu)
		vv  = (v[prog,:,:]);  vv  = np.squeeze(vv)

		# Retirando flags Tmm
		for i in range(0,np.shape(uu)[0]):
			for j in range(0,np.shape(uu)[1]):
				if tmm[i,j]>1.0e+5:
					tmm[i,j]=np.nan

		# Iniciando o plot
		fig   = plot_area 
		m     = Basemap(projection='merc', llcrnrlat=lat_s, urcrnrlat=lat_n, llcrnrlon = float(lon_oeste), urcrnrlon=float(lon_leste), lat_ts=float(lat_media), resolution='h')
		x,y   = m(lon,lat)
		
		# Linhas de contorno
		cntrf = m.contourf(x,y,tmm,levels=label_bar_cntrf,cmap=plt.cm.jet)
		cntr  = m.contour(x,y,tmm, levels=label_bar_cntr, colors='k')			
		plt.clabel(cntr, colors='k', fontsize=8, fmt = '%2.1f')

		# Escala
		cbar = plt.colorbar(cntrf, format='%.2f')
		cbar.ax.set_ylabel(var_cbar[sys.argv[1]])

		# Paralelos e meridianos
		m.drawcoastlines(linewidth=0.5, color='k')
		m.fillcontinents(color='gray')
		m.drawparallels(np.arange(float(lat_sul),  float(lat_norte), range_lat), labels=[1,0,0,0],fmt='%.2f')
		m.drawmeridians(np.arange(float(lon_oeste),float(lon_leste), range_lon), labels=[0,0,0,1],fmt='%.2f')    
		
		# Incluindo os vetores de direção de onda na figura
		Q = m.quiver(x[::skip, ::skip], y[::skip, ::skip], uu[::skip, ::skip], vv[::skip, ::skip], scale=40, width=0.008, headlength=5, headwidth=3.5, headaxislength=5, pivot='tail', color='k', minshaft=2, minlength=1)
		
		# Título
		if prog == 0: # prog 00
			progname = '00Z{0}{1}{2} ({3}) - Analise'.format(datai[6:8], dict_title_mon[datai[4:6]], datai[0:4], dict_title_day[dayname])
		else:         # prog > 00
			progname = 'Ref: 00Z{0}{1}{2} ({3}) +PROG{4:02d}/Val:{5:02d}Z{6}{7}{8} ({9}) '.format(datai[6:8], dict_title_mon[datai[4:6]], datai[0:4], dict_title_day[dayname], 
																						   prog, hh, dt[6:8], dict_title_mon[dt[4:6]], dt[0:4], dict_title_day[daynameprog]) 
		plt.title('MODELO ADCIRC/SWAN - '+'{0} '.format(dict_title_pt[sys.argv[1]])+' - ADCIRC/SWAN Model - '+ \
				  '{0} \n'.format(dict_title_en[sys.argv[1]]) + progname, fontsize=8)
		
		# Salvando as figuras
		figpath = os.path.join(adcpath, sys.argv[3]) 
		if not os.path.exists(figpath):			
			os.makedirs(figpath) 
		figpng = '{0}/{1}_{2}'.format(figpath, figname[sys.argv[1]], '{0:03d}.png'.format(prog))
		figgif = '{0}/{1}_{2}'.format(figpath, figname[sys.argv[1]], '{0:03d}.gif'.format(prog))
		convert_fig = '/usr/bin/convert {0} {1}'.format(figpng, figgif) # converter .png em .gif
		plt.savefig(figpng, dpi=300)
		os.system(convert_fig) # converter .png em .gif
		plt.close()
		# ~ plt.show()
		
		hh=hh+3
		if hh==24:  # hh = 24h --> muda o dia
			hh=0    # zera a contagem dos prognósticos do dia
			dd=dd+1 # muda de dia



## CORRENTE SUPERFICIAL ================================================
elif sys.argv[1] == "curr":
	print()
	print('------------------------------------------')
	print(r'Plotando --> Correntes superficiais ({0})'.format(dict_area[sys.argv[3]]))
	print('------------------------------------------')
	day     = date_list[0]  # dia da rodada
	dayname = day.strftime('%A') # nome do dia da semana para o dia da rodada (ex: seg, ter)

	# Arquivo de correntes superficiais 
	nc_cur    = filepath+datai+'/'+'ADCIRC_{0}_uv_'.format(dict_area[sys.argv[3]])+datai+'_graderegular.nc'
	nc_fid    = Dataset(nc_cur, 'r')
	lat       = nc_fid.variables['lat'][:]
	lon       = nc_fid.variables['lon'][:]
	lat_sul   = np.nanmin(lat) 
	lat_norte = np.nanmax(lat) 
	lon_oeste = np.nanmin(lon) 
	lon_leste = np.nanmax(lon) 
	lat_s     = float(lat_sul)
	lat_n     = float(lat_norte)
	lat_media = -((-lat_s)+(-lat_n))/2
	lat_media = str(lat_media)
	u         = nc_fid.variables['u'][iprog:fprog+1,:,:]
	v         = nc_fid.variables['v'][iprog:fprog+1,:,:] 
	u         = np.squeeze(u); v  = np.squeeze(v)

	hh=0 # HH
	dd=0 # dia do prognóstico
	for prog in range(0,fprog+1,6): # range de 6 em 6 = range de 3 em 3 horas
		print(' Processando figura da data:',datai+',', 'prog:', '{0:03d}'.format(prog), '({0:02d}Z{1})'.format(hh, date_list[dd].strftime('%Y%m%d')))
		# Data do prognóstico	
		dayprog     = date_list[dd] # dia do prognóstico
		dt          = dayprog.strftime('%Y%m%d')
		daynameprog = dayprog.strftime('%A') # nome do dia da semana para o dia do prognóstico (ex: seg, ter)

		# Selecionando dados para plot
		uu = (u[prog,:,:]); uu = np.squeeze(uu)
		vv = (v[prog,:,:]); vv = np.squeeze(vv)

		# Retirando flags
		for i in range(0,np.shape(uu)[0]):
		   for j in range(0,np.shape(uu)[1]):
			   if uu[i,j]>1.0e+5: 					   
				   uu[i,j]=np.nan
			   if vv[i,j]>1.0e+5:
				   vv[i,j]=np.nan
		# ~ M = np.sqrt(uu**2+vv**2)     # magnitude correntes m/s  
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

		# Iniciando o plot
		fig   = plot_area 
		m     = Basemap(projection='merc', llcrnrlat=lat_s, urcrnrlat=lat_n, llcrnrlon = float(lon_oeste), urcrnrlon=float(lon_leste), lat_ts=float(lat_media), resolution='h')
		x,y   = m(lon,lat)
		
		# Linhas de contorno
		cntrf = m.contourf(x,y,M,levels=label_bar_cntrf,cmap=plt.cm.jet)
		cntr  = m.contour(x,y,M, levels=label_bar_cntr, colors='k')			
		plt.clabel(cntr, colors='k', fontsize=8, fmt = '%2.1f')

		# Escala
		cbar = plt.colorbar(cntrf, format='%.2f')
		cbar.ax.set_ylabel(var_cbar[sys.argv[1]])

		# Paralelos e meridianos
		m.drawcoastlines(linewidth=0.5, color='k')
		m.fillcontinents(color='gray')
		m.drawparallels(np.arange(float(lat_sul),  float(lat_norte), range_lat), labels=[1,0,0,0],fmt='%.2f')
		m.drawmeridians(np.arange(float(lon_oeste),float(lon_leste), range_lon), labels=[0,0,0,1],fmt='%.2f')     

		# Incluindo os vetores de corrente na figura
		Q = m.quiver(x[::skip, ::skip], y[::skip, ::skip], U[::skip, ::skip], V[::skip, ::skip], scale=4, units='inches', scale_units='inches', width=0.008, headlength=5, headwidth=3.5,headaxislength=5, pivot='tail', color='k', minshaft=2, minlength=1)
		
		# Título
		if prog == 0: # prog 00
			progname = '00Z{0}{1}{2} ({3}) - Analise'.format(datai[6:8], dict_title_mon[datai[4:6]], datai[0:4], dict_title_day[dayname])
		else:         # prog > 00
			progname = 'Ref: 00Z{0}{1}{2} ({3}) +PROG{4:02d}/Val:{5:02d}Z{6}{7}{8} ({9}) '.format(datai[6:8], dict_title_mon[datai[4:6]], datai[0:4], dict_title_day[dayname], 
																						   prog, hh, dt[6:8], dict_title_mon[dt[4:6]], dt[0:4], dict_title_day[daynameprog]) 
		plt.title('MODELO ADCIRC/SWAN - '+'{0} '.format(dict_title_pt[sys.argv[1]])+' - ADCIRC/SWAN Model - '+ \
				  '{0} \n'.format(dict_title_en[sys.argv[1]]) + progname, fontsize=8)
		
		# Salvando as figuras
		figpath = os.path.join(adcpath, sys.argv[3]) 
		if not os.path.exists(figpath):			
			os.makedirs(figpath) 
		figpng = '{0}/{1}_{2}'.format(figpath, figname[sys.argv[1]], '{0:03d}.png'.format(prog))
		figgif = '{0}/{1}_{2}'.format(figpath, figname[sys.argv[1]], '{0:03d}.gif'.format(prog))
		convert_fig = '/usr/bin/convert {0} {1}'.format(figpng, figgif) # converter .png em .gif
		plt.savefig(figpng, dpi=300)
		os.system(convert_fig) # converter .png em .gif
		plt.close()
		# ~ plt.show()
		
		hh=hh+3
		if hh==24:  # hh = 24h --> muda o dia
			hh=0    # zera a contagem dos prognósticos do dia
			dd=dd+1 # muda de dia



## NÍVEL DO MAR ========================================================
elif sys.argv[1] == "zeta":
	print()
	print('--------------------------------')
	print(r'Plotando --> Nível do mar ({0})'.format(dict_area[sys.argv[3]]))
	print('--------------------------------')
	day     = date_list[0]  # dia da rodada
	dayname = day.strftime('%A') # nome do dia da semana para o dia da rodada (ex: seg, ter)
	
	# Arquivo de zeta
	nc_file   = filepath+datai+'/'+'ADCIRC_{0}_zeta_'.format(dict_area[sys.argv[3]])+datai+'_graderegular.nc'
	nc_fid    = Dataset(nc_file, 'r')
	lat       = nc_fid.variables['lat'][:]
	lon       = nc_fid.variables['lon'][:]
	lat_sul   = np.nanmin(lat) 
	lat_norte = np.nanmax(lat) 
	lon_oeste = np.nanmin(lon) 
	lon_leste = np.nanmax(lon) 
	lat_s     = float(lat_sul)
	lat_n     = float(lat_norte)
	lat_media = -((-lat_s)+(-lat_n))/2
	lat_media = str(lat_media)
	zeta      = nc_fid.variables['zeta'][iprog:fprog+1,:,:] 
	zeta      = np.squeeze(zeta)

	hh=0 # HH
	dd=0 # dia do prognóstico
	for prog in range(0,fprog+1,6): # range de 6 em 6 = range de 3 em 3 horas
		print(' Processando figura da data:',datai+',', 'prog:', '{0:03d}'.format(prog), '({0:02d}Z{1})'.format(hh, date_list[dd].strftime('%Y%m%d')))
		
		# Data do prognóstico	
		dayprog     = date_list[dd] # dia do prognóstico
		dt          = dayprog.strftime('%Y%m%d')
		daynameprog = dayprog.strftime('%A') # nome do dia da semana para o dia do prognóstico (ex: seg, ter)

		# Selecionando dados para plot
		zetaa = (zeta[prog,:,:]); zetaa = np.squeeze(zetaa)

		# Retirando flags zeta
		for i in range(0,np.shape(zetaa)[0]):
			for j in range(0,np.shape(zetaa)[1]):
				if zetaa[i,j]>1.0e+5:
					zetaa[i,j]=np.nan

		# Iniciando o plot
		fig   = plot_area 
		m     = Basemap(projection='merc', llcrnrlat=lat_s, urcrnrlat=lat_n, llcrnrlon = float(lon_oeste), urcrnrlon=float(lon_leste), lat_ts=float(lat_media), resolution='h')
		x,y   = m(lon,lat)
		
		# Linhas de contorno
		cntrf     = m.contourf(x,y,zetaa,levels=label_bar_cntrf,cmap=plt.cm.jet)
		cntr      = m.contour(x,y,zetaa,levels=label_bar_cntr, colors='k')			
		plt.clabel(cntr, colors='k', fontsize=8, fmt = '%2.1f')

		# Escala
		cbar = plt.colorbar(cntrf, format='%.2f')
		cbar.ax.set_ylabel(var_cbar[sys.argv[1]])

		# Paralelos e meridianos
		m.drawcoastlines(linewidth=0.5, color='k')
		m.fillcontinents(color='gray')
		m.drawparallels(np.arange(float(lat_sul),  float(lat_norte), range_lat), labels=[1,0,0,0],fmt='%.2f')
		m.drawmeridians(np.arange(float(lon_oeste),float(lon_leste), range_lon), labels=[0,0,0,1],fmt='%.2f')      
		
		# Título
		if prog == 0: # prog 00
			progname = '00Z{0}{1}{2} ({3}) - Analise'.format(datai[6:8], dict_title_mon[datai[4:6]], datai[0:4], dict_title_day[dayname])
		else:         # prog > 00
			progname = 'Ref: 00Z{0}{1}{2} ({3}) +PROG{4:02d}/Val:{5:02d}Z{6}{7}{8} ({9}) '.format(datai[6:8], dict_title_mon[datai[4:6]], datai[0:4], dict_title_day[dayname], 
																						   prog, hh, dt[6:8], dict_title_mon[dt[4:6]], dt[0:4], dict_title_day[daynameprog]) 
		plt.title('MODELO ADCIRC/SWAN - '+'{0} '.format(dict_title_pt[sys.argv[1]])+' - ADCIRC/SWAN Model - '+ \
				  '{0} \n'.format(dict_title_en[sys.argv[1]]) + progname, fontsize=8)
		
		# Salvando as figuras
		figpath = os.path.join(adcpath, sys.argv[3]) 
		if not os.path.exists(figpath):			
			os.makedirs(figpath) 
		figpng = '{0}/{1}_{2}'.format(figpath, figname[sys.argv[1]], '{0:03d}.png'.format(prog))
		figgif = '{0}/{1}_{2}'.format(figpath, figname[sys.argv[1]], '{0:03d}.gif'.format(prog))
		convert_fig = '/usr/bin/convert {0} {1}'.format(figpng, figgif) # converter .png em .gif
		plt.savefig(figpng, dpi=300)
		os.system(convert_fig) # converter .png em .gif
		plt.close()
		# ~ plt.show()
		
		hh=hh+3
		if hh==24:  # hh = 24h --> muda o dia
			hh=0    # zera a contagem dos prognósticos do dia
			dd=dd+1 # muda de dia


quit()
