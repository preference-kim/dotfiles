### Hugging Face authentication

Use bare `hf auth whoami` to check the host's standard credential store. Check
whether `HF_TOKEN` or `HUGGING_FACE_HUB_TOKEN` overrides it without printing their
values. Verify persistent authentication with those overrides absent.

If the stored credential is missing or invalid, report the authentication
prerequisite. Synchronize it only when the user explicitly requests HF credential
setup, repair or synchronization; daily and generic agent refreshes do not fetch
or apply private credentials. For that authorized action, read the canonical
[private synchronization protocol](../skills/agent-update/references/private-sync.md).
Fetch and verify the approved HF payload with the registered host's own access
and age identity. Pipe decrypted bytes directly to
`<dotfiles>/scripts/install-hf-credential`; never pass the token in argv, log it,
or save plaintext outside the standard Hugging Face store and its protected
recovery backups. The installer locates the HF CLI's Python runtime, uses its
configured credential paths and verifies mode 0600 and authentication.

Missing enrollment, tools, decryption access or failed verification is a reported
prerequisite failure. Do not fall back to historical public ciphertext, another
host's private keys, interactive login or token creation. Token rotation and
changes to the recipient population require explicit authorization.
