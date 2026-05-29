#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SECRETS_FILE="${FORTIVPN_SECRETS_FILE:-$SCRIPT_DIR/.secrets}"
if [ ! -f "$SECRETS_FILE" ] && [ -f "$SCRIPT_DIR/../.secrets" ]; then
    SECRETS_FILE="$SCRIPT_DIR/../.secrets"
fi

if [ ! -f "$SECRETS_FILE" ]; then
    echo "Error: .secrets file not found at $SECRETS_FILE" >&2
    exit 1
fi
FORTIVPN_HOST_ENV="${FORTIVPN_HOST:-}"
FORTIVPN_TRUSTED_CERT_ENV="${FORTIVPN_TRUSTED_CERT:-}"
FORTIVPN_USERNAME_ENV="${FORTIVPN_USERNAME:-}"
FORTIVPN_PASSWORD_ENV="${FORTIVPN_PASSWORD:-}"
source "$SECRETS_FILE"

[ -z "$FORTIVPN_HOST_ENV" ] || FORTIVPN_HOST="$FORTIVPN_HOST_ENV"
[ -z "$FORTIVPN_TRUSTED_CERT_ENV" ] || FORTIVPN_TRUSTED_CERT="$FORTIVPN_TRUSTED_CERT_ENV"
[ -z "$FORTIVPN_USERNAME_ENV" ] || FORTIVPN_USERNAME="$FORTIVPN_USERNAME_ENV"
[ -z "$FORTIVPN_PASSWORD_ENV" ] || FORTIVPN_PASSWORD="$FORTIVPN_PASSWORD_ENV"
unset FORTIVPN_HOST_ENV FORTIVPN_TRUSTED_CERT_ENV FORTIVPN_USERNAME_ENV FORTIVPN_PASSWORD_ENV

require_secret() {
    local name="$1"
    if [ -z "${!name:-}" ]; then
        echo "Error: $name is required in $SECRETS_FILE" >&2
        exit 1
    fi
}

require_secret FORTIVPN_HOST
require_secret FORTIVPN_TRUSTED_CERT
require_secret FORTIVPN_USERNAME
require_secret FORTIVPN_PASSWORD

# Wait for the network and DNS to be ready before launching openfortivpn.
# At early boot (or right after a disconnect) the gateway hostname may not yet
# resolve; exec'ing immediately would fail with getaddrinfo and launchd would
# treat it as a fast-fail and throttle the service. A bounded readiness loop
# absorbs that transient window. If it times out we exec anyway and let launchd
# retry (the service uses a short ThrottleInterval as a backstop).
GATEWAY_HOST="${FORTIVPN_HOST%%:*}"
READY_TIMEOUT="${FORTIVPN_READY_TIMEOUT:-60}"

resolve_host_ip() {
    local host="$1"
    local ip=""

    if command -v dscacheutil >/dev/null 2>&1; then
        ip="$(dscacheutil -q host -a name "$host" 2>/dev/null | awk '/ip_address:/ { print $2; exit }')"
    fi

    if [ -z "$ip" ] && command -v dig >/dev/null 2>&1; then
        ip="$(dig +short "$host" A 2>/dev/null | awk 'NF { print; exit }')"
    fi

    if [ -z "$ip" ] && command -v host >/dev/null 2>&1; then
        ip="$(host "$host" 2>/dev/null | awk '/has address/ { print $4; exit }')"
    fi

    printf '%s' "$ip"
}

deadline=$(( $(date +%s) + READY_TIMEOUT ))
while [ "$(date +%s)" -lt "$deadline" ]; do
    if route -n get default >/dev/null 2>&1 && [ -n "$(resolve_host_ip "$GATEWAY_HOST")" ]; then
        break
    fi
    echo "waiting for network/DNS to resolve gateway..."
    sleep 2
done

exec /opt/homebrew/bin/openfortivpn "$FORTIVPN_HOST" \
    --trusted-cert="$FORTIVPN_TRUSTED_CERT" \
    --username="$FORTIVPN_USERNAME" \
    --password="$FORTIVPN_PASSWORD"
