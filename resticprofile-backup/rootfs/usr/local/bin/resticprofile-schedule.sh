#!/usr/bin/with-contenv bashio

set -euo pipefail

PROFILES="/usr/local/etc/resticprofile/profiles.yaml"

# ensure the correct scheduler is set
yq '.global.scheduler = "crond"' /config/profiles.yaml > "$PROFILES"
cp /config/password.txt /usr/local/etc/resticprofile/password.txt

resticprofile -c "$PROFILES" profiles --quiet | \
  awk '/^[[:space:]]+[a-zA-Z0-9_-]+:/ { gsub(":", "", $1); print $1 }' | \
  while read -r profile; do
    bashio::log.info "Initializing profile: $profile"
    if ! resticprofile -c "$PROFILES" "${profile}.snapshots" > /dev/null 2>&1; then
      resticprofile -c "$PROFILES" "${profile}.init"
    else
      bashio::log.info "Profile '$profile' already initialized, skipping."
    fi
done

bashio::log.info "Writing cron schedules"
resticprofile -c "$PROFILES" schedule --all
