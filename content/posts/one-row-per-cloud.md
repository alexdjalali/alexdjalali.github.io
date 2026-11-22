---
title: "One Row Per Cloud"
date: 2026-11-21T10:00:00-05:00
draft: false
description: "Bring-your-own-cloud deployment looks like an infrastructure problem, but the hard part is deciding who is allowed to write each fact about an environment, and normalizing the answer."
images:
  - "images/og/one-row-per-cloud.png"
tags: ["architecture", "distributed-systems", "system-design", "reliability"]
keywords: ["bring your own cloud", "byoc", "multi-account aws", "environment descriptor", "single source of truth", "gitops", "argo cd applicationset", "external-dns", "twelve-factor config", "normalization"]
series: ["Software Architecture"]
---

Here is a way to take a website down that external-dns's own documentation will explain to you, if you read it in the right order. external-dns keeps an *ownership registry*: it labels the DNS records it creates with TXT records carrying an owner id, and it "will never modify any records over which it doesn't have control." That is exactly the right behavior, and it is the reason the tool is safe to run in a zone other people also write to. Now rebuild an environment and, in the course of tidying up its names, change that owner id. The old records survive (the hosted zone was never deleted), they still point at a load balancer that no longer exists, and the new external-dns, correctly, refuses to touch them. The site returns errors, every tool involved behaved as documented, and the culprit is a string that nobody on the team would have described as configuration.

I bring this up because it is a near-perfect specimen of the problem I want to talk about, which shows up most acutely when a product moves to a bring-your-own-cloud (BYOC) model. The argument of this post is that BYOC is sold as an infrastructure problem and is really a problem of authorship, and that the remedy is one that database people worked out more than fifty years ago.

## What BYOC asks for

The request is simple to state. A product that has run in its vendor's cloud account is now to run, unchanged, in a customer's own account, under the customer's identity provider, secrets store and audit trail, while the vendor keeps its own environments running beside it. Ideally all of them are deployed from one repository, so that a fix made once reaches everyone.

There are (at least) four ways to arrange this, and they are worth writing down before picking one:

| Option | What it buys | What it costs |
|---|---|---|
| The customer runs its own pipeline from a fork | The cleanest ownership boundary | Two pipelines and two copies of the infrastructure code, drifting apart from the first day |
| The vendor's pipeline assumes a role *into* the customer's account | One pipeline and almost no customer setup | The vendor's repository holds standing deploy access to a customer's cloud |
| Infrastructure-as-code workspaces rather than per-account configuration | Less duplication on disk | Workspaces sit awkwardly across truly separate accounts and state backends |
| An environment × account matrix: one pipeline, short-lived federated credentials per account, state kept in each account | One code path and one release to N clouds | Each new account has to be bootstrapped |

I would opt for the matrix nine times out of ten. It follows the grain of the cloud providers' own multi-account guidance (AWS's whitepaper on organizing environments across accounts is the canonical version), and with OIDC federation from the CI system there is no long-lived credential sitting anywhere for anyone to steal. Adding a customer becomes, in principle, a new entry in a list plus a bootstrap.

Granted, that is the easy part. The matrix tells you *which account* an environment lives in. It says nothing about the dozens of other facts an environment has.

## Four authors for one fact

Think about everything that distinguishes one environment from another: its domain, its identity provider's tenant, its queue and bucket names, its certificate and role identifiers, the network it runs in, the git revision its deployment controller tracks, and (as above) the owner id its DNS controller stamps on records. In a typical setup, any one of those can be written down in several places at once. It might be an input or output of the infrastructure code, a value in a committed per-environment config file, a variable stored in the CI system's settings, and a literal in a Kubernetes manifest, and the four copies are kept in agreement by nothing more reliable than people remembering to.

With one environment, this mostly works, because every copy was written at the same time by the same person and nobody has had a reason to change any of them. The trouble starts on the day you add a second environment, or rename the first. Every fact that was really *derived* from something (an identifier the infrastructure code minted, a prefix computed from the environment's name) but was *copied* instead becomes a small, silent time bomb, since the copy has no way of knowing that its source has changed. The infrastructure itself comes up perfectly. Everything downstream of it is pointed at the old world.

The twelve-factor methodology made a version of this point years ago, observing that grouping config into named environments "does not scale cleanly" as the number of deploys grows. I'd go a step further. It is not only that per-environment config files multiply. It is that each fact has more than one author.

## Normalizing an environment

If you squint, a fleet of environments is a database, and the problem above is a denormalized schema with update anomalies. Codd (1970) would recognize it immediately. The fix is the same one: every fact gets exactly one place where it is written, and everything else is derived.

Concretely, I would argue for the following discipline. An environment is a single row in a descriptor file, and that row is the only per-environment thing a person writes by hand. Something like this (a made-up example):

```yaml
environments:
  - name: acme-staging
    customer: acme
    account_id: "111122223333"
    region: us-east-1
    resource_prefix: acme
    domain: staging.acme.example
    config_profile: staging
    release: v1.42.0
```

Three of those fields encode lessons that seem to be learned the hard way. `resource_prefix` is separate from `name` because building resource names out of the environment's name makes the name part of every resource's identity, which turns a rename into a teardown. `config_profile` is separate from `name` because naming config files after environments forces a full copy of the config for every new environment, when most environments of the same kind should share one. And `release` is the git revision the environment's GitOps controller tracks, so that promoting an environment is a one-line change rather than an edit scattered across a dozen manifests.

The row alone is not enough. The other half of the discipline is a rule about which *kind* of fact may be authored where:

| Fact class | Author | How it reaches the thing that reads it |
|---|---|---|
| Environment identity | the row | generated into the infrastructure code's inputs, the Kubernetes values and the deployment controller's config |
| Infrastructure-derived identifiers | the infrastructure code's outputs | published at apply time and read at runtime, never committed |
| Behavior (which backend, which timeouts) | a shared config profile | the application's config loader |
| Secrets | a secrets manager | an in-cluster secrets operator |

The second row of that table does most of the work. A value the infrastructure code minted (a network id, a certificate identifier) is never pasted anywhere. The code that created it publishes it, and whatever needs it reads it from there. A value that can't be pasted can't go stale.

Deployment manifests follow the same logic. If every per-environment overlay is rendered from a shared template and the row, then a CI check can regenerate them all and fail on any difference, and a second check can scan for environment-specific literals that have crept in by hand. Argo CD's ApplicationSet generators are a good fit here, since an application per environment, pinned to that environment's `release`, is exactly what they are designed to stamp out.

## People are environments too

The part of this I think is most often missed is the operator. A person (or, increasingly, an agent acting for one) who needs to work in an environment needs credentials for that environment's cloud account and for its identity tenant, and a surprising amount of operational damage comes from having the wrong pair loaded in a shell. The same normalization applies. If the row names the role an operator should assume, then a login command can derive everything from the row, and, crucially, can check after logging in that the account it actually reached is the account the row names. It is a tiny check, and it turns the most dangerous mistake in multi-account operations (doing the right thing in the wrong place) into an error message.

## Build once

Last, a smaller point. It is tempting, with one pipeline and N accounts, to build the product's images N times, once per account. I'd resist that. Build each image once, sign it, and have every account pull the same digest (Sigstore's tooling makes the signing and verification part straightforward). What a customer runs is then byte-for-byte what was tested, rather than a rebuild from the same commit, which is not the same thing, as anyone who has chased a non-reproducible build will tell you.

## The point I want to make

On the face of it, BYOC is about clouds: accounts, roles, state backends, the differences between providers' managed services. Those matter, and they are where anyone would start. Upon closer investigation, though, the question that decides whether you can run ten environments rather than two is whether each fact about an environment has exactly one author and one path to the thing that reads it. The DNS owner id I opened with is the perfect example, because it fails that test without anybody ever having thought of it as a fact.

Of course there is nothing new under the sun here. Normalization is older than most of the people reading this, and the twelve-factor authors said much of the rest about config a decade ago. All I'm really trying to say is that a deployment has a schema whether or not you write it down, and that writing it down, one row per environment, is what turns the second cloud (and, one hopes, the third) into something boring.

## References

- Codd, E. F. (1970). A relational model of data for large shared data banks. *Communications of the ACM* 13(6).
- Wiggins, A. *The Twelve-Factor App*, "III. Config." <https://12factor.net/config>
- Amazon Web Services. *Organizing Your AWS Environment Using Multiple Accounts* (whitepaper).
- GitHub Docs. "About security hardening with OpenID Connect."
- Argo CD documentation. "Generating Applications with ApplicationSet."
- ExternalDNS documentation. "FAQ" (ownership registry) and "The TXT registry." <https://kubernetes-sigs.github.io/external-dns/>
- Sigstore documentation. Cosign signing and verification.
