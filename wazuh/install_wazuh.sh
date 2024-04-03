#!/bin/sh
# Wazuh-agent installation script with dynamic version and agent name input
# Usage: Run this script as root without any arguments. It will prompt for necessary details.

# Define the default version of Wazuh-agent. This should be the latest stable version.
DEFAULT_WAZUH_VERSION="4.7.1-1"

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

# Prompt user to enter the desired Wazuh-agent version or use the default
read -p "Enter Wazuh-agent version to install (default: $DEFAULT_WAZUH_VERSION): " WAZUH_VERSION
WAZUH_VERSION=${WAZUH_VERSION:-$DEFAULT_WAZUH_VERSION}

# Install Wazuh-agent
echo "Installing Wazuh-agent version $WAZUH_VERSION..."
WAZUH_MANAGER="87.98.220.106" apt-get install wazuh-agent=$WAZUH_VERSION

# Copy SSL certificates
echo "Copying SSL certificates..."
cp newsslagent.* /var/ossec/etc
chown root:root /var/ossec/etc/newsslagent.*
chmod 644 /var/ossec/etc/newsslagent.*

# Prompt user to enter the agent name following the given format
echo "Please enter the agent name (e.g., for cc_plakhov_personal, 'plakhov' is the personal identifier):"
read AGENT_NAME

# Construct agent name and perform agent authentication
echo "Performing agent authentication..."
/var/ossec/bin/agent-auth -m 87.98.220.106 -x /var/ossec/etc/newsslagent.cert -k /var/ossec/etc/newsslagent.key -G default,ContactCenter -A cc_${AGENT_NAME}_personal

# Reload systemd, enable and start Wazuh-agent, and then check its status
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
