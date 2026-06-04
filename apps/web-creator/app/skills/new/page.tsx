import Link from "next/link";
import { ArrowRight, FilePlus2, LibraryBig, Upload } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const CHOICES = [
  {
    id: "blank",
    title: "Start blank",
    description:
      "An empty canvas. You'll wire up nodes from scratch with no guardrails.",
    icon: FilePlus2,
    href: "/skills/draft-blank/builder",
  },
  {
    id: "import",
    title: "Import existing project",
    description:
      "Bring in a Claude Code project, OpenAI Custom GPT, Assistant, or Codex export.",
    icon: Upload,
    href: "/import",
  },
  {
    id: "template",
    title: "Pick a template",
    description:
      "Drop in a 5–8 node starter graph from the gallery, then edit to taste.",
    icon: LibraryBig,
    href: "/templates",
  },
] as const;

export default function NewSkillPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main
        id="main"
        className="mx-auto w-full max-w-5xl flex-1 px-4 py-10 md:px-8"
      >
        <header>
          <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
            Start a new skill
          </h1>
          <p className="mt-1 text-sm text-fg-muted">
            Three ways in. The fastest path is a template.
          </p>
        </header>

        <div className="mt-8 grid gap-4 md:grid-cols-3">
          {CHOICES.map((choice) => (
            <Card
              key={choice.id}
              className="group transition-shadow hover:shadow-md"
            >
              <CardHeader>
                <choice.icon
                  className="h-6 w-6 text-brand-500"
                  aria-hidden
                />
                <CardTitle className="mt-2">{choice.title}</CardTitle>
                <CardDescription>{choice.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Link
                  href={choice.href}
                  className="inline-flex items-center gap-1 text-sm font-medium text-brand-500 group-hover:underline"
                >
                  Continue
                  <ArrowRight className="h-4 w-4" />
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
