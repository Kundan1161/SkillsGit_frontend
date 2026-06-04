export interface WhatsInsidePreviewProps {
  bodyMd: string | null;
}

/**
 * Phase 1: lightweight markdown rendering for the public preview.
 * We skip a heavy ``unified``/``remark`` dependency for now — the server
 * already strips "How to apply" and clips Examples, and the preview body
 * is short. A proper renderer + sanitizer lands with reviews/comments.
 */
export function WhatsInsidePreview({ bodyMd }: WhatsInsidePreviewProps) {
  if (!bodyMd) {
    return (
      <p className="text-sm text-fg-muted">
        No preview available for this version.
      </p>
    );
  }
  return (
    <pre 
      className="whitespace-pre-wrap p-5 font-sans text-sm leading-relaxed text-fg border-none"
      style={{
        borderRadius: "1.25rem",
        background: "var(--color-bg)",
        boxShadow: "var(--shadow-neu-inset-sm)",
      }}
    >
      {bodyMd}
    </pre>
  );
}
