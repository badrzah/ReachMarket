"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import AuthLayout from "@/components/layout/AuthLayout";
import ContentCard from "@/components/content/ContentCard";
import type { ContentAssetRecord } from "@/types";

export default function ContentPage() {
  const [assets, setAssets] = useState<ContentAssetRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");

  useEffect(() => {
    const fetchContent = async () => {
      const token = localStorage.getItem("access_token");
      const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
      try {
        const url = filter
          ? `${base}/api/v1/content/?content_type=${filter}`
          : `${base}/api/v1/content/`;
        const res = await fetch(url, {
          headers: { Authorization: `Bearer ${token}` },
        });
        const data = await res.json();
        setAssets(data.assets || []);
      } catch {
        setAssets([]);
      }
      setLoading(false);
    };
    fetchContent();
    
    // Re-fetch when token changes (different account login)
    let lastToken = localStorage.getItem("access_token");
    const interval = setInterval(() => {
      const currentToken = localStorage.getItem("access_token");
      if (currentToken !== lastToken) {
        lastToken = currentToken;
        fetchContent();
      }
    }, 500);
    return () => clearInterval(interval);
  }, [filter]);

  return (
    <AuthLayout>
      <div className="max-w-6xl animate-fade-in">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold">Content Library</h1>
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              All your generated content assets in one place
            </p>
          </div>
          <Link href="/content/create" className="btn-primary">
            + Generate Content
          </Link>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-6">
          {["", "cold_email", "linkedin_post", "blog_outline", "ad_copy"].map((type) => (
            <button
              key={type}
              onClick={() => setFilter(type)}
              className="px-3 py-1.5 rounded-lg text-sm transition-all"
              style={{
                background: filter === type ? "var(--accent-purple)" : "var(--bg-tertiary)",
                color: filter === type ? "white" : "var(--text-secondary)",
                border: `1px solid ${filter === type ? "var(--accent-purple)" : "var(--border-light)"}`,
              }}
            >
              {type ? type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()) : "All"}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <div key={i} className="shimmer h-48 rounded-xl" style={{ background: "var(--bg-card)" }} />
            ))}
          </div>
        ) : assets.length === 0 ? (
          <div className="glass-card p-16 text-center">
            <p className="text-4xl mb-3">📝</p>
            <p className="font-medium mb-1">No content assets yet</p>
            <p className="text-sm mb-4" style={{ color: "var(--text-muted)" }}>
              Generate your first content from a strategy
            </p>
            <Link href="/content/create" className="btn-primary">
              Generate Content
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {assets.map((asset) => (
              <ContentCard key={asset.id} asset={asset} />
            ))}
          </div>
        )}
      </div>
    </AuthLayout>
  );
}
