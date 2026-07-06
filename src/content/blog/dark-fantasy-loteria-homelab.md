---
title: "Naming the Homelab: A Dark Fantasy Lotería Deck"
date: 2026-07-06
description: "Building out a NAS, Proxmox, and a proper home network gave me an excuse to stop calling my gaming PC 'Terra' and start building something more personal — a Lotería deck pulled toward the Cthulhu/sacred-geometry end of my own tattoos instead of straight folklórico."
tags: [homelab, naming, loteria, proxmox, nas]
draft: true
---

Every homelab eventually needs names, and I'd been putting it off — my gaming/AI PC was just "Terra," named after the case it came in, and I never liked it. Once a NAS, a Proxmox host, and some actual networking gear entered the picture, "just name things after the parts" stopped being enough.

I write about Teleport, Terraform, and Vault a lot on this site, but the honest input for this one was three things inked on my own arm: Mexican folklórico, Lovecraftian cosmic horror, and sacred geometry. Lotería — the traditional Mexican bingo-style card game — is the natural bridge between all three: bright, recognizable folk-art iconography that's easy to twist darker without losing what makes it *mine* rather than borrowed from someone else's franchise.

## The rules

Every card starts as a real Lotería card. The twist stays close enough to the original iconography that it's recognizable, pulled toward whichever end of the aesthetic fits the role. Some names are literal hostnames (an actual machine you'd find in a router's client list). Others are just documentation shorthand — a label for a piece of Terraform, a policy, a concept that doesn't have its own box to plug in.

## The deck so far

| Card | Twist | What it is |
|---|---|---|
| **El Diablito** | Unchanged — already iconic | My gaming/AI PC (Ryzen 7 7800X3D, RTX 4080) — hostname |
| **La Sirena Abisal** (The Abyssal Siren) | Classic mermaid pulled into deep-water horror | Jellyfin/Plex — hostname, once it has a box |
| **La Calavera Eterna** (The Eternal Skull) | Death, but specifically what *remains* after | NAS/backups — hostname |
| **El Árbol de Huesos** (The Bone Tree) | The tree card, skeletal — one root, many branches | Proxmox host — hostname |
| **El Mundo Fracturado** (The Fractured World) | The globe, shattered, held together by something | Ubiquiti gateway/router — hostname *and* shorthand for "the network as a whole" |
| **El Alacrán de Sangre** (The Blood Scorpion) | Already a danger card, sharpened | The WAF ruleset (`chrisdlg-com.tf`) — documentation label, not a hostname |
| **La Corona Caída** (The Fallen Crown) | A crown that cost something to wear | Vault — thematic label layered on an already-named service |
| **La Araña Tejenoches** (The Night-Weaving Spider) | A web spun through every room, sensing the smallest change | Home Assistant — hostname |
| **El Cotorro Viajero** (The Traveling Parrot) | Repeats what it hears, carries it elsewhere | The Raspberry Pi tunneling in from Colorado — hostname |
| **La Escalera al Abismo** (The Ladder into the Abyss) | Each rung down goes deeper toward what's protected | Zero Trust Access/policy layer (`chrisdlg-com-zerotrust.tf`) — documentation label |
| **El Cantarito del Forastero** (The Stranger's Pitcher) | Hospitality offered carefully to someone from outside | The guest-access policy for Jellyfin/Plex — not built yet |
| **La Mano que Todo Sabe** (The Hand That Knows All) | Always with you, an extension of yourself | iPhone — hostname |
| **La Luna que Vela** (The Watching Moon) | Reflected light, always present, changing phase | iPad — hostname |

## Why this over just picking a fandom

Norse mythology and the Cosmere both had genuinely good fits (Heimdall for a gateway is almost too on the nose). But none of them are actually *mine* the way this is — this deck only exists because of a specific, personal aesthetic, not because I like a book series. Still updating this as the actual hardware shows up.
