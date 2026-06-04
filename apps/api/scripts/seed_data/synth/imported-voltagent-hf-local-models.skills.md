---
id: skillsgit-curated/imported-voltagent-hf-local-models
version: 1.0.0
name: Hugging Face Local Models with llama.cpp
description: Run open-weight models locally with llama.cpp and GGUF on CPU, Mac Metal, CUDA, or ROCm — finding GGUFs, quant selection, and OpenAI-compatible local serving.
authors:
  - name: Hugging Face
    handle: huggingface
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, huggingface, llama-cpp, gguf, local-inference, quantization]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [llama.cpp, gguf, local llm, q4_k_m, llama-server, llama-cli, ollama]
example_invocations:
  - Run a Qwen GGUF model locally with llama-server
  - Pick the right quant for 24GB VRAM
  - Convert a Transformers checkpoint to GGUF
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under MIT.
---

# Hugging Face Local Models

Search the Hugging Face Hub for llama.cpp-compatible GGUF repos, choose the right quant, and launch the model with `llama-cli` or `llama-server`.

## When to use

Use this skill when selecting and running open-weight models locally with llama.cpp and GGUF on CPU, Mac Metal, CUDA, or ROCm — covering Hub discovery, quant choice, exact GGUF lookup, conversion, and OpenAI-compatible local serving.

## How to apply

Prefer the exact quant that HF marks as compatible on the `?local-app=llama.cpp` page. Default to `Q4_K_M` unless the repo page or hardware suggests otherwise. Confirm exact `.gguf` filenames via the tree API. Convert from Transformers weights only when no GGUF is available.

## Default Workflow

1. Search the Hub with `apps=llama.cpp`.
2. Open `https://huggingface.co/<repo>?local-app=llama.cpp`.
3. Prefer the exact HF local-app snippet and quant recommendation when visible.
4. Confirm exact `.gguf` filenames with `https://huggingface.co/api/models/<repo>/tree/main?recursive=true`.
5. Launch with `llama-cli -hf <repo>:<QUANT>` or `llama-server -hf <repo>:<QUANT>`.
6. Fall back to `--hf-repo` + `--hf-file` when the repo uses custom file naming.
7. Convert from Transformers weights only if the repo does not already expose GGUF files.

## Quick Start

### Install llama.cpp

```bash
brew install llama.cpp     # macOS
winget install llama.cpp   # Windows
```

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
make
```

### Authenticate for gated repos

```bash
hf auth login
```

### Search the Hub

```
https://huggingface.co/models?apps=llama.cpp&sort=trending
https://huggingface.co/models?search=Qwen&apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&num_parameters=min:0,max:24B&sort=trending
```

### Run from the Hub

```bash
llama-cli -hf unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_M
llama-server -hf unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_M
```

### Run an exact GGUF file

```bash
llama-server \
    --hf-repo unsloth/Qwen3.6-35B-A3B-GGUF \
    --hf-file Qwen3.6-35B-A3B-UD-Q4_K_M.gguf \
    -c 4096
```

### Convert only when no GGUF is available

```bash
hf download <repo-without-gguf> --local-dir ./model-src
python convert_hf_to_gguf.py ./model-src \
    --outfile model-f16.gguf \
    --outtype f16
llama-quantize model-f16.gguf model-q4_k_m.gguf Q4_K_M
```

### Smoke test a local server

```bash
llama-server -hf unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_M

curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer no-key" \
  -d '{ "messages": [{"role": "user", "content": "Hello"}] }'
```

## Quant Choice

- Prefer the exact quant HF marks as compatible on the `?local-app=llama.cpp` page.
- Keep repo-native labels (`UD-Q4_K_M`) instead of normalizing.
- Default to `Q4_K_M`.
- Prefer `Q5_K_M` or `Q6_K` for code or technical workloads when memory allows.
- Consider `Q3_K_M`, `Q4_K_S`, or repo-specific `IQ` / `UD-*` variants for tight RAM/VRAM budgets.
- Treat `mmproj-*.gguf` as projector weights, not the main checkpoint.

## Resources

- llama.cpp: https://github.com/ggml-org/llama.cpp
- HF + llama.cpp docs: https://huggingface.co/docs/hub/gguf-llamacpp
- HF Local Apps docs: https://huggingface.co/docs/hub/main/local-apps
- GGUF converter Space: https://huggingface.co/spaces/ggml-org/gguf-my-repo

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `huggingface/skills` repository under the MIT license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/huggingface/skills/tree/main/skills/huggingface-local-models (MIT)
