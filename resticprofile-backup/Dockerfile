FROM ghcr.io/hassio-addons/base:20.1.0@sha256:ba1c56462d6228463e561419c2b9878b77e54e34fac4f73d384346a771084703

# Copy root filesystem
COPY rootfs /

ARG TARGETARCH
ARG RESTICPROFILE_VERSION=0.33.1
ARG RESTIC_VERSION=0.18.1
ARG RCLONE_VERSION=1.74.0
RUN <<EOF
set -eu
apk add --no-cache \
  lsblk=2.41.4-r0 \
  libcap-ng=0.8.5-r0 \
  talloc=2.4.3-r0 \
  libwbclient=4.22.8-r0 \
  cifs-utils=7.4-r0 \
  lz4-libs=1.10.0-r0 \
  libpq=18.3-r0 \
  ncurses-terminfo-base=6.5_p20251123-r0 \
  libncursesw=6.5_p20251123-r0 \
  readline=8.3.1-r0 \
  zstd-libs=1.5.7-r2 \
  postgresql18-client=18.3-r0 \
  yq-go=4.49.2-r5
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
