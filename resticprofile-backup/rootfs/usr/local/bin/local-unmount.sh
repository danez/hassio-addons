#!/usr/bin/with-contenv bashio

set -euo pipefail

if bashio::config.has_value 'localdisks'; then
    LOCALDISKS=$(bashio::config 'localdisks')
    echo "Local Disks unmounting..."

    # Separate comma separated values
    # shellcheck disable=SC2086
    for disk in ${LOCALDISKS//,/ }; do

        # Remove text until last slash
        disk="${disk##*/}"

        bashio::log.info "Unmounting ${disk} ..."

        # Try normal unmount first and if it fails try lazy unmount
        if ! umount /mnt/"$disk"; then
            bashio::log.warning "Unmount failed, device busy, trying lazy unmount!"
            umount -l /mnt/"$disk"
        fi
        rmdir /mnt/"$disk"

        bashio::log.info "Success!"
    done

fi
