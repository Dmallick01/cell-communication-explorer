#!/usr/bin/env python3
"""Phase 0 benchmark runner — validates pipeline on PBMC3k and Kang IFN-β."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import time
from pathlib import Path

from pipeline.benchmarks.acceptance import summarize, validate_kang_ifn, validate_pbmc3k
from pipeline.benchmarks.datasets import fetch_kang_ifn, fetch_pbmc3k, resolve_dataset
from pipeline.integrations.nichenet import nichenet_available
from pipeline.runner import run_pipeline


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _preflight(reference_dir: Path) -> None:
    ok, msg = nichenet_available(reference_dir)
    if not ok:
        print(f"PREFLIGHT FAIL: {msg}", file=sys.stderr)
        sys.exit(1)
    if not shutil.which("Rscript"):
        print("PREFLIGHT FAIL: Rscript not found. Install R 4.4+.", file=sys.stderr)
        sys.exit(1)
    import subprocess

    r_check = subprocess.run(
        ["Rscript", "-e", 'stopifnot(requireNamespace("nichenetr", quietly=TRUE))'],
        capture_output=True,
        text=True,
    )
    if r_check.returncode != 0:
        print(
            "PREFLIGHT FAIL: R package 'nichenetr' not installed.\n"
            "  Run: R -e 'install.packages(\"remotes\"); remotes::install_github(\"saeyslab/nichenetr\")'",
            file=sys.stderr,
        )
        sys.exit(1)
    print("Preflight OK: NicheNet priors + Rscript + nichenetr available")


def run_benchmark(
    dataset: str,
    input_path: Path,
    *,
    reference_dir: Path,
    max_cells: int | None = None,
) -> dict:
    job_id = f"bench-{dataset}"
    out = Path(tempfile.mkdtemp(prefix=f"cce-bench-{dataset}-"))
    print(f"Output: {out}")

    # Optional subsample for faster CI (not used for Phase 0 pass)
    effective_input = str(input_path)
    if max_cells:
        import anndata as ad

        adata = ad.read_h5ad(input_path)
        if adata.n_obs > max_cells:
            import numpy as np

            idx = np.random.default_rng(0).choice(adata.n_obs, max_cells, replace=False)
            sub_path = out / "subsample.h5ad"
            adata[idx].write_h5ad(sub_path)
            effective_input = str(sub_path)
            print(f"Subsampled to {max_cells} cells")

    t0 = time.time()
    results = run_pipeline(
        job_id=job_id,
        input_path=effective_input,
        metadata_path=None,
        output_dir=str(out),
        reference_dir=str(reference_dir),
        demo_mode=False,
    )
    elapsed = time.time() - t0
    results["elapsed_seconds"] = round(elapsed, 1)
    results["output_dir"] = str(out)

    if dataset.startswith("pbmc"):
        checks = validate_pbmc3k(results, out)
    else:
        checks = validate_kang_ifn(results, out)

    report = summarize(checks)
    report["dataset"] = dataset
    report["elapsed_seconds"] = results["elapsed_seconds"]
    report["output_dir"] = str(out)

    report_path = Path("benchmarks") / f"{dataset}_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cell Communication Explorer Phase 0 benchmarks")
    parser.add_argument("--dataset", choices=["pbmc3k", "kang_ifn", "all"], default="pbmc3k")
    parser.add_argument("--input", type=Path, help="Path to .h5ad (overrides default location)")
    parser.add_argument("--fetch", action="store_true", help="Download dataset if missing")
    parser.add_argument("--max-cells", type=int, default=None, help="Subsample for quick smoke tests")
    parser.add_argument("--reference-dir", type=Path, default=_repo_root() / "reference")
    args = parser.parse_args(argv)

    _preflight(args.reference_dir)

    datasets = ["pbmc3k", "kang_ifn"] if args.dataset == "all" else [args.dataset]
    all_ok = True

    for ds in datasets:
        print(f"\n=== Benchmark: {ds} ===")
        if args.input and len(datasets) == 1:
            input_path = args.input
        else:
            if args.fetch:
                if ds == "pbmc3k":
                    input_path = fetch_pbmc3k()
                else:
                    input_path = fetch_kang_ifn()
            else:
                input_path = resolve_dataset(ds, fetch=False)

        if not input_path.is_file():
            print(f"Missing input: {input_path}. Run with --fetch", file=sys.stderr)
            all_ok = False
            continue

        report = run_benchmark(
            ds,
            input_path,
            reference_dir=args.reference_dir,
            max_cells=args.max_cells,
        )
        if not report["ok"]:
            all_ok = False

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
