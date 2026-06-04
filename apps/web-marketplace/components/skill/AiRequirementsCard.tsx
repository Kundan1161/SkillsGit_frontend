import { Cpu } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { AiRequirements } from "@/lib/api/catalog";

export interface AiRequirementsCardProps {
  ai: AiRequirements;
}

export function AiRequirementsCard({ ai }: AiRequirementsCardProps) {
  return (
    <Card className="border-none" style={{ borderRadius: "1.25rem", background: "var(--color-bg)", boxShadow: "var(--shadow-neu-md)" }}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-base">
          <Cpu className="h-4 w-4 text-fg-muted" /> AI requirements
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        {ai.required_models.length > 0 ? (
          <div>
            <p className="mb-1 text-xs text-fg-subtle">Required models</p>
            <div className="flex flex-wrap gap-1.5">
              {ai.required_models.map((m) => (
                <Badge key={m} variant="default" className="font-mono text-[11px]">
                  {m}
                </Badge>
              ))}
            </div>
          </div>
        ) : null}

        {ai.compatible_models.length > 0 ? (
          <div>
            <p className="mb-1 text-xs text-fg-subtle">Compatible</p>
            <div className="flex flex-wrap gap-1.5">
              {ai.compatible_models.map((m) => (
                <Badge key={m} variant="outline" className="font-mono text-[11px]">
                  {m}
                </Badge>
              ))}
            </div>
          </div>
        ) : null}

        {ai.tools_required.length > 0 ? (
          <div>
            <p className="mb-1 text-xs text-fg-subtle">Tools required</p>
            <ul className="text-xs text-fg">
              {ai.tools_required.map((t) => (
                <li key={t} className="font-mono">
                  · {t}
                </li>
              ))}
            </ul>
          </div>
        ) : null}

        {ai.min_context_tokens != null ? (
          <p className="text-xs text-fg-muted">
            Min context: {ai.min_context_tokens.toLocaleString()} tokens
          </p>
        ) : null}
        {ai.estimated_tokens_per_invocation != null ? (
          <p className="text-xs text-fg-muted">
            Est. tokens/invocation:{" "}
            {ai.estimated_tokens_per_invocation.toLocaleString()}
          </p>
        ) : null}
      </CardContent>
    </Card>
  );
}
