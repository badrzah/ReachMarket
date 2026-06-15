"use client";

import { useEffect, useState } from "react";
import AuthLayout from "@/components/layout/AuthLayout";
import type { ResearchReport, StrategyRecord } from "@/types";

export default function ResearchPage() {
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchResearch = async () => {
      const token = localStorage.getItem("access_token");
      const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      try {
        const res = await fetch(`${base}/api/v1/strategy/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        // Get the latest completed strategy's research data
        const strategies = data.strategies || [];
        const latest = strategies.find((s: any) => s.status === "complete" && s.payload);
        if (latest?.payload) {
          // Research report may be embedded in strategy or available separately
          setReport(latest.payload.research_report || null);
        }
      } catch {}
      setLoading(false);
    };
    fetchResearch();
  }, []);

  if (loading) {
    return (
      <AuthLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="spinner" style={{ width: 32, height: 32 }} />
        </div>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout>
      <div className="max-w-6xl animate-fade-in">
        <h1 className="text-2xl font-bold mb-1">Market Research</h1>
        <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
          AI-generated market intelligence from your latest strategy run
        </p>

        {!report ? (
          <div className="glass-card p-16 text-center">
            <p className="text-4xl mb-3">🔬</p>
            <p className="font-medium mb-1">No research data yet</p>
            <p className="text-sm" style={{ color: "var(--text-muted)" }}>
              Generate a strategy to see market research here
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Market Size */}
            {report.market_size && (
              <div>
                <h2 className="text-lg font-semibold mb-3">Market Size</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { label: "TAM", value: report.market_size.tam, desc: "Total Addressable Market" },
                    { label: "SAM", value: report.market_size.sam, desc: "Serviceable Addressable Market" },
                    { label: "SOM", value: report.market_size.som, desc: "Serviceable Obtainable Market" },
                  ].map((item) => (
                    <div key={item.label} className="glass-card p-5 text-center">
                      <p className="text-xs font-medium mb-1" style={{ color: "var(--text-muted)" }}>
                        {item.desc}
                      </p>
                      <p className="text-2xl font-bold gradient-text">{item.value}</p>
                      <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                        {report.market_size.source} ({report.market_size.year})
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Competitors */}
            {report.competitors && report.competitors.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold mb-3">Competitors</h2>
                <div className="space-y-3">
                  {report.competitors.map((comp, i) => (
                    <div key={i} className="glass-card p-5">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold">{comp.name}</h3>
                        {comp.pricing_model && (
                          <span className="text-xs px-2 py-1 rounded" style={{ background: "var(--bg-tertiary)", color: "var(--text-secondary)" }}>
                            {comp.pricing_model}
                          </span>
                        )}
                      </div>
                      <p className="text-sm mb-3" style={{ color: "var(--text-secondary)" }}>{comp.positioning}</p>
                      <div className="grid grid-cols-2 gap-3">
                        <div>
                          <p className="text-xs font-medium mb-1" style={{ color: "var(--accent-green)" }}>Strengths</p>
                          {comp.strengths.map((s, j) => <p key={j} className="text-xs mb-0.5">• {s}</p>)}
                        </div>
                        <div>
                          <p className="text-xs font-medium mb-1" style={{ color: "var(--accent-red)" }}>Weaknesses</p>
                          {comp.weaknesses.map((w, j) => <p key={j} className="text-xs mb-0.5">• {w}</p>)}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Segments */}
            {report.segments && report.segments.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold mb-3">Target Segments</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {report.segments.map((seg, i) => (
                    <div key={i} className="glass-card p-5">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold">{seg.name}</h3>
                        <span className="text-xs" style={{ color: "var(--accent-teal)" }}>{seg.size_estimate}</span>
                      </div>
                      <p className="text-sm mb-3" style={{ color: "var(--text-secondary)" }}>{seg.description}</p>
                      <div className="flex flex-wrap gap-1">
                        {seg.pain_points.map((pp, j) => (
                          <span key={j} className="text-xs px-2 py-0.5 rounded" style={{ background: "rgba(239,68,68,0.1)", color: "var(--accent-red)" }}>
                            {pp}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Signals */}
            {report.signals && report.signals.length > 0 && (
              <div>
                <h2 className="text-lg font-semibold mb-3">Market Signals</h2>
                <div className="space-y-2">
                  {report.signals.map((sig, i) => (
                    <div key={i} className="glass-card p-4 flex items-start gap-3">
                      <span className="badge badge-pending">{sig.type}</span>
                      <div className="flex-1">
                        <p className="text-sm">{sig.description}</p>
                        <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>Relevance: {sig.relevance}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Sources */}
            {report.sources && report.sources.length > 0 && (
              <div className="glass-card p-5">
                <h2 className="text-sm font-semibold mb-2" style={{ color: "var(--text-secondary)" }}>Sources</h2>
                <ul className="space-y-1">
                  {report.sources.map((src, i) => (
                    <li key={i} className="text-xs" style={{ color: "var(--text-muted)" }}>• {src}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </div>
    </AuthLayout>
  );
}
