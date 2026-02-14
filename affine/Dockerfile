ARG BUILD_AFFINE_VERSION
FROM ghcr.io/toeverything/affine:${BUILD_AFFINE_VERSION} AS affine

ARG BUILD_ARCH

RUN <<EOF
set -eu

# Remove unneeded native bindings for other architectures
rm -rf /app/dist/server-native.armv7.node

# Remove source maps to reduce final image size
rm -rf /app/dist/main.js.map /app/src /app/static/js/*.js.map /app/static/mobile/js/*.js.map /app/static/admin/js/*.js.map

if [ "${BUILD_ARCH}" = "aarch64" ]; then
    rm -rf /app/dist/server-native.x64.node
else
    rm -rf /app/dist/server-native.arm64.node
fi

EOF

FROM node:22.22.0-trixie-slim@sha256:780adb393de425b91be1868956244fcdabf4a1df52d8c147b581c5372f230278 AS node

FROM ghcr.io/hassio-addons/debian-base:9.2.0@sha256:f97dc1d0f6960b8445746922fa03e73598eef7eca1bb98357b9f63d32ae22fce

# NODE
COPY --from=node /usr/local /usr/local
COPY --from=node /opt /opt
# AFFINE
COPY --from=affine /app /app
WORKDIR /app

# Re-declare ARG for final stage (ARGs don't persist across stages)
ARG BUILD_AFFINE_VERSION

RUN <<EOF
set -euo pipefail
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
