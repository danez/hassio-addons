ARG AFFINE_VERSION=0.26.3@sha256:725aaceb0ed94d4b832ae6ef9414503291c9b2b4f60bd6f3c7eef571b6149add
FROM ghcr.io/toeverything/affine:${AFFINE_VERSION} AS affine

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

FROM node:22.22.2-trixie-slim@sha256:fbd78b2335c6c9894466257f6efcf285593bd449dd8cd525e9252219ca706165 AS node

FROM ghcr.io/hassio-addons/debian-base:9.2.0@sha256:f97dc1d0f6960b8445746922fa03e73598eef7eca1bb98357b9f63d32ae22fce

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
