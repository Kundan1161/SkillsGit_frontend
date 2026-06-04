import { SiteHeader } from "@/components/site-header";
import { SkillSubnav } from "@/components/skill-subnav";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const STEPS = [
  "Validate",
  "Pricing & terms",
  "Reviewer notes",
  "Confirm",
] as const;

export default async function PublishPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div className="flex min-h-screen flex-col bg-bg">
      <SiteHeader />
      <SkillSubnav skillId={id} active="publish" />

      <main
        id="main"
        className="mx-auto w-full max-w-4xl flex-1 px-4 py-8 md:px-8"
      >
        <header>
          <h1 className="text-2xl font-semibold tracking-tight">
            Publish to marketplace
          </h1>
          <p className="mt-1 text-sm text-fg-muted">
            Four steps to ship. Your skill will enter the review queue once
            you confirm.
          </p>
        </header>

        {/* Steps strip */}
        <ol className="mt-8 flex items-center gap-2">
          {STEPS.map((step, idx) => (
            <li
              key={step}
              className={cn(
                "flex flex-1 items-center gap-2 rounded-md border border-border bg-bg-raised px-3 py-2 text-sm",
                idx === 0 && "border-brand-500 text-fg",
              )}
            >
              <span
                className={cn(
                  "flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-semibold",
                  idx === 0
                    ? "bg-brand-500 text-white"
                    : "bg-bg-muted text-fg-muted",
                )}
              >
                {idx + 1}
              </span>
              <span className={cn(idx === 0 ? "text-fg" : "text-fg-muted")}>
                {step}
              </span>
            </li>
          ))}
        </ol>

        <Card className="mt-6 p-6">
          <p className="text-xs font-semibold uppercase tracking-wide text-fg-muted">
            Step 1: Validate
          </p>
          <div className="mt-3 h-[40vh] rounded-md bg-bg-muted" />
          <p className="mt-3 text-xs text-fg-subtle">
            Wizard logic, server-side validation, and the publish hand-off
            land in Phase 3.
          </p>
        </Card>
      </main>
    </div>
  );
}
