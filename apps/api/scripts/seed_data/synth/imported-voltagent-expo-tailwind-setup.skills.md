---
id: skillsgit-curated/imported-voltagent-expo-tailwind-setup
version: 1.0.0
name: Tailwind CSS v4 in Expo (NativeWind v5)
description: Set up Tailwind CSS v4 in Expo with react-native-css and NativeWind v5 for universal styling across iOS, Android, and Web.
authors:
  - name: Expo
    handle: expo
    role: author
  - name: skillsgit Curated
    handle: skillsgit-curated
    role: maintainer
category: engineering
tags: [imported, source-voltagent, expo, tailwind, nativewind, styling, react-native]
license_type: free
pricing:
  currency: USD
  support_included: false
ai:
  required_models: [claude-opus-4-7]
  compatible_models: [claude-sonnet-4-6, gpt-4o]
  min_context_tokens: 32000
  estimated_tokens_per_invocation: 6000
trigger_keywords: [tailwind expo, nativewind, react-native-css, tailwind v4, universal styling]
example_invocations:
  - Set up Tailwind v4 in my Expo app
  - Configure NativeWind v5 with metro and postcss
  - Use Apple system colors with CSS variables
inputs: []
outputs: []
changelog:
  - version: 1.0.0
    date: 2026-05-14
    notes: Imported from VoltAgent/awesome-agent-skills under MIT.
---

# Tailwind CSS Setup for Expo with react-native-css

## When to use

Use this skill when adding Tailwind CSS v4 to an Expo project for universal styling across iOS, Android, and Web — typically replacing inline styles or NativeWind v4.

## How to apply

Install dependencies, configure Metro with `withNativewind`, set up PostCSS with `@tailwindcss/postcss`, write a global CSS file, and wrap React Native components with `useCssElement` to enable the `className` prop.

## Overview

This setup uses:

- **Tailwind CSS v4** — Modern CSS-first configuration
- **react-native-css** — CSS runtime for React Native
- **NativeWind v5** — Metro transformer for Tailwind in React Native
- **@tailwindcss/postcss** — PostCSS plugin for Tailwind v4

## Installation

```bash
npx expo install tailwindcss@^4 nativewind@5.0.0-preview.2 react-native-css@0.0.0-nightly.5ce6396 @tailwindcss/postcss tailwind-merge clsx
```

Resolutions for `lightningcss`:

```json
// package.json
{
  "resolutions": {
    "lightningcss": "1.30.1"
  }
}
```

- `autoprefixer` is not needed in Expo because of lightningcss.
- `postcss` is included in Expo by default.

## Metro Config

```js
// metro.config.js
const { getDefaultConfig } = require("expo/metro-config");
const { withNativewind } = require("nativewind/metro");

const config = getDefaultConfig(__dirname);

module.exports = withNativewind(config, {
  inlineVariables: false,        // inline variables break PlatformColor in CSS variables
  globalClassNamePolyfill: false // we add className support manually
});
```

## PostCSS Config

```js
// postcss.config.mjs
export default {
  plugins: { "@tailwindcss/postcss": {} },
};
```

## Global CSS

```css
/* src/global.css */
@import "tailwindcss/theme.css" layer(theme);
@import "tailwindcss/preflight.css" layer(base);
@import "tailwindcss/utilities.css";

@media android {
  :root {
    --font-mono: monospace;
    --font-rounded: normal;
    --font-serif: serif;
    --font-sans: normal;
  }
}

@media ios {
  :root {
    --font-mono: ui-monospace;
    --font-serif: ui-serif;
    --font-sans: system-ui;
    --font-rounded: ui-rounded;
  }
}
```

## IMPORTANT: No Babel Config Needed

With Tailwind v4 and NativeWind v5, you do NOT need a `babel.config.js` for Tailwind. Remove any NativeWind babel presets if present.

## CSS Component Wrappers

Since `react-native-css` requires explicit CSS element wrapping, create reusable components.

```tsx
// src/tw/index.tsx
import { useCssElement, useNativeVariable as useFunctionalVariable } from "react-native-css";
import { Link as RouterLink } from "expo-router";
import Animated from "react-native-reanimated";
import React from "react";
import {
  View as RNView,
  Text as RNText,
  Pressable as RNPressable,
  ScrollView as RNScrollView,
  TouchableHighlight as RNTouchableHighlight,
  TextInput as RNTextInput,
  StyleSheet,
} from "react-native";

export const View = (props: React.ComponentProps<typeof RNView> & { className?: string }) =>
  useCssElement(RNView, props, { className: "style" });

export const Text = (props: React.ComponentProps<typeof RNText> & { className?: string }) =>
  useCssElement(RNText, props, { className: "style" });

export const ScrollView = (
  props: React.ComponentProps<typeof RNScrollView> & {
    className?: string;
    contentContainerClassName?: string;
  }
) =>
  useCssElement(RNScrollView, props, {
    className: "style",
    contentContainerClassName: "contentContainerStyle",
  });

export const Pressable = (props: React.ComponentProps<typeof RNPressable> & { className?: string }) =>
  useCssElement(RNPressable, props, { className: "style" });

export const TextInput = (props: React.ComponentProps<typeof RNTextInput> & { className?: string }) =>
  useCssElement(RNTextInput, props, { className: "style" });

export const useCSSVariable =
  process.env.EXPO_OS !== "web"
    ? useFunctionalVariable
    : (variable: string) => `var(${variable})`;
```

## Usage

```tsx
import { View, Text, ScrollView } from "@/tw";

export default function MyScreen() {
  return (
    <ScrollView className="flex-1 bg-white">
      <View className="p-4 gap-4">
        <Text className="text-xl font-bold text-gray-900">Hello Tailwind!</Text>
      </View>
    </ScrollView>
  );
}
```

## Custom Theme Variables (`@theme`)

```css
@layer theme {
  @theme {
    --font-rounded: "SF Pro Rounded", sans-serif;
    --text-base--line-height: calc(1.5em / 1);
    --leading-normal: 1.5em;
  }
}
```

## Apple System Colors

```css
/* src/css/sf.css */
:root {
  --sf-blue: light-dark(rgb(0 122 255), rgb(10 132 255));
  --sf-text: light-dark(rgb(0 0 0), rgb(255 255 255));
  --sf-bg: light-dark(rgb(255 255 255), rgb(0 0 0));
}

@media ios {
  :root {
    --sf-blue: platformColor(systemBlue);
    --sf-text: platformColor(label);
    --sf-bg: platformColor(systemBackground);
  }
}

@layer theme {
  @theme {
    --color-sf-blue: var(--sf-blue);
    --color-sf-text: var(--sf-text);
    --color-sf-bg: var(--sf-bg);
  }
}
```

## Using CSS Variables in JS

```tsx
import { useCSSVariable } from "@/tw";

function MyComponent() {
  const blue = useCSSVariable("--sf-blue");
  return <View style={{ borderColor: blue }} />;
}
```

## Key Differences from NativeWind v4 / Tailwind v3

1. No `babel.config.js` — CSS-first config.
2. PostCSS plugin (`@tailwindcss/postcss`) instead of `tailwindcss`.
3. CSS `@import` instead of `@tailwind` directives.
4. `@theme` in CSS instead of `tailwind.config.js`.
5. Components wrapped with `useCssElement` for className support.
6. Metro: `withNativewind` with `inlineVariables: false`.

## Troubleshooting

- **Styles not applying** — ensure global CSS is imported in entry; check wrapper usage.
- **Platform colors not working** — use `platformColor()` in `@media ios`, fall back to `light-dark()` for web/Android.
- **TypeScript errors** — extend props: `type Props = React.ComponentProps<typeof RNView> & { className?: string }`.

## Attribution

This skill was imported from `VoltAgent/awesome-agent-skills` under the MIT license, originating from the `expo/skills` repository under the MIT license. Original content authored by the listed contributor(s) at the source repository. Modifications by skillsgit: frontmatter normalization to fit marketplace spec; addition of attribution and sources sections.

## Sources reviewed

- https://github.com/VoltAgent/awesome-agent-skills (MIT)
- https://github.com/expo/skills/tree/main/plugins/expo/skills/expo-tailwind-setup (MIT)
