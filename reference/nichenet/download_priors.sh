#!/usr/bin/env bash
# Download official NicheNet human prior files (Browaeys et al., Nat Methods 2020)
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$DIR/weighted_networks"

download() {
  local url="$1"
  local dest="$2"
  if [[ -f "$dest" ]]; then
    echo "exists: $dest"
    return
  fi
  echo "downloading: $dest"
  curl -L "$url" -o "$dest"
}

download "https://zenodo.org/records/7074291/files/ligand_target_matrix_nsga2r_final.csv" \
  "$DIR/ligand_target_matrix_nsga2r_final.csv"
download "https://zenodo.org/records/7074291/files/ligand_receptor_matrix.csv" \
  "$DIR/ligand_receptor_matrix.csv"
download "https://zenodo.org/records/7074291/files/ligand_signaling_network.csv" \
  "$DIR/weighted_networks/ligand_signaling_network.csv"
download "https://zenodo.org/records/7074291/files/gr_network.csv" \
  "$DIR/weighted_networks/gr_network.csv"

echo "NicheNet priors ready in $DIR"
