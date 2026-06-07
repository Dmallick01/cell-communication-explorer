"use client";

import { useEffect, useState } from "react";
import { resolveArtifactUrl, type JobResultsResponse } from "@/lib/api";

export default function ReportPanel({ results }: { results: JobResultsResponse }) {
  const exports = results.exports ?? {};
  const [methods, setMethods] = useState<string>("");
  const [provenance, setProvenance] = useState<string>("");

  useEffect(() => {
    const methodsUrl = resolveArtifactUrl(exports.methods);
    const provUrl = resolveArtifactUrl(exports.provenance);
    if (methodsUrl) {
      fetch(methodsUrl).then((r) => r.text()).then(setMethods).catch(() => {});
    }
    if (provUrl) {
      fetch(provUrl).then((r) => r.text()).then(setProvenance).catch(() => {});
    }
  }, [exports.methods, exports.provenance]);

  return (
    <div>
      <div className="group-header">
        <span>Report & provenance</span>
        <span className="group-count">publication-ready</span>
      </div>

      <div className="export-actions">
        {exports.report_html && (
          <a className="btn" href={resolveArtifactUrl(exports.report_html)} target="_blank" rel="noreferrer">
            HTML report
          </a>
        )}
        {exports.report_pdf && (
          <a className="btn" href={resolveArtifactUrl(exports.report_pdf)} target="_blank" rel="noreferrer">
            PDF report
          </a>
        )}
        {exports.communication_edges && (
          <a className="btn" href={resolveArtifactUrl(exports.communication_edges)} target="_blank" rel="noreferrer">
            Interactions CSV
          </a>
        )}
        {exports.cell_types && (
          <a className="btn" href={resolveArtifactUrl(exports.cell_types)} target="_blank" rel="noreferrer">
            Cell types CSV
          </a>
        )}
        {exports.de_genes && (
          <a className="btn" href={resolveArtifactUrl(exports.de_genes)} target="_blank" rel="noreferrer">
            DE genes CSV
          </a>
        )}
        {exports.methods && (
          <a className="btn" href={resolveArtifactUrl(exports.methods)} target="_blank" rel="noreferrer">
            methods.txt
          </a>
        )}
        {exports.provenance && (
          <a className="btn" href={resolveArtifactUrl(exports.provenance)} target="_blank" rel="noreferrer">
            provenance.json
          </a>
        )}
      </div>

      <div className="panel panel-accent">
        <h3>Methods paragraph</h3>
        <div className="report-preview">{methods || "Methods not generated yet."}</div>
      </div>

      <div className="panel" style={{ marginTop: 16 }}>
        <h3>Provenance JSON</h3>
        <pre className="code-block">{provenance || "{}"}</pre>
      </div>
    </div>
  );
}
