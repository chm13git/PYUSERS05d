#!/bin/bash
#
#  script ledata_corr.sh
#  leitura da data-corrente
#
# ---------------------------------------------------------


## Passo 1: Verifica a hora de referencia
if [ $# -ne 1 ]
then
     echo "Entre com o horario de referencia (00 ou 12)"
     exit
fi
HH=$1


# ---------------------------------------------------------
# Passo 2: Cria arquivos
#
#~ rm -f ~/datas/datacorrente$HH
rm -f /home/pyusers/ch131/liana/ADCIRC/datas/datacorrente$HH


## le data corrente e copia para arquivo
date +%Y%m%d > /home/pyusers/ch131/liana/ADCIRC/datas/datacorrente$HH
date +%b >  /home/pyusers/ch131/liana/ADCIRC/datas/MES${HH}
date +%d >  /home/pyusers/ch131/liana/ADCIRC/datas/dia${HH}
date +%d > /home/pyusers/ch131/liana/ADCIRC/datas/diacorrente$HH
date +%j > /home/pyusers/ch131/liana/ADCIRC/datas/diaano$HH
date +%d%m%Y > /home/pyusers/ch131/liana/ADCIRC/datas/data_status$HH
#date --date='1day' +%Y%m%d > ~/datas/datacorrente_p1${HH}
#date --date='2day' +%Y%m%d > ~/datas/datacorrente_p2${HH}
#date --date='1day' +%b >  ~/datas/MES_p1${HH}
#date --date='1day' +%d >  ~/datas/dia_p1${HH}
#date --date='2day' +%b >  ~/datas/MES_p2${HH}
##date --date='2day' +%d >  ~/datas/dia_p2${HH}
cat /home/pyusers/ch131/liana/ADCIRC/datas/datacorrente$HH

export LANG=en
export LANGUAGE=en

date +%d%b%Y > /home/pyusers/ch131/liana/ADCIRC/datas/datacorrente_grads$HH

if [ $HH -eq 00 ]
then
   cp /home/pyusers/ch131/liana/ADCIRC/datas/datacorrente_grads$HH /home/pyusers/ch131/liana/ADCIRC/datas/datacorrente_grads
fi

#
# fim
