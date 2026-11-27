import { History, Clock } from "lucide-react";

export default function HistorySidebar({ items, onSelect, activeId }) {
  return (
    <div className="bg-panel border border-line rounded-2xl p-4 h-fit sticky top-6">
      <div className="flex items-center gap-2 mb-3">
        <History className="w-4 h-4 text-mist" />
        <h4 className="font-medium text-cloud text-sm">History</h4>
      </div>
      {items.length === 0 ? (
        <p className="text-xs text-mist">No queries yet — ask something to get started.</p>
      ) : (
        <ul className="space-y-1 max-h-[420px] overflow-y-auto">
          {items.map((h) => (
            <li key={h.id}>
              <button
                onClick={() => onSelect(h.id)}
                className={`w-full text-left px-3 py-2 rounded-lg text-xs transition ${
                  activeId === h.id ? "bg-sage/20 text-cloud border border-sage/40" : "text-mist hover:bg-panel2"
                }`}
              >
                <div className="flex items-center gap-1.5 mb-1 opacity-70">
                  <Clock className="w-3 h-3" />
                  {new Date(h.created_at).toLocaleString()}
                </div>
                <div className="line-clamp-2 text-cloud/90">{h.query_text}</div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
