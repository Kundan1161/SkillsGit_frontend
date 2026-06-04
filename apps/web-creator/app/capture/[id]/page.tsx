"use client";

import { use, useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  CheckCircle2,
  ChevronLeft,
  Loader2,
  Sparkles,
  XCircle,
} from "lucide-react";

import { SiteHeader } from "@/components/site-header";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  captureApi,
  type CaptureSessionRead,
  type PiiFlag,
  type SuggestedLink,
} from "@/lib/api/capture";

const POLL_INTERVAL_MS = 2500;

function useAutoSave(
  sessionId: string,
  fields: {
    situation_md: string;
    decision_md: string;
    outcome_md: string;
    context_md: string;
  },
) {
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const save = useCallback(() => {
    captureApi.updateSession(sessionId, fields).catch(() => undefined);
  }, [sessionId, fields]);

  useEffect(() => {
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(save, 1200);
    return () => {
      if (timer.current) clearTimeout(timer.current);
    };
  }, [save]);
}

export default function CaptureSessionPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = use(params);
  const router = useRouter();

  const [session, setSession] = useState<CaptureSessionRead | null>(null);
  const [situation, setSituation] = useState("");
  const [decision, setDecision] = useState("");
  const [outcome, setOutcome] = useState("");
  const [context, setContext] = useState("");
  const [acceptedLinks, setAcceptedLinks] = useState<Set<string>>(new Set());
  const [extracting, setExtracting] = useState(false);
  const [finalizing, setFinalizing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Auto-save draft fields
  useAutoSave(id, {
    situation_md: situation,
    decision_md: decision,
    outcome_md: outcome,
    context_md: context,
  });

  const loadSession = useCallback(async () => {
    const s = await captureApi.getSession(id);
    setSession(s);
    if (!situation) setSituation(s.situation_md ?? "");
    if (!decision) setDecision(s.decision_md ?? "");
    if (!outcome) setOutcome(s.outcome_md ?? "");
    if (!context) setContext(s.context_md ?? "");
    // Pre-accept all suggested links
    if (s.suggested_links_json) {
      setAcceptedLinks(
        new Set(
          s.suggested_links_json
            .filter((l) => l.accepted)
            .map((l) => l.skill_id),
        ),
      );
    }
    return s;
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    loadSession();
  }, [loadSession]);

  // Poll while extracting / finalizing
  useEffect(() => {
    if (!session) return;
    if (
      session.status === "extracting" ||
      session.status === "finalizing"
    ) {
      pollingRef.current = setInterval(async () => {
        const s = await captureApi.getSession(id);
        setSession(s);
        if (s.status !== "extracting" && s.status !== "finalizing") {
          clearInterval(pollingRef.current!);
        }
      }, POLL_INTERVAL_MS);
    }
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, [session?.status, id]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleExtract = async () => {
    setExtracting(true);
    setError(null);
    try {
      await captureApi.updateSession(id, {
        situation_md: situation,
        decision_md: decision,
        outcome_md: outcome,
        context_md: context,
      });
      await captureApi.triggerExtract(id);
      const updated = await loadSession();
      setSession(updated);
    } catch (e) {
      setError((e as { message?: string }).message ?? "Extraction failed.");
    } finally {
      setExtracting(false);
    }
  };

  const toggleLink = (skillId: string) => {
    setAcceptedLinks((prev) => {
      const next = new Set(prev);
      if (next.has(skillId)) next.delete(skillId);
      else next.add(skillId);
      return next;
    });
  };

  const handleFinalize = async () => {
    setFinalizing(true);
    setError(null);
    try {
      const result = await captureApi.finalize(id, {
        accepted_link_skill_ids: Array.from(acceptedLinks),
      });
      router.push(
        `/personas?neuron_created=${result.neuron_skill_id}`,
      );
    } catch (e) {
      setError((e as { message?: string }).message ?? "Finalize failed.");
      setFinalizing(false);
    }
  };

  if (!session) {
    return (
      <div className="flex min-h-screen flex-col">
        <SiteHeader />
        <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-10 md:px-8 space-y-4">
          <Skeleton className="h-8 w-1/2" />
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-40 w-full" />
        </main>
      </div>
    );
  }

  const isEditable =
    session.status === "draft" || session.status === "draft_ready";
  const isDraftReady = session.status === "draft_ready";
  const isFinalized = session.status === "finalized";
  const isExtracting =
    session.status === "extracting" || extracting;
  const piiFlags = session.pii_flags_json ?? [];
  const suggestedLinks = session.suggested_links_json ?? [];
  const highPii = piiFlags.filter((f) => f.severity === "high");

  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-10 md:px-8">
        {/* Back + status bar */}
        <div className="mb-6 flex items-center gap-3">
          <a
            href="/capture"
            className="flex items-center gap-1 text-sm text-fg-muted hover:text-fg"
          >
            <ChevronLeft className="h-4 w-4" />
            Captures
          </a>
          <Separator orientation="vertical" className="h-4" />
          <p className="truncate text-sm font-medium text-fg">
            {session.title}
          </p>
          <Badge
            variant={isFinalized ? "default" : "outline"}
            className="ml-auto shrink-0"
          >
            {session.status.replace("_", " ")}
          </Badge>
        </div>

        {isFinalized ? (
          <div className="flex flex-col items-center gap-3 rounded-xl border border-border bg-bg-raised py-16 text-center">
            <CheckCircle2 className="h-8 w-8 text-success" />
            <p className="font-medium text-fg">Neuron published</p>
            <p className="text-sm text-fg-muted">
              This experience has been added to your persona vault.
            </p>
            <Button asChild variant="outline" className="mt-2">
              <a href="/capture">Back to captures</a>
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Input form */}
            <div className="space-y-5">
              <Field
                id="situation"
                label="Situation"
                description="What was the context? What problem were you facing?"
                value={situation}
                onChange={setSituation}
                disabled={!isEditable}
                placeholder="Two days after upgrading Redis 6→7, our nightly CI suite started failing 1-in-12 runs…"
              />
              <Field
                id="decision"
                label="Decision"
                description="What did you decide to do, and why?"
                value={decision}
                onChange={setDecision}
                disabled={!isEditable}
                placeholder="I pinned the Redis client library and reverted the tcp-keepalive timeout the upgrade had silently reset…"
              />
              <Field
                id="outcome"
                label="Outcome"
                description="What happened? What did you learn?"
                value={outcome}
                onChange={setOutcome}
                disabled={!isEditable}
                placeholder="Failure rate dropped from ~8% to zero. Root cause was the keepalive change, not the client library…"
              />
              <Field
                id="context"
                label="Additional context"
                description="Links, logs, PR numbers, anything else relevant. (Optional)"
                value={context}
                onChange={setContext}
                disabled={!isEditable}
                placeholder="PR #1234, incident #5678"
                rows={3}
              />
            </div>

            {/* PII warnings */}
            {highPii.length > 0 && (
              <Card className="border-warning">
                <CardHeader className="pb-2">
                  <CardTitle className="flex items-center gap-2 text-sm text-warning">
                    <AlertTriangle className="h-4 w-4" />
                    Sensitive information detected
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {highPii.map((f, i) => (
                    <div key={i} className="text-xs">
                      <span className="font-mono bg-bg-muted px-1 rounded">
                        {f.span}
                      </span>{" "}
                      — {f.kind}
                      {f.suggestion && (
                        <span className="text-fg-subtle"> · {f.suggestion}</span>
                      )}
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Suggested links */}
            {isDraftReady && suggestedLinks.length > 0 && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold">
                    Suggested skill links
                  </CardTitle>
                  <CardDescription className="text-xs">
                    AI identified related skills in the occupation vault.
                    Accept the ones that are relevant to this neuron.
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  {suggestedLinks.map((link) => {
                    const accepted = acceptedLinks.has(link.skill_id);
                    return (
                      <button
                        key={link.skill_id}
                        onClick={() => toggleLink(link.skill_id)}
                        className="flex w-full items-center gap-3 rounded-lg border border-border px-3 py-2.5 text-left transition-colors hover:border-brand-500"
                      >
                        {accepted ? (
                          <CheckCircle2 className="h-4 w-4 shrink-0 text-brand-500" />
                        ) : (
                          <XCircle className="h-4 w-4 shrink-0 text-fg-subtle" />
                        )}
                        <span className="min-w-0 flex-1 truncate text-sm text-fg">
                          {link.skill_name}
                        </span>
                        <span className="text-xs text-fg-subtle">
                          {Math.round(link.relevance * 100)}%
                        </span>
                      </button>
                    );
                  })}
                </CardContent>
              </Card>
            )}

            {/* Draft preview */}
            {isDraftReady && session.draft_md && (
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-semibold">
                    AI-generated draft
                  </CardTitle>
                  <CardDescription className="text-xs">
                    Review the structured neuron below. Go back and edit the
                    fields above if anything is wrong, then re-extract.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <pre className="max-h-64 overflow-y-auto whitespace-pre-wrap rounded-md border border-border bg-bg-muted/50 p-3 font-mono text-xs leading-relaxed text-fg">
                    {session.draft_md}
                  </pre>
                </CardContent>
              </Card>
            )}

            {error && (
              <p className="text-sm text-danger">{error}</p>
            )}

            {/* Action bar */}
            <div className="flex flex-wrap gap-3 pt-2">
              {!isDraftReady && (
                <Button
                  onClick={handleExtract}
                  disabled={isExtracting || !situation.trim()}
                >
                  {isExtracting ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Sparkles className="mr-2 h-4 w-4" />
                  )}
                  {isExtracting ? "Extracting…" : "Extract neuron"}
                </Button>
              )}
              {isDraftReady && (
                <>
                  <Button
                    variant="outline"
                    onClick={handleExtract}
                    disabled={isExtracting}
                  >
                    {isExtracting ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <Sparkles className="mr-2 h-4 w-4" />
                    )}
                    Re-extract
                  </Button>
                  <Button
                    onClick={handleFinalize}
                    disabled={finalizing || highPii.length > 0}
                  >
                    {finalizing ? (
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    ) : (
                      <CheckCircle2 className="mr-2 h-4 w-4" />
                    )}
                    Publish neuron
                  </Button>
                </>
              )}
            </div>
            {isDraftReady && highPii.length > 0 && (
              <p className="text-xs text-warning">
                Resolve high-severity PII flags before publishing.
              </p>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

function Field({
  id,
  label,
  description,
  value,
  onChange,
  disabled,
  placeholder,
  rows = 5,
}: {
  id: string;
  label: string;
  description: string;
  value: string;
  onChange: (v: string) => void;
  disabled: boolean;
  placeholder?: string;
  rows?: number;
}) {
  return (
    <div className="space-y-1.5">
      <Label htmlFor={id} className="text-sm font-medium">
        {label}
      </Label>
      <p className="text-xs text-fg-subtle">{description}</p>
      <Textarea
        id={id}
        rows={rows}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        placeholder={placeholder}
        className="resize-y font-sans text-sm leading-relaxed"
      />
    </div>
  );
}
