#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DAEMON_SCRIPT="$SCRIPT_DIR/openfortivpn-daemon.sh"
PLIST_PATH="/Library/LaunchDaemons/com.openfortivpn.plist"

if [ "$EUID" -ne 0 ]; then
    echo "sudo로 실행해주세요: sudo $0"
    exit 1
fi

killall openfortivpn 2>/dev/null && echo "기존 openfortivpn 프로세스 종료" || true

launchctl unload "$PLIST_PATH" 2>/dev/null || true

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
