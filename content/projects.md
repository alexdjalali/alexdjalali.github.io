---
title: "Projects"
date: 2026-03-05
draft: false
type: "projects"
description: "Active engineering projects by AJ Djalali spanning distributed search systems, NLP pipelines, and large-scale data infrastructure."
images:
  - "images/og-default.png"
---

## Present

<div class="project-card">
  <h2>House Proceedings Corpus</h2>
  <div class="project-tech-list">
    <span class="project-tech">Python</span>
    <span class="project-tech">FastAPI</span>
    <span class="project-tech">Kafka</span>
    <span class="project-tech">Elasticsearch</span>
    <span class="project-tech">Neo4j</span>
    <span class="project-tech">spaCy</span>
    <span class="project-tech">Docker</span>
    <span class="project-tech">Prometheus</span>
    <span class="project-tech">Grafana</span>
  </div>
  <p>
    The House Proceedings Corpus (HPC) is a multi-service search and analysis platform built for large-scale congressional text. The system indexes over 181 million tokens across 2,700+ transcripts from the U.S. House of Representatives, enabling full-text search, entity-based exploration, and structural analysis of legislative discourse.
  </p>
  <p>
    The architecture follows an event-driven, microservice design. A FastAPI gateway handles ingest and query routing, Kafka brokers decouple producers from consumers, Elasticsearch powers full-text and faceted search, and Neo4j stores entity graphs linking speakers, bills, committees, and topics. An NLP pipeline built on spaCy extracts named entities, noun phrases, and dependency structures at ingest time, enriching every transcript with structured annotations before it reaches the search index.
  </p>
  <p>
    The project emphasizes clean layered architecture with strict separation between domain logic, data access, and API surfaces. Each service follows a repository pattern with dependency injection at the composition root. The full observability stack&mdash;Prometheus metrics, Grafana dashboards, structured JSON logging&mdash;provides real-time visibility into pipeline throughput, query latency, and service health. An interactive transcript editor supports manual correction and re-annotation of processed documents.
  </p>
  <p>
    <a href="https://github.com/alexdjalali/hpc" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-github"></i> View on GitHub</a>
  </p>
</div>

<div class="project-card">
  <h2>Enterprise Search &amp; Ingestion Platform</h2>
  <div class="project-tech-list">
    <span class="project-tech">Python</span>
    <span class="project-tech">FastAPI</span>
    <span class="project-tech">Ray</span>
    <span class="project-tech">Spark</span>
    <span class="project-tech">Databricks</span>
    <span class="project-tech">CLIP</span>
    <span class="project-tech">S3</span>
    <span class="project-tech">Qdrant</span>
    <span class="project-tech">Redis</span>
    <span class="project-tech">GPU</span>
    <span class="project-tech">Docker</span>
  </div>
  <p>
    A large-scale semantic search and image ingestion platform designed for enterprise workloads. The system supports both text and visual queries across millions of records, combining dense vector retrieval with structured metadata filtering to deliver sub-200ms query latency at production scale.
  </p>
  <h3>Search</h3>
  <div class="mermaid">
graph LR
Q[Query] --> API[FastAPI]
API --> Cache[Redis Cache]
API --> QD[Qdrant]
Cache --> R[Response]
QD --> R
style Q fill:#e1f5ff,stroke:#333
style API fill:#fff3cd,stroke:#333
style Cache fill:#d4edda,stroke:#333
style QD fill:#d1ecf1,stroke:#333
style R fill:#e1f5ff,stroke:#333
  </div>
  <p>
    The search API, built on FastAPI, exposes hybrid retrieval that blends dense vector nearest-neighbor search with keyword and metadata filters. The platform uses Qdrant as its vector database backend, with a repository abstraction that keeps provider-specific APIs behind a consistent service layer.
  </p>
  <p>
    Fault tolerance is built into every layer of the search path. Circuit breakers wrap each vector store client, tripping after configurable failure thresholds to prevent cascade failures and automatically recovering once the backend is healthy. Retry logic with exponential backoff handles transient network errors, and connection pooling bounds resource consumption under burst traffic. A Redis caching layer absorbs hot-query load, and the system gracefully degrades&mdash;returning partial results or cached responses&mdash;when downstream dependencies are unavailable rather than failing outright.
  </p>
  <p>
    Observability covers the full request lifecycle. Structured JSON logs attach correlation IDs to every query, and Prometheus metrics track query latency percentiles, cache hit rates, circuit breaker state transitions, and per-backend error rates. A benchmark pipeline continuously measures recall, throughput, and tail latency across configurations, enabling data-driven decisions about quantization strategies, index parameters, and replication factors. The architecture follows clean layered patterns with repository abstractions for each vector store, dependency injection throughout, and comprehensive integration tests against containerized infrastructure.
  </p>
  <h3>Ingestion</h3>
  <div class="mermaid">
graph LR
S3[S3] --> Spark[Spark Read]
Spark --> Ray[Ray Cluster]
Ray --> GPU1[GPU Worker]
Ray --> GPU2[GPU Worker]
Ray --> GPU3[GPU Worker]
GPU1 --> CLIP1[CLIP Embed]
GPU2 --> CLIP2[CLIP Embed]
GPU3 --> CLIP3[CLIP Embed]
CLIP1 --> Quant[Quantize]
CLIP2 --> Quant
CLIP3 --> Quant
Quant --> QD[Qdrant]
style S3 fill:#e1f5ff,stroke:#333
style Spark fill:#fff3cd,stroke:#333
style Ray fill:#d4edda,stroke:#333
style GPU1 fill:#f8d7da,stroke:#333
style GPU2 fill:#f8d7da,stroke:#333
style GPU3 fill:#f8d7da,stroke:#333
style CLIP1 fill:#d1ecf1,stroke:#333
style CLIP2 fill:#d1ecf1,stroke:#333
style CLIP3 fill:#d1ecf1,stroke:#333
style Quant fill:#fff3cd,stroke:#333
style QD fill:#e2e3e5,stroke:#333
  </div>
  <p>
    The ingestion engine moves images from S3 through CLIP embedding generation and into Qdrant at massive scale. The end-to-end pipeline has completed clean runs over 4 million images with zero errors, running on distributed Ray clusters deployed through Databricks.
  </p>
  <p>
    Ray handles distributed task orchestration while Spark provides high-throughput data reads from S3. Images are streamed in batches through CLIP running on GPU workers, where embeddings are generated, optionally quantized (scalar and binary), and written directly into the target vector store. Careful batch sizing, backpressure handling, and per-worker fault isolation ensure that individual image failures never halt the broader run&mdash;the pipeline has maintained zero-error completion across multi-million-image datasets.
  </p>
  <p>
    Performance optimization has been a central focus. By scaling CLIP inference across GPU-backed Ray workers and tuning batch geometry, prefetch depth, and write concurrency, the engine can process over 400 million images in under 24 hours. Quantization is applied at embedding time rather than post-hoc, eliminating a separate reduction pass and cutting total wall-clock time. The system dynamically balances GPU utilization against vector store write throughput to prevent either side from becoming the bottleneck.
  </p>
  <p>
    Fault tolerance is engineered at the batch level. Each Ray task processes an isolated image batch with its own error boundary&mdash;corrupt images, transient S3 read failures, and vector store write timeouts are caught, logged, and retried without affecting other in-flight batches. Dead-letter tracking records any image that exhausts retries so it can be reprocessed in a subsequent run. Per-worker fault isolation means a single node failure triggers automatic rescheduling across the remaining cluster rather than a full pipeline abort.
  </p>
  <p>
    Observability is woven through every stage. Structured JSON logs tag each batch with a run ID, source prefix, and worker identity, creating a complete audit trail from S3 object to vector store record. Real-time metrics track per-batch embedding throughput, GPU utilization, write latency, and queue depth, surfaced through dashboards that make bottlenecks immediately visible. End-of-run reconciliation compares source object counts against final record counts in the target vector store, flagging any discrepancies before the run is marked complete.
  </p>
  <p>
    The architecture cleanly separates reading, embedding, and writing into composable stages, each independently scalable.
  </p>
</div>

<hr class="section-divider">

## Past

<div class="project-card">
  <h2>PerceptivePanda</h2>
  <div class="project-tech-list">
    <span class="project-tech">Python</span>
    <span class="project-tech">LLMs</span>
    <span class="project-tech">Discourse Theory</span>
    <span class="project-tech">Dialogue State Management</span>
    <span class="project-tech">FastAPI</span>
    <span class="project-tech">React</span>
  </div>
  <p>
    PerceptivePanda was an AI-native customer research platform that replaced traditional human-led interviews with AI-driven micro-interviews at scale. I co-founded the company and served as CTO, architecting the entire technical stack. The platform conducted dynamic, adaptive conversations that captured meaningful customer feedback for SaaS and e-commerce growth teams, addressing use cases like churn analysis and trial conversion. PerceptivePanda was a <a href="https://startx.com/" target="_blank" rel="noopener noreferrer">StartX</a> &rsquo;24 Summer cohort company and was <a href="https://zapier.com/blog/perceptive-panda-joins-zapier/" target="_blank" rel="noopener noreferrer">acquired by Zapier</a> in January 2026.
  </p>
  <p>
    The core technical contribution was a deterministic control layer that wrapped LLMs to guardrail and drive natural Q&amp;A conversation. Rather than exposing a raw language model to users, the system modeled dialogue state in real time using a discrete framework grounded in discourse theory from my work at Stanford&mdash;particularly the Questions Under Discussion (QUD) model of information structure. The wrapper tracked which questions had been addressed, which threads deserved deeper probing, and when to broaden the inquiry to a new topic, orchestrating LLM calls through a structured state machine that ensured every interview followed a coherent analytical arc while preserving the fluidity of natural conversation.
  </p>
  <p>
    This architecture solved a fundamental limitation of using LLMs directly for structured research: a raw model has no principled way to decide when to go deep versus when to circle back and go broad. The discourse-theoretic layer provided exactly that&mdash;a formal model of conversational relevance and information need that governed the LLM&rsquo;s behavior at each turn. The result was interviews that felt natural to respondents but produced structured, analyzable data for research teams.
  </p>
</div>

<div class="project-card">
  <h2>ClearGraph / Tableau Ask Data</h2>
  <div class="project-tech-list">
    <span class="project-tech">NLP</span>
    <span class="project-tech">Montague Grammar</span>
    <span class="project-tech">Context-Free Grammar</span>
    <span class="project-tech">Formal Semantics</span>
    <span class="project-tech">Java</span>
    <span class="project-tech">Python</span>
    <span class="project-tech">Elasticsearch</span>
  </div>
  <p>
    At ClearGraph, I architected the proprietary natural language querying (NLQ) technology that let non-technical users analyze data by typing plain-English questions instead of writing SQL. In 2017, <a href="https://www.prnewswire.com/news-releases/tableau-acquires-natural-language-query-startup-cleargraph-300501577.html" target="_blank" rel="noopener noreferrer">Tableau acquired ClearGraph</a>&mdash;at the time a five-person team&mdash;and the technology became <strong>Tableau Ask Data</strong>, shipping in Tableau 2019.1. I led the integration and scaling effort at Tableau, growing the team to over 30 engineers at its peak and deploying Ask Data to hundreds of thousands of users across Tableau's product suite.
  </p>
  <p>
    The system solved the NLQ problem before the modern AI era&mdash;the core architecture was designed and deployed before BERT was even published. Rather than relying on learned representations, the approach drew directly on work from my time at Stanford in formal semantics, particularly Montague Grammar and proof-theoretic grammars. User utterances were parsed into an intermediate representation called ArkLang using context-free grammar rules enriched with a compositional semantic model of the underlying data source. The grammar composed meaning incrementally&mdash;each syntactic rule carried a corresponding semantic action that built up a formal representation of the user's analytical intent, resolving ambiguity, underspecification, and implicit context at each stage of the derivation.
  </p>
  <p>
    This approach handled challenges that statistical methods of the time could not: inferring omitted data fields, resolving scope ambiguities in aggregation, supporting cascading edits where modifying one phrase automatically updated dependent expressions, and maintaining conversational context across multi-turn analytical sessions. The system distinguished between explicit user intent and implicit intent inferred from the current visualization state, enabling coherent iterative workflows without dead ends.
  </p>
  <p>
    The work produced 9 issued patents covering the core NLQ architecture, underspecification resolution, intent inference, cascading edits, table calculations via natural language, and incremental visual feedback during query composition:
  </p>
  <ul class="cv-list" style="margin-top: 0.5em;">
    <li><a href="https://patents.google.com/patent/US11550853B2" target="_blank" rel="noopener noreferrer">US-11550853-B2</a> &mdash; Table calculations via natural language</li>
    <li><a href="https://patents.google.com/patent/US11314817B1" target="_blank" rel="noopener noreferrer">US-11314817-B1</a> &mdash; Intent inference and context for NL expressions</li>
    <li><a href="https://patents.google.com/patent/US11301631B1" target="_blank" rel="noopener noreferrer">US-11301631-B1</a> &mdash; Visual correlation of NL terms to structured phrases</li>
    <li><a href="https://patents.google.com/patent/US11244114B2" target="_blank" rel="noopener noreferrer">US-11244114-B2</a> &mdash; Analyzing underspecified NL utterances</li>
    <li><a href="https://patents.google.com/patent/US11055489B2" target="_blank" rel="noopener noreferrer">US-11055489-B2</a> &mdash; Levels of detail via NL constructs</li>
    <li><a href="https://patents.google.com/patent/US11048871B2" target="_blank" rel="noopener noreferrer">US-11048871-B2</a> &mdash; Analyzing NL expressions in data visualization</li>
    <li><a href="https://patents.google.com/patent/US10902045B2" target="_blank" rel="noopener noreferrer">US-10902045-B2</a> &mdash; NL interface with cascading filter edits</li>
    <li><a href="https://patents.google.com/patent/US20220253481A1" target="_blank" rel="noopener noreferrer">US-20220253481-A1</a> &mdash; Inferring intent for NL in data visualization</li>
    <li><a href="https://patents.google.com/patent/US20210319186A1" target="_blank" rel="noopener noreferrer">US-20210319186-A1</a> &mdash; Using NL constructs for data visualizations</li>
  </ul>
</div>

<div class="project-card">
  <h2>Partial Order Optimality Theory</h2>
  <div class="project-tech-list">
    <span class="project-tech">Python</span>
    <span class="project-tech">Order Theory</span>
    <span class="project-tech">Lattice Theory</span>
    <span class="project-tech">Combinatorics</span>
  </div>
  <p>
    Companion implementation to <a href="https://link.springer.com/article/10.1007/s10849-017-9248-0" target="_blank" rel="noopener noreferrer">"A constructive solution to the ranking problem in Partial Order Optimality Theory"</a> (<em>Journal of Logic, Language &amp; Information</em>, 2017). Classical Optimality Theory (OT) assumes grammars are strict total orders over a set of constraints, but this makes it impossible to model free variation&mdash;cases where multiple surface forms are grammatical for a single input. Partial Order Optimality Theory (PoOT) generalizes the framework by allowing grammars to be arbitrary partial orders, but the ranking problem&mdash;given observed input/output pairs, find <em>all</em> grammars compatible with the data&mdash;had remained unsolved.
  </p>
  <p>
    The paper provides a set-theoretic construction that solves the PoOT ranking problem exactly. The key insight is that the space of all partial orders over <em>n</em> constraints forms a lattice under the subset relation. Each candidate pair induces a set of grammars that make the intended winner optimal, and the compatible grammar set is computed by intersecting winner sets and subtracting loser sets across the entire dataset. The construction also yields candidate entailments&mdash;logical relationships showing that if one form is grammatical, another must or cannot be.
  </p>
  <p>
    The codebase implements this construction end to end. It generates the full lattice of strict partial orders for a given constraint set, pre-computing the upset and downset of every element. From there it enriches raw candidates with violation-vector comparisons, computes the functional space mapping losers to winners (the set-theoretic core of the proof), and derives the classical and partial-order grammar sets from that mapping. The system returns the full set of compatible grammars (both classical OT and PoOT), identifies harmonically bounded candidates, computes minimal and maximal compatible grammars within the lattice, and derives atomic and set-based candidate entailments.
  </p>
  <p>
    The repository includes datasets from the paper&mdash;Finnish vowel coalescence and Finnish semantically conditioned case&mdash;with constraint sets of 4 and 6 constraints respectively, exercising the system against linguistically motivated tableaux with both free variation and categorical outcomes.
  </p>
  <p>
    <a href="https://github.com/alexdjalali/OT" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-github"></i> View on GitHub</a>
  </p>
</div>
