"use client";

import React from "react";
import Link from "next/link";
import type { StrategyRecord } from "@/types";

interface StrategyCardProps {
  strategy: StrategyRecord;
}

const StrategyCard = React.memo(function StrategyCard({ strategy }: StrategyCardProps) {
  const payload = strategy.payload;

  return (
    <Link href={`/strategy/${strategy.id}`}>
      <div className="card p-5 group">
        <div className="flex items-center justify-between mb-3">
          <span className={`badge badge-${strategy.status}`}>{strategy.status}</span>
          <span className="text-xs" style={{ color: "var(--text-muted)" }}>
            {new Date(strategy.created_at).toLocaleDateString()}
          </span>
        </div>

        <h3 className="font-semibold text-sm mb-2 line-clamp-2">
          {payload?.positioning_statement?.slice(0, 100) || `Strategy ${strategy.id.slice(0, 8)}`}
        </h3>

        {payload && (
          <div className="flex items-center gap-3 text-xs" style={{ color: "var(--text-secondary)" }}>
            {payload.icp && (
              <span className="flex items-center gap-1">
                {payload.icp.title}
              </span>
            )}
            {payload.channels && (
              <span className="flex items-center gap-1">
                {payload.channels.length} channels
              </span>
            )}
          </div>
        )}

        {payload?.motion && (
          <div className="mt-3">
            <span
              className="text-xs px-2 py-0.5 rounded border"
              style={{ borderColor: "var(--border-color)", color: "var(--text-primary)" }}
            >
              {payload.motion.replace(/_/g, " ")}
            </span>
          </div>
        )}

        {/* Hover indicator */}
        <div
          className="mt-3 text-xs font-medium opacity-0 group-hover:opacity-100 transition-opacity"
          style={{ color: "var(--text-primary)" }}
        >
          View details →
        </div>
      </div>
    </Link>
  );
});

StrategyCard.displayName = "StrategyCard";
export default StrategyCard;
