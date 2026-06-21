FROM ghcr.io/hassio-addons/base:21.0.0@sha256:26c14772d1eb72c8aa7f0b6866a2bc13ada705f77b8c263fcfa09116a5e00e25

# Copy root filesystem
COPY rootfs /

ARG TARGETARCH
ARG RESTICPROFILE_VERSION=0.33.1
ARG RESTIC_VERSION=0.18.1
ARG RCLONE_VERSION=1.74.3
RUN <<EOF
set -eu
apk add --no-cache \
  ca-certificates=20260611-r0 \
  cifs-utils=7.4-r0 \
  lsblk=2.41.4-r0 \
  openssh-client-default=10.2_p1-r0 \
  postgresql18-client=18.4-r0 \
  tzdata=2026b-r0 \
  yq-go=4.49.2-r6

yq --version

wget -qO /tmp/resticprofile.tar.gz "https://github.com/creativeprojects/resticprofile/releases/download/v${RESTICPROFILE_VERSION}/resticprofile_no_self_update_${RESTICPROFILE_VERSION}_linux_${TARGETARCH}.tar.gz"
mkdir -p /tmp/resticprofile
tar -xzf /tmp/resticprofile.tar.gz -C /tmp/resticprofile
mv /tmp/resticprofile/resticprofile /usr/bin/resticprofile
chmod +x /usr/bin/resticprofile
resticprofile version

wget -qO /tmp/restic.bz2 "https://github.com/restic/restic/releases/download/v${RESTIC_VERSION}/restic_${RESTIC_VERSION}_linux_${TARGETARCH}.bz2"
bunzip2 -c /tmp/restic.bz2 > /usr/bin/restic
chmod +x /usr/bin/restic
restic version

wget -qO /tmp/rclone.zip "https://github.com/rclone/rclone/releases/download/v${RCLONE_VERSION}/rclone-v${RCLONE_VERSION}-linux-${TARGETARCH}.zip"
mkdir -p /tmp/rclone
unzip -jq /tmp/rclone.zip -d /tmp/rclone
mv /tmp/rclone/rclone /usr/bin/rclone
chmod +x /usr/bin/rclone
RCLONE_VERSION=false rclone --version
rm -rf /tmp/*

mkdir -p /usr/local/etc/resticprofile/
chmod +x /usr/local/bin/cifs-mount.sh
chmod +x /usr/local/bin/cifs-unmount.sh
chmod +x /usr/local/bin/init.sh
chmod +x /usr/local/bin/local-mount.sh
chmod +x /usr/local/bin/local-unmount.sh
chmod +x /usr/local/bin/resticprofile-schedule.sh
EOF

LABEL \
  io.hass.type="addon" \
  org.opencontainers.image.title="Home Assistant App: Resticprofile Backup" \
  org.opencontainers.image.description="Home Assistant App that can run scheduled resticprofile Backups." \
  org.opencontainers.image.source="https://github.com/danez/hassio-addons/tree/main/resticprofile-backup" \
  org.opencontainers.image.licenses="MIT"
