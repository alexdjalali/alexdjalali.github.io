---
title: "The Ideal Repository Structure"
date: 2026-02-24
draft: false
description: "That strict layer boundaries, enforced by the directory structure itself, keep a codebase from decaying, with a detailed tour of interface-first, layered monorepo design in Go and Python."
images:
  - "images/og/the-ideal-repository-structure.png"
tags: ["architecture", "design-patterns", "go", "python"]
keywords: ["repository structure", "layered architecture", "clean architecture", "monorepo", "dependency injection", "interfaces", "go", "python"]
series: ["Software Architecture"]
---

Most repositories start out with the best of intentions. The first hundred commits are tidy, the components are small and focused, and it's obvious which way the dependencies run. By commit five thousand, the codebase looks more like a tangled graph. Services depend on repositories that depend back on services, infrastructure concerns leak into business logic, circular imports need elaborate workarounds, and every change risks breaking something distant and apparently unrelated. The structure rotted, and it rotted because nothing enforced its boundaries.

Flat structures invite disorder. When everything lives in one directory, or when layering exists only as a naming convention that nothing enforces, developers reach for the expedient choice over the architecturally sound one. A service needs the database, so it imports the repository directly. The repository needs to emit an event, so it imports the event bus. The event bus needs to log, so it imports the logger. Three months later every component depends on every other, the dependency graph has cycles in it, and refactoring becomes all but impossible, because any change ripples unpredictably across the codebase.

Layers are the remedy. If directory boundaries fix the direction of dependencies, so that code can depend on the layers below it and never on those above or beside it, then a strict layer model turns implicit architectural conventions into explicit build failures. When a repository tries to import from a service, the compiler rejects it; when a workflow reaches for a controller, the import path doesn't resolve. The structure enforces itself, and architectural decay stops being a slow, inevitable slide.

## The Inspiration: Ardanlabs Service

I didn't invent any of this. The structure grew out of Bill Kennedy's <a href="https://github.com/ardanlabs/service" target="_blank" rel="noopener noreferrer">ardanlabs/service</a> template, which introduced a three-layer model for Go services that made the direction of dependencies visible in the directory structure itself:

```
service/
├── foundation/    # Utilities, logging, metrics, database drivers
├── business/      # Domain logic, business rules, data access
└── app/           # HTTP handlers, service composition, main()
```

The crucial insight was physical enforcement. The `foundation/` layer holds infrastructure primitives (loggers, metric emitters, database clients, cache adapters) and depends on nothing above it. The `business/` layer implements the domain logic and data models and depends only on `foundation/`. The `app/` layer wires everything together and exposes the HTTP endpoints, depending on both of the others while being owned by neither.

That alone rules out a good many pathologies. A database repository can't import an HTTP handler, because handlers live in `app/` and `business/` may not import `app/`. A logger can't depend on business logic, because `foundation/` has no upward dependencies. Every such violation becomes a compile-time error rather than a surprise discovered in the middle of a production incident.

Kennedy's model established two principles I still hold to: dependencies flow downward, and layers are directories, not comments. The first keeps the lower layers reusable and testable on their own (the logger doesn't need a database to work, and the business logic doesn't need an HTTP server to run). The second makes the architecture visible and enforceable, since a static analysis tool can verify that no file in `business/` imports from `app/`, and a reviewer can catch a violation before it merges.

The ardanlabs model was designed for small and medium Go services. As I stretched it over larger polyglot monorepos with dozens of microservices and shared libraries, three layers stopped being enough. Business logic split into distinct responsibilities (data access, domain services, sequential pipelines, multi-step workflows), each deserving a layer of its own. Infrastructure grew beyond foundation utilities to include external clients wrapped in decorators, and repository abstractions. And the interface contracts needed a home of their own, to keep the layers from depending on each other in circles.

The result is a nine-layer model that keeps Kennedy's central insight (dependencies flow downward across physical boundaries) while offering finer distinctions for complex systems.

## The Layer Model

The structure separates concerns into nine layers, each with a single responsibility and clear constraints on what it may depend on. The lower layers provide primitives and infrastructure, the middle layers implement the domain logic, and the upper layers coordinate it and expose it to the world. Every dependency arrow points down.

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

### Core Interfaces: Contracts Before Implementations

Interface definitions live in a package of their own, isolated from every implementation. Every layer imports from `core/interfaces/`, and `core/interfaces/` imports from nothing at all, which breaks circular dependencies and gives the contracts a single source of truth.

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

The interface layer defines the contracts for repositories, services, pipelines, workflows, controllers, clients, loggers, metrics emitters, cache adapters and every other abstraction, while the implementations live elsewhere. That separation buys two things. It makes code testable, because a service test can inject a fake repository that implements `Repository[T, P, ID]` without needing a real database. And it makes implementations pluggable, because swapping PostgreSQL for MongoDB takes only a different repository implementation, with no change at all to the service logic.

### Foundation: Cross-Cutting Infrastructure

The foundation layer provides utilities and adapters for logging, metrics, distributed tracing, caching, retries, circuit breaking, rate limiting, timeouts and the like. Each component is versioned and publishable on its own, depends only on the core interfaces, and knows nothing whatsoever about the domain.

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

The foundation logger has three implementations, `stdlib` (Go's `log/slog`), `zap` (Uber's structured logger) and `zerolog` (a zero-allocation logger), and each satisfies the `interfaces.Logger` contract. Application code depends on the interface rather than any implementation, so moving from `zap` to `zerolog` means changing the dependency wiring and nothing else, certainly not every call site that logs.

Each foundation component is also its own Go module, with its own `go.mod`, `VERSION` file and `CHANGELOG.md`. The logger can be published as `github.com/org/mothership/foundation/logger@v1.2.0` and the metrics emitter as `github.com/org/mothership/foundation/metrics@v1.1.0`. A team can upgrade the logger without touching the circuit breaker, and an outside project can depend on a single foundation module without pulling in the whole monorepo.

### Clients: External System Integration

The client layer wraps every interaction with an external system, whether a database, a message broker, object storage or a third-party API. Clients implement interfaces from the core layer and are wrapped in stacks of decorators for observability and resilience.

A MongoDB client in Python shows the pattern:

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

The raw client does very little on its own. In production it needs retries for transient failures, a circuit breaker to keep failures from cascading, structured logging and metrics, and decorators supply each of these:

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

A factory function assembles the stack:

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

The resulting client satisfies the `DatabaseClient` interface while quietly adding retries, circuit breaking, logging and metrics. Service code calls `client.collection('users').find({})` with no idea that the stack is there. (I go into the pattern in more detail in <a href="/posts/decorator-pattern-observability-resilience/" target="_blank">the decorator pattern for observability and resilience</a>.)

### Repositories: Data Access Abstraction

Repositories give persistent storage an interface shaped by the domain. A repository accepts domain entities (not the database's own persistence models), translates them into whatever the storage needs, and hides how queries get built.

In Go, repositories are generic over the entity type, the query parameters and the identifier:

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

Concrete repositories embed `BaseRepository` and add queries specific to their domain:

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

Python repositories follow the same pattern, using abstract base classes:

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

Repositories depend on clients (the layer below) and implement the `Repository[T, P, ID]` interface from the core. From the service layer's point of view, they don't care which database sits underneath; swapping MongoDB for PostgreSQL means injecting a different repository at the composition root and changing no service code at all.

### Services: Business Logic

Services implement the domain logic and business rules. They are stateless, depend on repositories and clients only through interfaces, and expose methods that operate on domain entities.

Here is a service in Go:

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

Services get the same decorator stack as clients (logging, metrics, retries, circuit breaking), assembled by a `ServiceBuilder`:

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

Services depend on repositories and clients below them and implement service interfaces from the core. They never depend on workflows, controllers or entrypoints above them.

### Pipelines: Sequential Transformations

Pipelines model sequences of transformations in which each stage consumes the output of the one before it. A pipeline implements `Pipeline[In, Out]`:

```go
// pkg/go/core/interfaces/pipeline.go
package interfaces

type Pipeline[In any, Out any] interface {
    Execute(ctx context.Context, input In) (Out, error)
}
```

An NLP pipeline in Python shows how stages compose (and, being a linguist, I couldn't resist):

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

Pipelines are stateless transformations. They may call services or clients to fetch data, but they don't coordinate multi-step processes; that job belongs to the next layer up.

### Workflows: Multi-Step Orchestration

Workflows coordinate several operations at once: fetching data, validating it, transforming it, publishing events and handling errors. A workflow implements `Workflow[In, Out]`:

```go
// pkg/go/core/interfaces/workflow.go
package interfaces

type Workflow[In any, Out any] interface {
    Execute(ctx context.Context, input In) (Out, error)
}
```

A search workflow shows the cache-aside pattern:

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

Workflows depend on services, pipelines, repositories and clients, and never on controllers or entrypoints.

### Controllers: HTTP/gRPC Handlers

Controllers are thin adapters between a transport protocol (HTTP, gRPC, GraphQL) and the workflows. They deserialize requests into DTOs, call a workflow, and serialize the response.

Here is a FastAPI controller in Python:

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

Controllers depend on workflows, the layer below, and contain no business logic of their own. Validation, transformation and orchestration all belong further down.

### Entrypoints: DI Wiring and Bootstrap

Entrypoints are composition roots. They load configuration, construct dependencies, wire them together and start the server, and every microservice has one:

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

Entrypoints depend on every other layer, and no layer depends on them. It's the dependency inversion principle in physical form: the composition root knows about every detail (services, repositories and the rest), and none of those details know about it.

## The Dependency Rule

If I had to keep only one structural constraint, it would be the direction of dependencies. Code in layer N may depend on layers N-1, N-2 and so on, all the way down to the core interfaces. It may *not* depend on layer N+1, or on anything above that.

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

Go enforces the rule through import paths. A service in `pkg/go/services/corpus/` can import from `pkg/go/repos/` and `pkg/go/foundation/`, but an attempt to import `pkg/go/workflow/` or `pkg/go/controllers/` fails to compile if those packages don't exist at a lower layer.

So compile-time checks make violations impossible. A repository that tries to emit domain events by importing the event bus gets this:

```
pkg/go/repos/postgres/user_repository.go:5:2:
    cannot import "github.com/org/mothership/pkg/go/workflow/events"
    (import cycle or dependency rule violation)
```

And a simple `go mod graph | grep` can find violations across layers:

```bash
go mod graph | grep "repos.*->.*services"
# Output: (empty if no violations)
```

### Enforcement in Python

Python, of course, has no compile step to stop a circular import. An import linter such as `import-linter` enforces the rule instead:

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

Running `lint-imports` fails the build whenever a service imports from a workflow:

```
Layer violation: src.service.corpus imported src.workflow.search
  Layers: service -> workflow (forbidden upward dependency)
```

The directory structure reinforces the rule as well. A developer about to write `from workflow.search import SearchWorkflow` in a service file can see from the path alone that something is wrong, before any linter runs.

## Interface-First Design

Defining every interface in a package of its own prevents circular dependencies and puts the contract first. Implementation layers import the interface definitions, and the interface package imports nothing.

### Go: Compile-Time Verification

Go repositories implement the interfaces like so:

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

The assertion `var _ interfaces.Repository[...] = (*UserRepository)(nil)` is checked at compile time, so if `UserRepository` fails to implement any method of `Repository[T, P, ID]`, the build fails. The interfaces document themselves, and the compiler enforces them.

### Python: Runtime Protocol Checks

Python repositories define their interfaces as abstract base classes:

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

Concrete implementations inherit from them and override the methods:

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

A type checker such as Mypy verifies that the protocol is honored before anything runs, and the `@runtime_checkable` decorator allows `isinstance()` checks at runtime:

```python
repo = TranscriptRepository(client)
assert isinstance(repo, Repository)  # True
```

### Why Dedicated Interface Packages Matter

Without a separate interface package, repositories and services end up depending on each other. A service needs `RepositoryInterface`, so it imports from the repository package; the repository needs `ServiceInterface` for a callback, so it imports from the service package; and the resulting cycle breaks the build.

A dedicated `core/interfaces/` package (in Go) or `interfaces/` package (in Python) resolves the cycle:

- Services import `interfaces.Repository`
- Repositories import `interfaces.Repository` and implement it
- No service-to-repository or repository-to-service import required

The interfaces become the shared contract, and so long as an interface stays stable, changing a repository's implementation requires no change to any service.

## The Monorepo Layout

The layer model maps directly onto the directory structure, and the Go and Python monorepos are organized in parallel, each with the conventions of its language.

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

Both repositories have the same conceptual layers, named as each language prefers:

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

The directory structure makes the flow of dependencies visible. Read from top to bottom and abstraction increases; read the imports and you can see which way the dependencies run.

## Decorator Composition Across Layers

Each boundary between layers is wrapped in decorators for logging, metrics, tracing, retries and circuit breaking, so a service calling a repository passes through a decorator stack on both sides:

```
Controller → [Logging → Metrics] → Workflow
                 ↓
Workflow → [Logging → Metrics] → Service
                 ↓
Service → [Logging → Metrics → Retry → CB] → Repository
                 ↓
Repository → [Logging → Metrics → Retry → CB] → Client
```

The decorators keep cross-cutting concerns out of the business logic. (Again, <a href="/posts/decorator-pattern-observability-resilience/" target="_blank">the decorator pattern for observability and resilience</a> explains in more detail how they stack.)

Builders assemble the stack at each layer:

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

The decorators apply uniformly to every service, repository and client, so operational changes (a different backoff, a new metrics backend, another log format) mean changing a decorator rather than every place a service gets called.

## What the Structure Prevents

Layers rule out a number of pathologies that plague unstructured codebases.

### Circular Imports

Flat structures produce import cycles. A service imports a repository. The repository emits domain events, so it imports the event publisher. The publisher logs, so it imports the logger. The logger needs configuration, so it imports the config loader. The config loader validates schemas, so it imports domain models from the service. The circle closes, and the build breaks.

Layers break the cycle by making dependencies run in one direction only. Services depend on repositories, but repositories never depend on services. If a repository needs to publish an event, it accepts an `EventPublisher` interface through dependency injection, and the entrypoint wires in a concrete publisher from the foundation layer. The repository imports `interfaces.EventPublisher`, never a service package.

### God Services

Without clear boundaries, services accumulate responsibilities. A `UserService` starts out handling authentication, then picks up email notifications, then file uploads, then payment processing, until it's a thousand-line monolith that depends on every repository and client in the system.

Layers enforce the single-responsibility principle by keeping these apart. Authentication belongs in an `AuthService`, notifications in a `NotificationService`, and file uploads in a `StorageService`. Each service depends on a narrow subset of repositories and clients, and workflows coordinate anything that spans several services.

### Infrastructure Leaking into Business Logic

Services that import database drivers, HTTP clients or message brokers directly tie the business logic to particular infrastructure. Moving from PostgreSQL to DynamoDB then means changing every service method that builds a SQL query, and replacing Kafka with RabbitMQ means touching every place that publishes an event.

Repository and client abstractions keep the infrastructure at arm's length. Services depend on `interfaces.Repository[User, UserParams, uuid.UUID]`, not on `*sql.DB`, so swapping the persistence backend takes a different repository implementation at the composition root and leaves the services untouched.

### Untestable Code

Services that construct their own dependencies are hard to test. One that opens its own database connection needs a real database to be tested at all, and one that calls external APIs directly needs network access or some elaborate mocking.

Injecting dependencies through interfaces makes testing nearly trivial. A service test simply injects a fake repository:

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

There's no database, no network and no external dependency of any kind, and the tests run in milliseconds.

### Deployment Coupling

Microservices that share code by importing each other directly can no longer be deployed independently. If service A imports a utility from service B's internal package, deploying B means coordinating with A to make sure nothing breaks.

Layers remove that coupling by putting shared code in the foundation. Utilities live in `pkg/go/foundation/` rather than in application packages, and services import foundation modules rather than each other. Because foundation modules are versioned independently and each service declares its constraints in its own `go.mod`, upgrading a foundation module for service A has no effect on service B until B chooses to upgrade too.

## Summary

I should say plainly that none of this is about naming conventions or directory aesthetics. It's about enforcing the direction of dependencies with physical boundaries, and everything else follows from that. Making upward imports impossible prevents circular dependencies; separating responsibilities prevents god services; isolating abstractions from implementations keeps infrastructure out of the business logic; and confining shared code to independently versioned foundation modules keeps deployments decoupled.

The nine-layer model works for small services and large polyglot monorepos alike. The Go structure in mothership and the Python structure in hpc apply the same principles, each in the idiom of its language: both enforce the dependency rule, both define interfaces before implementations, both compose decorators for cross-cutting concerns, and both lean on the directory structure to make the architecture visible and its violations obvious.

People sometimes object that all this structure is overhead. On the face of it, it is; there are more directories, more interfaces and more wiring than a flat layout needs. But recall the repository at commit five thousand from the opening of this post. The structure is the price of not ending up there, and as far as I'm concerned it's a bargain.
