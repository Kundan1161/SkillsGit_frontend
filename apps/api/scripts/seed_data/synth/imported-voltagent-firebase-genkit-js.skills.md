---
id: skillsgit-curated/imported-voltagent-firebase-genkit-js
version: 1.0.0
name: Developing with Genkit JS
description: Build AI-powered apps with Firebase Genkit (JavaScript/TypeScript) — initialization, flows, generate calls, plugins, and the Genkit CLI for docs lookup.
authors:
  - name: Firebase
    handle: firebase
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, firebase, genkit, ai-flows, javascript, typescript]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [genkit, firebase genkit, ai flow, genkit js, defineflow]
example_invocations:
  - Build a Genkit flow that summarizes incoming emails
  - Initialize Genkit with Google AI and a custom plugin
  - Look up Genkit docs via the CLI
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under Apache-2.0.
---

# Developing Genkit JS

## When to use

Use this skill when building AI-powered apps with Firebase Genkit (JavaScript/TypeScript) — defining flows, calling models, wiring plugins, and looking up the current API surface.

## How to apply

> Genkit recently went through a major breaking API change. Your knowledge is outdated.

Treat internal knowledge as unreliable. Use the Genkit CLI (`genkit docs:search`, `genkit docs:read`, `genkit docs:list`) for authoritative, current information before writing or reviewing code.

## Prerequisites

- Minimum CLI version: **1.29.0**. Verify with `genkit --version`.

## Essential Protocols

1. **Error handling** — Always consult the **Common Errors** reference first. This protocol is non-negotiable.
2. **Provider selection** — Default to **Google AI** if the user has not specified a provider.
3. **Documentation lookup** — Use `genkit docs:search`, `genkit docs:read`, and `genkit docs:list` commands for current API references.

## Hello World

```ts
import { genkit } from 'genkit';
import { googleAI } from '@genkit-ai/google-genai';

const ai = genkit({
  plugins: [googleAI()],
});

export const summarize = ai.defineFlow(
  { name: 'summarize', inputSchema: { text: 'string' } },
  async ({ text }) => {
    const result = await ai.generate({
      model: 'googleai/gemini-1.5-flash',
      prompt: `Summarize: ${text}`,
    });
    return result.text;
  }
);
```

## Available References (in source repo)

- Best Practices
- Common Errors (lists deprecated APIs)
- Setup Guide
- CLI Reference
- Examples

## Reminder

Because of the recent breaking changes, do not rely on pre-trained Genkit knowledge. Always confirm signatures and import paths via `genkit docs:read`.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `firebase/skills` repository under the Apache-2.0 license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/firebase/skills/tree/main/skills/developing-genkit-js (Apache-2.0)
