#!/bin/bash
set -u

SSH_TARGET="${VPN_CHECK_SSH_TARGET:-${1:-}}"
HOST="${VPN_CHECK_HOST:-}"
PORT="${VPN_CHECK_PORT:-}"
ROUTE_TARGET="${VPN_CHECK_ROUTE_TARGET:-}"
CONNECT_TIMEOUT="${VPN_CHECK_TIMEOUT:-5}"
SKIP_SSH="${VPN_CHECK_SKIP_SSH:-0}"

failures=0

ok() {
    echo "OK: $*"
}

warn() {
    echo "WARN: $*" >&2
}

fail() {
    echo "FAIL: $*" >&2
    failures=$((failures + 1))
}

need_command() {
    if ! command -v "$1" >/dev/null 2>&1; then
        fail "missing command: $1"
        return 1
    fi
    return 0
}

run_with_timeout() {
    local seconds="$1"
    shift

    /usr/bin/perl -e 'alarm shift; exec @ARGV' "$seconds" "$@"
}

resolve_ssh_target() {
    local target="$1"
    local ssh_config

    if ! need_command ssh; then
        return
    fi

    if ! ssh_config="$(ssh -G "$target" 2>/dev/null)"; then
        fail "ssh config could not be resolved for $target"
        return
    fi

    if [ -z "$HOST" ]; then
        HOST="$(printf '%s\n' "$ssh_config" | awk '$1 == "hostname" { print $2; exit }')"
    fi

    if [ -z "$PORT" ]; then
        PORT="$(printf '%s\n' "$ssh_config" | awk '$1 == "port" { print $2; exit }')"
    fi
}

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

check_route() {
    local target="$1"
    local route_out

    if [ -z "$target" ]; then
        warn "route check skipped: no route target"
        return
    fi

    if ! need_command route; then
        return
    fi

    if ! route_out="$(route -n get "$target" 2>&1)"; then
        fail "route lookup failed for $target: $route_out"
        return
    fi

    printf '%s\n' "$route_out" | sed 's/^/  /'

    if printf '%s\n' "$route_out" | grep -q 'interface: ppp0'; then
        ok "route to $target uses ppp0"
    else
        fail "route to $target does not use ppp0"
    fi
}

check_tcp_port() {
    local host="$1"
    local port="$2"
    local nc_out

    if [ -z "$host" ] || [ -z "$port" ]; then
        warn "tcp check skipped: host or port is empty"
        return
    fi

    if ! need_command nc; then
        return
    fi

    if nc_out="$(run_with_timeout "$((CONNECT_TIMEOUT + 2))" nc -vz -G "$CONNECT_TIMEOUT" -w "$CONNECT_TIMEOUT" "$host" "$port" 2>&1)"; then
        ok "tcp connect to $host:$port succeeded"
    else
        fail "tcp connect to $host:$port failed: $nc_out"
    fi
}

check_ssh() {
    local target="$1"
    local ssh_out

    if [ "$SKIP_SSH" = "1" ]; then
        warn "ssh check skipped: VPN_CHECK_SKIP_SSH=1"
        return
    fi

    if [ -z "$target" ]; then
        warn "ssh check skipped: VPN_CHECK_SSH_TARGET is empty"
        return
    fi

    if ! need_command ssh; then
        return
    fi

    if ssh_out="$(run_with_timeout "$((CONNECT_TIMEOUT + 2))" ssh -o BatchMode=yes -o ConnectTimeout="$CONNECT_TIMEOUT" -o ConnectionAttempts=1 "$target" true 2>&1)"; then
        ok "ssh $target succeeded"
    else
        fail "ssh $target failed: $ssh_out"
    fi
}

if pgrep -x openfortivpn >/dev/null 2>&1; then
    ok "openfortivpn process is running"
else
    fail "openfortivpn process is not running"
fi

if ifconfig ppp0 >/dev/null 2>&1; then
    ok "ppp0 interface exists"
else
    fail "ppp0 interface is missing"
fi

if [ -n "$SSH_TARGET" ]; then
    resolve_ssh_target "$SSH_TARGET"
fi

if [ -z "$PORT" ]; then
    PORT=22
fi

if [ -n "$HOST" ]; then
    resolved_ip="$(resolve_host_ip "$HOST")"
    if [ -n "$resolved_ip" ]; then
        ok "$HOST resolves to $resolved_ip"
        if [ -z "$ROUTE_TARGET" ]; then
            ROUTE_TARGET="$resolved_ip"
        fi
    else
        fail "$HOST could not be resolved"
    fi
fi

check_route "$ROUTE_TARGET"
check_tcp_port "$HOST" "$PORT"
check_ssh "$SSH_TARGET"

if [ "$failures" -eq 0 ]; then
    ok "openfortivpn health check passed"
else
    echo "FAIL: $failures check(s) failed" >&2
fi

exit "$failures"
