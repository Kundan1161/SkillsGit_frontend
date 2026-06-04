import { SiteHeader } from "@/components/site-header";
import { SkillSubnav } from "@/components/skill-subnav";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const SECTIONS = [
  "Identity",
  "Discovery",
  "AI runtime",
  "Pricing",
  "Support & contact",
  "Inputs & Outputs",
  "Versioning",
];

export default async function ConfigPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div className="flex min-h-screen flex-col bg-bg">
      <SiteHeader />
      <SkillSubnav skillId={id} active="config" />

      <main
        id="main"
        className="mx-auto w-full max-w-4xl flex-1 px-4 py-8 pb-24 md:px-8"
      >
        <header>
          <h1 className="text-2xl font-semibold tracking-tight">
            Skill configuration
          </h1>
          <p className="mt-1 text-sm text-fg-muted">
            Metadata, AI runtime requirements, pricing. The builder defines
            <em> what </em> the skill does; this defines <em>how it ships</em>.
          </p>
        </header>

        <div className="mt-8 space-y-4">
          {SECTIONS.map((section) => (
            <Card key={section}>
              <CardHeader>
                <CardTitle className="text-base">{section}</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-24 rounded-md bg-bg-muted" />
                <p className="mt-2 text-xs text-fg-subtle">
                  Form fields land in Phase 3.
                </p>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>

      {/* Sticky bottom action bar mockup */}
      <div className="sticky bottom-0 border-t border-border bg-bg-raised/95 backdrop-blur">
        <div className="mx-auto flex max-w-4xl items-center gap-2 px-4 py-3 md:px-8">
          <p className="text-xs text-fg-muted">Autosaved · valid</p>
          <div className="ml-auto flex gap-2">
            <Button variant="ghost" size="sm">
              Preview compiled file
            </Button>
            <Button variant="secondary" size="sm">
              Run in sandbox
            </Button>
            <Button size="sm">Publish</Button>
          </div>
        </div>
      </div>
    </div>
  );
}
