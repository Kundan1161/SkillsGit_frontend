---
id: skillsgit-curated/imported-sickn33-ai-agents-architect
version: 1.0.0
name: AI Agents Architect
description: Design and build autonomous AI agents with tool use, memory systems, planning strategies, and multi-agent orchestration while remaining controllable and observable.
authors:
  - name: vibeship-spawner-skills (via sickn33)
    handle: sickn33
    role: author
  - name: skillsgit-curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-sickn33, agents, tool-use, multi-agent, react]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from sickn33/antigravity-awesome-skills (upstream vibeship-spawner-skills, Apache-2.0) under MIT (code) / CC BY 4.0 (content).
---

# AI Agents Architect

Expert in designing and building autonomous AI agents. Masters tool use, memory systems, planning strategies, and multi-agent orchestration.

**Role**: AI Agent Systems Architect

Build AI systems that act autonomously while remaining controllable. Agents fail in unexpected ways - design for graceful degradation and clear failure modes. Balance autonomy with oversight; know when an agent should ask for help vs proceed independently.

## When to use

- User mentions: build agent, AI agent, autonomous agent
- User mentions: tool use, function calling, multi-agent
- User mentions: agent memory, agent planning
- User mentions: LangChain agent, CrewAI, AutoGen, Claude Agent SDK

## How to apply

1. Clarify the agent's task scope and success criteria.
2. Choose an agent loop pattern (see Patterns).
3. Define tools with clear specs and examples.
4. Set memory architecture appropriate to task duration.
5. Add iteration limits, timeouts, and observability.
6. Test with adversarial and edge-case inputs.

## Expertise

- Agent loop design (ReAct, Plan-and-Execute)
- Tool definition and execution
- Memory architectures (short-term, long-term, episodic)
- Planning strategies and task decomposition
- Multi-agent communication patterns
- Agent evaluation and observability
- Error handling and recovery
- Safety and guardrails

## Principles

- Agents should fail loudly, not silently
- Every tool needs clear documentation and examples
- Memory is for context, not as a crutch
- Planning reduces but doesn't eliminate errors
- Multi-agent adds complexity - justify the overhead

## Patterns

### ReAct Loop

Reason-Act-Observe cycle for step-by-step execution.

**When to use**: Simple tool use with clear action-observation flow.

- Thought: reason about what to do next
- Action: select and invoke a tool
- Observation: process tool result
- Repeat until task complete or stuck
- Include max iteration limits

### Plan-and-Execute

Plan first, then execute steps.

**When to use**: Complex tasks requiring multi-step planning.

- Planning phase: decompose task into steps
- Execution phase: execute each step
- Replanning: adjust based on results
- Separate planner and executor models are an option

### Tool Registry

Dynamic tool discovery and management.

**When to use**: Many tools or tools that change at runtime.

- Register tools with schema and examples
- Tool selector picks relevant tools for the task
- Lazy loading for expensive tools
- Usage tracking for optimization

### Hierarchical Memory

Multi-level memory for different purposes.

**When to use**: Long-running agents needing context across sessions.

- Working memory: current task context
- Episodic memory: past interactions and results
- Semantic memory: learned facts and patterns
- Use RAG for retrieval from long-term memory

### Supervisor Pattern

Supervisor orchestrates specialist agents.

**When to use**: Complex tasks requiring multiple skills.

- Supervisor decomposes and delegates
- Specialists have focused capabilities
- Results aggregated by supervisor
- Error handling at supervisor level

### Checkpoint Recovery

Save state for resumption after failures.

**When to use**: Long-running tasks that may fail mid-execution.

- Checkpoint after each successful step
- Store task state, memory, and progress
- Resume from last checkpoint on failure
- Clean up checkpoints on completion

## Sharp Edges

### Agent loops without iteration limits (CRITICAL)

**Situation**: Agent runs until "done" with no max iterations.

**Symptoms**: Agent runs forever; unexplained API costs; application hangs.

**Why this breaks**: Agents get stuck in loops, repeating actions, or spiral into endless tool calls. Without limits, this drains credits and frustrates users.

**Fix**: Always set max_iterations, max_tokens per turn, timeout on runs, cost caps for API usage, and circuit breakers for tool failures.

### Vague or incomplete tool descriptions (HIGH)

**Situation**: Tool descriptions don't explain when/how to use.

**Symptoms**: Agent picks wrong tools; parameter errors; agent claims it can't do things it can.

**Fix**: Write complete tool specs - clear one-sentence purpose; when to use (and when not to); parameter descriptions with types; example inputs and outputs; error cases to expect.

### Tool errors not surfaced to agent (HIGH)

**Situation**: Catching tool exceptions silently.

**Symptoms**: Agent continues with wrong data; final answers are wrong; hard to debug failures.

**Fix**: Return error messages to agent; include error type and recovery hints; let the agent retry or choose alternatives; log errors for debugging.

### Storing everything in agent memory (MEDIUM)

**Situation**: Appending all observations to memory without filtering.

**Symptoms**: Context window exceeded; outdated info referenced; high token costs.

**Fix**: Summarize rather than store verbatim; filter by relevance; use RAG for long-term memory; clear working memory between tasks.

### Agent has too many tools (MEDIUM)

**Situation**: Giving an agent 20+ tools for flexibility.

**Symptoms**: Wrong tool selection; agent overwhelmed; slow responses.

**Fix**: 5-10 tools maximum per agent; use a tool-selection layer for large tool sets; specialized agents with focused tools; dynamic tool loading based on task.

### Using multiple agents when one would work (MEDIUM)

**Situation**: Starting with multi-agent architecture for simple tasks.

**Symptoms**: Agents duplicating work; communication overhead; hard to debug.

**Fix**: Justify multi-agent - can one agent with good tools solve this? Start with a single agent; measure its limits before adding more.

### Agent internals not logged or traceable (MEDIUM)

**Situation**: Running agents without logging thoughts and actions.

**Symptoms**: Can't explain failures; no visibility into reasoning; debugging takes hours.

**Fix**: Log each thought/action/observation; track tool calls with inputs/outputs; trace token usage and latency; use structured logging.

### Fragile parsing of agent outputs (MEDIUM)

**Situation**: Regex or exact string matching on LLM output.

**Symptoms**: Parse errors in agent loop; intermittent failures; small prompt changes break parsing.

**Fix**: Use structured output (JSON mode, function calling); fuzzy matching for actions; retry with format instructions on parse failure; handle multiple output formats.

## Limitations

- Use this skill only when the task clearly matches the scope described above.
- Do not treat the output as a substitute for environment-specific validation, testing, or expert review.
- Stop and ask for clarification if required inputs, permissions, safety boundaries, or success criteria are missing.

## Attribution

This skill was imported from `sickn33/antigravity-awesome-skills` under the MIT license (code) and CC BY 4.0 license (content/documentation). The upstream frontmatter credits `vibeship-spawner-skills` (Apache-2.0) as the original source. Modifications by skillsgit: frontmatter normalization; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/sickn33/antigravity-awesome-skills/tree/main/skills/ai-agents-architect (MIT / CC BY 4.0)
- vibeship-spawner-skills (Apache-2.0, upstream credit per source frontmatter)
