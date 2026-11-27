import {
  ResponsiveContainer, BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip,
} from "recharts";

const COLORS = ["#5E8B7E", "#C7A17A", "#9DBFB3", "#E3CBAE", "#3F6A5E", "#A9B8B3"];

const GRID = "#3F5A5A";
const TICK = "#A9B8B3";
const TOOLTIP = {
  contentStyle: { background: "#34464E", border: "1px solid #3F5A5A", borderRadius: 8 },
  labelStyle: { color: "#EFF3F1" },
  itemStyle: { color: "#EFF3F1" },
};

function toBarData(data) {
  return Object.entries(data).map(([name, value]) => ({ name, value }));
}

export default function ChartCard({ chart }) {
  const { type, title, data } = chart;

  return (
    <div className="bg-panel border border-line rounded-2xl p-4">
      <h4 className="text-sm font-medium text-cloud mb-3">{title}</h4>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          {type === "bar" && (
            <BarChart data={toBarData(data)}>
              <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fill: TICK, fontSize: 11 }} />
              <YAxis tick={{ fill: TICK, fontSize: 11 }} />
              <Tooltip {...TOOLTIP} />
              <Bar dataKey="value" fill="#5E8B7E" radius={[4, 4, 0, 0]} />
            </BarChart>
          )}

          {type === "histogram" && (
            <BarChart
              data={Array.isArray(data) ? data.map((v, i) => ({ name: i, value: v })) : []}
            >
              <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
              <XAxis dataKey="name" tick={{ fill: TICK, fontSize: 11 }} hide />
              <YAxis tick={{ fill: TICK, fontSize: 11 }} />
              <Tooltip {...TOOLTIP} />
              <Bar dataKey="value" fill="#C7A17A" radius={[4, 4, 0, 0]} />
            </BarChart>
          )}

          {type === "line" && (
            <LineChart
              data={(data.actual || []).map((v, i) => ({
                idx: i,
                actual: v,
                forecast: i >= (data.actual.length - (data.forecast?.length || 0)) ? undefined : undefined,
              })).concat(
                (data.forecast || []).map((v, i) => ({
                  idx: (data.actual?.length || 0) + i,
                  forecast: v,
                }))
              )}
            >
              <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
              <XAxis dataKey="idx" tick={{ fill: TICK, fontSize: 11 }} />
              <YAxis tick={{ fill: TICK, fontSize: 11 }} />
              <Tooltip {...TOOLTIP} />
              <Line type="monotone" dataKey="actual" stroke="#5E8B7E" dot={false} strokeWidth={2} />
              <Line type="monotone" dataKey="forecast" stroke="#C7A17A" strokeDasharray="4 3" dot={false} strokeWidth={2} />
            </LineChart>
          )}

          {type === "pie" && (
            <PieChart>
              <Pie
                data={toBarData(data)}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={70}
                label={({ name }) => name}
              >
                {toBarData(data).map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip {...TOOLTIP} />
            </PieChart>
          )}

          {type === "scatter" && (
            <ScatterChart>
              <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
              <XAxis dataKey={chart.x} tick={{ fill: TICK, fontSize: 11 }} />
              <YAxis dataKey={chart.y} tick={{ fill: TICK, fontSize: 11 }} />
              <Tooltip {...TOOLTIP} />
              <Scatter
                data={Array.isArray(data) ? data : []}
                fill="#5E8B7E"
              />
            </ScatterChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}
