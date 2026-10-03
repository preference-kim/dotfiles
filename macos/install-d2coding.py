#!/usr/bin/env python3
"""Install the pinned official D2Coding release into the current macOS account."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from zipfile import ZipFile

VERSION = '1.4.0'
ARCHIVE = 'D2Coding-Ver1.4.0-20261003.zip'
FONT = 'D2Coding-Ver1.4.0-20261003-all.ttc'
URL = f'https://github.com/naver/d2-coding-font/releases/download/VER{VERSION}/{ARCHIVE}'
SHA256 = '17e2da5e2879006eb725b87943f7988736ef8b6c9f8b84bc8e3bdbcb8dd46744'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive', type=Path, help='Use an already downloaded archive (checksum still checked)')
    args = parser.parse_args()
    if platform.system() != 'Darwin':
        parser.error('This installer targets macOS user fonts.')
    with tempfile.TemporaryDirectory(prefix='d2coding-download-') as temp:
        archive = args.archive or Path(temp) / ARCHIVE
        if not args.archive:
            subprocess.run(['curl', '--fail', '--location', '--proto', '=https', '--output', str(archive), URL], check=True)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
            raise SystemExit('Archive checksum mismatch; no fonts changed.')
        with ZipFile(archive) as z:
            data = z.read(f'D2CodingAll/{FONT}')
            license_data = z.read('OFL.txt')
        fonts = Path.home() / 'Library/Fonts'
        fonts.mkdir(parents=True, exist_ok=True)
        # Only official distribution filenames; preserve patched/renamed fonts.
        old = sorted(p for p in fonts.iterdir() if p.name.startswith(('D2Coding-Ver', 'D2CodingBold-Ver')) and p.suffix.lower() in ('.ttc', '.ttf'))
        dest = fonts / FONT
        if old == [dest] and dest.read_bytes() == data:
            print(f'D2Coding {VERSION} already installed; no changes.')
            return
        backup = Path.home() / '.local/state/d2coding' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup.mkdir(parents=True, mode=0o700)
        for p in old:
            shutil.copy2(p, backup / p.name)
        (backup / 'manifest.json').write_text(json.dumps({'version': VERSION, 'installed': str(dest), 'previous': [p.name for p in old], 'archive_sha256': SHA256}, indent=2) + '\n')
        (backup / 'OFL.txt').write_bytes(license_data)
        try:
            for p in old:
                p.unlink()
            dest.write_bytes(data)
            dest.chmod(0o644)
        except Exception:
            if dest.exists():
                dest.unlink()
            for p in old:
                shutil.copy2(backup / p.name, p)
            raise
        print(f'Installed D2Coding {VERSION}: {dest}')
        print(f'Rollback backup: {backup}')
        print('Running apps may retain cached fonts until you reopen them after saving work.')


if __name__ == '__main__':
    main()
