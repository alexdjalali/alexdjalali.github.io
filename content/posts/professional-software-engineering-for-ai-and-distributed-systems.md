---
title: "Professional Software Engineering for AI and Distributed Systems"
date: 2026-03-01
draft: false
description: "That the gap between writing code and engineering production systems can be taught, given a graduate course built on deliberate technical debt, an architecture defense and AI used as a force multiplier."
images:
  - "images/og/professional-software-engineering-for-ai-and-distributed-systems.png"
tags: ["software-engineering", "education", "distributed-systems", "ai", "architecture"]
keywords: ["software engineering course", "distributed systems", "AI engineering", "production systems", "graduate course", "architecture decision records", "trunk-based development", "clean architecture"]
series: ["AI-Assisted Engineering"]
---

Computer science programs teach programming, and on the whole they teach it well: data structures, algorithms, complexity analysis, the syntax of a language or two. Students graduate knowing how to invert a binary tree, implement a hash map and reason about Big-O. These are valuable skills. They are also, I would argue, insufficient.

The gap between writing code and engineering production systems is enormous. It's the difference between solving a problem in isolation and working inside a system that other people depend on, one that runs at scale, has to be deployed without downtime, is monitored in production, gets debugged at 2 AM, and evolves over years in the hands of people who weren't there when the original decisions were made. Most CS programs don't teach this. Most graduates discover it on the job, through expensive mistakes and patient mentors (if they're lucky enough to have mentors at all).

*Professional Software Engineering for AI and Distributed Systems* is a graduate course I designed to close that gap. It treats software engineering as a discipline distinct from computer science, with its own vocabulary, its own practices and its own ways of thinking. (As someone who came to engineering by way of a PhD in linguistics, I have some sympathy for the idea that you can know a great deal about a subject and still not know how to *practice* it.)

## The Philosophy

The course rests on a single principle, borrowed shamelessly from the world of sports:

> You play like you practice.

If you practice with toy projects, unrealistic environments and no consequences for bad decisions, that is how you will play in production. If you practice with development environments that match production, real CI/CD pipelines, and architecture decisions you have to defend in front of your peers, you'll carry those habits into your career instead.

In practice, that means <a href="https://www.docker.com/" target="_blank" rel="noopener noreferrer">Docker</a> and <a href="https://containers.dev/" target="_blank" rel="noopener noreferrer">devcontainers</a> from day one, not as a topic in week twelve but as the environment in which all the coursework happens. It means treating <a href="https://12factor.net/dev-prod-parity" target="_blank" rel="noopener noreferrer">dev/prod parity</a> as a foundational constraint rather than an aspiration. And it means secrets management and configuration discipline before students write their first feature, since in production, misconfigured environments cause more outages than buggy code does.

The course is organized around six pillars: engineering foundations; codebase and architecture mastery; distributed systems and production realism; operational excellence; AI-augmented engineering; and leadership and organizational impact. Each pillar spans several weeks, and each week builds on the ones before it.

## Orion: A Deliberately Broken System

Students don't start from scratch. They inherit a system called Orion, a distributed AI platform written in Python, with a <a href="https://fastapi.tiangolo.com/" target="_blank" rel="noopener noreferrer">FastAPI</a> service layer, an asynchronous worker service, <a href="https://www.postgresql.org/" target="_blank" rel="noopener noreferrer">PostgreSQL</a>, <a href="https://redis.io/" target="_blank" rel="noopener noreferrer">Redis</a>, a message queue, an AI integration layer and a Docker-based development environment. It works. It also has problems.

The CI pipeline is broken. The codebase carries deliberate technical debt: tightly coupled components, missing type annotations, inconsistent error handling, implicit dependencies between services, and no observability whatsoever. There are no <a href="https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions" target="_blank" rel="noopener noreferrer">Architecture Decision Records</a>, and nothing explains why things are the way they are.

All of this is on purpose. Starting from a clean codebase teaches students how to build. Starting from a messy one teaches them how to *engineer*: how to find their way around an unfamiliar system, diagnose structural problems, introduce discipline a little at a time, and make things better without breaking what already works. Every professional engineer inherits far more code than they write, and Orion is meant to reflect that.

Over the semester, the students evolve Orion together into a production-ready platform. They refactor its architecture, introduce ADRs, add static typing, adopt <a href="https://trunkbaseddevelopment.com/" target="_blank" rel="noopener noreferrer">trunk-based development</a>, build CI/CD pipelines, add observability, design safe database migrations, tune performance and cost, secure the system against real threats, and finally defend their architectural decisions in a formal review.

## Engineering Foundations

The first three weeks establish the mindset and the mechanics.

**Week 1** draws the line between a programmer and an engineer. A programmer writes code that works. An engineer owns a system: understands how it fails, considers how it behaves in operation, makes decisions under constraint, and accepts responsibility for the consequences. The distinction may sound philosophical, but it isn't. It decides whether you ship a feature and walk away, or ship it and watch what it does to latency, error rates and the services downstream. The week covers ownership, systems thinking and the ethics of AI in engineering, since students will increasingly work alongside AI systems and need some framework for when to trust the output and when to question it.

**Week 2** builds the development environment. Students configure Docker-based environments with development containers, keep development and production at parity, and learn to manage secrets. By the end of the week, every student should be able to run the entire Orion stack locally with a single command, in an environment structurally identical to the one that runs in CI. I have [written before]({{< relref "/posts/my-development-environment" >}}) about why it's worth investing in your development environment, and this week puts that into practice.

**Week 3** introduces trunk-based development. Students learn to work with short-lived branches, to use CI as an enforcement mechanism, to hide incomplete work behind <a href="https://martinfowler.com/articles/feature-toggles.html" target="_blank" rel="noopener noreferrer">feature flags</a>, and to review code rigorously. The emphasis is on small, frequent merges rather than long-lived branches, because in production the risk of integration grows with the age of a branch, and merge conflicts are a symptom of a failing process rather than of complex code.

## Codebase and Architecture Mastery

Weeks four and five teach students how to read and restructure large codebases.

**Week 4** is about finding your way around. Static typing becomes the main tool, not as an academic exercise but as a way of understanding code you didn't write. When a function signature tells you that it accepts a `TranscriptQueryParams` and returns a `list[Transcript]`, you know what it does without reading its body. (A linguist would say the types carry much of the meaning, and a linguist would be right.) Students learn to identify module boundaries, spot <a href="https://refactoring.guru/refactoring/smells" target="_blank" rel="noopener noreferrer">code smells</a>, and use type annotations as both documentation and a safety net for refactoring.

**Week 5** introduces <a href="https://en.wikipedia.org/wiki/Dependency_inversion_principle" target="_blank" rel="noopener noreferrer">dependency inversion</a> and <a href="https://en.wikipedia.org/wiki/Composition_over_inheritance" target="_blank" rel="noopener noreferrer">composition over inheritance</a>, the principles that separate maintainable architectures from brittle ones. Students refactor Orion's legacy code into a clean layered architecture, with interfaces defined before implementations, the direction of dependencies enforced by the directory structure, and cross-cutting concerns handled by composing decorators. I have written about this architecture at length in [the ideal repository structure]({{< relref "/posts/the-ideal-repository-structure" >}}) and in the companion post on [the decorator pattern for observability and resilience]({{< relref "/posts/decorator-pattern-observability-resilience" >}}).

## Testing and Delivery

Weeks six and seven address how code gets validated and shipped.

**Week 6** covers testing in distributed systems, which is a rather different problem from testing a monolith. Unit tests verify individual components, integration tests verify how services interact, and <a href="https://pact.io/" target="_blank" rel="noopener noreferrer">contract tests</a> verify that the boundaries between services honor their agreements. Students learn to design for idempotency (so that a retried operation produces the same result) and to simulate failure: network partitions, slow databases, downstream services that have simply gone away. The question to ask is not whether the thing works when everything is healthy, but whether it degrades gracefully when something isn't.

**Week 7** introduces <a href="https://martinfowler.com/articles/continuousIntegration.html" target="_blank" rel="noopener noreferrer">CI/CD</a> and release engineering. Students build multi-stage pipelines that enforce quality gates (formatting, linting, type checking, tests) on every commit. They learn to produce reproducible builds, to design rollback strategies, and to treat the deployment pipeline as code, versioned, tested and reviewed as carefully as the application itself.

## Distributed Systems and Data Safety

Weeks eight and nine introduce the theory and practice of systems that span several processes, machines and failure domains.

**Week 8** covers the fundamentals of distributed systems: consistency models, the trade-off between availability and partition tolerance, retries with exponential backoff and jitter, and <a href="https://martinfowler.com/articles/201701-event-driven.html" target="_blank" rel="noopener noreferrer">event-driven architecture</a>. The emphasis is practical. Students implement these patterns in Orion rather than reading about them, and so they get to experience what happens when a message is delivered twice, when a consumer crashes halfway through its work, and when a network timeout sets off a cascade of retries that flattens a downstream service.

**Week 9** addresses schema evolution and data safety. Databases change, and so do APIs, and the challenge is to make those changes without downtime and without breaking existing clients. Students learn zero-downtime migration patterns (expand and contract, parallel writes, backfills) and build versioned APIs that let old clients coexist with new ones. In production, the most dangerous deploys are usually not code changes at all; they are data changes.

## Operational Excellence

Weeks ten and eleven shift the focus from building systems to running them.

**Week 10** introduces observability and <a href="https://sre.google/sre-book/table-of-contents/" target="_blank" rel="noopener noreferrer">SRE</a> thinking. Students instrument Orion with structured logging, metrics and distributed tracing, and define <a href="https://sre.google/sre-book/service-level-objectives/" target="_blank" rel="noopener noreferrer">service level objectives</a>, not as abstract percentages but as concrete commitments about latency, error rates and availability that actually drive engineering decisions. They also practice incident retrospectives, the blameless kind, which look for causes in the system rather than in individuals. The aim is to move from reactive firefighting to proactive reliability engineering.

**Week 11** covers performance and cost. Students learn to profile applications systematically (CPU, memory, queries) instead of guessing where the bottleneck is, and they run load tests against Orion to find out where it breaks under pressure. Because Orion integrates AI services, they also learn the economics of tokens: what LLM inference costs at scale, how to use fewer tokens without hurting quality, and how to weigh a model's capability against what it costs to run. Performance in production, in other words, is about sustainability as much as speed.

## Security and AI

Weeks twelve and thirteen take on the two areas where the stakes are highest.

**Week 12** looks at security through the lens of production systems. Students carry out <a href="https://owasp.org/www-community/Threat_Modeling" target="_blank" rel="noopener noreferrer">threat modeling</a> against Orion, identifying its attack surfaces, classifying the threats and prioritizing mitigations. They learn <a href="https://slsa.dev/" target="_blank" rel="noopener noreferrer">supply chain security</a>: auditing dependencies, generating SBOMs, pinning versions, and the risks of trusting your dependencies' dependencies. And since Orion has an AI integration layer, they study <a href="https://owasp.org/www-project-top-10-for-large-language-model-applications/" target="_blank" rel="noopener noreferrer">prompt injection</a>, both how adversarial input can manipulate a model and what defenses against it look like in practice.

**Week 13** is about AI-augmented engineering, by which I mean AI treated neither as a toy nor as a replacement for engineering judgment, but as a professional tool that demands the same discipline as anything else in the stack. Students use LLMs for large-scale refactors, for generating tests and for augmenting code review. They learn to evaluate hallucinations systematically: how to tell when a model is confidently wrong, how to design workflows that catch its errors before they ship, and how to build the kind of engineering system I described in [a previous post]({{< relref "/posts/anatomy-of-an-ai-engineering-system" >}}), in which the AI works within explicit constraints rather than improvising freely. Whether a tool is [leverage or liability]({{< relref "/posts/how-i-learned-to-love-the-bomb" >}}) depends on the discipline of the person holding it.

## Organization and Defense

The last two weeks connect engineering to the realities of organizations.

**Week 14** covers the human side of software engineering: writing stories developers can actually implement, estimating work without false precision, managing technical debt as a portfolio rather than a line in the backlog, and living with the tension between shipping fast and shipping well. These are the skills that decide whether an engineer leads or follows, and CS programs almost never teach them.

**Week 15** is the architecture defense. Each team presents how its Orion evolved: the decisions it made, the alternatives it considered, the trade-offs it accepted and the evidence for its choices, with ADRs, architecture diagrams, observability dashboards, coverage reports, pipeline runs and live demonstrations. It isn't a final exam so much as a rehearsal of the architecture review that exists at every serious engineering organization, the moment when you have to explain not just *what* you built but *why*. (Having defended a dissertation, I can report that the experience is good for the soul, if not always for the nerves.)

## What Students Leave With

By the end of the course, students should be able to work inside distributed AI systems, make architectural decisions responsibly, refactor safely at scale, ship production-ready software, lead technical discussions, and use AI as a force multiplier rather than a crutch.

More to the point, they'll have practiced all of this under conditions that resemble the real world, which is to say not in isolation, not with toy data, and not with unlimited time and no constraints. They will have inherited a broken system, fixed it together, defended their decisions in public and shipped something that works. That experience carries over to the first day of a professional engineering job in a way that a passing grade on a data structures final simply doesn't.

## Course Reading

These are the books, articles and other resources on the course's reading list, organized by module.

### Engineering Foundations (Weeks 1–3)

- <a href="https://abseil.io/resources/swe-book" target="_blank" rel="noopener noreferrer">Software Engineering at Google</a> by Titus Winters, Tom Manshreck, and Hyrum Wright: Chapters 1–3 on what distinguishes software engineering from programming, and how Google thinks about code over time. Free to read online.
- <a href="https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/" target="_blank" rel="noopener noreferrer">The Pragmatic Programmer</a> by David Thomas and Andrew Hunt: Chapters 1–2 on pragmatic philosophy: ownership, responsibility, and the "broken windows" theory of software decay.
- <a href="https://web.stanford.edu/~ouster/cgi-bin/book.php" target="_blank" rel="noopener noreferrer">A Philosophy of Software Design</a> by John Ousterhout: Chapters 1–4 on complexity as the central problem, and the distinction between tactical and strategic programming.
- <a href="https://12factor.net/" target="_blank" rel="noopener noreferrer">The Twelve-Factor App</a> by Adam Wiggins: all twelve factors, with emphasis on <a href="https://12factor.net/dev-prod-parity" target="_blank" rel="noopener noreferrer">Factor X: Dev/Prod Parity</a> and <a href="https://12factor.net/config" target="_blank" rel="noopener noreferrer">Factor III: Config</a>.
- <a href="https://trunkbaseddevelopment.com/" target="_blank" rel="noopener noreferrer">Trunk Based Development</a> by Paul Hammant: the complete site, covering short-lived branches, branch by abstraction, and feature flags.
- <a href="https://martinfowler.com/articles/feature-toggles.html" target="_blank" rel="noopener noreferrer">Feature Toggles</a> by Pete Hodgson (Martin Fowler's site): taxonomy of toggle types, lifecycle management, and the operational burden of flags.
- <a href="https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions" target="_blank" rel="noopener noreferrer">Documenting Architecture Decisions</a> by Michael Nygard: the original blog post that introduced lightweight ADRs.

### Codebase and Architecture Mastery (Weeks 4–5)

- <a href="https://refactoring.com/" target="_blank" rel="noopener noreferrer">Refactoring: Improving the Design of Existing Code</a> by Martin Fowler: the catalog of refactorings and the chapter on code smells. The companion site <a href="https://refactoring.guru/refactoring/smells" target="_blank" rel="noopener noreferrer">Refactoring Guru</a> provides visual explanations of each smell.
- **Clean Architecture** by Robert C. Martin: Part V on architecture, with emphasis on the dependency rule, the stable abstractions principle, and the separation of policy from detail.
- <a href="https://pragprog.com/titles/tpp20/the-pragmatic-programmer-20th-anniversary-edition/" target="_blank" rel="noopener noreferrer">The Pragmatic Programmer</a>: Chapter 5 on decoupling: the Law of Demeter, metaprogramming, and reducing coupling between components.
- [The Ideal Repository Structure](/posts/the-ideal-repository-structure/): how strict layer boundaries prevent architectural decay, with Go and Python examples of interface-first, layered monorepo design.
- [The Decorator Pattern for Observability and Resilience](/posts/decorator-pattern-observability-resilience/): composing cross-cutting concerns through decorator stacks rather than scattering them through business logic.

### Testing and Delivery (Weeks 6–7)

- <a href="https://www.oreilly.com/library/view/working-effectively-with/0131177052/" target="_blank" rel="noopener noreferrer">Working Effectively with Legacy Code</a> by Michael Feathers: the definitive guide to introducing tests into codebases that were not designed for testability. Chapters on seam identification and breaking dependencies.
- <a href="https://martinfowler.com/articles/practical-test-pyramid.html" target="_blank" rel="noopener noreferrer">The Practical Test Pyramid</a> by Ham Vocke (Martin Fowler's site): a modern restatement of the test pyramid with concrete examples of unit, integration, and end-to-end tests.
- <a href="https://docs.pact.io/" target="_blank" rel="noopener noreferrer">Pact Documentation</a>: consumer-driven contract testing for microservices. How to verify that service boundaries honor their agreements without running full integration environments.
- <a href="https://continuousdelivery.com/" target="_blank" rel="noopener noreferrer">Continuous Delivery</a> by Jez Humble and David Farley: the foundational text on deployment pipelines, reproducible builds, and the practice of keeping software in a releasable state at all times.
- <a href="https://martinfowler.com/articles/continuousIntegration.html" target="_blank" rel="noopener noreferrer">Continuous Integration</a> by Martin Fowler: the principles behind CI as a practice, not just a tool.

### Distributed Systems and Data Safety (Weeks 8–9)

- <a href="https://dataintensive.net/" target="_blank" rel="noopener noreferrer">Designing Data-Intensive Applications</a> by Martin Kleppmann: Part II on distributed data: replication, partitioning, consistency, and consensus. The single most important textbook for understanding distributed systems in practice.
- <a href="https://martinfowler.com/articles/201701-event-driven.html" target="_blank" rel="noopener noreferrer">What do you mean by "Event-Driven"?</a> by Martin Fowler: disambiguating event notification, event-carried state transfer, event sourcing, and CQRS.
- <a href="https://jepsen.io/consistency" target="_blank" rel="noopener noreferrer">Jepsen: Consistency Models</a> by Kyle Kingsbury: a visual guide to the hierarchy of consistency models, from linearizability to eventual consistency.
- <a href="https://queue.acm.org/detail.cfm?id=3025012" target="_blank" rel="noopener noreferrer">Life beyond Distributed Transactions</a> by Pat Helland: how to build correct applications without relying on distributed transactions, using idempotency and natural keys.
- <a href="https://pragprog.com/titles/mnee2/release-it-second-edition/" target="_blank" rel="noopener noreferrer">Release It!</a> by Michael Nygard: stability patterns (circuit breakers, bulkheads, timeouts) and anti-patterns (cascading failures, blocked threads, self-denial attacks). Essential reading for building systems that survive production.

### Operational Excellence (Weeks 10–11)

- <a href="https://sre.google/sre-book/table-of-contents/" target="_blank" rel="noopener noreferrer">Site Reliability Engineering</a> edited by Betsy Beyer, Chris Jones, Jennifer Petoff, and Niall Richard Murphy: Chapters on <a href="https://sre.google/sre-book/service-level-objectives/" target="_blank" rel="noopener noreferrer">service level objectives</a>, <a href="https://sre.google/sre-book/monitoring-distributed-systems/" target="_blank" rel="noopener noreferrer">monitoring distributed systems</a>, and <a href="https://sre.google/sre-book/postmortem-culture/" target="_blank" rel="noopener noreferrer">postmortem culture</a>. Free to read online.
- <a href="https://sre.google/workbook/table-of-contents/" target="_blank" rel="noopener noreferrer">The Site Reliability Workbook</a>: the practical companion to the SRE book, with worked examples of SLO implementation, alerting strategies, and incident response. Free to read online.
- <a href="https://www.oreilly.com/library/view/observability-engineering/9781492076438/" target="_blank" rel="noopener noreferrer">Observability Engineering</a> by Charity Majors, Liz Fong-Jones, and George Miranda: the distinction between monitoring and observability, structured events over metrics, and high-cardinality debugging in distributed systems.
- <a href="https://how.complexsystems.fail/" target="_blank" rel="noopener noreferrer">How Complex Systems Fail</a> by Richard I. Cook: a short, essential paper on why complex systems fail, how failure is evaluated after the fact, and why hindsight bias distorts incident analysis. Required reading before the first retrospective exercise.

### Security and AI (Weeks 12–13)

- <a href="https://owasp.org/www-project-top-ten/" target="_blank" rel="noopener noreferrer">OWASP Top 10</a>: the standard reference for web application security risks: injection, broken authentication, sensitive data exposure, and the rest. Students should be able to identify each risk category in Orion's codebase.
- <a href="https://owasp.org/www-project-top-10-for-large-language-model-applications/" target="_blank" rel="noopener noreferrer">OWASP Top 10 for Large Language Model Applications</a>: prompt injection, insecure output handling, training data poisoning, and other LLM-specific attack vectors. The AI-era companion to the classic Top 10.
- <a href="https://slsa.dev/spec/v1.0/" target="_blank" rel="noopener noreferrer">SLSA Framework</a> (Supply-chain Levels for Software Artifacts): a security framework for achieving increasing levels of supply chain integrity, from basic provenance to hermetic builds.
- **Threat Modeling: Designing for Security** by Adam Shostack: the STRIDE methodology, attack trees, and practical approaches to identifying threats before they become vulnerabilities.
- [Anatomy of an AI Engineering System](/posts/anatomy-of-an-ai-engineering-system/): how composable skills, quality gates, and model tiers turn AI tools into a disciplined engineering workflow rather than unconstrained generation.
- [How I Learned to Love the Bomb](/posts/how-i-learned-to-love-the-bomb/): the shift from AI skepticism to building an engineering system around it, and why the leverage is real only if you bring the discipline with you.

### Organization and Leadership (Weeks 14–15)

- <a href="https://itrevolution.com/product/accelerate/" target="_blank" rel="noopener noreferrer">Accelerate</a> by Nicole Forsgren, Jez Humble, and Gene Kim: the research behind the four key metrics (deployment frequency, lead time, change failure rate, mean time to recovery) and how they predict organizational performance.
- <a href="https://teamtopologies.com/book" target="_blank" rel="noopener noreferrer">Team Topologies</a> by Matthew Skelton and Manuel Pais: how team structure shapes software architecture (and vice versa), the four fundamental team types, and the three interaction modes.
- **The Mythical Man-Month** by Frederick P. Brooks Jr.: essays on why adding people to a late project makes it later, the distinction between essential and accidental complexity, and the surgical team model. Published in 1975, still correct.
- <a href="https://abseil.io/resources/swe-book" target="_blank" rel="noopener noreferrer">Software Engineering at Google</a>: Chapters 9–10 on code review culture and documentation, and Chapter 22 on large-scale changes.

## Course Materials

The course is published so that anyone can teach it, or work through it on their own.

- <a href="https://github.com/alexdjalali/professional-software-engineering" target="_blank" rel="noopener noreferrer">The course repository</a> holds the syllabus, thirty slide decks (two per week), a lab, handout and homework with a grading rubric for every week, the reading list, and the guidance for the final architecture defense.
- <a href="https://github.com/alexdjalali/orion" target="_blank" rel="noopener noreferrer">Orion</a> is the deliberately broken system the students inherit, published as a GitHub template repository. Use it as a template and evolve your own copy.

The solutions are not public. The answer keys, the catalog of defects planted in Orion, and a reference Orion taken through all fifteen weeks live in a private repository, so that the labs stay worth doing. If you teach the course and would like them, <a href="https://calendly.com/alex-djalali/30min" target="_blank" rel="noopener noreferrer">book a call</a>.

## The Guiding Principle

If there is one idea behind all of this, it's that professional software engineering is not really about writing code. It's about owning systems, making decisions under constraint, and shipping reliable software inside real organizations.

Everything in the course (the environments that match production, the deliberately broken codebase, the architecture defenses, the AI integration) serves that idea. The tools will change, the languages will evolve, and the models will certainly get better. But the discipline of engineering, the habit of making decisions explicitly, enforcing quality and taking responsibility for what you ship, is the part I expect to outlast all of them.
