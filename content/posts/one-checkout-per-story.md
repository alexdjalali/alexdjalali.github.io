---
title: "One Checkout Per Story"
date: 2026-11-21T11:00:00-05:00
draft: false
description: "Git worktrees were a niche feature until coding agents made it normal to have several people typing into one repository at once; here is how I think they should be used, and where the isolation they offer quietly ends."
images:
  - "images/og/one-checkout-per-story.png"
tags: ["developer-tools", "software-engineering", "process", "claude", "ai"]
keywords: ["git worktree", "parallel development", "coding agents", "claude code", "cherry-pick", "integration branch", "docker compose project name", "gitignore", "testcontainers"]
series: ["AI-Assisted Engineering"]
---

For most of my career I had no use for `git worktree`. It has been in git since 2015, and its whole job is to let one repository have several working directories, each with its own branch checked out, all sharing one object store. That is a solution to a problem a single person rarely has, since a person can only type into one branch at a time, and `git stash` covered the rest (badly, but it covered it). What changed is that I am no longer the only one typing. Once you have two or three coding agents working on the same repository at the same time, the question of where each of them *stands* stops being academic, and worktrees turn out to be a very good answer to it, up to a point. This post is about where that point is.

## Why not just branches

The obvious objection is that branches already give you parallel lines of development, so why would you want more than one directory? The answer is that a branch isolates *history*, but it does nothing for the *working tree*, and the working tree is where an agent actually lives. An agent edits files, runs the formatter, runs the tests, builds binaries and leaves generated output lying around. Two agents in one checkout, on two branches, are two people sharing one desk by taking turns at very short intervals. Even one agent and one human in the same checkout is a problem, since the moment the human switches branches to look at something, the files have changed under the agent.

So there are (at least) three options. You can clone the repository several times, which works but duplicates the object store and leaves you with several clones to keep in sync. You can run each agent in a container or a remote sandbox with its own clone, which is the cleanest isolation and the most setup. Or you can use worktrees, which give each agent its own directory and branch while sharing one repository, so a commit made in one is immediately available (as an object, if not as a checkout) in all the others. The git documentation is precise about what is shared: most refs and the repository config are common to every worktree, while `HEAD` and a few other per-worktree refs are not. For local work I opt for worktrees, mostly because cherry-picking between them is free, and cherry-picking turns out to be the whole game.

## One story, one worktree, one commit

The rule I have settled on is easiest to state as an equation: one story equals one plan equals one worktree equals one commit. A story is a unit of work with its own acceptance criteria. An agent writes a plan for it, a person approves the plan, and the agent implements it in its own worktree on its own branch and finishes with exactly one commit, which is then cherry-picked onto an integration branch. The worktree is removed when the story lands.

The "one commit" part matters more than it looks. A story that lands as one commit can be cherry-picked, reverted or reordered as a unit, and the integration branch ends up reading like a table of contents rather than a transcript of somebody's afternoon. It also forces the agent to finish properly (formatted, linted, tested) before it may call the story done, because there is no "fix lint" commit to tack on afterwards.

Two corollaries follow. The first is that every branch in a parallel run should be cut from the same base commit. If one branch starts later than the others, its stories quietly depend on changes the integration branch has not seen, and the cherry-picks stop meaning what you think they mean. The second is that parallelism is a property of stories, not of tools. A worktree lets you run things in parallel. Whether you *should* depends on which files the stories touch, and two stories that both edit the same package will conflict on every cherry-pick no matter how many directories you give them. In practice that means grouping stories into lanes, running the disjoint ones side by side and the overlapping ones one after another.

I'll grant that this is the software equivalent of multitrack recording. Every musician gets their own track (and their own headphone mix) and plays without hearing anyone else's mistakes, and all the real work happens at mixdown. The analogy is a stretch in one respect: a mixing engineer can't revert the bassist.

## Where the isolation ends

This is the part I would have liked to read before starting. A worktree isolates exactly what git tracks and nothing else, and the interesting failures are all in the "nothing else."

Ignored files don't come along. A new worktree is a fresh checkout of tracked files, so anything your build generates locally and ignores (code generated from a schema, a rendered config file, a local secrets directory) simply isn't there. A fresh worktree has to run the project's generators before it runs anything else, and any tool that silently assumes those files exist will fail in a confusing way.

Ignore patterns may not mean what you think. The `gitignore` documentation is explicit that a pattern with a separator at the end matches only directories. If a worktree links in a directory with a symlink (a shared secrets folder, say), a pattern like `.secrets/` will not match the symlink, and the link shows up as an untracked file, which is just the thing to trip a clean-tree check.

The `.git` in a linked worktree is a file, not a directory. It contains a pointer back to the repository's real git directory. Most tools handle this, but anything that mounts the working directory into a container and then expects to find git metadata there will be told, with total confidence, that it is not in a repository, unless the common git directory is mounted as well.

Everything outside git is shared. This is the big one. Docker Compose names a project after the directory that contains the Compose file, unless a project name is set explicitly by flag, environment variable or the top-level `name:` attribute. Worktrees in different directories therefore get different project names by default, which is helpful. But many projects pin `name:` in their Compose file, and then every worktree's `docker compose up` targets the same project and the same containers, so starting the stack from an agent's worktree replaces the stack you were running from your own checkout with one built from half-finished code. The safe pattern is to give each worktree its own project name, or to keep the shared stack in one checkout and verify agents' work in tests that start their own throwaway dependencies (testcontainers is the standard way to do this).

The same is true of anything installed globally. A binary on your `PATH`, a long-running local server, a linter installed by a package manager rather than pinned by the project: none of these know which worktree you are in, and an agent can spend a long time testing a change against yesterday's build without realizing it. Builds made in a worktree should be run from that worktree.

Finally, a matter of taste that I hold fairly strongly: worktrees belong beside the repository, not inside it. Some tools offer to create worktrees for you in a hidden directory inside the repository. That keeps them out of sight, which sounds tidy until you have six and cannot remember which one holds what. Naming each worktree after the repository plus a short suffix, in the same parent folder, means `ls` tells you everything that is in flight (`git worktree list` will too, but `ls` is what you actually type).

## What I would tell someone starting

On the face of it, worktrees are a git feature, and you would expect the hard parts to be git problems. Upon closer investigation, very few of them are. With one commit per story and lanes that keep overlapping stories apart, merging is the easy part. The trouble is in the parts of the machine git doesn't know about: generated files, ignored files, container names, binaries on a `PATH`. The job, before handing worktrees to a handful of agents, is to make an honest list of what *your* project keeps outside of git.

Granted, much of this goes away if each agent gets its own container. For now, a few folders on a laptop and a rule about one commit per story are enough for me, and I find I like being able to `cd` into what an agent is doing and simply read it. Whether that habit survives ten agents rather than three, I honestly don't know yet.

## References

- Git documentation. `git-worktree`. <https://git-scm.com/docs/git-worktree>
- Git documentation. `gitignore`. <https://git-scm.com/docs/gitignore>
- Docker documentation. "Specify a project name." <https://docs.docker.com/compose/how-tos/project-name/>
- Testcontainers. <https://testcontainers.com/>
