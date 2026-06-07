# CURSOR MASTER BUILD PROMPT
## Cell Communication Explorer (CCE) — Full-Stack Research Platform

> **How to use this document:** Paste this entire file (or sections by phase) into Cursor when starting a build session. Every feature must cite a validated open-source tool or primary literature. No synthetic biology. No uncited claims.

---

# PART 0 — EXECUTIVE SUMMARY

## What we are building

**Cell Communication Explorer** is a research-grade, end-to-end platform that helps biomedical scientists go from **single-cell RNA-seq (scRNA-seq)** to **testable hypotheses** about **who signals to whom, through which molecules, via which pathways, and why (including epigenetic context)** — in disease vs. healthy tissue.

It is **not** disease-specific (works for heart, skin, brain, any dissociated tissue). It is **not** a toy demo. It is **not** a black-box AI oracle.

### The scientist's question (canonical workflow)

1. Dissociate tissue (e.g., heart) to **viable individual cells** (cardiomyocytes, macrophages, fibroblasts, T/B cells, endothelial, etc.).
2. Run **scRNA-seq** → expression matrix + metadata (patient ID, condition, batch).
3. **Cluster & annotate** cell types (fibroblasts by collagen, macrophages by CD68/IBA1, etc.).
4. Compare **disease vs. control** per cell type (e.g., T2D vs. healthy fibroblasts show transcriptional shift; cardiomyocytes may not).
5. Ask: **Which cell type A is "talking to" cell type B to cause the shift?**
   - Example (T2D): Are macrophages reprogramming fibroblasts via secreted ligands?
   - Example (scleroderma): Fli1 underexpression in monocytes/macrophages → fibrosis. Which cells express Fli1? What do endothelial cells vs. macrophages signal to fibroblasts to drive collagen overproduction?
6. Need: **cell-to-cell signaling map** (ligand → receptor → pathway → TF → target genes → phenotype), grounded in **published evidence**, plus **suggested validation experiments**.

### Deliverables per analysis run

| Output | Description |
|--------|-------------|
| **Cell-type atlas** | Annotated clusters, UMAP, disease vs. control DE per type |
| **Communication network** | Ranked ligand–receptor edges with statistics |
| **Signaling cascade view** | Ligand secretion → receptor → MAPK/etc. → nuclear effect |
| **Epigenetic context** | Promoter methylation / accessibility hypotheses where data allows |
| **Literature evidence** | PMIDs, titles, abstracts per edge and per gene |
| **Hypothesis report** | "Macrophage X may drive fibroblast Y via cytokine Z" — labeled HYPOTHESIS |
| **Experiment table** | CRISPR KO/KD, cytokine blockade, co-culture, ChIP, bisulfite seq, etc. |
| **Methods paragraph** | Publication-ready, version-pinned, fully cited |
| **Chat Q&A** | Natural-language queries over *this run's* data + knowledge base |

### Deployment targets

- **Web app** (primary): Next.js, cloud-hosted (Fly.io / Render / Vercel frontend + API)
- **macOS DMG** (secondary): Tauri wrapper bundling local FastAPI + embedded Python/R runtime
- **Design reference:** Match the aesthetic of the user's **DTube** project in Cursor — clean, modern, content-first, minimal chrome, dark/light theme, fast interactions. Reference sites: dimden.dev, khanux.com (typography-led, not cluttered).

---

# PART 1 — CORE PRINCIPLES (NON-NEGOTIABLE)

1. **Citation before claim** — Every biological statement links to PMID, database entry, or "user data (unvalidated)".
2. **Free & open-source first** — MIT/BSD/Apache tools only for core pipeline. No paywalled DBs in v1.
3. **Reproducibility** — Every job stores: tool versions, parameters, reference file SHA256 hashes, random seeds.
4. **Hypothesis ≠ fact** — All causal language prefixed with confidence tier: `ESTABLISHED` | `SUPPORTED` | `HYPOTHESIS` | `SPECULATIVE`.
5. **No demo biology in production** — Benchmark datasets (PBMC, Kang IFN, etc.) replace synthetic data.
6. **Supervisor agent always on** — One orchestrator validates checkpoints, retries failures, blocks release on regression.
7. **Parallel agents where independent** — Literature mining per edge can fan out; analysis steps respect DAG order.
8. **Privacy** — User uploads stay on their instance unless opted into cloud; literature fetch is the only external call by default.

---

# PART 2 — SCIENTIFIC ONTOLOGY (WHAT THE APP "KNOWS")

## 2.1 Entity types (knowledge graph nodes)

```
Tissue → Sample → Cell → CellType → Cluster
Gene → Transcript → Protein → Ligand | Receptor
Pathway → TF → Promoter → EpigeneticMark (methylation, H3K27ac, etc.)
Interaction (LR pair) → Edge (CellType_A → CellType_B)
Disease → Phenotype (fibrosis, inflammation, etc.)
Publication (PMID) → Evidence (supports | contradicts | neutral)
Experiment → ValidationDesign
```

## 2.2 Relationship types (knowledge graph edges)

```
CellType --expresses--> Gene
Gene --encodes--> Protein
Ligand --binds--> Receptor
CellType_A --secretes--> Ligand
CellType_B --expresses--> Receptor
Receptor --activates--> Pathway
Pathway --regulates--> TF
TF --binds--> Promoter
Promoter --methylated_in--> DiseaseState
Interaction --supported_by--> Publication
Interaction --hypothesized_in--> JobRun
```

## 2.3 Signaling layer stack (UI visualization)

```
Layer 0: DNA / Epigenome (promoter methylation, histone state — when ATAC/ChIP data present or imputed from databases)
Layer 1: Transcription (scRNA-seq DE, TF activity inference)
Layer 2: Translation / Protein (optional: surfaceome, secretome databases)
Layer 3: Secreted ligand (sender cell)
Layer 4: Receptor binding (receiver cell)
Layer 5: Intracellular cascade (KEGG/Reactome)
Layer 6: Phenotype (fibrosis score, inflammatory score — gene set based)
```

User clicks an edge in the Sankey/network → popover walks layers 3→6 with citations.

---

# PART 3 — FREE & OPEN-SOURCE STACK (MANDATORY)

## 3.1 Frontend

| Component | Tool | License |
|-----------|------|---------|
| Framework | Next.js 15+ (App Router) | MIT |
| UI | MUI v6 or shadcn (match DTube) | MIT |
| Charts | Plotly.js, Cytoscape.js (networks), Sankey (plotly/d3) | MIT |
| Chat | Vercel AI SDK + streaming | Apache 2.0 |
| State | TanStack Query | MIT |
| Desktop | Tauri 2.x | MIT/Apache |

## 3.2 Backend

| Component | Tool | License |
|-----------|------|---------|
| API | FastAPI + Uvicorn | MIT |
| Jobs | PostgreSQL + SQLAlchemy | PostgreSQL / MIT |
| Queue | Redis or RabbitMQ (optional v2) | BSD / MPL |
| Object storage | MinIO (S3-compatible) | Apache 2.0 |
| Vector DB | pgvector (Postgres extension) | PostgreSQL |
| Auth | JWT (optional) / Clerk free tier | — |

## 3.3 Scientific compute

| Step | Tool | Key paper |
|------|------|-----------|
| QC / norm / cluster | Scanpy | Wolf et al. 2018 |
| Doublets | Scrublet | Wolock et al. 2019 |
| Batch correction | Harmony | Korsunsky et al. 2019 |
| Cell typing | CellTypist | Domínguez et al. 2022 |
| LR inference (primary) | NicheNet (R) | Browaeys et al. 2020 |
| LR inference (alt) | CellPhoneDB | Efremova et al. 2020 |
| LR inference (alt) | CellChat (R) | Jin et al. 2021 |
| Pathways | gseapy (MSigDB, KEGG, Reactome) | — |
| TF activity | decoupleR / pySCENIC (phase 3) | — |
| Epigenome refs | ENCODE, EpiMap (downloadable BEDs) | — |
| Protein structure note | UniProt API (free) | — |
| Literature | Entrez E-utilities, Europe PMC REST | Public |

## 3.4 LLM (strictly gated)

| Use | Model | Rule |
|-----|-------|------|
| Literature summarization | GPT-4o / local Llama via vLLM | Every sentence must cite PMID from retrieved set |
| Chat Q&A | Same | Retrieval-augmented only; no parametric biology |
| Experiment design | Same | Output labeled HYPOTHESIS; cite similar studies |

## 3.5 CI / monitoring (free tier)

- GitHub Actions
- Prometheus + Grafana (self-hosted)
- Sentry (free tier)
- Testcontainers for integration tests

---

# PART 4 — MULTI-AGENT ARCHITECTURE

## 4.1 Agent roster

| ID | Name | Role | Runs |
|----|------|------|------|
| **0** | Supervisor | Orchestration, checkpoints, retries, alerts | Always |
| **A** | DataPrep | Ingest, validate, convert to AnnData | Sequential |
| **B** | CoreAnalysis | QC, Harmony, cluster, DE, pathway enrichment | After A |
| **C** | LiteratureMiner | PubMed/Europe PMC per edge/gene | Parallel per edge |
| **D** | CellComm | NicheNet / CellPhoneDB / CellChat | After B |
| **E** | EpigenomeContext | Map genes to promoter methylation refs | After B (parallel with D) |
| **F** | PathwayCASCADE | Ligand→receptor→pathway→TF→target | After D |
| **G** | ValidationDesigner | CRISPR, siRNA, cytokine, co-culture proposals | After C+D+F |
| **H** | KnowledgeBuilder | Embed papers + edges into pgvector | After C |
| **I** | ReportEngine | HTML, PDF, methods.txt, provenance.json | After all |
| **J** | ChatAgent | RAG over job + KB | On user query |
| **K** | HealthMonitor | Heartbeat, resource checks, regression tests | Every 30s |

## 4.2 Supervisor (Agent 0) specification

```python
# Pseudocode contract for Supervisor
class Supervisor:
    def launch_job(job_id, config):
        dag = ["A", "B", ("D","E"), "F", ("C"*N_edges), "G", "H", "I"]
        for step in dag:
            spawn_agent(step, job_id)
            wait_for_checkpoint(step)
            if failed and retries < 3:
                exponential_backoff_retry(step)
            elif failed:
                mark_job_failed(job_id)
                notify_user(email|slack)
                log_to_sentry()
    
    def poll():
        every 30s: read agent logs, update Postgres, emit Prometheus metrics
```

**Idempotency:** Re-run only failed step; upstream artifacts cached in S3/MinIO by content hash.

## 4.3 Checkpoint matrix (Supervisor enforces)

| Checkpoint | Agent | Tool | Pass criteria | On fail |
|------------|-------|------|---------------|---------|
| Input sanity | A | JSON schema | Unique barcodes, ≥50 cells, ≥200 genes | Reject upload |
| QC | B | Scanpy | Mito median <25%, doublets <10%, ≥30 cells | Retry A→B once |
| Batch | B | Harmony | Convergence, batch vars documented | Skip if no batch col |
| Cluster stability | B | silhouette | Report score (warn if <0.15, don't hard-fail) | Warn only |
| DE sanity | B | BH-FDR | Valid p-value distribution | Flag in report |
| Cell types | B | CellTypist | ≥1 type with confidence >0.5 | Fallback + warn |
| LR network | D | NicheNet | ≥1 edge with p_adj <0.05 | Fail with message |
| Literature | C | Entrez | ≥1 PMID per top-10 edge OR "none found" | Retry 2x |
| Citation integrity | H | regex validator | 100% sentences have [PMID:...] in summaries | Regenerate |
| Report | I | WeasyPrint | PDF + HTML render | Retry |
| E2E nightly | K | CI | Full pipeline on PBMC benchmark | Block deploy |

## 4.4 Parallel fan-out pattern (Literature Agent C)

```
For each edge in top_K_edges (default K=50, max 10 concurrent workers):
  query = f"{ligand} AND {receptor} AND {source_cell} AND {target_cell} AND {disease}"
  pmids = entrez_search(query, max=10)
  for pmid in pmids:
    abstract = efetch(pmid)
    chunk + embed → pgvector
    summary = llm_summarize(abstract, must_cite=pmid)
  aggregate → evidence_block attached to edge
```

---

# PART 5 — KNOWLEDGE BASE DESIGN

## 5.1 Three-tier memory

| Tier | Store | Contents | Lifecycle |
|------|-------|----------|-----------|
| **Run memory** | Postgres per job | AnnData refs, DE tables, edges, parameters | User-owned, deletable |
| **Evidence cache** | MinIO + Postgres | PDFs, abstracts, embedding chunks | Global, PMID-keyed |
| **Organism KB** | pgvector + Postgres | Curated LR DBs, pathway maps, TF-target priors | Versioned, admin-updated |

## 5.2 Reference data manifests (ship with app)

```
reference/
  nichenet/
    human_ligand_target_matrix.csv   # SHA256 pinned
    human_lr_network.csv
    human_gr_network.csv
  cellphonedb/
    v5.0/cellphonedb.zip
  cellchat/
    CellChatDB.human.rda
  pathways/
    reactome_2024.gmt
    kegg_hsa.gmt
  epigenome/
    encode_tf_binding_bed/          # optional download
  benchmarks/
    pbmc3k/                         # 10x public
    kang_ifn/                       # GEO GSE96583
  citations.json                    # tool → DOI mapping
```

## 5.3 pgvector schema

```sql
CREATE TABLE evidence_chunks (
  id UUID PRIMARY KEY,
  pmid TEXT NOT NULL,
  gene_pair TEXT,
  cell_pair TEXT,
  disease TEXT,
  chunk_text TEXT,
  embedding vector(1536),
  source_url TEXT,
  created_at TIMESTAMPTZ
);
CREATE INDEX ON evidence_chunks USING ivfflat (embedding vector_cosine_ops);

CREATE TABLE interactions (
  id UUID PRIMARY KEY,
  job_id UUID,
  source_cell_type TEXT,
  target_cell_type TEXT,
  ligand TEXT,
  receptor TEXT,
  score FLOAT,
  p_value FLOAT,
  evidence_tier TEXT,  -- ESTABLISHED|SUPPORTED|HYPOTHESIS
  pmids TEXT[]
);
```

## 5.4 Chat RAG scope

Chat agent retrieves from:
1. Current job results (DE, edges, QC)
2. Evidence chunks for genes/edges mentioned in query
3. Knowledge graph paths (precomputed)
4. **Never** from LLM weights for factual claims

Example queries:
- "Which signaling pathways are unique to diabetic fibroblasts?"
- "Is there prior evidence for CXCL12–CXCR4 between macrophages and fibroblasts in cardiac tissue?"
- "Why might Fli1 downregulation in monocytes cause fibroblast collagen overproduction in scleroderma?"

---

# PART 6 — USER INPUTS (FORMAL SPEC)

## 6.1 Required uploads

| Field | Format | Validation |
|-------|--------|------------|
| Expression matrix | `.h5ad`, 10x `.zip`, `.mtx`+barcodes+features | Barcode uniqueness |
| Cell metadata | CSV (index=barcode) | Must have `condition` (disease/control) |
| Sample metadata | CSV (optional) | batch, patient_id, tissue, disease_name |
| Comparison config | UI form | e.g. `fibroblast: T2D vs control` |

## 6.2 Optional uploads (unlock advanced layers)

| Field | Unlocks |
|-------|---------|
| scATAC-seq (h5ad) | Real epigenome layer |
| Bulk RNA-seq | Pseudo-bulk validation |
| Spatial coords | Spatial CellChat (v3) |
| Known marker genes | Custom annotation override |

## 6.3 Analysis parameters (exposed in UI, defaults from literature)

```
organism: human | mouse
communication_method: nichenet | cellphonedb | cellchat
min_cells_per_type: 25
de_method: wilcoxon
de_fdr: 0.05
logfc_threshold: 0.25
nichenet_top_ligands: 20
literature_max_papers_per_edge: 10
disease_ontology: EFO term (optional, improves literature query)
```

---

# PART 7 — UI / UX SPECIFICATION (DTube-STYLE)

## 7.1 Design language

- **Layout:** Left sidebar navigation + main canvas (like DTube)
- **Typography:** Inter or Geist; large headings, generous whitespace
- **Color:** Deep navy primary (`#0f3460`), accent coral/red (`#e94560`), off-white background
- **Tone:** Professional lab software, not consumer app
- **No:** Gamified checkpoints, toy illustrations, "demo" buttons in production

## 7.2 Pages / routes

```
/                     → Landing + new project
/projects             → List of analysis runs
/projects/[id]        → Main dashboard (tabbed)
  ├─ Overview         → QC summary, cell type counts, condition comparison
  ├─ Cells            → UMAP, dotplot markers, DE tables per type
  ├─ Communication    → Network graph, Sankey, heatmap, edge table
  ├─ Cascades         → Selected edge → pathway walk-through
  ├─ Epigenome        → Promoter/TF context (when available)
  ├─ Literature       → Evidence panel per edge/gene
  ├─ Experiments      → Validation design table
  ├─ Report           → Download PDF/HTML/methods
  └─ Chat             → RAG chat interface
/settings             → API keys, reference data versions
/benchmarks           → Run validation datasets (admin)
```

## 7.3 Key visualizations

| Viz | Library | Interaction |
|-----|---------|-------------|
| UMAP (cells) | Plotly | Click cell type → filter all panels |
| UMAP split (D vs C) | Plotly facets | Side-by-side disease/control |
| Communication network | Cytoscape.js | Click edge → cascade + literature |
| Sankey (cell→ligand→receptor→cell) | Plotly Sankey | Top N flows |
| LR heatmap | Plotly | Source × target cell types |
| Pathway cascade | Custom SVG / Mermaid | Ligand→receptor→MAPK→TF→gene |
| DE volcano | Plotly | Per cell type tab |
| Evidence timeline | Table + links | PMIDs expandable |
| Experiment matrix | MUI DataGrid | Export CSV |

## 7.4 Cell-to-cell cascade card (signature UI element)

For edge `Macrophage → CXCL12 → CXCR4 → Fibroblast`:

```
┌─────────────────────────────────────────────────────────────┐
│ Macrophage (T2D)  ──secretes──▶  CXCL12  [PMID: 12345678]  │
│         │                                                    │
│         ▼                                                    │
│ Fibroblast (T2D)  ──expresses──▶  CXCR4  [CellPhoneDB]      │
│         │                                                    │
│         ▼                                                    │
│ Pathway: MAPK / ERK  [Reactome:R-HSA-...]                   │
│         │                                                    │
│         ▼                                                    │
│ TF: AP-1  →  Target genes: COL1A1, COL3A1 (↑ in T2D)       │
│         │                                                    │
│         ▼                                                    │
│ Phenotype: Fibrosis score ↑  [HYPOTHESIS — verify ex vivo]  │
│                                                              │
│ Epigenome: COL1A1 promoter — hypermethylation in control?   │
│            [ENCODE ref / HYPOTHESIS if no ATAC]              │
└─────────────────────────────────────────────────────────────┘
```

---

# PART 8 — PHASED BUILD ROADMAP (ENRICHED)

## PHASE 0 — Research foundation (weeks 1–4)
**Goal:** Validated pipeline on real benchmarks. No polish.

- [ ] Pin Docker image: Python 3.12 + R 4.4 + Scanpy + NicheNet + CellPhoneDB
- [ ] Download & hash all NicheNet human priors
- [ ] Implement `provenance.json` + `methods.txt` generator
- [ ] Run Kang IFN + PBMC3k benchmarks; document in `VALIDATION.md`
- [ ] Remove synthetic/demo from production builds
- [ ] Define acceptance: top-10 edges include ≥3 literature-supported pairs per benchmark

**Cursor task prompt:**
> Implement NicheNet integration with official human priors. Add provenance.json output with SHA256 of all reference files. Run against PBMC3k h5ad. Do not add UI.

---

## PHASE 1 — Research MVP (weeks 5–12)
**Goal:** Scientist uploads data → citable communication report in <30 min.

### 1.1 Ingest & QC (Agent A + B)
- h5ad, 10x zip, mtx+tsv
- Metadata: condition, batch, tissue, disease
- QC report with Scanpy + Scrublet
- Harmony batch correction when `batch` present
- Leiden clustering + UMAP
- CellTypist with confidence scores per cell
- DE per cell type: disease vs control (Wilcoxon, BH-FDR)
- Pathway enrichment (gseapy → Reactome/KEGG)

### 1.2 Communication (Agent D)
- NicheNet: sender/receiver cell types from annotation
- Rank ligand activities + target gene predictions
- Export edge table with scores and target gene lists
- Optional: CellPhoneDB statistical analysis as cross-check

### 1.3 Export (Agent I)
- HTML + PDF report
- CSV: edges, DE, cell types, pathways
- methods.txt with citations
- provenance.json

### 1.4 UI (minimal, DTube layout)
- Upload wizard
- Pipeline progress (step list, no gamification)
- Results: UMAP, edge table, network plot
- Download report

**Cursor task prompt:**
> Build Phase 1 backend DAG: A→B→D→I. Use Supervisor with SQLite job store. Add FastAPI endpoints. Create Next.js upload + results pages matching DTube sidebar layout. No chat, no literature yet.

---

## PHASE 2 — Evidence layer (weeks 13–20)
**Goal:** Every top edge backed by searchable literature.

### 2.1 Literature miner (Agent C)
- Entrez + Europe PMC
- 1 req/sec rate limit; PMID cache in Postgres
- Store title, abstract, link — no AI yet

### 2.2 UI literature panel
- Per edge: paper list
- Per gene: paper list filtered by disease term
- "No literature found" explicit state

### 2.3 Knowledge builder (Agent H v1)
- Chunk abstracts → pgvector
- Edge ↔ PMID many-to-many table

**Cursor task prompt:**
> Add parallel Literature Agent C: fan-out per top-20 edge, Entrez search with disease term from metadata. Store in Postgres. Add Literature tab in UI. No LLM summarization.

---

## PHASE 3 — Hypothesis & cascade (weeks 21–30)
**Goal:** Answer "who causes the shift?" with pathway context.

### 3.1 Pathway cascade (Agent F)
- Map receptor → KEGG/Reactome via OmniPath or gseapy
- TF target overlap with DE genes in receiver cell type
- Generate cascade diagram data JSON

### 3.2 Epigenome context (Agent E)
- Query ENCODE / EpiMap for TF binding near DE promoters
- If scATAC uploaded: real peak overlap
- Promoter methylation: integrate GEO methylation refs or impute as HYPOTHESIS
- Report: "Fli1 promoter methylation may silence expression in monocytes"

### 3.3 LLM summarization (gated)
- Summarize only retrieved abstracts
- Mandatory [PMID:...] per sentence
- Validator agent rejects uncited output

### 3.4 Validation designer (Agent G)
- CRISPR/siRNA suggestions via CRISPOR API (free)
- Cytokine neutralization experiments from literature patterns
- Co-culture designs
- ChIP/bisulfite for epigenome claims
- All labeled HYPOTHESIS with feasibility checklist

**Cursor task prompt:**
> Implement Agent F pathway cascade from LR edge to TF to DE targets. Add Epigenome Agent E with ENCODE TF binding lookup. Add Validation Agent G experiment table. Implement citation-gated LLM summarization for literature chunks.

---

## PHASE 4 — Chat & knowledge graph (weeks 31–40)
**Goal:** Conversational exploration of results + cross-run memory.

### 4.1 Chat agent (Agent J)
- RAG: job results + pgvector evidence + interaction graph
- Streaming UI (Vercel AI SDK)
- Every response includes source panel (PMIDs, data refs)
- Suggested questions: "What drives fibroblast shift in T2D?"

### 4.2 Knowledge graph UI
- Neo4j or Postgres recursive queries
- Explore: gene → pathway → cell type → disease

### 4.3 Cross-dataset comparison (v2.5)
- Compare edges across two jobs
- Meta-analysis: consistent LR pairs across studies

**Cursor task prompt:**
> Add Chat page with RAG over current job + evidence_chunks. Use streaming. Show citation panel beside each answer. Add Neo4j or Postgres graph queries for gene-pathway-cell traversal.

---

## PHASE 5 — Platform hardening (weeks 41–48)
**Goal:** Production deploy + Mac DMG + monitoring.

### 5.1 Deploy
- Docker multi-stage build
- Fly.io or Render for API
- Vercel for frontend
- Supabase Postgres + MinIO

### 5.2 Mac DMG (Tauri)
- Bundle FastAPI + Python venv + R + NicheNet
- WebView → localhost:8000
- Code sign script (unsigned for OSS, signed for release)

### 5.3 Health monitor (Agent K)
- Prometheus metrics: job duration, failure rate, literature cache hit rate
- Nightly CI: full benchmark pipeline
- Slack/email alert on regression

### 5.4 Security & privacy
- Max upload 2GB
- Self-hosted mode: disable external literature
- Audit log for all agent actions

**Cursor task prompt:**
> Create Tauri Mac wrapper. Bundle backend via pyoxidizer or embedded conda. Add Prometheus metrics to Supervisor. Set up GitHub Actions nightly benchmark CI.

---

# PART 9 — FEATURE EXHAUSTION LIST (BACKLOG)

Every item requires citation or explicit HYPOTHESIS label.

## Analysis features
- [ ] Multi-condition comparison (T2D vs prediabetic vs control)
- [ ] Pseudotime communication (CellChat)
- [ ] Spatial transcriptomics (stLearn, Squidpy)
- [ ] scATAC + scRNA multimodal (ArchR bridge)
- [ ] TF activity (decoupleR, DoRothEA)
- [ ] Protein structural notes (UniProt domains — only if phenotype-relevant)
- [ ] Cell–cell contact vs secreted signaling split
- [ ] Nichenet ligand activity vs target gene regulatory potential
- [ ] Custom marker-based annotation override
- [ ] Automatic disease ontology detection (EFO via OLS API)

## Literature & knowledge
- [ ] Europe PMC full-text PDF download
- [ ] Semantic Scholar API (free) as backup
- [ ] Contradiction detection (edge supported vs refuted)
- [ ] Citation graph (paper A cites paper B)
- [ ] Auto-update KB weekly (supervised, human approve)

## Experiment design
- [ ] CRISPR guide design (CRISPOR)
- [ ] siRNA/shRNA suggestions
- [ ] Recombinant protein / neutralizing antibody lookup (UniProt + literature)
- [ ] Co-culture protocol templates from protocols.io
- [ ] Power analysis stub for validation experiments
- [ ] Cost estimate table (reagents, rough)

## Visualization
- [ ] Sankey: cell → ligand → receptor → cell
- [ ] Split UMAP disease vs control
- [ ] Dotplot: LR genes per cell type
- [ ] Violin: ligand expression sender cells
- [ ] Cascade Sankey through pathways
- [ ] Epigenome track viewer (IGV.js) when BED available
- [ ] Printable multi-page PDF report

## Platform
- [ ] Multi-user workspaces
- [ ] Shared projects within lab
- [ ] API keys for programmatic submit
- [ ] Webhook on job complete
- [ ] Export to GEO-style supplementary tables
- [ ] Import from CellxGene Census

---

# PART 10 — REPOSITORY STRUCTURE (TARGET)

```
cell-communication-explorer/
├── apps/
│   ├── web/                 # Next.js (DTube-style UI)
│   └── desktop/             # Tauri
├── services/
│   ├── api/                 # FastAPI gateway
│   └── supervisor/          # Agent 0 orchestrator
├── agents/
│   ├── data_prep/
│   ├── core_analysis/
│   ├── cell_comm/
│   ├── literature/
│   ├── epigenome/
│   ├── pathway_cascade/
│   ├── validation/
│   ├── knowledge/
│   ├── report/
│   └── health/
├── pipeline/                # Shared scientific libs
├── reference/               # Versioned DB manifests
├── benchmarks/              # PBMC, Kang, etc.
├── knowledge/
│   ├── migrations/          # pgvector schema
│   └── seed/
├── docs/
│   ├── VALIDATION.md
│   ├── METHODS.md
│   └── CURSOR_MASTER_BUILD_PROMPT.md  # this file
├── deploy/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── fly.toml
│   └── tauri/
├── .github/workflows/
│   ├── ci.yml
│   └── nightly-benchmark.yml
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

---

# PART 11 — CURSOR SESSION STARTER PROMPTS

Copy-paste one of these to begin a build session.

## Session: Fix foundation (do this first)
```
Read CURSOR_MASTER_BUILD_PROMPT.md Parts 1-3 and Phase 0.

Current repo has a toy MVP with demo mode and fake LR scoring. Your job:
1. Remove demo mode from production code paths.
2. Integrate real NicheNet (R) with official human priors in reference/nichenet/.
3. Add provenance.json and methods.txt to every job output.
4. Add VALIDATION.md with PBMC3k benchmark instructions.
5. Do not add new UI features until NicheNet runs end-to-end on a real h5ad.

Match existing FastAPI + pipeline structure. Free software only.
```

## Session: DTube UI shell
```
Read CURSOR_MASTER_BUILD_PROMPT.md Part 7.

Build Next.js app shell matching DTube project aesthetic:
- Left sidebar: Overview, Cells, Communication, Literature, Chat, Report
- Deep navy + coral accent theme
- Project list page + project detail with tabs
- Connect to existing FastAPI job API
- No chat backend yet — placeholder tab
```

## Session: Literature agent
```
Read CURSOR_MASTER_BUILD_PROMPT.md Agent C and Phase 2.

Implement parallel literature mining:
- Supervisor fans out one worker per top-20 LR edge
- Entrez esearch + efetch, 1 req/sec
- Store pmid, title, abstract in Postgres linked to edge_id
- Add Literature tab showing papers per edge
- No LLM yet
```

## Session: Supervisor + checkpoints
```
Read CURSOR_MASTER_BUILD_PROMPT.md Part 4.

Refactor pipeline into agents A, B, D, I with Supervisor (Agent 0):
- DAG execution with retry and idempotency
- Checkpoint matrix from Part 4.3
- Job state in Postgres
- HealthMonitor heartbeat every 30s
- Prometheus /metrics endpoint
```

---

# PART 12 — EXAMPLE END-TO-END USER STORY

**Dr. Patel** studies cardiac tissue in T2D.

1. Uploads `heart_t2d_scRNA.h5ad` + `metadata.csv` (columns: barcode, condition, patient_id, batch).
2. Sets comparison: `fibroblast: T2D vs control`, `macrophage: T2D vs control`.
3. Clicks **Run Analysis**. Supervisor spawns agents.
4. 18 minutes later:
   - **Cells tab:** 8 cell types, fibroblasts show 847 DE genes vs control.
   - **Communication tab:** Top edge: Macrophage→Fibroblast via TNF–TNFRSF1A (NicheNet score 0.89).
   - **Literature tab:** 6 papers link TNF from cardiac macrophages to fibroblast activation in diabetes.
   - **Cascade tab:** TNF→TNFR1→NF-κB→IL6, COL1A1 upregulation hypothesis.
   - **Experiments tab:** Suggests macrophage depletion + TNF neutralization in ex vivo heart slices [HYPOTHESIS].
   - **Report:** Downloads PDF with methods paragraph citing Wolf 2018, Browaeys 2020, etc.
5. **Chat:** Asks "Could B cells be driving the fibroblast shift instead?" — Chat agent compares B cell LR scores, cites 2 PMIDs, answers "B cell edges rank 12th; macrophage TNF pathway has stronger evidence [PMID: ...]."

---

# PART 13 — WHAT NOT TO BUILD

- ❌ Synthetic demo data in production
- ❌ Uncited LLM biological claims
- ❌ "AI says this causes disease" without HYPOTHESIS label
- ❌ Paywalled databases without user API key
- ❌ Multi-agent orchestration before single pipeline validates on benchmarks
- ❌ Epigenome claims without ATAC/methylation data or explicit IMPUTED label
- ❌ Protein structure trivia unrelated to phenotype

---

# PART 14 — SUCCESS CRITERIA

| Milestone | Metric |
|-----------|--------|
| Phase 0 | 2 benchmarks pass; methods.txt validates |
| Phase 1 | Real upload → report <30 min; no demo code path |
| Phase 2 | Top-10 edges have literature attached |
| Phase 3 | Cascade + experiment table for top-5 edges |
| Phase 4 | Chat answers with 100% citation coverage |
| Phase 5 | Web deploy + Mac DMG install on clean macOS VM |
| Research impact | Grad student generates testable hypothesis without manual PubMed search for LR pairs |

---

**END OF MASTER BUILD PROMPT**

*Version: 1.0 | Project: Cell Communication Explorer | License: MIT*
