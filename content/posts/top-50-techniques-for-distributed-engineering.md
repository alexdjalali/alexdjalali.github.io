---
title: "The Top 50 Techniques for Distributed Engineering"
date: 2026-07-13
draft: false
description: "That nearly every distributed system is built from the same fifty techniques (sharding, quorums, idempotency, backpressure, circuit breakers and the rest), each shown here with a Go or Python implementation and, where it helps, a diagram."
images:
  - "images/og/top-50-techniques-for-distributed-engineering.png"
tags: ["distributed-systems", "system-design", "architecture", "reliability", "go", "python"]
keywords: ["distributed systems", "system design", "sharding", "consistent hashing", "caching", "idempotency", "saga pattern", "circuit breaker", "backpressure", "quorum", "CAP theorem", "rate limiting", "event sourcing", "go", "python"]
series: ["Software Architecture"]
---

Distributed engineering, as I have come to understand it, is less a collection of technologies than a collection of *tradeoffs*. Every technique below buys you something (throughput, latency, availability, durability) and charges you for it somewhere else, usually in consistency or in operational complexity. The engineers who are good at this are not the ones who have memorized the most tools. They're the ones who can look at a requirement, name the two or three techniques that apply, and say precisely what each one will cost.

What follows is my attempt to distill that vocabulary. The organizing spine comes from <a href="https://www.hellointerview.com/learn/system-design" target="_blank" rel="noopener noreferrer">HelloInterview's *System Design in a Hurry*</a>, whose <a href="https://www.hellointerview.com/learn/system-design/in-a-hurry/core-concepts" target="_blank" rel="noopener noreferrer">core concepts</a>, <a href="https://www.hellointerview.com/learn/system-design/in-a-hurry/key-technologies" target="_blank" rel="noopener noreferrer">key technologies</a> and <a href="https://www.hellointerview.com/learn/system-design/in-a-hurry/patterns" target="_blank" rel="noopener noreferrer">common patterns</a> map almost one-to-one onto what you actually reach for in production. I've paired each technique with a Go or Python implementation and, where it clarifies the moving parts, a diagram. The code is illustrative (real implementations add error handling, metrics and configuration), but every snippet is correct and idiomatic enough to lift into a service.

One warning will recur throughout, so I may as well give it up front: most of these techniques are introduced too early far more often than too late. A well-tuned single database handles more than you think. Sharding, distributed locks and home-grown consensus are where systems go to die when they arrive before they're needed. The skill lies less in knowing the technique than in knowing the moment.

With that said, on to the techniques.

## Part I: Scaling the Stateless Tier

The cheapest scaling you will ever do is on the tier that handles requests, *provided* you keep it stateless, and everything in this part is about earning that proviso.

### 1. Scale out, not up

Vertical scaling (a bigger box) is the first instinct and the first ceiling. You run out of cores, the machine becomes a single point of failure, and the price curve goes vertical well before the performance does. Horizontal scaling adds commodity machines behind a load balancer instead. It's cheaper per unit of throughput, it gives you redundancy for free, and it has no obvious ceiling. The catch is that your service may hold no per-request state locally: no in-memory sessions, no "sticky" files on disk, nothing a second replica couldn't reproduce.

{{< mermaid >}}
flowchart TB
    C[Clients] --> LB[Load Balancer]
    LB --> A1[App replica 1]
    LB --> A2[App replica 2]
    LB --> A3[App replica 3]
    A1 --> D[(Shared DB / Cache)]
    A2 --> D
    A3 --> D
{{< /mermaid >}}

### 2. Load balancing: L4 versus L7

A layer-4 load balancer routes on TCP or UDP. It sees connections rather than content, which makes it fast and, for want of a kinder word, dumb. A layer-7 load balancer speaks HTTP, so it can route `/api` to one service and `/static` to another, terminate TLS and retry idempotent requests. Default to L7 for its flexibility, and reach for L4 when you have persistent connections (WebSockets, gRPC streams) and want the balancer to pin a raw TCP connection to a backend and otherwise stay out of the way.

### 3. Externalize session state

This is the rule that makes technique #1 possible: if a request needs state, the state lives in a shared store (Redis, a database, a signed token) and never in the replica's memory. Session data goes in a distributed cache, identity travels in a JWT that any replica can verify, and uploads go straight to blob storage. Once no replica is special, any replica can die and any replica can serve any request.

### 4. Health checks, readiness, and graceful shutdown

The load balancer has to know which replicas can take traffic, and the trick is to split the signal in two. A *liveness* check answers "is this process alive?", while a *readiness* check answers "can it serve right now?" and goes false while the replica warms its caches or drains. On shutdown, stop accepting new work, finish what's in flight, and only then exit.

```go
func (s *Server) Shutdown(ctx context.Context) error {
    s.ready.Store(false)          // readiness now fails; LB stops routing here
    time.Sleep(s.drainDelay)      // let the LB notice before we close connections
    return s.http.Shutdown(ctx)   // finish in-flight requests, reject new ones
}
```

### 5. Autoscale on the signal that actually predicts load

Autoscaling on CPU is a trap for I/O-bound services, which saturate on connections or queue depth long before the CPU notices. Scale instead on the metric that leads your bottleneck, whether that's request concurrency, p99 latency or consumer lag for a worker fed by a queue. And scale *out* faster than you scale *in*, since an overeager scale-down during a lull will leave you flat-footed when the next spike arrives.

### 6. Consistent hashing for elastic membership

If you distribute keys across N servers with `hash(key) % N`, then adding or removing a single server changes N and remaps *almost every key*, which is catastrophic for a cache or a sharded store. Consistent hashing places servers and keys on a virtual ring, and a key belongs to the next server clockwise. Add a server and only the keys in one arc move, so roughly `1/N` of the data relocates rather than nearly all of it. This is the mechanism behind membership changes in Cassandra, DynamoDB and Redis Cluster.

```go
type Ring struct {
    replicas int                // virtual nodes per server, for even spread
    ring     []uint32           // sorted positions on the hash circle
    owner    map[uint32]string  // position -> server
}

func (r *Ring) Add(servers ...string) {
    for _, s := range servers {
        for i := 0; i < r.replicas; i++ {
            h := crc32.ChecksumIEEE([]byte(strconv.Itoa(i) + s))
            r.ring = append(r.ring, h)
            r.owner[h] = s
        }
    }
    sort.Slice(r.ring, func(i, j int) bool { return r.ring[i] < r.ring[j] })
}

// Get returns the server that owns key: the first ring position >= hash(key),
// wrapping around the circle.
func (r *Ring) Get(key string) string {
    h := crc32.ChecksumIEEE([]byte(key))
    i := sort.Search(len(r.ring), func(i int) bool { return r.ring[i] >= h })
    return r.owner[r.ring[i%len(r.ring)]]
}
```

The `replicas` field (the virtual nodes) matters more than it looks. With one point per server, load lands unevenly; with 100 to 200 virtual nodes per server, the arcs even out.

## Part II: Data at Scale

The database is where distributed systems get hard, because data has requirements of *identity* and *durability* that stateless replicas simply don't.

### 7. Pick one database and know it cold

The "SQL versus NoSQL" debate is a tar pit. The two categories overlap enormously: Postgres has JSON columns and scales horizontally, and DynamoDB models relationships perfectly well. A broad claim like "I need relational because I have relationships" tends to signal inexperience. Pick the database you understand deeply instead, and justify it with a *specific* property ("Postgres, because I want ACID transactions across the order and inventory tables"). Depth in one store beats a shallow comparison of two.

### 8. Index for your query patterns

An index turns a full-table scan into a logarithmic lookup. The default B-tree serves exact matches *and* range queries because it keeps its keys sorted, whereas a hash index is faster for exact matches and useless for anything else. The technique people most often miss is the composite index: for a query that filters on two columns, one index over both beats two separate indexes.

```sql
-- Query: events in a city on a date
SELECT * FROM events WHERE city = 'SF' AND event_date = '2026-12-25';

-- One composite index serves it; column order matters (equality then range)
CREATE INDEX idx_events_city_date ON events (city, event_date);
```

Every index you add speeds up reads and *slows down writes*, since each write has to update every index. Index the columns you filter and join on, not every column you have.

### 9. Denormalize the read path, deliberately

Normalization removes duplication: an order references a `user_id` rather than copying the user's name. That keeps the data consistent but forces joins, and joins get expensive at scale. Denormalization copies the name into the order row so that a read touches one table, and the cost lands on writes instead (change a name and you must fan the update out to every copy). Start normalized, and denormalize a particular hot path only once you've measured that its joins hurt. Denormalizing up front, before you know your read patterns, is guessing.

### 10. Shard when (and only when) one node can't hold it

Sharding splits data across independent database servers, and you need it only when you hit a real wall: more data than one instance can store, or more writes than one primary can absorb. The decision that dominates all others is the shard key. Shard a social app by `user_id` and each user's data lives on one shard, so reads scoped to a user are fast and touch a single shard, but "trending across all users" now scatters across every shard. That is the tradeoff, and you should say it out loud.

{{< mermaid >}}
flowchart TB
    W[Write for user_id=42] --> R{shard = hash user_id mod N}
    R -->|shard 0| S0[(Shard 0)]
    R -->|shard 1| S1[(Shard 1)]
    R -->|shard 2| S2[(Shard 2)]
{{< /mermaid >}}

Sharding also creates problems you didn't have before. Transactions across shards become nearly impossible, hot shards form when one key gets a disproportionate share of traffic, and resharding means moving terabytes around. Do the capacity math first. At 10K writes a second and 100GB of data, you don't need shards; you need a well-tuned primary.

### 11. Read replicas and the lag they introduce

Read traffic usually grows faster than writes, and ratios of 10:1 or 100:1 are common. The first and cheapest lever is read replicas: the primary takes the writes and streams its changelog to read-only copies that absorb the reads. The cost is replication lag. A replica is milliseconds to seconds behind, so a user who writes and immediately reads from a replica may not see their own change. Where that matters, route that user's next read to the primary (read-your-writes), or read from the primary only on the paths where consistency is critical.

{{< mermaid >}}
flowchart LR
    App -->|writes| P[(Primary)]
    P -. async replication .-> R1[(Replica 1)]
    P -. async replication .-> R2[(Replica 2)]
    App -->|reads| R1
    App -->|reads| R2
{{< /mermaid >}}

### 12. Change Data Capture (CDC)

You often need the same data in two shapes, say the source of truth in Postgres and a searchable copy in Elasticsearch, or an analytics copy in a warehouse. Writing to both from the application is a race condition waiting to happen: one write succeeds, the other fails, and the stores diverge. Change data capture solves this by tailing the database's write-ahead log and emitting each committed change as an event, which consumers downstream apply to the derived stores. The derived store lags slightly, which for search and analytics is almost always fine.

{{< mermaid >}}
flowchart LR
    App --> DB[(Postgres)]
    DB -->|WAL| CDC[CDC connector]
    CDC --> K[Kafka]
    K --> ES[Elasticsearch]
    K --> DW[Warehouse]
{{< /mermaid >}}

### 13. Inverted indexes for full-text search

`WHERE text LIKE '%term%'` is a full-table scan, and it doesn't scale. A search engine builds an inverted index instead, a map from each word to the list of documents containing it, so a query becomes a lookup rather than a scan. Tokenization splits text into words, stemming collapses "running" and "runs" into "run" (the linguist in me would like a word about the difference between stemming and lemmatization, but I'll restrain myself), and fuzzy matching tolerates typos by edit distance. Elasticsearch is the default, and Postgres's GIN indexes cover lighter needs without a second system.

```json
{
  "distributed": [doc1, doc3, doc9],
  "systems":     [doc1, doc2, doc9],
  "quorum":      [doc3, doc9]
}
```

A search for "distributed systems" intersects the two postings lists, giving `[doc1, doc9]` in microseconds.

### 14. Geospatial indexing

"Find drivers within 2km" against a table of raw latitudes and longitudes means a scan over every row. Geospatial indexes make proximity queries fast by mapping two-dimensional space onto a one-dimensional sortable key. Geohashing interleaves the bits of latitude and longitude so that nearby points share key prefixes, and a quadtree recursively subdivides space so that dense regions get finer cells. Postgres with PostGIS, Redis's geo commands and Elasticsearch's geo queries all implement one or the other. Reach for them only at scale, though; for a thousand points, a scan beats the overhead of the index.

### 15. Offload large objects to blob storage

Never put images, video or files in your primary database; it's expensive and slow. Store the bytes in S3-style blob storage and keep only a URL in the database. To keep the bytes off your application servers entirely, hand the client a presigned URL, a temporary, scoped credential to upload or download directly to and from storage.

{{< mermaid >}}
sequenceDiagram
    participant C as Client
    participant S as App Server
    participant B as Blob Storage
    C->>S: request upload URL
    S->>S: record pending file in DB
    S-->>C: presigned PUT URL
    C->>B: PUT bytes directly (bypasses app server)
    B-->>S: upload-complete notification
    S->>S: mark file ready
{{< /mermaid >}}

### 16. Chunked, resumable uploads

A 4GB upload that fails at 95% shouldn't have to start again from zero. Multipart upload splits the file into parts, uploads them in parallel and assembles them on the server, so a failed part retries on its own and an interrupted upload resumes from the last acknowledged part. S3's multipart API gives you all of this out of the box; the technique is simply knowing to use it for anything large enough that a single stream is a liability.

## Part III: Caching

A cache hit on Redis takes about a millisecond, against 20 to 50 for a database query. Caching is the biggest latency win you have, and also the source of the subtlest bugs.

### 17. Cache-aside is the default

This is the pattern you'll use ninety percent of the time. On a read, check the cache; on a miss, load from the database, populate the cache with a TTL, and return. The application owns the cache, and the database never talks to it.

```python
import json

TTL_SECONDS = 300

def get_user(user_id: str) -> dict | None:
    key = f"user:{user_id}"
    if (cached := redis.get(key)) is not None:
        return json.loads(cached)              # hit

    user = db.query_one("SELECT * FROM users WHERE id = %s", user_id)  # miss
    if user is not None:
        redis.set(key, json.dumps(user), ex=TTL_SECONDS)
    return user
```

{{< mermaid >}}
sequenceDiagram
    participant A as App
    participant Ca as Cache
    participant DB as Database
    A->>Ca: GET user:42
    alt hit
        Ca-->>A: value
    else miss
        Ca-->>A: nil
        A->>DB: SELECT ...
        DB-->>A: row
        A->>Ca: SET user:42 (TTL)
    end
{{< /mermaid >}}

### 18. Know the write strategies

When data changes, how does the cache stay correct? Write-through writes the cache and the database together, which is consistent but makes every write pay the cost of the cache. Write-back writes the cache and flushes to the database later, which is fast but loses unflushed writes in a crash. Write-around writes only the database and lets the cache fill on the next read, which avoids caching data that is written and never read. Match the strategy to how often the data is written relative to how often it's read.

### 19. Invalidation is the hard part

There are only two hard things in computer science, as the saying goes, and cache invalidation is one of them. There are three workable strategies. You can delete the entry on write, which is simple and correct but risks a thundering herd (see #20); use a short TTL and accept bounded staleness; or write through to keep it fresh. Choose according to how stale is *too* stale. A product review can lag five seconds; an account balance can't.

### 20. Prevent the cache stampede

When a hot key expires, thousands of concurrent requests miss at once and stampede the database, a "thundering herd" that can take the whole system down. There are three defenses: request coalescing (one caller recomputes while the rest wait for its result), early recomputation (refresh before the key expires) and jittered TTLs (so keys don't all expire together). Go's `singleflight` gives you coalescing directly.

```go
var group singleflight.Group

func getUser(ctx context.Context, id string) (*User, error) {
    if u, ok := cacheGet(id); ok {
        return u, nil
    }
    // Concurrent callers for the same id share ONE database load.
    v, err, _ := group.Do(id, func() (any, error) {
        u, err := db.LoadUser(ctx, id)
        if err != nil {
            return nil, err
        }
        cacheSet(id, u, jitter(5*time.Minute))   // spread expiries
        return u, nil
    })
    if err != nil {
        return nil, err
    }
    return v.(*User), nil
}
```

### 21. Mitigate hot keys

A single key (a celebrity's profile, a viral post) can receive more traffic than one cache node can serve, and consistent hashing doesn't help, because the key still maps to one node. You can replicate the hot key across several nodes and pick one at random, or put it in a small in-process (L1) cache in front of Redis so that the hottest reads never leave the app server.

### 22. Push static content to a CDN

A CDN caches static assets (images, video, JavaScript, CSS) at edge locations physically close to users. A request from Sydney hits an edge in Sydney rather than your origin in Virginia, which saves hundreds of milliseconds and takes load off your servers. Pair it with blob storage (#15), so that the blob store is the origin and the CDN is the cache. The levers for invalidation here are cache-control headers and filenames that include a hash of their content.

## Part IV: Consistency and Coordination

This is the intellectual core of distributed systems, and (I'll admit) the part I enjoy most: what happens when two things must agree and the network sits between them.

### 23. CAP and PACELC: choose your failure behavior on purpose

During a network partition you can keep the system *consistent* (nodes refuse to serve rather than return stale data) or *available* (nodes keep serving and may diverge), but not both. Most systems should pick availability, since users tolerate a feed that's two seconds stale far better than an app that's down. Pick consistency when stale data costs money: inventory, payments, seat booking. PACELC adds the part CAP leaves out. *Else*, when there's no partition, you still trade latency against consistency, because strong consistency requires nodes to coordinate before they answer. You can, and should, mix models by subsystem, with eventual consistency for product reviews and strong consistency for the order ledger.

### 24. Eventual consistency and read-your-writes

Eventual consistency guarantees that, absent new writes, all replicas converge. It's the right default for systems that must stay available, but it produces a jarring bug: a user updates their profile, and the next read (served by a lagging replica) shows the old value. Read-your-writes consistency patches the experience. After a user writes, route *their* reads to the primary (or to a replica known to have the write) for a short window, and let the rest of the world see the eventually consistent view.

### 25. Quorums: R + W > N

In a replicated store with N copies, require W replicas to acknowledge a write and R replicas to answer a read. If `R + W > N`, the set of replicas you read from and the set you wrote to must overlap in at least one place, so a read always sees the latest acknowledged write, and you get strong consistency without contacting every node. (There is a certain pigeonhole elegance to it that I find hard not to admire.) Tune the knobs to the workload: `W=N, R=1` for read-heavy data that rarely changes, `W=1, R=N` for write-heavy data, and `W=R=⌈(N+1)/2⌉` for a balanced majority quorum.

```python
def is_strongly_consistent(n: int, r: int, w: int) -> bool:
    return r + w > n

# N=3 replicas, majority quorum: R=2, W=2 -> 2+2 > 3, overlap guaranteed
assert is_strongly_consistent(n=3, r=2, w=2)
assert not is_strongly_consistent(n=3, r=1, w=1)   # fast but may read stale
```

### 26. Optimistic concurrency control

When conflicts are rare, don't lock; *detect* them instead. Attach a version to each row, read it, compute your change, and write on the condition that the version is unchanged. If another writer got there first, the version has moved, your update matches no rows, and you retry. No locks are held, nothing deadlocks, and throughput is as high as it gets under low contention.

```python
def decrement_stock(item_id: str, qty: int) -> bool:
    row = db.query_one("SELECT quantity, version FROM inventory WHERE id = %s", item_id)
    if row["quantity"] < qty:
        raise OutOfStock(item_id)

    # Compare-and-swap: succeeds only if no one changed the row since we read it.
    updated = db.execute(
        """UPDATE inventory
              SET quantity = quantity - %s, version = version + 1
            WHERE id = %s AND version = %s""",
        qty, item_id, row["version"],
    )
    return updated == 1     # 0 rows -> lost the race -> caller retries
```

### 27. Pessimistic locking

When conflicts are common (everyone wants the *same* concert seat), optimistic retries thrash. Lock the row up front with `SELECT ... FOR UPDATE`, and other transactions will block until you commit. It's correct and simple, at the cost of throughput and of a deadlock if two transactions take their locks in different orders. Keep the critical section as short as you can.

```python
with db.transaction():
    seat = db.query_one(
        "SELECT status FROM seats WHERE id = %s FOR UPDATE", seat_id
    )
    if seat["status"] != "available":
        raise SeatTaken(seat_id)
    db.execute("UPDATE seats SET status = 'held' WHERE id = %s", seat_id)
# lock releases at commit
```

### 28. Distributed locks with leases and fencing tokens

Database row locks don't span systems or survive long holds. A distributed lock, held in Redis or ZooKeeper, coordinates across processes, for instance to hold a concert ticket for ten minutes while the user checks out. Two properties are non-negotiable. The lock needs a lease, so that it expires on its own and a crashed holder can't wedge the resource forever. And it needs a fencing token, a monotonic counter handed out with each acquisition, so that the resource can reject a stale holder whose lease has already expired.

```go
// Acquire atomically: SET key token NX PX ttl  (set-if-absent with expiry).
func acquire(rdb *redis.Client, key, token string, ttl time.Duration) (bool, error) {
    return rdb.SetNX(ctx, key, token, ttl).Result()
}

// Release only if WE still hold it — checked and deleted atomically in Lua,
// so we never delete a lock a slow predecessor already lost to expiry.
var releaseLock = redis.NewScript(`
    if redis.call("GET", KEYS[1]) == ARGV[1] then
        return redis.call("DEL", KEYS[1])
    end
    return 0`)

func release(rdb *redis.Client, key, token string) error {
    return releaseLock.Run(ctx, rdb, []string{key}, token).Err()
}
```

{{< mermaid >}}
sequenceDiagram
    participant W1 as Worker 1
    participant L as Lock (Redis)
    participant R as Resource
    W1->>L: SET lock t1 NX PX 10m
    L-->>W1: OK (token t1)
    Note over W1: lease expires before W1 finishes
    W1->>R: write with token t1
    R-->>W1: REJECT (t1 < latest token t2)
{{< /mermaid >}}

The fencing token is what makes the lock *safe* rather than merely *usually correct*. Without it, a worker that pauses and then resumes can corrupt state after its lease has lapsed.

### 29. Idempotency keys

Networks retry. A client that doesn't get a response sends again, and now you've charged the card twice. An idempotency key is a unique ID the client supplies for each logical operation; the server records it and returns the *original* result whenever the request is replayed. The subtlety is the race between two concurrent retries, which you settle with a `UNIQUE` constraint on the key, so that exactly one insert wins and the conflict is treated as a replay.

```python
def charge(idempotency_key: str, amount: int) -> Charge:
    prior = db.query_one(
        "SELECT charge_id FROM idempotency WHERE key = %s", idempotency_key
    )
    if prior is not None:
        return load_charge(prior["charge_id"])      # replay -> same result

    charge = gateway.charge(amount)
    try:
        db.execute(
            "INSERT INTO idempotency (key, charge_id) VALUES (%s, %s)",  # key is UNIQUE
            idempotency_key, charge.id,
        )
    except UniqueViolation:
        gateway.refund(charge.id)                    # a concurrent retry won; undo ours
        return load_charge(
            db.query_one("SELECT charge_id FROM idempotency WHERE key = %s",
                         idempotency_key)["charge_id"]
        )
    return charge
```

### 30. Leader election and consensus

Some jobs must have exactly one owner, such as the writer for a shard or the scheduler for a cron. Consensus algorithms (Raft, Paxos) let a cluster agree on a single leader and a single ordered log even as nodes fail. You'll rarely implement one yourself; you lean on ZooKeeper, etcd or a database's built-in election. The technique is *recognizing* the need ("this must run in exactly one place") and reaching for a coordination service rather than hand-rolling agreement, which is where careers go to die.

### 31. Distributed transactions: two-phase commit and sagas

When one operation must update several services atomically, there are two families of answer. In two-phase commit, a coordinator asks every participant to *prepare* and then to *commit* only if all of them agreed. That's strongly consistent, but it blocks on the coordinator and holds locks across the whole prepare window, so it scales poorly. The saga is the pragmatic alternative: run the steps as a sequence of local transactions, each with a compensating action that undoes it, and on failure run the compensations in reverse. You give up atomicity for availability and accept that intermediate states will be visible.

```python
class Saga:
    def __init__(self):
        self._undos = []

    def step(self, do, undo):
        result = do()               # local transaction
        self._undos.append(undo)    # register how to reverse it
        return result

    def compensate(self):
        for undo in reversed(self._undos):
            try:
                undo()
            except Exception:
                log.exception("compensation failed; needs manual repair")

def book_trip(req) -> Trip:
    saga = Saga()
    try:
        flight = saga.step(lambda: book_flight(req), lambda: cancel_flight(flight))
        hotel  = saga.step(lambda: book_hotel(req),  lambda: cancel_hotel(hotel))
        car    = saga.step(lambda: book_car(req),    lambda: cancel_car(car))
        return Trip(flight, hotel, car)
    except Exception:
        saga.compensate()           # unwind whatever succeeded
        raise
```

{{< mermaid >}}
sequenceDiagram
    participant O as Orchestrator
    participant F as Flight
    participant H as Hotel
    participant Ca as Car
    O->>F: book
    F-->>O: ok
    O->>H: book
    H-->>O: ok
    O->>Ca: book
    Ca-->>O: FAIL
    O->>H: cancel (compensate)
    O->>F: cancel (compensate)
{{< /mermaid >}}

Modern durable-execution engines such as Temporal and AWS Step Functions do the saga's bookkeeping (state, retries, compensation) for you, so you write the steps and the framework guarantees that the workflow survives crashes.

## Part V: Asynchronous Processing

The moment an operation takes longer than a user will wait, or must survive the failure of whatever started it, it belongs off the request path.

### 32. Queues decouple and absorb bursts

A queue sits between a producer and a pool of consumers and does two jobs. It smooths bursts, so that a spike of 1,000 requests against a system that handles 200 a second gets queued rather than dropped. And it decouples, so that producer and consumer scale, deploy and fail independently. A word of warning, though: never put a queue in a synchronous, low-latency path, or you will all but guarantee that you blow the latency budget.

{{< mermaid >}}
flowchart LR
    P[Producers] --> Q[[Queue]]
    Q --> W1[Worker]
    Q --> W2[Worker]
    Q --> W3[Worker]
    W1 --> DB[(Store)]
    W2 --> DB
    W3 --> DB
{{< /mermaid >}}

### 33. Async worker pools for long-running tasks

Video encoding, report generation, bulk email: anything that takes more than a few seconds. The web tier validates the request, enqueues a job and returns a job ID in milliseconds, while a separate fleet of workers drains the queue and does the heavy lifting. The user polls for the result or has it pushed to them, and the web and worker tiers now scale on different signals.

```go
func runPool(jobs <-chan Job, workers int) {
    var wg sync.WaitGroup
    for i := 0; i < workers; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {   // ranges until the channel is closed
                if err := process(job); err != nil {
                    log.Printf("job %s failed: %v", job.ID, err)
                }
            }
        }()
    }
    wg.Wait()
}
```

### 34. Dead letter queues

Some messages can never succeed (malformed payloads, references to rows that have since been deleted). Retried forever, such a "poison" message blocks the queue and burns compute. After a bounded number of attempts, route it to a dead letter queue, a side channel where failed messages wait for inspection instead of jamming the main flow. The DLQ also turns out to be your best debugging surface, since it tells you exactly what your consumers can't handle.

### 35. Backpressure and load shedding

A queue makes it *easy* to accept more work than you can finish, and the backlog simply grows until the system falls over. A queue doesn't add capacity; it hides the lack of it. Backpressure pushes the limit back to the producer, so that when you're full you reject or slow new work rather than accept an unbounded backlog. Shedding load deliberately keeps the system alive to serve the load it *can* handle.

```go
sem := make(chan struct{}, maxInFlight)   // bounded concurrency

func handle(req Request) error {
    select {
    case sem <- struct{}{}:               // got a slot
        defer func() { <-sem }()
        return process(req)
    default:
        return ErrOverloaded              // shed rather than queue unboundedly
    }
}
```

### 36. Batch and coalesce writes

Per-operation overhead (a round trip, an fsync, an index update) dominates when operations are small and frequent. Buffer them and flush in batches; one insert of 500 rows beats 500 single inserts by a wide margin. Flush on *either* a size threshold or a time limit, so that a trickle of traffic doesn't sit in the buffer forever.

```go
func batcher(in <-chan Item, flush func([]Item), maxSize int, maxWait time.Duration) {
    buf := make([]Item, 0, maxSize)
    tick := time.NewTicker(maxWait)
    defer tick.Stop()
    for {
        select {
        case item, ok := <-in:
            if !ok {
                flush(buf)                 // channel closed: final flush
                return
            }
            if buf = append(buf, item); len(buf) >= maxSize {
                flush(buf)
                buf = buf[:0]              // size trigger
            }
        case <-tick.C:
            if len(buf) > 0 {
                flush(buf)
                buf = buf[:0]              // time trigger
            }
        }
    }
}
```

### 37. Streams and event sourcing

A queue deletes a message once it's consumed. A stream (Kafka, Kinesis) is an append-only, replayable log that keeps events for a configured window, so several independent consumer groups can read the same events and a new consumer can replay history from the beginning. Event sourcing builds on this: rather than storing current state, you store the ordered sequence of events that produced it and derive the state by replaying them. You get a perfect audit trail and time-travel debugging for free, and the price is that "current state" becomes a computed projection.

```python
def replay(events: list[dict]) -> Account:
    account = Account(balance=0)
    for e in events:                       # events are the source of truth
        match e["type"]:
            case "deposited":
                account.balance += e["amount"]
            case "withdrawn":
                account.balance -= e["amount"]
            case "frozen":
                account.frozen = True
    return account
```

{{< mermaid >}}
flowchart LR
    P[Producer] --> Log[(Append-only log)]
    Log --> G1[Consumer group: dashboard]
    Log --> G2[Consumer group: warehouse]
    Log --> G3[Consumer group: fraud checks]
{{< /mermaid >}}

### 38. Publish/subscribe fan-out

When one event must reach many independent consumers (a new message notifying every device in a chat, a price change reaching everyone watching it), pub/sub decouples the publisher from a set of subscribers that is unknown and always changing. The publisher emits to a topic, and subscribers register interest and receive independently. It's the backbone of notifications, cache-invalidation broadcasts and real-time fan-out.

### 39. The transactional outbox

Here is a trap I suspect most of us have fallen into at least once. Your handler writes to the database *and* publishes an event. If it writes and then crashes before publishing, the event is lost and downstream state diverges, and you can't commit a database transaction and a message broker atomically. The outbox pattern makes it atomic anyway, by writing the event into an `outbox` table *in the same transaction* as the business change. A separate relay polls the table (or tails it with CDC), publishes, and marks the rows sent. An event can be published twice but never lost, so consumers must be idempotent (#29).

```sql
BEGIN;
  INSERT INTO orders (id, user_id, total) VALUES ($1, $2, $3);
  INSERT INTO outbox (id, topic, payload)
       VALUES ($4, 'order.created', $5);   -- same transaction as the order
COMMIT;
-- A relay process publishes unsent outbox rows, then marks them sent.
```

### 40. Exactly-once is idempotency plus dedup

True exactly-once delivery is, in the general case, impossible; what you actually build is *effectively once* processing. Combine at-least-once delivery (the broker's default) with idempotent consumers by attaching a unique ID to each message, tracking the IDs you've processed, and skipping duplicates. The message may arrive twice, but its *effect* happens once. This is why #29 and #39 keep reappearing: idempotency is what holds up the entire asynchronous stack.

## Part VI: Real-Time Delivery

This part is about pushing data *to* the client the moment it changes, without the client having to ask.

### 41. Climb the realtime ladder only as far as you must

There's a ladder here of increasing power and complexity, and most systems stop well short of the top. Short polling (asking every few seconds) is trivial and often enough. Long polling holds the request open until there's data, which cuts out the empty round trips. Server-Sent Events give you a persistent one-way stream from server to client over plain HTTP, perfect for live scores, notifications and progress bars. WebSockets add full two-way messaging for chat and collaborative editing. Every rung adds the complexity of stateful connections, so climb only when the rung below has genuinely failed you.

```go
func streamUpdates(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    flusher := w.(http.Flusher)

    events := subscribe(r.Context())      // channel fed by pub/sub
    for {
        select {
        case <-r.Context().Done():        // client disconnected
            return
        case ev := <-events:
            fmt.Fprintf(w, "data: %s\n\n", ev.JSON())  // SSE wire format
            flusher.Flush()               // push immediately
        }
    }
}
```

### 42. Route stateful connections deliberately

SSE and WebSocket connections are *stateful*: a user is pinned to the one server holding their socket. So how does an event generated on server B reach a user connected to server A? There are two standard answers. You can put a pub/sub layer (Redis, a broker) behind the connection servers, so that any server publishes and every server delivers to its local sockets. Or you can keep a registry mapping each user to a server and route each event to the right one. Because the connections are stateful, front them with an L4 load balancer (#2) rather than L7.

{{< mermaid >}}
flowchart TB
    U1[User A socket] --- SA[WS Server A]
    U2[User B socket] --- SB[WS Server B]
    SA <--> PS[(Pub/Sub)]
    SB <--> PS
    Note[Event from A's server reaches B's socket via Pub/Sub]
{{< /mermaid >}}

### 43. Push versus pull fan-out, and the celebrity problem

When a user posts, do you push the post into every follower's precomputed feed (fan-out on write), or pull it in by gathering posts from followed accounts when the feed is read (fan-out on read)? Pushing makes reads cheap and writes expensive, which is fine until someone with 100M followers posts and you have to write 100M feed entries. Pulling makes writes cheap and reads expensive. The answer in production is a hybrid: push for ordinary users and pull for celebrities, merging their posts in at read time. Recognizing that no single technique covers both the median and the tail is, to my mind, the mark of a senior engineer.

### 44. Rate limiting

Rate limiting protects a service from abuse, and from itself. The token bucket is the workhorse: a bucket refills at a fixed rate up to some capacity, each request spends a token, and an empty bucket rejects. It allows short bursts (up to the capacity) while bounding the sustained rate, which is usually just what you want. Sliding-window counters are the main alternative when you need a strict rolling limit.

```go
type TokenBucket struct {
    mu       sync.Mutex
    tokens   float64
    capacity float64
    rate     float64      // tokens per second
    last     time.Time
}

func (b *TokenBucket) Allow() bool {
    b.mu.Lock()
    defer b.mu.Unlock()
    now := time.Now()
    // Refill for the elapsed time, capped at capacity.
    b.tokens = math.Min(b.capacity, b.tokens+now.Sub(b.last).Seconds()*b.rate)
    b.last = now
    if b.tokens >= 1 {
        b.tokens--
        return true
    }
    return false          // rate exceeded -> 429
}
```

## Part VII: Resilience

Everything so far has assumed the happy path. This part is about what keeps the system standing when the path is anything but.

### 45. Put a timeout on everything

The default timeout for most network clients is "forever," and forever is how long a hung dependency will hold your thread, your connection and eventually your entire thread pool. Every outbound call (database, cache, RPC, HTTP) should get an explicit deadline scoped to its context. A request that can't finish within its budget should fail fast so that its resources go back to the pool, rather than piling up into a cascading collapse.

```go
ctx, cancel := context.WithTimeout(r.Context(), 200*time.Millisecond)
defer cancel()
resp, err := client.Fetch(ctx, id)   // returns promptly if the deadline passes
```

### 46. Retry with exponential backoff and jitter

Transient failures (a blip, a brief overload) deserve a retry. But naive immediate retries, and especially retries *synchronized* across many clients, produce a retry storm that turns a hiccup into an outage. Back off exponentially, and add jitter (randomness) so that clients don't all retry in lockstep. Retry only idempotent operations, and cap the number of attempts.

```python
import random, time

def with_retry(fn, attempts=5, base=0.1, cap=10.0):
    for attempt in range(attempts):
        try:
            return fn()
        except TransientError:
            if attempt == attempts - 1:
                raise
            # Full jitter: sleep a random amount in [0, exponential backoff].
            time.sleep(random.uniform(0, min(cap, base * 2 ** attempt)))
```

### 47. Circuit breakers

Retrying a dependency that is *down* only piles more load onto something that can't take it, while tying up your own resources in waiting. A circuit breaker watches the failure rate and, once it crosses a threshold, *trips open*, failing calls instantly for a cooldown period instead of attempting them. After the cooldown it goes *half-open* and lets a single trial through; if that succeeds it closes, and if it fails it opens again. It gives the struggling dependency room to recover and keeps your own callers responsive.

```go
type Breaker struct {
    mu        sync.Mutex
    state     State         // Closed, Open, HalfOpen
    failures  int
    threshold int
    openUntil time.Time
    cooldown  time.Duration
}

func (b *Breaker) Call(fn func() error) error {
    b.mu.Lock()
    if b.state == Open {
        if time.Now().Before(b.openUntil) {
            b.mu.Unlock()
            return ErrCircuitOpen          // fail fast, don't even try
        }
        b.state = HalfOpen                 // cooldown elapsed: allow one trial
    }
    b.mu.Unlock()

    err := fn()

    b.mu.Lock()
    defer b.mu.Unlock()
    if err != nil {
        b.failures++
        if b.state == HalfOpen || b.failures >= b.threshold {
            b.state, b.openUntil = Open, time.Now().Add(b.cooldown)
        }
        return err
    }
    b.failures, b.state = 0, Closed        // recovered
    return nil
}
```

{{< mermaid >}}
stateDiagram-v2
    [*] --> Closed
    Closed --> Open: failures >= threshold
    Open --> HalfOpen: cooldown elapsed
    HalfOpen --> Closed: trial succeeds
    HalfOpen --> Open: trial fails
{{< /mermaid >}}

### 48. Bulkheads

The name comes from a ship's hull, which is divided into watertight compartments so that one breach doesn't sink the vessel. In software, you isolate resources per dependency (a separate connection pool or thread pool for each one downstream), so that when one dependency hangs it exhausts only *its* pool and the rest of the system keeps serving. Without bulkheads, one slow dependency saturates a shared pool and takes down everything that shares it.

### 49. Graceful degradation

When a non-critical dependency fails, degrade the feature rather than the whole request. Is the recommendations service down? Serve a generic list. Can't reach the live inventory count? Show "in stock" from the cache, with a disclaimer. The pattern is a fallback: catch the failure, return a cached or default value, and keep the core path alive. A partial answer usually beats an error page.

```python
def get_recommendations(user_id: str) -> list[Item]:
    try:
        return recommender.fetch(user_id, timeout=0.1)
    except (Timeout, ServiceError):
        return popular_items_cached()      # degrade, don't fail the page
```

### 50. Know your numbers, then measure everything

Every decision above hinges on quantities, and most premature scaling comes from carrying numbers from 2010 around in your head. Modern hardware is faster than instinct suggests. A tuned relational primary handles tens of thousands of transactions a second and terabytes of data, a single Redis node does hundreds of thousands of operations a second, and an app server can hold something like 100K concurrent connections. Anchor yourself on a few latency facts, and do the arithmetic *when a decision depends on it* rather than as a ritual up front.

| Operation | Order of magnitude |
| --- | --- |
| L1 / L2 cache reference | ~1 ns |
| Main memory reference | ~100 ns |
| SSD random read | ~100 µs |
| Datacenter round trip | ~0.5 ms |
| Redis GET (in-DC) | ~1 ms |
| Database query (indexed, cached) | ~1–5 ms |
| Disk seek (spinning) | ~10 ms |
| NY ↔ London round trip | ~80 ms |

The numbers tell you *whether* to reach for a technique; observability tells you *when*. You can't operate what you can't see, so instrument the three pillars from day one: metrics (rates, errors and durations, the RED method), traces (one request's path across services) and structured logs (queryable, and correlated by request ID). If there is a single thread running through this whole post, it's that every technique here has a *trigger condition*, and you can only detect the trigger if you've been measuring. Is the cache hit rate falling below 80%? Is consumer lag climbing? Is p99 crossing the SLA? Those are the signals that tell you which of the other forty-nine techniques to reach for next.

## Closing

Fifty techniques, then, and one meta-technique: name the tradeoff before you deploy the tool. Sharding buys write throughput and charges you cross-shard queries. Caching buys latency and charges you invalidation. A queue buys tolerance for bursts and charges you a latency budget and a backpressure problem. Eventual consistency buys availability and charges you read-your-writes bugs. None of these is free, and the engineer who can state the price out loud (before the incident, that is, and not during the post-mortem) is the one you want designing the system.

If you want the interview-oriented version of this material, with the failure modes interviewers like to probe and worked breakdowns of problems, <a href="https://www.hellointerview.com/learn/system-design" target="_blank" rel="noopener noreferrer">HelloInterview's *System Design in a Hurry*</a> is the best free-to-start resource I've found, and it's the backbone this post is built on. Learn the technique first. Then comes the harder part, which is learning the moment.
