import Link from "next/link";
import { ArrowRight, User, Mail, Lock } from "lucide-react";

export default function SignUpPage() {
  return (
    <section
      className="relative flex min-h-[calc(100svh-4rem)] items-center justify-center overflow-hidden px-6 py-16"
      style={{ background: "var(--color-bg)" }}
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(circle 420px at 50% 0%, rgba(124,58,237,0.10), transparent 70%)",
        }}
      />

      <div
        className="scroll-reveal-scale relative z-10 w-full max-w-md p-8 sm:p-10"
        style={{ background: "var(--color-bg)", borderRadius: "1.75rem", boxShadow: "var(--shadow-neu-lg)" }}
      >
        <div className="mb-8 flex flex-col items-center text-center">
          <div
            className="mb-4 flex h-14 w-14 items-center justify-center text-lg font-black text-white"
            style={{ background: "linear-gradient(135deg,#7c3aed,#6366f1)", borderRadius: "1rem", boxShadow: "6px 6px 16px rgba(124,58,237,0.3),-2px -2px 8px rgba(255,255,255,0.5)" }}
          >
            SG
          </div>
          <h1 className="text-2xl font-black tracking-tight" style={{ color: "var(--color-fg)", letterSpacing: "-0.03em" }}>
            Create your account
          </h1>
          <p className="mt-1.5 text-sm" style={{ color: "var(--color-fg-muted)" }}>
            Start buying skills — or shipping your own.
          </p>
        </div>

        <form className="flex flex-col gap-5">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="name" className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--color-fg-subtle)" }}>
              Name
            </label>
            <div className="relative">
              <User className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2" style={{ color: "var(--color-fg-subtle)" }} />
              <input
                id="name"
                type="text"
                autoComplete="name"
                placeholder="Jane Doe"
                className="neu-input w-full py-3 pl-10 pr-4 text-sm"
                style={{ color: "var(--color-fg)" }}
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="email" className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--color-fg-subtle)" }}>
              Email
            </label>
            <div className="relative">
              <Mail className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2" style={{ color: "var(--color-fg-subtle)" }} />
              <input
                id="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                className="neu-input w-full py-3 pl-10 pr-4 text-sm"
                style={{ color: "var(--color-fg)" }}
              />
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="password" className="text-xs font-bold uppercase tracking-wider" style={{ color: "var(--color-fg-subtle)" }}>
              Password
            </label>
            <div className="relative">
              <Lock className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2" style={{ color: "var(--color-fg-subtle)" }} />
              <input
                id="password"
                type="password"
                autoComplete="new-password"
                placeholder="At least 12 characters"
                className="neu-input w-full py-3 pl-10 pr-4 text-sm"
                style={{ color: "var(--color-fg)" }}
              />
            </div>
          </div>

          <button
            type="submit"
            className="neu-btn-brand mt-1 inline-flex w-full items-center justify-center gap-2 px-6 py-3.5 text-sm font-bold text-white"
            style={{ borderRadius: "1rem" }}
          >
            Create account <ArrowRight className="h-4 w-4" />
          </button>
        </form>

        <div className="my-6 flex items-center gap-3">
          <span className="h-px flex-1" style={{ background: "var(--color-border)" }} />
          <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color: "var(--color-fg-subtle)" }}>or</span>
          <span className="h-px flex-1" style={{ background: "var(--color-border)" }} />
        </div>

        <button
          type="button"
          className="inline-flex w-full items-center justify-center gap-2 px-6 py-3 text-sm font-semibold"
          style={{ color: "var(--color-fg)", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-sm)", borderRadius: "1rem" }}
        >
          Continue with Google
        </button>

        <p className="mt-6 text-center text-sm" style={{ color: "var(--color-fg-muted)" }}>
          Already have an account?{" "}
          <Link href="/sign-in" className="font-semibold hover:underline" style={{ color: "#7c3aed" }}>
            Sign in
          </Link>
        </p>
      </div>
    </section>
  );
}
