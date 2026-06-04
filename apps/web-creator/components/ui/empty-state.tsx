import * as React from "react";
import { cn } from "@/lib/utils";

interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  className,
  ...props
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-bg-muted/40 px-6 py-12 text-center",
        className,
      )}
      {...props}
    >
      {icon ? (
        <div className="mb-4 text-fg-subtle [&>svg]:h-10 [&>svg]:w-10">
          {icon}
        </div>
      ) : null}
      <h3 className="text-base font-semibold text-fg">{title}</h3>
      {description ? (
        <p className="mt-1 max-w-sm text-sm text-fg-muted">{description}</p>
      ) : null}
      {action ? <div className="mt-6">{action}</div> : null}
    </div>
  );
}
