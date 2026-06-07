"use client";

import { useState } from "react";
import { createJob } from "@/lib/api";

interface UploadFormProps {
  onJobCreated: (jobId: string) => void;
}

export default function UploadForm({ onJobCreated }: UploadFormProps) {
  const [dataFile, setDataFile] = useState<File | null>(null);
  const [metaFile, setMetaFile] = useState<File | null>(null);
  const [projectName, setProjectName] = useState("");
  const [tissue, setTissue] = useState("");
  const [disease, setDisease] = useState("");
  const [drag, setDrag] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(demo = false) {
    if (!demo && !dataFile) {
      setError("Select a data file (.h5ad, 10x .zip, or expression matrix)");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const file =
        demo
          ? new File([new Blob(["demo"])], "demo.h5ad", { type: "application/octet-stream" })
          : dataFile!;
      const { job_id } = await createJob(file, metaFile, demo, {
        projectName: projectName || undefined,
        tissue: tissue || undefined,
        disease: disease || undefined,
      });
      onJobCreated(job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <div
        className={`dropzone ${drag ? "active" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDrag(true);
        }}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          const f = e.dataTransfer.files[0];
          if (f) setDataFile(f);
        }}
        onClick={() => document.getElementById("data-file")?.click()}
      >
        <h2>{dataFile ? dataFile.name : "Drop scRNA-seq data here"}</h2>
        <p>.h5ad · 10x Genomics (.zip) · CSV/TSV expression matrix</p>
        <input
          id="data-file"
          type="file"
          hidden
          accept=".h5ad,.mtx,.csv,.tsv,.txt,.gz,.zip"
          onChange={(e) => setDataFile(e.target.files?.[0] ?? null)}
        />
      </div>

      <div className="panel" style={{ marginTop: 16 }}>
        <div className="control-group">
          <label>Project name</label>
          <input
            className="control-input"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            placeholder="e.g. PBMC IFN response"
          />
        </div>
        <div className="grid-2">
          <div className="control-group">
            <label>Tissue</label>
            <input
              className="control-input"
              value={tissue}
              onChange={(e) => setTissue(e.target.value)}
              placeholder="e.g. adipose"
            />
          </div>
          <div className="control-group">
            <label>Disease / condition</label>
            <input
              className="control-input"
              value={disease}
              onChange={(e) => setDisease(e.target.value)}
              placeholder="e.g. T2D vs control"
            />
          </div>
        </div>
        <div className="control-group">
          <label>Metadata CSV (optional)</label>
          <input
            className="control-input"
            type="file"
            accept=".csv,.tsv,.txt"
            onChange={(e) => setMetaFile(e.target.files?.[0] ?? null)}
          />
          {metaFile && (
            <p style={{ fontSize: 11, color: "var(--cdisabled)", marginTop: 4 }}>{metaFile.name}</p>
          )}
        </div>
      </div>

      {error && <div className="alert alert-error" style={{ marginTop: 16 }}>{error}</div>}

      {loading && (
        <div className="progress-panel" style={{ marginTop: 16 }}>
          <p>Uploading and starting pipeline…</p>
          <div className="progress-track">
            <div className="progress-fill" style={{ width: "60%" }} />
          </div>
        </div>
      )}

      <div style={{ marginTop: 16, display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button
          type="button"
          className="btn btn-primary"
          disabled={loading || !dataFile}
          onClick={() => submit(false)}
        >
          Run analysis pipeline
        </button>
        {process.env.NEXT_PUBLIC_DEVELOPMENT_ONLY === "true" && (
          <button type="button" className="btn" disabled={loading} onClick={() => submit(true)}>
            Dev-only synthetic run
          </button>
        )}
      </div>
    </div>
  );
}
