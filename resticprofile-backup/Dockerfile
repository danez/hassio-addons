ARG BUILD_FROM=ghcr.io/hassio-addons/base:18.1.1
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# Copy root filesystem
COPY rootfs /

RUN apk add --no-cache \
    # Install cifs-utils and its dependencies for SMB/CIFS support
    libcap-ng=0.8.5-r0 \
    talloc=2.4.2-r1 \
    libwbclient=4.21.4-r4 \
    cifs-utils=7.3-r0 \
    # pg-client
    lz4-libs=1.10.0-r0 \
    libpq=17.6-r0 \
    ncurses-terminfo-base=6.5_p20250503-r0 \
    libncursesw=6.5_p20250503-r0 \
    readline=8.2.13-r1 \
    zstd-libs=1.5.7-r0 \
    postgresql17-client=17.6-r0 \
    # yq
    yq-go=4.47.2-r0 \
    && yq --version


ARG BUILD_ARCH BUILD_RESTICPROFILE_VERSION BUILD_RESTIC_VERSION BUILD_RCLONE_VERSION
RUN \
    if [ "${BUILD_ARCH}" = "aarch64" ]; then \
    export RESTICPROFILE_ARCH="arm64"; \
    elif [ "${BUILD_ARCH}" = "i386" ]; then \
    export RESTICPROFILE_ARCH="386"; \
    elif [ "${BUILD_ARCH}" = "armhf" ]; then \
    export RESTICPROFILE_ARCH="armv6"; \
    else \
    export RESTICPROFILE_ARCH="${BUILD_ARCH}"; \
    fi \
    && wget -qO /tmp/resticprofile.tar.gz \
    "https://github.com/creativeprojects/resticprofile/releases/download/v${BUILD_RESTICPROFILE_VERSION}/resticprofile_no_self_update_${BUILD_RESTICPROFILE_VERSION}_linux_${RESTICPROFILE_ARCH}.tar.gz" \
    && mkdir -p /tmp/resticprofile \
    && tar -xzf /tmp/resticprofile.tar.gz -C /tmp/resticprofile \
    && mv /tmp/resticprofile/resticprofile /usr/bin/resticprofile \
    && chmod +x /usr/bin/resticprofile \
    && resticprofile version \
    \
    && if [ "${BUILD_ARCH}" = "aarch64" ]; then \
    export RESTIC_ARCH="arm64"; \
    elif [ "${BUILD_ARCH}" = "i386" ]; then \
    export RESTIC_ARCH="386"; \
    elif [ "${BUILD_ARCH}" = "armhf" ]; then \
    export RESTIC_ARCH="arm"; \
    elif [ "${BUILD_ARCH}" = "armv7" ]; then \
    export RESTIC_ARCH="arm"; \
    else \
    export RESTIC_ARCH="${BUILD_ARCH}"; \
    fi \
    && wget -qO /tmp/restic.bz2 \
    "https://github.com/restic/restic/releases/download/v${BUILD_RESTIC_VERSION}/restic_${BUILD_RESTIC_VERSION}_linux_${RESTIC_ARCH}.bz2" \
    && bunzip2 -c /tmp/restic.bz2 > /usr/bin/restic \
    && chmod +x /usr/bin/restic \
    && restic version \
    \
    && if [ "${BUILD_ARCH}" = "aarch64" ]; then \
    export RCLONE_ARCH="arm64"; \
    elif [ "${BUILD_ARCH}" = "i386" ]; then \
    export RCLONE_ARCH="386"; \
    elif [ "${BUILD_ARCH}" = "armhf" ]; then \
    export RCLONE_ARCH="arm-v6"; \
    elif [ "${BUILD_ARCH}" = "armv7" ]; then \
    export RCLONE_ARCH="arm-v7"; \
    else \
    export RCLONE_ARCH="${BUILD_ARCH}"; \
    fi \
    && wget -qO /tmp/rclone.zip \
    "https://github.com/rclone/rclone/releases/download/v${BUILD_RCLONE_VERSION}/rclone-v${BUILD_RCLONE_VERSION}-linux-${RCLONE_ARCH}.zip" \
    && mkdir -p /tmp/rclone \
    && unzip -jq /tmp/rclone.zip -d /tmp/rclone \
    && mv /tmp/rclone/rclone /usr/bin/rclone \
    && chmod +x /usr/bin/rclone \
    && rclone --version \
    && rm -rf /tmp/*

RUN mkdir -p /usr/local/etc/resticprofile/ \
    && chmod +x /usr/local/bin/cifs-mount.sh \
    && chmod +x /usr/local/bin/init.sh \
    && chmod +x /usr/local/bin/resticprofile-schedule.sh
