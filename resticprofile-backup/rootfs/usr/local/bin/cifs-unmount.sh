#!/usr/bin/with-contenv bashio

set -euo pipefail

if bashio::config.has_value 'smb_shares'; then
    SMBSHARES=$(bashio::config 'smb_shares')

    bashio::log.info "SMB shares unmounting..."

    for share in $SMBSHARES
    do
        local=$(bashio::jq "$share" ".local")

        bashio::log.info "Unmounting ${local} ..."

        # Try normal unmount first and if it fails try lazy unmount
        if ! umount "$local"; then
            bashio::log.warning "Unmount failed, device busy, trying lazy unmount!"
            umount -l "$local"
        fi
        rmdir "$local"

        bashio::log.info "Success!"
    done
fi
