#!/bin/sh
set -e
sudo apt update
sudo snap install pycharm-community --classic
sudo snap install insomnia
sudo snap install postman
sudo snap install pycharm-professional --classic
sudo snap install insomnia
sudo snap install postman
sudo snap install --classic code
sudo apt update
sudo apt -y install vim bash-completion wget zsh
zsh --version

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" |sudo tee  /etc/apt/sources.list.d/pgdg.list
sudo apt update
sudo apt -y install postgresql-9.6 postgresql-client-9.6
systemctl is-enabled postgresql
sudo sed -i '85 s|peer|trust|' /etc/postgresql/9.6/main/pg_hba.conf
sudo sed -i '92 s|md5|trust|' /etc/postgresql/9.6/main/pg_hba.conf
sudo apt -y install postgresql-12 postgresql-client-12
sudo sed -i '89 s|peer|trust|' /etc/postgresql/12/main/pg_hba.conf
sudo sed -i '96 s|md5|trust|' /etc/postgresql/12/main/pg_hba.conf
sudo systemctl restart postgresql

curl https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo apt-key add
sudo sh -c 'echo "deb https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'
sudo apt install pgadmin4

sudo apt-get install -y python3-dev python3-venv python3-pip python3.6 python3.7 python3.8-dev python3.8-venv 
sudo pip3 install virtualenv
#sudo apt -y install postgresql-12 postgresql-client-12
#systemctl is-enabled postgresql
#sudo sed -i '85 s|peer|trust|' /etc/postgresql/9.6/main/pg_hba.conf
#sudo sed -i '92 s|md5|trust|' /etc/postgresql/9.6/main/pg_hba.conf
#sudo systemctl restart postgresql
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.6 python3.6-dev python3.6-venv

sudo add-apt-repository "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -sc)-pgdg main"
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y postgresql-9.6

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.6 python3.6-venv python3.6-dev

sudo apt-get install -y python3-dev python3-venv python3-pip python3.7  python3.8-dev python3.8-venv 
sudo pip3 install virtualenv
curl -fsSL https://www.mongodb.org/static/pgp/server-4.4.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list
sudo apt update
sudo apt -y install mongodb-org
sudo systemctl enable mongod
