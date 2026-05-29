# Dotfiles Agent Guide

This repository is the source of truth for host-level dotfiles and small host
maintenance scripts. Keep changes portable, conservative, and safe to publish.

## Working Rules

- Do not add secrets, passwords, tokens, private keys, company hostnames,
  internal server names, private IPs, or personal mount paths.
- Keep environment-specific aliases and shell shortcuts out of tracked files
  unless they are guarded by file or directory existence checks.
- Prefer optional loading for tools that may not be installed on every host.
- Keep `kits` and other container-specific setup separate from this host
  dotfiles repository.
- Avoid rewriting unrelated setup while making a targeted change.

## Shell and tmux

- Host zsh additions live in `zsh/interactive.zsh`.
- Load optional shell integrations only when their files or directories exist.
- Preserve the blinking block cursor behavior through `_dotfiles_set_cursor_style`
  and the `precmd` hook.
- Keep the `codex` wrapper defaulting to `--no-alt-screen` so terminal and tmux
  scrollback retain the previous conversation.
- Host tmux settings should keep mouse support, a large history limit,
  `SSH_AUTH_SOCK`, `SSH_CONNECTION`, and `DISPLAY` environment updates, plus TPM
  with sensible/resurrect/continuum plugins.

## OpenFortiVPN Scripts

The OpenFortiVPN launchd setup lives in `scripts/`.

- `scripts/openfortivpn-daemon.sh` starts OpenFortiVPN using the installed
  `.secrets` file; do not hardcode VPN endpoints, usernames, or certificate
  hashes in the script. It waits (up to `FORTIVPN_READY_TIMEOUT`, default 60s)
  for the network and gateway DNS to be ready before launching, so a boot or
  reconnect race does not fast-fail into the launchd throttle window. The
  LaunchDaemon uses a short `ThrottleInterval` (15s) as a backstop, so the VPN
  recovers within seconds after a reboot or disconnect.
- `scripts/install-openfortivpn-service.sh` installs the daemon, checker, and
  watchdog scripts under `/usr/local/etc/openfortivpn`, writes LaunchDaemons,
  and restarts the service.
- `scripts/openfortivpn-check.sh` checks the VPN process, `ppp0`, route
  selection, TCP reachability, and optional SSH reachability.
- `.secrets.example` documents the required local-only keys. Keep real values
  in ignored `.secrets`.

Run the installer only when a VPN service restart is intended:

```sh
sudo scripts/install-openfortivpn-service.sh
```

Use the checker before restarting VPN when SSH over VPN is flaky:

```sh
scripts/openfortivpn-check.sh
scripts/openfortivpn-check.sh <ssh-alias>
VPN_CHECK_HOST=<host> VPN_CHECK_PORT=<port> scripts/openfortivpn-check.sh
VPN_CHECK_ROUTE_TARGET=<ip> scripts/openfortivpn-check.sh
```

Do not put VPN passwords directly on the command line. They can be captured in
shell history and process listings. Keep credentials in `.secrets`, and do not
commit that file.
