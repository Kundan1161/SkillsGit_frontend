import { SiteHeader } from "@/components/site-header";
import { SkillSubnav } from "@/components/skill-subnav";
import { Card } from "@/components/ui/card";

export default async function VersionsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div className="flex min-h-screen flex-col bg-bg">
      <SiteHeader />
      <SkillSubnav skillId={id} active="versions" />

      <main
        id="main"
        className="mx-auto w-full max-w-4xl flex-1 px-4 py-8 md:px-8"
      >
        <header>
          <h1 className="text-2xl font-semibold tracking-tight">
            Version history
          </h1>
          <p className="mt-1 text-sm text-fg-muted">
            Every published version of this skill. Drafts are not listed here.
          </p>
        </header>

        <ol className="relative mt-8 space-y-4 border-l border-border pl-6">
          {[
            { v: "v0.1.0", note: "Initial draft", state: "Draft" },
            { v: "—", note: "Nothing published yet", state: "Pending" },
          ].map((item, idx) => (
            <li key={idx} className="relative">
              <span className="absolute -left-[1.85rem] top-1.5 flex h-3 w-3 items-center justify-center rounded-full border border-border bg-bg-raised">
                <span className="h-1.5 w-1.5 rounded-full bg-brand-500" />
              </span>
              <Card className="p-4">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium">{item.v}</p>
                  <span className="text-xs text-fg-muted">{item.state}</span>
                </div>
                <p className="mt-1 text-xs text-fg-muted">{item.note}</p>
              </Card>
            </li>
          ))}
        </ol>
      </main>
    </div>
  );
}
