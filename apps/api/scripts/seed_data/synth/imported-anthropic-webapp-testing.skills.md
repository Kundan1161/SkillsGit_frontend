---
id: skillsgit-curated/imported-anthropic-webapp-testing
version: 1.0.0
name: "Webapp Testing"
description: "Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs."
authors:
  - name: "Anthropic (original)"
    handle: anthropic
    role: author
  - name: "skillsgit Curated"
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-anthropics-skills, playwright, testing, browser-automation, e2e]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6]
  tools_required: []
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords:
  - webapp
  - testing
  - toolkit
  - interacting
  - local
  - applications
  - playwright
example_invocations:
  - "Use the webapp testing skill on this."
  - "Apply webapp testing guidance to my work."
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: "Imported from anthropics/skills under Apache-2.0."
---
## When to use

Use this skill when: Toolkit for interacting with and testing local web applications using Playwright. Supports verifying frontend functionality, debugging UI behavior, capturing browser screenshots, and viewing browser logs.

_Note: this section was added during import to satisfy the marketplace validator. The original Anthropic skill expresses its trigger conditions throughout the body below._

## How to apply

Follow the instructional content in the sections below. The original skill body (preserved verbatim) contains the step-by-step guidance. Read it top-to-bottom, treat any `## Overview` / introductory paragraphs as orientation, then execute the numbered or sub-headed procedures as written.

_Note: this section was added during import to satisfy the marketplace validator._

# Web Application Testing

To test local web applications, write native Python Playwright scripts.

**Helper Scripts Available**:
- `scripts/with_server.py` - Manages server lifecycle (supports multiple servers)

**Always run scripts with `--help` first** to see usage. DO NOT read the source until you try running the script first and find that a customized solution is abslutely necessary. These scripts can be very large and thus pollute your context window. They exist to be called directly as black-box scripts rather than ingested into your context window.

## Decision Tree: Choosing Your Approach

```
User task → Is it static HTML?
    ├─ Yes → Read HTML file directly to identify selectors
    │         ├─ Success → Write Playwright script using selectors
    │         └─ Fails/Incomplete → Treat as dynamic (below)
    │
    └─ No (dynamic webapp) → Is the server already running?
        ├─ No → Run: python scripts/with_server.py --help
        │        Then use the helper + write simplified Playwright script
        │
        └─ Yes → Reconnaissance-then-action:
            1. Navigate and wait for networkidle
            2. Take screenshot or inspect DOM
            3. Identify selectors from rendered state
            4. Execute actions with discovered selectors
```

## Example: Using with_server.py

To start a server, run `--help` first, then use the helper:

**Single server:**
```bash
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py
```

**Multiple servers (e.g., backend + frontend):**
```bash
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

To create an automation script, include only Playwright logic (servers are managed automatically):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # Always launch chromium in headless mode
    page = browser.new_page()
    page.goto('http://localhost:5173') # Server already running and ready
    page.wait_for_load_state('networkidle') # CRITICAL: Wait for JS to execute
    # ... your automation logic
    browser.close()
```

## Reconnaissance-Then-Action Pattern

1. **Inspect rendered DOM**:
   ```python
   page.screenshot(path='/tmp/inspect.png', full_page=True)
   content = page.content()
   page.locator('button').all()
   ```

2. **Identify selectors** from inspection results

3. **Execute actions** using discovered selectors

## Common Pitfall

❌ **Don't** inspect the DOM before waiting for `networkidle` on dynamic apps
✅ **Do** wait for `page.wait_for_load_state('networkidle')` before inspection

## Best Practices

- **Use bundled scripts as black boxes** - To accomplish a task, consider whether one of the scripts available in `scripts/` can help. These scripts handle common, complex workflows reliably without cluttering the context window. Use `--help` to see usage, then invoke directly. 
- Use `sync_playwright()` for synchronous scripts
- Always close the browser when done
- Use descriptive selectors: `text=`, `role=`, CSS selectors, or IDs
- Add appropriate waits: `page.wait_for_selector()` or `page.wait_for_timeout()`

## Reference Files

- **examples/** - Examples showing common patterns:
  - `element_discovery.py` - Discovering buttons, links, and inputs on a page
  - `static_html_automation.py` - Using file:// URLs for local HTML
  - `console_logging.py` - Capturing console logs during automation

## Attribution

This skill was imported from the public `anthropics/skills` repository under the Apache-2.0 license. Original content authored by Anthropic. Modifications by skillsgit: frontmatter normalization to fit marketplace spec, addition of attribution and sources sections. The original LICENSE and NOTICE files are preserved at the source repository.

## Sources reviewed
- https://github.com/anthropics/skills/tree/main/skills/webapp-testing (Apache-2.0)
