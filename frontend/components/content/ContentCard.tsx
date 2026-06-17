"use client";

import React, { useState } from "react";
import type { ContentAssetRecord } from "@/types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface ContentCardProps {
  asset: ContentAssetRecord;
  onDelete?: (id: string) => void;
}

function formatBody(body: string, contentType: string): string {
  // LinkedIn posts and ad copies often have non-markdown formats
  if (contentType === "ad_copy" && body.startsWith("ContentAsset")) {
    // Custom ad copy format - wrap in code block
    return "```\n" + body + "\n```";
  }
  if (contentType === "linkedin_post" && !body.startsWith("```")) {
    // JSON format without code fence - add one
    return "```json\n" + body + "\n```";
  }
  return body;
}

const TYPE_CONFIG: Record<string, { color: string }> = {
  cold_email: { color: "var(--text-primary)" },
  linkedin_post: { color: "var(--text-primary)" },
  blog_outline: { color: "var(--text-primary)" },
  ad_copy: { color: "var(--text-primary)" },
};

const ContentCard = React.memo(function ContentCard({ asset, onDelete }: ContentCardProps) {
  const [copied, setCopied] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const config = TYPE_CONFIG[asset.content_type] || { color: "var(--text-secondary)" };

  const handleCopy = async (e: React.MouseEvent) => {
    e.stopPropagation();
    await navigator.clipboard.writeText(asset.body);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    setDeleting(true);
    const token = localStorage.getItem("access_token");
    const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    try {
      const res = await fetch(`${base}/api/v1/content/${asset.id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (res.ok) {
        onDelete?.(asset.id);
      }
    } catch {}
    setDeleting(false);
  };

  return (
    <div
      className="card p-4 cursor-pointer"
      onClick={() => setExpanded(!expanded)}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span
            className="text-xs font-semibold px-2 py-0.5 rounded border"
            style={{ borderColor: "var(--border-color)", color: "var(--text-primary)" }}
          >
            {asset.content_type?.replace(/_/g, " ")}
          </span>
        </div>
        <span
          className={`badge badge-${asset.validation_status === "approved" ? "approved" : "pending"}`}
        >
          {asset.validation_status}
        </span>
      </div>

      {/* Title */}
      <h3 className="text-sm font-semibold mb-2 line-clamp-2">
        {asset.title}
      </h3>

      {/* Body preview */}
      <div
        className="text-xs leading-relaxed mb-3"
        style={{
          color: "var(--text-secondary)",
          ...(expanded ? {} : {
            display: "-webkit-box",
            WebkitLineClamp: 3,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
          }),
        }}
      >
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {asset.content_type === "ad_copy" && asset.body.startsWith("ContentAsset")
            ? "```\n" + asset.body + "\n```"
            : asset.content_type === "linkedin_post" && !asset.body.startsWith("```")
              ? "```json\n" + asset.body + "\n```"
              : asset.body}
        </ReactMarkdown>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          {asset.brand_alignment_score != null && (
            <div className="flex items-center gap-1.5">
              <div
                className="w-16 h-1.5 rounded-full"
                style={{ background: "var(--bg-tertiary)" }}
              >
                <div
                  className="h-full rounded-full transition-all"
                  style={{
                    width: `${(asset.brand_alignment_score * 100).toFixed(0)}%`,
                    background: "var(--text-primary)"
                  }}
                />
              </div>
              <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                {(asset.brand_alignment_score * 100).toFixed(0)}%
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleDelete}
            disabled={deleting}
            className="text-xs px-2 py-1 rounded transition-all hover:bg-red-500/10 border"
            style={{ color: "var(--text-muted)", borderColor: "var(--border-color)" }}
          >
            {deleting ? "..." : "Delete"}
          </button>
          <button
            onClick={handleCopy}
            className="text-xs px-2 py-1 rounded transition-all hover:bg-[var(--bg-hover)] border"
            style={{ color: copied ? "var(--text-primary)" : "var(--text-muted)", borderColor: "var(--border-color)" }}
          >
            {copied ? "Copied" : "Copy"}
          </button>
        </div>
      </div>
    </div>
  );
});

ContentCard.displayName = "ContentCard";
export default ContentCard;
