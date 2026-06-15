"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import AuthLayout from "@/components/layout/AuthLayout";
import { AgentProgress } from "@/components/agent/AgentProgress";
import { authFetch } from "@/lib/auth-fetch";
import type { CompanyProfile, AgentEvent } from "@/types";

const INDUSTRIES = [
  "SaaS", "FinTech", "HealthTech", "EdTech", "E-Commerce", "AI/ML",
  "Cybersecurity", "MarTech", "HRTech", "DevTools", "CleanTech", "Other",
];

const STAGES = [
  { value: "seed", label: "Seed" },
  { value: "series_a", label: "Series A" },
  { value: "series_b", label: "Series B" },
  { value: "growth", label: "Growth" },
];

export default function NewStrategyPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState(false);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [strategyId, setStrategyId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<CompanyProfile & { additional_context: string }>({
    name: "",
    industry: "SaaS",
    stage: "seed",
    description: "",
    website: "",
    founded_year: null,
    additional_context: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setEvents([]);
    setError(null);

    const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

    try {
      // Step 1: Create strategy
      const res = await authFetch(`${base}/api/v1/strategy/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_profile: {
            name: form.name,
            industry: form.industry,
            stage: form.stage,
            description: form.description,
            website: form.website || null,
            founded_year: form.founded_year,
          },
          additional_context: form.additional_context || null,
        }),
      });

      const data = await res.json();
      setStrategyId(data.strategy_id);
      setStreaming(true);

      // Step 2: Listen to SSE stream
      const profileJson = encodeURIComponent(JSON.stringify(form));
      const ctx = form.additional_context ? encodeURIComponent(form.additional_context) : "";
      const currentToken = localStorage.getItem("access_token") || "";
      const streamUrl = `${base}/api/v1/strategy/generate/stream?session_id=${data.session_id}&strategy_id=${data.strategy_id}&token=${currentToken}&company_profile=${profileJson}&additional_context=${ctx}`;
      const eventSource = new EventSource(streamUrl);

      eventSource.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          setEvents((prev) => [...prev, parsed]);

          if (parsed.event === "done") {
            eventSource.close();
            setStreaming(false);
            setLoading(false);
            if (data.strategy_id) {
              setTimeout(() => router.push(`/strategy/${data.strategy_id}`), 1500);
            }
          }
          if (parsed.event === "error") {
            eventSource.close();
            setStreaming(false);
            setLoading(false);
          }
        } catch {}
      };

      eventSource.onerror = () => {
        eventSource.close();
        setStreaming(false);
        setLoading(false);
        setError("Connection lost. The agents might still be working — check the strategy page in a moment.");
      };
    } catch (err) {
      setLoading(false);
      setError(err instanceof Error ? err.message : "Failed to start strategy generation. Check that you're logged in.");
    }
  };

  return (
    <AuthLayout>
      <div className="max-w-4xl animate-fade-in">
        <h1 className="text-2xl font-bold mb-1">Generate GTM Strategy</h1>
        <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
          Tell us about your company and our AI agents will research, strategize, and create content.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Form */}
          <form onSubmit={handleSubmit} className="lg:col-span-2 space-y-5">
            <div className="card p-6 space-y-4">
              <div>
                <label className="label">Company Name *</label>
                <input
                  type="text"
                  required
                  className="input"
                  placeholder="e.g., ReachGTM"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Industry *</label>
                  <select
                    className="select"
                    value={form.industry}
                    onChange={(e) => setForm({ ...form, industry: e.target.value })}
                  >
                    {INDUSTRIES.map((ind) => (
                      <option key={ind} value={ind}>{ind}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="label">Stage *</label>
                  <select
                    className="select"
                    value={form.stage}
                    onChange={(e) => setForm({ ...form, stage: e.target.value })}
                  >
                    {STAGES.map((s) => (
                      <option key={s.value} value={s.value}>{s.label}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="label">Description *</label>
                <textarea
                  required
                  className="input"
                  rows={4}
                  placeholder="What does your company do? What problem do you solve?"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  style={{ resize: "vertical" }}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Website</label>
                  <input
                    type="url"
                    className="input"
                    placeholder="https://example.com"
                    value={form.website || ""}
                    onChange={(e) => setForm({ ...form, website: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label">Founded Year</label>
                  <input
                    type="number"
                    className="input"
                    placeholder="2024"
                    value={form.founded_year || ""}
                    onChange={(e) => setForm({ ...form, founded_year: parseInt(e.target.value) || null })}
                  />
                </div>
              </div>

              <div>
                <label className="label">Additional Context</label>
                <textarea
                  className="input"
                  rows={3}
                  placeholder="Target market, competitor concerns, specific goals..."
                  value={form.additional_context}
                  onChange={(e) => setForm({ ...form, additional_context: e.target.value })}
                  style={{ resize: "vertical" }}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !form.name || !form.description}
              className="btn-primary w-full py-3 text-base"
            >
              {loading ? (
                <>
                  <span className="spinner" />
                  Generating Strategy...
                </>
              ) : (
                <>
                  Generate GTM Strategy
                </>
              )}
            </button>
          </form>

          {/* Error banner */}
          {error && (
            <div className="lg:col-span-3">
              <div className="p-4 rounded-lg text-sm" style={{ background: "#fef2f2", border: "1px solid #fecaca", color: "#b91c1c" }}>
                {error}
              </div>
            </div>
          )}

          {/* Agent Progress */}
          <div className="space-y-4">
            <div className="card p-5">
              <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--text-secondary)" }}>
                AI Agent Pipeline
              </h3>
              <AgentProgress events={events} />
            </div>

            {streaming && (
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="spinner" />
                  <span className="text-sm font-medium">Agents working...</span>
                </div>
                <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                  This usually takes 30-60 seconds
                </p>
              </div>
            )}

            {strategyId && !streaming && (
              <div className="card p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-sm font-medium">Strategy Generated!</span>
                </div>
                <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                  Redirecting to results...
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </AuthLayout>
  );
}
