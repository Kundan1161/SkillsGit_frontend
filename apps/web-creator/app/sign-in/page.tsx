import Link from "next/link";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function SignInPage() {
  return (
    <main
      id="main"
      className="flex min-h-screen items-center justify-center bg-bg px-4 py-12"
    >
      <Card className="w-full max-w-sm">
        <CardHeader className="items-center space-y-2">
          <Sparkles className="h-6 w-6 text-brand-500" aria-hidden />
          <h1 className="text-xl font-semibold tracking-tight">
            Sign in to Studio
          </h1>
          <p className="text-center text-sm text-fg-muted">
            Same account works on the marketplace.
          </p>
        </CardHeader>
        <CardContent>
          <form className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                autoComplete="email"
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="••••••••"
                autoComplete="current-password"
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled>
              Sign in (Phase 2)
            </Button>
          </form>
          <p className="mt-4 text-center text-xs text-fg-muted">
            No account?{" "}
            <Link
              href="/sign-up"
              className="font-medium text-brand-500 hover:underline"
            >
              Sign up
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
