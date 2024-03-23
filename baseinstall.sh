#!/bin/sh

echo "base"
set -e
sudo apt update -y
sudo apt upgrade -y

sudo tee /etc/apt/sources.list.d/pritunl.list << EOF
deb https://repo.pritunl.com/stable/apt jammy main
EOF

sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com --recv 7568D9BB55FF9E5287D586017AE645C0CF8E292A
sudo apt-get update
sudo apt-get install pritunl-client-electron

sudo wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo wget -O- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor | sudo tee /usr/share/keyrings/google-chrome.gpg
#sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
echo deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-cache policy shutter
sudo apt-get update
sudo apt install -y shutter
sudo apt-get install google-chrome-stable -y
sudo apt install -y git
sudo apt install -y gnome-tweaks
sudo apt install curl -y 
sudo apt install mc -y
sudo apt install eom -y
sudo snap install telegram-desktop
sudo snap install skype --classic

sudo apt-get install language-pack-gnome-uk language-pack-gnome-ru -y
#sudo update-locale "LC_ALL=uk_UA.UTF-8" "LANG=uk_UA.UTF-8" "LANGUAGE=uk_UA"
sudo update-locale "LC_ALL=ru_RU.UTF-8" "LANG=ru_RU.UTF-8" "LANGUAGE=ru_RU"
sudo apt-get install $(check-language-support) -y

sudo sed -i '335 s|CDATA\[\[|&'\''<Alt>Shift_L'\'', |' /usr/share/glib-2.0/schemas/org.gnome.desktop.wm.keybindings.gschema.xml
sudo sed -i '18 s|\[\(.*\)\]|[('\''xkb'\'', '\''us'\''), ('\''xkb'\'', '\''ru'\''), ('\''xkb'\'', '\''ua'\'')]|' /usr/share/glib-2.0/schemas/org.gnome.desktop.input-sources.gschema.xml
sudo sed -i '9 s|\[.*\]|['\''ubiquity.desktop'\'', '\''thunderbird.desktop'\'', '\''google-chrome.desktop'\'', '\''org.gnome.Nautilus.desktop'\'', '\''libreoffice-writer.desktop'\'', '\''pritunl-client-electron.desktop'\'', '\''telegram-desktop_telegram-desktop.desktop'\''] |' /usr/share/glib-2.0/schemas/10_ubuntu-settings.gschema.override
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

sudo sed -i '/modify.system/,/^$/ {/<allow_active>/,/<\/allow_active>/ s|auth_admin_keep|yes|}' /usr/share/polkit-1/actions/org.freedesktop.NetworkManager.policy
sudo sed -i '/all-edit/,/^$/ {/<allow_active>/,/<\/allow_active>/ s|auth_admin_keep|yes|}' /usr/share/polkit-1/actions/org.opensuse.cupspkhelper.mechanism.policy
sudo ufw enable

sudo apt autoremove -y
hostnamectl
