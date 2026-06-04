import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const SOURCES = [
  {
    id: "claude-code",
    title: "Claude Code project",
    description:
      "Point us at a Claude Code project export. We'll parse the agents and tools into a graph.",
  },
  {
    id: "openai-gpt",
    title: "OpenAI Custom GPT",
    description:
      "Paste your GPT URL or upload the export bundle. System prompt becomes a context node.",
  },
  {
    id: "openai-assistant",
    title: "OpenAI Assistant",
    description:
      "Bring in an Assistant by API ID. Tools and instructions map to action nodes.",
  },
  {
    id: "codex",
    title: "Codex project",
    description: "Import a Codex project export.",
  },
] as const;

export default function ImportPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main
        id="main"
        className="mx-auto w-full max-w-5xl flex-1 px-4 py-10 md:px-8"
      >
        <header>
          <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
            Import an existing project
          </h1>
          <p className="mt-1 text-sm text-fg-muted">
            Bring in what you already have. We&apos;ll do our best to populate
            the canvas; you take it from there.
          </p>
          <p className="mt-1 text-xs text-fg-subtle">
            Step 1 of 3 — choose a source
          </p>
        </header>

        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {SOURCES.map((src) => (
            <Card key={src.id} className="transition-shadow hover:shadow-md">
              <CardHeader>
                <CardTitle>{src.title}</CardTitle>
                <CardDescription>{src.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <button
                  type="button"
                  disabled
                  className="text-sm font-medium text-brand-500 opacity-60"
                >
                  Continue (Phase 4)
                </button>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
