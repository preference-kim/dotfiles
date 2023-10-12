#!/bin/bash

# before running, command chmod +x sshconfig.sh

# make sure config file exists
ssh_dir="$HOME/.ssh"
[ -d "$ssh_dir" ] || mkdir -m 700 "$ssh_dir"

# Set proper permissions for the .ssh directory
chmod 700 "$ssh_dir"

# generate ssh key
# ssh-keygen -t rsa -b 2048 -C "preferencekimm@gmail.com" -f ~/.ssh/general_id_rsa

# Set proper permissions for the key files
chmod 600 ~/.ssh/general_id_rsa
chmod 644 ~/.ssh/general_id_rsa.pub

# Create or update the SSH config file
config_file="$ssh_dir/config"
[ -f "$config_file" ] || touch "$config_file"
chmod 600 "$config_file"

echo -e "Host mercury\n    User sunho\n    HostName XX.XXX.XX.XX\n    Port XXX\n    IdentityFile ~/.ssh/general_id_rsa.pub\n" >> "$config_file"

# Copy the public key to the remote host using ssh-copy-id
ssh-copy-id -i ~/.ssh/general_id_rsa.pub mercury

echo "Host configuration added to $config_file"