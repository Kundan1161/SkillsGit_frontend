import Link from "next/link";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function SignUpPage() {
  return (
    <section className="mx-auto flex max-w-md flex-col px-4 py-16 md:px-0">
      <Card>
        <CardHeader>
          <CardTitle>Create your account</CardTitle>
          <CardDescription>
            Start buying skills (or shipping your own). Auth wiring lands in
            Phase 1.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="name">Name</Label>
            <Input
              id="name"
              autoComplete="name"
              placeholder="Jane Doe"
              disabled
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              placeholder="you@example.com"
              disabled
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              autoComplete="new-password"
              placeholder="At least 12 characters"
              disabled
            />
          </div>
        </CardContent>
        <CardFooter className="flex flex-col gap-3">
          <Button disabled className="w-full">
            Create account
          </Button>
          <p className="text-sm text-fg-muted">
            Already have one?{" "}
            <Link href="/sign-in" className="text-brand-500 hover:underline">
              Sign in
            </Link>
          </p>
        </CardFooter>
      </Card>
    </section>
  );
}
