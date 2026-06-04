import Link from "next/link";
import { Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function SignUpPage() {
  return (
    <main
      id="main"
      className="flex min-h-screen items-center justify-center bg-bg px-4 py-12"
    >
      <Card className="w-full max-w-sm">
        <CardHeader className="items-center space-y-2">
          <Sparkles className="h-6 w-6 text-brand-500" aria-hidden />
          <h1 className="text-xl font-semibold tracking-tight">
            Create your account
          </h1>
          <p className="text-center text-sm text-fg-muted">
            Free to start building. Pay only when you sell.
          </p>
        </CardHeader>
        <CardContent>
          <form className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                type="text"
                placeholder="Ada Lovelace"
                autoComplete="name"
                required
              />
            </div>
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
                placeholder="At least 12 characters"
                autoComplete="new-password"
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled>
              Create account (Phase 2)
            </Button>
          </form>
          <p className="mt-4 text-center text-xs text-fg-muted">
            Already have one?{" "}
            <Link
              href="/sign-in"
              className="font-medium text-brand-500 hover:underline"
            >
              Sign in
            </Link>
          </p>
        </CardContent>
      </Card>
    </main>
  );
}
