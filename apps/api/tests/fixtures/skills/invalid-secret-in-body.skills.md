---
id: janedoe/leaks-secret
version: 1.0.0
name: Leaks Secret
description: Contains an OpenAI API key in the body.
category: finance
license_type: free
ai:
  required_models:
    - claude-opus-4-7
---

# Leaks Secret

## When to use
Trigger validator on secret detection in the body.

## How to apply
Set your API key like so:

```bash
export OPENAI_API_KEY=sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ012345
```

The validator should detect and reject this.
