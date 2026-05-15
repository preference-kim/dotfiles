#!/bin/bash
SECRETS_FILE="$(dirname "$0")/.secrets"
if [ ! -f "$SECRETS_FILE" ]; then
    echo "Error: .secrets file not found at $SECRETS_FILE" >&2
    exit 1
fi
source "$SECRETS_FILE"

exec /opt/homebrew/bin/openfortivpn vpn.example.com \
    --trusted-cert="trusted-cert-hash" \
    --username="username" \
    --password="$FORTIVPN_PASSWORD"
