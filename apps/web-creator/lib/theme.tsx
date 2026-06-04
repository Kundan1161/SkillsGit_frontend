"use client";

import { ThemeProvider as NextThemesProvider } from "next-themes";
import type { ComponentProps, ReactNode } from "react";

type Props = Omit<ComponentProps<typeof NextThemesProvider>, "children"> & {
  children: ReactNode;
};

/**
 * Creator app defaults to **dark**. Per shared/design-system.md:
 *   "Creator: dark by default (long-running canvas work, less eye strain)."
 *
 * `enableSystem` is intentionally false so first-paint never flashes light.
 * A theme toggle in the user menu lets users switch to light if they prefer.
 */
export function ThemeProvider({ children, ...props }: Props) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="dark"
      enableSystem={false}
      disableTransitionOnChange
      {...props}
    >
      {children}
    </NextThemesProvider>
  );
}
