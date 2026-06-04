import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { templatesByCategory } from "@/lib/builder/templates";

const CATEGORY_LABELS: Record<string, string> = {
  finance: "Finance",
  design: "Design",
  marketing: "Marketing",
  engineering: "Engineering",
  operations: "Operations",
  legal: "Legal",
  sales: "Sales",
  support: "Support",
};

export default function TemplatesPage() {
  const grouped = templatesByCategory();
  const categories = Object.keys(grouped) as Array<keyof typeof grouped>;

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main
        id="main"
        className="mx-auto w-full max-w-7xl flex-1 px-4 py-10 md:px-8"
      >
        <header>
          <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
            Templates
          </h1>
          <p className="mt-1 text-sm text-fg-muted">
            Industry-tuned starter graphs. Pick one and edit to taste —
            usually faster than a blank canvas.
          </p>
        </header>

        <div className="mt-10 space-y-10">
          {categories.map((cat) => (
            <section key={cat}>
              <div className="mb-3 flex items-center gap-2">
                <h2 className="text-xl font-semibold">
                  {CATEGORY_LABELS[cat] ?? cat}
                </h2>
                <Badge variant="outline" className="text-[10px]">
                  {grouped[cat].length}
                </Badge>
              </div>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {grouped[cat].map((tpl) => (
                  <Card
                    key={tpl.id}
                    className="transition-shadow hover:shadow-md"
                  >
                    <CardHeader>
                      <CardTitle className="text-base">{tpl.name}</CardTitle>
                      <CardDescription>{tpl.description}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <button
                        type="button"
                        disabled
                        className="text-sm font-medium text-brand-500 opacity-60"
                      >
                        Use template (Phase 3)
                      </button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </section>
          ))}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
