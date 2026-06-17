"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AuthLayout from "@/components/layout/AuthLayout";

interface DashStats {
  strategies: number;
  content: number;
  knowledge: number;
}

export default function DashboardPage() {
  const [tokenCheck, setTokenCheck] = useState(0);
  const [stats, setStats] = useState<DashStats>({ strategies: 0, content: 0, knowledge: 0 });
  const [strategies, setStrategies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashData = async () => {
      const token = localStorage.getItem("access_token");
      const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
      const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

      try {
        const [stratRes, contentRes, knowledgeRes] = await Promise.allSettled([
          fetch(`${base}/api/v1/strategy/`, { headers }),
          fetch(`${base}/api/v1/content/`, { headers }),
          fetch(`${base}/api/v1/knowledge/`, { headers }),
        ]);

        const stratData = stratRes.status === "fulfilled" ? await stratRes.value.json() : { strategies: [], total: 0 };
        const contentData = contentRes.status === "fulfilled" ? await contentRes.value.json() : { total: 0 };
        const knowledgeData = knowledgeRes.status === "fulfilled" ? await knowledgeRes.value.json() : { total: 0 };

        setStats({
          strategies: stratData.total || 0,
          content: contentData.total || 0,
          knowledge: knowledgeData.total || 0,
        });
        setStrategies(stratData.strategies || []);
      } catch {
        // Dashboard will show zeros on error
      }
      setLoading(false);
    };
    fetchDashData();
    
    // Watch for token changes (user switched accounts)
    let lastToken = localStorage.getItem("access_token");
    const interval = setInterval(() => {
      const t = localStorage.getItem("access_token");
      if (t !== lastToken) {
        lastToken = t;
        fetchDashData();
      }
    }, 500);
    return () => clearInterval(interval);
  }, []);

  const statCards = [
    {
      label: "Strategies",
      value: stats.strategies,
    },
    {
      label: "Content Assets",
      value: stats.content,
    },
    {
      label: "Knowledge Docs",
      value: stats.knowledge,
    },
  ];

  return (
    <AuthLayout>
      <div className="max-w-6xl animate-fade-in">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-1">Welcome back</h1>
          <p style={{ color: "var(--text-secondary)" }}>
            Your GTM command center. Generate strategies, create content, and grow faster.
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {statCards.map((card, i) => (
            <div
              key={card.label}
              className={`card p-5 animate-slide-up stagger-${i + 1}`}
              style={{ animationFillMode: "both" }}
            >
              <div className="flex items-center justify-between mb-3">
                <span
                  className="text-3xl font-bold"
                  style={{ color: "var(--text-primary)" }}
                >
                  {loading ? "-" : card.value}
                </span>
              </div>
              <p className="text-sm font-medium" style={{ color: "var(--text-secondary)" }}>
                {card.label}
              </p>
            </div>
          ))}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
          <Link href="/strategy/new" className="card p-5 flex items-center gap-4 group">
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center transition-all group-hover:scale-110"
              style={{ background: "var(--bg-tertiary)" }}
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold">New Strategy</h3>
              <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                Generate a complete GTM strategy with AI
              </p>
            </div>
          </Link>

          <Link href="/knowledge" className="card p-5 flex items-center gap-4 group">
            <div
              className="w-12 h-12 rounded-xl flex items-center justify-center transition-all group-hover:scale-110"
              style={{ background: "var(--bg-tertiary)" }}
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            </div>
            <div>
              <h3 className="font-semibold">Upload Knowledge</h3>
              <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                Add brand guides and docs for better alignment
              </p>
            </div>
          </Link>
        </div>

        {/* Recent Strategies */}
        <div className="card p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Recent Strategies</h2>
            <Link href="/strategy/new" className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
              View all →
            </Link>
          </div>

          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="shimmer h-14 rounded-lg" style={{ background: "var(--bg-tertiary)" }} />
              ))}
            </div>
          ) : strategies.length === 0 ? (
            <div className="text-center py-10">
              <p className="font-medium mb-1">No strategies yet</p>
              <p className="text-sm mb-4" style={{ color: "var(--text-muted)" }}>
                Create your first GTM strategy to get started
              </p>
              <Link href="/strategy/new" className="btn-primary">
                Generate Strategy
              </Link>
            </div>
          ) : (
            <div className="space-y-2">
              {strategies.slice(0, 5).map((s: any) => (
                <Link
                  key={s.id}
                  href={`/strategy/${s.id}`}
                  className="flex items-center justify-between p-3 rounded-lg transition-all hover:bg-[var(--bg-hover)]"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "var(--bg-tertiary)" }}>
                    </div>
                    <div>
                      <p className="text-sm font-medium">
                        {s.payload?.positioning_statement?.slice(0, 60) || `Strategy ${s.id.slice(0, 8)}`}
                      </p>
                      <p className="text-xs" style={{ color: "var(--text-muted)" }}>
                        {new Date(s.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <span className={`badge badge-${s.status}`}>{s.status}</span>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </AuthLayout>
  );
}
