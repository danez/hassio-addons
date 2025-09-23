#!/usr/bin/with-contenv bashio
# shellcheck shell=bash

set -euo pipefail

# This file is heavily based on alexbelgium/hassio-addons
# https://github.com/alexbelgium/hassio-addons/blob/master/.templates/00-local_mounts.sh

if bashio::config.has_value 'localdisks'; then
    LOCALDISKS=$(bashio::config 'localdisks')

    bashio::log.info "Local Disks mounting..."

    fstypessupport="$(grep -v nodev /proc/filesystems | awk '{print $NF}')"
    # Separate comma separated values
    # shellcheck disable=SC2086
    for disk in ${LOCALDISKS//,/ }; do

        # Remove text until last slash
        disk="${disk##*/}"

        # Resolve to an actual block device path
        dev=""
        if [ -e "/dev/$disk" ]; then
            dev="/dev/$disk"
        else
            dev="$(blkid -U "$disk" 2>/dev/null || true)"
            [ -z "$dev" ] && dev="$(blkid -L "$disk" 2>/dev/null || true)"
        fi
        if [ -z "${dev:-}" ] || [ ! -e "$dev" ]; then
            bashio::log.fatal "$disk does not match any known physical device, UUID, or label."
            continue
        fi

        # Check FS type and set relative options (thanks @https://github.com/dianlight/hassio-addons)
        fstype="$(lsblk -no fstype -- "$dev")"
        if [ -z "${fstype:-}" ]; then
            # lsblk might not return a fs, blkid directly probes the disk and might still return something
            fstype="$(blkid -o value -s TYPE -- "$dev" 2>/dev/null || true)"
        fi
        options="nosuid,nodev,relatime,noexec"
        type="auto"

        # Check if supported
        if [ -z "${fstype:-}" ] || ! printf '%s\n' "$fstypessupport" | grep -qw -- "${fstype}"; then
            bashio::log.fatal "${fstype:-unknown} type for ${disk} is not supported"
            # Stop the addon if any disk could not be mounted
            bashio::addon.stop
        fi

        # Creates dir
        mkdir -p /mnt/"$disk"

        # Mount drive
        bashio::log.info "Mounting ${disk} of type ${fstype}"
        case "$fstype" in
            exfat | vfat | msdos)
                bashio::log.warning "${fstype}: permissions/ACLs may not work; EXPERIMENTAL support"
                options="${options},umask=000"
                ;;
            ntfs)
                bashio::log.warning "${fstype} is an EXPERIMENTAL support"
                options="${options},umask=000"
                type="ntfs"
                ;;
            squashfs)
                bashio::log.warning "${fstype} is an EXPERIMENTAL support"
                options="loop"
                type="squashfs"
                ;;
        esac


        if mount -t "$type" -- "$dev" "/mnt/$disk" -o "$options"; then
            bashio::log.info "Success! $disk mounted to /mnt/$disk"
        else
            bashio::log.fatal "Unable to mount $disk ($dev, fstype=${fstype})"
            # Stop the addon if any disk could not be mounted
            bashio::addon.stop
        fi
    done

fi
