import type { ReactNode } from "react";

export interface PlaceholderProps {
  title: string;
  reference?: string;
  children?: ReactNode;
}

/**
 * Generic "coming soon" page used during Phase 0 scaffolding.
 * Replace per-route as the relevant prompt is implemented.
 */
export function Placeholder({ title, reference, children }: PlaceholderProps) {
  return (
    <section className="mx-auto max-w-7xl px-4 py-16 md:px-8">
      <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
        {title}
      </h1>
      <p className="mt-3 text-base text-fg-muted">
        Coming soon
        {reference ? (
          <>
            {" — see "}
            <code className="rounded-sm bg-bg-muted px-1.5 py-0.5 font-mono text-xs">
              {reference}
            </code>
          </>
        ) : null}
        .
      </p>
      {children ? <div className="mt-8">{children}</div> : null}
    </section>
  );
}
