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

sudo apt-get install tigervnc-scraping-server -y
mkdir -p /home/$1/.vnc
yes "Con3T1g)
Con3T1g)
n"S | vncpasswd /home/$1/.vnc/passwd
chown -R $1:$1 /home/$1/.vnc

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

for id in ${vpns[@]} 
do
	case "$id" in 
		1)
		  sudo ufw allow from 192.168.236.0/24 to any port 5900
		  sudo ufw allow from 192.168.247.0/24 to any port 5900
		  echo "Admins додано"
		  ;;
		2)
		  sudo ufw allow from 192.168.216.0/24 to any port 5900
		  sudo ufw allow from 192.168.250.0/24 to any port 5900
		  echo "Employees додано"
		  ;;
		3)
		  sudo ufw allow from 192.168.245.0/24 to any port 5900
		  sudo ufw allow from 192.168.218.0/24 to any port 5900
		  echo "Managers додано"
		  ;;
		4)
		  sudo ufw allow from 192.168.220.0/24 to any port 5900
		  sudo ufw allow from 192.168.242.0/24 to any port 5900
		  echo "Partners-piastrix додано"
		  ;;	
		5)
		  sudo ufw allow from 192.168.230.0/24 to any port 5900
		  sudo ufw allow from 192.168.241.0/24 to any port 5900
		  echo "Partners-support додано"
		  ;;	
		6)
		  sudo ufw allow from 192.168.229.0/24 to any port 5900
		  sudo ufw allow from 192.168.249.0/24 to any port 5900
		  echo "Piastrix-walletreg додано"
		  ;;
		7)
		  sudo ufw allow from 192.168.215.0/24 to any port 5900
		  sudo ufw allow from 192.168.223.0/24 to any port 5900
		  echo "Partners-other додано"
		  ;;
		8)
		  sudo ufw allow from 192.168.235.0/24 to any port 5900
		  echo "IntraAccess додано"
		  ;;
		9)
		  sudo ufw allow from 192.168.244.0/24 to any port 5900
		  echo "LawVpn додано"
		  ;;
		10)
		  sudo ufw allow from 192.168.226.0/24 to any port 5900
		  echo "Remed додано"
		  ;;
		*)
		  echo "$id - некоректне значення!"
		  ;;
	esac
done

sudo sed -i 's/#WaylandEnable=false/WaylandEnable=false/g' /etc/gdm3/custom.conf
echo -e "\033[1;31mДля коректної роботи необхідно перезавантажити ПК! \033[0m"
