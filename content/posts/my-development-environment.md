---
title: "My Development Environment"
date: 2026-01-15
draft: false
description: "A tour of my macOS setup (zsh, Neovim, tmux and 80-odd command-line tools), all of it kept in one dotfiles repo that installs with a single command."
images:
  - "images/og/my-development-environment.png"
tags: ["developer-tools"]
keywords: ["development environment", "dotfiles", "neovim", "tmux", "macos setup"]
---

Every developer I respect keeps a dotfiles repo. The configs themselves are rarely interesting (most people's aren't, mine included), but keeping them under version control forces you to make deliberate choices about your tools, because you can't very well version a setup you don't understand. Curating a dotfiles repo amounts to deciding what matters in your workflow and throwing the rest away.

Mine lives at [github.com/alexdjalali/dotfiles](https://github.com/alexdjalali/dotfiles), and it turns a blank Mac into a full development environment with a single command. What follows is a tour of what's in it and, where I can justify it, why.

## The Philosophy

The whole thing rests on three principles, and I'll admit up front that the first one is partly aesthetic.

I use one theme everywhere: [Catppuccin Mocha](https://catppuccin.com/) in the terminal, the editor, tmux, git diffs and `bat`. I would like to claim this is about reducing the friction of switching contexts, and it is (when everything looks like it belongs together, you stop noticing the seams between tools), but I also just like how it looks.

I replace the old Unix tools with modern ones wherever a good replacement exists: `eza` for `ls`, `bat` for `cat`, `ripgrep` for `grep`, `fd` for `find`, `sd` for `sed`, `dust` for `du`, `btop` for `top` and `delta` for `diff`. None of these are gimmicks. They're faster, their defaults are better, and their output is something a person can actually read.

And a fresh Mac should go from nothing installed to fully productive with `./install.sh`, with no manual steps and no "oh, I also need to install X" the next morning. The script is idempotent, so I can safely run it again whenever I add something.

## The Shell

Zsh with [Oh My Zsh](https://ohmyz.sh/), [Powerlevel10k](https://github.com/romkatv/powerlevel10k) for the prompt, and a modular config that keeps `.zshrc` clean:

```zsh
# .zshrc is a thin bootstrap that sources conf.d/ modules in order
export DOTFILES="${DOTFILES:-$HOME/dotfiles}"
for conf in "$DOTFILES/zsh/conf.d/"*.zsh(N); do
  source "$conf"
done
```

Each numbered file in `conf.d/` handles one concern (environment variables, the path, aliases, completions, fzf, tool initialization), so when I want to change an alias I open `04-aliases.zsh`, and when I want to tweak fzf I open `06-fzf.zsh`. Nobody should have to scroll through a 500-line `.zshrc` looking for the right section.

The plugins are few, and each one is there on purpose:

- [fzf-tab](https://github.com/Aloxaf/fzf-tab): replaces zsh's default completion menu with fzf, so tab completion gets fuzzy matching and preview windows
- [zsh-autosuggestions](https://github.com/zsh-users/zsh-autosuggestions): ghost text from history
- [zsh-syntax-highlighting](https://github.com/zsh-users/zsh-syntax-highlighting): real-time command highlighting
- [zoxide](https://github.com/ajeetdsouza/zoxide): frecency-based `cd` replacement (learns which directories you visit most)
- [atuin](https://github.com/atuinsh/atuin): shell history with full-text search and optional sync across machines

I removed Oh My Zsh's default `git` plugin on purpose. It defines 176 aliases, most of which I will never use and a few of which shadow commands I actually want. My own git aliases live in `conf.d/04-aliases.zsh`, where I know exactly what exists.

## tmux

I spend most of my day inside tmux. Its config is hand-rolled, with the Catppuccin colors written in as raw codes rather than pulled from a theme plugin:

```tmux
# Status bar
set -g status-style "bg=#181825,fg=#cdd6f4"
setw -g window-status-current-style "bg=#313244,fg=#cba6f7,bold"

# Panes
set -g pane-border-style "fg=#313244"
set -g pane-active-border-style "fg=#cba6f7"
```

The keybindings are Vim-style throughout: `h/j/k/l` to move between panes, `|` and `-` for splits (in place of the frankly baffling `"` and `%` defaults), and `v` and `y` in copy mode. True color and undercurl are configured so that Neovim's squiggly LSP diagnostics render properly inside tmux, a detail that took me an embarrassingly long time to get right:

```tmux
set -g default-terminal "tmux-256color"
set -ga terminal-overrides ",*-256color:Tc"
set -as terminal-overrides ',*:Smulx=\E[4::%p1%dm'
set -as terminal-overrides ',*:Setulc=\E[58::2::%p1%{65536}%/%d::%p1%{256}%/%{255}%&%d::%p1%{255}%&%d%;m'
```

[tmux-resurrect](https://github.com/tmux-plugins/tmux-resurrect) and [tmux-continuum](https://github.com/tmux-plugins/tmux-continuum) take care of persistence, so I can reboot and come back to exactly the windows, panes and working directories I left.

## Neovim

The editor config is built on AstroNvim, written entirely in Lua, with configurations for 30-odd plugins. The pieces that matter most are these:

- **LSP** for every language I work in (Go via `gopls`, Python via `basedpyright`, TypeScript via `ts_ls`, Lua via `lua_ls`, LaTeX via `texlab`)
- **DAP** (Debug Adapter Protocol) for stepping through Go and Python without leaving the editor
- **Treesitter** for syntax highlighting, text objects, and structural navigation
- **59 custom LuaSnip snippets for LaTeX**: 20 for TikZ/pgfplots, 17 for Beamer presentations, 22 for common packages and document structures

The LaTeX setup deserves a word, if only because I wrote a dissertation full of lambda terms and proof trees and have opinions about it. I do academic writing in Neovim with [VimTeX](https://github.com/lervag/vimtex), `latexmk` compiling continuously, and [Skim](https://skim-app.sourceforge.io/) for the PDF with SyncTeX search in both directions. Click a line in the PDF and Neovim jumps to it in the source; click a line in Neovim and Skim jumps to the corresponding spot in the PDF. Once you've worked this way, writing LaTeX in anything else feels broken.

## Git

My `.gitconfig` is, I'll grant, opinionated:

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

A few of those choices deserve an explanation.

Every commit is GPG-signed. I don't consider that optional: if your commits aren't signed, anyone can impersonate you with `git config user.email`.

Delta is the pager, which gives me side-by-side diffs with syntax highlighting and line numbers, themed like everything else. It turns `git diff` into something you might actually want to read.

The diff algorithm is histogram rather than the default Myers. It produces better diffs, especially when blocks of code move, and once you've switched you notice the difference immediately.

`rerere` ("reuse recorded resolution") is on, so git remembers how I resolved a conflict and applies the same resolution if the same conflict comes up again. On a long-running branch that rebases often, that is close to essential.

Finally, `git pull` rebases and rebasing auto-stashes. There are no merge commits from pulling, and if I have local changes, git stashes them, rebases and pops them back without my having to think about it. The history stays linear for free.

## The Brewfile

Everything I install lives in one file, and `brew bundle` on a fresh machine installs the lot (command-line tools, languages, casks and fonts):

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

The full Brewfile has more than 80 entries. I certainly don't use all of them every day; the point is that when I need `k9s` or `grpcurl` or `hyperfine`, it's already there. Installing something I never use costs a few hundred megabytes of disk. Needing something that isn't installed costs a context switch away from whatever problem I was in the middle of, which is the more expensive of the two by some margin.

## Raycast Scripts

[Raycast](https://www.raycast.com/) replaced Spotlight on my machine some time ago. On top of what it does out of the box, I keep 29 script commands in `~/dotfiles/raycast/` for the things I do often:

- `focus-mode.sh` / `end-focus-mode.sh`: toggle Do Not Disturb, close distracting apps, set Slack status
- `meeting-mode.sh`: same as focus mode but opens Zoom and positions windows
- `open-project.sh`: fuzzy-find a project directory and open it in Cursor
- `lazygit-here.sh`: open lazygit in the current Finder directory
- `git-status-all.sh`: check git status across all project directories at once
- `dev-stack.sh`: start/stop the local dev stack (Docker containers, databases)
- `k8s-context.sh`: switch kubectl context without remembering cluster names
- `window-layout-coding.sh`: arrange windows into my preferred coding layout

Each one is a plain bash file with Raycast's metadata in the header, with no plugins or dependencies behind it. My rule, such as it is: when something annoys me more than twice, it becomes a Raycast script.

## The Install Script

All of it bootstraps from a blank Mac:

```bash
git clone https://github.com/alexdjalali/dotfiles.git ~/dotfiles
cd ~/dotfiles
./install.sh
```

The script runs 15 steps: the Xcode command-line tools, Homebrew, `brew bundle`, the shell, Oh My Zsh and its plugins, symlinks (backing up whatever was there before), fzf, the Catppuccin theme for `bat` and delta, iTerm2's shell integration, directory scaffolding, TPM and the tmux plugins, git-lfs, the LaTeX environment, and finally a headless Neovim run that syncs every plugin and installs the Treesitter parsers.

Every step checks whether it has already been done before doing it (a symlink checks where it points, Homebrew checks whether it's installed), which is what makes the script safe to rerun. It logs what it did and what it skipped:

```
[ok]    Homebrew already installed
[ok]    ~/.gitconfig -> ~/dotfiles/git/.gitconfig (already linked)
[info]  Installing Oh My Zsh plugins...
[ok]    fzf-tab already installed
[warn]  Backed up ~/.tmux.conf -> ~/.dotfiles-backup/20260115_143022/
[ok]    ~/.tmux.conf -> ~/dotfiles/tmux/.tmux.conf
```

## AI Tool Integration

The repo also manages the configuration for my AI coding tools, and the same engineering standards are symlinked into three of them:

```
~/.claude/CLAUDE.md        -> ~/dotfiles/.claude/CLAUDE.md
~/.claude/settings.json    -> ~/dotfiles/.claude/settings.json
~/.claude/commands         -> ~/dotfiles/.claude/commands
~/.cursor/rules            -> ~/dotfiles/cursor/rules
~/.kilocode/rules          -> ~/dotfiles/kilocode/rules
```

So my [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Cursor](https://www.cursor.com/) and [Kilo Code](https://kilocode.ai/) configurations are versioned alongside everything else. When I change a standard (a new quality gate, say, or a refinement to an architecture pattern), every tool picks it up the next time I open it. I wrote more about how that works in [How I Learned to Love the Bomb](/posts/how-i-learned-to-love-the-bomb/).

## The Point

I should say, in fairness to anyone who has read this far, that none of it is about having the fanciest terminal or the most plugins. Every tool here is configured because it solves a problem I kept running into, whether that's finding my way around code, reading diffs, wrangling containers or just staying in the flow of the work.

What makes it last is the repo itself. Without it, my first day on any new machine would be spent reinstalling things from memory and getting half the configs wrong. With it, I clone one repository, run one script, and get on with my day.

It's all MIT-licensed and [on GitHub](https://github.com/alexdjalali/dotfiles). Take whatever is useful to you (and if you find a better diff algorithm than histogram, do let me know).
