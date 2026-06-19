"use client";

import { useState, useRef, useEffect } from "react";
import AuthLayout from "@/components/layout/AuthLayout";
import { authFetch } from "@/lib/auth-fetch";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface ChatMessage {
  role: "user" | "agent";
  content: string;
  agent?: string;
  timestamp: Date;
}

export default function AgentChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMessage: ChatMessage = {
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    const base = "https://reachgtm-chat-proxy.reminiscent-moonstone.workers.dev";

    // Decode JWT to get company_id and user_id
    const getJwtPayload = (): { company_id?: string; sub?: string } => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) return {};
        // base64url → base64 (fix -_ chars)
        const base64 = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
        const payload = JSON.parse(atob(base64));
        return { company_id: payload.company_id, sub: payload.sub };
      } catch {
        return {};
      }
    };

    try {
      const jwtPayload = getJwtPayload();
      const res = await authFetch(`${base}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: null,
          company_id: jwtPayload.company_id,
          user_id: jwtPayload.sub,
        }),
      });

      if (!res.ok) throw new Error(`Request failed (${res.status})`);

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      let agentResponse = "";
      let buffer = "";

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: !done });
          const lines = buffer.split("\n");
          // Keep the last (potentially incomplete) line in the buffer
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const parsed = JSON.parse(line.slice(6));
                if (parsed.event === "agent_output" && parsed.message) {
                  agentResponse = parsed.message;
                } else if (parsed.data?.response) {
                  agentResponse = parsed.data.response;
                }
              } catch {}
            }
          }
        }
        // Process any remaining data in buffer
        if (buffer.startsWith("data: ")) {
          try {
            const parsed = JSON.parse(buffer.slice(6));
            if (parsed.event === "agent_output" && parsed.message) {
              agentResponse = parsed.message;
            } else if (parsed.data?.response) {
              agentResponse = parsed.data.response;
            }
          } catch {}
        }
      }

      if (agentResponse) {
        setMessages((prev) => [
          ...prev,
          {
            role: "agent",
            content: agentResponse,
            agent: "orchestrator",
            timestamp: new Date(),
          },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          content: "Sorry, I couldn't process your request. Please try again.",
          agent: "system",
          timestamp: new Date(),
        },
      ]);
    }
    setLoading(false);
  };

  return (
    <AuthLayout>
      <div className="max-w-4xl h-[calc(100vh-8rem)] flex flex-col animate-fade-in">
        <div className="mb-4">
          <h1 className="text-2xl font-bold">AI Chat</h1>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            Ask questions about GTM strategy, get instant AI-powered insights
          </p>
        </div>

        {/* Messages */}
        <div
          className="flex-1 overflow-y-auto space-y-4 p-4 rounded-xl mb-4"
          style={{ background: "var(--bg-secondary)" }}
        >
          {messages.length === 0 && (
            <div className="text-center py-16">
              <p className="text-4xl mb-3">💬</p>
              <p className="font-medium mb-2">Start a conversation</p>
              <p className="text-sm" style={{ color: "var(--text-muted)" }}>
                Ask about GTM strategies, market research, content ideas...
              </p>
              <div className="grid grid-cols-2 gap-2 max-w-md mx-auto mt-6">
                {[
                  "What's the best GTM motion for a B2B SaaS startup?",
                  "How should I structure my cold email sequence?",
                  "What channels work best for Series A companies?",
                  "Help me define my ICP for a DevTools product",
                ].map((suggestion, i) => (
                  <button
                    key={i}
                    onClick={() => { setInput(suggestion); }}
                    className="text-left p-3 rounded-lg text-xs transition-all hover:bg-[var(--bg-hover)]"
                    style={{ background: "var(--bg-tertiary)", color: "var(--text-secondary)" }}
                  >
                    {suggestion}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-slide-up`}
            >
              <div
                className="max-w-[80%] p-4 rounded-2xl"
                style={{
                  background:
                    msg.role === "user"
                      ? "linear-gradient(135deg, var(--accent-purple), var(--accent-purple-dark))"
                      : "var(--bg-card)",
                  border: msg.role === "agent" ? "1px solid var(--border-subtle)" : "none",
                  borderBottomRightRadius: msg.role === "user" ? "4px" : undefined,
                  borderBottomLeftRadius: msg.role === "agent" ? "4px" : undefined,
                }}
              >
                {msg.role === "agent" && (
                  <div className="flex items-center gap-2 mb-2">
                    <div
                      className="w-5 h-5 rounded-full flex items-center justify-center text-[10px]"
                      style={{ background: "var(--accent-teal)", color: "white" }}
                    >
                      AI
                    </div>
                    <span className="text-xs font-medium" style={{ color: "var(--accent-teal)" }}>
                      ReachGTM Agent
                    </span>
                  </div>
                )}
                <div className="text-sm whitespace-pre-wrap leading-relaxed">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                </div>
                <p className="text-[10px] mt-2 opacity-50">
                  {msg.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="glass-card p-4 flex items-center gap-2">
                <div className="spinner" style={{ width: 16, height: 16 }} />
                <span className="text-sm" style={{ color: "var(--text-secondary)" }}>Thinking...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="flex gap-3">
          <input
            type="text"
            className="input flex-1"
            placeholder="Ask about GTM strategy, content, market research..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={loading}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="btn-primary px-6"
          >
            {loading ? <span className="spinner" style={{ width: 16, height: 16 }} /> : "Send"}
          </button>
        </div>
      </div>
    </AuthLayout>
  );
}
