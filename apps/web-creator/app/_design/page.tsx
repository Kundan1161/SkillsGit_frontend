"use client";

import { Inbox } from "lucide-react";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Spinner } from "@/components/ui/spinner";
import { Banner } from "@/components/ui/banner";
import { EmptyState } from "@/components/ui/empty-state";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

/**
 * Kitchen-sink page. Visual regression surface for every Phase 0 primitive.
 * Mirrors the marketplace `/_design` page; this one renders dark by default.
 */
export default function DesignKitchenSinkPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <SiteHeader />
      <main
        id="main"
        className="mx-auto w-full max-w-5xl flex-1 space-y-12 px-4 py-10 md:px-8"
      >
        <header>
          <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
            Design kitchen sink
          </h1>
          <p className="mt-1 text-sm text-fg-muted">
            Every Phase 0 primitive on one page, dark-default for the creator
            app.
          </p>
        </header>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">Buttons</h2>
          <div className="flex flex-wrap items-center gap-2">
            <Button>Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="link">Link</Button>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button size="sm">Small</Button>
            <Button size="md">Medium</Button>
            <Button size="lg">Large</Button>
            <Button size="icon" aria-label="Icon">
              <Inbox className="h-4 w-4" />
            </Button>
          </div>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">Badges</h2>
          <div className="flex flex-wrap gap-2">
            <Badge>Default</Badge>
            <Badge variant="secondary">Secondary</Badge>
            <Badge variant="outline">Outline</Badge>
            <Badge variant="success">Success</Badge>
            <Badge variant="warning">Warning</Badge>
            <Badge variant="danger">Danger</Badge>
            <Badge variant="info">Info</Badge>
          </div>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">Inputs</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="kx-name">Name</Label>
              <Input id="kx-name" placeholder="Ada Lovelace" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="kx-bio">Bio</Label>
              <Textarea id="kx-bio" placeholder="Tell us about yourself…" />
            </div>
            <div className="space-y-2">
              <Label>Category</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Pick one" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="finance">Finance</SelectItem>
                  <SelectItem value="design">Design</SelectItem>
                  <SelectItem value="marketing">Marketing</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-3 pt-6">
              <Checkbox id="kx-tos" />
              <Label htmlFor="kx-tos">Accept terms</Label>
              <Switch id="kx-notify" />
              <Label htmlFor="kx-notify">Notifications</Label>
            </div>
            <div>
              <Label>Plan</Label>
              <RadioGroup defaultValue="one" className="mt-2">
                <div className="flex items-center gap-2">
                  <RadioGroupItem id="kx-one" value="one" />
                  <Label htmlFor="kx-one">One-time</Label>
                </div>
                <div className="flex items-center gap-2">
                  <RadioGroupItem id="kx-sub" value="sub" />
                  <Label htmlFor="kx-sub">Subscription</Label>
                </div>
              </RadioGroup>
            </div>
            <div>
              <Label>Slider</Label>
              <Slider defaultValue={[40]} max={100} step={1} className="mt-3" />
            </div>
          </div>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">Cards</h2>
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Card title</CardTitle>
                <CardDescription>
                  A short description goes here.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-fg-muted">
                  Cards are the building block for most list surfaces.
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Another card</CardTitle>
                <CardDescription>With actions.</CardDescription>
              </CardHeader>
              <CardContent className="flex gap-2">
                <Button size="sm">Confirm</Button>
                <Button size="sm" variant="ghost">
                  Cancel
                </Button>
              </CardContent>
            </Card>
          </div>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">Tabs & accordion</h2>
          <Tabs defaultValue="a">
            <TabsList>
              <TabsTrigger value="a">First</TabsTrigger>
              <TabsTrigger value="b">Second</TabsTrigger>
            </TabsList>
            <TabsContent value="a">
              <p className="py-2 text-sm text-fg-muted">First tab content.</p>
            </TabsContent>
            <TabsContent value="b">
              <p className="py-2 text-sm text-fg-muted">Second tab content.</p>
            </TabsContent>
          </Tabs>
          <Accordion type="single" collapsible className="w-full">
            <AccordionItem value="i1">
              <AccordionTrigger>What is skillsgit?</AccordionTrigger>
              <AccordionContent>
                A two-sided marketplace for AI skills.
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="i2">
              <AccordionTrigger>Who is this for?</AccordionTrigger>
              <AccordionContent>
                Professionals who want to publish their expertise as a skill.
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">Feedback</h2>
          <div className="space-y-3">
            <Banner variant="info">An informational banner.</Banner>
            <Banner variant="success">Saved successfully.</Banner>
            <Banner variant="warning">Heads up — needs review.</Banner>
            <Banner variant="danger">Something went wrong.</Banner>
          </div>
          <div className="flex items-center gap-3">
            <Progress value={42} className="w-48" />
            <Spinner />
            <Skeleton className="h-6 w-32" />
          </div>
        </section>

        <section className="space-y-3">
          <h2 className="text-xl font-semibold">Empty state</h2>
          <EmptyState
            icon={<Inbox aria-hidden />}
            title="Nothing here yet"
            description="Empty states are friendly, not blank."
            action={<Button size="sm">Get started</Button>}
          />
        </section>

        <Separator />
        <p className="text-xs text-fg-subtle">End of kitchen sink.</p>
      </main>
      <SiteFooter />
    </div>
  );
}
