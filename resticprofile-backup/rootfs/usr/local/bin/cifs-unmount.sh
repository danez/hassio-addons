#!/usr/bin/with-contenv bashio
# shellcheck shell=bash

set -euo pipefail

if bashio::config.has_value 'smb_shares'; then
    SMBSHARES=$(bashio::config 'smb_shares')

    bashio::log.info "SMB shares unmounting..."

    for share in $SMBSHARES
    do
        local="$(bashio::jq "$share" ".local")"

        bashio::log.info "Unmounting ${local} ..."

        # Skip if mountpoint doesn't exist
        if [ ! -d "$local" ]; then
            bashio::log.info "Skipping $local; $local not found."
            continue
        fi

        # Try normal unmount first and if it fails try lazy unmount
        if ! umount "$local"; then
            bashio::log.warning "Unmount failed, device busy, trying lazy unmount!"
            umount -l "$local"
        fi
        rmdir "$local"

        bashio::log.info "Success!"
    done
fi
