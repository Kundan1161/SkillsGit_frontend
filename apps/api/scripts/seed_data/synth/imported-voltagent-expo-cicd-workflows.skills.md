---
id: skillsgit-curated/imported-voltagent-expo-cicd-workflows
version: 1.0.0
name: EAS Workflows for Expo CI/CD
description: Understand and author EAS workflow YAML files for Expo projects — build pipelines, deployment automation, and pre-packaged jobs.
authors:
  - name: Expo
    handle: expo
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, expo, eas, ci-cd, workflows, automation]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [eas workflows, expo ci, .eas/workflows, eas pipeline, expo automation]
example_invocations:
  - Write an EAS workflow that builds and submits to TestFlight on tag push
  - Add PR preview deploys to my Expo workflow
  - Validate my .eas/workflows yaml against the schema
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under MIT.
---

# EAS Workflows Skill

Help developers write and edit EAS CI/CD workflow YAML files.

## When to use

Use this skill when the user asks about CI/CD or workflows in an Expo / EAS context, mentions `.eas/workflows/`, or wants help with EAS build pipelines and deployment automation.

## How to apply

Always fetch the current schema and syntax documentation before generating or validating workflow files. Validate the generated YAML against the schema and fix any reported errors before considering the work complete.

## Reference Documentation

Fetch these resources before generating or validating workflow files. Do not rely on memorized values; these resources evolve as new features are added.

1. **JSON Schema** — https://api.expo.dev/v2/workflows/schema
   - It is NECESSARY to fetch this schema
   - Source of truth for validation
   - All job types and their required/optional parameters
   - Trigger types and configurations
   - Runner types, VM images, and all enums

2. **Syntax Documentation** — https://raw.githubusercontent.com/expo/expo/refs/heads/main/docs/pages/eas/workflows/syntax.mdx
   - Overview of workflow YAML syntax
   - Examples and English explanations
   - Expression syntax and contexts

3. **Pre-packaged Jobs** — https://raw.githubusercontent.com/expo/expo/refs/heads/main/docs/pages/eas/workflows/pre-packaged-jobs.mdx
   - Documentation for supported pre-packaged job types
   - Job-specific parameters and outputs

## Workflow File Location

Workflows live in `.eas/workflows/*.yml` (or `.yaml`).

## Top-Level Structure

A workflow file has these top-level keys:

- `name` — Display name
- `on` — Triggers that start the workflow (at least one required)
- `jobs` — Job definitions (required)
- `defaults` — Shared defaults for all jobs
- `concurrency` — Control parallel workflow runs

Consult the schema for the full specification of each section.

## Expressions

Use `${{ }}` syntax for dynamic values. The schema defines available contexts:

- `github.*` — GitHub repo and event information
- `inputs.*` — Values from `workflow_dispatch` inputs
- `needs.*` — Outputs and status from dependent jobs
- `jobs.*` — Job outputs (alternative syntax)
- `steps.*` — Step outputs within custom jobs
- `workflow.*` — Workflow metadata

## Generating Workflows

When generating or editing workflows:

1. Fetch the schema to get current job types, parameters, and allowed values.
2. Validate that required fields are present for each job type.
3. Verify job references in `needs` and `after` exist.
4. Check that expressions reference valid contexts and outputs.
5. Ensure `if` conditions respect the schema's length constraints.

## Validation

After generating or editing a workflow file, validate against the schema. The Expo skills repo ships a validator under `scripts/`:

```sh
# Install deps if missing
[ -d "{baseDir}/scripts/node_modules" ] || npm install --prefix {baseDir}/scripts

node {baseDir}/scripts/validate.js <workflow.yml> [workflow2.yml ...]
```

The validator fetches the latest schema and checks the YAML structure. Fix any reported errors.

## Answering Questions

When users ask about available options (job types, triggers, runner types), fetch the schema and derive the answer from it rather than relying on potentially outdated information.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `expo/skills` repository under the MIT license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-cicd-workflows (MIT)
