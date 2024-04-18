#!/bin/sh
# Wazuh-agent installation script with dynamic version and agent name input
# Usage: Run this script as root without any arguments. It will prompt for necessary details.

# Define the default version and manager IP of Wazuh-agent
DEFAULT_WAZUH_VERSION="4.7.1-1"
DEFAULT_MANAGER_IP="87.98.220.106"

# Prompt user for the Wazuh-agent version or use the default
echo "Please enter the Wazuh-agent version to install (press Enter for default: $DEFAULT_WAZUH_VERSION):"
read WAZUH_VERSION
WAZUH_VERSION=${WAZUH_VERSION:-$DEFAULT_WAZUH_VERSION}

# Prompt user for the manager IP or use the default
echo "Please enter the WAZUH_MANAGER IP (press Enter for default: $DEFAULT_MANAGER_IP):"
read WAZUH_MANAGER
WAZUH_MANAGER=${WAZUH_MANAGER:-$DEFAULT_MANAGER_IP}

# Prompt user to enter the agent name
echo "Please enter the agent name (format: 'cc_lastname_personal' where 'cc' is contact center, 'lastname' is the user's last name, and 'personal' indicates personal device):"
read AGENT_NAME

# Import Wazuh repository GPG key
echo "Importing Wazuh repository GPG key..."
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | gpg --no-default-keyring --keyring gnupg-ring:/usr/share/keyrings/wazuh.gpg --import
chmod 644 /usr/share/keyrings/wazuh.gpg

# Add Wazuh repository to the sources list
echo "Adding Wazuh repository to the sources list..."
echo "deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list

# Update package information
echo "Updating package information..."
apt-get update

# Install Wazuh-agent
echo "Installing Wazuh-agent version $WAZUH_VERSION with manager at $WAZUH_MANAGER..."
apt-get install wazuh-agent=$WAZUH_VERSION

# Copy SSL certificates
echo "Copying SSL certificates..."
cp newsslagent.* /var/ossec/etc
chown root:root /var/ossec/etc/newsslagent.*
chmod 644 /var/ossec/etc/newsslagent.*

# Perform agent authentication using the specified manager IP
echo "Performing agent authentication with manager $WAZUH_MANAGER..."
/var/ossec/bin/agent-auth -m $WAZUH_MANAGER -x /var/ossec/etc/newsslagent.cert -k /var/ossec/etc/newsslagent.key -G default,ContactCenter -A $AGENT_NAME

# Reload systemd, enable and start Wazuh-agent, then check its status
echo "Setting up Wazuh-agent service..."
systemctl daemon-reload
systemctl enable wazuh-agent
systemctl start wazuh-agent
echo "Checking Wazuh-agent status..."
systemctl status wazuh-agent

# Prevent Wazuh-agent from being automatically updated
echo "Preventing automatic updates for Wazuh-agent..."
sudo apt-mark hold wazuh-agent

echo "Wazuh-agent installation and configuration complete."
