#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SECRETS_SRC="$SCRIPT_DIR/../.secrets"
DAEMON_SRC="$SCRIPT_DIR/openfortivpn-daemon.sh"
CHECK_SRC="$SCRIPT_DIR/openfortivpn-check.sh"
WATCHDOG_SRC="$SCRIPT_DIR/openfortivpn-watchdog.sh"
INSTALL_DIR="/usr/local/etc/openfortivpn"
DAEMON_SCRIPT="$INSTALL_DIR/openfortivpn-daemon.sh"
CHECK_SCRIPT="$INSTALL_DIR/openfortivpn-check.sh"
WATCHDOG_SCRIPT="$INSTALL_DIR/openfortivpn-watchdog.sh"
SECRETS_FILE="$INSTALL_DIR/.secrets"
PLIST_LABEL="com.openfortivpn"
PLIST_PATH="/Library/LaunchDaemons/${PLIST_LABEL}.plist"
WATCHDOG_LABEL="com.openfortivpn.watchdog"
WATCHDOG_PLIST_PATH="/Library/LaunchDaemons/${WATCHDOG_LABEL}.plist"

if [ "$EUID" -ne 0 ]; then
    echo "sudo로 실행해주세요: sudo $0"
    exit 1
fi

if [ ! -f "$SECRETS_SRC" ]; then
    echo "Error: .secrets 파일이 없습니다: $SECRETS_SRC"
    exit 1
fi

if [ ! -f "$CHECK_SRC" ]; then
    echo "Error: checker 스크립트가 없습니다: $CHECK_SRC"
    exit 1
fi

if [ ! -f "$WATCHDOG_SRC" ]; then
    echo "Error: watchdog 스크립트가 없습니다: $WATCHDOG_SRC"
    exit 1
fi

# bootout이 프로세스 종료도 처리하므로 killall 불필요
launchctl bootout system/"$WATCHDOG_LABEL" 2>/dev/null || true
launchctl bootout system/"$PLIST_LABEL" 2>/dev/null || true
sleep 2

# bootout 후에도 남아있을 수 있는 프로세스 정리
killall openfortivpn 2>/dev/null || true
sleep 1

mkdir -p "$INSTALL_DIR"
cp "$DAEMON_SRC" "$DAEMON_SCRIPT"
cp "$CHECK_SRC" "$CHECK_SCRIPT"
cp "$WATCHDOG_SRC" "$WATCHDOG_SCRIPT"
cp "$SECRETS_SRC" "$SECRETS_FILE"
chown -R root:wheel "$INSTALL_DIR"
chmod 700 "$INSTALL_DIR"
chmod 700 "$DAEMON_SCRIPT"
chmod 755 "$CHECK_SCRIPT"
chmod 755 "$WATCHDOG_SCRIPT"
chmod 600 "$SECRETS_FILE"

cat > "$PLIST_PATH" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$PLIST_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$DAEMON_SCRIPT</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>ThrottleInterval</key>
    <integer>300</integer>
    <key>StandardOutPath</key>
    <string>/var/log/openfortivpn.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/openfortivpn.err</string>
</dict>
</plist>
PLIST

cat > "$WATCHDOG_PLIST_PATH" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>$WATCHDOG_LABEL</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$WATCHDOG_SCRIPT</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>VPN_CHECK_TIMEOUT</key>
        <string>3</string>
    </dict>
    <key>StartInterval</key>
    <integer>5</integer>
    <key>StandardOutPath</key>
    <string>/var/log/openfortivpn-watchdog.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/openfortivpn-watchdog.err</string>
</dict>
</plist>
PLIST

chown root:wheel "$PLIST_PATH"
chmod 644 "$PLIST_PATH"
chown root:wheel "$WATCHDOG_PLIST_PATH"
chmod 644 "$WATCHDOG_PLIST_PATH"

launchctl bootstrap system "$PLIST_PATH"
sleep 3
launchctl bootstrap system "$WATCHDOG_PLIST_PATH"

if pgrep -x openfortivpn > /dev/null; then
    echo "openfortivpn 서비스 시작 완료"
    echo "설치 경로: $INSTALL_DIR"
    echo "상태 확인:"
    echo "  $CHECK_SCRIPT"
    echo "  $CHECK_SCRIPT <ssh-alias>"
    echo "  VPN_CHECK_HOST=<host> VPN_CHECK_PORT=<port> $CHECK_SCRIPT"
    echo "watchdog:"
    echo "  launchctl print system/$WATCHDOG_LABEL"
    echo "  tail -f /var/log/openfortivpn-watchdog.log"
else
    echo "서비스 시작 실패 — 로그 확인:"
    echo "  stdout: cat /var/log/openfortivpn.log"
    echo "  stderr: cat /var/log/openfortivpn.err"
    exit 1
fi
