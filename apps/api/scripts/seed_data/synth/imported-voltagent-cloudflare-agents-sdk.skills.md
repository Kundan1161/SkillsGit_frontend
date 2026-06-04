---
id: skillsgit-curated/imported-voltagent-cloudflare-agents-sdk
version: 1.0.0
name: Cloudflare Agents SDK
description: Build AI agents on Cloudflare Workers using the Agents SDK — stateful agents, durable workflows, real-time WebSocket apps, scheduled tasks, MCP servers, and chat applications.
authors:
  - name: Cloudflare
    handle: cloudflare
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, cloudflare, workers, agents, mcp, durable-objects]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [cloudflare agents, agents sdk, workers agent, durable object agent, mcp server, ai chat agent, agent workflow]
example_invocations:
  - Build a stateful chat agent on Cloudflare Workers using the Agents SDK
  - Set up an MCP server with McpAgent and OAuth
  - Add scheduled tasks and durable workflows to my agent
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Cloudflare Agents SDK

Your knowledge of the Agents SDK may be outdated. **Prefer retrieval over pre-training** for any Agents SDK task.

## When to use

Use this skill when creating stateful agents on Cloudflare Workers, building durable workflows, real-time WebSocket apps, scheduled tasks, MCP servers, chat applications, voice agents, or browser automation. The Agents SDK covers the `Agent` class, state management, callable RPC, Workflows, durable execution, queues, retries, observability, and React hooks.

## How to apply

Always retrieve current Cloudflare docs before writing code — APIs evolve quickly. Use the retrieval table below to find authoritative sources, then follow the configuration, agent class pattern, routing, and core APIs shown here.

## Retrieval Sources

Cloudflare docs: https://developers.cloudflare.com/agents/

| Topic | Docs URL | Use for |
|-------|----------|---------|
| Getting started | [Quick start](https://developers.cloudflare.com/agents/getting-started/quick-start/) | First agent, project setup |
| Adding to existing project | [Add to existing project](https://developers.cloudflare.com/agents/getting-started/add-to-existing-project/) | Install into existing Workers app |
| Configuration | [Configuration](https://developers.cloudflare.com/agents/api-reference/configuration/) | `wrangler.jsonc`, bindings, assets, deployment |
| Agent class | [Agents API](https://developers.cloudflare.com/agents/api-reference/agents-api/) | Agent lifecycle, patterns, pitfalls |
| State | [Store and sync state](https://developers.cloudflare.com/agents/api-reference/store-and-sync-state/) | `setState`, `validateStateChange`, persistence |
| Routing | [Routing](https://developers.cloudflare.com/agents/api-reference/routing/) | URL patterns, `routeAgentRequest` |
| Callable methods | [Callable methods](https://developers.cloudflare.com/agents/api-reference/callable-methods/) | `@callable`, RPC, streaming, timeouts |
| Scheduling | [Schedule tasks](https://developers.cloudflare.com/agents/api-reference/schedule-tasks/) | `schedule()`, `scheduleEvery()`, cron |
| Workflows | [Run workflows](https://developers.cloudflare.com/agents/api-reference/run-workflows/) | `AgentWorkflow`, durable multi-step tasks |
| HTTP/WebSockets | [WebSockets](https://developers.cloudflare.com/agents/api-reference/websockets/) | Lifecycle hooks, hibernation |
| Chat agents | [Chat agents](https://developers.cloudflare.com/agents/api-reference/chat-agents/) | `AIChatAgent`, streaming, tools, persistence |
| Client SDK | [Client SDK](https://developers.cloudflare.com/agents/api-reference/client-sdk/) | `useAgent`, `useAgentChat`, React hooks |
| MCP client | [MCP client](https://developers.cloudflare.com/agents/api-reference/mcp-client-api/) | Connecting to MCP servers |
| MCP server | [MCP server](https://developers.cloudflare.com/agents/api-reference/mcp-agent-api/) | Building MCP servers with `McpAgent` |
| Securing MCP servers | [Securing MCP](https://developers.cloudflare.com/agents/api-reference/securing-mcp-servers/) | OAuth, proxy MCP, hardening |
| Human-in-the-loop | [Human-in-the-loop](https://developers.cloudflare.com/agents/concepts/human-in-the-loop/) | Approval flows, `needsApproval`, workflows |
| Durable execution | [Durable execution](https://developers.cloudflare.com/agents/api-reference/durable-execution/) | `runFiber()`, `stash()`, surviving DO eviction |
| Retries | [Retries](https://developers.cloudflare.com/agents/api-reference/retries/) | `this.retry()`, backoff/jitter |
| Observability | [Observability](https://developers.cloudflare.com/agents/api-reference/observability/) | Diagnostics-channel events |

## Capabilities

The Agents SDK provides:

- **Persistent state** — SQLite-backed, auto-synced to clients via `setState`
- **Callable RPC** — `@callable()` methods invoked over WebSocket
- **Scheduling** — One-time, recurring (`scheduleEvery`), and cron tasks
- **Workflows** — Durable multi-step background processing via `AgentWorkflow`
- **Durable execution** — `runFiber()` / `stash()` for work that survives DO eviction
- **Queue** — Built-in FIFO queue with retries via `queue()`
- **MCP integration** — Connect to MCP servers or build your own with `McpAgent`
- **Email handling** — Receive and reply to emails with secure routing
- **Streaming chat** — `AIChatAgent` with resumable streams, message persistence, tools
- **React hooks** — `useAgent`, `useAgentChat` for client apps
- **Observability** — `diagnostics_channel` events for state, RPC, schedule, lifecycle

## FIRST: Verify Installation

```bash
npm ls agents  # Should show agents package
```

If not installed:
```bash
npm install agents
```

For chat agents:
```bash
npm install agents @cloudflare/ai-chat ai @ai-sdk/react
```

## Wrangler Configuration

```jsonc
{
  "compatibility_flags": ["nodejs_compat"],
  "durable_objects": {
    "bindings": [{ "name": "MyAgent", "class_name": "MyAgent" }]
  },
  "migrations": [{ "tag": "v1", "new_sqlite_classes": ["MyAgent"] }]
}
```

**Gotchas:**
- Do NOT enable `experimentalDecorators` in tsconfig (breaks `@callable`)
- Never edit old migrations — always add new tags
- Each agent class needs its own DO binding + migration entry
- Add `"ai": { "binding": "AI" }` for Workers AI

## Agent Class

```typescript
import { Agent, routeAgentRequest, callable } from "agents";

type State = { count: number };

export class Counter extends Agent<Env, State> {
  initialState = { count: 0 };

  validateStateChange(nextState: State, source: Connection | "server") {
    if (nextState.count < 0) throw new Error("Count cannot be negative");
  }

  onStateUpdate(state: State, source: Connection | "server") {
    console.log("State updated:", state);
  }

  @callable()
  increment() {
    this.setState({ count: this.state.count + 1 });
    return this.state.count;
  }
}

export default {
  fetch: (req, env) => routeAgentRequest(req, env) ?? new Response("Not found", { status: 404 })
};
```

## Routing

Requests route to `/agents/{agent-name}/{instance-name}`:

| Class | URL |
|-------|-----|
| `Counter` | `/agents/counter/user-123` |
| `ChatRoom` | `/agents/chat-room/lobby` |

Client: `useAgent({ agent: "Counter", name: "user-123" })`

Custom routing: use `getAgentByName(env.MyAgent, "instance-id")` then `agent.fetch(request)`.

## Core APIs

| Task | API |
|------|-----|
| Read state | `this.state.count` |
| Write state | `this.setState({ count: 1 })` |
| SQL query | `` this.sql`SELECT * FROM users WHERE id = ${id}` `` |
| Schedule (delay) | `await this.schedule(60, "task", payload)` |
| Schedule (cron) | `await this.schedule("0 * * * *", "task", payload)` |
| Schedule (interval) | `await this.scheduleEvery(30, "poll")` |
| RPC method | `@callable() myMethod() { ... }` |
| Streaming RPC | `@callable({ streaming: true }) stream(res) { ... }` |
| Start workflow | `await this.runWorkflow("ProcessingWorkflow", params)` |
| Durable fiber | `await this.runFiber("name", async (ctx) => { ... })` |
| Enqueue work | `this.queue("handler", payload)` |
| Retry with backoff | `await this.retry(fn, { maxAttempts: 5 })` |
| Broadcast to clients | `this.broadcast(message)` |
| Get connections | `this.getConnections(tag?)` |

## React Client

```tsx
import { useAgent } from "agents/react";

function App() {
  const [state, setLocalState] = useState({ count: 0 });

  const agent = useAgent({
    agent: "Counter",
    name: "my-instance",
    onStateUpdate: (newState) => setLocalState(newState),
    onIdentity: (name, agentType) => console.log(`Connected to ${name}`)
  });

  return (
    <button onClick={() => agent.setState({ count: state.count + 1 })}>
      Count: {state.count}
    </button>
  );
}
```

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `cloudflare/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/cloudflare/skills/tree/main/skills/agents-sdk (Apache-2.0)
