---
title: "Professional Software Engineering for AI and Distributed Systems"
date: 2026-03-01
draft: false
lastmod: 2026-10-31
description: "A graduate course designed to bridge the gap between writing code and engineering production-grade distributed systems — with intentional technical debt, architecture defense, and AI as a force multiplier."
images:
  - "images/og/professional-software-engineering-for-ai-and-distributed-systems.png"
tags: ["software-engineering", "education", "distributed-systems", "ai", "architecture"]
keywords: ["software engineering course", "distributed systems", "AI engineering", "production systems", "graduate course", "architecture decision records", "trunk-based development", "clean architecture"]
series: ["Software Architecture"]
---

Computer science programs teach programming. They teach data structures, algorithms, complexity analysis, and language syntax. Students graduate knowing how to invert a binary tree, implement a hash map, and reason about Big-O notation. These are valuable skills. They are also insufficient.

The gap between writing code and engineering production systems is enormous. It is the difference between solving a problem in isolation and operating inside a system that other people depend on, that runs at scale, that must be deployed without downtime, monitored in production, debugged at 2 AM, and evolved over years by teams of people who were not there when the original decisions were made. Most CS programs do not teach this. Most graduates discover it on the job, through expensive mistakes and patient mentors — if they are lucky enough to have mentors at all.

This is the gap that *Professional Software Engineering for AI and Distributed Systems* is designed to close. It is a graduate-level course I designed that treats software engineering as a discipline distinct from computer science — one that requires its own vocabulary, its own practices, and its own modes of thinking.

## The Philosophy

The course is built on a single principle:

> You play like you practice.

If you practice with toy projects, unrealistic environments, and no consequences for bad decisions, you will play that way in production. If you practice with production-parity development environments, real CI/CD pipelines, and architecture decisions that must be defended in front of peers, you will carry those habits into your career.

This means <a href="https://www.docker.com/" target="_blank" rel="noopener noreferrer">Docker</a> and <a href="https://containers.dev/" target="_blank" rel="noopener noreferrer">devcontainers</a> from day one — not as a topic in week twelve, but as the environment in which all coursework happens. It means <a href="https://12factor.net/dev-prod-parity" target="_blank" rel="noopener noreferrer">dev/prod parity</a> as a foundational constraint, not an aspiration. It means secrets management and configuration discipline before students write their first feature, because in production, misconfigured environments cause more outages than buggy code.

The course is organized around six pillars: engineering foundations, codebase and architecture mastery, distributed systems and production realism, operational excellence, AI-augmented engineering, and leadership and organizational impact. Each pillar spans multiple weeks, and each week builds on what came before.

## Orion: A Deliberately Broken System

Students do not start from scratch. They inherit a system called Orion — a Python-based distributed AI platform with a <a href="https://fastapi.tiangolo.com/" target="_blank" rel="noopener noreferrer">FastAPI</a> service layer, an async worker service, <a href="https://www.postgresql.org/" target="_blank" rel="noopener noreferrer">PostgreSQL</a>, <a href="https://redis.io/" target="_blank" rel="noopener noreferrer">Redis</a>, a message queue, an AI integration layer, and a Docker-based development environment. It functions. It also has problems.

The CI pipeline is broken. The codebase contains intentional technical debt — tightly coupled components, missing type annotations, inconsistent error handling, implicit dependencies between services, and no observability. There are no <a href="https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions" target="_blank" rel="noopener noreferrer">Architecture Decision Records</a>. There is no documentation explaining why things are the way they are.

This is deliberate. Starting with a clean codebase teaches students how to build. Starting with a messy one teaches them how to *engineer* — how to navigate unfamiliar systems, diagnose structural problems, introduce discipline incrementally, and make things better without breaking what already works. Every professional engineer inherits more code than they write. Orion reflects that reality.

Over the semester, students collaboratively evolve Orion into a production-ready platform. They refactor the architecture, introduce ADRs, add static typing, implement <a href="https://trunkbaseddevelopment.com/" target="_blank" rel="noopener noreferrer">trunk-based development</a>, build CI/CD pipelines, add observability, design safe database migrations, optimize performance and cost, secure the system against real threats, and ultimately defend their architectural decisions in a formal review.

## Engineering Foundations

The first three weeks establish the mindset and the mechanics.

**Week 1** draws the line between a programmer and an engineer. A programmer writes code that works. An engineer owns a system — understands its failure modes, considers its operational characteristics, makes decisions under constraint, and accepts responsibility for the consequences. This distinction is not philosophical. It determines whether you ship a feature and walk away, or ship a feature and monitor its impact on latency, error rates, and downstream services. The week covers ownership, systems thinking, and the ethics of AI in engineering — because students will increasingly work alongside AI systems, and they need a framework for when to trust the output and when to question it.

**Week 2** builds the development environment. Students configure Docker-based environments with development containers, enforce environment parity between development and production, and learn secrets management. The goal is that by the end of week two, every student can run the entire Orion stack locally with a single command, and the environment they run locally is structurally identical to the one that runs in CI. I have [written previously]({{< relref "/posts/my-development-environment" >}}) about the importance of investing in your development environment — this week puts that philosophy into practice.

**Week 3** introduces trunk-based development. Students learn to work with short-lived branches, use CI as an enforcement mechanism, implement <a href="https://martinfowler.com/articles/feature-toggles.html" target="_blank" rel="noopener noreferrer">feature flags</a> for incomplete work, and practice rigorous code review. The emphasis is on small, frequent merges rather than long-lived feature branches — because in production, integration risk grows with branch age, and merge conflicts are a symptom of process failure, not code complexity.

## Codebase and Architecture Mastery

Weeks four and five teach students how to read and restructure large codebases.

**Week 4** focuses on navigation. Static typing becomes the primary tool — not as an academic exercise, but as a means of understanding code you did not write. When a function signature tells you it accepts a `TranscriptQueryParams` and returns a `list[Transcript]`, you know what it does without reading the implementation. Students learn to identify modular boundaries, detect <a href="https://refactoring.guru/refactoring/smells" target="_blank" rel="noopener noreferrer">code smells</a>, and use type annotations as both documentation and a safety net for refactoring.

**Week 5** introduces <a href="https://en.wikipedia.org/wiki/Dependency_inversion_principle" target="_blank" rel="noopener noreferrer">dependency inversion</a> and <a href="https://en.wikipedia.org/wiki/Composition_over_inheritance" target="_blank" rel="noopener noreferrer">composition over inheritance</a> — the principles that separate maintainable architectures from brittle ones. Students refactor legacy code in Orion to follow clean layered architecture: interfaces defined before implementations, dependency direction enforced through physical directory boundaries, cross-cutting concerns handled through decorator composition. I have written about this architecture in detail in my post on [the ideal repository structure]({{< relref "/posts/the-ideal-repository-structure" >}}) and in the companion post on [the decorator pattern for observability and resilience]({{< relref "/posts/decorator-pattern-observability-resilience" >}}).

## Testing and Delivery

Weeks six and seven address how code gets validated and shipped.

**Week 6** covers testing in distributed systems — a fundamentally different challenge from testing a monolithic application. Unit tests verify individual components. Integration tests verify interactions between services. <a href="https://pact.io/" target="_blank" rel="noopener noreferrer">Contract tests</a> verify that service boundaries honor their agreements. Students learn to design for idempotency — ensuring that retried operations produce the same result — and to simulate failure conditions: network partitions, slow databases, unavailable downstream services. The question is not "does this work when everything is healthy?" but "does this degrade gracefully when something fails?"

**Week 7** introduces <a href="https://martinfowler.com/articles/continuousIntegration.html" target="_blank" rel="noopener noreferrer">CI/CD</a> and release engineering. Students build multi-stage pipelines that enforce quality gates — formatting, linting, type checking, tests — on every commit. They learn to produce reproducible builds, design rollback strategies, and treat the deployment pipeline as code that is versioned, tested, and reviewed with the same rigor as application code.

## Distributed Systems and Data Safety

Weeks eight and nine introduce the theory and practice of building systems that span multiple processes, machines, and failure domains.

**Week 8** covers distributed systems fundamentals: consistency models, the trade-offs between availability and partition tolerance, retry strategies with exponential backoff and jitter, and <a href="https://martinfowler.com/articles/201701-event-driven.html" target="_blank" rel="noopener noreferrer">event-driven architecture</a>. The emphasis is practical — students implement these patterns in Orion, not in a textbook. They experience what happens when a message is delivered twice, when a consumer crashes mid-processing, when a network timeout causes a cascade of retries that overwhelms a downstream service.

**Week 9** addresses schema evolution and data safety. Databases change. APIs change. The challenge is making those changes without downtime and without breaking existing clients. Students learn zero-downtime migration patterns — expand and contract, parallel writes, backfill strategies — and implement versioned APIs that allow old clients to coexist with new ones. In production, the most dangerous deploys are not code changes. They are data changes.

## Operational Excellence

Weeks ten and eleven shift focus from building systems to running them.

**Week 10** introduces observability and <a href="https://sre.google/sre-book/table-of-contents/" target="_blank" rel="noopener noreferrer">SRE</a> thinking. Students instrument Orion with structured logging, metrics, and distributed tracing. They define <a href="https://sre.google/sre-book/service-level-objectives/" target="_blank" rel="noopener noreferrer">service level objectives</a> — not as abstract percentages, but as concrete commitments about latency, error rates, and availability that drive engineering decisions. They practice incident retrospectives: blameless postmortems that focus on systemic causes rather than individual mistakes. The goal is to shift from reactive firefighting to proactive reliability engineering.

**Week 11** covers performance and cost engineering. Students learn to profile applications systematically — CPU profiling, memory profiling, query analysis — rather than guessing at bottlenecks. They run load tests against Orion and discover where the system breaks under pressure. And because Orion integrates AI services, they learn about token economics: the cost of LLM inference at scale, strategies for reducing token consumption without degrading quality, and the trade-offs between model capability and operational cost. In production, performance is not just about speed. It is about sustainability.

## Security and AI

Weeks twelve and thirteen address the two domains where the stakes are highest.

**Week 12** covers security through the lens of production systems. Students perform <a href="https://owasp.org/www-community/Threat_Modeling" target="_blank" rel="noopener noreferrer">threat modeling</a> against Orion — identifying attack surfaces, classifying threats, and prioritizing mitigations. They learn <a href="https://slsa.dev/" target="_blank" rel="noopener noreferrer">supply chain security</a>: dependency auditing, SBOM generation, pinned dependencies, and the risks of transitive trust. And because Orion includes an AI integration layer, they study <a href="https://owasp.org/www-project-top-10-for-large-language-model-applications/" target="_blank" rel="noopener noreferrer">prompt injection</a> — how adversarial inputs can manipulate LLM behavior, and what defenses look like in practice.

**Week 13** focuses on AI-augmented engineering. Not AI as a toy, and not AI as a replacement for engineering judgment — AI as a professional tool that requires the same discipline as any other tool in the stack. Students use LLMs for large-scale refactors, AI-assisted test generation, and code review augmentation. They learn to evaluate hallucinations systematically: how to detect when a model's output is confidently wrong, how to design workflows that catch errors before they ship, and how to build the kind of engineering system I described in [a previous post]({{< relref "/posts/anatomy-of-an-ai-engineering-system" >}}) — where AI operates within explicit constraints rather than unconstrained improvisation. The line between [leverage and liability]({{< relref "/posts/how-i-learned-to-love-the-bomb" >}}) is drawn by the discipline of the person holding the tool.

## Organization and Defense

The final two weeks connect engineering to organizational reality.

**Week 14** covers the human side of software engineering: writing stories that developers can actually implement, estimating work without false precision, managing technical debt as a portfolio rather than a backlog item, and navigating the tension between shipping fast and shipping well. These are the skills that determine whether an engineer leads or follows — and they are almost never taught in CS programs.

**Week 15** is the architecture defense. Each team presents the evolution of their Orion system — the decisions they made, the alternatives they considered, the trade-offs they accepted, and the evidence that supports their choices. ADRs, architecture diagrams, observability dashboards, test coverage reports, CI/CD pipeline runs, and live demonstrations. This is not a final exam. It is a simulation of the architectural review process that exists at every serious engineering organization — the moment where you must explain not just *what* you built, but *why*.

## What Students Leave With

By the end of this course, students will be able to operate inside distributed AI systems, architect responsibly, refactor safely at scale, ship production-ready software, lead technical discussions, and use AI as a force multiplier — not a crutch.

More importantly, they will have practiced these skills under conditions that mirror the real world. Not in isolation. Not with toy data. Not with unlimited time and no constraints. They will have inherited a broken system, fixed it collaboratively, defended their decisions publicly, and shipped something that works. That experience is transferable to the first day of a professional engineering role in a way that a passing grade on a data structures final is not.

## Course Reading

The following books, articles, and resources form the reading list for the course, organized by module.

### Engineering Foundations (Weeks 1–3)

- <a href="https://abseil.io/resources/swe-book" target="_blank" rel="noopener noreferrer">Software Engineering at Google</a> by Titus Winters, Tom Manshreck, and Hyrum Wright — Chapters 1–3 on what distinguishes software engineering from programming, and how Google thinks about code over time. Free to read online.
- <a href="https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/" target="_blank" rel="noopener noreferrer">The Pragmatic Programmer</a> by David Thomas and Andrew Hunt — Chapters 1–2 on pragmatic philosophy: ownership, responsibility, and the "broken windows" theory of software decay.
- <a href="https://web.stanford.edu/~ouster/cgi-bin/book.php" target="_blank" rel="noopener noreferrer">A Philosophy of Software Design</a> by John Ousterhout — Chapters 1–4 on complexity as the central problem, and the distinction between tactical and strategic programming.
- <a href="https://12factor.net/" target="_blank" rel="noopener noreferrer">The Twelve-Factor App</a> by Adam Wiggins — all twelve factors, with emphasis on <a href="https://12factor.net/dev-prod-parity" target="_blank" rel="noopener noreferrer">Factor X: Dev/Prod Parity</a> and <a href="https://12factor.net/config" target="_blank" rel="noopener noreferrer">Factor III: Config</a>.
- <a href="https://trunkbaseddevelopment.com/" target="_blank" rel="noopener noreferrer">Trunk Based Development</a> by Paul Hammant — the complete site, covering short-lived branches, branch by abstraction, and feature flags.
- <a href="https://martinfowler.com/articles/feature-toggles.html" target="_blank" rel="noopener noreferrer">Feature Toggles</a> by Pete Hodgson (Martin Fowler's site) — taxonomy of toggle types, lifecycle management, and the operational burden of flags.
- <a href="https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions" target="_blank" rel="noopener noreferrer">Documenting Architecture Decisions</a> by Michael Nygard — the original blog post that introduced lightweight ADRs.

### Codebase and Architecture Mastery (Weeks 4–5)

- <a href="https://refactoring.com/" target="_blank" rel="noopener noreferrer">Refactoring: Improving the Design of Existing Code</a> by Martin Fowler — the catalog of refactorings and the chapter on code smells. The companion site <a href="https://refactoring.guru/refactoring/smells" target="_blank" rel="noopener noreferrer">Refactoring Guru</a> provides visual explanations of each smell.
- **Clean Architecture** by Robert C. Martin — Part V on architecture, with emphasis on the dependency rule, the stable abstractions principle, and the separation of policy from detail.
- <a href="https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/" target="_blank" rel="noopener noreferrer">The Pragmatic Programmer</a> — Chapter 5 on decoupling: the Law of Demeter, metaprogramming, and reducing coupling between components.
- [The Ideal Repository Structure](/posts/the-ideal-repository-structure/) — how strict layer boundaries prevent architectural decay, with Go and Python examples of interface-first, layered monorepo design.
- [The Decorator Pattern for Observability and Resilience](/posts/decorator-pattern-observability-resilience/) — composing cross-cutting concerns through decorator stacks rather than scattering them through business logic.

### Testing and Delivery (Weeks 6–7)

- <a href="https://www.oreilly.com/library/view/working-effectively-with/0131177052/" target="_blank" rel="noopener noreferrer">Working Effectively with Legacy Code</a> by Michael Feathers — the definitive guide to introducing tests into codebases that were not designed for testability. Chapters on seam identification and breaking dependencies.
- <a href="https://martinfowler.com/articles/practical-test-pyramid.html" target="_blank" rel="noopener noreferrer">The Practical Test Pyramid</a> by Ham Vocke (Martin Fowler's site) — a modern restatement of the test pyramid with concrete examples of unit, integration, and end-to-end tests.
- <a href="https://docs.pact.io/" target="_blank" rel="noopener noreferrer">Pact Documentation</a> — consumer-driven contract testing for microservices. How to verify that service boundaries honor their agreements without running full integration environments.
- <a href="https://continuousdelivery.com/" target="_blank" rel="noopener noreferrer">Continuous Delivery</a> by Jez Humble and David Farley — the foundational text on deployment pipelines, reproducible builds, and the practice of keeping software in a releasable state at all times.
- <a href="https://martinfowler.com/articles/continuousIntegration.html" target="_blank" rel="noopener noreferrer">Continuous Integration</a> by Martin Fowler — the principles behind CI as a practice, not just a tool.

### Distributed Systems and Data Safety (Weeks 8–9)

- <a href="https://dataintensive.net/" target="_blank" rel="noopener noreferrer">Designing Data-Intensive Applications</a> by Martin Kleppmann — Part II on distributed data: replication, partitioning, consistency, and consensus. The single most important textbook for understanding distributed systems in practice.
- <a href="https://martinfowler.com/articles/201701-event-driven.html" target="_blank" rel="noopener noreferrer">What do you mean by "Event-Driven"?</a> by Martin Fowler — disambiguating event notification, event-carried state transfer, event sourcing, and CQRS.
- <a href="https://jepsen.io/consistency" target="_blank" rel="noopener noreferrer">Jepsen: Consistency Models</a> by Kyle Kingsbury — a visual guide to the hierarchy of consistency models, from linearizability to eventual consistency.
- <a href="https://queue.acm.org/detail.cfm?id=3025012" target="_blank" rel="noopener noreferrer">Life beyond Distributed Transactions</a> by Pat Helland — how to build correct applications without relying on distributed transactions, using idempotency and natural keys.
- <a href="https://pragprog.com/titles/mnee2/release-it-second-edition/" target="_blank" rel="noopener noreferrer">Release It!</a> by Michael Nygard — stability patterns (circuit breakers, bulkheads, timeouts) and anti-patterns (cascading failures, blocked threads, self-denial attacks). Essential reading for building systems that survive production.

### Operational Excellence (Weeks 10–11)

- <a href="https://sre.google/sre-book/table-of-contents/" target="_blank" rel="noopener noreferrer">Site Reliability Engineering</a> edited by Betsy Beyer, Chris Jones, Jennifer Petoff, and Niall Richard Murphy — Chapters on <a href="https://sre.google/sre-book/service-level-objectives/" target="_blank" rel="noopener noreferrer">service level objectives</a>, <a href="https://sre.google/sre-book/monitoring-distributed-systems/" target="_blank" rel="noopener noreferrer">monitoring distributed systems</a>, and <a href="https://sre.google/sre-book/postmortem-culture/" target="_blank" rel="noopener noreferrer">postmortem culture</a>. Free to read online.
- <a href="https://sre.google/workbook/table-of-contents/" target="_blank" rel="noopener noreferrer">The Site Reliability Workbook</a> — the practical companion to the SRE book, with worked examples of SLO implementation, alerting strategies, and incident response. Free to read online.
- <a href="https://www.oreilly.com/library/view/observability-engineering/9781492076438/" target="_blank" rel="noopener noreferrer">Observability Engineering</a> by Charity Majors, Liz Fong-Jones, and George Miranda — the distinction between monitoring and observability, structured events over metrics, and high-cardinality debugging in distributed systems.
- <a href="https://how.complexsystems.fail/" target="_blank" rel="noopener noreferrer">How Complex Systems Fail</a> by Richard I. Cook — a short, essential paper on why complex systems fail, how failure is evaluated after the fact, and why hindsight bias distorts incident analysis. Required reading before the first retrospective exercise.

### Security and AI (Weeks 12–13)

- <a href="https://owasp.org/www-project-top-ten/" target="_blank" rel="noopener noreferrer">OWASP Top 10</a> — the standard reference for web application security risks: injection, broken authentication, sensitive data exposure, and the rest. Students should be able to identify each risk category in Orion's codebase.
- <a href="https://owasp.org/www-project-top-10-for-large-language-model-applications/" target="_blank" rel="noopener noreferrer">OWASP Top 10 for Large Language Model Applications</a> — prompt injection, insecure output handling, training data poisoning, and other LLM-specific attack vectors. The AI-era companion to the classic Top 10.
- <a href="https://slsa.dev/spec/v1.0/" target="_blank" rel="noopener noreferrer">SLSA Framework</a> (Supply-chain Levels for Software Artifacts) — a security framework for achieving increasing levels of supply chain integrity, from basic provenance to hermetic builds.
- **Threat Modeling: Designing for Security** by Adam Shostack — the STRIDE methodology, attack trees, and practical approaches to identifying threats before they become vulnerabilities.
- [Anatomy of an AI Engineering System](/posts/anatomy-of-an-ai-engineering-system/) — how composable skills, quality gates, and model tiers turn AI tools into a disciplined engineering workflow rather than unconstrained generation.
- [How I Learned to Love the Bomb](/posts/how-i-learned-to-love-the-bomb/) — the shift from AI skepticism to building an engineering system around it, and why the leverage is real only if you bring the discipline with you.

### Organization and Leadership (Weeks 14–15)

- <a href="https://itrevolution.com/product/accelerate/" target="_blank" rel="noopener noreferrer">Accelerate</a> by Nicole Forsgren, Jez Humble, and Gene Kim — the research behind the four key metrics (deployment frequency, lead time, change failure rate, mean time to recovery) and how they predict organizational performance.
- <a href="https://teamtopologies.com/book" target="_blank" rel="noopener noreferrer">Team Topologies</a> by Matthew Skelton and Manuel Pais — how team structure shapes software architecture (and vice versa), the four fundamental team types, and the three interaction modes.
- **The Mythical Man-Month** by Frederick P. Brooks Jr. — essays on why adding people to a late project makes it later, the distinction between essential and accidental complexity, and the surgical team model. Published in 1975, still correct.
- <a href="https://abseil.io/resources/swe-book" target="_blank" rel="noopener noreferrer">Software Engineering at Google</a> — Chapters 9–10 on code review culture and documentation, and Chapter 22 on large-scale changes.

## Course Materials

The course is published so that anyone can teach it or work through it alone.

- <a href="https://github.com/alexdjalali/professional-software-engineering" target="_blank" rel="noopener noreferrer">The course repository</a> holds the syllabus, thirty slide decks (two per week), a lab, handout and homework with a grading rubric for every week, the reading list, and the guidance for the final architecture defense.
- <a href="https://github.com/alexdjalali/orion" target="_blank" rel="noopener noreferrer">Orion</a> is the deliberately broken system the students inherit, published as a GitHub template repository. Use it as a template and evolve your own copy.

The solutions are not public. The answer keys, the catalog of defects planted in Orion, and a reference Orion that has been taken through all fifteen weeks are kept in a private repository, so the labs stay worth doing. If you teach the course and want them, <a href="/about/">get in touch</a>.

## The Guiding Principle

Professional software engineering is not about writing code.

It is about owning systems, making decisions under constraint, and shipping reliable software in real organizations.

Everything in this course — the production-parity environments, the deliberately broken codebase, the architecture defenses, the AI integration — serves that principle. The tools and technologies will change. The languages will evolve. The AI capabilities will grow. But the discipline of engineering — the habit of making explicit decisions, enforcing quality, and accepting responsibility for what you ship — that endures.
