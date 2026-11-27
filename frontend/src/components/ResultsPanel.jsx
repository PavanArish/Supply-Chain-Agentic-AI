import { Lightbulb, CheckCircle2, AlertTriangle, Download } from "lucide-react";
import ChartCard from "./ChartCard";
import { reports } from "../api";

const AGENT_LABELS = {
  disruption: "Disruption",
  root_cause: "Root Cause",
  forecast: "Forecast",
  inventory: "Inventory",
  risk: "Risk",
  recommendation: "Recommendation",
};

export default function ResultsPanel({ result }) {
  if (!result) return null;

  const download = (fmt) => reports.download(result.history_id, fmt);

  return (
    <div className="space-y-5 min-w-0">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex flex-wrap gap-2">
          {result.agents_used.map((a) => (
            <span
              key={a}
              className="text-xs px-2.5 py-1 rounded-full bg-sage/20 text-cloud border border-sage/40"
            >
              {AGENT_LABELS[a] || a}
            </span>
          ))}
        </div>
        <div className="flex gap-2">
          {["csv", "xlsx", "pdf"].map((fmt) => (
            <button
              key={fmt}
              onClick={() => download(fmt)}
              className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-lg border border-line text-mist hover:border-sage hover:text-sand transition"
            >
              <Download className="w-3.5 h-3.5" />
              {fmt.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {result.risk_alerts?.length > 0 && (
        <div className="bg-clay/10 border border-clay/30 rounded-2xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-clay" />
            <h4 className="font-medium text-clay text-sm">Risk Alerts</h4>
          </div>
          <ul className="space-y-1.5">
            {result.risk_alerts.map((r, i) => (
              <li key={i} className="text-sm text-cloud/90">{r}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="bg-panel border border-line rounded-2xl p-5">
        <div className="flex items-center gap-2 mb-3">
          <Lightbulb className="w-4 h-4 text-sand" />
          <h4 className="font-medium text-cloud text-sm">Insights</h4>
        </div>
        <ul className="space-y-2">
          {result.insights.map((i, idx) => (
            <li key={idx} className="text-sm text-cloud/90 flex gap-2">
              <span className="text-sand mt-1">•</span>
              <span>{i}</span>
            </li>
          ))}
        </ul>
      </div>

      {result.charts?.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-[repeat(2,minmax(0,1fr))] gap-4">
          {result.charts.map((chart, idx) => (
            <ChartCard key={idx} chart={chart} />
          ))}
        </div>
      )}

      <div className="bg-panel border border-line rounded-2xl p-5">
        <div className="flex items-center gap-2 mb-3">
          <CheckCircle2 className="w-4 h-4 text-sage" />
          <h4 className="font-medium text-cloud text-sm">Recommendations</h4>
        </div>
        <ul className="space-y-2">
          {result.recommendations.map((r, idx) => (
            <li key={idx} className="text-sm text-cloud/90 flex gap-2">
              <span className="text-sage mt-1">•</span>
              <span>{r}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
