#!/bin/sh
#Wazuh-agent 4.4.3-1 installation script 
#Usage: ./install_wazuh.sh agentname 
#Run from root!

curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import && chmod 644 /usr/share/keyrings/wazuh.gpg
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list
apt-get update

WAZUH_MANAGER="87.98.220.106"  apt-get install wazuh-agent=4.7.1-1

cp newsslagent.* /var/ossec/etc
chown root:root /var/ossec/etc/newsslagent.*
chmod 644 /var/ossec/etc/newsslagent.*

/var/ossec/bin/agent-auth -m 87.98.220.106 -x /var/ossec/etc/newsslagent.cert -k /var/ossec/etc/newsslagent.key -G default,ContactCenter -A cc_dell_1SBDB53

systemctl daemon-reload
systemctl enable wazuh-agent
systemctl start wazuh-agent
systemctl status wazuh-agent
sudo apt-mark hold wazuh-agent
