#!/usr/bin/with-contenv bashio

set -euo pipefail

if bashio::config.has_value 'smb_shares'; then
    SMBSHARES=$(bashio::config 'smb_shares')

    bashio::log.info "SMB shares mounting..."

    for share in $SMBSHARES
    do
        host=$(bashio::jq "$share" ".host")
        local=$(bashio::jq "$share" ".local")
        username=$(bashio::jq "$share" ".username")
        password=$(bashio::jq "$share" ".password")
        smb_version=$(bashio::jq "$share" ".smb_version")

        if [ ! -n "$smb_version" ]; then
            CIFS_VERSION_ARG=",vers=$smb_version"
        else
            CIFS_VERSION_ARG=""
        fi

        bashio::log.info "Mount ${local} from ${host}..."
        bashio::log.debug "mount -t cifs -o \"rw,noserverino,username=$username,password=$password$CIFS_VERSION_ARG\" $host $local"
        mkdir -p "$local"
        mount -t cifs -o "rw,noserverino,username=$username,password=$password$CIFS_VERSION_ARG" "$host" "$local"
        bashio::log.info "Success!"
    done
fi
