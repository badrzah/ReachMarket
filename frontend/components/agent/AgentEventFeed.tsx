"use client";

import type { AgentEvent } from "@/types";

interface AgentEventFeedProps {
  events: AgentEvent[];
}

const AGENT_COLORS: Record<string, string> = {
  orchestrator: "var(--accent-purple-light)",
  research: "var(--accent-teal)",
  strategy: "var(--accent-blue)",
  content: "var(--accent-amber)",
  brand_alignment: "var(--accent-green)",
};

const EVENT_ICONS: Record<string, string> = {
  agent_start: "▶",
  agent_progress: "⏳",
  agent_output: "📤",
  agent_complete: "✓",
  error: "✕",
  done: "🎉",
};

export default function AgentEventFeed({ events }: AgentEventFeedProps) {
  if (events.length === 0) {
    return (
      <div className="text-center py-6">
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          Events will appear here during generation
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-1.5 max-h-96 overflow-y-auto">
      {events.map((event, i) => {
        const color = event.agent ? AGENT_COLORS[event.agent] || "var(--text-secondary)" : "var(--text-secondary)";
        const icon = EVENT_ICONS[event.event] || "•";
        const time = new Date(event.timestamp).toLocaleTimeString();

        return (
          <div
            key={i}
            className="flex items-start gap-2 p-2 rounded-lg text-xs animate-slide-in-right"
            style={{ background: "var(--bg-tertiary)" }}
          >
            <span className="shrink-0 mt-0.5">{icon}</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                {event.agent && (
                  <span
                    className="font-semibold"
                    style={{ color }}
                  >
                    {event.agent}
                  </span>
                )}
                <span style={{ color: "var(--text-muted)" }}>{event.event.replace(/_/g, " ")}</span>
              </div>
              {event.message && (
                <p className="mt-0.5 truncate" style={{ color: "var(--text-secondary)" }}>
                  {event.message}
                </p>
              )}
            </div>
            <span className="shrink-0 text-[10px]" style={{ color: "var(--text-muted)" }}>{time}</span>
          </div>
        );
      })}
    </div>
  );
}
