#!/bin/sh
# Script for setting up auditd with specific Wazuh audit rules.

# Check and install auditd if it's not installed
echo "Checking for auditd and installing if necessary..."
which auditd || apt-get install -y auditd

# Create the wazuh.rules file with monitoring rules
echo "Creating the /etc/audit/rules.d/wazuh.rules file..."
cat > /etc/audit/rules.d/wazuh.rules << EOF
## /etc/audit/rules.d/wazuh.rules
# Monitoring configuration files

# Auditd configuration and audit rules monitoring
-w /etc/audit/auditd.conf -p w -k audit-wazuh-secret-w
-w /etc/audit/auditd.conf -p a -k audit-wazuh-secret-a
-w /etc/audit/rules.d/ -F auid>=1000 -F auid<=2147483647 -p w -k audit-wazuh-secret-w
-w /etc/audit/rules.d/ -F auid>=1000 -F auid<=2147483647 -p a -k audit-wazuh-secret-a
-w /etc/audit/rules.d/ -F auid>=1000 -F auid<=2147483647 -p r -k audit-wazuh-secret-r
-w /etc/audit/rules.d/ -F auid>=1000 -F auid<=2147483647 -p x -k audit-wazuh-secret-x
-w /etc/libaudit.conf -p w -k audit-wazuh-w
-w /etc/libaudit.conf -p a -k audit-wazuh-a
-w /etc/default/auditd -p w -k audit-wazuh-w
-w /etc/default/auditd -p a -k audit-wazuh-a

# Monitoring root's .ssh directory
-w /root/.ssh/ -F gid!=wazuh -p w -k audit-wazuh-secret-w
-w /root/.ssh/ -F gid!=wazuh -p a -k audit-wazuh-secret-a
-w /root/.ssh/ -F gid!=wazuh -p r -k audit-wazuh-secret-r
-w /root/.ssh/ -F gid!=wazuh -p x -k audit-wazuh-secret-x

# Monitoring audit log files
-w /var/log/audit/ -F gid!=wazuh -p x -k audit-wazuh-secret-x
-w /var/log/audit/ -F gid!=wazuh -p r -k audit-wazuh-secret-r
-w /var/log/audit/ -F gid!=wazuh -p w -k audit-wazuh-secret-w
-w /var/log/audit/ -F gid!=wazuh -p a -k audit-wazuh-secret-a

# Monitoring Ossec configuration changes
-w /var/ossec/etc/ -F auid>=1000 -F auid<=2147483647 -p w -k audit-wazuh-secret-w
-w /var/ossec/etc/ -F auid>=1000 -F auid<=2147483647 -p a -k audit-wazuh-secret-a
-w /var/ossec/etc/ -F auid>=1000 -F auid<=2147483647 -p r -k audit-wazuh-r
-w /var/ossec/etc/ -F auid>=1000 -F auid<=2147483647 -p x -k audit-wazuh-secret-x

# Monitoring at settings and jobs
-w /var/spool/at
-w /etc/at.allow
-w /etc/at.deny

# Monitoring cron jobs and settings
-w /etc/cron.allow -p w -k audit-wazuh-w
-w /etc/cron.allow -p a -k audit-wazuh-a
-w /etc/cron.deny -p w -k audit-wazuh-w
-w /etc/cron.deny -p a -k audit-wazuh-a
-w /etc/cron.d/ -p w -k audit-wazuh-w
-w /etc/cron.d/ -p a -k audit-wazuh-a
-w /etc/cron.daily/ -p w -k audit-wazuh-w
-w /etc/cron.daily/ -p a -k audit-wazuh-a
-w /etc/cron.hourly/ -p w -k audit-wazuh-w
-w /etc/cron.hourly/ -p a -k audit-wazuh-a
-w /etc/cron.monthly/ -p w -k audit-wazuh-w
-w /etc/cron.monthly/ -p a -k audit-wazuh-a
-w /etc/cron.weekly/ -p w -k audit-wazuh-w
-w /etc/cron.weekly/ -p a -k audit-wazuh-a
-w /etc/crontab -p w -k audit-wazuh-w
-w /etc/crontab -p a -k audit-wazuh-a
-w /var/spool/cron/root

# Monitoring password and group files
-w /etc/group -p w -k audit-wazuh-w
-w /etc/group -p a -k audit-wazuh-a
-w /etc/passwd -p w -k audit-wazuh-w
-w /etc/passwd -p a -k audit-wazuh-a
-w /etc/shadow -p w -k audit-wazuh-secret-w
-w /etc/shadow -p a -k audit-wazuh-a
-w /etc/shadow -p r -k audit-wazuh-r
-w /etc/shadow -p x -k audit-wazuh-x

# Monitoring login configuration and log files
-w /etc/login.defs -p w -k audit-wazuh-w
-w /etc/login.defs -p a -k audit-wazuh-a
-w /etc/securetty
-w /var/log/faillog
-w /var/log/lastlog

# Monitoring hosts file
-w /etc/hosts -p w -k audit-wazuh-w
-w /etc/hosts -p a -k audit-wazuh-a

# Monitoring daemon start scripts
-w /etc/init.d/
-w /etc/init.d/auditd -p w -k audit-wazuh-w
-w /etc/init.d/auditd -p a -k audit-wazuh-a

# Monitoring library search paths
-w /etc/ld.so.conf.d
-w /etc/ld.so.conf -p w -k audit-wazuh-w
-w /etc/ld.so.conf -p a -k audit-wazuh-a

# Monitoring time settings
-w /etc/localtime -p w -k audit-wazuh-w
-w /etc/localtime -p a -k audit-wazuh-a

# Monitoring system variables
-w /etc/sysctl.conf -p w -k audit-wazuh-w
-w /etc/sysctl.conf -p a -k audit-wazuh-a

# Monitoring module loading rules
-w /etc/modprobe.d/

# Monitoring PAM system modules
-w /etc/pam.d/

# Monitoring SSH server settings
-w /etc/ssh/sshd_config

# Monitoring /home directory
-w /home -p w -k audit-wazuh-w
-w /home -p a -k audit-wazuh-a
#-w /home -p r -k audit-wazuh-r
-w /home -p x -k audit-wazuh-x

# Monitoring commands executed by root and users with specific auid
-a always,exit -F arch=b64 -F euid=0 -F auid>=1000 -F auid!=-1 -S execve -k audit-wazuh-c
-a always,exit -F arch=b32 -F euid=0 -F auid>=1000 -F auid!=-1 -S execve -k audit-wazuh-c
-a exit,always -F arch=b64 -F auid>=1000 -F auid<60001 -F auid!=-1 -S execve -k audit-wazuh-c
-a exit,always -F arch=b32 -F auid>=1000 -F auid<60001 -F auid!=-1 -S execve -k audit-wazuh-c
-a exit,always -F arch=b64 -F auid>=65535 -F auid<=2147483647 -F auid!=-1 -S execve -k audit-wazuh-c
-a exit,always -F arch=b32 -F auid>=65535 -F auid<=2147483647 -F auid!=-1 -S execve -k audit-wazuh-c
EOF

# Restart auditd to apply changes
echo "Restarting auditd service..."
service auditd restart

echo "Wazuh auditd configuration is now complete."
