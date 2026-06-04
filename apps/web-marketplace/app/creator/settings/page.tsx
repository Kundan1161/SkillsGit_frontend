"use client"
import { useState } from "react"
import { CreatorShell } from "@/components/creator/CreatorShell"

const inputStyle = {
  background: "var(--color-bg)",
  boxShadow: "var(--shadow-neu-inset)",
  borderRadius: "1rem",
  border: "none",
  outline: "none",
  padding: "12px 16px",
  width: "100%",
  fontSize: "0.9rem",
  fontFamily: "inherit",
  color: "var(--color-fg)",
} as const;

function Toggle({ active, onToggle }: { active: boolean; onToggle: () => void }) {
  return (
    <button
      onClick={onToggle}
      style={{
        width: 44,
        height: 24,
        borderRadius: 12,
        background: "var(--color-bg)",
        boxShadow: active ? "var(--shadow-neu-inset-sm)" : "var(--shadow-neu-sm)",
        cursor: "pointer",
        position: "relative",
        border: "none",
      }}
    >
      <div
        style={{
          position: "absolute",
          top: 3,
          left: active ? 22 : 3,
          width: 18,
          height: 18,
          borderRadius: "50%",
          background: active ? "#7c3aed" : "var(--color-fg-subtle)",
          boxShadow: "var(--shadow-neu-xs)",
          transition: "all 0.2s ease",
        }}
      />
    </button>
  );
}

export default function SettingsPage() {
  const [name, setName] = useState("Marcus Webb");
  const [bio, setBio] = useState("DevOps expert with 12+ years in Kubernetes and cloud infrastructure.");
  const [notifSubscriber, setNotifSubscriber] = useState(true);
  const [notifQuestion, setNotifQuestion] = useState(true);
  const [notifReport, setNotifReport] = useState(false);
  const [notifPayout, setNotifPayout] = useState(true);

  return (
    <CreatorShell active="settings">
      <div className="flex flex-col gap-8 max-w-2xl">
        <div>
          <span className="tag-label block mb-2">Account</span>
          <h1 className="text-3xl font-black tracking-[-0.04em]" style={{ color: "var(--color-fg)" }}>
            Creator <span className="gradient-text">Settings</span>
          </h1>
        </div>

        {/* Profile */}
        <div className="neu-lg p-8 flex flex-col gap-5">
          <h2 className="text-base font-bold" style={{ color: "var(--color-fg)" }}>Profile</h2>

          {/* Avatar */}
          <div className="flex items-center gap-5">
            <div
              style={{
                width: 72, height: 72, borderRadius: "50%",
                background: "linear-gradient(135deg, #7c3aed, #6366f1)",
                display: "flex", alignItems: "center", justifyContent: "center",
                color: "white", fontWeight: 900, fontSize: 24,
                boxShadow: "var(--shadow-neu-md)",
              }}
            >
              MW
            </div>
            <button className="neu-btn px-5 py-2 text-sm font-semibold" style={{ color: "var(--color-fg-muted)" }}>
              Upload Avatar
            </button>
          </div>

          <div className="flex flex-col gap-2">
            <label className="tag-label">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              style={inputStyle}
            />
          </div>

          <div className="flex flex-col gap-2">
            <label className="tag-label">Bio</label>
            <textarea
              value={bio}
              onChange={e => setBio(e.target.value)}
              rows={3}
              style={{ ...inputStyle, resize: "none", lineHeight: 1.6 }}
            />
          </div>

          <button className="neu-btn-brand px-6 py-2.5 text-sm font-bold text-white w-fit">
            Save Profile
          </button>
        </div>

        {/* Notifications */}
        <div className="neu-lg p-8 flex flex-col gap-5">
          <h2 className="text-base font-bold" style={{ color: "var(--color-fg)" }}>Notifications</h2>
          {[
            { label: "New subscriber", desc: "When someone subscribes to your AI", active: notifSubscriber, toggle: () => setNotifSubscriber(v => !v) },
            { label: "Question asked", desc: "When a subscriber asks a question", active: notifQuestion, toggle: () => setNotifQuestion(v => !v) },
            { label: "Monthly report", desc: "Monthly earnings and usage summary", active: notifReport, toggle: () => setNotifReport(v => !v) },
            { label: "Payout received", desc: "When a payout is sent to your bank", active: notifPayout, toggle: () => setNotifPayout(v => !v) },
          ].map(item => (
            <div key={item.label} className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-semibold" style={{ color: "var(--color-fg)" }}>{item.label}</p>
                <p className="text-xs mt-0.5" style={{ color: "var(--color-fg-subtle)" }}>{item.desc}</p>
              </div>
              <Toggle active={item.active} onToggle={item.toggle} />
            </div>
          ))}
        </div>

        {/* Payout */}
        <div className="neu-lg p-8 flex flex-col gap-5">
          <h2 className="text-base font-bold" style={{ color: "var(--color-fg)" }}>Payout</h2>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div
                style={{
                  width: 10, height: 10, borderRadius: "50%",
                  background: "#10b981",
                  boxShadow: "0 0 6px rgba(16,185,129,0.5)",
                }}
              />
              <span className="text-sm font-semibold" style={{ color: "var(--color-fg)" }}>Bank account connected</span>
            </div>
            <button className="neu-btn px-5 py-2 text-sm font-semibold" style={{ color: "#7c3aed" }}>
              View in Stripe
            </button>
          </div>
        </div>

        {/* Danger zone */}
        <div className="neu-lg p-8 flex flex-col gap-4">
          <h2 className="text-base font-bold" style={{ color: "#ef4444" }}>Danger Zone</h2>
          <p className="text-sm" style={{ color: "var(--color-fg-muted)" }}>
            Permanently delete your account and all associated data. This cannot be undone.
          </p>
          <button
            className="neu-btn px-6 py-2.5 text-sm font-bold w-fit"
            style={{ color: "#ef4444", boxShadow: "4px 4px 10px rgba(239,68,68,0.15), -4px -4px 10px rgba(255,255,255,0.7)" }}
          >
            Delete Account
          </button>
        </div>
      </div>
    </CreatorShell>
  );
}
