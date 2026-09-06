### Claude authentication

For local Claude subprocesses and reviewer workflows, use the subscription credentials managed by `claude auth login` or `/login`. Do not read or maintain `$HOME/.claude/oauth-token` as a local credential source, and do not export a static `CLAUDE_CODE_OAUTH_TOKEN` from a file.

- Remove inherited `CLAUDE_CODE_OAUTH_TOKEN`, `ANTHROPIC_API_KEY`, and `ANTHROPIC_AUTH_TOKEN` only from the Claude child process so those overrides cannot take precedence over the CLI-managed login. Do not unset credentials in the parent session.
- Treat `claude auth status` as a local configuration check, not proof that a bearer token is accepted by the service. When authentication health is material, a successful minimal non-interactive Claude request is the authoritative check.
- If the managed local login is unavailable or cannot refresh, stop and ask the user to run `claude auth login`. Do not start an authentication flow or mint and persist a replacement token without explicit authorization.
- For CI or another browserless environment that cannot use the managed login, generate a long-lived token with `claude setup-token` and inject it as `CLAUDE_CODE_OAUTH_TOKEN` through the environment's secret manager. The command prints the token but does not save it; never commit, log, or store it in a shared plaintext file.

Never print or commit any credential.
