import Link from "next/link";
import { ArrowRight, Users, CheckCircle, Brain, Video, Music, FileText, Image, FileCode, File } from "lucide-react";
import { BrainHeroClient } from "@/components/BrainHeroClient";
import { MovingLight } from "@/components/MovingLight";

const professions = [
  { emoji: "🔧", title: "Mechanics",   example: "Engine diagnostics & repair" },
  { emoji: "📚", title: "Teachers",    example: "Curriculum & lesson plans" },
  { emoji: "🏋️", title: "Coaches",     example: "Training & nutrition plans" },
  { emoji: "👨‍🍳", title: "Chefs",       example: "Recipes & kitchen mastery" },
  { emoji: "🔨", title: "Plumbers",    example: "Pipe repair & installation" },
  { emoji: "💼", title: "Consultants", example: "Strategy frameworks" },
  { emoji: "🩺", title: "Doctors",     example: "Clinical decision support" },
  { emoji: "⚖️", title: "Lawyers",     example: "Contract review & research" },
  { emoji: "🎯", title: "Trainers",    example: "Personalized protocols" },
  { emoji: "⚙️", title: "Engineers",   example: "Technical specs & debug" },
  { emoji: "🎨", title: "Designers",   example: "Design & portfolio review" },
  { emoji: "📊", title: "Accountants", example: "Tax & financial planning" },
];

const steps = [
  { num: "01", title: "Upload Your Knowledge",  desc: "PDFs, videos, audio recordings, notes — any format." },
  { num: "02", title: "AI Builds Your Vault",   desc: "Structured, searchable knowledge with source citations." },
  { num: "03", title: "Launch Your Expert AI",  desc: "Customize tone & depth. Set your price. Go live in minutes." },
  { num: "04", title: "Earn While You Sleep",   desc: "Subscribers chat with your AI 24/7. You earn every month." },
];

const plans = [
  {
    name: "Starter",
    price: "$0",
    period: "/forever",
    tagline: "Explore expert AIs",
    featured: false,
    features: ["Browse all experts", "5 questions / month", "Community support"],
    cta: "Get Started",
    href: "/sign-up",
  },
  {
    name: "Pro",
    price: "$19",
    period: "/month",
    tagline: "For serious learners",
    featured: true,
    features: ["Unlimited questions", "Verified source citations", "Priority responses", "Cancel anytime"],
    cta: "Start Pro",
    href: "/sign-up",
  },
  {
    name: "Expert",
    price: "$49",
    period: "/month",
    tagline: "For teams & power users",
    featured: false,
    features: ["Everything in Pro", "Up to 5 team seats", "API access", "Dedicated support"],
    cta: "Go Expert",
    href: "/sign-up",
  },
];

const LEFT_CARDS = [
  { icon: "⚡", title: "Knowledge Capture", sub: "Any format" },
  { icon: "🔮", title: "AI Processing",     sub: "Transcribe, extract, structure" },
  { icon: "🗄️", title: "Smart Vault",       sub: "Organised markdown vault" },
];

const RIGHT_CARDS = [
  { icon: "🪪", title: "Expert Persona", sub: "Digital twin of you" },
  { icon: "👥", title: "Subscribers",    sub: "Ask questions 24/7" },
  { icon: "💰", title: "Recurring Income", sub: "Earn every month" },
];

const FORMATS = [
  { Icon: Video,    label: "Video" },
  { Icon: Music,    label: "Audio" },
  { Icon: FileText, label: "PDF" },
  { Icon: Image,    label: "Images" },
  { Icon: File,     label: "Docs" },
  { Icon: FileText, label: "Notes" },
  { Icon: FileCode, label: "Markdown" },
];

export default function HomePage() {
  return (
    <div style={{ background: "var(--color-bg)" }}>

      {/* Scroll progress bar */}
      <div className="scroll-progress" aria-hidden />

      {/* Moving spotlight; cards with data-lit react to it */}
      <MovingLight />

      {/* ── HERO ─────────────────────────────────────────────────── */}
      <BrainHeroClient />


      {/* ── SOCIAL PROOF MARQUEE ──────────────────────────────────── */}
      <div
        className="scroll-reveal-fade overflow-hidden py-4"
        style={{
          background:"linear-gradient(135deg,#7c3aed,#6366f1)",
          boxShadow:"0 4px 20px rgba(124,58,237,0.25)",
        }}
      >
        <style>{`@keyframes marquee{from{transform:translateX(0)}to{transform:translateX(-50%)}}`}</style>
        <div style={{ display:"flex", width:"max-content", animation:"marquee 28s linear infinite" }}>
          {Array.from({ length: 2 }, (_, i) =>
            ["AI DevOps","Finance","UX Design","Legal","ML & Data","Healthcare","Marketing","Real Estate","Engineering","Culinary Arts","Coaching","Architecture"].map((cat) => (
              <span key={`${cat}-${i}`} className="mx-8 inline-flex items-center gap-3 font-mono text-xs font-bold uppercase tracking-widest" style={{ color:"rgba(255,255,255,0.8)", whiteSpace:"nowrap" }}>
                <span style={{ display:"inline-block", width:4, height:4, borderRadius:"50%", background:"rgba(255,255,255,0.4)" }} />
                {cat}
              </span>
            ))
          ).flat()}
        </div>
      </div>

      {/* ── HOW IT WORKS ──────────────────────────────────────────── */}
      <section id="how-it-works" className="mx-auto max-w-7xl px-6 py-24 lg:px-16 scroll-mt-24">
        <div className="mb-16 text-center scroll-reveal">
          <span className="tag-label mb-3 block">Simple Process</span>
          <h2 style={{ fontSize:"clamp(2.2rem,4vw,4rem)", fontWeight:900, letterSpacing:"-0.04em", color:"var(--color-fg)" }}>
            How It{" "}
            <span style={{ background:"linear-gradient(135deg,#7c3aed,#6366f1)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent", backgroundClip:"text" }}>
              Works
            </span>
          </h2>
        </div>
        <div className="scroll-stagger grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-4">
          {steps.map((step) => (
            <div key={step.num} data-lit className="scroll-reveal-scale neu-feature p-8 flex flex-col gap-4">
              <div
                className="flex h-14 w-14 items-center justify-center text-lg font-black text-white"
                style={{ background:"linear-gradient(135deg,#7c3aed,#6366f1)", borderRadius:"50%", boxShadow:"6px 6px 14px rgba(124,58,237,0.3),-2px -2px 8px rgba(255,255,255,0.5)" }}
              >
                {step.num}
              </div>
              <h3 className="text-base font-bold tracking-tight" style={{ color:"var(--color-fg)" }}>{step.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color:"var(--color-fg-muted)" }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── WHO CAN USE IT ────────────────────────────────────────── */}
      <section className="mx-auto max-w-7xl px-6 py-16 lg:px-16">
        <div className="mb-12 text-center scroll-reveal-clip">
          <span className="tag-label mb-3 block">For Every Expert</span>
          <h2 style={{ fontSize:"clamp(2.2rem,4vw,4rem)", fontWeight:900, letterSpacing:"-0.04em", color:"var(--color-fg)" }}>
            Anyone with knowledge{" "}
            <span style={{ background:"linear-gradient(135deg,#7c3aed,#6366f1)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent", backgroundClip:"text" }}>
              can sell AI.
            </span>
          </h2>
        </div>
        <div className="scroll-stagger grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6">
          {professions.map((p) => (
            <div key={p.title} data-lit className="scroll-reveal-flip neu-tile flex flex-col items-center gap-3 p-5 text-center">
              <span style={{ fontSize:32 }}>{p.emoji}</span>
              <span className="text-sm font-bold" style={{ color:"var(--color-fg)", letterSpacing:"-0.01em" }}>{p.title}</span>
              <span className="text-xs leading-snug" style={{ color:"var(--color-fg-subtle)" }}>{p.example}</span>
            </div>
          ))}
        </div>
      </section>

      {/* ── PRICING ───────────────────────────────────────────────── */}
      <section id="pricing" className="mx-auto max-w-7xl px-6 py-16 lg:px-16 scroll-mt-24">
        <div className="mb-12 text-center scroll-reveal">
          <span className="tag-label mb-3 block">Pricing</span>
          <h2 style={{ fontSize:"clamp(2.2rem,4vw,4rem)", fontWeight:900, letterSpacing:"-0.04em", color:"var(--color-fg)" }}>
            Simple, transparent{" "}
            <span style={{ background:"linear-gradient(135deg,#7c3aed,#6366f1)", WebkitBackgroundClip:"text", WebkitTextFillColor:"transparent", backgroundClip:"text" }}>
              pricing.
            </span>
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-base leading-relaxed" style={{ color:"var(--color-fg-muted)" }}>
            Start free. Upgrade when your knowledge starts earning.
          </p>
        </div>

        <div className="scroll-stagger mx-auto grid max-w-5xl grid-cols-1 gap-6 md:grid-cols-3">
          {plans.map((plan) => (
            <div
              key={plan.name}
              data-lit
              className="scroll-reveal-scale relative flex flex-col gap-6 p-8"
              style={{
                background: "var(--color-bg)",
                borderRadius: "1.5rem",
                boxShadow: plan.featured ? "var(--shadow-neu-lg)" : "var(--shadow-neu-md)",
                border: plan.featured ? "1.5px solid #7c3aed" : "1px solid var(--color-border)",
              }}
            >
              {plan.featured && (
                <span
                  className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full px-3 py-1 text-[10px] font-black uppercase tracking-widest text-white"
                  style={{ background: "linear-gradient(135deg,#7c3aed,#6366f1)", boxShadow: "0 4px 14px rgba(124,58,237,0.4)" }}
                >
                  Most Popular
                </span>
              )}
              <div>
                <h3 className="text-lg font-black tracking-tight" style={{ color: "var(--color-fg)" }}>{plan.name}</h3>
                <p className="mt-1 text-xs" style={{ color: "var(--color-fg-subtle)" }}>{plan.tagline}</p>
              </div>
              <div className="flex items-end gap-1">
                <span className="text-4xl font-black tracking-tight" style={{ color: "var(--color-fg)" }}>{plan.price}</span>
                <span className="mb-1 text-sm" style={{ color: "var(--color-fg-subtle)" }}>{plan.period}</span>
              </div>
              <ul className="flex flex-col gap-2.5">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2.5 text-sm" style={{ color: "var(--color-fg-muted)" }}>
                    <CheckCircle className="h-4 w-4 shrink-0" style={{ color: "#7c3aed" }} />
                    {f}
                  </li>
                ))}
              </ul>
              <Link
                href="/sign-up"
                className={`${plan.featured ? "neu-btn-brand text-white" : ""} mt-auto inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-bold w-full`}
                style={
                  plan.featured
                    ? { borderRadius: "1rem" }
                    : { borderRadius: "1rem", color: "var(--color-fg)", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)" }
                }
              >
                {plan.cta} <ArrowRight className="h-4 w-4" style={plan.featured ? undefined : { color: "#7c3aed" }} />
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* ── DUAL CTA ──────────────────────────────────────────────── */}
      <section className="mx-auto max-w-7xl px-6 py-16 pb-28 lg:px-16">
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div data-lit className="scroll-reveal-left neu-lg relative overflow-hidden p-10 flex flex-col gap-6">
            <div aria-hidden className="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full blur-[40px] opacity-20" style={{ background:"#7c3aed" }} />
            <div className="flex h-16 w-16 items-center justify-center" style={{ background:"linear-gradient(135deg,#7c3aed,#6366f1)", borderRadius:"1.25rem", boxShadow:"6px 6px 16px rgba(124,58,237,0.3),-2px -2px 8px rgba(255,255,255,0.5)" }}>
              <Brain className="h-8 w-8 text-white" />
            </div>
            <div>
              <h3 className="text-2xl font-black tracking-tight" style={{ color:"var(--color-fg)", letterSpacing:"-0.03em" }}>For Creators & Experts</h3>
              <p className="mt-2 text-base leading-relaxed" style={{ color:"var(--color-fg-muted)" }}>Transform your expertise into a 24/7 income stream. Upload once, earn forever.</p>
            </div>
            <ul className="scroll-stagger flex flex-col gap-2.5">
              {["Upload any content format","AI trained exclusively on YOUR knowledge","Set your own subscription price","Full analytics & earnings dashboard"].map(item=>(
                <li key={item} className="scroll-reveal-fade flex items-center gap-2.5 text-sm" style={{ color:"var(--color-fg-muted)" }}>
                  <CheckCircle className="h-4 w-4 shrink-0" style={{ color:"#7c3aed" }} />
                  {item}
                </li>
              ))}
            </ul>
            <Link href="/creator/dashboard" className="neu-btn-brand mt-2 inline-flex items-center gap-2 px-7 py-3.5 text-sm font-bold text-white w-fit" style={{ borderRadius:"1rem" }}>
              Start Creating <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div data-lit className="scroll-reveal-right neu-lg relative overflow-hidden p-10 flex flex-col gap-6">
            <div aria-hidden className="pointer-events-none absolute -right-8 -bottom-8 h-32 w-32 rounded-full blur-[40px] opacity-15" style={{ background:"#6366f1" }} />
            <div className="flex h-16 w-16 items-center justify-center" style={{ background:"var(--color-bg)", boxShadow:"var(--shadow-neu-md)", borderRadius:"1.25rem" }}>
              <Users className="h-8 w-8" style={{ color:"#7c3aed" }} />
            </div>
            <div>
              <h3 className="text-2xl font-black tracking-tight" style={{ color:"var(--color-fg)", letterSpacing:"-0.03em" }}>For Knowledge Seekers</h3>
              <p className="mt-2 text-base leading-relaxed" style={{ color:"var(--color-fg-muted)" }}>Expert-level answers instantly. Chat with AI built from verified professional knowledge.</p>
            </div>
            <ul className="scroll-stagger flex flex-col gap-2.5">
              {["Verified expert knowledge — not generic AI","Source citations on every answer","Cancel any subscription anytime","Unlimited questions to your expert"].map(item=>(
                <li key={item} className="scroll-reveal-fade flex items-center gap-2.5 text-sm" style={{ color:"var(--color-fg-muted)" }}>
                  <CheckCircle className="h-4 w-4 shrink-0" style={{ color:"#7c3aed" }} />
                  {item}
                </li>
              ))}
            </ul>
            <Link href="/explore" className="mt-2 inline-flex items-center gap-2 px-7 py-3.5 text-sm font-semibold w-fit" style={{ color:"var(--color-fg)", background:"var(--color-bg)", boxShadow:"var(--shadow-neu-sm)", borderRadius:"1rem" }}>
              Explore Experts <ArrowRight className="h-4 w-4" style={{ color:"#7c3aed" }} />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
