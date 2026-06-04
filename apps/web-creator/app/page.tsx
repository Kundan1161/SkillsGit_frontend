import Link from "next/link";
import {
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  CircleDollarSign,
  FilePlus2,
  Layers3,
  MessageCircle,
  Orbit,
  ShieldCheck,
  Sparkles,
  Upload,
  WandSparkles,
  Zap,
} from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { Button } from "@/components/ui/button";

const orbitCards = [
  {
    Icon: Upload,
    title: "Capture",
    sub: "Notes, calls, files",
    className: "creator-orbit-card creator-orbit-card-1",
  },
  {
    Icon: WandSparkles,
    title: "Structure",
    sub: "AI memory neurons",
    className: "creator-orbit-card creator-orbit-card-2",
  },
  {
    Icon: BrainCircuit,
    title: "Persona",
    sub: "Expert twin",
    className: "creator-orbit-card creator-orbit-card-3",
  },
  {
    Icon: CircleDollarSign,
    title: "Publish",
    sub: "Earn monthly",
    className: "creator-orbit-card creator-orbit-card-4",
  },
];

const formats = ["Video", "Audio", "PDF", "Docs", "Markdown", "Notes"];

export default function CreatorHomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main id="main" className="relative flex-1 overflow-hidden">
        <section className="creator-hero relative isolate overflow-hidden">
          <div className="creator-hero-bg" aria-hidden />
          <div className="creator-grid-bg" aria-hidden />
          <div className="mx-auto grid min-h-[calc(100svh-3.5rem)] w-full max-w-7xl items-center gap-10 px-4 py-12 md:px-8 lg:grid-cols-[0.92fr_1.08fr] lg:py-16">
            <div className="relative z-10 max-w-2xl">
              <div className="animate-fade-up inline-flex items-center gap-3 rounded-full border border-brand-500/20 bg-bg-raised/80 px-3 py-2 text-xs font-bold uppercase tracking-[0.18em] text-brand-500 shadow-[0_18px_55px_rgba(124,58,237,0.12)] backdrop-blur-xl">
                <span className="flex -space-x-2" aria-hidden>
                  <span className="h-6 w-6 rounded-full border-2 border-bg bg-brand-500" />
                  <span className="h-6 w-6 rounded-full border-2 border-bg bg-sky-400" />
                  <span className="h-6 w-6 rounded-full border-2 border-bg bg-emerald-400" />
                </span>
                <span className="h-2 w-2 rounded-full bg-brand-400 shadow-[0_0_0_6px_rgba(124,58,237,0.2)]" />
                Studio for expert AI creators
              </div>

              <h1 className="animate-fade-up mt-8 max-w-4xl text-5xl font-black leading-[0.95] tracking-tight text-white md:text-7xl lg:text-8xl">
                Shape your knowledge into a{" "}
                <span className="creator-gradient-text">living AI expert.</span>
              </h1>

              <p className="animate-fade-up mt-6 max-w-xl text-base leading-8 text-slate-300 md:text-lg">
                Capture your process, build a persona, and publish an expert AI with
                citations, memory, and a studio workflow that feels fast from the first click.
              </p>

              <div className="creator-cta-row animate-fade-up mt-8 flex flex-wrap items-center gap-3">
                <Button asChild size="lg" className="creator-primary-cta h-14 rounded-2xl px-7 text-base">
                  <Link href="/skills/new">
                    Start building
                    <ArrowRight className="h-5 w-5" />
                  </Link>
                </Button>
                <Button asChild size="lg" variant="secondary" className="h-14 rounded-2xl px-7 text-base">
                  <Link href="/capture">
                    <Upload className="h-5 w-5" />
                    Capture memory
                  </Link>
                </Button>
              </div>

              <div className="animate-fade-up mt-9 grid max-w-2xl gap-3 sm:grid-cols-3">
                {[
                  { Icon: Zap, label: "10 min setup", sub: "From blank to draft" },
                  { Icon: ShieldCheck, label: "Cited answers", sub: "Sources stay attached" },
                  { Icon: MessageCircle, label: "Live preview", sub: "Test the persona" },
                ].map(({ Icon, label, sub }) => (
                  <div
                    key={label}
                    className="creator-stat-card group rounded-2xl border border-border/70 bg-bg-raised/75 p-4 backdrop-blur-xl transition duration-300 hover:-translate-y-1 hover:border-brand-500/35"
                  >
                    <Icon className="h-5 w-5 text-brand-500 transition duration-300 group-hover:scale-110" />
                    <p className="mt-3 text-sm font-bold text-fg">{label}</p>
                    <p className="mt-1 text-xs text-fg-muted">{sub}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="creator-scene-wrap relative mx-auto flex h-[560px] w-full max-w-[680px] items-center justify-center">
              <div className="creator-scene">
                <div className="creator-orbit creator-orbit-a" aria-hidden />
                <div className="creator-orbit creator-orbit-b" aria-hidden />
                <div className="creator-platform" aria-hidden>
                  <span />
                  <span />
                </div>

                <div className="creator-core group" aria-label="Animated 3D expert brain">
                  <div className="creator-core-glow" aria-hidden />
                  <div className="creator-brain-shell">
                    <div className="creator-brain-lobe creator-brain-lobe-left" />
                    <div className="creator-brain-lobe creator-brain-lobe-right" />
                    <div className="creator-brain-stem" />
                    <div className="creator-neuron creator-neuron-1" />
                    <div className="creator-neuron creator-neuron-2" />
                    <div className="creator-neuron creator-neuron-3" />
                    <div className="creator-neuron creator-neuron-4" />
                  </div>
                  <div className="creator-core-badge">
                    <Orbit className="h-5 w-5" />
                    <span>Neural vault</span>
                  </div>
                </div>

                {orbitCards.map(({ Icon, title, sub, className }) => (
                  <Link key={title} href={title === "Capture" ? "/capture" : "/personas"} className={className}>
                    <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-500/10 text-brand-500">
                      <Icon className="h-5 w-5" />
                    </span>
                    <span>
                      <span className="block text-sm font-black text-fg">{title}</span>
                      <span className="block text-xs text-fg-muted">{sub}</span>
                    </span>
                  </Link>
                ))}

                <div className="creator-revenue-card">
                  <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-fg-subtle">
                    Draft quality
                  </p>
                  <p className="mt-2 text-3xl font-black text-brand-500">94%</p>
                  <p className="mt-1 flex items-center gap-1 text-xs font-semibold text-emerald-500">
                    <CheckCircle2 className="h-3.5 w-3.5" />
                    Ready to test
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="relative z-10 mx-auto w-full max-w-7xl px-4 pb-16 md:px-8">
          <div className="-mt-8 rounded-2xl border border-border/70 bg-bg-raised/85 p-4 shadow-[0_22px_80px_rgba(15,23,42,0.14)] backdrop-blur-xl md:p-6">
            <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-fg-subtle">
                  Supports your source material
                </p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {formats.map((format) => (
                    <span
                      key={format}
                      className="rounded-full border border-border bg-bg px-3 py-1.5 text-xs font-semibold text-fg-muted"
                    >
                      {format}
                    </span>
                  ))}
                </div>
              </div>
              <div className="grid gap-3 sm:grid-cols-2 lg:w-[500px]">
                <Link
                  href="/personas"
                  className="group flex items-center gap-4 rounded-2xl border border-border bg-bg p-4 transition-all hover:-translate-y-1 hover:border-brand-500/35 hover:shadow-lg hover:shadow-brand-500/10"
                >
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-purple-500/10 text-purple-500">
                    <BrainCircuit className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-fg group-hover:text-brand-500">Personas</p>
                    <p className="text-xs text-fg-muted">Tune expert memory and voice</p>
                  </div>
                </Link>
                <Link
                  href="/templates"
                  className="group flex items-center gap-4 rounded-2xl border border-border bg-bg p-4 transition-all hover:-translate-y-1 hover:border-brand-500/35 hover:shadow-lg hover:shadow-brand-500/10"
                >
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-amber-500/10 text-amber-500">
                    <Layers3 className="h-5 w-5" />
                  </div>
                  <div>
                    <p className="font-semibold text-fg group-hover:text-brand-500">Templates</p>
                    <p className="text-xs text-fg-muted">Start from proven systems</p>
                  </div>
                </Link>
              </div>
            </div>
          </div>

          <div className="mt-10 grid gap-6 lg:grid-cols-[0.74fr_1.26fr]">
            <div>
              <h2 className="text-2xl font-black tracking-tight text-fg md:text-3xl">
                My drafts
              </h2>
              <p className="mt-2 text-sm text-fg-muted">
                Skills you're building. Autosaved as you work.
              </p>
              <Button asChild className="mt-5 rounded-full px-5 shadow-sm transition-all hover:shadow-md hover:shadow-brand-500/15">
                <Link href="/skills/new">
                  <FilePlus2 className="h-4 w-4" />
                  New skill
                </Link>
              </Button>
            </div>

            <div className="relative overflow-hidden rounded-2xl border border-dashed border-border bg-bg-raised px-6 py-14 text-center">
              <div className="pointer-events-none absolute inset-0">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_60%_50%_at_50%_100%,rgba(124,58,237,0.08),transparent)]" />
              </div>
              <div className="relative">
                <div className="mx-auto mb-5 inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500/10 to-accent-500/10 text-brand-500">
                  <Sparkles className="h-8 w-8" aria-hidden />
                </div>
                <h3 className="text-xl font-semibold text-fg">No skills started yet</h3>
                <p className="mx-auto mt-2 max-w-sm text-sm text-fg-muted">
                  Pick a template, import an existing project, or start from a blank canvas.
                </p>
                <div className="mt-7 flex flex-wrap items-center justify-center gap-3">
                  <Button asChild className="rounded-full px-6">
                    <Link href="/skills/new">
                      <FilePlus2 className="h-4 w-4" />
                      New skill
                    </Link>
                  </Button>
                  <Button asChild variant="secondary" className="rounded-full px-6">
                    <Link href="/import">
                      <Upload className="h-4 w-4" />
                      Import
                    </Link>
                  </Button>
                  <Button asChild variant="outline" className="rounded-full px-6">
                    <Link href="/templates">Browse templates</Link>
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
