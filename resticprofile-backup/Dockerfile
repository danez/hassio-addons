FROM ghcr.io/hassio-addons/base:20.0.1@sha256:81e9befb43d927cea0738683381835f1660dce5f5794b5417b39a5768c0ecf59

# Copy root filesystem
COPY rootfs /

RUN apk add --no-cache \
    # lsblk
    lsblk=2.41.2-r0 \
    # Install cifs-utils and its dependencies for SMB/CIFS support
    libcap-ng=0.8.5-r0 \
    talloc=2.4.3-r0 \
    libwbclient=4.22.6-r0 \
    cifs-utils=7.4-r0 \
    # pg-client
    lz4-libs=1.10.0-r0 \
    libpq=18.2-r0 \
    ncurses-terminfo-base=6.5_p20251123-r0 \
    libncursesw=6.5_p20251123-r0 \
    readline=8.3.1-r0 \
    zstd-libs=1.5.7-r2 \
    postgresql18-client=18.2-r0 \
    # yq
    yq-go=4.49.2-r3 \
    && yq --version


ARG BUILD_ARCH BUILD_RESTICPROFILE_VERSION BUILD_RESTIC_VERSION BUILD_RCLONE_VERSION
RUN \
    export GO_ARCH=$([ "${BUILD_ARCH}" = "aarch64" ] && echo "arm64" || echo "amd64") \
    && wget -qO /tmp/resticprofile.tar.gz \
    "https://github.com/creativeprojects/resticprofile/releases/download/v${BUILD_RESTICPROFILE_VERSION}/resticprofile_no_self_update_${BUILD_RESTICPROFILE_VERSION}_linux_${GO_ARCH}.tar.gz" \
    && mkdir -p /tmp/resticprofile \
    && tar -xzf /tmp/resticprofile.tar.gz -C /tmp/resticprofile \
    && mv /tmp/resticprofile/resticprofile /usr/bin/resticprofile \
    && chmod +x /usr/bin/resticprofile \
    && resticprofile version \
    \
    && wget -qO /tmp/restic.bz2 \
    "https://github.com/restic/restic/releases/download/v${BUILD_RESTIC_VERSION}/restic_${BUILD_RESTIC_VERSION}_linux_${GO_ARCH}.bz2" \
    && bunzip2 -c /tmp/restic.bz2 > /usr/bin/restic \
    && chmod +x /usr/bin/restic \
    && restic version \
    \
    && wget -qO /tmp/rclone.zip \
    "https://github.com/rclone/rclone/releases/download/v${BUILD_RCLONE_VERSION}/rclone-v${BUILD_RCLONE_VERSION}-linux-${GO_ARCH}.zip" \
    && mkdir -p /tmp/rclone \
    && unzip -jq /tmp/rclone.zip -d /tmp/rclone \
    && mv /tmp/rclone/rclone /usr/bin/rclone \
    && chmod +x /usr/bin/rclone \
    && rclone --version \
    && rm -rf /tmp/*

RUN mkdir -p /usr/local/etc/resticprofile/ \
    && chmod +x /usr/local/bin/cifs-mount.sh \
    && chmod +x /usr/local/bin/cifs-unmount.sh \
    && chmod +x /usr/local/bin/init.sh \
    && chmod +x /usr/local/bin/local-mount.sh \
    && chmod +x /usr/local/bin/local-unmount.sh \
    && chmod +x /usr/local/bin/resticprofile-schedule.sh
