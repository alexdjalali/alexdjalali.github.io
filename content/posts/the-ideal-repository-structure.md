---
title: "The Ideal Repository Structure"
date: 2026-02-24
draft: false
description: "How strict layer boundaries prevent architectural decay — a deep-dive into interface-first, layered monorepo design with Go and Python examples."
images:
  - "images/og/the-ideal-repository-structure.png"
tags: ["architecture", "design-patterns", "go", "python"]
keywords: ["repository structure", "layered architecture", "clean architecture", "monorepo", "dependency injection", "interfaces", "go", "python"]
series: ["Software Architecture"]
---

Most repositories start with good intentions. The first hundred commits are organized, components are small and focused, and dependency flow is obvious. By commit five thousand, the codebase resembles a tangled graph — services depend on repositories that depend back on services, infrastructure concerns leak into business logic, circular imports require elaborate workarounds, and every change carries the risk of breaking something distant and unrelated. The structure has rotted because there was no mechanism to enforce boundaries.

Flat structures invite disorder. When everything lives in a single directory, or when layering exists only as a naming convention without enforcement, developers default to expedient choices rather than architecturally sound ones. A service needs database access, so it imports the repository directly. The repository needs to emit an event, so it imports the event bus. The event bus needs to log, so it imports the logger. Three months later, every component depends on every other component, and the dependency graph is cyclic. Refactoring becomes impossible because changes ripple unpredictably across the codebase.

Layers are the antidote. Physical directory boundaries enforce dependency direction — code can depend downward on lower layers, never upward or sideways. A strict layer model transforms implicit architectural conventions into explicit compilation failures. When a repository attempts to import from a service, the compiler rejects it. When a workflow tries to access a controller, the import path does not resolve. The structure becomes self-enforcing, and architectural decay stops being a gradual slide toward chaos.

## The Inspiration: Ardanlabs Service

The foundation for this structure came from Bill Kennedy's <a href="https://github.com/ardanlabs/service" target="_blank" rel="noopener noreferrer">ardanlabs/service</a> template. Kennedy's approach introduced a three-layer model for Go services that made dependency direction visible through directory structure:

```
service/
├── foundation/    # Utilities, logging, metrics, database drivers
├── business/      # Domain logic, business rules, data access
└── app/           # HTTP handlers, service composition, main()
```

The breakthrough insight was physical enforcement. The `foundation/` layer contains infrastructure primitives — loggers, metric emitters, database clients, cache adapters — with zero dependencies on anything above it. The `business/` layer implements domain logic and data models, depending only on `foundation/`. The `app/` layer wires everything together and exposes HTTP endpoints, depending on both `foundation/` and `business/` but owned by neither.

This structure prevents common pathologies. A database repository cannot import an HTTP handler because handler code lives in `app/`, and `business/` is forbidden from importing `app/`. A logger cannot depend on business logic because `foundation/` has no upward dependencies. Every import violation is a compile-time error, not a runtime surprise discovered during a production incident.

Kennedy's model established two principles that remain central: **dependency direction flows downward**, and **layers are directories, not comments**. The first principle ensures that lower layers are reusable and testable in isolation — the logger does not need a database to function, and the business logic does not need an HTTP server to execute. The second principle makes architecture visible and enforceable — static analysis tools can verify that no `business/` file imports from `app/`, and code review can catch violations before they merge.

The ardanlabs model was designed for small to medium Go services. As the pattern scaled to larger polyglot monorepos with dozens of microservices and shared libraries, the three-layer division became insufficient. Business logic stratified into distinct responsibilities — data access, domain services, sequential pipelines, multi-step workflows — each deserving a separate layer. Infrastructure expanded beyond foundation utilities to include decorator-wrapped external clients and repository abstractions. Interface contracts needed a dedicated location to prevent circular dependencies between layers.

The evolution produced a nine-layer model that preserves Kennedy's core insight — dependency flows downward through physical boundaries — while providing finer granularity for complex systems.

## The Layer Model

The ideal structure separates concerns into nine layers, each with a single responsibility and clear dependency constraints. Lower layers provide primitives and infrastructure. Middle layers implement domain logic. Upper layers coordinate and expose functionality. Dependency arrows point strictly downward.

{{<mermaid>}}
graph TD
    E[Entrypoints<br/>DI wiring, bootstrap] --> C[Controllers<br/>HTTP/gRPC handlers]
    C --> W[Workflows<br/>Multi-step orchestration]
    W --> P[Pipelines<br/>Sequential transformations]
    W --> S[Services<br/>Business logic]
    S --> R[Repositories<br/>Data access]
    S --> CL[Clients<br/>External systems]
    R --> F[Foundation<br/>Logger, metrics, cache]
    CL --> F
    R --> I[Core Interfaces<br/>Contracts]
    S --> I
    P --> I
    W --> I
    C --> I
    CL --> I
    F --> I

    style E fill:#e1f5ff
    style C fill:#fff3cd
    style W fill:#fff3cd
    style P fill:#d4edda
    style S fill:#d4edda
    style R fill:#d1ecf1
    style CL fill:#d1ecf1
    style F fill:#f8d7da
    style I fill:#e2e3e5
{{</mermaid>}}

### Core Interfaces — Contracts Before Implementations

Interface definitions live in a dedicated package, isolated from all implementations. Every layer imports from `core/interfaces/`, but `core/interfaces/` imports from nothing. This breaks circular dependencies and establishes a single source of truth for contracts.

In Go, this means a `pkg/go/core/interfaces/` directory containing only interface definitions and their documentation:

```go
// pkg/go/core/interfaces/repository.go
package interfaces

// Repository provides generic CRUD operations for any entity type T,
// filtered by parameters P, and identified by ID.
type Repository[T any, P any, ID comparable] interface {
    Create(ctx context.Context, entity T) (T, error)
    GetByID(ctx context.Context, id ID) (T, error)
    GetAll(ctx context.Context, params P) ([]T, error)
    Update(ctx context.Context, id ID, entity T) (T, error)
    DeleteByID(ctx context.Context, id ID) error
    Count(ctx context.Context, params P) (int64, error)
}
```

In Python, the equivalent is an `src/interfaces/` package with abstract base classes:

```python
# src/interfaces/repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar('T')  # Entity type
P = TypeVar('P')  # Query parameters
ID = TypeVar('ID')  # Identifier type

class Repository(ABC, Generic[T, P, ID]):
    """Generic repository interface for CRUD operations."""

    @abstractmethod
    def create(self, entity: T, *, ctx: Ctx = None) -> T:
        """Create a new entity."""
        ...

    @abstractmethod
    def get_by_id(self, entity_id: ID, *, ctx: Ctx = None) -> T | None:
        """Retrieve an entity by its unique identifier."""
        ...

    @abstractmethod
    def get_all(self, params: P, *, ctx: Ctx = None) -> list[T]:
        """Retrieve all entities matching the given parameters."""
        ...
```

The interface layer defines contracts for repositories, services, pipelines, workflows, controllers, clients, loggers, metrics emitters, cache adapters, and all other abstractions. Implementations live elsewhere. This separation enables **testability through mocking** — a service test can inject a fake repository that implements the `Repository[T, P, ID]` interface without requiring a real database — and **pluggability** — swapping PostgreSQL for MongoDB requires only a different repository implementation, with zero changes to service logic.

### Foundation — Cross-Cutting Infrastructure

The foundation layer provides utilities and adapters for logging, metrics collection, distributed tracing, caching, retry logic, circuit breaking, rate limiting, timeout enforcement, and other infrastructure concerns. Each component is independently versioned and publishable, depends only on core interfaces, and has zero dependencies on domain logic.

A logger in the foundation layer implements the `Logger` interface from core:

```go
// pkg/go/foundation/logger/logger.go
package logger

import "github.com/org/mothership/pkg/go/core/interfaces"

type Config struct {
    Kind        Kind   // stdlib, zap, zerolog
    Level       string
    JSON        bool
    Development bool
}

func New(kind Kind, opts ...Option) interfaces.Logger {
    cfg := DefaultConfig()
    for _, opt := range opts {
        opt(&cfg)
    }
    return newFromConfig(cfg)
}
```

The foundation logger has three implementations: `stdlib` (Go's `log/slog`), `zap` (Uber's structured logger), and `zerolog` (zero-allocation logger). Each implementation satisfies the `interfaces.Logger` contract. Application code depends on the interface, not the implementation, so switching from `zap` to `zerolog` requires changing only the DI wiring, not every log call site.

Foundation components are **independently versioned Go modules**. Each has its own `go.mod`, `VERSION` file, and `CHANGELOG.md`. The logger is publishable as `github.com/org/mothership/foundation/logger@v1.2.0`, the metrics emitter as `github.com/org/mothership/foundation/metrics@v1.1.0`. Teams can upgrade the logger without touching the circuit breaker, and external projects can depend on individual foundation modules without pulling the entire monorepo.

### Clients — External System Integration

The client layer wraps all interactions with external systems — databases, message brokers, object storage, third-party APIs. Clients implement interfaces from the core layer and are wrapped with decorator stacks for observability and resilience.

A MongoDB client in Python demonstrates the pattern:

```python
# src/clients/domain/mongodb/client.py
from motor.motor_asyncio import AsyncIOMotorClient
from src.interfaces.client import DatabaseClient

class MongoDBClient(DatabaseClient):
    """Async MongoDB client implementation."""

    def __init__(self, uri: str, database: str) -> None:
        self._client = AsyncIOMotorClient(uri)
        self._db = self._client[database]

    async def connect(self) -> None:
        await self._client.admin.command('ping')

    async def disconnect(self) -> None:
        self._client.close()

    def collection(self, name: str):
        return self._db[name]
```

The raw client provides minimal functionality. Production use requires retry logic for transient failures, circuit breaking to prevent cascading failures, structured logging for observability, and metrics for monitoring. Decorators compose these concerns:

```python
# src/clients/sdk/decorators.py
from src.clients.sdk.base import ClientDecorator

class RetryDecorator(ClientDecorator[T]):
    """Wraps a client with retry logic."""

    def __init__(self, inner: T, retrier: Retrier) -> None:
        super().__init__(inner)
        self._retrier = retrier

    async def execute(self, operation, *args, **kwargs):
        return await self._retrier.execute(
            lambda: getattr(self._inner, operation)(*args, **kwargs)
        )

class CircuitBreakerDecorator(ClientDecorator[T]):
    """Wraps a client with circuit breaking."""

    def __init__(self, inner: T, circuit_breaker: CircuitBreaker) -> None:
        super().__init__(inner)
        self._cb = circuit_breaker

    async def execute(self, operation, *args, **kwargs):
        return await self._cb.call(
            lambda: getattr(self._inner, operation)(*args, **kwargs)
        )
```

A factory function composes the stack:

```python
def create_mongo_client(settings: Settings) -> DatabaseClient:
    """Factory that wraps raw client with resilience and observability."""
    raw = MongoDBClient(settings.mongo_uri, settings.database)

    # Inner: circuit breaker → retry
    with_retry = RetryDecorator(raw, create_retrier())
    with_cb = CircuitBreakerDecorator(with_retry, create_circuit_breaker())

    # Outer: logging → metrics
    with_logging = LoggingDecorator(with_cb, logger)
    with_metrics = MetricsDecorator(with_logging, metrics)

    return with_metrics
```

The resulting client satisfies the `DatabaseClient` interface while transparently adding retry, circuit breaking, logging, and metrics. Service code calls `client.collection('users').find({})` without awareness of the decorator stack. For the full decorator pattern details, see my earlier post on <a href="/posts/decorator-pattern-observability-resilience/" target="_blank">the decorator pattern for observability and resilience</a>.

### Repositories — Data Access Abstraction

Repositories provide a domain-oriented interface to persistent storage. A repository accepts domain entities (not database-specific persistence models), translates them to the appropriate storage format, and abstracts query construction.

Go repositories are generic over entity type, query parameters, and identifier:

```go
// pkg/go/platform/repository/repository.go
package repository

type BaseRepository[T any, P any, ID comparable] struct {
    tableName string
    db        interfaces.DatabaseClient
}

func (r *BaseRepository[T, P, ID]) GetByID(
    ctx context.Context,
    id ID,
) (T, error) {
    var zero T
    query := fmt.Sprintf("SELECT * FROM %s WHERE id = $1", r.tableName)
    // Execute query, scan into entity, return
    // ...
}
```

Concrete repositories embed `BaseRepository` and add domain-specific queries:

```go
// apps/go/server/internal/repositories/user_repository.go
package repositories

type UserRepository struct {
    *repository.BaseRepository[User, UserParams, uuid.UUID]
}

func NewUserRepository(db interfaces.DatabaseClient) *UserRepository {
    return &UserRepository{
        BaseRepository: repository.NewBase[User, UserParams, uuid.UUID](
            "users",
            db,
        ),
    }
}

func (r *UserRepository) GetByEmail(
    ctx context.Context,
    email string,
) (User, error) {
    // Custom query beyond base CRUD
}
```

Python repositories follow the same pattern with ABCs:

```python
# src/repository/mongo/transcript.py
from src.interfaces.repository import Repository
from src.repository.mongo.models import TranscriptMongoModel

class TranscriptRepository(Repository[Transcript, TranscriptQueryParams, str]):
    """MongoDB repository for transcripts."""

    def __init__(self, client: DatabaseClient) -> None:
        self._collection = client.collection('transcripts')

    async def get_by_id(
        self,
        entity_id: str,
        *,
        ctx: Ctx = None
    ) -> Transcript | None:
        doc = await self._collection.find_one({'_id': entity_id})
        if not doc:
            return None
        return self._translator.to_domain(doc)
```

Repositories depend on clients (the layer below) and implement the `Repository[T, P, ID]` interface from core. They are **database-agnostic from the service layer's perspective** — swapping MongoDB for PostgreSQL requires only injecting a different repository implementation at the composition root, with zero service code changes.

### Services — Business Logic

Services implement domain logic and business rules. They are stateless, depend on repositories and clients through interfaces, and expose methods that operate on domain entities.

A service in Go:

```go
// pkg/go/services/corpus/service.go
package corpus

type Service struct {
    transcriptRepo interfaces.Repository[Transcript, TranscriptParams, string]
    speakerRepo    interfaces.Repository[Speaker, SpeakerParams, string]
    logger         interfaces.Logger
}

func (s *Service) GetTranscriptWithSpeakers(
    ctx context.Context,
    transcriptID string,
) (TranscriptWithSpeakers, error) {
    // Business logic: fetch transcript, fetch related speakers, assemble
    transcript, err := s.transcriptRepo.GetByID(ctx, transcriptID)
    if err != nil {
        return TranscriptWithSpeakers{}, fmt.Errorf("fetch transcript: %w", err)
    }

    speakerIDs := transcript.SpeakerIDs()
    speakers, err := s.speakerRepo.GetAll(ctx, SpeakerParams{IDs: speakerIDs})
    if err != nil {
        return TranscriptWithSpeakers{}, fmt.Errorf("fetch speakers: %w", err)
    }

    return s.assembleTranscriptWithSpeakers(transcript, speakers), nil
}
```

Services are wrapped with the same decorator stack as clients — logging, metrics, retry, circuit breaking. A `ServiceBuilder` composes decorators:

```python
# src/service/sdk/builder.py
from src.interfaces.builder import Builder

class ServiceBuilder(Builder[T, C], Generic[T, C]):
    """Builds services with decorator composition."""

    def build(self) -> T:
        instance = self._create_instance()

        # Apply fault tolerance decorators (innermost)
        if self._fault_tolerance:
            instance = RetryDecorator(instance, self._retrier)
            instance = CircuitBreakerDecorator(instance, self._cb)

        # Apply observability decorators (outermost)
        if self._observability:
            instance = LoggingDecorator(instance, self._logger)
            instance = MetricsDecorator(instance, self._metrics)

        return instance
```

Services depend on repositories and clients (layers below) and implement service interfaces from core. They do not depend on workflows, controllers, or entrypoints (layers above).

### Pipelines — Sequential Transformations

Pipelines model sequential data transformations where each stage consumes the output of the prior stage. A pipeline implements `Pipeline[In, Out]`:

```go
// pkg/go/core/interfaces/pipeline.go
package interfaces

type Pipeline[In any, Out any] interface {
    Execute(ctx context.Context, input In) (Out, error)
}
```

An NLP pipeline in Python demonstrates composition:

```python
# src/pipeline/domain/nlp/spacy_pipeline.py
from src.interfaces.pipeline import Pipeline

class SpacyPipeline(Pipeline[str, ProcessedDocument]):
    """NLP processing pipeline using spaCy."""

    def __init__(self, model: str = "en_core_web_sm") -> None:
        self._nlp = spacy.load(model)

    def execute(self, input: str, *, ctx: Ctx = None) -> ProcessedDocument:
        """Process text through: tokenization → POS → NER → dep parse."""
        doc = self._nlp(input)

        return ProcessedDocument(
            text=input,
            tokens=[token.text for token in doc],
            pos_tags=[token.pos_ for token in doc],
            entities=[(ent.text, ent.label_) for ent in doc.ents],
            dependencies=[(token.text, token.dep_, token.head.text) for token in doc],
        )
```

Pipelines are stateless transformations. They depend on services or clients for data fetching but do not coordinate multi-step workflows. That responsibility belongs to the next layer.

### Workflows — Multi-Step Orchestration

Workflows coordinate multiple operations — fetch data, validate, transform, publish events, handle errors. A workflow implements `Workflow[In, Out]`:

```go
// pkg/go/core/interfaces/workflow.go
package interfaces

type Workflow[In any, Out any] interface {
    Execute(ctx context.Context, input In) (Out, error)
}
```

A search workflow demonstrates cache-aside pattern:

```python
# src/workflow/domain/search/workflow.py
from src.interfaces.workflow import AsyncWorkflow

class SearchWorkflow(AsyncWorkflow[SearchRequest, SearchResponse]):
    """Implements cache-aside search: check cache, else pipeline."""

    def __init__(
        self,
        cache: Cache,
        pipeline: AsyncPipeline[SearchRequest, SearchResponse],
    ) -> None:
        self._cache = cache
        self._pipeline = pipeline

    async def execute(
        self,
        input: SearchRequest,
        *,
        ctx: Ctx = None
    ) -> SearchResponse:
        cache_key = self._build_cache_key(input)

        # Cache hit?
        cached = await self._cache.get(cache_key)
        if cached:
            return SearchResponse.from_json(cached)

        # Cache miss — execute pipeline
        result = await self._pipeline.execute(input, ctx=ctx)

        # Cache result
        await self._cache.set(cache_key, result.to_json(), ttl=300)

        return result
```

Workflows depend on services, pipelines, repositories, and clients. They do not depend on controllers or entrypoints.

### Controllers — HTTP/gRPC Handlers

Controllers are thin adapters between transport protocols (HTTP, gRPC, GraphQL) and workflows. They deserialize requests into DTOs, invoke workflows, and serialize responses.

A FastAPI controller in Python:

```python
# src/controller/domain/search/controller.py
from fastapi import APIRouter
from src.interfaces.workflow import AsyncWorkflow

class SearchController:
    """HTTP controller for search endpoints."""

    def __init__(
        self,
        workflow: AsyncWorkflow[SearchRequest, SearchResponse],
    ) -> None:
        self._workflow = workflow
        self.router = APIRouter()
        self.router.add_api_route("/search", self.search, methods=["GET"])

    async def search(
        self,
        query: str,
        filters: str = None,
        limit: int = 10,
    ) -> SearchResponse:
        """GET /search endpoint."""
        request = SearchRequest(query=query, filters=filters, limit=limit)
        return await self._workflow.execute(request)
```

Controllers depend on workflows (the layer below). They do not contain business logic. Validation, transformation, and orchestration belong in lower layers.

### Entrypoints — DI Wiring and Bootstrap

Entrypoints are composition roots. They load configuration, instantiate dependencies, wire the DI container, and start the server. Each microservice has an entrypoint:

```python
# entrypoints/server/search/container.py
from dependency_injector import containers, providers
from src.foundation.config import CoreContainer

class SearchContainer(containers.DeclarativeContainer):
    """DI container for search server."""

    # Inherit core infrastructure
    core = providers.DependenciesContainer()

    # Repository
    es_repo = providers.Singleton(
        AsyncElasticTranscriptRepository,
        client=core.es_client,
    )

    # Pipeline
    search_pipeline = providers.Singleton(
        SearchPipeline,
        repository=es_repo,
    )

    # Workflow
    search_workflow = providers.Singleton(
        SearchWorkflow,
        cache=core.redis_client,
        pipeline=search_pipeline,
    )

    # Controller
    search_controller = providers.Singleton(
        SearchController,
        workflow=search_workflow,
    )
```

Entrypoints depend on every other layer. No other layer depends on entrypoints. This is the **dependency inversion principle** in physical form — high-level policy (entrypoints) depends on low-level details (services, repositories), but low-level details do not depend back.

## The Dependency Rule

Dependency direction is the single most important structural constraint. Code in layer N can depend on layers N-1, N-2, ... all the way down to core interfaces. Code in layer N **cannot** depend on layers N+1, N+2, or any layer above.

{{<mermaid>}}
graph TD
    subgraph "Allowed Dependencies (Downward)"
        E1[Entrypoint] -->|✓| C1[Controller]
        C1 -->|✓| W1[Workflow]
        W1 -->|✓| S1[Service]
        S1 -->|✓| R1[Repository]
        R1 -->|✓| F1[Foundation]
    end

    subgraph "Forbidden Dependencies (Upward/Sideways)"
        S2[Service] -.->|✗| W2[Workflow]
        R2[Repository] -.->|✗| S2[Service]
        F2[Foundation] -.->|✗| R2[Repository]
        W3[Workflow] -.->|✗| C2[Controller]
    end

    style E1 fill:#e1f5ff
    style C1 fill:#fff3cd
    style C2 fill:#fff3cd
    style W1 fill:#d4edda
    style W2 fill:#d4edda
    style W3 fill:#d4edda
    style S1 fill:#d1ecf1
    style S2 fill:#d1ecf1
    style R1 fill:#f8d7da
    style R2 fill:#f8d7da
    style F1 fill:#e2e3e5
    style F2 fill:#e2e3e5
{{</mermaid>}}

### Enforcement in Go

Go enforces the dependency rule through import paths. A service in `pkg/go/services/corpus/` can import from `pkg/go/repos/` and `pkg/go/foundation/`, but attempting to import `pkg/go/workflow/` or `pkg/go/controllers/` produces a compilation error if those packages do not exist at lower layers.

Compile-time checks make violations impossible. A repository that tries to emit domain events by importing the event bus triggers:

```
pkg/go/repos/postgres/user_repository.go:5:2:
    cannot import "github.com/org/mothership/pkg/go/workflow/events"
    (import cycle or dependency rule violation)
```

Static analysis tools like `go mod graph | grep` can detect cross-layer violations:

```bash
go mod graph | grep "repos.*->.*services"
# Output: (empty if no violations)
```

### Enforcement in Python

Python does not prevent circular imports at compile time. Import linting tools like `import-linter` enforce the dependency rule:

```toml
# pyproject.toml
[tool.importlinter]
root_package = "src"

[[tool.importlinter.contracts]]
name = "Layered architecture"
type = "layers"
layers = [
    "entrypoints",
    "controller",
    "workflow",
    "pipeline",
    "service",
    "repository | clients",
    "foundation",
    "interfaces",
]
```

Running `lint-imports` fails the build if a service imports from workflow:

```
Layer violation: src.service.corpus imported src.workflow.search
  Layers: service -> workflow (forbidden upward dependency)
```

Directory structure reinforces the rule. A developer attempting to import `from workflow.search import SearchWorkflow` into a service file sees the import path and realizes the violation before running linters.

## Interface-First Design

Defining all interfaces in a dedicated package prevents circular dependencies and establishes a contract-first development model. Implementation layers import interface definitions, but the interface package imports nothing.

### Go: Compile-Time Verification

Go repositories provide interface implementations:

```go
// pkg/go/repos/postgres/user_repository.go
package postgres

import "github.com/org/mothership/pkg/go/core/interfaces"

type UserRepository struct {
    db interfaces.DatabaseClient
}

// Compile-time assertion: UserRepository implements Repository[User, UserParams, uuid.UUID]
var _ interfaces.Repository[User, UserParams, uuid.UUID] = (*UserRepository)(nil)

func (r *UserRepository) GetByID(
    ctx context.Context,
    id uuid.UUID,
) (User, error) {
    // Implementation
}
```

The assertion `var _ interfaces.Repository[...] = (*UserRepository)(nil)` is checked at compile time. If `UserRepository` fails to implement any method from `Repository[T, P, ID]`, compilation fails. Interfaces are self-documenting contracts with compiler enforcement.

### Python: Runtime Protocol Checks

Python repositories use ABCs for interface definitions:

```python
# src/interfaces/repository.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, runtime_checkable, Protocol

T = TypeVar('T')
P = TypeVar('P')
ID = TypeVar('ID')

@runtime_checkable
class Repository(Protocol, Generic[T, P, ID]):
    """Repository protocol for CRUD operations."""

    def get_by_id(self, entity_id: ID, *, ctx: Ctx = None) -> T | None:
        ...
```

Concrete implementations inherit and override:

```python
# src/repository/mongo/transcript.py
from src.interfaces.repository import Repository

class TranscriptRepository(Repository[Transcript, TranscriptQueryParams, str]):
    """MongoDB transcript repository."""

    def get_by_id(
        self,
        entity_id: str,
        *,
        ctx: Ctx = None
    ) -> Transcript | None:
        # Implementation
```

Type checkers like Mypy verify protocol adherence at static analysis time. The `@runtime_checkable` decorator enables `isinstance()` checks:

```python
repo = TranscriptRepository(client)
assert isinstance(repo, Repository)  # True
```

### Why Dedicated Interface Packages Matter

Without a separate interface package, repositories and services create circular dependencies. A service needs `RepositoryInterface`, so it imports from the repository package. The repository needs `ServiceInterface` for callbacks, so it imports from the service package. The import cycle breaks the build.

A dedicated `core/interfaces/` package (Go) or `interfaces/` package (Python) solves this:

- Services import `interfaces.Repository`
- Repositories import `interfaces.Repository` and implement it
- No service-to-repository or repository-to-service import required

Interfaces become the shared contract. Changes to repository implementations do not require service code changes if the interface remains stable.

## The Monorepo Layout

The layer model maps to directory structure. Go and Python monorepos follow parallel organization with language-appropriate conventions.

### Go: mothership

```
mothership/
├── pkg/
│   └── go/
│       ├── core/
│       │   ├── interfaces/      # 60+ interface definitions
│       │   ├── types/           # Option, Either, Result, Page, ID
│       │   └── errors/          # Core error types
│       │
│       ├── foundation/          # ~20 independent modules
│       │   ├── logger/          # stdlib, zap, zerolog
│       │   │   ├── go.mod       # Independent versioning
│       │   │   ├── VERSION
│       │   │   ├── base/
│       │   │   ├── noop/
│       │   │   ├── stdlib/
│       │   │   ├── zap/
│       │   │   └── zerolog/
│       │   ├── metrics/         # Prometheus, OTEL
│       │   ├── cache/           # Redis, Ristretto
│       │   ├── circuitbreaker/
│       │   ├── retrier/
│       │   └── ...
│       │
│       ├── repos/               # Data access implementations
│       │   ├── databases/
│       │   │   ├── relational/  # PostgreSQL, SQLite
│       │   │   ├── time-series/ # InfluxDB, TimescaleDB
│       │   │   └── document/    # MongoDB
│       │   └── caches/          # Redis, Ristretto
│       │
│       ├── services/            # Domain services
│       │   ├── git/
│       │   └── version/
│       │
│       ├── platform/            # Request processing layers
│       │   ├── pipeline/
│       │   ├── decorators/
│       │   └── workflow/
│       │
│       └── config/              # Config providers
│
└── apps/
    └── go/
        ├── server/              # Main API server
        │   ├── cmd/main.go      # Bootstrap
        │   ├── internal/
        │   │   ├── handlers/
        │   │   ├── services/
        │   │   ├── repositories/
        │   │   └── wire/        # Google Wire DI
        │   └── configs/
        ├── worker/              # Background worker
        └── job/                 # Batch job
```

### Python: hpc

```
hpc/
├── src/
│   ├── interfaces/          # ABCs for all contracts
│   │   ├── repository.py
│   │   ├── service.py
│   │   ├── pipeline.py
│   │   ├── workflow.py
│   │   └── ...
│   │
│   ├── foundation/          # Infrastructure
│   │   ├── logger/
│   │   ├── metrics/
│   │   ├── cache/
│   │   ├── resilience/      # Retry, circuit breaker
│   │   └── ...
│   │
│   ├── clients/             # External systems
│   │   ├── sdk/             # Decorator framework
│   │   │   ├── base.py
│   │   │   ├── retry.py
│   │   │   ├── circuit_breaker.py
│   │   │   └── logging.py
│   │   └── domain/          # Concrete clients
│   │       ├── mongodb/
│   │       ├── redis/
│   │       ├── elasticsearch/
│   │       └── kafka/
│   │
│   ├── repository/          # Data access
│   │   ├── sdk/             # Base repository
│   │   └── mongo/           # MongoDB repositories
│   │
│   ├── service/             # Business logic
│   │   ├── sdk/
│   │   └── domain/
│   │
│   ├── pipeline/            # Sequential transformations
│   │   ├── sdk/
│   │   └── domain/
│   │
│   ├── workflow/            # Multi-step orchestration
│   │   ├── sdk/
│   │   └── domain/
│   │
│   └── controller/          # HTTP handlers
│       ├── sdk/
│       └── domain/
│
└── entrypoints/             # Service wiring
    ├── server/
    │   ├── search/          # Search API
    │   │   ├── container.py # DI wiring
    │   │   ├── app.py       # FastAPI factory
    │   │   └── routes/
    │   ├── admin/           # Admin API
    │   └── auth/            # Auth API
    ├── stream/              # Kafka consumers
    │   ├── processor/
    │   └── indexer/
    └── cli/                 # Typer CLI
```

### Parallel Structure

Both repositories follow the same conceptual layers with language-appropriate naming:

| Layer | Go | Python |
|-------|----|----- |
| Interfaces | `pkg/go/core/interfaces/` | `src/interfaces/` |
| Foundation | `pkg/go/foundation/` | `src/foundation/` |
| Clients | `pkg/go/clients/` | `src/clients/` |
| Repositories | `pkg/go/repos/` | `src/repository/` |
| Services | `pkg/go/services/` | `src/service/` |
| Pipelines | `pkg/go/platform/pipeline/` | `src/pipeline/` |
| Workflows | `pkg/go/platform/workflow/` | `src/workflow/` |
| Controllers | (in app) | `src/controller/` |
| Entrypoints | `apps/go/` | `entrypoints/` |

The directory structure makes dependency flow visible. Reading from top to bottom shows increasing abstraction. Reading imports shows dependency direction.

## Decorator Composition Across Layers

Each layer boundary is wrapped with decorators for logging, metrics, tracing, retry, and circuit breaking. A service calling a repository triggers the decorator stack at both boundaries:

```
Controller → [Logging → Metrics] → Workflow
                 ↓
Workflow → [Logging → Metrics] → Service
                 ↓
Service → [Logging → Metrics → Retry → CB] → Repository
                 ↓
Repository → [Logging → Metrics → Retry → CB] → Client
```

The decorator pattern separates cross-cutting concerns from business logic. For a detailed explanation of how decorators stack, see <a href="/posts/decorator-pattern-observability-resilience/" target="_blank">the decorator pattern for observability and resilience</a>.

Builders compose the decorator stack at each layer:

```python
service = (
    CorpusServiceBuilder(config)
    .with_repository(repo)
    .with_observability(enabled=True)
    .with_fault_tolerance(enabled=True)
    .build()
)
# Returns: LoggingDecorator(MetricsDecorator(RetryDecorator(CircuitBreakerDecorator(raw_service))))
```

Decorators apply uniformly across all services, repositories, and clients. Operational changes — adjusting retry backoff, switching metric backends, changing log formats — require modifications to decorator implementations, not to every service call site.

## What the Structure Prevents

Layers eliminate pathologies that plague unstructured codebases.

### Circular Imports

Flat structures produce import cycles. A service imports a repository. The repository emits domain events, so it imports the event publisher. The event publisher logs, so it imports the logger. The logger needs configuration, so it imports the config loader. The config loader validates schemas, so it imports domain models from the service. The circle closes, and the build breaks.

Layers break cycles through **unidirectional dependency flow**. Services depend on repositories, but repositories do not depend on services. If a repository needs to publish an event, it accepts an `EventPublisher` interface via dependency injection, and the entrypoint wires a concrete publisher from the foundation layer. The repository imports `interfaces.EventPublisher`, not a service package.

### God Services

Without clear boundaries, services accumulate responsibilities. A `UserService` starts with authentication. Then it handles email notifications. Then it manages file uploads. Then it orchestrates payment processing. The service becomes a thousand-line monolith that depends on every repository and client in the system.

Layers enforce the **single responsibility principle** through separation. Authentication belongs in an `AuthService`. Notifications belong in a `NotificationService`. File uploads belong in a `StorageService`. Each service depends on a narrow subset of repositories and clients. Workflows coordinate multi-service operations.

### Infrastructure Leaking into Business Logic

Services that directly import database drivers, HTTP clients, or message brokers tie business logic to infrastructure choices. Switching from PostgreSQL to DynamoDB requires changing every service method that constructs SQL queries. Replacing Kafka with RabbitMQ requires modifying every event publisher call site.

Repository and client abstractions isolate infrastructure. Services depend on `interfaces.Repository[User, UserParams, uuid.UUID]`, not `*sql.DB`. Swapping persistence backends requires only a different repository implementation at the DI layer. Service code remains unchanged.

### Untestable Code

Services that instantiate dependencies internally are hard to test. A service that creates its own database connection requires a real database for tests. A service that calls external APIs directly requires network access or elaborate mocking.

Dependency injection through interfaces makes testing trivial. A service test injects a fake repository:

```go
func TestService_GetUser(t *testing.T) {
    fakeRepo := &FakeUserRepository{
        Users: map[uuid.UUID]User{
            testUserID: {ID: testUserID, Email: "test@example.com"},
        },
    }
    service := NewUserService(fakeRepo, fakeLogger)

    user, err := service.GetUser(context.Background(), testUserID)
    require.NoError(t, err)
    assert.Equal(t, "test@example.com", user.Email)
}
```

No database, no network, no external dependencies. Tests run in milliseconds.

### Deployment Coupling

Microservices that share code through direct imports couple deployment. Service A imports a utility function from Service B's internal package. Deploying Service B requires coordinating with Service A to ensure compatibility. The services are no longer independently deployable.

Layers eliminate coupling through **shared libraries in foundation**. Utilities live in `pkg/go/foundation/`, not in application packages. Services import foundation modules, not each other. Foundation modules are independently versioned, and services declare version constraints in their `go.mod` files. Upgrading a foundation module in Service A does not affect Service B until Service B updates its own dependency declaration.

## Summary

The ideal repository structure is not about naming conventions or directory aesthetics. It is about **enforcing dependency direction through physical boundaries**. Layers prevent circular dependencies by making upward imports impossible. Layers prevent God components by separating responsibilities. Layers prevent infrastructure leakage by isolating abstractions from implementations. Layers prevent deployment coupling by limiting shared code to independently versioned foundation modules.

Layers are directories. Interfaces are files in a dedicated package. Dependencies flow downward. Violations fail at compile time or in CI. The structure becomes self-enforcing, and architectural decay stops being inevitable.

The nine-layer model scales from small services to large polyglot monorepos. The Go structure in mothership and the Python structure in hpc demonstrate the same principles with language-appropriate implementations. Both enforce the dependency rule. Both define interfaces before implementations. Both use decorator composition for cross-cutting concerns. Both rely on physical directory structure to make architecture visible and violations obvious.

Structure is not overhead. Structure is the mechanism that prevents complexity from compounding into chaos.
