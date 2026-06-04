import { ExternalLink } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const MARKETPLACE_URL =
  process.env.NEXT_PUBLIC_MARKETPLACE_URL ?? "http://localhost:3000";

export default function SettingsPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main
        id="main"
        className="mx-auto w-full max-w-3xl flex-1 px-4 py-10 md:px-8"
      >
        <header>
          <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
            Settings
          </h1>
          <p className="mt-1 text-sm text-fg-muted">
            Profile, payouts, and notifications live in the marketplace app —
            both apps share the same account.
          </p>
        </header>

        <div className="mt-8 grid gap-4">
          {["Account", "Payouts", "Notifications", "API keys"].map((s) => (
            <Card key={s}>
              <CardHeader>
                <CardTitle className="text-base">{s}</CardTitle>
                <CardDescription>
                  Managed in the marketplace settings.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <a
                  href={`${MARKETPLACE_URL}/settings`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-sm font-medium text-brand-500 hover:underline"
                >
                  Open in marketplace
                  <ExternalLink className="h-3.5 w-3.5" />
                </a>
              </CardContent>
            </Card>
          ))}
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
