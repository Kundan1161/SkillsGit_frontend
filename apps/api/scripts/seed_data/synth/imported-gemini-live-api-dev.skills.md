---
id: skillsgit-curated/imported-google-gemini-live-api-dev
version: 1.0.0
name: Gemini Live API Development
description: Build real-time bidirectional streaming applications with the Gemini Live API — WebSocket audio/video/text, VAD, native audio, function calling, ephemeral tokens.
authors:
  - name: Google (original)
    handle: google
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-google, gemini, live-api, websockets, streaming, voice]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o, gemini-2.0-pro]
trigger_keywords: [gemini live, websocket, real-time audio, voice activity detection, ephemeral tokens, native audio]
example_invocations:
  - "Connect a Python client to the Gemini Live API for voice chat."
  - "Stream camera frames and audio to Gemini Live."
  - "Handle session resumption and context compression in Live API."
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from google-gemini/gemini-skills under Apache-2.0.
---

# Gemini Live API Development Skill

## When to use

Use this skill when building real-time, bidirectional streaming applications with the Gemini Live API. Covers WebSocket-based audio/video/text streaming, voice activity detection (VAD), native audio features, function calling, session management, ephemeral tokens for client-side auth, and all Live API configuration options. SDKs covered: `google-genai` (Python), `@google/genai` (JavaScript/TypeScript).

## How to apply

Connect over WebSockets to `gemini-3.1-flash-live-preview`. Use `send_realtime_input` / `sendRealtimeInput` for all real-time user input (audio, video, text). Reserve `send_client_content` only for seeding initial context history. Process all parts in each server event. Implement session resumption and context-window compression for long sessions.

## Overview

The Live API enables low-latency, real-time voice and video interactions with Gemini over WebSockets. It processes continuous streams of audio, video, or text to deliver immediate, human-like spoken responses.

Key capabilities:
- Bidirectional audio streaming — real-time mic-to-speaker conversations
- Video streaming — send camera/screen frames alongside audio
- Text input/output — send and receive text within a live session
- Audio transcriptions — get text transcripts of both input and output audio
- Voice Activity Detection (VAD) — automatic interruption handling
- Native audio — thinking (with configurable `thinkingLevel`)
- Function calling — synchronous tool use
- Google Search grounding — ground responses in real-time search results
- Session management — context compression, session resumption, GoAway signals
- Ephemeral tokens — secure client-side authentication

> [!NOTE]
> The Live API currently only supports WebSockets. For WebRTC support or simplified integration, use a partner integration.

## Models

- `gemini-3.1-flash-live-preview` — Optimized for low-latency, real-time dialogue. Native audio output, thinking (via `thinkingLevel`). 128k context window. This is the recommended model for all Live API use cases.

> [!WARNING]
> The following Live API models are deprecated and will be shut down. Migrate to `gemini-3.1-flash-live-preview`.
> - `gemini-2.5-flash-native-audio-preview-12-2025`
> - `gemini-live-2.5-flash-preview` (shutdown Dec 9, 2025)
> - `gemini-2.0-flash-live-001` (shutdown Dec 9, 2025)

## SDKs

- Python: `google-genai` — `pip install google-genai`
- JavaScript/TypeScript: `@google/genai` — `npm install @google/genai`

> [!WARNING]
> Legacy SDKs `google-generativeai` (Python) and `@google/generative-ai` (JS) are deprecated. Use the new SDKs above.

## Partner Integrations

To streamline real-time audio/video app development, use a third-party integration supporting the Gemini Live API over WebRTC or WebSockets: LiveKit, Pipecat by Daily, Fishjam by Software Mansion, Vision Agents by Stream, Voximplant, Firebase AI SDK.

## Audio Formats

- Input: Raw PCM, little-endian, 16-bit, mono. 16kHz native (will resample others). MIME type: `audio/pcm;rate=16000`
- Output: Raw PCM, little-endian, 16-bit, mono. 24kHz sample rate.

> [!IMPORTANT]
> Use `send_realtime_input` / `sendRealtimeInput` for all real-time user input (audio, video, and text). `send_client_content` / `sendClientContent` is only supported for seeding initial context history. Do not use it to send new user messages during the conversation.

> [!WARNING]
> Do not use `media` in `sendRealtimeInput`. Use the specific keys: `audio` for audio data, `video` for images/video frames, and `text` for text input.

---

## Quick Start

### Authentication

#### Python

```python
from google import genai

client = genai.Client(api_key="YOUR_API_KEY")
```

#### JavaScript

```js
import { GoogleGenAI } from '@google/genai';

const ai = new GoogleGenAI({ apiKey: 'YOUR_API_KEY' });
```

### Connecting to the Live API

#### Python
```python
from google.genai import types

config = types.LiveConnectConfig(
    response_modalities=[types.Modality.AUDIO],
    system_instruction=types.Content(
        parts=[types.Part(text="You are a helpful assistant.")]
    )
)

async with client.aio.live.connect(model="gemini-3.1-flash-live-preview", config=config) as session:
    pass
```

#### JavaScript
```js
const session = await ai.live.connect({
  model: 'gemini-3.1-flash-live-preview',
  config: {
    responseModalities: ['audio'],
    systemInstruction: { parts: [{ text: 'You are a helpful assistant.' }] }
  },
  callbacks: {
    onopen: () => console.log('Connected'),
    onmessage: (response) => console.log('Message:', response),
    onerror: (error) => console.error('Error:', error),
    onclose: () => console.log('Closed')
  }
});
```

### Sending Text

```python
await session.send_realtime_input(text="Hello, how are you?")
```

```js
session.sendRealtimeInput({ text: 'Hello, how are you?' });
```

### Sending Audio

```python
await session.send_realtime_input(
    audio=types.Blob(data=chunk, mime_type="audio/pcm;rate=16000")
)
```

```js
session.sendRealtimeInput({
  audio: { data: chunk.toString('base64'), mimeType: 'audio/pcm;rate=16000' }
});
```

### Sending Video

```python
await session.send_realtime_input(
    video=types.Blob(data=frame, mime_type="image/jpeg")
)
```

```js
session.sendRealtimeInput({
  video: { data: frame.toString('base64'), mimeType: 'image/jpeg' }
});
```

### Receiving Audio and Text

> [!IMPORTANT]
> A single server event can contain multiple content parts simultaneously (e.g., audio chunks and transcript). Always process all parts in each event.

```python
async for response in session.receive():
    content = response.server_content
    if content:
        if content.model_turn:
            for part in content.model_turn.parts:
                if part.inline_data:
                    audio_data = part.inline_data.data
        if content.input_transcription:
            print(f"User: {content.input_transcription.text}")
        if content.output_transcription:
            print(f"Gemini: {content.output_transcription.text}")
        if content.interrupted is True:
            pass
```

```js
const content = response.serverContent;
if (content?.modelTurn?.parts) {
  for (const part of content.modelTurn.parts) {
    if (part.inlineData) {
      const audioData = part.inlineData.data;
    }
  }
}
if (content?.inputTranscription) console.log('User:', content.inputTranscription.text);
if (content?.outputTranscription) console.log('Gemini:', content.outputTranscription.text);
if (content?.interrupted) { /* Stop playback, clear audio queue */ }
```

## Limitations

- Response modality: Only `TEXT` or `AUDIO` per session, not both
- Audio-only session: 15 min without compression
- Audio+video session: 2 min without compression
- Connection lifetime: ~10 min (use session resumption)
- Context window: 128k tokens (native audio) / 32k tokens (standard)
- Async function calling: Not yet supported
- Proactive audio and affective dialogue: Not yet supported in Gemini 3.1 Flash Live
- Code execution and URL context: Not supported

## Migrating from Gemini 2.5 Flash Live

1. Update the model string to `gemini-3.1-flash-live-preview`.
2. Use `thinkingLevel` (`minimal`, `low`, `medium`, `high`) instead of `thinkingBudget`.
3. Process all content parts in each event.
4. Use `send_realtime_input` for text during conversation.
5. Default turn coverage changed to `TURN_INCLUDES_AUDIO_ACTIVITY_AND_ALL_VIDEO`.
6. Function calling is synchronous only.
7. Remove proactive audio and affective dialogue configuration.

## Best Practices

1. Use headphones when testing mic audio to prevent echo/self-interruption.
2. Enable context window compression for sessions longer than 15 minutes.
3. Implement session resumption to handle connection resets gracefully.
4. Use ephemeral tokens for client-side deployments — never expose API keys in browsers.
5. Use `send_realtime_input` for all real-time user input.
6. Send `audioStreamEnd` when the mic is paused to flush cached audio.
7. Clear audio playback queues on interruption signals.
8. Process all parts in each server event.

## Documentation Lookup

Use the Google MCP `search_docs` tool when available; otherwise fetch from `https://ai.google.dev/gemini-api/docs/llms.txt` to discover the per-feature `.md.txt` reference pages (Live API Overview, Capabilities Guide, Tool Use, Session Management, Ephemeral Tokens, WebSockets API Reference).

## Supported Languages

The Live API supports 70 languages including: English, Spanish, French, German, Italian, Portuguese, Chinese, Japanese, Korean, Hindi, Arabic, Russian, and many more. Native audio models automatically detect and switch languages.

## Attribution

This skill was imported from `google-gemini/gemini-skills` under the Apache-2.0 license. Original content authored by Google. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections; addition of `## When to use` and `## How to apply` stubs required by our validator. The original LICENSE and NOTICE files are preserved at the source repository.

## Sources reviewed

- https://github.com/google-gemini/gemini-skills/tree/main/skills/gemini-live-api-dev (Apache-2.0)
