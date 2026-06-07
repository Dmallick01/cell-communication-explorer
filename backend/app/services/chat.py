"""Rule-based research assistant over job results (no external LLM)."""

from __future__ import annotations

from typing import Any


def answer_question(question: str, results: dict[str, Any]) -> str:
    q = question.lower().strip()
    edges = results.get("communication_edges") or []
    cell_types = results.get("cell_types") or []
    qc = results.get("qc_report") or {}
    cluster = results.get("cluster_summary") or {}

    if not q:
        return "Ask about cell types, ligand–receptor interactions, QC, or literature evidence."

    if any(w in q for w in ("hello", "hi", "help")):
        return (
            "I summarize your completed analysis. Try: "
            '"top interactions", "cell types", "qc summary", or "methods".'
        )

    if "cell type" in q or "annotation" in q:
        if not cell_types:
            return "Cell-type counts are not available yet."
        lines = [f"• {ct['cell_type']}: {ct['count']} cells ({ct['fraction']*100:.1f}%)" for ct in cell_types[:12]]
        return "Annotated cell types:\n" + "\n".join(lines)

    if any(w in q for w in ("interaction", "ligand", "receptor", "communication", "signaling", "nichenet")):
        if not edges:
            return "No NicheNet communication edges found. Ensure R + nichenetr priors are installed."
        lines = []
        for e in edges[:8]:
            lines.append(
                f"• {e['source_cell_type']} → {e['target_cell_type']}: "
                f"{e['ligand']} → {e['receptor']} (score {e['score']}, p={e['p_value']})"
            )
        return "Top ligand–receptor interactions (NicheNet):\n" + "\n".join(lines)

    if "qc" in q or "quality" in q:
        return (
            f"QC summary: {qc.get('cells_remaining', '—')} cells after filtering; "
            f"median mitochondrial % = {qc.get('pct_mito_median', '—')}; "
            f"clusters = {cluster.get('n_clusters', '—')} "
            f"(silhouette {cluster.get('silhouette_score', '—')})."
        )

    if "method" in q or "provenance" in q:
        return (
            "Methods: Scanpy QC → Harmony batch correction → Leiden clustering → "
            "CellTypist annotation → NicheNet ligand–receptor inference. "
            "Download methods.txt and provenance.json from the Report tab."
        )

    if "literature" in q or "paper" in q or "pubmed" in q:
        if not edges:
            return "Run communication analysis first, then check the Literature tab for PubMed links."
        top = edges[0]
        return (
            f"See Literature tab for PubMed hits on edges like "
            f"{top['ligand']}→{top['receptor']} ({top['source_cell_type']}→{top['target_cell_type']}). "
            "Citations are fetched live from NCBI E-utilities."
        )

    # Default: summarize top edge
    if edges:
        e = edges[0]
        return (
            f"Strongest edge: {e['source_cell_type']} signals to {e['target_cell_type']} via "
            f"{e['ligand']}→{e['receptor']} (NicheNet score {e['score']}). "
            "Ask about 'cell types', 'qc', or 'methods' for more detail."
        )
    return "Analysis results are limited. Check Overview for pipeline status."
