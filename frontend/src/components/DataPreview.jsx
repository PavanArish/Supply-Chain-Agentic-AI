const ROLE_COLORS = {
  date: "bg-sage/25 text-cloud",
  supplier: "bg-sand/15 text-sand",
  product: "bg-clay/15 text-clay",
  quantity: "bg-sage/25 text-cloud",
  delay: "bg-clay/15 text-clay",
  status: "bg-sand/15 text-sand",
  location: "bg-sage/25 text-cloud",
  cost: "bg-sand/15 text-sand",
  inventory: "bg-sage/25 text-cloud",
  risk: "bg-clay/15 text-clay",
  id: "bg-mist/15 text-mist",
  numeric: "bg-mist/15 text-mist",
  categorical: "bg-mist/15 text-mist",
};

export default function DataPreview({ dataset, preview }) {
  if (!dataset || !preview) return null;

  return (
    <div className="bg-panel border border-line rounded-2xl p-5 min-w-0 max-w-full overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-display font-semibold text-cloud">{dataset.filename}</h3>
          <p className="text-xs text-mist mt-0.5">
            {preview.row_count} rows · {dataset.column_count} columns
          </p>
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {Object.entries(dataset.column_roles).map(([col, role]) => (
          <span
            key={col}
            className={`text-xs px-2 py-1 rounded-md font-mono max-w-full break-all ${ROLE_COLORS[role] || "bg-mist/15 text-mist"}`}
            title={`Detected role: ${role}`}
          >
            {col} <span className="opacity-60">· {role}</span>
          </span>
        ))}
      </div>

      <div className="overflow-x-auto max-w-full rounded-lg border border-line">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-panel2 text-mist text-xs uppercase tracking-wide">
              {preview.columns.map((c) => (
                <th key={c} className="px-3 py-2 text-left whitespace-nowrap">
                  {c}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {preview.sample_rows.slice(0, 8).map((row, i) => (
              <tr key={i} className="border-t border-line">
                {preview.columns.map((c) => (
                  <td key={c} className="px-3 py-2 whitespace-nowrap font-mono text-xs text-cloud/90">
                    {row[c]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
