#!/usr/bin/env bash
# Download official NicheNet v2 human priors (Browaeys et al., Zenodo 7074291)
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
BASE="https://zenodo.org/record/7074291/files"

download() {
  local url="$1"
  local dest="$2"
  if [[ -f "$dest" ]] && [[ $(wc -c < "$dest") -gt 10000 ]]; then
    echo "exists: $dest"
    return
  fi
  echo "downloading: $dest"
  curl -Lf "$url" -o "$dest"
  if [[ $(wc -c < "$dest") -lt 10000 ]]; then
    echo "ERROR: download too small (likely HTML error page): $dest" >&2
    rm -f "$dest"
    exit 1
  fi
}

mkdir -p "$DIR/weighted_networks"

# RDS format (official nichenetr vignette URLs — CSV paths on Zenodo return 404)
download "$BASE/lr_network_human_21122021.rds" "$DIR/lr_network_human_21122021.rds"
download "$BASE/ligand_target_matrix_nsga2r_final.rds" "$DIR/ligand_target_matrix_nsga2r_final.rds"
download "$BASE/weighted_networks_nsga2r_final.rds" "$DIR/weighted_networks_nsga2r_final.rds"

echo "NicheNet priors ready in $DIR"
