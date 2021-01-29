#!/bin/bash
#
###################################################
#						  #
# Script para rodar o pos-processamento do ADCIRC #
#						  #
###################################################

HOME=/home/operador
DIR_SCRIPT=${HOME}/ftpscript
DIR_GIF=${HOME}/grads/gif/adcirc
#~ DIR_INTERNET=${HOME}/grads/gif/adcirc/internet


if [ $# -ne 6 ]; then
for AREA in bg sig ssib; do
	rm ${DIR_GIF}/${AREA}/*.gif
	rm ${DIR_GIF}/${AREA}/*.png

	cd ${DIR_SCRIPT}

	${DIR_SCRIPT}/ftp_adcirc.py hs 24 ${AREA}
	${DIR_SCRIPT}/ftp_adcirc.py tp 24 ${AREA}
	#${DIR_SCRIPT}/ftp_adcirc.py tmm 48 ${AREA}
	#${DIR_SCRIPT}/ftp_adcirc_05e.py zeta 48 ${AREA}
	#${DIR_SCRIPT}/ftp_adcirc.py curr 48 ${AREA}
done
else
	echo 'roda especifico'
	VAR=$1
	PROG=$2
	AREA=$3
	ANO=$4
        MES=$5
        DIA=$6
        echo ${VAR} ${PROG} ${AREA} ${ANO} ${MES} ${DIA}
        ${DIR_SCRIPT}/ftp_adcirc.py ${VAR} ${PROG} ${AREA} ${ANO} ${MES} ${DIA}

fi

