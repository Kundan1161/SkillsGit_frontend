import { SiteHeader } from "@/components/site-header";
import { SkillSubnav } from "@/components/skill-subnav";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default async function SandboxPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div className="flex min-h-screen flex-col bg-bg">
      <SiteHeader />
      <SkillSubnav skillId={id} active="sandbox" />

      <main
        id="main"
        className="mx-auto w-full max-w-7xl flex-1 px-4 py-8 md:px-8"
      >
        <header className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">Sandbox</h1>
            <p className="mt-1 text-sm text-fg-muted">
              Run the skill against the configured model with sample inputs.
            </p>
          </div>
          <Button>Run</Button>
        </header>

        <div className="grid gap-4 lg:grid-cols-[1fr_1.5fr]">
          <Card className="p-6">
            <p className="text-xs font-semibold uppercase tracking-wide text-fg-muted">
              Inputs
            </p>
            <div className="mt-3 space-y-3">
              <div className="h-10 rounded-md bg-bg-muted" />
              <div className="h-10 rounded-md bg-bg-muted" />
              <div className="h-24 rounded-md bg-bg-muted" />
            </div>
            <p className="mt-3 text-xs text-fg-subtle">
              Generated from parameter nodes in the builder.
            </p>
          </Card>
          <Card className="p-6">
            <p className="text-xs font-semibold uppercase tracking-wide text-fg-muted">
              Output
            </p>
            <div className="mt-3 h-[60vh] rounded-md bg-bg-muted" />
            <p className="mt-3 text-xs text-fg-subtle">
              Real sandbox runs against the model arrive in Phase 3.
            </p>
          </Card>
        </div>
      </main>
    </div>
  );
}
