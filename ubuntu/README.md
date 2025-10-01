# Setup Ubuntu

Scripts for configuring the Ubuntu development environment can be found here. Any other miscellaneous issues related to Ubuntu are documented in the [`./others`](./others/) directory.

## Program Installation

Run [`setup_ubuntu.sh``](./setup_ubuntu.sh)

### List of items

- IDEs / Browsers
    - Microsoft Visual Studio Code
    - Google Chrome
- Productivities
    - Microsoft Todo
    - TeamViewer
    - Dropbox
    - kolourpaint
    - peek
- Dev essentials
    - Python3
    - miniconda3
    - C++
- Terminal / Shell
    - tilix
    - zsh
    - <del>powerlevel10k</del> -> _please install it manually_: [LINK](https://github.com/romkatv/powerlevel10k#meslo-nerd-font-patched-for-powerlevel10k)
    - tmux
- Container
    - Docker

---

## Simplication for server access

By creating an `rsa_id`, configuring `~/.ssh/config`, and using `ssh-copy-id`, we can streamline server access using a simple ID, eliminating the need for a password.

Use [`sshconfig.sh`](./sshconfig.sh) with revision
Before run it, the following commands may be needed.

```bash
  chmod +x ./sshconfig.sh
```
