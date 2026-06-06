"use client";

import {
  Box,
  Grid,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import type { JobResultsResponse } from "@/lib/api";

export default function ResultsDashboard({
  results,
}: {
  results: JobResultsResponse;
}) {
  const edges = results.communication_edges ?? [];
  const cellTypes = results.cell_types ?? [];

  return (
    <Box sx={{ mt: 3 }}>
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
