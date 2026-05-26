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

exec /opt/homebrew/bin/openfortivpn "$FORTIVPN_HOST" \
    --trusted-cert="$FORTIVPN_TRUSTED_CERT" \
    --username="$FORTIVPN_USERNAME" \
    --password="$FORTIVPN_PASSWORD"
