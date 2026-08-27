# Secret management

The Hugging Face token is committed only as the `age`-encrypted
`.hf-token.age` file. Its pinned SSH recipients are public values in
`.hf-token.recipients`; the plaintext `.hf-token` source is ignored by Git.

## Use on a configured machine

Install `age` through the host's package manager. The machine must have an
on-disk RSA or Ed25519 SSH private key whose companion public key is listed in
`.hf-token.recipients`. A key registered with GitHub but absent from the machine,
a forwarded `ssh-agent`, and a hardware-held key cannot decrypt this ciphertext.

Run a Hugging Face command through the wrapper:

```bash
./scripts/with-hf-token hf auth whoami
```

The wrapper selects a matching `~/.ssh/*.pub` and private-key pair, decrypts the
token in memory, and exports `HF_TOKEN` only to the child command. If the public
companion file is absent, identify the private-key file explicitly:

```bash
HF_TOKEN_SSH_IDENTITY="$HOME/.ssh/id_ed25519" \
  ./scripts/with-hf-token hf auth whoami
```

## Add or remove a machine

Add the machine's supported GitHub SSH public key to `.hf-token.recipients`, or
remove a retired key, on a machine that already has the plaintext `.hf-token`.
Then regenerate the ciphertext:

```bash
./scripts/update-hf-token-ciphertext.sh
```

Commit the recipients file and ciphertext together. Do not fetch the GitHub
profile dynamically while decrypting: a reviewed, pinned recipient set defines
who can recover the secret. Removing a key from GitHub or from the recipients
file does not revoke an old ciphertext already copied elsewhere. If a private
key may be compromised, rotate the Hugging Face token and regenerate the
ciphertext for the retained recipients.

Never print, log, commit, or pass the plaintext token as a command-line
argument.
