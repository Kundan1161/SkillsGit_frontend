---
id: skillsgit-curated/imported-voltagent-hf-transformers-js
version: 1.0.0
name: Transformers.js — ML in JavaScript
description: Run state-of-the-art machine learning models in JavaScript across browsers and server-side runtimes (Node.js, Bun, Deno) with no Python server required.
authors:
  - name: Hugging Face
    handle: huggingface
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, huggingface, transformers, javascript, browser-ml, webgpu, onnx]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [transformers.js, javascript ml, browser ml, webgpu, onnx js, huggingface pipeline]
example_invocations:
  - Run a sentiment analysis pipeline in the browser
  - Add object detection to my Node.js app using transformers.js
  - Set up a quantized text generation model with WebGPU
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under MIT.
---

# Transformers.js — Machine Learning for JavaScript

Transformers.js enables running state-of-the-art ML models directly in JavaScript across browsers and server-side runtimes (Node.js, Bun, Deno), with no Python server required.

## When to use

Use this skill when you need to:

- Run ML models for text analysis, generation, or translation in JavaScript
- Perform image classification, object detection, or segmentation
- Implement speech recognition or audio processing
- Build multimodal AI applications (text-to-image, image-to-text, etc.)
- Run models client-side in the browser without a backend

## How to apply

Install `@huggingface/transformers`, use the `pipeline` API to load a model for your task, run inference, and always call `pipe.dispose()` when finished to free memory. Use quantized models (`dtype: 'q4'` or `'q8'`) for faster inference and WebGPU when available.

## Installation

```bash
npm install @huggingface/transformers
```

Browser via CDN:

```html
<!-- script type="module" -->
  import { pipeline } from 'https://cdn.jsdelivr.net/npm/@huggingface/transformers';
<!-- /script -->
```

## Pipeline API

```javascript
import { pipeline } from '@huggingface/transformers';

const pipe = await pipeline('sentiment-analysis');
const result = await pipe('I love transformers!');
// [{ label: 'POSITIVE', score: 0.999817686 }]

await pipe.dispose();
```

> All pipelines must be disposed with `pipe.dispose()` when finished to prevent memory leaks.

## Model Selection

```javascript
const pipe = await pipeline(
  'sentiment-analysis',
  'Xenova/bert-base-multilingual-uncased-sentiment'
);
```

Browse models: https://huggingface.co/models?library=transformers.js&sort=trending

## Device & Quantization

```javascript
// GPU via WebGPU
const pipe = await pipeline('sentiment-analysis', 'model-id', { device: 'webgpu' });

// Quantization: 'fp32' | 'fp16' | 'q8' | 'q4'
const pipe = await pipeline('sentiment-analysis', 'model-id', { dtype: 'q4' });
```

## Common Tasks

### NLP

```javascript
// Classification
const cls = await pipeline('text-classification');
await cls('This movie was amazing!');

// NER
const ner = await pipeline('token-classification');
await ner('My name is John and I live in New York.');

// QA
const qa = await pipeline('question-answering');
await qa({ question: 'What is the capital of France?', context: 'Paris is the capital of France.' });

// Text generation
const gen = await pipeline('text-generation', 'onnx-community/gemma-3-270m-it-ONNX');
await gen('Once upon a time', { max_new_tokens: 100, temperature: 0.7 });

// Translation
const tr = await pipeline('translation', 'Xenova/nllb-200-distilled-600M');
await tr('Hello, how are you?', { src_lang: 'eng_Latn', tgt_lang: 'fra_Latn' });

// Summarization
const sum = await pipeline('summarization');
await sum(longText, { max_length: 100, min_length: 30 });

// Zero-shot
const zs = await pipeline('zero-shot-classification');
await zs('This is a story about sports.', ['politics', 'sports', 'technology']);
```

### Vision

```javascript
// Image classification
const ic = await pipeline('image-classification');
await ic('image.jpg');

// Object detection
const od = await pipeline('object-detection');
await od('image.jpg'); // [{ label, score, box: { xmin, ymin, xmax, ymax } }, ...]

// Segmentation
const seg = await pipeline('image-segmentation');
await seg('image.jpg');

// Depth estimation
const depth = await pipeline('depth-estimation');
await depth('image.jpg');

// Zero-shot image classification
const zic = await pipeline('zero-shot-image-classification');
await zic('image.jpg', ['cat', 'dog', 'bird']);
```

### Audio

```javascript
// Speech recognition
const asr = await pipeline('automatic-speech-recognition');
await asr('audio.wav');

// Audio classification
const ac = await pipeline('audio-classification');
await ac('audio.wav');

// Text-to-speech
const tts = await pipeline('text-to-speech', 'Xenova/speecht5_tts');
await tts('Hello', { speaker_embeddings });
```

### Multimodal & Embeddings

```javascript
// Image captioning
const cap = await pipeline('image-to-text');
await cap('image.jpg');

// Document QA
const dqa = await pipeline('document-question-answering');
await dqa('doc.jpg', 'What is the total amount?');

// Embeddings
const fe = await pipeline('feature-extraction', 'onnx-community/all-MiniLM-L6-v2-ONNX');
await fe('Text to embed', { pooling: 'mean', normalize: true });
```

## Choosing a Model

1. **Size** — Small (<100MB) for browsers; Medium (100-500MB) for most cases; Large (>500MB) for accuracy.
2. **Quantization** — Start with `q8`/`q4` for speed.
3. **Compatibility** — Check the model card for tasks, languages, and license.
4. **ONNX files** — Ensure the model repo has an `onnx` folder.

## Environment Configuration

```javascript
import { env, LogLevel } from '@huggingface/transformers';

env.allowRemoteModels = true;
env.allowLocalModels = false;
env.localModelPath = '/models/';
env.useFSCache = true;
env.useBrowserCache = true;
env.cacheDir = './.cache';
env.logLevel = LogLevel.INFO;

// Custom fetch (auth, retries)
env.fetch = (url, options) => fetch(url, {
  ...options,
  headers: { ...options?.headers, Authorization: `Bearer ${HF_TOKEN}` },
});
```

## ModelRegistry (v4)

```javascript
import { ModelRegistry } from '@huggingface/transformers';

const files = await ModelRegistry.get_pipeline_files(task, modelId, options);
const cached = await ModelRegistry.is_pipeline_cached(task, modelId, options);
const dtypes = await ModelRegistry.get_available_dtypes(modelId);
```

## Progress Tracking

```javascript
function onProgress(info) {
  if (info.status === 'progress') {
    console.log(`${info.file}: ${info.progress.toFixed(1)}%`);
  }
}

const classifier = await pipeline('sentiment-analysis', null, {
  progress_callback: onProgress
});
```

## Error Handling

```javascript
try {
  const pipe = await pipeline('sentiment-analysis', 'model-id');
  const result = await pipe('text to analyze');
} catch (error) {
  if (error.message.includes('fetch')) console.error('Model download failed.');
  else if (error.message.includes('ONNX')) console.error('Model execution failed.');
  else console.error('Unknown error:', error);
}
```

## Performance Tips

1. Reuse pipelines — don't recreate.
2. Use quantization (`q8` / `q4`).
3. Batch process multiple inputs.
4. Cache models automatically.
5. WebGPU for large models.
6. Limit `max_new_tokens` for generation.
7. **Always `pipe.dispose()`** when done.

## Troubleshooting

- **Model not found** — verify name and ONNX files.
- **Memory issues** — smaller/quantized models, smaller batch, lower `max_length`.
- **WebGPU errors** — Chrome 113+/Edge 113+; try `fp16` instead of `fp32`; fall back to WASM.

## Best Practices

1. Always dispose pipelines.
2. Start with the pipeline API.
3. Test locally before deploying.
4. Monitor download sizes for web apps.
5. Show loading progress.
6. Pin model versions in production.
7. Wrap in try/catch.
8. Provide fallbacks for unsupported browsers.
9. Reuse models — don't recreate.
10. Dispose on SIGTERM/SIGINT in servers.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `huggingface/skills` repository under the MIT license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/huggingface/skills/tree/main/skills/transformers-js (MIT)
