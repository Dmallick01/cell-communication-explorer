from __future__ import annotations

import json
from pathlib import Path
from typing import Any

IFN_GENES = {"IFNG", "IFNB1", "IFIT1", "IFIT2", "IFIT3", "ISG15", "MX1", "OAS1", "IRF7", "STAT1"}


def _check(name: str, ok: bool, detail: str) -> dict[str, Any]:
    return {"name": name, "passed": ok, "detail": detail}


def validate_pbmc3k(results: dict[str, Any], output_dir: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    cell_types = results.get("cell_types") or []
    edges = results.get("communication_edges") or []
    params = results.get("exports", {})

    checks.append(
        _check(
            "cell_types",
            len(cell_types) >= 6,
            f"{len(cell_types)} cell types annotated (need ≥6)",
        )
    )
    checks.append(
        _check(
            "nichenet_edges",
            len(edges) >= 10,
            f"{len(edges)} LR edges (need ≥10)",
        )
    )

    methods_path = output_dir / "methods.txt"
    methods_text = methods_path.read_text() if methods_path.is_file() else ""
    cites = ["Scanpy", "CellTypist", "NicheNet"]
    missing = [c for c in cites if c.lower() not in methods_text.lower()]
    checks.append(
        _check(
            "methods_citations",
            not missing,
            "missing: " + ", ".join(missing) if missing else "Scanpy, CellTypist, NicheNet cited",
        )
    )

    prov_path = output_dir / "provenance.json"
    prov_ok = False
    prov_detail = "provenance.json not found"
    if prov_path.is_file():
        prov = json.loads(prov_path.read_text())
        hashes = prov.get("reference_files_sha256") or {}
        prov_ok = len(hashes) >= 4 and all(hashes.values())
        prov_detail = f"{len(hashes)} NicheNet prior SHA256 hashes recorded"
    checks.append(_check("provenance_hashes", prov_ok, prov_detail))

    exports = results.get("exports") or {}
    checks.append(
        _check(
            "nichenet_method",
            results.get("communication_method") == "nichenet",
            "NicheNet communication (no synthetic LR scoring)",
        )
    )
    checks.append(_check("exports_present", bool(exports), f"{len(exports)} export artifacts"))

    return checks


def validate_kang_ifn(results: dict[str, Any], output_dir: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    de_tables = results.get("de_tables") or []
    edges = results.get("communication_edges") or []

    isg_hits = [
        row
        for row in de_tables
        if str(row.get("names", row.get("gene", ""))).upper() in IFN_GENES
    ]
    checks.append(
        _check(
            "isg_de",
            len(isg_hits) > 0,
            f"{len(isg_hits)} ISG/IFN genes in DE tables",
        )
    )

    edge_genes = {e.get("ligand", "").upper() for e in edges} | {e.get("receptor", "").upper() for e in edges}
    ifn_edge = edge_genes & IFN_GENES
    checks.append(
        _check(
            "ifn_pathway_edges",
            bool(ifn_edge),
            f"IFN-pathway genes in edges: {', '.join(sorted(ifn_edge)) or 'none'}",
        )
    )

    checks.append(
        _check(
            "nichenet_edges",
            len(edges) >= 5,
            f"{len(edges)} LR edges (need ≥5 for Kang subset)",
        )
    )

    return checks


def summarize(checks: list[dict[str, Any]]) -> dict[str, Any]:
    passed = sum(1 for c in checks if c["passed"])
    return {
        "passed": passed,
        "total": len(checks),
        "ok": passed == len(checks),
        "checks": checks,
    }
