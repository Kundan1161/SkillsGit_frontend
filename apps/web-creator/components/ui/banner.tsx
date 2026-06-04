import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const bannerVariants = cva(
  "flex items-start gap-3 rounded-md border px-4 py-3 text-sm",
  {
    variants: {
      variant: {
        info: "border-info/30 bg-info/10 text-info",
        success: "border-success/30 bg-success/10 text-success",
        warning: "border-warning/30 bg-warning/10 text-warning",
        danger: "border-danger/30 bg-danger/10 text-danger",
        neutral: "border-border bg-bg-muted text-fg",
      },
    },
    defaultVariants: { variant: "info" },
  },
);

export interface BannerProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof bannerVariants> {
  icon?: React.ReactNode;
}

export function Banner({
  className,
  variant,
  icon,
  children,
  ...props
}: BannerProps) {
  return (
    <div
      role="status"
      className={cn(bannerVariants({ variant }), className)}
      {...props}
    >
      {icon ? <div className="mt-0.5 shrink-0">{icon}</div> : null}
      <div className="flex-1">{children}</div>
    </div>
  );
}
