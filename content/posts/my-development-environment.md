---
title: "My Development Environment"
date: 2026-01-15
draft: false
description: "A walkthrough of my macOS development setup: zsh, neovim, tmux, and 80+ CLI tools — all managed from a single dotfiles repo with a one-command install."
images:
  - "images/og/my-development-environment.png"
tags: ["developer-tools"]
keywords: ["development environment", "dotfiles", "neovim", "tmux", "macos setup"]
---

Every developer I respect has a dotfiles repo. Not because the configs themselves are interesting — most of them aren't — but because maintaining one forces you to make deliberate choices about your tools. You can't version-control a setup you don't understand. The act of curating a dotfiles repo is the act of deciding what matters in your workflow and throwing everything else away.

Mine lives at [github.com/alexdjalali/dotfiles](https://github.com/alexdjalali/dotfiles). It provisions a full macOS development environment from a blank machine in a single command. This post walks through what's in it and why.

## The Philosophy

Three principles:

**One theme everywhere.** [Catppuccin Mocha](https://catppuccin.com/) in the terminal, in the editor, in tmux, in git diffs, in bat output. Visual consistency across tools isn't vanity — it reduces context-switching friction. When everything looks like it belongs together, your brain stops noticing the seams between tools and starts focusing on the work.

**Modern replacements for legacy tools.** `ls` becomes `eza`. `cat` becomes `bat`. `grep` becomes `ripgrep`. `find` becomes `fd`. `sed` becomes `sd`. `du` becomes `dust`. `top` becomes `btop`. `diff` becomes `delta`. These aren't gimmicks. They're faster, they have better defaults, and they produce output that's actually readable.

**One command, full setup.** A fresh Mac should go from "nothing installed" to "fully productive" with `./install.sh`. No manual steps. No "oh, I also need to install X." The install script is idempotent — safe to run again whenever I add something new.

## The Shell

Zsh with [Oh My Zsh](https://ohmyz.sh/), [Powerlevel10k](https://github.com/romkatv/powerlevel10k) for the prompt, and a modular config that keeps `.zshrc` clean:

```zsh
# .zshrc is a thin bootstrap that sources conf.d/ modules in order
export DOTFILES="${DOTFILES:-$HOME/dotfiles}"
for conf in "$DOTFILES/zsh/conf.d/"*.zsh(N); do
  source "$conf"
done
```

Each numbered file in `conf.d/` handles one concern — environment variables, path setup, aliases, completions, fzf config, tool initialization. When I want to change how aliases work, I open `04-aliases.zsh`. When I want to tweak fzf, I open `06-fzf.zsh`. No scrolling through a 500-line `.zshrc` looking for the right section.

The plugins are minimal and deliberate:

- [fzf-tab](https://github.com/Aloxaf/fzf-tab) — replaces zsh's default completion menu with fzf, so tab completion gets fuzzy matching and preview windows
- [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions) — ghost text from history
- [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting) — real-time command highlighting
- [zoxide](https://github.com/ajeetdsouza/zoxide) — frecency-based `cd` replacement (learns which directories you visit most)
- [atuin](https://github.com/atuinsh/atuin) — shell history with full-text search and optional sync across machines

I intentionally removed the default `git` plugin from Oh My Zsh. It defines 176 aliases, most of which I'll never use, and some of which shadow commands I actually want. My own git aliases live in `conf.d/04-aliases.zsh` where I control exactly what exists.

## tmux

I spend most of my day inside tmux. The config is hand-rolled with Catppuccin Mocha colors — no plugin themes, just raw color codes mapped to the palette:

```tmux
# Status bar
set -g status-style "bg=#181825,fg=#cdd6f4"
setw -g window-status-current-style "bg=#313244,fg=#cba6f7,bold"

# Panes
set -g pane-border-style "fg=#313244"
set -g pane-active-border-style "fg=#cba6f7"
```

Vim-style keybindings for everything: `h/j/k/l` for pane navigation, `|` and `-` for splits (instead of the unintuitive `"` and `%` defaults), `v` and `y` in copy mode. True color and undercurl support are configured so Neovim's LSP diagnostic squiggly lines render correctly inside tmux — a detail that took an embarrassing amount of time to get right:

```tmux
set -g default-terminal "tmux-256color"
set -ga terminal-overrides ",*-256color:Tc"
set -as terminal-overrides ',*:Smulx=\E[4::%p1%dm'
set -as terminal-overrides ',*:Setulc=\E[58::2::%p1%{65536}%/%d::%p1%{256}%/%{255}%&%d::%p1%{255}%&%d%;m'
```

[tmux-resurrect](https://github.com/tmux-plugins/tmux-resurrect) and [tmux-continuum](https://github.com/tmux-plugins/tmux-continuum) handle session persistence. I can reboot and come back to exactly where I left off — same windows, same panes, same working directories.

## Neovim

AstroNvim-based config, fully Lua, with 30+ plugin configurations. The key pieces:

- **LSP** for every language I work in (Go via `gopls`, Python via `basedpyright`, TypeScript via `ts_ls`, Lua via `lua_ls`, LaTeX via `texlab`)
- **DAP** (Debug Adapter Protocol) for stepping through Go and Python without leaving the editor
- **Treesitter** for syntax highlighting, text objects, and structural navigation
- **59 custom LuaSnip snippets for LaTeX** — 20 for TikZ/pgfplots, 17 for Beamer presentations, 22 for common packages and document structures

The LaTeX setup deserves a mention. I do academic writing in Neovim with [VimTeX](https://github.com/lervag/vimtex), `latexmk` for continuous compilation, and [Skim](https://skim-app.sourceforge.io/) for PDF preview with SyncTeX forward/inverse search. Click a line in the PDF, and Neovim jumps to that line in the source. Click a line in Neovim, and Skim jumps to the corresponding position in the PDF. Once you've experienced this workflow, writing LaTeX in anything else feels broken.

## Git

The `.gitconfig` is opinionated:

```gitconfig
[core]
	editor = nvim
	pager = delta
	fsmonitor = true
	untrackedCache = true

[commit]
	gpgsign = true

[delta]
	navigate = true
	side-by-side = true
	syntax-theme = "Catppuccin Mocha"

[diff]
	algorithm = histogram

[merge]
	conflictstyle = diff3

[rerere]
	enabled = true

[pull]
	rebase = true

[rebase]
	autoStash = true
	autoSquash = true
```

A few choices worth explaining:

**GPG signing on every commit.** Non-negotiable. If your commits aren't signed, anyone can impersonate you with `git config user.email`.

**Delta as the pager.** Side-by-side diffs with syntax highlighting and line numbers, themed to match everything else. `git diff` output becomes something you actually want to read.

**Histogram diff algorithm.** Produces better diffs than the default Myers algorithm, especially for moved blocks of code. Once you switch, you notice the difference immediately and never go back.

**rerere enabled.** "Reuse recorded resolution" — git remembers how you resolved a conflict and applies the same resolution automatically if it encounters the same conflict again. Essential for long-running feature branches that rebase often.

**Pull with rebase, rebase with autoStash.** No merge commits from `git pull`. If I have local changes when pulling, git stashes them automatically, rebases, and pops the stash. Clean linear history with zero effort.

## The Brewfile

Everything I install lives in one file. Running `brew bundle` on a fresh machine installs the entire stack — CLI tools, languages, casks, fonts:

```ruby
# Modern CLI Replacements
brew "eza"         # ls
brew "bat"         # cat
brew "ripgrep"     # grep
brew "fd"          # find
brew "sd"          # sed
brew "dust"        # du
brew "btop"        # top
brew "delta"       # diff
brew "xh"          # curl
brew "doggo"       # dig

# Languages
brew "go"
brew "python@3"
brew "uv"
brew "node"
brew "pnpm"
brew "oven-sh/bun/bun"

# Kubernetes
brew "kubectl"
brew "k9s"
brew "helm"
brew "kind"
brew "stern"
brew "lazydocker"
brew "dive"
brew "trivy"

# Infrastructure
brew "terraform"
brew "pgcli"
brew "mongosh"
brew "grpcurl"
```

The full Brewfile has 80+ entries. The point isn't that I use all of them every day — the point is that when I need `k9s` or `grpcurl` or `hyperfine`, it's already there. The cost of installing something unused is a few hundred megabytes of disk. The cost of needing something that isn't installed is a context switch away from the problem I'm solving.

## Raycast Scripts

[Raycast](https://www.raycast.com/) replaced Spotlight on my machine. Beyond its built-in features, I have 29 custom script commands in `~/dotfiles/raycast/` that automate common workflows:

- `focus-mode.sh` / `end-focus-mode.sh` — toggle Do Not Disturb, close distracting apps, set Slack status
- `meeting-mode.sh` — same as focus mode but opens Zoom and positions windows
- `open-project.sh` — fuzzy-find a project directory and open it in Cursor
- `lazygit-here.sh` — open lazygit in the current Finder directory
- `git-status-all.sh` — check git status across all project directories at once
- `dev-stack.sh` — start/stop the local dev stack (Docker containers, databases)
- `k8s-context.sh` — switch kubectl context without remembering cluster names
- `window-layout-coding.sh` — arrange windows into my preferred coding layout

Each script is a plain bash file with Raycast metadata in the header. No plugins, no dependencies, no framework. When something annoys me more than twice, it becomes a Raycast script.

## The Install Script

The whole thing bootstraps from a blank Mac:

```bash
git clone https://github.com/alexdjalali/dotfiles.git ~/dotfiles
cd ~/dotfiles
./install.sh
```

The script runs 15 steps: Xcode CLT, Homebrew, `brew bundle`, shell setup, Oh My Zsh with plugins, symlinks (with automatic backup of existing files), fzf integration, bat/delta Catppuccin theme, iTerm2 shell integration, directory scaffolding, TPM and tmux plugins, git-lfs, LaTeX environment, and a headless Neovim bootstrap that syncs all plugins and installs Treesitter parsers.

It's idempotent. Every step checks whether it's already been done before doing it. Symlinks check whether they already point to the right place. Homebrew checks whether it's already installed. The script produces a clean log of what it did and what it skipped:

```
[ok]    Homebrew already installed
[ok]    ~/.gitconfig -> ~/dotfiles/git/.gitconfig (already linked)
[info]  Installing Oh My Zsh plugins...
[ok]    fzf-tab already installed
[warn]  Backed up ~/.tmux.conf -> ~/.dotfiles-backup/20260115_143022/
[ok]    ~/.tmux.conf -> ~/dotfiles/tmux/.tmux.conf
```

## AI Tool Integration

The dotfiles also manage my AI coding tool configurations. The same engineering standards get symlinked into three different tools:

```
~/.claude/CLAUDE.md        -> ~/dotfiles/.claude/CLAUDE.md
~/.claude/settings.json    -> ~/dotfiles/.claude/settings.json
~/.claude/commands         -> ~/dotfiles/.claude/commands
~/.cursor/rules            -> ~/dotfiles/cursor/rules
~/.kilocode/rules          -> ~/dotfiles/kilocode/rules
```

This means my [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Cursor](https://www.cursor.com/), and [Kilo Code](https://kilocode.ai/) configurations are version-controlled alongside everything else. When I update a standard — say, adding a new quality gate or refining an architecture pattern — the change propagates to every tool the next time I open it. I wrote more about this workflow in [How I Learned to Love the Bomb](/posts/how-i-learned-to-love-the-bomb/).

## The Point

None of this is about having the fanciest terminal or the most plugins. It's about removing friction. Every tool configured here solves a specific problem I hit repeatedly: navigating code, reviewing diffs, managing containers, switching contexts, staying in flow.

The dotfiles repo is the mechanism that makes this sustainable. Without it, I'd spend my first day on any new machine reinstalling things from memory, getting half the configs wrong, and losing a day of productivity. With it, I clone one repo, run one script, and I'm working.

The whole thing is MIT-licensed and [on GitHub](https://github.com/alexdjalali/dotfiles) if any of it is useful to you.
