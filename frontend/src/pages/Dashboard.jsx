import { useEffect, useState } from "react";
import Navbar from "../components/Navbar";
import FileUpload from "../components/FileUpload";
import DataPreview from "../components/DataPreview";
import QueryBox from "../components/QueryBox";
import ResultsPanel from "../components/ResultsPanel";
import HistorySidebar from "../components/HistorySidebar";
import { datasets as datasetsApi, query as queryApi, history as historyApi } from "../api";

export default function Dashboard() {
  const [dataset, setDataset] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [historyItems, setHistoryItems] = useState([]);
  const [activeHistoryId, setActiveHistoryId] = useState(null);

  const refreshHistory = () => {
    historyApi.list().then((res) => setHistoryItems(res.data)).catch(() => {});
  };

  useEffect(() => {
    refreshHistory();
  }, []);

  const handleUploaded = async (ds) => {
    setDataset(ds);
    setResult(null);
    const res = await datasetsApi.preview(ds.id);
    setPreview(res.data);
  };

  const handleQuery = async (text) => {
    if (!dataset) {
      setError("Upload a dataset first.");
      return;
    }
    setError("");
    setBusy(true);
    setResult(null);
    try {
      const res = await queryApi.submit(dataset.id, text);
      setResult(res.data);
      setActiveHistoryId(res.data.history_id);
      refreshHistory();
    } catch (err) {
      setError(err?.response?.data?.detail || "Query failed. Please try again.");
    } finally {
      setBusy(false);
    }
  };

  const handleSelectHistory = async (id) => {
    setActiveHistoryId(id);
    setBusy(true);
    try {
      const res = await historyApi.get(id);
      setResult({
        history_id: res.data.id,
        agents_used: res.data.agents_used,
        insights: res.data.result.insights || [],
        charts: res.data.result.charts || [],
        recommendations: res.data.result.recommendations || [],
        risk_alerts: res.data.result.risk_alerts || [],
      });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen bg-ink overflow-x-clip">
      <Navbar />
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_260px] gap-6">
          <div className="space-y-6 min-w-0">
            {!dataset && (
              <div>
                <h1 className="font-display text-2xl font-semibold mb-1">Upload a dataset</h1>
                <p className="text-mist text-sm mb-5">
                  Any shipment, supplier, or inventory file — we'll detect the relevant columns automatically.
                </p>
                <FileUpload onUploaded={handleUploaded} />
              </div>
            )}

            {dataset && (
              <>
                <DataPreview dataset={dataset} preview={preview} />
                <button
                  onClick={() => {
                    setDataset(null);
                    setPreview(null);
                    setResult(null);
                  }}
                  className="text-xs text-mist hover:text-sand transition"
                >
                  Upload a different file
                </button>
                <QueryBox onSubmit={handleQuery} busy={busy} activeAgents={result?.agents_used} />

                {error && (
                  <div className="text-clay text-sm bg-clay/10 border border-clay/30 rounded-lg px-3 py-2">
                    {error}
                  </div>
                )}

                {busy && !result && (
                  <div className="text-center text-mist text-sm py-10">Running the agent pipeline…</div>
                )}

                <ResultsPanel result={result} />
              </>
            )}
          </div>

          <HistorySidebar items={historyItems} onSelect={handleSelectHistory} activeId={activeHistoryId} />
        </div>
      </div>
    </div>
  );
}
