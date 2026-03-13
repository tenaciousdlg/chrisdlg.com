---
title: "Wiring Okta to Teleport via SCIM and Terraform"
date: 2025-03-01
description: "How I built a fully automated identity pipeline from Okta group membership to Teleport access controls — zero manual user management required."
tags: [teleport, terraform, okta, scim, iac]
---

One of the most common pain points in Teleport deployments is keeping access up to date as people join teams, change roles, or leave the company. The default approach — managing `teleport_role` assignments in Terraform — works fine at small scale but becomes a liability the moment HR is the source of truth for group membership.

Here's how I solved it for a demo environment, and why the same pattern works for production.

## The goal

- Okta is the identity provider (SAML + SCIM)
- Group membership in Okta drives Teleport access — add someone to `senior-devs`, they get `platform-dev-access` automatically
- No Terraform changes needed when users join or switch teams
- Everything reproducible from `terraform apply`

## The pieces

**Teleport side:**
- An `okta-integrator` SAML connector for authentication
- SCIM provisioning endpoint created with `tctl plugins install scim --connector=okta-integrator`
- Access Lists with `type: scim` wired to Okta groups (`devs`, `senior-devs`, `engineers`)
- Each access list grants the appropriate Teleport roles

**Okta side (Terraform):**
- `okta_app_saml` for the SAML app
- `okta_group` + `okta_group_memberships` for each tier
- Users defined in `terraform.tfvars` with a `groups` list — Terraform derives membership automatically

**Important gotcha:** The SCIM credentials Teleport generates are OAuth 2.0 (client ID + client secret), _not_ a bearer token. The `okta_app_provisioning_connection` Terraform resource only supports bearer tokens, so that piece must be configured manually in the Okta UI. Everything else is automated.

## The access tier structure

Three tiers, each with increasing blast radius:

| Tier | Okta Group | Access Lists grants |
|------|-----------|---------------------|
| devs | `devs` | `dev-access`, `dev-auto-access`, `dev-requester` |
| senior devs | `senior-devs` | `platform-dev-access`, `dev-auto-access`, `senior-dev-requester` |
| engineers | `engineers` | `platform-dev-access`, `prod-readonly-access`, `prod-requester`, `prod-reviewer`, `editor`, `auditor` |

`dev-requester` can only request `prod-readonly-access`. `senior-dev-requester` can request `prod-readonly-access` or `prod-access`. Engineers have standing prod access plus reviewer rights for the access request workflow.

## What "push groups" actually means

Okta's SCIM provisioning has a "Push Groups" tab that most guides skim over. This is what sends group membership events to Teleport — without it, users provision but roles never attach. You configure it manually in the Okta UI since the Terraform provider has no resource for it.

One limitation: Okta's built-in "Everyone" group cannot be pushed via SCIM. If you want a baseline role for all users, define an explicit group (`everyone` in my case) and populate it.

## Why this beats static Terraform role assignments

The alternative — hardcoding `teleport_role` grants per user in Terraform — means every onboarding or team change is a PR. With SCIM, Okta is the system of record and Teleport stays in sync automatically. The Terraform code only changes when the access model itself changes, not when people move around.

The full Terraform layout lives in [github.com/tenaciousdlg/okta](https://github.com/tenaciousdlg).
