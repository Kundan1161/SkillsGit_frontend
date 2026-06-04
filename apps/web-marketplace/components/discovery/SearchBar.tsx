"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useCallback, useEffect, useRef } from "react";
import { Search } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export interface SearchBarProps {
  placeholder?: string;
  defaultValue?: string;
  redirectTo?: "search" | "browse";
}

export function SearchBar({
  placeholder = "Search skills, tags, creators…",
  defaultValue = "",
  redirectTo = "search",
}: SearchBarProps) {
  const router = useRouter();
  const params = useSearchParams();
  const [value, setValue] = useState(defaultValue || params.get("q") || "");
  const inputRef = useRef<HTMLInputElement>(null);

  // Keep value in sync if the URL changes externally.
  useEffect(() => {
    const next = params.get("q") ?? "";
    setValue(next);
  }, [params]);

  const onSubmit = useCallback(
    (e: React.FormEvent<HTMLFormElement>) => {
      e.preventDefault();
      const q = value.trim();
      const base = redirectTo === "browse" ? "/browse" : "/search";
      if (!q) {
        router.push(base);
        return;
      }
      router.push(`${base}?q=${encodeURIComponent(q)}`);
    },
    [router, value, redirectTo],
  );

  return (
    <form onSubmit={onSubmit} role="search" className="flex w-full max-w-2xl items-center gap-2">
      <div className="relative flex-1">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-fg-subtle" />
        <Input
          ref={inputRef}
          type="search"
          name="q"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder={placeholder}
          aria-label="Search skills"
          className="pl-9"
        />
      </div>
      <Button type="submit">Search</Button>
    </form>
  );
}
