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
  {{< construction "projects/conversational-document-intelligence" >}}
  <h2>Conversational Document Intelligence Platform</h2>
  <div class="project-tech-list">
    <span class="project-tech">Go</span>
    <span class="project-tech">Python</span>
    <span class="project-tech">TypeScript</span>
    <span class="project-tech">React</span>
    <span class="project-tech">Protobuf</span>
    <span class="project-tech">PostgreSQL</span>
    <span class="project-tech">Redis</span>
    <span class="project-tech">S3</span>
    <span class="project-tech">SQS</span>
    <span class="project-tech">Bedrock</span>
    <span class="project-tech">Ray</span>
    <span class="project-tech">Auth0</span>
    <span class="project-tech">Kong</span>
    <span class="project-tech">Kubernetes</span>
    <span class="project-tech">OpenTelemetry</span>
  </div>
  <p>
    A multi-tenant enterprise platform for conversational question-answering over an organization's documents, built for an enterprise client (proprietary, so unnamed here) and delivered in phases.
  </p>
  <p>
    <strong>Phase 1: the RAG platform (delivered).</strong> The end-to-end pipeline, built in about three months: upload, ingest, index, retrieve, and a citation-backed answer streamed back over WebSockets. Users upload documents in nine supported formats; an ingestion pipeline parses them through a distributed worker fleet (with a Ray lane for bulk loads), extracts page-level citation provenance, and syncs content into a managed RAG knowledge base. The query path rewrites multi-turn conversations into standalone questions, performs semantic retrieval with metadata-aware filtering (workspace, classification, trust level), and streams LLM-generated answers with source citations. Tenancy follows an organization, team, and workspace hierarchy, and each user's clearance level is checked against document classification at retrieval time. Go services handle identity, API orchestration, and connector management over Protobuf contracts with code-generated ORM schemas; Python services handle parsing, retrieval, and notification dispatch; the frontend is React, TypeScript, and Tailwind. Both languages share a strict eight-layer architecture&mdash;core interfaces through transport&mdash;with decorator builders composing logging, metrics, tracing, retry, and circuit breaking at each boundary. A custom CLI replaces Makefiles as the sole task runner across code generation, testing, migrations, and deployment. It runs on Kubernetes behind an API gateway, with Helm charts, Kustomize overlays, Terraform-provisioned cloud resources, and full observability via Grafana, Prometheus, Loki, and Tempo.
  </p>
  <p>
    <strong>Phase 2: AI operations and economics (in progress).</strong> Phase 2 makes the AI stack observable, measurable, affordable, and auditable: every production AI call is traced, sample-evaluated, budget-enforced, cache-eligible, and audited, and prompts and models are promoted only through evaluation gates. Its scope is an evaluation platform with graders, a versioned prompt registry, an AI audit trail that produces SOC&nbsp;2 and HIPAA evidence, a token ledger with per-tenant budgets, a model gateway with semantic routing and cost controls, a semantic response cache, quality and drift monitoring, and an AI-operations console. It adds no new architectural layer: each capability is a new interface with a configuration-selected implementation and a no-op default, or a new decorator in the existing stacks, enabled per concern and per environment. LLM and agent tracing and the first AI-operations console and analytics screens have shipped.
  </p>
</div>

<div class="project-card">
  {{< construction "projects/house-proceedings-corpus" >}}
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
    A multi-service search and analysis platform for large-scale congressional text, indexing over 181 million tokens across 2,700+ U.S. House transcripts. A FastAPI gateway routes queries, Kafka decouples ingest pipelines, Elasticsearch powers full-text and faceted search, and Neo4j stores entity graphs linking speakers, bills, committees, and topics. A spaCy-based NLP pipeline extracts named entities, noun phrases, and dependency structures at ingest time. The system follows clean layered architecture with repository pattern, dependency injection, and full observability via Prometheus metrics, Grafana dashboards, and structured JSON logging.
  </p>
  <p>
    <a href="https://github.com/alexdjalali/hpc" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-github"></i> View on GitHub</a>
  </p>
</div>

<hr class="section-divider">

## Past

<div class="project-card">
  {{< construction "projects/enterprise-search-ingestion" >}}
  <h2>Enterprise Search &amp; Ingestion Platform</h2>
  <div class="project-tech-list">
    <span class="project-tech">Python</span>
    <span class="project-tech">FastAPI</span>
    <span class="project-tech">Ray</span>
    <span class="project-tech">Spark</span>
    <span class="project-tech">Databricks</span>
    <span class="project-tech">CLIP</span>
    <span class="project-tech">Qdrant</span>
    <span class="project-tech">Weaviate</span>
    <span class="project-tech">S3</span>
    <span class="project-tech">MinIO</span>
    <span class="project-tech">Redis</span>
    <span class="project-tech">GPU</span>
    <span class="project-tech">Prometheus</span>
    <span class="project-tech">Docker</span>
  </div>
  <p>
    A large-scale semantic search and image ingestion platform built with <a href="https://www.inaturalist.org/" target="_blank" rel="noopener noreferrer">iNaturalist</a> and released as open source under the MIT license (<strong>iNatInq</strong>). I am its top contributor. It has two engines. The <strong>query engine</strong> embeds a text query with CLIP, checks a semantic cache, and runs dense nearest-neighbor retrieval in Qdrant (Weaviate is also supported) blended with keyword and metadata filters, delivering sub-200ms query latency. The <strong>ingestion engine</strong> lists images in S3, embeds them with CLIP on distributed Ray/GPU clusters (with Spark and Databricks pipelines alongside), and upserts the vectors to Qdrant, processing over 400 million images in under 24 hours.
  </p>
  <p>
    Every external call is wrapped in retry with exponential backoff, circuit breakers, and rate limiting, so search degrades gracefully when a dependency fails. Ingestion is built to finish clean at scale: batch-level fault isolation, a dead-letter queue with reprocessing, checkpointing for resumable jobs, change data capture for incremental updates, and end-of-run reconciliation. Prometheus metrics cover clients, breakers, retries, cache, search, and ingestion, and all logs are structured.
  </p>
  <p>
    Retrieval quality is measured, not assumed. A benchmark harness scores Precision@K, Recall@K, NDCG@K, MAP@K, and MRR, along with p50/p95 latency and throughput, against the <a href="https://arxiv.org/abs/2411.02537" target="_blank" rel="noopener noreferrer">INQUIRE</a> text-to-image retrieval benchmark (Vendrow et al., NeurIPS 2024). INQUIRE pairs 250 expert-level natural-world queries with iNat24, a dataset of five million iNaturalist images. The same harness compares vector-database providers and four quantization profiles (float32, scalar, scalar with rescoring, and binary with rescoring).
  </p>
  <p>
    <a href="https://github.com/inaturalist/Inquire-vector-search" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-github"></i> View on GitHub</a>
  </p>
</div>

<div class="project-card">
  {{< construction "projects/perceptivepanda" >}}
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
    PerceptivePanda was an AI-native customer research platform that replaced traditional human-led interviews with AI-driven micro-interviews at scale. I co-founded the company and served as CTO. The core contribution was a deterministic control layer wrapping LLMs using a dialogue state framework grounded in discourse theory from my work at Stanford&mdash;particularly the Questions Under Discussion model. The system tracked addressed questions, identified threads for deeper probing, and orchestrated LLM calls through a structured state machine, ensuring coherent analytical conversations while preserving natural fluidity. PerceptivePanda was a <a href="https://startx.com/" target="_blank" rel="noopener noreferrer">StartX</a> &rsquo;24 company, <a href="https://zapier.com/blog/perceptive-panda-joins-zapier/" target="_blank" rel="noopener noreferrer">acquired by Zapier</a> in January 2026.
  </p>
</div>

<div class="project-card">
  {{< construction "projects/cleargraph-ask-data" >}}
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
    At ClearGraph, I architected the natural language querying technology that became <strong>Tableau Ask Data</strong> after <a href="https://www.prnewswire.com/news-releases/tableau-acquires-natural-language-query-startup-cleargraph-300501577.html" target="_blank" rel="noopener noreferrer">Tableau&rsquo;s 2017 acquisition</a>. I led integration and scaling, growing the team to 30+ engineers and deploying to hundreds of thousands of users. The system&mdash;designed before BERT existed&mdash;used Montague Grammar and compositional semantics from my Stanford research. User utterances were parsed via context-free grammar rules into a formal intermediate representation, resolving ambiguity, underspecification, and implicit context at each derivation stage. The work produced 9 issued patents covering NLQ architecture, intent inference, cascading edits, table calculations, and incremental visual feedback:
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
  {{< construction "projects/poot" >}}
  <h2>Partial Order Optimality Theory</h2>
  <div class="project-tech-list">
    <span class="project-tech">Python</span>
    <span class="project-tech">Order Theory</span>
    <span class="project-tech">Lattice Theory</span>
    <span class="project-tech">Combinatorics</span>
  </div>
  <p>
    Companion implementation to <a href="https://link.springer.com/article/10.1007/s10849-017-9248-0" target="_blank" rel="noopener noreferrer">&ldquo;A constructive solution to the ranking problem in Partial Order Optimality Theory&rdquo;</a> (<em>Journal of Logic, Language &amp; Information</em>, 2017). Classical OT assumes grammars are strict total orders over constraints, making it impossible to model free variation. PoOT generalizes to arbitrary partial orders, but the ranking problem&mdash;finding all compatible grammars from observed data&mdash;was unsolved. The paper provides an exact set-theoretic construction exploiting the lattice structure of partial orders. The codebase generates the full lattice, computes grammar sets via winner/loser set intersection, identifies harmonically bounded candidates, and derives candidate entailments. Includes Finnish vowel coalescence and case datasets.
  </p>
  <p>
    <a href="https://github.com/alexdjalali/OT" target="_blank" rel="noopener noreferrer"><i class="fa-brands fa-github"></i> View on GitHub</a>
  </p>
</div>

<div class="project-card">
  {{< construction "projects/dissertation" >}}
  <h2>Doctoral Dissertation: On Adjectival Comparatives</h2>
  <div class="project-tech-list">
    <span class="project-tech">Formal Semantics</span>
    <span class="project-tech">Continuation Semantics</span>
    <span class="project-tech">Montague Grammar</span>
    <span class="project-tech">Type Theory</span>
    <span class="project-tech">Syntax</span>
  </div>
  <p>
    <a href="https://stacks.stanford.edu/file/druid:zd767rn6093/djalali_diss_final-augmented.pdf" target="_blank" rel="noopener noreferrer"><em>The syntax and semantics of ordinary comparative constructions in English</em></a>. PhD Dissertation, Stanford University, 2015. The dissertation argues that standard degree-based analyses of comparatives are fundamentally flawed&mdash;requiring abstract degrees as first-class objects and covert operators to handle scope. The alternative framework, grounded in Barker and Shan&rsquo;s continuation semantics and Muskens&rsquo; simplified Montague logic, computes comparative meaning compositionally through continuation-passing without positing degrees or hidden structure. The account covers phrasal, clausal, sub-, and differential comparatives, and resolves long-standing puzzles around scope interactions between comparatives and quantifiers.
  </p>
  <p>
    <a href="https://stacks.stanford.edu/file/druid:zd767rn6093/djalali_diss_final-augmented.pdf" target="_blank" rel="noopener noreferrer"><i class="fa-solid fa-file-pdf"></i> Read the dissertation</a>
  </p>
</div>
