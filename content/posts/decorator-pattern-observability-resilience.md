---
title: "The Decorator Pattern for Observability and Resilience"
date: 2026-02-22
draft: false
description: "Why logging, metrics, retry and circuit breaking belong in wrappers rather than in your business logic, with examples in Go and Python."
images:
  - "images/og/decorator-pattern-observability-resilience.png"
tags: ["architecture", "design-patterns", "reliability"]
keywords: ["decorator pattern", "observability", "resilience", "design patterns", "python", "go"]
series: ["Software Architecture"]
---

Every production service I have worked on needs logging, metrics, retries and circuit breaking. Nobody argues about that. The interesting question is where all of it should live. The naive answer (and it is the answer most of us reach for first) is to put it directly inside the business methods, which leaves you with functions that are mostly infrastructure boilerplate and only incidentally about the domain. Then someone decides to change the retry policy, or swap the metrics backend, and you find yourself editing every service in the codebase. That is the single-responsibility principle violated in the most tedious way possible.

The decorator pattern offers a more principled alternative. You pull each cross-cutting concern out into its own wrapper, and that wrapper implements the same interface as the thing it wraps. Each one adds exactly one behavior (logging, say, or retry), then hands the call to the implementation inside it. The business logic never learns that it is being watched or protected, and each concern can be written, tested and changed on its own.

## Motivation: Failure in Distributed Systems

In a monolith, a failed function call raises an exception and the caller deals with it. Distributed systems fail differently. Network partitions, timeouts, overloaded upstreams and cold starts are not edge cases there; they are a normal Tuesday. So every call from one service to another needs some defensive layer around it: retries with exponential backoff so that transient failures have a chance to clear, circuit breakers so that one degraded upstream doesn't drag its callers down with it, timeouts so that a hung connection can't hold resources forever, and structured logging so that you can trace a request across service boundaries after the fact.

What the decorator pattern buys you is the ability to apply all of this uniformly, at every client and service boundary, without writing it twice. One `RetryDecorator` wraps any client interface. One `CircuitBreakerDecorator` protects any upstream. When operations decides the backoff should be jittered rather than purely exponential, the change touches one file. And when a new database client comes along, you compose the same stack around it with an error classifier for that particular database, and it inherits logging, metrics, retry and circuit breaking for free.

## The Pattern in Go

Go's implicit interfaces make the pattern feel almost native. A logging decorator for an event producer is simply a struct that holds the inner producer and a logger. Because it satisfies the same `EventProducer` interface, callers have no way of telling it apart from the real thing:

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

A circuit breaker has the same shape. It checks the state of the circuit before each call and records the outcome afterward; if the upstream has already failed too often, it returns immediately without trying the call at all:

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

The property that matters is that every decorator takes and returns the same interface. That is what makes them composable: you can stack as many as you like without changing a single type signature.

## The Pattern in Python

Python lets you go a step further with `__getattr__`. Instead of wrapping each method by hand, the decorator intercepts attribute access, checks whether the attribute is callable, and wraps it on the way out. The result is one decorator class that works on any interface at all, with no per-method boilerplate:

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

The same trick works for metrics, retry, timeout and circuit breaker decorators. Each is a small standalone class that can wrap any object with callable attributes.

## Composition: Stacking Decorators

Where the pattern really earns its keep is composition. Each decorator knows about exactly two things: the interface it wraps and the one concern it adds. You stack them, and each layer contributes one behavior. A fluent builder makes the order explicit and, to my mind at least, rather pleasant to read:

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

You don't need a builder, mind you. Composing by hand is just as explicit, and the variable names document each layer as you go:

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

When a new client shows up (Redis, Elasticsearch, Kafka, whatever it happens to be), you build the same stack around it with an error classifier that knows that system's failures, and it inherits every bit of the observability and resilience above without any new implementation work.

## Summary

None of this is new, of course. The Gang of Four wrote the pattern down in 1994, and functional programmers would point out (correctly) that it is just function composition wearing a trench coat. But that is rather the point. A repository should be about data access, not about Prometheus histograms or when to retry, and decorators let it stay that way. Each one can be tested on its own by mocking the interface it wraps, and the builder chain or factory tells you, in order, exactly which protections are in place. There is no annotation magic and no framework quietly intercepting your calls; there are only functions wrapping functions, each with a contract you can read. I have yet to find a cleaner way to keep the plumbing out of the house.
