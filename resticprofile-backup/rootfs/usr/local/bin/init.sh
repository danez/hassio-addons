#!/usr/bin/with-contenv bashio

set -euo pipefail

# Available devices
blkid | awk '{print substr($1, 0, length($1) - 1)}' | awk -F'/' '{print $NF}' > availabledisks
echo "NAME" >> availabledisks

## List available Disk with Labels and Id
bashio::log.blue "---------------------------------------------------"
bashio::log.green "Available local disks for mounting:"
output=$(lsblk -o name,label,size,fstype,ro | awk '$4 != "" { print $0 }' | grep -f availabledisks)
if [ "$(echo "$output" | grep -c '^')" -le 1 ]; then
  bashio::log.yellow "No local disks available"
else
  echo "$output"
fi
bashio::log.blue "---------------------------------------------------"
rm availabledisks

# Show support fs https://github.com/dianlight/hassio-addons/blob/2e903184254617ac2484fe7c03a6e33e6987151c/sambanas/rootfs/etc/s6-overlay/s6-rc.d/init-automount/run#L106
fstypessupport=$(grep -v nodev < /proc/filesystems | awk '{$1=" "$1}1' | tr -d '\n\t')
bashio::log.green "Supported fs: ${fstypessupport}"
bashio::log.blue "---------------------------------------------------"

# if password file does not exist, generate a new one
if [ ! -f /config/password.txt ]; then
  bashio::log.info "Generating new restic password file..."
  resticprofile generate --random-key 2048 > /config/password.txt
  bashio::log.red "-----------------------------------------------------------------------------"
  bashio::log.red "IMPORTANT:"
  bashio::log.red "Backup the password in /addon_configs/xxx_resticprofile_backup/password.txt"
  bashio::log.red "to a safe place! This password is REQUIRED to restore your backups."
  bashio::log.red "If you lose this password, you will PERMANENTLY lose access to all your"
  bashio::log.red "backups!"
  bashio::log.red "Store it in a safe place (e.g. a password manager) or ensure Add-on configs"
  bashio::log.red "are included in your default Home Assistant backup!"
  bashio::log.red "-----------------------------------------------------------------------------"
else
  bashio::log.info "Using existing password from password.txt"
fi

if [ ! -f /config/profiles.yaml ]; then
  bashio::log.yellow "The configuration file /addon_configs/xxx_resticprofile_backup/profiles.yaml"
  bashio::log.yellow "could not be found. Please create this file and add your configuration to it."
  bashio::log.yellow "An example file has been created in profiles.yaml.example or checkout"
  bashio::log.yellow "https://creativeprojects.github.io/resticprofile/."
  bashio::log.red "The add-on will NOT start without this file."

  cp /usr/local/share/resticprofile/profiles.yaml.example /config/profiles.yaml.example
  exit 1
fi
