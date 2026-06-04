import Link from "next/link";

/**
 * Minimal footer — creator app is task-focused. Stays out of the way
 * on canvas-heavy routes, present only as a courtesy on home/marketing.
 */
export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-bg">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-2 px-4 py-4 text-xs text-fg-subtle md:flex-row md:px-8">
        <p>skillsgit Studio · v0.1</p>
        <div className="flex gap-4">
          <Link href="/_design" className="hover:text-fg">
            Design
          </Link>
          <a
            href="https://github.com"
            className="hover:text-fg"
            target="_blank"
            rel="noopener noreferrer"
          >
            Docs
          </a>
        </div>
      </div>
    </footer>
  );
}
