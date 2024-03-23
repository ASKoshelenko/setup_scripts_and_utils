#!/bin/bash

set -e
sudo apt update -y
sudo apt upgrade -y

#pritunl
sudo tee /etc/apt/sources.list.d/pritunl.list << EOF
deb https://repo.pritunl.com/stable/apt jammy main
EOF

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com --recv 7568D9BB55FF9E5287D586017AE645C0CF8E292A
sudo apt-get update
sudo apt-get install pritunl-client-electron

#Wine
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/jammy/winehq-jammy.sources

#Chrome
sudo wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo wget -O- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor | sudo tee /usr/share/keyrings/google-chrome.gpg
echo deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main | sudo tee /etc/apt/sources.list.d/google-chrome.list

sudo apt-get update
sudo apt-get install google-chrome-stable -y
sudo apt install --install-recommends winehq-stable
sudo apt install -y git
sudo apt install -y gnome-tweaks
sudo apt install curl -y 
sudo apt install mc -y
sudo apt install eom -y
sudo snap install telegram-desktop
sudo snap install code --classic
sudo snap install discord

sudo apt-get install language-pack-gnome-uk language-pack-gnome-ru -y
sudo apt-get install $(check-language-support) -y
sudo ufw enable
sudo apt autoremove -y

echo "___Complete___"