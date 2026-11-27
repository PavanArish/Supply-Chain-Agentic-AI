import { useCallback, useRef, useState } from "react";
import { UploadCloud, FileSpreadsheet } from "lucide-react";
import { datasets } from "../api";

export default function FileUpload({ onUploaded }) {
  const [dragging, setDragging] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef(null);

  const handleFile = useCallback(
    async (file) => {
      if (!file) return;
      setError("");
      setBusy(true);
      try {
        const res = await datasets.upload(file);
        onUploaded(res.data);
      } catch (err) {
        setError(err?.response?.data?.detail || "Upload failed. Please try a .csv or .xlsx file.");
      } finally {
        setBusy(false);
      }
    },
    [onUploaded]
  );

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          handleFile(e.dataTransfer.files?.[0]);
        }}
        onClick={() => inputRef.current?.click()}
        className={`cursor-pointer rounded-2xl border-2 border-dashed p-10 text-center transition ${
          dragging ? "border-sage bg-sage/5" : "border-line hover:border-mist"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0])}
        />
        <div className="flex flex-col items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-panel2 flex items-center justify-center">
            {busy ? (
              <FileSpreadsheet className="w-6 h-6 text-sage animate-pulse" />
            ) : (
              <UploadCloud className="w-6 h-6 text-sage" />
            )}
          </div>
          <p className="font-medium text-cloud">
            {busy ? "Processing your file…" : "Drop a shipment/supplier file here, or click to browse"}
          </p>
          <p className="text-sm text-mist">.csv, .xlsx or .xls — any column names, we'll detect them</p>
        </div>
      </div>
      {error && (
        <div className="mt-3 text-clay text-sm bg-clay/10 border border-clay/30 rounded-lg px-3 py-2">
          {error}
        </div>
      )}
    </div>
  );
}
