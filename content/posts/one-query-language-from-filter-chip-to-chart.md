---
title: "One Query Language, From Filter Chip to Chart"
date: 2026-10-31
draft: false
description: "A small, typed query language can carry a platform from the filter chips on a list page all the way to a pivoting analytics engine. One filter tree, one field schema, and one sort form, compiled by a fold into SQL, CQL, or anything else."
images:
  - "images/og/one-query-language-from-filter-chip-to-chart.png"
tags: ["architecture", "design-patterns", "go", "system-design"]
keywords: ["query language", "filter DSL", "intermediate representation", "visual algebra", "Polaris", "Tableau", "keyset pagination", "analytics engine", "go generics"]
series: ["Software Architecture"]
---

Every product with a list page eventually grows a filter bar, and every product with a filter bar eventually grows a dashboard. The usual result is two unrelated query systems. The list endpoints accept a pile of ad-hoc parameters (`status=`, `search=`, `from=`), each store parses them its own way, and sorting is whatever order the database happens to return. The dashboards get a bespoke endpoint per chart, fixed at design time, that cannot pivot, regroup, or drill down without another endpoint.

On the multi-tenant document search platform I'm building for an enterprise client, we went the other way. One small, typed query language runs the whole stack: the filter chips and typeahead on every list page, the sort and paging behind infinite scroll, and the analytics engine that draws every chart on the operations console. This post walks through how that language is built, why it is a tree rather than a string, and how the same filter a user builds on a list page compiles, unchanged, into a query against the analytics store.

## The grammar

The wire grammar is deliberately boring. A filter is JSON: a leaf compares one field to one value, and `$and` / `$or` compose leaves into a tree.

```json
{"$and": [
  {"$eq":   {"status": "indexed"}},
  {"$gte":  {"created_at": "2026-10-01T04:00:00Z"}},
  {"$like": {"name": "quarterly report"}}
]}
```

The operators are a small fixed set: equality and inequality, the four orderings, set membership, a case-insensitive `like`, and null checks. Sort is a list of fields with directions, `created_at:desc,name` on the wire. Both are strings on list requests because list endpoints are `GET`s and query parameters must be scalars; inside the system they are typed values.

That is the entire user-facing surface. The interesting decisions are all about what happens after parsing.

## A filter is a tree, so compile it with a fold

Inside the services the filter is not JSON. It is a sealed union with exactly two shapes, a clause and a group:

```go
// Filter is a sealed union: a single comparison or a boolean group of filters.
type Filter interface{ isFilter() }

// Clause compares one field to one value.
type Clause struct {
	Field string
	Op    Op
	Value any
}

// Group joins its members with AND or OR.
type Group struct {
	Or      bool
	Members []Filter
}

func (Clause) isFilter() {}
func (Group) isFilter()  {}
```

The key observation is that this is a free algebra. A SQL `WHERE` clause, a MongoDB query document, and an Elasticsearch `bool` query are not different contracts. They are different *interpretations* of the same tree:

| Filter | SQL | Mongo | Elasticsearch |
|---|---|---|---|
| `status = "indexed"` | `status = $1` | `{status: {$eq: "indexed"}}` | `{"term": {"status": "indexed"}}` |
| `A AND B` | `(A) AND (B)` | `{$and: [A, B]}` | `{"bool": {"must": [A, B]}}` |

So compilation is a fold: walk the tree once, and hand each node to a backend that knows how to say it in its own language. The backend is an interface with two type parameters, one for predicates and one for sort directives, because those are different structures in most datastores:

```go
// Backend interprets filter nodes into a datastore's native predicate (Q) and sort (S) types.
type Backend[Q, S any] interface {
	Clause(column string, op Op, value any) Q
	And(members []Q) Q
	Or(members []Q) Q
	Empty() Q // match everything
	Order(column string, desc bool) S
}

// Compile folds f through b. resolve maps a public field name to its storage column
// and rejects any field that is not on the resource's allow-list.
func Compile[Q, S any](b Backend[Q, S], resolve func(field string) (string, error), f Filter) (Q, error) {
	switch n := f.(type) {
	case nil:
		return b.Empty(), nil
	case Clause:
		col, err := resolve(n.Field)
		if err != nil {
			var zero Q
			return zero, err
		}
		return b.Clause(col, n.Op, n.Value), nil
	case Group:
		members := make([]Q, 0, len(n.Members))
		for _, m := range n.Members {
			q, err := Compile(b, resolve, m)
			if err != nil {
				var zero Q
				return zero, err
			}
			members = append(members, q)
		}
		if n.Or {
			return b.Or(members), nil
		}
		return b.And(members), nil
	}
	var zero Q
	return zero, fmt.Errorf("unknown filter node %T", f)
}
```

The fold is written once and imports no database driver. The SQL backend is a few dozen lines that map each operator to a parameterized predicate. Adding a datastore means writing one more backend and selecting it by configuration, not forking the compiler. That property turned out to matter far more than we expected when we built the analytics engine, but first, the list pages.

## The allow-list is the security boundary

A query language that lets clients name columns is an injection vector unless every name is checked. Each resource therefore declares which fields are filterable, which operators each field accepts, and which fields are sortable. `resolve` in the fold above is where that list is enforced: an unknown field is a coded `INVALID_ARGUMENT` error at the transport edge, values are type-checked against the field's declared type, and every predicate the backend emits is parameterized. Nesting is capped, so a client cannot send a ten-thousand-level tree.

We generate the allow-lists rather than hand-write them. Each filterable field on a list resource is annotated once, in the API contract:

```proto
string status = 4 [(listquery.field) = {
  type: ENUM
  operators: [EQ, NE, IN]
  value_source: ENUM
  sortable: true
}];
```

A code generator turns those annotations into the Go allow-lists, the TypeScript field schema the filter builder reads, and the input to a build gate. That gate cross-checks the schema against the database migrations and fails the build if any field exposed for `like`, sort, or keyset paging lacks the index that makes the query cheap. Exposing a filter is a performance promise, and the build holds us to it.

Sort is strict in the same way. An early version quietly dropped unknown sort fields; we changed it to reject them, because a stale saved view that silently sorts by `created_at` is a bug the user cannot see.

## Paging is just another filter

List pages need two kinds of paging: a numbered pager with a total count, and infinite scroll on card views. Offset paging is correct for the first and quadratic for the second, so we support both behind one opaque page token. The client treats the token as a blob; the server decodes it and dispatches to the offset arm or the keyset arm.

The keyset arm has a nice property. "Rows after the last one I saw, under sort `(created_at desc, id desc)`" is itself a filter:

```
created_at < last.created_at
OR (created_at = last.created_at AND id < last.id)
```

So the seek is built as an ordinary filter tree and handed to the same fold as the user's filter. There is no second, ORM-specific pagination compiler, and the keyset seek works on any backend the fold supports. The token also carries a fingerprint of the sort and filter, so a cursor minted under one query and replayed under another is a clean error rather than a page of duplicated or skipped rows.

## The edges: typeahead, caching, and time zones

The query language also shapes the parts of the UI that feel like polish.

**Typeahead follows the field schema.** Each field's `value_source` tells the client which control to render. A small enum becomes a static dropdown with no network call. A high-cardinality text field becomes a debounced typeahead backed by a bounded suggestion endpoint. A reference to another entity, such as an owner, searches that entity's table and returns `{value: id, label: name}`. Suggestions run under exactly the same authorization predicate as the list itself, so the typeahead can never reveal a value from a row the user could not see.

**Caching keys on access, not just on the query.** Suggestions and total counts are cached; list pages are not (the index is the performance mechanism). Every cache key includes an *access fingerprint*: a hash of the workspaces the user can see and their clearance level. When a grant changes, the fingerprint changes, and old entries are simply never read again. Authorization changes invalidate by key rotation, not by reaching into the cache.

**Time is UTC everywhere except the edges.** Storage, sorting, and cursors are UTC. A date filter is entered as a local civil date ("today", "last 7 days") and converted to a half-open range of UTC instants at local midnights, so daylight-saving boundaries come out right. Audit views use a fixed, labeled zone instead, because there a "day" is a record boundary.

## From list pages to charts

All of that would be a tidy list-query SDK. The reason I wanted to write about it is what happened when the platform needed dashboards.

The second phase of the project is operational: every AI call is traced, evaluated, budgeted, and audited, and each of those capabilities ships a console screen. Written the naive way, that was about twenty bespoke chart-plus-endpoint pairs, none of which could pivot or drill down. We already had half of an analytics engine: a typed filter tree, allow-listed field schemas, a multi-target compiler, and a streaming channel to the browser. What was missing was a grammar of graphics, an aggregate query shape, and an analytic store.

The grammar came from work I have been close to for a long time. Chris Stolte's Polaris, built with Diane Tang and Pat Hanrahan at Stanford and later commercialized as Tableau, formalized a visualization as a *table algebra* over fields ([Stolte, Tang & Hanrahan, 2002](https://doi.org/10.1109/2945.981851)). Fields are dimensions or measures. Expressions on the Rows and Columns shelves combine them with three operators: concatenation (`+`), cross (`×`), and nest (`/`, the cross product restricted to combinations that occur in the data). A Level-of-Detail shelf sets the grouping grain, and encodings map fields to color, size, shape, and label. The crucial property is that a specification compiles *mechanically* into the database queries, the partition of the result into panes, and the mark for each pane.

Our chart specification is a small version of that formalism. Simplified, a cost-by-model trend looks like this:

```json
{
  "source":  "ai_usage",
  "columns": "day",
  "rows":    "sum(cost_usd)",
  "color":   "model",
  "filter":  {"$and": [{"$eq": {"provider": "bedrock"}}]},
  "sort":    [{"field": "day"}],
  "grain":   "day",
  "range":   {"last": "30d"}
}
```

The `filter` and `sort` fields are not "similar to" the list-query ones. They are the same types, validated against the same kind of field schema, which now also records each field's role (dimension, measure, or time) and the aggregates each measure permits. A pure compiler turns the specification into three things:

1. **One aggregate query.** The group-by is the union of every dimension on every shelf, plus level of detail, plus encodings; the measures carry their aggregates; the filter, sort, grain, and time range pass through.
2. **A pane structure.** The normalized shelf algebra gives the ordered row and column tuples that lay out the small multiples.
3. **A mark per pane**, inferred from field roles the way Polaris does it: ordinal by ordinal is a text or heat cell, ordinal by quantitative is a bar, time by quantitative is a line, quantitative by quantitative is a point. An explicit mark overrides the inference.

Drill-down replaces a dimension on a shelf with its child in a declared hierarchy, for example organization, then team, then workspace, then user. The result is a new specification, not a new endpoint.

## The analytic store is just another backend

The analytic store is Cassandra, chosen for time-bucketed, tenant-partitioned, pre-aggregated rollups. Each declared cube has a rollup table per grain, partitioned by tenant, cube, and time bucket so partitions stay bounded, and each row holds additive partial aggregates (sum, count, min, max, and mergeable sketches for distinct counts and percentiles). A query scans the bucket partitions for its time range and merges the partials in the engine. The tenant is always the first partition-key component and always comes from the verified token, so a cross-tenant read is not an expressible query.

Here the fold paid for itself. The Cassandra client implements the same `Backend` interface, so the chart's filter goes through the same `Compile` as a list page's filter. Clauses that hit a partition or clustering column push down into CQL; the rest become a residual predicate the engine applies while merging. Pushdown is an optimization, never a semantic difference: a filter means the same thing on a list page and in a chart, by construction.

## One query core

Once both systems existed, their seams started to show. The list endpoints and the chart endpoint shared the filter grammar and the filter type, but they had two sort wire forms, two field descriptors, two TypeScript clients, and, worst of all, different behavior: an unknown sort field was silently dropped by one API and rejected by the other. The chart's filter was also an opaque string inside a structured message, so we could not diff it, reuse one clause, or version it clause by clause.

So we collapsed them into a single query core, defined once in the API contract and once in each language:

| Layer | What it adds |
|---|---|
| **Query core** | source, filter tree, sort, and time range plus grain where the source has a time field |
| **List query** | the core plus paging |
| **Aggregate query** | the core plus group-by and measures |
| **Chart specification** | shelves, encodings, and marks, which compile to an aggregate query |

The filter became a structured message: a `oneof` of a clause, an `and` group, or an `or` group. List requests still carry a string, because `GET`, but the string is defined as the JSON encoding of that same tree, and one codec converts between them, so a saved list view stores the structured form. Sort is one message everywhere and is strict everywhere. On the frontend, one TypeScript module owns the filter tree, the operators, the sort form, and the codecs; the chart client imports its filter and sort from there and keeps only shelves, encodings, and marks.

The payoff is that the filter builder is written once, and a filter means the same thing wherever it appears. Moving a filter from a list page to a chart, or from a chart back to the rows behind it, is a matter of passing a value, because there is only one kind of filter to pass.

## What I would keep

**Make the internal representation a tree, and compile it with a fold.** Strings are fine on the wire; inside the system they hide structure you will want later, for diffing, versioning, pushdown, and reuse. A fold through a backend interface turns "support another datastore" into "write one interpreter".

**Put the security boundary in the schema, and generate the schema.** Allow-lists that are annotations on the contract cannot drift from the code, and a generated schema can be checked against the database's indexes at build time.

**Reject, don't drop.** Every place we silently ignored an unknown field later produced a bug that looked like wrong data. A coded error at the edge is cheaper.

**Look for the second consumer before building the second system.** Paging became a filter. Typeahead inherited the list's authorization. Charts inherited the filter, the sort, the schema, and the compiler. Each time, the new feature was smaller because it was an interpretation of the language we already had, not a new language.

More than two decades after Polaris, the lesson still holds: when a query has a precise algebra, the rest of the system can be derived from it.
