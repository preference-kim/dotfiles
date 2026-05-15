#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SECRETS_SRC="$SCRIPT_DIR/../.secrets"
DAEMON_SRC="$SCRIPT_DIR/openfortivpn-daemon.sh"
INSTALL_DIR="/usr/local/etc/openfortivpn"
DAEMON_SCRIPT="$INSTALL_DIR/openfortivpn-daemon.sh"
SECRETS_FILE="$INSTALL_DIR/.secrets"
PLIST_PATH="/Library/LaunchDaemons/com.openfortivpn.plist"

if [ "$EUID" -ne 0 ]; then
    echo "sudo로 실행해주세요: sudo $0"
    exit 1
fi

if [ ! -f "$SECRETS_SRC" ]; then
    echo "Error: .secrets 파일이 없습니다: $SECRETS_SRC"
    exit 1
fi

killall openfortivpn 2>/dev/null && echo "기존 openfortivpn 프로세스 종료" || true

launchctl unload "$PLIST_PATH" 2>/dev/null || true

mkdir -p "$INSTALL_DIR"
cp "$DAEMON_SRC" "$DAEMON_SCRIPT"
cp "$SECRETS_SRC" "$SECRETS_FILE"
chmod 700 "$INSTALL_DIR"
chmod 700 "$DAEMON_SCRIPT"
chmod 600 "$SECRETS_FILE"

cat > "$PLIST_PATH" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openfortivpn</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>$DAEMON_SCRIPT</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/var/log/openfortivpn.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/openfortivpn.err</string>
</dict>
</plist>
PLIST

launchctl load "$PLIST_PATH"
sleep 2

if pgrep -x openfortivpn > /dev/null; then
    echo "openfortivpn 서비스 시작 완료"
else
    echo "서비스 시작 실패 — 로그 확인: cat /var/log/openfortivpn.err"
    exit 1
fi
