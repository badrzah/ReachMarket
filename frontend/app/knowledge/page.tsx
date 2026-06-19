"use client";

import { useEffect, useState, useCallback } from "react";
import AuthLayout from "@/components/layout/AuthLayout";
import type { KnowledgeDocument } from "@/types";

const DOC_TYPES = ["brand_guide", "pitch_deck", "case_study", "competitor_analysis", "other"];

export default function KnowledgePage() {
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [selectedType, setSelectedType] = useState("brand_guide");

  const fetchDocs = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    try {
      const res = await fetch(`${base}/api/v1/knowledge/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setDocuments(data.documents || []);
    } catch {}
    setLoading(false);
  }, []);

  useEffect(() => { fetchDocs(); }, [fetchDocs]);

  const handleUpload = async (file: File) => {
    setUploading(true);
    const token = localStorage.getItem("access_token");
    const base = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    const formData = new FormData();
    formData.append("file", file);
    formData.append("doc_type", selectedType);

    try {
      const res = await fetch(`${base}/api/v1/knowledge/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (res.ok) {
        await fetchDocs();
      } else {
        const err = await res.text().catch(() => "Upload failed");
        alert(`Upload error: ${err.slice(0, 200)}`);
      }
    } catch (e) {
      alert("Network error during upload");
    }
    setUploading(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  };

  return (
    <AuthLayout>
      <div className="max-w-5xl animate-fade-in">
        <h1 className="text-2xl font-bold mb-1">Knowledge Base</h1>
        <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
          Upload brand guides and documents for AI-powered brand alignment
        </p>

        {/* Upload Zone */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-8">
          <div className="lg:col-span-2">
            <div
              className="glass-card p-8 text-center transition-all cursor-pointer"
              style={{
                borderStyle: "dashed",
                borderWidth: "2px",
                borderColor: dragActive ? "var(--accent-purple)" : "var(--border-light)",
                background: dragActive ? "rgba(124,58,237,0.05)" : undefined,
              }}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
              onClick={() => {
                const input = document.createElement("input");
                input.type = "file";
                input.accept = ".pdf,.docx,.doc";
                input.onchange = (e) => {
                  const file = (e.target as HTMLInputElement).files?.[0];
                  if (file) handleUpload(file);
                };
                input.click();
              }}
            >
              {uploading ? (
                <div className="flex flex-col items-center gap-3">
                  <div className="spinner" style={{ width: 32, height: 32 }} />
                  <p className="font-medium">Processing document...</p>
                  <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                    Extracting text, chunking, and generating embeddings
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-3">
                  <div
                    className="w-16 h-16 rounded-2xl flex items-center justify-center"
                    style={{ background: "var(--bg-tertiary)" }}
                  >
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ color: "var(--accent-purple-light)" }}>
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                      <polyline points="17 8 12 3 7 8" />
                      <line x1="12" y1="3" x2="12" y2="15" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium">Drop files here or click to upload</p>
                    <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                      PDF or DOCX • Max 10MB
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="glass-card p-5">
            <label className="label">Document Type</label>
            <div className="space-y-2">
              {DOC_TYPES.map((type) => (
                <button
                  key={type}
                  onClick={() => setSelectedType(type)}
                  className="w-full text-left px-3 py-2 rounded-lg text-sm transition-all"
                  style={{
                    background: selectedType === type ? "rgba(124,58,237,0.15)" : "transparent",
                    color: selectedType === type ? "var(--text-primary)" : "var(--text-secondary)",
                    border: `1px solid ${selectedType === type ? "var(--accent-purple)" : "transparent"}`,
                  }}
                >
                  {type.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Document List */}
        <div className="glass-card overflow-hidden">
          <div className="p-4" style={{ borderBottom: "1px solid var(--border-subtle)" }}>
            <h2 className="font-semibold">Uploaded Documents</h2>
          </div>

          {loading ? (
            <div className="p-8 text-center"><div className="spinner mx-auto" /></div>
          ) : documents.length === 0 ? (
            <div className="p-12 text-center">
              <p className="text-3xl mb-2">📚</p>
              <p className="text-sm" style={{ color: "var(--text-muted)" }}>No documents uploaded yet</p>
            </div>
          ) : (
            <table className="w-full">
              <thead>
                <tr style={{ background: "var(--bg-tertiary)" }}>
                  <th className="text-left text-xs font-medium px-4 py-3" style={{ color: "var(--text-muted)" }}>Filename</th>
                  <th className="text-left text-xs font-medium px-4 py-3" style={{ color: "var(--text-muted)" }}>Type</th>
                  <th className="text-left text-xs font-medium px-4 py-3" style={{ color: "var(--text-muted)" }}>Status</th>
                  <th className="text-left text-xs font-medium px-4 py-3" style={{ color: "var(--text-muted)" }}>Chunks</th>
                  <th className="text-left text-xs font-medium px-4 py-3" style={{ color: "var(--text-muted)" }}>Date</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr key={doc.id} className="transition-all hover:bg-[var(--bg-hover)]" style={{ borderBottom: "1px solid var(--border-subtle)" }}>
                    <td className="px-4 py-3 text-sm font-medium">{doc.filename}</td>
                    <td className="px-4 py-3">
                      <span className="badge badge-pending">{doc.doc_type?.replace(/_/g, " ")}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`badge badge-${doc.status === "indexed" ? "complete" : "generating"}`}>
                        {doc.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: "var(--text-secondary)" }}>
                      {doc.chunk_count ?? "-"}
                    </td>
                    <td className="px-4 py-3 text-sm" style={{ color: "var(--text-muted)" }}>
                      {new Date(doc.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    </AuthLayout>
  );
}
