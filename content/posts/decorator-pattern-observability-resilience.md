---
title: "The Decorator Pattern for Observability and Resilience"
date: 2026-02-22
draft: false
description: "How the decorator pattern cleanly separates logging, metrics, retry, and circuit breaking from business logic — with examples in Python and Go."
images:
  - "images/og/decorator-pattern-observability-resilience.png"
tags: ["architecture", "design-patterns", "observability", "resilience"]
keywords: ["decorator pattern", "observability", "resilience", "design patterns", "python", "go"]
series: ["Software Architecture"]
---

Production services require logging, metrics collection, retry logic, and circuit breaking. The central question is where these cross-cutting concerns should reside. The naive approach — scattering observability and resilience logic directly inside business methods — produces implementations that are predominantly infrastructure boilerplate, with the actual domain logic obscured. Modifications to retry policies or metrics backends require changes across every service in the codebase, violating the single-responsibility principle and making the system brittle to operational change.

The decorator pattern provides a principled alternative. Each cross-cutting concern is extracted into a standalone wrapper that implements the same interface as the component it decorates. Each wrapper adds exactly one behavior — logging, metrics, retry, or circuit breaking — then delegates to the inner implementation. The business logic remains unaware that it is being observed or protected, and each concern can be developed, tested, and modified independently.

## Motivation: Failure in Distributed Systems

In a monolithic system, a failed function call raises an exception that the caller handles directly. Distributed systems present a fundamentally different failure model. Network partitions, request timeouts, overloaded upstreams, and cold starts are not edge cases; they are routine operational conditions. Every service-to-service call requires a defensive layer: retries with exponential backoff to allow transient failures to resolve, circuit breakers to prevent a degraded upstream from cascading into the caller, timeouts to bound resource consumption on hung connections, and structured logging to enable distributed tracing across service boundaries.

The decorator pattern enables uniform application of these concerns across every client and service boundary without duplicating the implementation. A single `RetryDecorator` wraps any client interface. A single `CircuitBreakerDecorator` protects any upstream dependency. When the operational team determines that a backoff strategy should change from exponential to jittered, the modification is confined to one file. When a new database client is introduced, the same decorator stack is composed with a domain-specific error classifier, and the full set of protections — logging, metrics, retry, circuit breaking — is applied automatically.

## The Pattern in Go

Go's implicit interface satisfaction makes the decorator pattern particularly natural. A logging decorator for an event producer is a struct that holds the inner producer and a logger. It satisfies the same `EventProducer` interface, so callers cannot distinguish it from the underlying implementation:

```go
// loggingProducer wraps an EventProducer with structured logging.
// It records publish duration, event name, and any errors without
// modifying the underlying producer's behavior.
type loggingProducer struct {
    inner  EventProducer
    logger Logger
}

// WithLogging decorates a producer with entry/exit logging.
// Returns the same EventProducer interface — callers cannot tell
// they are talking to a decorator.
func WithLogging(p EventProducer, logger Logger) EventProducer {
    return &loggingProducer{inner: p, logger: logger}
}

func (p *loggingProducer) Publish(ctx context.Context, event Event) error {
    start := time.Now()
    err := p.inner.Publish(ctx, event)
    p.logger.Info("publish",
        "event", event.Name(),
        "duration", time.Since(start),
        "error", err,
    )
    return err
}
```

A circuit breaker decorator follows the same structural pattern. It checks the circuit state before each call and records the outcome afterward. If the upstream has exceeded the failure threshold, the decorator short-circuits immediately without attempting the call:

```go
// circuitBreakerProducer fails fast when the upstream is degraded.
// BeforeCall checks the circuit state; AfterCall records the outcome
// so the breaker can track the failure rate over time.
type circuitBreakerProducer struct {
    inner EventProducer
    cb    CircuitBreaker
}

func (p *circuitBreakerProducer) Publish(ctx context.Context, event Event) error {
    if err := p.cb.BeforeCall(ctx); err != nil {
        return err // circuit is open — fail fast
    }
    err := p.inner.Publish(ctx, event)
    p.cb.AfterCall(ctx, err)
    return err
}
```

The essential property is that every decorator accepts and returns the same interface. This makes decorators composable — an arbitrary number can be stacked without altering any type signatures.

## The Pattern in Python

Python's `__getattr__` proxy mechanism extends the pattern further. Rather than wrapping each method individually, the decorator intercepts attribute access at the class level, determines whether the attribute is callable, and wraps it transparently. This approach yields a single decorator class that operates on any interface without per-method boilerplate:

```python
class LoggingDecorator:
    """Transparent proxy that logs entry, exit, and errors for every call.

    Uses __getattr__ so it works with any interface — no per-method
    boilerplate. Adding logging to a new client is a single line:
        client = LoggingDecorator(raw_client, service="neo4j", logger=logger)
    """

    def __init__(self, inner, *, service: str, logger):
        self._inner = inner
        self._logger = logger
        self._service = service

    def __getattr__(self, name):
        # Delegate non-callable attributes unchanged
        attr = getattr(self._inner, name)
        if not callable(attr):
            return attr

        @wraps(attr)
        async def wrapper(*args, **kwargs):
            start = time.monotonic()
            try:
                result = await attr(*args, **kwargs)
                self._logger.debug(
                    "%s.%s ok",
                    self._service, name,
                    extra={"duration_ms": (time.monotonic() - start) * 1000},
                )
                return result
            except Exception as exc:
                self._logger.warning(
                    "%s.%s failed",
                    self._service, name,
                    extra={"error": str(exc)},
                )
                raise

        return wrapper
```

The same `__getattr__` approach generalizes to metrics, retry, timeout, and circuit breaker decorators. Each is a standalone class capable of wrapping any object that exposes callable attributes.

## Composition: Stacking Decorators

The power of the pattern lies in composition. Each decorator is independent — it is aware only of the interface it wraps and the single concern it introduces. Decorators are composed into a stack where each layer contributes exactly one behavior. A fluent builder makes the ordering explicit and the composition readable:

```go
// Fluent builder — reads top-to-bottom as outermost to innermost.
// A call enters at Recovery, flows through Auth → Transaction →
// Observability, reaches the concrete service, then unwinds back out.
svc := decorators.NewBuilder(NewUserService(repo), "users").
    WithRecovery().
    WithAuthorization(authorizer).
    WithTransaction(txManager).
    WithObservability(logger, metrics, tracer).
    Build()
```

Without a builder, the manual composition is equally explicit. Each variable name documents the layer being applied:

```python
# Stack order: Logging → Metrics → Retry → CircuitBreaker → Timeout → Raw
# Each decorator wraps the previous, adding one concern.
raw = Neo4JClient(uri=uri, user=user, password=password)
with_timeout = TimeoutDecorator(raw, timeout_seconds=30.0, service="neo4j")
with_cb = CircuitBreakerDecorator(with_timeout, name="neo4j", threshold=5)
with_retry = RetryDecorator(with_cb, max_attempts=3, classifier=Neo4JErrorClassifier())
with_metrics = MetricsDecorator(with_retry, service="neo4j")
client = LoggingDecorator(with_metrics, service_name="neo4j", logger=logger)
```

When a new database client is introduced — Redis, Elasticsearch, Kafka — the same decorator stack is composed with a domain-specific error classifier, and the full complement of observability and resilience behaviors is inherited without additional implementation effort.

## Summary

The decorator pattern confines each cross-cutting concern to a single file with a single responsibility. Business logic remains clean: a repository implementation is concerned with data access, not with Prometheus histograms or retry scheduling. Decorators are individually testable — the inner interface is mocked, and the wrapper's behavior is verified in isolation. The composition is explicit and inspectable: the builder chain or factory function specifies exactly which protections are in place and in what order. There is no annotation indirection, no framework-level interception, and no implicit behavior — only functions wrapping functions, each with a well-defined contract.
