"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import AuthLayout from "@/components/layout/AuthLayout";
import type { StrategyRecord, GTMStrategy } from "@/types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const TABS = ["Overview", "ICP", "Channels", "Battlecards", "Growth Loops", "90-Day Plan"];

export default function StrategyDetailPage() {
  const params = useParams();
  const [strategy, setStrategy] = useState<StrategyRecord | null>(null);
  const [activeTab, setActiveTab] = useState("Overview");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStrategy = async () => {
      const token = localStorage.getItem("access_token");
      const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      try {
        const res = await fetch(`${base}/api/v1/strategy/${params.id}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setStrategy(data);
      } catch {}
      setLoading(false);
    };
    if (params.id) fetchStrategy();
  }, [params.id]);

  // Auto-refresh when status is "generating"
  useEffect(() => {
    if (strategy?.status === "generating") {
      const interval = setInterval(async () => {
        const token = localStorage.getItem("access_token");
        const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
        try {
          const res = await fetch(`${base}/api/v1/strategy/${params.id}`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          const data = await res.json();
          setStrategy(data);
          if (data.status !== "generating") clearInterval(interval);
        } catch {}
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [strategy?.status, params.id]);

  if (loading) {
    return (
      <AuthLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="spinner" style={{ width: 32, height: 32 }} />
        </div>
      </AuthLayout>
    );
  }

  if (!strategy) {
    return (
      <AuthLayout>
        <div className="text-center py-20">
          <p className="font-medium">Strategy not found</p>
        </div>
      </AuthLayout>
    );
  }

  const payload: GTMStrategy | null = strategy.payload as GTMStrategy | null;

  return (
    <AuthLayout>
      <div className="max-w-6xl animate-fade-in">
        {/* Header */}
        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold">GTM Strategy</h1>
              <span className={`badge badge-${strategy.status}`}>{strategy.status}</span>
            </div>
            <p className="text-sm" style={{ color: "var(--text-muted)" }}>
              Created {new Date(strategy.created_at).toLocaleDateString()} · ID: {strategy.id.slice(0, 8)}
            </p>
          </div>
        </div>

        {strategy.status === "generating" ? (
          <div className="card p-10 text-center">
            <div className="spinner mx-auto mb-4" style={{ width: 32, height: 32 }} />
            <p className="font-medium">Strategy is being generated...</p>
            <p className="text-sm mt-1" style={{ color: "var(--text-muted)" }}>
              AI agents are working. Refresh in a moment.
            </p>
          </div>
        ) : !payload ? (
          <div className="card p-10 text-center">
            <p className="font-medium">Strategy data unavailable</p>
          </div>
        ) : (
          <>
            {/* Tabs */}
            <div className="flex gap-1 mb-6 p-1 rounded-xl" style={{ background: "var(--bg-secondary)" }}>
              {TABS.map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
                  style={{
                    background: activeTab === tab ? "var(--bg-card)" : "transparent",
                    color: activeTab === tab ? "var(--text-primary)" : "var(--text-muted)",
                    boxShadow: activeTab === tab ? "var(--shadow-sm)" : "none",
                  }}
                >
                  {tab}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="animate-fade-in">
              {activeTab === "Overview" && (
                <div className="space-y-4">
                  <div className="card p-6">
                    <h3 className="text-sm font-semibold mb-3" style={{ color: "var(--text-secondary)" }}>
                      Positioning Statement
                    </h3>
                    <p className="text-lg leading-relaxed">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {payload.positioning_statement}
                      </ReactMarkdown>
                    </p>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="card p-5">
                      <h3 className="text-sm font-semibold mb-2" style={{ color: "var(--text-secondary)" }}>
                        GTM Motion
                      </h3>
                      <span className="badge badge-complete text-sm">
                        {payload.motion?.replace(/_/g, " ").toUpperCase()}
                      </span>
                    </div>
                    <div className="card p-5">
                      <h3 className="text-sm font-semibold mb-2" style={{ color: "var(--text-secondary)" }}>
                        Value Proposition
                      </h3>
                      <p className="font-semibold mb-1">{payload.value_proposition?.headline}</p>
                      <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                        {payload.value_proposition?.subheadline}
                      </p>
                    </div>
                  </div>
                  {payload.value_proposition && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="card p-5">
                        <h4 className="text-sm font-semibold mb-3" style={{ color: "var(--text-secondary)" }}>
                          Proof Points
                        </h4>
                        <ul className="space-y-2">
                          {payload.value_proposition.proof_points?.map((p, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              {p}
                            </li>
                          ))}
                        </ul>
                      </div>
                      <div className="card p-5">
                        <h4 className="text-sm font-semibold mb-3" style={{ color: "var(--text-secondary)" }}>
                          Differentiators
                        </h4>
                        <ul className="space-y-2">
                          {payload.value_proposition.differentiators?.map((d, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm">
                              {d}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === "ICP" && payload.icp && (
                <div className="card p-6 space-y-4">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                      { label: "Title", value: payload.icp.title },
                      { label: "Industry", value: payload.icp.industry },
                      { label: "Company Size", value: payload.icp.company_size },
                      { label: "Budget Range", value: payload.icp.budget_range },
                    ].map((item) => (
                      <div key={item.label} className="p-3 rounded-lg" style={{ background: "var(--bg-tertiary)" }}>
                        <p className="text-xs mb-1" style={{ color: "var(--text-muted)" }}>{item.label}</p>
                        <p className="text-sm font-medium">{item.value}</p>
                      </div>
                    ))}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-semibold mb-2" style={{ color: "var(--text-secondary)" }}>Pain Points</h4>
                      {payload.icp.pain_points?.map((p, i) => (
                        <p key={i} className="text-sm mb-1">• {p}</p>
                      ))}
                    </div>
                    <div>
                      <h4 className="text-sm font-semibold mb-2" style={{ color: "var(--text-secondary)" }}>Goals</h4>
                      {payload.icp.goals?.map((g, i) => (
                        <p key={i} className="text-sm mb-1">• {g}</p>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold mb-2" style={{ color: "var(--text-secondary)" }}>Buying Committee</h4>
                    <div className="flex flex-wrap gap-2">
                      {payload.icp.buying_committee?.map((role, i) => (
                        <span key={i} className="badge badge-pending">{role}</span>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "Channels" && (
                <div className="space-y-3">
                  {payload.channels?.map((ch, i) => (
                    <div key={i} className="card p-5">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <span
                            className="w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold border"
                            style={{ borderColor: "var(--border-color)", color: "var(--text-primary)" }}
                          >
                            #{ch.priority}
                          </span>
                          <h3 className="font-semibold">{ch.name?.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}</h3>
                        </div>
                        {ch.estimated_cac && (
                          <span className="text-sm" style={{ color: "var(--accent-teal)" }}>CAC: {ch.estimated_cac}</span>
                        )}
                      </div>
                      <p className="text-sm mb-3" style={{ color: "var(--text-secondary)" }}>{ch.rationale}</p>
                      <div className="flex flex-wrap gap-2">
                        {ch.kpis?.map((kpi, j) => (
                          <span key={j} className="text-xs px-2 py-1 rounded" style={{ background: "var(--bg-tertiary)", color: "var(--text-secondary)" }}>
                            {kpi}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === "Battlecards" && (
                <div className="space-y-4">
                  {payload.battlecards?.map((bc, i) => (
                    <div key={i} className="card p-5">
                      <h3 className="font-semibold mb-4 text-lg">vs {bc.competitor}</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div className="p-3 rounded-lg border" style={{ borderColor: "var(--border-color)" }}>
                          <h4 className="text-xs font-semibold mb-2">Our Strengths</h4>
                          {bc.our_strengths_vs_them?.map((s, j) => <p key={j} className="text-sm mb-1">{s}</p>)}
                        </div>
                        <div className="p-3 rounded-lg border" style={{ borderColor: "var(--border-color)" }}>
                          <h4 className="text-xs font-semibold mb-2">Their Strengths</h4>
                          {bc.their_strengths_vs_us?.map((s, j) => <p key={j} className="text-sm mb-1">{s}</p>)}
                        </div>
                      </div>
                      <div className="p-3 rounded-lg" style={{ background: "var(--bg-tertiary)" }}>
                        <h4 className="text-xs font-semibold mb-2" style={{ color: "var(--text-primary)" }}>Talk Track</h4>
                        <p className="text-sm italic" style={{ color: "var(--text-secondary)" }}>&quot;{bc.talk_track}&quot;</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === "Growth Loops" && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {payload.growth_loops?.map((gl, i) => (
                    <div key={i} className="card p-5">
                      <div className="flex items-center gap-2 mb-3">
                        <span className="badge badge-pending">{gl.type}</span>
                        <h3 className="font-semibold">{gl.name}</h3>
                      </div>
                      <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>{gl.description}</p>
                      <div className="flex items-center gap-3">
                        <div className="flex-1 p-2 rounded text-center" style={{ background: "var(--bg-tertiary)" }}>
                          <p className="text-xs" style={{ color: "var(--text-muted)" }}>Input</p>
                          <p className="text-xs font-medium">{gl.input_metric}</p>
                        </div>
                        <span style={{ color: "var(--text-primary)" }}>→</span>
                        <div className="flex-1 p-2 rounded text-center" style={{ background: "var(--bg-tertiary)" }}>
                          <p className="text-xs" style={{ color: "var(--text-muted)" }}>Output</p>
                          <p className="text-xs font-medium">{gl.output_metric}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === "90-Day Plan" && (
                <div className="space-y-2">
                  {payload.ninety_day_plan?.map((ms, i) => (
                    <div key={i} className="card p-4 flex items-start gap-4">
                      <div
                        className="w-12 h-12 rounded-xl flex flex-col items-center justify-center shrink-0"
                        style={{ background: "var(--bg-tertiary)" }}
                      >
                        <span className="text-xs" style={{ color: "var(--text-muted)" }}>WK</span>
                        <span className="text-sm font-bold" style={{ color: "var(--text-primary)" }}>{ms.week}</span>
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{ms.goal}</p>
                        <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>Owner: {ms.owner}</p>
                        <div className="flex flex-wrap gap-1 mt-2">
                          {ms.kpis?.map((kpi, j) => (
                            <span key={j} className="text-xs px-2 py-0.5 rounded" style={{ background: "var(--bg-tertiary)", color: "var(--text-secondary)" }}>
                              {kpi}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </AuthLayout>
  );
}
