---
title: "Six Broken Images and a Case-Sensitive Field in Cloudflare's Bot Management"
date: 2026-07-07
description: "A handful of doodles silently 403'd for every visitor, not just bots. Tracing it back to a Cloudflare WAF field that only recognizes lowercase file extensions, and fixing it at both the asset layer and the Terraform layer."
tags: [cloudflare, terraform, waf, bot-management, debugging]
draft: false
---

Someone pointed out that a handful of images on my [sketchbook page](/doodles) weren't loading. Broken image icons, captions rendering fine, nothing in the page source that looked wrong. The `<img src>` paths matched the files in the repo exactly, extension and all. That's usually where this kind of bug ends: a typo, a case mismatch between the filename and the reference. Not this time.

## Ruling out the obvious

Six files were broken: a few `.PNG`s, a couple `.JPG`s. Every other image, all lowercase extensions, rendered fine. First guess was a case-sensitivity mismatch between what's committed to git and what's on disk, the kind of thing that hides easily on a case-insensitive Mac filesystem and then breaks the moment it hits a case-sensitive host. I checked with `git ls-files` to see the exact case actually tracked in the repo:

```
public/doodles/ah_1.PNG
public/doodles/archie_1.JPG
public/doodles/hello_whale.PNG
...
```

Matched the source references exactly, uppercase and all. So it wasn't a mismatch. The files existed, at the paths the page was asking for, with the casing the page was asking for. And they still didn't load.

## Reproducing it directly

Next step was cutting the browser out of it entirely:

```
❯ curl -s -o /dev/null -w "%{http_code}\n" https://chrisdlg.com/doodles/ah_1.PNG
403
❯ curl -s -o /dev/null -w "%{http_code}\n" https://chrisdlg.com/doodles/hi.png
200
```

Same site, same directory, only difference was the case of the extension. The 403 body wasn't a normal "forbidden," either. The response headers had `cf-mitigated: challenge`, and a `content-security-policy` pointing at `challenges.cloudflare.com`. Cloudflare wasn't returning "no," it was returning a JS challenge page in place of the image. A browser can solve that challenge when it's navigating to a page. An `<img>` tag just gets challenge HTML back where image bytes were supposed to be, and renders it as a broken image.

I tried spoofing a normal browser user agent on the curl request. Still 403. I tried a path that didn't exist at all with an uppercase extension. Still 403, still challenged, not a clean 404. Whatever was flagging these requests wasn't just "detects curl," and it wasn't about the specific file. It was about the extension casing.

## The rule that was actually catching this

chrisdlg.com's Cloudflare zone is Terraform-managed, not click-ops, so the WAF logic wasn't buried in a dashboard somewhere. It was sitting in a `.tf` file I could just read. Two custom rules, both keyed off Cloudflare's bot score:

```hcl
{
  description = "Bot Score: 1"
  action      = "managed_challenge"
  expression  = "(cf.bot_management.score lt 2 and not cf.bot_management.static_resource and not cf.bot_management.verified_bot)"
},
{
  description = "Bot Score: 2 - 30"
  action      = "js_challenge"
  expression  = "(cf.bot_management.score ge 2 and cf.bot_management.score le 30 and not cf.bot_management.verified_bot and not cf.bot_management.static_resource)"
},
```

Both rules skip the challenge if `cf.bot_management.static_resource` is true, Cloudflare's own signal for "this request is for a static file, don't bother." That's exactly the kind of exemption you'd want for images, and it clearly works, since every lowercase-extension file on the page loads fine. The gap is that the field only recognizes a fixed, apparently case-sensitive list of extensions. `.png` gets classified as a static resource and skips the challenge. `.PNG` doesn't get classified that way, falls through to the bot-score check, and gets challenged like any other uncertain request, real visitor or not.

## Fixing it in two places

The fast fix was the asset itself: rename the six files and their references to lowercase extensions, rebuild, redeploy. That resolved the visible bug immediately.

But the underlying gap doesn't go away just because these six files got renamed. Phone photos and most screenshot tools default to uppercase extensions, `IMG_1234.JPG` is the norm, not the exception, which is exactly how these files ended up uppercase in the first place. The next photo I drop into that folder without thinking about it breaks the same way.

So the second fix went into the Terraform rule itself: a case-insensitive path match, OR'd alongside the existing `static_resource` check, so the exemption no longer depends on Cloudflare's extension list matching case exactly.

```hcl
locals {
  static_asset_regex = "(?i)\\.(png|jpe?g|gif|svg|webp|ico|css|js|woff2?|ttf|eot|pdf|mp4|mov)$"
}
```

Both rules got the same change:

```hcl
expression = "(cf.bot_management.score lt 2 and not (cf.bot_management.static_resource or http.request.uri.path matches \"${local.static_asset_regex}\") and not cf.bot_management.verified_bot)"
```

`terraform plan` showed exactly what I expected: one resource updated, two rule expressions changed, nothing else. Credentials for this come from the same Vault-backed `direnv` setup [I wrote about recently](/blog/dotfiles-vault-cleanup): `.envrc` pulls the Cloudflare API key and account ID via `vault kv get`, so there was nothing to paste and nothing new to leak. `terraform apply`, and `terraform state show` confirmed the live rule matched what was committed.

## Why this was worth chasing down

A broken image on a sketchbook page is low stakes. The same bot-management gap on a page with real content wouldn't be: any asset that happens to get uploaded with an uppercase extension silently 403s for every visitor, indistinguishable from a normal broken link unless you go looking at response headers. Renaming the files fixed what was visible. Fixing the rule means the next uppercase-extension file doesn't get to cause the same bug quietly, months from now, from a machine that isn't even mine anymore.
