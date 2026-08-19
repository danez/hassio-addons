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

FROM node:22.23.2-trixie-slim@sha256:db8a96a63e5264607ada2d206758876ebbed6a12be2ada7517793cbfb0c2a29c AS node

FROM ghcr.io/hassio-addons/debian-base:9.4.0@sha256:3fd1a6eb8216caaff8bf3eb4d685bb9589dcb70235e326779ee0b5b2bd170054

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
