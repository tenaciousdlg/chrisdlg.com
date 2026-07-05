---
title: "My Dotfiles Were a Stale Fork, and Other Things I Found Cleaning House"
date: 2026-07-05
description: "Rebuilding a personal dotfiles repo from scratch turned into finding live secrets in shell history, a two-year-old forgotten Vault container, and 80GB of disk I didn't need to be carrying."
tags: [dotfiles, zsh, vault, security, tooling]
draft: false
---

I asked for a review of my home directory expecting a list of stale files. What I actually had was a security review that happened to be disguised as spring cleaning.

## The dotfiles repo was a fossil

`tenaciousdlg/dotfiles` on GitHub was a fork of [mathiasbynens/dotfiles](https://github.com/mathiasbynens/dotfiles) — a great repo, last touched by me in April 2024. It was bash-oriented: `.bash_profile`, `.bash_prompt`, generic aliases like `d="cd ~/Documents/Dropbox"`. My actual daily driver is zsh, oh-my-zsh, and Powerlevel10k, with a completely different `.aliases` file. None of it overlapped. If this laptop died, my real shell config — the one I actually use every day — had zero backup anywhere.

Worse: `.zshrc` never actually sourced `.aliases`. It had been silently not-loading my own aliases for who knows how long, working anyway through pure muscle memory.

The fix was straightforward in principle: retire the fork, build a real repo that mirrors what I actually run, and manage it with symlinks instead of copy-paste.

```bash
link() {
  local src="$1" dest="$2"
  if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then
    return
  fi
  if [ -e "$dest" ]; then
    mv "$dest" "$dest.bak"
  fi
  ln -s "$src" "$dest"
}
```

`bootstrap.sh` symlinks `.zshrc`, `.aliases`, `.gitconfig`, `.vimrc`, `.p10k.zsh`, and a `bin/` directory straight into `$HOME`. The repo and the live config are now the same file. Editing one edits the other. There's no "sync" step to forget.

## The part that actually mattered: secrets were living in shell history

While pulling together what should go in the repo, I ran a frequency analysis on `.zsh_history` — 10,000+ commands, extended history format. Buried in `export` blocks: an Okta API token, a Teleport SCIM client secret, a Slack bot token, several sets of temporary AWS credentials, all pasted directly into the terminal at some point because that's the fastest way to get a Terraform demo environment running *right now*.

That's the real problem dotfiles hygiene was masking. Shell history is not a secrets store. It's an unencrypted, append-only, 600-permission text file that syncs to every backup and outlives whatever context made you think it was fine to paste that token in the first place.

The fix isn't "don't paste secrets" — that's not a fix, that's a wish. The fix is making the correct behavior the path of least resistance: `direnv` loads a per-project `.envrc` automatically on `cd`, so instead of re-exporting the same `TF_VAR_*` block by hand every time, you write it once and it just loads. The only remaining question was where those secrets should actually come from.

## I already had a Vault. I'd forgotten about it.

My first instinct was 1Password — I use it daily anyway. But the person actually holding the secrets should populate a secrets store, not the assistant helping me clean up dotfiles, so I asked for options instead of an implementation. That's when I remembered: I had a HashiCorp Vault running in a Docker container, spun up two years ago for a one-off Terraform + Teleport database cert use case, sitting untouched ever since.

```
❯ docker ps -a
...
aeb619c41abb   hashicorp/vault   "vault server -confi…"   2 years ago   Up 6 days   0.0.0.0:8200->8200/tcp   vault
```

Up 6 days — it had been quietly restarting itself (`restart: always`) this entire time without me noticing. Checked its status:

```
❯ vault status
Sealed          true
Total Shares    6
Threshold       3
```

Sealed, as Shamir-sealed Vault always is after a restart, needing 3 of 6 unseal keys. I didn't remember where I'd saved them. A search through the same shell history that had leaked all those other secrets turned up the exact `for key in ...; do vault operator unseal "$key"; done` loop I'd used to bring it up the last time. Three keys, matching the threshold exactly. Unsealed it, and the cached root token in `~/.vault-token` still worked — full access to a two-year-old Vault instance, still holding the original `mongo`/`mysql` cert data from whatever it was originally built for.

I gave it a new job: a `secret/demo/*` namespace for the Terraform demo credentials, and an `.envrc` template that pulls them via `vault kv get` instead of `export`:

```bash
export TF_VAR_okta_api_token="$(vault kv get -field=api_token secret/demo/okta-integrator)"
```

Same convenience as hand-pasting, none of the plaintext-in-history risk. The irony of finding the fix to a secrets-hygiene problem by way of a secrets-hygiene problem in the same log file was not lost on me.

## What else was just sitting there

Once you're auditing one thing, you end up auditing everything. The tally, once I started actually measuring instead of assuming:

| What | Reclaimed |
|---|---|
| A 49GB "media to review" folder, moved to external storage | 49GB off the internal disk |
| Three UTM virtual machines I assumed were my "test Windows sometime" VM | 26GB — they were all Ubuntu, untouched since January 2024. There was no Windows VM. There never had been one recently. |
| `minikube`, fully redundant with `kind`, and already broken | 2.2GB |
| Cached `tsh`/`tctl`/`tbot` binaries, one per Teleport version I'd ever connected to | 1.7GB |
| 14 old Terraform version binaries, only one of which was in use | ~840MB |

Nearly 80GB, none of it doing anything for me. The UTM finding was the most humbling — I'd been telling myself a story ("nice to keep around for occasional Windows testing") about infrastructure that, on inspection, wasn't even the thing I thought it was.

Along the way `tfswitch` also started failing outright with `openpgp: key expired` — HashiCorp's signing key had a self-signature extension that expired, and the copy cached locally in `.terraform.versions` was frozen at the old expiry. Re-fetching the current key from HashiCorp fixed it; the fingerprint matched, only the trailing self-signature packet differed.

## The lesson

None of this was really about disk space. A stale fork sitting in a personal GitHub repo is invisible until you go looking for it, and so is a forgotten Vault container, and so is a plaintext secret sitting quietly in a history file with 600 permissions, and so is a "Windows VM" that's actually three abandoned Ubuntu installs. Cleaning up dotfiles was the excuse to go looking. What I found was closer to: the config that isn't backed up, the credential handling that isn't real credential handling, and the mental model of my own environment that hadn't matched reality in a while.

The repo's public now: [github.com/tenaciousdlg/dotfiles](https://github.com/tenaciousdlg/dotfiles).
