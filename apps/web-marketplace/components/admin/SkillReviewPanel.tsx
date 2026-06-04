"use client";

import { useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { adminApi } from "@/lib/api/admin";

interface Props {
  skillId: string;
  onActed?: () => void;
}

export function SkillReviewPanel({ skillId, onActed }: Props) {
  const [busy, setBusy] = useState(false);
  const [reason, setReason] = useState("");

  async function approve() {
    setBusy(true);
    try {
      await adminApi.approveSkill(skillId);
      toast.success("Approved and published");
      onActed?.();
    } catch (e) {
      toast.error((e as { message?: string }).message ?? "Approval failed");
    } finally {
      setBusy(false);
    }
  }

  async function reject() {
    setBusy(true);
    try {
      await adminApi.rejectSkill(skillId, reason);
      toast.success("Sent back to creator");
      onActed?.();
    } catch (e) {
      toast.error((e as { message?: string }).message ?? "Rejection failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex gap-2">
      <Button variant="primary" onClick={approve} disabled={busy}>
        Approve & publish
      </Button>
      <Dialog>
        <DialogTrigger asChild>
          <Button variant="outline" disabled={busy}>
            Reject…
          </Button>
        </DialogTrigger>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Send back for changes</DialogTitle>
            <DialogDescription>
              Explain what the creator needs to fix. The skill stays in
              pending_review with the reason attached.
            </DialogDescription>
          </DialogHeader>
          <Textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="e.g. The body references stale model ids."
            rows={5}
          />
          <DialogFooter>
            <DialogClose asChild>
              <Button variant="ghost">Cancel</Button>
            </DialogClose>
            <Button
              variant="destructive"
              onClick={reject}
              disabled={busy || reason.trim().length === 0}
            >
              Send
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
