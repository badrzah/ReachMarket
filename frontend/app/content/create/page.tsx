"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AuthLayout from "@/components/layout/AuthLayout";
import type { StrategyRecord, ContentType } from "@/types";

const CONTENT_TYPES = [
  { value: "cold_email", label: "Cold Email", icon: "✉️" },
  { value: "linkedin_post", label: "LinkedIn Post", icon: "💼" },
  { value: "blog_outline", label: "Blog Outline", icon: "📝" },
  { value: "ad_copy", label: "Ad Copy", icon: "📢" },
];

export default function CreateContentPage() {
  const router = useRouter();
  const [strategies, setStrategies] = useState<StrategyRecord[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState("");
  const [selectedTypes, setSelectedTypes] = useState<string[]>(["cold_email", "linkedin_post"]);
  const [countPerType, setCountPerType] = useState(3);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    const fetchStrategies = async () => {
      const token = localStorage.getItem("access_token");
      const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      try {
        const res = await fetch(`${base}/api/v1/strategy/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        const completed = (data.strategies || []).filter((s: any) => s.status === "complete");
        setStrategies(completed);
        if (completed.length > 0) setSelectedStrategy(completed[0].id);
      } catch {}
    };
    fetchStrategies();
  }, []);

  const toggleType = (type: string) => {
    setSelectedTypes((prev) =>
      prev.includes(type) ? prev.filter((t) => t !== type) : [...prev, type]
    );
  };

  const handleGenerate = async () => {
    if (!selectedStrategy || selectedTypes.length === 0) return;
    setLoading(true);
    setResult(null);

    const token = localStorage.getItem("access_token");
    const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

    try {
      const res = await fetch(`${base}/api/v1/content/generate`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          strategy_id: selectedStrategy,
          content_types: selectedTypes,
          count_per_type: countPerType,
        }),
      });
      const data = await res.json();
      setResult(data);
    } catch {}
    setLoading(false);
  };

  return (
    <AuthLayout>
      <div className="max-w-3xl animate-fade-in">
        <h1 className="text-2xl font-bold mb-1">Generate Content</h1>
        <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
          Create brand-aligned content from an existing strategy
        </p>

        <div className="glass-card p-6 space-y-6">
          <div>
            <label className="label">Select Strategy</label>
            <select
              className="select"
              value={selectedStrategy}
              onChange={(e) => setSelectedStrategy(e.target.value)}
            >
              <option value="">Choose a completed strategy...</option>
              {strategies.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.payload?.positioning_statement?.slice(0, 50) || `Strategy ${s.id.slice(0, 8)}`}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="label">Content Types</label>
            <div className="grid grid-cols-2 gap-3">
              {CONTENT_TYPES.map((ct) => (
                <button
                  key={ct.value}
                  onClick={() => toggleType(ct.value)}
                  className="p-3 rounded-lg text-sm font-medium text-left transition-all flex items-center gap-2"
                  style={{
                    background: selectedTypes.includes(ct.value)
                      ? "rgba(124,58,237,0.15)"
                      : "var(--bg-tertiary)",
                    border: `1px solid ${selectedTypes.includes(ct.value) ? "var(--accent-purple)" : "var(--border-light)"}`,
                    color: selectedTypes.includes(ct.value) ? "var(--text-primary)" : "var(--text-secondary)",
                  }}
                >
                  <span>{ct.icon}</span>
                  {ct.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="label">Count per Type: {countPerType}</label>
            <input
              type="range"
              min={1}
              max={5}
              value={countPerType}
              onChange={(e) => setCountPerType(parseInt(e.target.value))}
              className="w-full"
              style={{ accentColor: "var(--accent-purple)" }}
            />
            <div className="flex justify-between text-xs" style={{ color: "var(--text-muted)" }}>
              <span>1</span><span>2</span><span>3</span><span>4</span><span>5</span>
            </div>
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !selectedStrategy || selectedTypes.length === 0}
            className="btn-primary w-full py-3"
          >
            {loading ? <><span className="spinner" /> Generating...</> : "⚡ Generate Content"}
          </button>
        </div>

        {result && result.assets && (
          <div className="mt-6 space-y-3 animate-slide-up">
            <h2 className="text-lg font-semibold">
              Generated {result.assets.length} assets
            </h2>
            {result.assets.map((asset: any, i: number) => (
              <div key={i} className="glass-card p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="badge badge-complete">{asset.content_type?.replace(/_/g, " ")}</span>
                  <span className="text-sm font-medium">{asset.title?.slice(0, 60)}</span>
                </div>
                <p className="text-sm whitespace-pre-wrap" style={{ color: "var(--text-secondary)" }}>
                  {asset.body?.slice(0, 300)}{asset.body?.length > 300 ? "..." : ""}
                </p>
              </div>
            ))}
            <button onClick={() => router.push("/content")} className="btn-secondary w-full">
              View Content Library →
            </button>
          </div>
        )}
      </div>
    </AuthLayout>
  );
}
