#!/bin/bash

echo "Ubuntu 24.04 (Noble Numbat) Setup Script"
set -e

# Update and upgrade
sudo apt update -y
sudo apt upgrade -y

# Enable 32-bit architecture
sudo dpkg --add-architecture i386

# Install Pritunl client
sudo tee /etc/apt/sources.list.d/pritunl.list << EOF
deb https://repo.pritunl.com/stable/apt noble main
EOF
sudo apt --assume-yes install gnupg
gpg --keyserver hkp://keyserver.ubuntu.com --recv-keys 7568D9BB55FF9E5287D586017AE645C0CF8E292A
gpg --armor --export 7568D9BB55FF9E5287D586017AE645C0CF8E292A | sudo tee /etc/apt/trusted.gpg.d/pritunl.asc
sudo apt update
sudo apt install pritunl-client-electron -y

# Install Wine
sudo mkdir -pm755 /etc/apt/keyrings
sudo wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
sudo wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/noble/winehq-noble.sources

# Install Google Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
sudo wget -O- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor | sudo tee /usr/share/keyrings/google-chrome.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list

# Update and install packages
sudo apt update
sudo apt install --install-recommends winehq-stable -y || {
    echo "Failed to install winehq-stable. Trying to install wine-stable..."
    sudo apt install wine-stable -y
}
sudo apt install google-chrome-stable -y
sudo apt install git gnome-tweaks curl mc eom -y

# Install Snap packages
sudo snap install telegram-desktop
sudo snap install discord
sudo snap install code --classic

# Install language packs
sudo apt install language-pack-gnome-uk language-pack-gnome-ru -y
sudo update-locale "LC_ALL=ru_RU.UTF-8" "LANG=ru_RU.UTF-8" "LANGUAGE=ru_RU"
sudo apt install $(check-language-support) -y

# Configure keyboard shortcuts and input sources
sudo sed -i '/<name>switch-input-source<\/name>/,/<\/property>/ s|<default>\[.*\]</default>|<default>['\''<Alt>Shift_L'\'']</default>|' /usr/share/glib-2.0/schemas/org.gnome.desktop.wm.keybindings.gschema.xml
sudo sed -i '/<key name="sources">/,/<\/key>/ s|<default>.*</default>|<default>[('\''xkb'\'', '\''us'\''), ('\''xkb'\'', '\''ru'\''), ('\''xkb'\'', '\''ua'\'')]</default>|' /usr/share/glib-2.0/schemas/org.gnome.desktop.input-sources.gschema.xml

# Update favorite apps
sudo sed -i 's|favorite-apps=.*|favorite-apps=['\''ubiquity.desktop'\'', '\''thunderbird.desktop'\'', '\''google-chrome.desktop'\'', '\''org.gnome.Nautilus.desktop'\'', '\''libreoffice-writer.desktop'\'', '\''pritunl-client-electron.desktop'\'', '\''telegram-desktop_telegram-desktop.desktop'\'']|' /usr/share/glib-2.0/schemas/10_ubuntu-settings.gschema.override

# Compile schemas
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

# Modify PolicyKit rules
sudo sed -i '/modify.system/,/^$/ {/<allow_active>/,/<\/allow_active>/ s|auth_admin_keep|yes|}' /usr/share/polkit-1/actions/org.freedesktop.NetworkManager.policy
sudo sed -i '/all-edit/,/^$/ {/<allow_active>/,/<\/allow_active>/ s|auth_admin_keep|yes|}' /usr/share/polkit-1/actions/org.opensuse.cupspkhelper.mechanism.policy

# Enable firewall
sudo ufw enable

# Clean up
sudo apt autoremove -y

# Display system information
hostnamectl

#again!
echo "Ubuntu 24.04 (Noble Numbat) Setup Script"
set -e

# ... (предыдущая часть скрипта остается без изменений)

# Настройка раскладки клавиатуры и переключения языка
gsettings set org.gnome.desktop.input-sources sources "[('xkb', 'us'), ('xkb', 'ru'), ('xkb', 'ua')]"
gsettings set org.gnome.desktop.wm.keybindings switch-input-source "['<Alt>Shift_L']"
gsettings set org.gnome.desktop.wm.keybindings switch-input-source-backward "['<Shift>Alt_L']"

# Убедимся, что настройки применяются для всех пользователей
sudo tee /usr/share/glib-2.0/schemas/90_custom-keyboard-layout.gschema.override << EOF
[org.gnome.desktop.input-sources]
sources=[('xkb', 'us'), ('xkb', 'ru'), ('xkb', 'ua')]

[org.gnome.desktop.wm.keybindings]
switch-input-source=['<Alt>Shift_L']
switch-input-source-backward=['<Shift>Alt_L']
EOF

# Компилируем схемы
sudo glib-compile-schemas /usr/share/glib-2.0/schemas/

# ... (остальная часть скрипта остается без изменений)

# Перезагрузка GNOME Shell (это работает только в X11 сессии, не в Wayland)
if [ "$XDG_SESSION_TYPE" = "x11" ]; then
    echo "Перезагрузка GNOME Shell..."
    killall -SIGQUIT gnome-shell
else
    echo "Вы используете Wayland. Пожалуйста, выйдите из системы и войдите снова, чтобы изменения вступили в силу."
fi

# Display system information
hostnamectl