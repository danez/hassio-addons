ARG BUILD_AFFINE_VERSION
FROM ghcr.io/toeverything/affine:${BUILD_AFFINE_VERSION} AS affine

ARG BUILD_ARCH

RUN <<EOF
set -eu

# Remove node_modules to reduce final image size and we are installing them later anyway again
rm -rf /app/node_modules

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

FROM node:22.21.1-alpine3.22 AS node

# Remove yarn and yarnpkg to use corepack managed versions later
RUN rm -rf /usr/local/bin/yarn /usr/local/bin/yarnpkg

FROM ghcr.io/hassio-addons/base:19.0.0

# NODE
COPY --from=node /usr/local /usr/local
# AFFINE
COPY --from=affine /app /app
WORKDIR /app

# Enable jemalloc by preloading the library
ENV LD_PRELOAD=/usr/lib/libjemalloc.so.2

# Re-declare ARG for final stage (ARGs don't persist across stages)
ARG BUILD_AFFINE_VERSION

RUN <<EOF
set -euo pipefail
# Install dependencies for Affine
# Also install redis and manticore
apk add --no-cache \
openssl=3.5.4-r0 \
libgcc=14.2.0-r6 \
libstdc++=14.2.0-r6 \
jemalloc=5.3.0-r6 \
redis=8.0.4-r0


# Verify installations
redis-server --version
npm --version
node --version

# Derive package manager from upstream package.json
curl -o /tmp/upstream.json "https://raw.githubusercontent.com/toeverything/AFFiNE/refs/tags/v${BUILD_AFFINE_VERSION}/package.json"
PACKAGE_MANAGER=$(jq -r '.packageManager' /tmp/upstream.json)

# Install specific Yarn version
corepack enable
corepack install --global "$PACKAGE_MANAGER"

# Clean up Affine installation by removing dev dependencies
jq 'del(.devDependencies, .dependencies["@affine/reader"], .dependencies["@affine/server-native"])' /app/package.json > /app/package.json.tmp
mv /app/package.json.tmp /app/package.json

# Fetch yarn.lock for the specific AFFiNE version to ensure we do not install other versions of dependencies
curl -o /app/yarn.lock "https://raw.githubusercontent.com/toeverything/AFFiNE/refs/tags/v${BUILD_AFFINE_VERSION}/yarn.lock"

# Create a custom .yarnrc.yml similar to the one upstream
cat > /app/.yarnrc.yml <<YEOF
compressionLevel: mixed
enableGlobalCache: false
nmMode: hardlinks-local
nodeLinker: node-modules
npmRegistryServer: "https://registry.npmjs.org"
YEOF

# Remove explicit Prisma client output line from Prisma schema file
# This puts the client into the default location under /app/node_modules/.prisma/client
sed -i '/output[[:space:]]*=[[:space:]]*".*node_modules\/\.prisma\/client"/d' /app/schema.prisma

# Run yarn install to ensure that musl native bindings are installed and no dev dependencies are present
NODE_ENV="production" yarn install

# Create Affine config directory
mkdir -p /root/.affine/config/

# Clean up unneeded files
rm -rf \
/app/.yarnrc.yml \
/app/.yarn \
/app/node_modules/.cache \
/app/yarn.lock \
/etc/group- \
/etc/passwd- \
/etc/shadow- \
/root/.yarn \
/root/.cache \
/tmp/*
EOF

# Copy root filesystem
COPY rootfs /
