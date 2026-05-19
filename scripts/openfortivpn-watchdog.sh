#!/bin/bash
set -u

LABEL="${VPN_SERVICE_LABEL:-com.openfortivpn}"
CHECK_SCRIPT="${VPN_CHECK_SCRIPT:-/usr/local/etc/openfortivpn/openfortivpn-check.sh}"
WATCH_TARGET="${VPN_WATCH_TARGET:-ssh-alias-or-host}"
CHECK_TIMEOUT="${VPN_CHECK_TIMEOUT:-3}"
COOLDOWN="${VPN_WATCH_COOLDOWN:-300}"
STAMP_FILE="${VPN_WATCH_STAMP:-/var/run/openfortivpn-watchdog.last_restart}"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S%z') openfortivpn-watchdog: $*"
}

if [ ! -x "$CHECK_SCRIPT" ]; then
    log "check script is missing or not executable: $CHECK_SCRIPT"
    exit 1
fi

if VPN_CHECK_TIMEOUT="$CHECK_TIMEOUT" VPN_CHECK_SKIP_SSH=1 "$CHECK_SCRIPT" "$WATCH_TARGET"; then
    log "health check passed for $WATCH_TARGET"
    exit 0
fi

now="$(date +%s)"
last_restart=0
if [ -r "$STAMP_FILE" ]; then
    last_restart="$(cat "$STAMP_FILE" 2>/dev/null || printf '0')"
fi

case "$last_restart" in
    ''|*[!0-9]*)
        last_restart=0
        ;;
esac

elapsed=$((now - last_restart))
if [ "$elapsed" -lt "$COOLDOWN" ]; then
    log "health check failed for $WATCH_TARGET, but restart skipped; ${elapsed}s since last restart, cooldown ${COOLDOWN}s"
    exit 1
fi

printf '%s\n' "$now" > "$STAMP_FILE"
log "health check failed for $WATCH_TARGET; restarting $LABEL"

if launchctl kickstart -k "system/$LABEL"; then
    log "kickstart requested for $LABEL"
else
    log "kickstart failed for $LABEL"
    exit 1
fi

sleep 4
if VPN_CHECK_TIMEOUT="$CHECK_TIMEOUT" VPN_CHECK_SKIP_SSH=1 "$CHECK_SCRIPT" "$WATCH_TARGET"; then
    log "health check passed after restart"
    exit 0
fi

log "health check still failing after restart"
exit 1
