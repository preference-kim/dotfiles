# D2Coding on macOS

Install NAVER's official **D2Coding 1.4.0** (2026-10-03) for the current user:

```sh
python3 macos/install-d2coding.py
```

The installer pins the [official release](https://github.com/naver/d2-coding-font/releases/tag/VER1.4.0)
and verifies the archive's SHA-256 before replacing fonts. Its single TTC includes
Regular and Bold faces of both `D2Coding` and `D2Coding ligature`. Do not also install
the individual TTFs; duplicate font families can make version selection ambiguous.
Older official distribution files are backed up under `~/.local/state/d2coding/`.
Patched or renamed copies must be reviewed separately in Font Book.

## VS Code

Merge `vscode-fonts.json` into your user settings; do not replace the entire file.
The terminal retains MesloLGS NF as a fallback for Powerlevel10k/Nerd Font symbols
when that font is installed. The standard D2Coding family keeps operators literal.
To opt into programming ligatures, select `D2Coding ligature` and enable
`editor.fontLigatures`. Version 1.4.0 also supports a dotted zero through `cv01`;
for example `"editor.fontLigatures": "'cv01'"` with the standard family.

## iTerm2

Install the [dynamic profile](https://iterm2.com/documentation-dynamic-profiles.html):

```sh
mkdir -p "$HOME/Library/Application Support/iTerm2/DynamicProfiles"
cp macos/iterm2-d2coding.json "$HOME/Library/Application Support/iTerm2/DynamicProfiles/d2coding.json"
```

Back up an existing `d2coding.json` before replacing it. Choose **Profiles >
D2Coding** for a new session. In **Settings > Profiles**, select D2Coding and use
**Other Actions > Set as Default** if desired. It inherits colors, shell, and
other settings from the existing Default profile, with 13-point D2Coding and
literal operators. MesloLGS NF stays installed for missing-symbol fallback;
check your prompt icons when first selecting the new profile. Current sessions
are not switched or closed by these instructions.

## Beamer and rollback

The Beamer repository owns its bundled fonts and `theme/fonts-code.tex`; keep
that configuration with the template so PDF builds do not depend on Mac fonts.
Body and math fonts are independent of the code font.

To undo a font update, save work and close font-using apps yourself, move the
installed TTC listed in the backup's `manifest.json` out of `~/Library/Fonts`,
and copy the previous font files from that backup into `~/Library/Fonts`.
Reopen the apps. To undo the iTerm2 profile, select your old profile before
removing `DynamicProfiles/d2coding.json`. Restore only the three VS Code font
keys if you changed them; preserve other edits made since installation.
