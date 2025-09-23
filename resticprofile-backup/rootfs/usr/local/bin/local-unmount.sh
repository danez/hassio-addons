#!/usr/bin/with-contenv bashio
# shellcheck shell=bash

set -euo pipefail

if bashio::config.has_value 'localdisks'; then
    LOCALDISKS=$(bashio::config 'localdisks')
    echo "Local Disks unmounting..."

    # Separate comma separated values
    # shellcheck disable=SC2086
    for disk in ${LOCALDISKS//,/ }; do

        # Remove text until last slash
        disk="${disk##*/}"

        # Skip if mountpoint doesn't exist
        if [ ! -d "/mnt/${disk}" ]; then
            bashio::log.info "Skipping ${disk}; /mnt/${disk} not found."
            continue
        fi

        bashio::log.info "Unmounting ${disk} ..."

        # Try normal unmount first and if it fails try lazy unmount
        if ! umount "/mnt/$disk"; then
            bashio::log.warning "Unmount failed, device busy, trying lazy unmount!"
            umount -l "/mnt/$disk"
        fi
        rmdir "/mnt/$disk"

        bashio::log.info "Success!"
    done

fi
