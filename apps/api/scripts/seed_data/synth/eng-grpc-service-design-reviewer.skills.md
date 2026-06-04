---
id: skillsgit-curated/grpc-service-design-reviewer
version: 1.0.0
name: gRPC Service Design Reviewer
description: Audit a gRPC service end to end — protobuf schema discipline, streaming choices, error mapping, deadlines, retries, interceptors, and generated-stub usage.
authors:
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: author
category: engineering
tags:
  - niche:grpc-design
  - protobuf
  - rpc-design
  - streaming
  - deadlines
  - retries
  - interceptors
  - schema-evolution
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gpt-4.1, gemini-1.5-pro]
  tools_required: [file_io]
  tools_optional: [web_search]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 7500
trigger_keywords:
  - grpc review
  - review my proto
  - grpc service design
  - protobuf schema review
  - protobuf breaking change
  - grpc streaming choice
  - grpc deadlines
  - grpc retries
  - grpc error mapping
  - grpc interceptor
  - unary vs streaming
  - grpc versioning
  - oneof abuse
  - grpc deprecation
  - grpc observability
example_invocations:
  - "Review my .proto file for an orders service before we publish it to client teams."
  - "Help me decide between server-streaming and a repeated unary response for a search endpoint."
  - "We're hitting deadline exceeded errors at p99 — review our gRPC client and server setup."
inputs:
  - name: proto_or_service
    type: text
    required: true
    description: The .proto definitions under review, or a prose description of the service surface, with rpc methods, message shapes, and known callers.
  - name: client_landscape
    type: text
    required: false
    description: Who calls this service — internal services on the same language, partner SDKs in many languages, mobile clients, web clients via gRPC-Web — and which generated stubs they consume.
  - name: latency_and_size_profile
    type: text
    required: false
    description: Tail latency budgets, expected message sizes, payload shapes (small JSON-like, large blobs), and whether long-lived streams are expected.
  - name: known_pain_points
    type: text
    required: false
    description: Specific complaints from production — deadline exceeded errors, message-too-large failures, version skew, ambiguous error codes, retry storms.
  - name: review_depth
    type: choice
    required: false
    description: How deep the review should go.
    choices: [schema-only, schema-and-runtime, full-including-rollout]
outputs:
  - name: review_report
    type: markdown
    description: Severity-ranked findings (blocker, major, minor, nit) across schema, runtime behavior, and operational concerns, each with an example fix.
  - name: proto_lint_findings
    type: markdown
    description: Per-method and per-message issues with naming, types, oneof use, well-known type adoption, deprecation, and forward-compatibility risk.
  - name: runtime_recommendations
    type: markdown
    description: Concrete defaults for deadlines, retries, message size limits, keepalive, interceptors, and observability that the reviewer recommends adopting.
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Initial release.
---

# gRPC Service Design Reviewer

## When to use

Use this skill when a team is about to publish a gRPC service, evolve an existing service, or chase down systemic issues that trace back to gRPC design choices. The output is a senior-reviewer pass that covers schema discipline, the choice of streaming versus unary, error and timeout discipline, and the operational glue that decides whether a gRPC system is pleasant or painful to run.

The skill is most valuable on these inputs:

- A first-cut `.proto` for a new service, before any client has shipped against it.
- A proposed change to an existing service that risks a wire-compatibility break.
- A service that works in development but melts in production at the tail (deadline exceeded, RST_STREAM, OOM, retry storms).
- A polyglot integration where stubs in different languages disagree about a corner of the contract.

Do not use this skill for:

- Pure REST or GraphQL APIs — those have their own conventions and a separate review skill.
- Non-protobuf RPC frameworks; while many ideas transfer, several recommendations here assume protobuf message evolution rules.
- Pure data modeling problems unrelated to the wire contract — those belong to the database or domain-model layer.

## Inputs

- `proto_or_service` (required) — The `.proto` text, or a prose description that names the service, the rpc methods, and the message shapes.
- `client_landscape` — Drives weight on backward compatibility, the strictness of naming conventions, and whether generated stubs across many languages need to be considered.
- `latency_and_size_profile` — Drives recommendations on streaming, message-size limits, deadlines, and chunking.
- `known_pain_points` — Steers the reviewer toward the live problems rather than running every check at uniform depth.
- `review_depth` — Bounds the scope so a quick lint pass does not balloon into a full operational audit when only schema review was requested.

## How to apply

Run the review in passes. Each pass produces findings; merge them into the final report at the end.

### 1. Frame the service

1.1. Restate the service in plain English: the noun (an `Orders` service, a `Payments` service), the verbs it offers, the callers, the data ownership boundary. Findings hang off this frame.

1.2. Identify the service style: command-style (each method mutates state), query-style (each method reads), event-style (server-streaming push), or mixed. Mixed services often hide design problems that splitting would expose.

1.3. Confirm the package path and namespace match the team's wider convention. A drifted package path is a smell that the service was carved off without coordination.

### 2. Schema-discipline pass

2.1. **Field numbers** — flag any reuse of a previously released field number. Once a field number has been on the wire in a released version, the number is burned. Reuse risks silently mismatched values on cross-version reads.

2.2. **Reserved fields and names** — confirm removed fields are entered into a `reserved` clause covering the old number and name. The reserved clause is the only thing that prevents accidental reuse in a future edit.

2.3. **Required-ness** — flag any attempt to mark fields as required in proto3 (the field rule was removed for good reason). Application-level required-ness is enforced in code with explicit checks; document those checks alongside the proto.

2.4. **Default values and presence** — for fields where "unset" must be distinguished from "set to default", flag the use of scalar fields and recommend the explicit presence form (wrapper messages or proto3 `optional`). A boolean field that ships as `false` is indistinguishable from "unset" without this discipline.

2.5. **Enums** — flag enums without an explicit zero value named `_UNSPECIFIED`. The zero value is what every receiver sees when the field is unset; the unspecified sentinel makes that case observable. Flag enums that lack an `_UNKNOWN` or open-set strategy for forward compatibility.

2.6. **Well-known types** — recommend `google.protobuf.Timestamp` for absolute times, `Duration` for spans, `Any` for genuinely polymorphic content (rarely), and the wrapper types (`StringValue`, `Int32Value`, etc.) only when explicit presence is required and a wrapper message is excessive. Flag custom timestamp formats, custom duration formats, and string-encoded numbers.

2.7. **Identifiers** — flag bare integer ids on cross-service boundaries. Prefer opaque string ids whose internal structure is hidden from callers. Flag id fields that mix tenant and entity scope without naming the scope (`user_id` vs `org_user_id`).

2.8. **Naming** — enforce the conventional case: `lower_snake_case` for fields, `PascalCase` for messages and services, `SCREAMING_SNAKE_CASE` for enum values. Flag plurals on repeated fields (`tags` not `tag_list`), suffixes that duplicate the type (`created_at_timestamp`), and Hungarian-style prefixes.

2.9. **Oneof discipline** — flag oneof groups used as a quasi-required selector across many alternatives; consider whether the operation is really several different operations that should be different rpcs. Oneof is correct for "exactly one of these payload shapes"; it is wrong for "do one of these operations".

2.10. **Map fields** — confirm map values are not themselves messages with high churn. Map deletion semantics are weak across versions; flag any caller that depends on the absence of a key as a strong signal.

2.11. **Deprecation** — confirm fields and methods being removed are first marked `deprecated = true` for at least one release. Flag immediate removal of any wire-visible element.

2.12. **Comments** — every public message and rpc should have a comment that survives codegen. The comment is the contract for callers reading the generated stub.

### 3. RPC-shape pass

3.1. **Unary vs streaming** — for each rpc, restate the access pattern. Unary is right when the request and response are bounded. Server-streaming is right for push, large response sets, or progress reporting. Client-streaming is right for ingest of unbounded inputs. Bidirectional streaming is right for long-lived interactive sessions (chat, telemetry). Flag streaming used purely to bypass a message-size limit; that is a chunking design and deserves its own framing.

3.2. **Message size** — flag any single-message payload that approaches the default 4 MB receive limit. Choose between chunked streaming, a content-addressable blob fetched separately, or compression (server-applied gzip with client opt-in).

3.3. **List endpoints** — flag `List*` rpcs without explicit pagination. Recommend page-token pagination with an opaque continuation token and a documented stable order; recommend a `page_size` field with a server-enforced upper bound and a documented default.

3.4. **Mutation endpoints** — flag mutating rpcs without an idempotency mechanism. For services that allow client retry, a client-provided idempotency key (a UUID per logical operation, validated server-side) is the cleanest pattern. Document the dedup window.

3.5. **Search and filter rpcs** — flag ad-hoc filter strings or stringly-typed query languages without a stable grammar. Either commit to a structured request message or commit to an explicit grammar (and version it).

3.6. **Empty messages** — flag rpcs that take or return `google.protobuf.Empty` if a future field is even slightly likely. A purpose-built request or response message future-proofs the surface at near-zero cost.

3.7. **Field masks** — for partial-update rpcs, recommend `google.protobuf.FieldMask` to specify exactly which fields the call intends to mutate. Flag PATCH-style endpoints that infer mutation from field presence; that pattern conflicts with proto3 default semantics for non-message fields.

### 4. Error-handling pass

4.1. **Status codes** — confirm the service maps domain errors to the canonical status codes (NOT_FOUND, ALREADY_EXISTS, INVALID_ARGUMENT, PERMISSION_DENIED, UNAUTHENTICATED, FAILED_PRECONDITION, ABORTED, OUT_OF_RANGE, UNIMPLEMENTED, INTERNAL, UNAVAILABLE, DEADLINE_EXCEEDED, RESOURCE_EXHAUSTED, CANCELLED, DATA_LOSS). Flag any use of OK with an error body — gRPC does not have that pattern; the status is the result.

4.2. **Retryability** — flag missing guidance for callers on which status codes are safe to retry. UNAVAILABLE and RESOURCE_EXHAUSTED are typically retryable with backoff; INTERNAL and ABORTED depend on context; INVALID_ARGUMENT and PERMISSION_DENIED are not.

4.3. **Error details** — confirm structured error details are attached for cases where the caller needs machine-readable context. Prefer `google.rpc.ErrorInfo`, `BadRequest`, `PreconditionFailure`, `QuotaFailure`, and `RetryInfo` over freeform error message strings.

4.4. **Sensitive content** — flag any error message that may include user input verbatim or backend stack details. Errors propagate through proxies, logs, and clients.

4.5. **Localization** — flag any attempt to localize error messages on the server. Server emits machine-readable codes; client localizes for display.

### 5. Timeouts, deadlines, and retries

5.1. **Deadlines** — every caller should set a deadline on every rpc. Servers should honor cancellation when the deadline is exceeded. Flag any client code that issues rpcs without a deadline; that is the most common cause of cascading hangs.

5.2. **Deadline propagation** — when service A calls service B, the deadline travels with the rpc. The downstream service must observe the same deadline (minus a budget for the work). Flag any boundary where the deadline is reset to a fresh value, because that hides backpressure.

5.3. **Retry policy** — for each rpc, decide whether retries are safe (idempotent operation or idempotency key present) and what backoff is appropriate. Recommend exponential backoff with full jitter, a maximum number of attempts, and a maximum total elapsed time bounded by the upstream deadline.

5.4. **Hedging** — for read-only rpcs where the tail latency matters more than extra load, consider hedged requests (send a second request after a short delay; take the first response). Flag hedging on non-idempotent rpcs.

5.5. **Service config** — recommend a method-level retry and timeout policy expressed in service config (declaratively) rather than scattered in client code. The declarative form survives codegen and is easier to audit.

### 6. Channel and connection pass

6.1. **Keepalive** — flag missing or aggressive keepalive settings. Servers must permit at least the keepalive interval the clients use, or connections die under load with confusing errors.

6.2. **Message size limits** — review the configured maximum receive and send sizes on both client and server. Mismatched limits cause asymmetric failures.

6.3. **Compression** — recommend per-method compression policy. Compression helps text-heavy payloads and hurts already-compressed binary payloads; do not apply globally without measurement.

6.4. **TLS** — flag any cross-trust-boundary call without TLS. Within a trusted mesh, mTLS plus deadline propagation is the common pattern.

6.5. **Load balancing** — confirm clients use a load balancer aware of gRPC's HTTP/2 multiplexing (per-call rather than per-connection). Round-robin over connections is wrong when one connection carries many calls.

### 7. Interceptor and middleware pass

7.1. **Logging interceptor** — confirm a request-scoped logger captures method, peer, deadline, response status, latency, and a trace id. Flag uncorrelated log lines that cannot be tied back to a single rpc.

7.2. **Tracing interceptor** — confirm propagation of distributed trace context across services. Without it, multi-service problems are invisible.

7.3. **Metrics interceptor** — confirm per-method counters and latency histograms with status code as a label. Aggregated-only metrics hide the methods that misbehave.

7.4. **Authn/authz interceptor** — confirm authentication happens at the interceptor boundary, not buried inside each handler. Authorization decisions belong adjacent to the domain operation but should consume the authenticated principal from the interceptor.

7.5. **Panic-recovery interceptor** — confirm a recovery interceptor maps panics or uncaught exceptions to `INTERNAL` with a logged correlation id. Do not leak stack traces to callers.

### 8. Schema evolution pass

8.1. Restate the wire-compatibility rules in the context of the proposed change. Adding a new field with a new number is safe. Removing a field is safe only if no caller uses it; the number must then be reserved. Renaming a field is wire-safe but breaks generated symbols in clients. Changing a field's type is generally unsafe.

8.2. Recommend a deprecation policy for fields and methods: mark deprecated, communicate to known callers, remove only after a documented quiet period.

8.3. For services with many client languages, recommend running a breaking-change detector against the previous published schema as part of CI.

8.4. Flag any branch that mutates the proto without a corresponding update to the generated stubs and to consumer SDKs.

### 9. Generated-stub usage

9.1. Confirm callers consume the language-idiomatic generated stub rather than hand-rolling a client. Hand-rolled clients drift from the contract.

9.2. Confirm the generated stub is regenerated in CI rather than checked in stale.

9.3. For streaming methods, confirm callers respect flow control. Unbounded reads from a server-streamed source cause memory pressure on slow consumers.

9.4. For client-streaming methods, confirm the sender closes the stream once input is exhausted. A forgotten close leaves the server waiting and the client wondering why.

### 10. Observability and rollout

10.1. Confirm health-check endpoints follow the standard gRPC health-check protocol so load balancers and orchestrators have a uniform signal.

10.2. Confirm reflection is enabled only where appropriate (developer tooling, internal mesh) and disabled on externally exposed endpoints.

10.3. For rollouts of breaking changes, recommend a parallel deployment with both old and new methods exposed during the transition. Migrate callers one at a time; retire the old methods after a documented window.

10.4. For services that fan out to many downstreams, recommend explicit circuit-breaker policies and per-downstream quotas to prevent cascading failure.

### 11. Emit the review

11.1. Lead with a verdict: ready, ready-with-fixes, or needs-rework. Bias toward strong language; ambiguous reviews are easy to ignore.

11.2. Group findings by severity (blocker, major, minor, nit) and by area (schema, rpc shape, errors, deadlines, channels, interceptors, evolution, stubs, observability). Each finding cites the method or message name, states the problem, and offers a specific replacement.

11.3. Include a small "what's good" section so the author can see which parts are healthy.

11.4. End with a checklist of the recommended defaults the team should encode in a service template so the next reviewer does not redo the same work.

### Decision rules and heuristics

- **Reserve every removed field number, always.** It is one line and prevents an entire class of silent bugs.
- **Default-zero is "unset".** Designs that depend on telling the two apart need explicit presence.
- **Empty messages are a future tax.** Spend a few bytes today.
- **Deadlines on every rpc.** Missing deadlines are the deadliest production issue gRPC services face.
- **Retries need idempotency.** A retry policy without an idempotency story is a duplicate-creation policy.
- **Status codes are the result.** Do not encode errors in OK responses.
- **Streaming is not a chunking workaround.** If the problem is large messages, design chunking explicitly.
- **One service does one thing.** Mixed command-query-event services hide rough seams.

### Edge cases

- **gRPC-Web clients** cannot consume client-streaming or bidirectional streaming. Flag any such method exposed to a web client without an alternative.
- **Long-lived streams** must survive proxy timeouts and load balancer idle limits. Recommend a heartbeat or periodic application-level message.
- **Binary blobs over rpc.** When the payload approaches several megabytes per call, recommend an object-store URL exchange instead.
- **Very high RPS, very small payloads.** Header overhead dominates; consider batching at the application level.
- **Cross-language number semantics.** Flag `int64` and `uint64` fields used by JavaScript clients without an explicit string-form fallback; the JS number type silently loses precision.
- **Polyglot enums.** Some languages map unknown enum values to the zero value and some to a special unknown; document the strategy.
- **Deprecation without telemetry.** Marking a field deprecated is half the work; instrument calls to it so the retirement date can be based on data.

## Outputs

- `review_report` — Severity-ranked findings across schema, runtime, and operational concerns with example fixes and a short "what's good" section.
- `proto_lint_findings` — Per-method and per-message issues focused on the schema discipline pass.
- `runtime_recommendations` — Concrete default values for deadlines, retries, message size, keepalive, interceptors, and observability that the reviewer would adopt as the service template.

## Examples

### Worked example

Input excerpt:

> Reviewing a new `Catalog` service. The `.proto` declares `SearchProducts`, `GetProduct`, `CreateProduct`, and a `WatchInventory` server-streaming method. Field 7 of `Product` was removed last month; the file does not mention it. `GetProduct` returns `google.protobuf.Empty` when the product is missing. `SearchProducts` accepts a `query` string and a `limit` int32. The error path returns OK with an `error_message` field in the response. Clients run in Go and TypeScript. No deadline policy is documented.

Expected findings sketch:

- Blocker: removed field 7 is not reserved; add `reserved 7;` and `reserved "old_name";`.
- Blocker: `GetProduct` returning Empty on missing — switch to returning the `Product` message and signal absence with `NOT_FOUND`.
- Blocker: error returned via OK with `error_message` — remove the field and return the appropriate status code; attach `google.rpc.ErrorInfo` for structured details.
- Major: `SearchProducts` has no pagination — add `page_size` (server-capped) and `page_token`.
- Major: `SearchProducts.query` is unstructured — either commit to a versioned grammar or convert to a structured filter message.
- Major: TypeScript clients consuming `int64` ids will lose precision — switch to string ids or add a string form.
- Major: no documented deadline policy — recommend method-level deadlines (200ms for `GetProduct`, 1s for `SearchProducts`, 30s for the streaming `WatchInventory` heartbeat interval).
- Minor: `Product` lacks comments on the public fields; add them so generated stubs are self-describing.
- Minor: `WatchInventory` should send a keepalive message at least every 30s so proxies do not idle-close the stream.
- Recommendation: add interceptors for logging, tracing, metrics, panic-recovery, and auth before publication.
- Recommendation: enable a breaking-change detector against the previous published schema in CI.

## Limitations

- The skill reviews design and recommended configuration; it does not run the service or measure its actual tail latency. Pair with a load test before high-RPS launches.
- Recommendations on retries and deadlines depend on the upstream/downstream call graph; the skill works from what the user describes.
- The skill does not produce regenerated stubs; that is a build-system task.
- For very large service surfaces (hundreds of rpcs), the schema pass is best run in sections to keep findings actionable.
- The skill assumes protobuf as the IDL. Other IDLs (FlatBuffers, Cap'n Proto) have different evolution rules.

## Sources reviewed

- https://github.com/grpc/grpc
- https://github.com/protocolbuffers/protobuf
- https://github.com/grpc-ecosystem/grpc-gateway
- https://github.com/bufbuild/buf
- https://github.com/googleapis/googleapis
- https://github.com/grpc/grpc-go
