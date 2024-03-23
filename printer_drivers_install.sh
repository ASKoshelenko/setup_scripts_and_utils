#!/bin/bash
loop=true
while($loop)
do
	echo "Виберiть бажаний принтер:
 	1 - Xerox 3225
 	2 - Canon MF643
	e - Щоб відмінити інсталяцію"
	read num
	case $num in
	1) ####Xerox WorkCentre 3225####
		if [ ! -d /tmp/uld/ ]
		then
			wget https://download.support.xerox.com/pub/drivers/WC3225/drivers/linux/en_GB/Xerox_WorkCentre_3225_Linux-Driver.tar.gz -P /tmp
			tar -xzf /tmp/Xerox_WorkCentre_3225_Linux-Driver.tar.gz -C /tmp/
		fi
		cd /tmp/uld/
		yes y | sudo ./install.sh
		sudo apt install libusb-0.1-4
		sudo rm /usr/lib/x86_64-linux-gnu/sane/libsane-smfp.so.1
		sudo ln -s /opt/smfp-common/scanner/lib/libsane-smfp.so.1.0.1 /usr/lib/x86_64-linux-gnu/sane/libsane-smfp.so.1
		sudo ufw allow to any port 22161
	        sudo ufw allow to any port 631
                sudo ufw allow to any port 5353 ;;
	2) ####Canon MF643Cdw####
		if [ ! -d /tmp/linux-UFRII-drv-v530-uken ]
		then
			#wget https://gdlp01.c-wss.com/gds/8/0100007658/25/linux-UFRII-drv-v540-uken-08.tar.gz -P /tmp
			tar -xzf /tmp/linux-UFRII-drv-v540-uken-08.tar.gz -C /tmp/
		fi
		cd /tmp/linux-UFRII-drv-v540-uken
		yes y | sudo ./install.sh ;; 
	e) exit 0;;
	*)
		echo "Невірний номер"
		continue ;; 
	esac
	echo 'Бажаєте інсталювати інший драйвер? (y):'
	read answ
	case $answ in
		y)continue;;
		*)loop=false;;
	esac
done
