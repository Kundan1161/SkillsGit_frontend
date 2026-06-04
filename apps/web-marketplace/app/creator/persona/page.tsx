"use client";
import { useState } from "react";
import { Star } from "lucide-react";
import { CreatorShell } from "@/components/creator/CreatorShell";

const categories = ["Engineering", "Healthcare", "Finance", "Legal", "Design", "Culinary", "Education", "Fitness"];
const communicationStyles = ["Formal", "Balanced", "Conversational"];
const detailLevels = ["Concise", "Standard", "Comprehensive"];

export default function PersonaPage() {
  const [name, setName] = useState("Marcus Webb");
  const [category, setCategory] = useState("Engineering");
  const [years, setYears] = useState(12);
  const [style, setStyle] = useState("Balanced");
  const [detail, setDetail] = useState("Standard");
  const [creativity, setCreativity] = useState(65);
  const [confidence, setConfidence] = useState(80);
  const [safety, setSafety] = useState(true);
  const [bio, setBio] = useState("12+ years architecting production Kubernetes clusters and DevOps pipelines. I specialize in making complex infrastructure approachable and reliable.");

  return (
    <CreatorShell active="persona">
      <div className="mx-auto max-w-5xl">
        <div className="mb-10">
          <span className="tag-label block mb-2">AI Configuration</span>
          <h1 className="text-3xl font-black tracking-[-0.04em]" style={{ color: "var(--color-fg)" }}>
            Persona <span className="gradient-text">Builder</span>
          </h1>
        </div>

        <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_360px]">
          {/* Form */}
          <div className="neu-lg p-8 flex flex-col gap-7">

            {/* Name */}
            <div className="flex flex-col gap-2">
              <label className="tag-label">Expert Name</label>
              <div className="neu-inset px-4 py-3" style={{ borderRadius: "var(--radius-xl)" }}>
                <input
                  type="text"
                  value={name}
                  onChange={e => setName(e.target.value)}
                  className="w-full bg-transparent text-base font-semibold outline-none"
                  style={{ color: "var(--color-fg)" }}
                />
              </div>
            </div>

            {/* Category */}
            <div className="flex flex-col gap-2">
              <label className="tag-label">Category</label>
              <div className="neu-inset px-4 py-3" style={{ borderRadius: "var(--radius-xl)" }}>
                <select
                  value={category}
                  onChange={e => setCategory(e.target.value)}
                  className="w-full bg-transparent text-base font-semibold outline-none"
                  style={{ color: "var(--color-fg)", background: "transparent" }}
                >
                  {categories.map(c => <option key={c} value={c} style={{ background: "var(--color-bg)" }}>{c}</option>)}
                </select>
              </div>
            </div>

            {/* Years of experience */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <label className="tag-label">Years of Experience</label>
                <span className="text-sm font-bold gradient-text">{years} years</span>
              </div>
              <div className="neu-inset px-4 py-3" style={{ borderRadius: "var(--radius-xl)" }}>
                <input type="range" min={1} max={40} value={years} onChange={e => setYears(Number(e.target.value))} className="w-full accent-purple-600" />
              </div>
            </div>

            {/* Communication style */}
            <div className="flex flex-col gap-3">
              <label className="tag-label">Communication Style</label>
              <div className="flex gap-3">
                {communicationStyles.map(s => (
                  <button
                    key={s}
                    onClick={() => setStyle(s)}
                    className={style === s ? "neu-btn-brand flex-1 py-2.5 text-sm font-bold text-white" : "neu-btn flex-1 py-2.5 text-sm font-semibold"}
                    style={style !== s ? { color: "var(--color-fg-muted)" } : {}}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>

            {/* Bio */}
            <div className="flex flex-col gap-2">
              <label className="tag-label">Bio</label>
              <div className="neu-inset px-4 py-3" style={{ borderRadius: "var(--radius-xl)" }}>
                <textarea
                  value={bio}
                  onChange={e => setBio(e.target.value)}
                  rows={3}
                  className="w-full bg-transparent text-sm leading-relaxed outline-none resize-none"
                  style={{ color: "var(--color-fg)" }}
                />
              </div>
            </div>

            {/* Creativity */}
            <div className="flex flex-col gap-3">
              <div className="flex items-center justify-between">
                <label className="tag-label">Creativity Level</label>
                <span className="text-sm font-bold gradient-text">{creativity}</span>
              </div>
              <div className="neu-inset px-4 py-3" style={{ borderRadius: "var(--radius-xl)" }}>
                <input type="range" min={0} max={100} value={creativity} onChange={e => setCreativity(Number(e.target.value))} className="w-full accent-purple-600" />
              </div>
            </div>

            {/* Detail level */}
            <div className="flex flex-col gap-3">
              <label className="tag-label">Detail Level</label>
              <div className="flex gap-3">
                {detailLevels.map(d => (
                  <button
                    key={d}
                    onClick={() => setDetail(d)}
                    className={detail === d ? "neu-btn-brand flex-1 py-2.5 text-sm font-bold text-white" : "neu-btn flex-1 py-2.5 text-sm font-semibold"}
                    style={detail !== d ? { color: "var(--color-fg-muted)" } : {}}
                  >
                    {d}
                  </button>
                ))}
              </div>
            </div>

            {/* Safety + Confidence */}
            <div className="grid grid-cols-2 gap-6">
              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <label className="tag-label">Safety Strictness</label>
                </div>
                <button
                  onClick={() => setSafety(!safety)}
                  className="relative flex h-8 w-14 items-center"
                  style={{
                    background: safety ? "linear-gradient(135deg, #7c3aed, #6366f1)" : "var(--color-bg)",
                    boxShadow: safety ? "6px 6px 16px rgba(124,58,237,0.3), -4px -4px 12px rgba(255,255,255,0.5)" : "var(--shadow-neu-inset)",
                    borderRadius: "9999px",
                    border: "none",
                    cursor: "pointer",
                    transition: "all 0.3s ease",
                  }}
                >
                  <div
                    style={{
                      position: "absolute",
                      width: 22, height: 22, borderRadius: "50%",
                      background: "white",
                      boxShadow: "2px 2px 6px rgba(0,0,0,0.2)",
                      left: safety ? "calc(100% - 26px)" : 4,
                      transition: "left 0.3s ease",
                    }}
                  />
                </button>
              </div>

              <div className="flex flex-col gap-3">
                <div className="flex items-center justify-between">
                  <label className="tag-label">Confidence Threshold</label>
                  <span className="text-sm font-bold gradient-text">{confidence}%</span>
                </div>
                <div className="neu-inset px-3 py-2" style={{ borderRadius: "var(--radius-lg)" }}>
                  <input type="range" min={50} max={100} value={confidence} onChange={e => setConfidence(Number(e.target.value))} className="w-full accent-purple-600" />
                </div>
              </div>
            </div>

            <button className="neu-btn-brand px-8 py-3.5 text-sm font-bold text-white w-fit mt-2">
              Save Persona
            </button>
          </div>

          {/* Preview panel */}
          <aside className="flex flex-col gap-4">
            <p className="tag-label">Live Preview</p>
            <div className="neu-lg p-6 flex flex-col gap-5">
              <div className="flex items-center gap-4">
                <div style={{ width: 72, height: 72, borderRadius: "50%", background: "linear-gradient(135deg, #7c3aed, #6366f1)", boxShadow: "var(--shadow-neu-sm)", display: "flex", alignItems: "center", justifyContent: "center", color: "white", fontWeight: 900, fontSize: 24 }}>
                  {name.split(" ").map(n => n[0]).join("").slice(0, 2)}
                </div>
                <div>
                  <h3 className="text-base font-bold" style={{ color: "var(--color-fg)" }}>{name || "Your Name"}</h3>
                  <span className="tag-label">{category}</span>
                  <div className="flex items-center gap-1 mt-1">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star key={i} className="h-3 w-3" style={{ color: "#f59e0b", fill: "#f59e0b" }} />
                    ))}
                  </div>
                </div>
              </div>

              <div className="neu-inset p-4" style={{ borderRadius: "var(--radius-lg)" }}>
                <p className="text-xs leading-relaxed" style={{ color: "var(--color-fg-muted)" }}>{bio}</p>
              </div>

              <div className="flex flex-wrap gap-2">
                <span className="neu-sm px-3 py-1 text-xs font-semibold" style={{ borderRadius: "9999px", color: "var(--color-fg-muted)" }}>{years} years exp.</span>
                <span className="neu-sm px-3 py-1 text-xs font-semibold" style={{ borderRadius: "9999px", color: "var(--color-fg-muted)" }}>{style}</span>
                <span className="neu-sm px-3 py-1 text-xs font-semibold" style={{ borderRadius: "9999px", color: "var(--color-fg-muted)" }}>{detail} detail</span>
              </div>

              <div className="neu-inset p-4" style={{ borderRadius: "var(--radius-lg)" }}>
                <p className="tag-label mb-2">Sample Response</p>
                <p className="text-xs leading-relaxed" style={{ color: "var(--color-fg-muted)" }}>
                  Based on my {years}+ years in {category.toLowerCase()}, I can help you navigate this challenge. Let me break it down clearly...
                </p>
              </div>
            </div>
          </aside>
        </div>
      </div>
    </CreatorShell>
  );
}
