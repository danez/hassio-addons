FROM ghcr.io/toeverything/affine:0.27.4@sha256:b649f5ce2384ffdf13c23bccf81d759e15973d59d0b0058af65d895a84373099 AS affine

ARG TARGETARCH

RUN <<EOF
set -eu
# Remove unneeded native bindings for other architectures
rm -rf /app/dist/server-native.armv7.node

# Remove source maps to reduce final image size
rm -rf /app/dist/main.js.map /app/src /app/static/js/*.js.map /app/static/mobile/js/*.js.map /app/static/admin/js/*.js.map

if [ "${TARGETARCH}" = "arm64" ]; then
    rm -rf /app/dist/server-native.x64.node
else
    rm -rf /app/dist/server-native.arm64.node
fi

EOF

FROM node:22.23.4-trixie-slim@sha256:be1e2a3dc2c4fd68cdfadad2a696a280e0d2749098bee509230174d72fb768c6 AS node

FROM ghcr.io/hassio-addons/debian-base:9.5.2@sha256:1faf86975f6215114064f597c1b8cc03f3793ff15f2bd1cad5989a675a541062

# NODE
COPY --from=node /usr/local /usr/local
COPY --from=node /opt /opt
# AFFINE
COPY --from=affine /app /app
WORKDIR /app

RUN <<EOF
set -eu
# Install dependencies for Affine
# Also install redis
apt-get update
apt-get install -y --no-install-recommends openssl libjemalloc2 redis-server
rm -rf /var/lib/apt/lists/*

# Verify installations
redis-server --version
npm --version
node --version

# Clean up unneeded files
rm -rf /tmp/*
EOF

# Enable jemalloc by preloading the library
ENV LD_PRELOAD=libjemalloc.so.2

EXPOSE 3010

# Copy root filesystem
COPY rootfs /

LABEL \
    io.hass.type="addon" \
    org.opencontainers.image.title="Home Assistant App: AFFiNE" \
    org.opencontainers.image.description="Home Assistant App that runs AFFiNE self-hosted." \
    org.opencontainers.image.source="https://github.com/danez/hassio-addons/tree/main/affine" \
    org.opencontainers.image.licenses="MIT"
