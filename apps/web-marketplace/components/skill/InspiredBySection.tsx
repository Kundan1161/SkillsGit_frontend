import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export interface InspiredBySectionProps {
  urls: string[];
}

export function InspiredBySection({ urls }: InspiredBySectionProps) {
  if (urls.length === 0) {
    return (
      <p className="text-sm text-fg-muted">
        No repository references are available for this skill yet.
      </p>
    );
  }

  return (
    <Card className="border-none shadow-md" style={{ borderRadius: "1.25rem", background: "var(--color-bg)" }}>
      <CardHeader>
        <CardTitle className="text-base">Inspired by</CardTitle>
        <p className="text-sm text-fg-muted">
          Public repository pages reviewed during synthesis of this skill.
        </p>
      </CardHeader>
      <CardContent>
        <ul className="space-y-3">
          {urls.map((url) => (
            <li key={url}>
              <a
                href={url}
                target="_blank"
                rel="noreferrer"
                className="break-all text-sm text-brand-500 hover:underline"
              >
                {url}
              </a>
            </li>
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}
