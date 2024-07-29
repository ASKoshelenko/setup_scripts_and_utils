#!/bin/bash

# Updating and installing the OpenSSH server
sudo apt update
sudo apt install -y openssh-server

# Enabling the SSH server to start on boot
sudo systemctl enable ssh
echo "SSH server is enabled to start on boot."

# Checking if the SSH server is active
SSH_STATUS=$(sudo systemctl is-active ssh)
if [ "${SSH_STATUS}" = "active" ]; then
    echo "SSH server is active."
else
    echo "SSH server is not active. Starting the SSH server..."
    sudo systemctl start ssh
    # Checking the status again after attempting to start
    if [ $(sudo systemctl is-active ssh) = "active" ]; then
        echo "SSH server has been started successfully."
    else
        echo "Failed to start the SSH server. Please check the settings or start the server manually."
    fi
fi

# Creating the .ssh directory and authorized_keys file for the 'support' user
sudo mkdir -p /home/support/.ssh
sudo touch /home/support/.ssh/authorized_keys

# Add permissions
sudo chown -R support:support /home/support/.ssh
sudo chmod 700 /home/support/.ssh
sudo chmod 600 /home/support/.ssh/authorized_keys

# Adding public keys to authorized_keys
#Romanko pub key
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDVsmTHPWlk1giKroHW1qbHWN50zAb8DL6tqzVRY9w75JMFZfOjKiPAvHYMZEJVqsPGPE43JfQdld7dWG5u+9Jn8UsCFO9b/3qJkpkbCB5PlHbiRMSlC1ojg6RL4M+p2sBgip+J0uHIMbLZkQpVpMYFpq5B6bwRF5bPgrRlrMEGtJmz2s84efbNavyK8sLZe6ZX8PBHOtj0gg6MaugnotF90PNxer92PvwQBvIw0pSfP9dholYVKWGbITZluaVxH0PBk0lC5KvD+jWeRukQI45VIXMm/HQ4yIgnrjk5UjqmY810KSYYKx1IlGTp56vNNHGej549ht/45yXdXi7xdrTFazYtqUGndJHvyHMJfdNkIgHZfiz1gWAyBqoBMXl6TVJQM3kHIs9X3HbL0CszH1PbO5VXATKhZup08dPy+z2FFaX94yshS4fdiHEyVmn/IZ1E8ATTKPnZZOXc0Y4vlze0vUdHu8zkbpHAHsg06IL90GmNNmJo0z+Bjvx/F4m4KaU= romanko@Inpirin" | sudo tee -a /home/support/.ssh/authorized_keys
#Koshelenko pub key
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQCmRls6iuufvsvdX603Rweeiti9YqWEmDmYcV/VmHAvtCyBqVkwYmqsSH+7BUMezR5DzZKB/hjJ+OiTvCHsnXyhG8+cbymdfL4FriCN+PergdfRFPEnFhMPqzws21Nkf9r6oBQZs36lFL4wZRxLw6cGYej/Fmpf2hUgfu24435/w1LX56XQmTBqntS3/80dEs/mNALT/qVuXpbD05zfo4L8ow72cUUII2I68eKySL1mHf/V8BemnzR7JagET1NNL4TI9Cah0C8LiAD2xs4l1mAaljNPoxmnCujACJdx7bQxnEOE5RHkYOfs+Tg5Chx/veVfqZ9WownschcRF2bMV8hYqot8JMo2MePMSoZA/DNyd+VL6IU/RQ1nnuMmD+bXFt59A063rPYkC9ttwEsnT+WWqFJRh0WqhQRUuiyXS0LaTcnIgthtk2T4dEfbeDjWuuySrYEEAkpVyWhFlTQDOIa/B5uUBxROPHIwil4Jl46sWK1nZvzJUA14fjT+uu2i4Xk= koshelenko@HP-Laptop-15-db1xxx" | sudo tee -a /home/support/.ssh/authorized_keys