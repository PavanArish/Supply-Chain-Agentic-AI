import { useState } from "react";
import { Send } from "lucide-react";

const SUGGESTIONS = [
  "Find delayed shipments and identify the top suppliers causing delays",
  "Forecast delivery delays for the next week",
  "Which products are at risk of running out of stock?",
  "What's our overall supply chain risk right now?",
];

const AGENT_STAGES = [
  "disruption", "root_cause", "forecast", "inventory", "risk", "recommendation",
];

const AGENT_LABELS = {
  disruption: "Disruption",
  root_cause: "Root Cause",
  forecast: "Forecast",
  inventory: "Inventory",
  risk: "Risk",
  recommendation: "Recommendation",
};

export default function QueryBox({ onSubmit, busy, activeAgents }) {
  const [text, setText] = useState("");

  const submit = (q) => {
    const value = (q ?? text).trim();
    if (!value) return;
    onSubmit(value);
  };

  return (
    <div className="bg-panel border border-line rounded-2xl p-5">
      <h3 className="font-display font-semibold text-cloud mb-1">Ask the agent</h3>
      <p className="text-sm text-mist mb-4">
        Ask in plain language — the orchestrator picks which specialized agents to run.
      </p>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
        className="flex gap-2"
      >
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="e.g. Find delayed shipments and identify the top suppliers causing delays"
          className="flex-1 bg-panel2 border border-line rounded-lg px-3 py-2.5 text-cloud focus:border-sage outline-none"
        />
        <button
          type="submit"
          disabled={busy}
          className="flex items-center gap-2 bg-sand text-ink font-semibold rounded-lg px-4 py-2.5 hover:brightness-110 transition disabled:opacity-50"
        >
          {busy ? "Working…" : "Ask"}
          {!busy && <Send className="w-4 h-4" />}
        </button>
      </form>

      <div className="flex flex-wrap gap-2 mt-3">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            onClick={() => submit(s)}
            disabled={busy}
            className="text-xs px-3 py-1.5 rounded-full border border-line text-mist hover:border-sage hover:text-sand transition disabled:opacity-50"
          >
            {s}
          </button>
        ))}
      </div>

      {/* Agent pipeline — signature element */}
      <div className="mt-6 pt-5 border-t border-line">
        <div className="relative flex items-center justify-between">
          <div className="route-dash absolute left-4 right-4 top-1/2 -translate-y-1/2 z-0" />
          {AGENT_STAGES.map((stage) => {
            const isActive = activeAgents?.includes(stage);
            return (
              <div key={stage} className="relative z-10 flex flex-col items-center gap-1.5">
                <div
                  className={`w-3 h-3 rounded-full border-2 ${
                    isActive ? "bg-sage border-sage node-active" : "bg-panel border-line"
                  }`}
                />
                <span className={`text-[10px] uppercase tracking-wide ${isActive ? "text-sand" : "text-mist"}`}>
                  {AGENT_LABELS[stage]}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
