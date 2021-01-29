#!/bin/bash
#
###################################################
#												  #
# Script para rodar o pos-processamento do ADCIRC #
#												  #
###################################################

HOME=/home/operador
DIR_SCRIPT=${HOME}/ftpscript
DIR_GIF=${HOME}/grads/gif/adcirc
#~ DIR_INTERNET=${HOME}/grads/gif/adcirc/internet


if [ $# -ne 3 ]; then
#~ for AREA in bg sig ssib; do
	for AREA in bg; do
		echo 'roda tudo'
		rm ${DIR_GIF}/${AREA}/*.gif
		rm ${DIR_GIF}/${AREA}/*.png

		#~ cd /home/operador/ftpscript
		cd ${DIR_SCRIPT}

		#${DIR_SCRIPT}/ftp_adcirc.py hs 48 ${AREA}
		#${DIR_SCRIPT}/ftp_adcirc.py tp 48 ${AREA}
		#${DIR_SCRIPT}/ftp_adcirc.py tmm 48 ${AREA}
		/home/pyusers/ch131/liana/ADCIRC/ftp_adcirc.py zeta 48 ${AREA}
		#${DIR_SCRIPT}/ftp_adcirc.py curr 48 ${AREA}
	done
else
	echo 'roda especifico'
	VAR=$1
	PROG=$2
	AREA=$3
	echo $VAR $PROG $AREA
	#${DIR_SCRIPT}/ftp_adcirc.py $VAR $PROG ${AREA}

fi

