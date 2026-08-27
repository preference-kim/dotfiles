#!/usr/bin/env bash

set -euo pipefail
set +x

SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(git -C "$SCRIPT_DIR/.." rev-parse --show-toplevel)
TOKEN_FILE="$REPO_ROOT/.hf-token"
RECIPIENTS_FILE="$REPO_ROOT/.hf-token.recipients"
ENCRYPTED_FILE="$REPO_ROOT/.hf-token.age"

if ! command -v age >/dev/null 2>&1; then
    echo "Error: age is required to encrypt the Hugging Face token." >&2
    exit 1
fi
if [[ ! -r "$TOKEN_FILE" ]]; then
    echo "Error: $TOKEN_FILE must exist and be readable." >&2
    exit 1
fi
if [[ ! -r "$RECIPIENTS_FILE" ]]; then
    echo "Error: $RECIPIENTS_FILE must exist and be readable." >&2
    exit 1
fi

token=$(<"$TOKEN_FILE")
if [[ ! "$token" =~ ^hf_[A-Za-z0-9]+$ ]]; then
    unset token
    echo "Error: .hf-token is not a Hugging Face user access token." >&2
    exit 1
fi
unset token

temporary_file=$(mktemp "$REPO_ROOT/.hf-token.age.tmp.XXXXXX")
trap 'unlink "$temporary_file" 2>/dev/null || true' EXIT
age --encrypt --armor --recipients-file "$RECIPIENTS_FILE" \
    --output "$temporary_file" "$TOKEN_FILE"
chmod 600 "$temporary_file"
mv "$temporary_file" "$ENCRYPTED_FILE"
trap - EXIT

echo "Updated .hf-token.age for the pinned SSH recipients."
