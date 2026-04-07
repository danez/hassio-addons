FROM ghcr.io/toeverything/affine:0.26.6@sha256:d1c65f5d545d3e0a51c1696c482739915fbf402ba37cefb31539a1de095531e8 AS affine

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

FROM node:22.22.2-trixie-slim@sha256:76043ed3132293c26b960ede4358d3c8ba424ee64662cd2d56318b76fcc51c4c AS node

FROM ghcr.io/hassio-addons/debian-base:9.3.0@sha256:01448978e65c3320030d97e9c9d59ed93e4173d54696ab4bc3eabe4439bff1ee

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
