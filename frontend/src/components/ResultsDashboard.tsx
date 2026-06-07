"use client";

import {
  Box,
  Button,
  Grid,
  Paper,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import DownloadIcon from "@mui/icons-material/Download";
import { resolveArtifactUrl, type JobResultsResponse } from "@/lib/api";

function PlotCard({ title, src }: { title: string; src?: string }) {
  if (!src) return null;
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <Box
        component="img"
        src={src}
        alt={title}
        sx={{ width: "100%", borderRadius: 1, border: "1px solid #eee" }}
      />
    </Paper>
  );
}

export default function ResultsDashboard({
  results,
}: {
  results: JobResultsResponse;
}) {
  const edges = results.communication_edges ?? [];
  const cellTypes = results.cell_types ?? [];
  const exports = results.exports ?? {};

  return (
    <Box sx={{ mt: 3 }}>
      <Stack direction="row" spacing={1} sx={{ mb: 3, flexWrap: "wrap", gap: 1 }}>
        {exports.report_html && (
          <Button
            variant="outlined"
            size="small"
            startIcon={<DownloadIcon />}
            href={resolveArtifactUrl(exports.report_html)!}
            target="_blank"
          >
            HTML Report
          </Button>
        )}
        {exports.report_pdf && (
          <Button
            variant="outlined"
            size="small"
            startIcon={<DownloadIcon />}
            href={resolveArtifactUrl(exports.report_pdf)!}
            target="_blank"
          >
            PDF Report
          </Button>
        )}
        {exports.communication_edges && (
          <Button
            variant="outlined"
            size="small"
            startIcon={<DownloadIcon />}
            href={resolveArtifactUrl(exports.communication_edges)!}
            target="_blank"
          >
            Interactions CSV
          </Button>
        )}
        {exports.cell_types && (
          <Button
            variant="outlined"
            size="small"
            startIcon={<DownloadIcon />}
            href={resolveArtifactUrl(exports.cell_types)!}
            target="_blank"
          >
            Cell Types CSV
          </Button>
        )}
      </Stack>

      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 4 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              QC Summary
            </Typography>
            <Typography variant="body2">
              Cells remaining:{" "}
              <strong>{String(results.qc_report?.cells_remaining ?? "—")}</strong>
            </Typography>
            <Typography variant="body2">
              Median mito %:{" "}
              <strong>{String(results.qc_report?.pct_mito_median ?? "—")}</strong>
            </Typography>
            <Typography variant="body2">
              Clusters:{" "}
              <strong>{String(results.cluster_summary?.n_clusters ?? "—")}</strong>
            </Typography>
            <Typography variant="body2">
              Silhouette:{" "}
              <strong>{String(results.cluster_summary?.silhouette_score ?? "—")}</strong>
            </Typography>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 8 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Cell Types
            </Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Cell Type</TableCell>
                  <TableCell align="right">Count</TableCell>
                  <TableCell align="right">Fraction</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {cellTypes.map((ct) => (
                  <TableRow key={ct.cell_type}>
                    <TableCell>{ct.cell_type}</TableCell>
                    <TableCell align="right">{ct.count}</TableCell>
                    <TableCell align="right">{(ct.fraction * 100).toFixed(1)}%</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>

        <Grid size={{ xs: 12, md: 4 }}>
          <PlotCard title="UMAP Clusters" src={resolveArtifactUrl(results.umap_plot)} />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <PlotCard title="Communication Network" src={resolveArtifactUrl(results.network_plot)} />
        </Grid>
        <Grid size={{ xs: 12, md: 4 }}>
          <PlotCard title="Ligand-Receptor Heatmap" src={resolveArtifactUrl(results.heatmap_plot)} />
        </Grid>

        <Grid size={{ xs: 12 }}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Top Ligand-Receptor Interactions
            </Typography>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Source</TableCell>
                  <TableCell>Target</TableCell>
                  <TableCell>Ligand</TableCell>
                  <TableCell>Receptor</TableCell>
                  <TableCell align="right">Score</TableCell>
                  <TableCell align="right">p-value</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {edges.slice(0, 15).map((e, i) => (
                  <TableRow key={`${e.ligand}-${e.receptor}-${i}`}>
                    <TableCell>{e.source_cell_type}</TableCell>
                    <TableCell>{e.target_cell_type}</TableCell>
                    <TableCell>{e.ligand}</TableCell>
                    <TableCell>{e.receptor}</TableCell>
                    <TableCell align="right">{e.score}</TableCell>
                    <TableCell align="right">{e.p_value}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
