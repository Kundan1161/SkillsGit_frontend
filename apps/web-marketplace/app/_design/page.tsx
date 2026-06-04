"use client";

import * as React from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Info,
  Loader2,
  Settings,
  Terminal,
  XCircle,
} from "lucide-react";
import { toast } from "sonner";

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Skeleton } from "@/components/ui/skeleton";
import { Slider } from "@/components/ui/slider";
import { Spinner } from "@/components/ui/spinner";
import { Switch } from "@/components/ui/switch";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import { ThemeToggle } from "@/components/theme-toggle";

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="space-y-4">
      <h2 className="text-xl font-semibold">{title}</h2>
      <div className="rounded-lg border border-border bg-bg-raised p-6">
        {children}
      </div>
    </section>
  );
}

export default function DesignPage() {
  return (
    <div className="mx-auto max-w-7xl space-y-12 px-4 py-16 md:px-8">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight md:text-4xl">
          Design kitchen sink
        </h1>
        <p className="mt-2 text-fg-muted">
          Every Phase 0 component in one place. Used for visual regression
          review and quick reference.
        </p>
      </header>

      <Section title="Theme">
        <div className="flex items-center gap-3">
          <ThemeToggle />
          <span className="text-sm text-fg-muted">
            Toggle light/dark via next-themes
          </span>
        </div>
      </Section>

      <Section title="Buttons">
        <div className="space-y-4">
          <div className="flex flex-wrap gap-3">
            <Button variant="primary">Primary</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="destructive">Destructive</Button>
            <Button variant="link">Link</Button>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button size="sm">Small</Button>
            <Button size="md">Medium</Button>
            <Button size="lg">Large</Button>
            <Button size="icon" aria-label="settings">
              <Settings />
            </Button>
            <Button disabled>Disabled</Button>
            <Button>
              <Loader2 className="animate-spin" />
              Loading
            </Button>
          </div>
        </div>
      </Section>

      <Section title="Inputs / Forms">
        <div className="grid gap-6 md:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="ks-email">Email</Label>
            <Input id="ks-email" type="email" placeholder="you@example.com" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="ks-textarea">Bio</Label>
            <Textarea id="ks-textarea" placeholder="A short bio" />
          </div>
          <div className="space-y-2">
            <Label>Plan</Label>
            <Select>
              <SelectTrigger>
                <SelectValue placeholder="Pick a plan" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="free">Free</SelectItem>
                <SelectItem value="pro">Pro</SelectItem>
                <SelectItem value="team">Team</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>Volume</Label>
            <Slider defaultValue={[40]} max={100} step={1} />
          </div>
          <div className="flex items-center gap-2">
            <Checkbox id="ks-check" />
            <Label htmlFor="ks-check">I agree to the terms</Label>
          </div>
          <div className="flex items-center gap-2">
            <Switch id="ks-switch" />
            <Label htmlFor="ks-switch">Email notifications</Label>
          </div>
          <RadioGroup defaultValue="m">
            <div className="flex items-center gap-2">
              <RadioGroupItem value="m" id="ks-r-m" />
              <Label htmlFor="ks-r-m">Monthly</Label>
            </div>
            <div className="flex items-center gap-2">
              <RadioGroupItem value="y" id="ks-r-y" />
              <Label htmlFor="ks-r-y">Yearly</Label>
            </div>
          </RadioGroup>
        </div>
      </Section>

      <Section title="Cards">
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Project Alpha</CardTitle>
              <CardDescription>Onboarding scorecard</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-fg-muted">
                A standard card with header, content, and footer slots.
              </p>
            </CardContent>
            <CardFooter className="justify-end gap-2">
              <Button variant="ghost" size="sm">
                Cancel
              </Button>
              <Button size="sm">Save</Button>
            </CardFooter>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Quiet card</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm">Minimal variant.</p>
            </CardContent>
          </Card>
        </div>
      </Section>

      <Section title="Dialog / Sheet / Popover">
        <div className="flex flex-wrap gap-3">
          <Dialog>
            <DialogTrigger asChild>
              <Button>Open dialog</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Confirm action</DialogTitle>
                <DialogDescription>
                  This will trigger nothing — pure visual demo.
                </DialogDescription>
              </DialogHeader>
              <DialogFooter>
                <Button variant="outline">Cancel</Button>
                <Button>Confirm</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          <Sheet>
            <SheetTrigger asChild>
              <Button variant="outline">Open sheet</Button>
            </SheetTrigger>
            <SheetContent>
              <SheetHeader>
                <SheetTitle>Filters</SheetTitle>
                <SheetDescription>
                  Right-side drawer for filtering.
                </SheetDescription>
              </SheetHeader>
            </SheetContent>
          </Sheet>

          <Popover>
            <PopoverTrigger asChild>
              <Button variant="secondary">Open popover</Button>
            </PopoverTrigger>
            <PopoverContent>
              <p className="text-sm">Tiny floating panel.</p>
            </PopoverContent>
          </Popover>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost">Dropdown</Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuLabel>Account</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Profile</DropdownMenuItem>
              <DropdownMenuItem>Settings</DropdownMenuItem>
              <DropdownMenuItem>Sign out</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </Section>

      <Section title="Tabs / Accordion / Collapsible">
        <div className="grid gap-6 md:grid-cols-2">
          <Tabs defaultValue="overview">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="usage">Usage</TabsTrigger>
              <TabsTrigger value="reviews">Reviews</TabsTrigger>
            </TabsList>
            <TabsContent value="overview">
              <p className="text-sm text-fg-muted">Tab one content.</p>
            </TabsContent>
            <TabsContent value="usage">
              <p className="text-sm text-fg-muted">Tab two content.</p>
            </TabsContent>
            <TabsContent value="reviews">
              <p className="text-sm text-fg-muted">Tab three content.</p>
            </TabsContent>
          </Tabs>

          <Accordion type="single" collapsible>
            <AccordionItem value="a">
              <AccordionTrigger>What is a skill?</AccordionTrigger>
              <AccordionContent>
                A skill is a single skills.md file with structured frontmatter.
              </AccordionContent>
            </AccordionItem>
            <AccordionItem value="b">
              <AccordionTrigger>How do I publish?</AccordionTrigger>
              <AccordionContent>
                Upload the file from the creator dashboard.
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>

        <Separator className="my-6" />

        <Collapsible>
          <CollapsibleTrigger asChild>
            <Button variant="outline" size="sm">
              Toggle details
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-3 text-sm text-fg-muted">
            Hidden until toggled.
          </CollapsibleContent>
        </Collapsible>
      </Section>

      <Section title="Tooltips">
        <div className="flex gap-3">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="outline">Hover me</Button>
            </TooltipTrigger>
            <TooltipContent>This is a tooltip.</TooltipContent>
          </Tooltip>
        </div>
      </Section>

      <Section title="Badges">
        <div className="flex flex-wrap gap-2">
          <Badge>Default</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="outline">Outline</Badge>
          <Badge variant="success">Active</Badge>
          <Badge variant="warning">Pending</Badge>
          <Badge variant="danger">Failed</Badge>
          <Badge variant="info">Info</Badge>
        </div>
      </Section>

      <Section title="Avatars">
        <div className="flex gap-3">
          <Avatar>
            <AvatarImage
              src="https://avatars.githubusercontent.com/u/1?v=4"
              alt="User"
            />
            <AvatarFallback>JD</AvatarFallback>
          </Avatar>
          <Avatar>
            <AvatarFallback>AK</AvatarFallback>
          </Avatar>
        </div>
      </Section>

      <Section title="Tables">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Skill</TableHead>
              <TableHead>Price</TableHead>
              <TableHead>Rating</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow>
              <TableCell>DCF Valuation</TableCell>
              <TableCell className="text-price">$19</TableCell>
              <TableCell>4.9</TableCell>
            </TableRow>
            <TableRow>
              <TableCell>Incident Postmortem</TableCell>
              <TableCell className="text-price">$12</TableCell>
              <TableCell>4.8</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </Section>

      <Section title="Breadcrumb">
        <Breadcrumb>
          <BreadcrumbList>
            <BreadcrumbItem>
              <BreadcrumbLink href="/">Home</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbLink href="/browse">Browse</BreadcrumbLink>
            </BreadcrumbItem>
            <BreadcrumbSeparator />
            <BreadcrumbItem>
              <BreadcrumbPage>DCF Valuation</BreadcrumbPage>
            </BreadcrumbItem>
          </BreadcrumbList>
        </Breadcrumb>
      </Section>

      <Section title="Toasts">
        <div className="flex flex-wrap gap-2">
          <Button
            variant="outline"
            onClick={() => toast("Saved.", { description: "All good." })}
          >
            Default
          </Button>
          <Button
            variant="outline"
            onClick={() => toast.success("License granted")}
          >
            Success
          </Button>
          <Button
            variant="outline"
            onClick={() => toast.error("Payment failed")}
          >
            Error
          </Button>
        </div>
      </Section>

      <Section title="Skeletons / Spinner">
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <Skeleton className="h-10 w-10 rounded-full" />
            <div className="space-y-2">
              <Skeleton className="h-3 w-40" />
              <Skeleton className="h-3 w-24" />
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Spinner size="sm" />
            <Spinner size="md" />
            <Spinner size="lg" />
          </div>
        </div>
      </Section>

      <Section title="Alerts">
        <div className="space-y-3">
          <Alert>
            <Terminal />
            <AlertTitle>Heads up</AlertTitle>
            <AlertDescription>This is a default alert.</AlertDescription>
          </Alert>
          <Alert variant="info">
            <Info />
            <AlertTitle>FYI</AlertTitle>
            <AlertDescription>An informational alert.</AlertDescription>
          </Alert>
          <Alert variant="success">
            <CheckCircle2 />
            <AlertTitle>All good</AlertTitle>
            <AlertDescription>Changes saved successfully.</AlertDescription>
          </Alert>
          <Alert variant="warning">
            <AlertTriangle />
            <AlertTitle>Heads up</AlertTitle>
            <AlertDescription>You may want to review this.</AlertDescription>
          </Alert>
          <Alert variant="destructive">
            <XCircle />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>Something went wrong.</AlertDescription>
          </Alert>
        </div>
      </Section>
    </div>
  );
}
