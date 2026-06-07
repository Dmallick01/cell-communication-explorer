from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

import anndata as ad
import pandas as pd

from pipeline.utils.checkpoints import CheckpointError


def nichenet_available(reference_dir: Path) -> tuple[bool, str]:
    rscript = shutil.which("Rscript")
    if not rscript:
        return False, "Rscript not found. Install R 4.4+ and nichenetr package."

    priors = reference_dir / "nichenet"
    required = [
        priors / "ligand_target_matrix_nsga2r_final.csv",
        priors / "ligand_receptor_matrix.csv",
        priors / "weighted_networks" / "ligand_signaling_network.csv",
        priors / "weighted_networks" / "gr_network.csv",
    ]
    missing = [str(p.relative_to(priors.parent.parent)) for p in required if not p.is_file()]
    if missing:
        return False, (
            "NicheNet prior files missing. Run: bash reference/nichenet/download_priors.sh "
            f"Missing: {', '.join(missing)}"
        )

    r_script = Path(__file__).parent / "nichenet_run.R"
    if not r_script.is_file():
        return False, "nichenet_run.R not found"

    return True, "ok"


def run_nichenet(
    adata: ad.AnnData,
    output_dir: Path,
    reference_dir: Path,
    top_sender_receiver_pairs: int = 15,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    ok, msg = nichenet_available(reference_dir)
    if not ok:
        raise CheckpointError(msg)

    work = output_dir / "nichenet_work"
    work.mkdir(parents=True, exist_ok=True)

    # Expression: genes × cells (NicheNet convention)
    X = adata.X
    if hasattr(X, "toarray"):
        X = X.toarray()
    expr = pd.DataFrame(X.T, index=adata.obs_names, columns=adata.var_names)
    expr_path = work / "expression.csv"
    expr.to_csv(expr_path)

    meta = adata.obs[["cell_type"]].copy()
    meta_path = work / "metadata.csv"
    meta.to_csv(meta_path)

    priors_dir = reference_dir / "nichenet"
    r_script = Path(__file__).parent / "nichenet_run.R"
    cell_types = list(adata.obs["cell_type"].unique())
    all_edges: list[dict[str, Any]] = []

    pairs_done = 0
    for sender in cell_types:
        for receiver in cell_types:
            if sender == receiver:
                continue
            if pairs_done >= top_sender_receiver_pairs:
                break

            out_json = work / f"edges_{sender}_{receiver}.json"
            cmd = [
                "Rscript",
                str(r_script),
                str(expr_path),
                str(meta_path),
                str(sender),
                str(receiver),
                str(priors_dir),
                str(out_json),
            ]
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=600)
            except subprocess.CalledProcessError as exc:
                # Skip pairs with insufficient cells; continue
                stderr = exc.stderr or ""
                if "Insufficient cells" in stderr:
                    continue
                raise CheckpointError(f"NicheNet failed for {sender}->{receiver}: {stderr}") from exc
            except subprocess.TimeoutExpired as exc:
                raise CheckpointError("NicheNet timed out") from exc

            if out_json.is_file():
                edges = json.loads(out_json.read_text())
                if isinstance(edges, dict):
                    edges = [edges]
                all_edges.extend(edges)
                pairs_done += 1

    if not all_edges:
        raise CheckpointError(
            "NicheNet produced no ligand-receptor edges. "
            "Check cell-type counts (≥10 per type) and gene symbol mapping."
        )

    # Rank and deduplicate
    seen = set()
    ranked: list[dict[str, Any]] = []
    for e in all_edges:
        key = (e["source_cell_type"], e["target_cell_type"], e["ligand"], e["receptor"])
        if key in seen:
            continue
        seen.add(key)
        ranked.append(e)

    metrics = {
        "method": "nichenet",
        "citation": "Browaeys et al., Nat Methods 2020",
        "n_edges": len(ranked),
        "n_cell_types": len(cell_types),
        "pairs_analyzed": pairs_done,
        "priors_dir": str(priors_dir),
    }
    return ranked[:100], metrics
