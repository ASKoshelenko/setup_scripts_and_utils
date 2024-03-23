#!/bin/bash
#Для моделей ноутів: HP 15s-eq0056ur, HP 15s-eq0073ur
#!!! Якщо нижчеперераховані пакети ставилися раніше,
# і потрібно лише оновити драйвер для нової версії ядра, то
# цей скріпт не використовуємо, а
# завантажуєм останню версію драйвера: git clone https://github.com/tomaspinho/rtl8821ce
# заходим в директорію: cd rtl8821ce
# видаляємо старий драйвер: ./dkms-remove.sh
# перевсталовлюєм ./dkms-install.sh
sudo dpkg -i binutils-common_2.34-6ubuntu1_amd64.deb
sudo dpkg -i libbinutils_2.34-6ubuntu1_amd64.deb
sudo dpkg -i libctf-nobfd0_2.34-6ubuntu1_amd64.deb
sudo dpkg -i libctf0_2.34-6ubuntu1_amd64.deb
sudo dpkg -i binutils-x86-64-linux-gnu_2.34-6ubuntu1_amd64.deb
sudo dpkg -i binutils_2.34-6ubuntu1_amd64.deb
sudo dpkg -i gcc-9-base_9.3.0-17ubuntu1~20.04_amd64.deb
sudo dpkg -i gcc-10-base_10.2.0-5ubuntu1~20.04_amd64.deb
sudo dpkg -i libitm1_10.2.0-5ubuntu1~20.04_amd64.deb
sudo dpkg -i liblsan0_10.2.0-5ubuntu1~20.04_amd64.deb
sudo dpkg -i libquadmath0_10.2.0-5ubuntu1~20.04_amd64.deb
sudo dpkg -i libtsan0_10.2.0-5ubuntu1~20.04_amd64.deb
sudo dpkg -i libubsan1_10.2.0-5ubuntu1~20.04_amd64.deb
sudo dpkg -i libatomic1_10.2.0-5ubuntu1~20.04_amd64.deb
sudo dpkg -i libasan5_9.3.0-17ubuntu1~20.04_amd64.deb
sudo dpkg -i libgcc-9-dev_9.3.0-17ubuntu1~20.04_amd64.deb
sudo dpkg -i gcc-9-base_9.3.0-17ubuntu1~20.04_amd64.deb
sudo dpkg -i cpp-9_9.3.0-17ubuntu1~20.04_amd64.deb
sudo dpkg -i gcc-9_9.3.0-17ubuntu1~20.04_amd64.deb
sudo dpkg -i gcc_4%3a9.3.0-1ubuntu2_amd64.deb
sudo dpkg -i make_4.2.1-1.2_amd64.deb
sudo dpkg -i dpkg-dev_1.19.7ubuntu3_all.deb
sudo dpkg -i dkms_2.8.1-5ubuntu1_all.deb
sudo dpkg -i module-assistant_0.11.10_all.deb
sudo dpkg -i bc_1.07.1-2build1_amd64.deb
sudo dpkg -i libcrypt-dev_1%3a4.4.10-10ubuntu4_amd64.deb
sudo dpkg -i linux-libc-dev_5.4.0-60.67_amd64.deb
sudo dpkg -i libc-dev-bin_2.31-0ubuntu9.1_amd64.deb
sudo dpkg -i libc6_2.31-0ubuntu9.1_amd64.deb
sudo dpkg -i libc6-dev_2.31-0ubuntu9.1_amd64.deb
sudo dpkg -i libstdc++-9-dev_9.3.0-17ubuntu1~20.04_amd64.deb
sudo dpkg -i g++-9_9.3.0-17ubuntu1~20.04_amd64.deb
sudo dpkg -i g++_4%3a9.3.0-1ubuntu2_amd64.deb
sudo dpkg -i build-essential_12.8ubuntu1.1_amd64.deb
unzip rtl8821ce-master
cd rtl8821ce-master/
sudo chmod +x dkms-install.sh
sudo ./dkms-install.sh
