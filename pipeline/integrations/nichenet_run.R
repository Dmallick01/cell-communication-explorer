#!/usr/bin/env Rscript
# NicheNet ligand-receptor prioritization (Browaeys et al., Nat Methods 2020)
# Args: expression_csv meta_csv sender receiver priors_dir output.json

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 6) {
  stop("Usage: nichenet_run.R <expr_csv> <meta_csv> <sender> <receiver> <priors_dir> <output.json>")
}

expr_path <- args[1]
meta_path <- args[2]
sender_type <- args[3]
receiver_type <- args[4]
priors_dir <- args[5]
out_path <- args[6]

suppressPackageStartupMessages({
  if (!requireNamespace("nichenetr", quietly = TRUE)) {
    stop("R package 'nichenetr' not installed. Run: remotes::install_github('saeyslab/nichenetr')")
  }
  library(nichenetr)
  library(dplyr)
  library(jsonlite)
})

expr <- read.csv(expr_path, row.names = 1, check.names = FALSE)
meta <- read.csv(meta_path, row.names = 1, check.names = FALSE)

lr_rds <- file.path(priors_dir, "lr_network_human_21122021.rds")
lt_rds <- file.path(priors_dir, "ligand_target_matrix_nsga2r_final.rds")
wn_rds <- file.path(priors_dir, "weighted_networks_nsga2r_final.rds")

if (file.exists(lr_rds)) {
  lr_network <- readRDS(lr_rds)
  ligand_target <- readRDS(lt_rds)
  weighted_networks <- readRDS(wn_rds)
  sig_network <- weighted_networks$sig
  gr_network <- weighted_networks$gr
} else {
  # Legacy CSV layout (deprecated — re-run download_priors.sh)
  ligand_target <- read.csv(file.path(priors_dir, "ligand_target_matrix_nsga2r_final.csv"), check.names = FALSE)
  lr_network <- read.csv(file.path(priors_dir, "ligand_receptor_matrix.csv"), check.names = FALSE)
  sig_network <- read.csv(file.path(priors_dir, "weighted_networks", "ligand_signaling_network.csv"), check.names = FALSE)
  gr_network <- read.csv(file.path(priors_dir, "weighted_networks", "gr_network.csv"), check.names = FALSE)
}

sender_cells <- rownames(meta)[meta$cell_type == sender_type]
receiver_cells <- rownames(meta)[meta$cell_type == receiver_type]

if (length(sender_cells) < 10 || length(receiver_cells) < 10) {
  stop(paste("Insufficient cells for", sender_type, "or", receiver_type))
}

sender_expr <- expr[, sender_cells, drop = FALSE]
receiver_expr <- expr[, receiver_cells, drop = FALSE]

expressed_sender <- rownames(sender_expr)[rowMeans(sender_expr) > 0]
background_expressed_genes <- rownames(receiver_expr)[rowMeans(receiver_expr) > 0]

if (length(background_expressed_genes) < 20) {
  stop("No expressed ligands or receptors in LR network")
}

# Geneset must differ from background — use top variable genes in receiver
receiver_vars <- apply(receiver_expr[background_expressed_genes, , drop = FALSE], 1, var)
geneset_oi <- names(sort(receiver_vars, decreasing = TRUE))[
  seq_len(min(200L, length(receiver_vars)))
]

ligands <- lr_network %>% filter(from %in% expressed_sender) %>% pull(from) %>% unique()
receptors <- lr_network %>% filter(to %in% background_expressed_genes) %>% pull(to) %>% unique()

if (length(ligands) == 0 || length(receptors) == 0) {
  stop("No expressed ligands or receptors in LR network")
}

ligand_activities <- predict_ligand_activities(
  geneset = geneset_oi,
  background_expressed_genes = background_expressed_genes,
  ligand_target_matrix = ligand_target,
  potential_ligands = ligands
)

best_ligands <- ligand_activities %>% arrange(desc(pearson)) %>% head(20) %>% pull(test_ligand)

edges <- lr_network %>%
  filter(from %in% best_ligands, to %in% receptors) %>%
  mutate(
    source_cell_type = sender_type,
    target_cell_type = receiver_type,
    ligand = from,
    receptor = to,
    score = 1.0,
    p_value = NA_real_,
    evidence_tier = "SUPPORTED",
    method = "nichenet"
  ) %>%
  select(source_cell_type, target_cell_type, ligand, receptor, score, p_value, evidence_tier, method)

write_json(edges, out_path, pretty = TRUE, auto_unbox = TRUE)
