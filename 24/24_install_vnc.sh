#!/bin/bash
#Usage: sudo ./install_vnc.sh username
echo "Вибери номери VPN-профілів, які наявні у користувача:
	1) admins;
	2) employees;
	3) managers;
	4) partners-piastrix;
	5) partners-support;
	6) piastrix-walletreg;
	7) partners-other;
	8) IntraAccess;
	9) LawVpn;
	10) Remed."
read -p "Номери через пробіл: " -a vpns

# Используем tigervnc-standalone-server вместо tigervnc-scraping-server
sudo apt-get install tigervnc-standalone-server -y
mkdir -p /home/$1/.vnc
yes "Con3T1g)
Con3T1g)
n"S | vncpasswd /home/$1/.vnc/passwd
chown -R $1:$1 /home/$1/.vnc

# Проверяем наличие директории Videos или её локализованных версий
if [ -d "/home/$1/Videos" ]; then
  cp *_sharing.sh /home/$1/Videos
  chown $1:$1 /home/$1/Videos/*_sharing.sh
  chmod u+x /home/$1/Videos/*_sharing.sh
elif [ -d "/home/$1/Видео" ]; then
  cp *_sharing.sh /home/$1/Видео
  chown $1:$1 /home/$1/Видео/*_sharing.sh
  chmod u+x /home/$1/Видео/*_sharing.sh
else
  cp *_sharing.sh /home/$1/Відео
  chown $1:$1 /home/$1/Відео/*_sharing.sh
  chmod u+x /home/$1/Відео/*_sharing.sh
fi

# Остальная часть скрипта остается без изменений
for id in ${vpns[@]} 
do
	case "$id" in 
		1)
		  sudo ufw allow from 192.168.236.0/24 to any port 5900
		  sudo ufw allow from 192.168.247.0/24 to any port 5900
		  sudo ufw allow from 192.168.236.0/24 to any port 22
		  sudo ufw allow from 192.168.247.0/24 to any port 22
		  echo "Admins додано"
		  ;;
		# ... (остальные case statements остаются без изменений)
	esac
done

# Проверяем, используется ли GDM3 или другой дисплейный менеджер
if [ -f "/etc/gdm3/custom.conf" ]; then
    sudo sed -i 's/#WaylandEnable=false/WaylandEnable=false/g' /etc/gdm3/custom.conf
elif [ -f "/etc/gdm/custom.conf" ]; then
    sudo sed -i 's/#WaylandEnable=false/WaylandEnable=false/g' /etc/gdm/custom.conf
fi

echo "Для коректної роботи потрібно перезавантажити ПК"