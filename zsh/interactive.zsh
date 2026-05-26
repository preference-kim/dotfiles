# Host-only interactive zsh additions.

if [[ -d "$HOME/.local/bin" ]]; then
  case ":$PATH:" in
    *":$HOME/.local/bin:"*) ;;
    *) export PATH="$HOME/.local/bin:$PATH" ;;
  esac
fi

if [[ -d "$HOME/.docker/completions" ]]; then
  if (( ${fpath[(Ie)$HOME/.docker/completions]} == 0 )); then
    fpath=("$HOME/.docker/completions" $fpath)
  fi

  if (( ! ${+_comps} )); then
    autoload -Uz compinit
    compinit
  fi
fi

export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
if [[ -s "$NVM_DIR/nvm.sh" ]] && ! typeset -f nvm >/dev/null 2>&1; then
  source "$NVM_DIR/nvm.sh"
fi
if [[ -s "$NVM_DIR/bash_completion" ]] && ! typeset -f _nvm >/dev/null 2>&1; then
  source "$NVM_DIR/bash_completion"
fi

if [[ -r "$HOME/powerlevel10k/powerlevel10k.zsh-theme" ]] && (( ! ${+functions[p10k]} )); then
  source "$HOME/powerlevel10k/powerlevel10k.zsh-theme"
  [[ ! -r "$HOME/.p10k.zsh" ]] || source "$HOME/.p10k.zsh"
fi

if ! typeset -f conda >/dev/null 2>&1; then
  if [[ -x "$HOME/miniconda3/bin/conda" ]]; then
    __dotfiles_conda_setup="$("$HOME/miniconda3/bin/conda" shell.zsh hook 2>/dev/null)"
    if [[ $? -eq 0 ]]; then
      eval "$__dotfiles_conda_setup"
    elif [[ -r "$HOME/miniconda3/etc/profile.d/conda.sh" ]]; then
      source "$HOME/miniconda3/etc/profile.d/conda.sh"
    else
      export PATH="$HOME/miniconda3/bin:$PATH"
    fi
    unset __dotfiles_conda_setup
  elif [[ -r "$HOME/miniconda3/etc/profile.d/conda.sh" ]]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
  fi
fi

_dotfiles_set_cursor_style() {
  [[ -t 1 ]] || return 0
  command tput cnorm >/dev/null 2>&1 || true
  printf '\033[?25h\033[1 q'
}

autoload -Uz add-zsh-hook
add-zsh-hook -d precmd _dotfiles_set_cursor_style >/dev/null 2>&1 || true
add-zsh-hook precmd _dotfiles_set_cursor_style

alias clear='command clear && _dotfiles_set_cursor_style'

codex() {
  # Codex's alternate screen does not leave the previous conversation in terminal scrollback,
  # so default invocations stay inline unless the command behavior changes upstream.
  command codex --no-alt-screen "$@"
}

_dotfiles_zsh_source="${${(%):-%x}:A}"
_dotfiles_root="${_dotfiles_zsh_source:h:h}"
if [[ -x "$_dotfiles_root/scripts/install-openfortivpn-service.sh" ]]; then
  alias refreshvpn="sudo $_dotfiles_root/scripts/install-openfortivpn-service.sh"
fi
unset _dotfiles_zsh_source _dotfiles_root
