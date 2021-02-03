#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: iso-8859-1 -*-




#----------------------------------------------
# altera no arq escolhido (file) 
# a string velha (str1) pela string nova (str2)

def alteraStr(file,str1,str2):
 s = open(file).read()
 s = s.replace(str1, str2)
 f = open(file, 'w')
 f.write(s)
 f.close()
 return


def alteraDia(file,dataini,datai,datafim,dataf):

 s = open(file).read()
 s = s.replace('dataini', datai)
 s = s.replace('datafim', dataf)
 f = open(file, 'w')
 f.write(s)
 f.close()
 return


def verificaRod(file):
 for line in open(file):
  if 'CONFLICTING TIMES' in line:

    temp=tuple(line[1:-1].split(' '))
    datarod = temp[10]+' '+temp[12] 

    return True 



def calcFreqs(NF,fini,freq_fac):
 freq = []
 for i in range(1,NF):
  freq.append(fini*freq_fac**(i-1)) #frequencias
 return freq


def horarios(data):
 horas=[]
 ano = data[0:4]
 mes = data[4:6]
 dia = data[6:8]
 horas.append(ano)
 horas.append(mes)
 horas.append(dia)
 return horas 




# -----------------------
# ideias para desenvolver
#
#def defineDir
#def defHorarios



