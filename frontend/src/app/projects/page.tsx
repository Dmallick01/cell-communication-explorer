"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Box,
  Button,
  Chip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  Typography,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";
import { listJobs, type JobListItem } from "@/lib/api";

export default function ProjectsPage() {
  const [jobs, setJobs] = useState<JobListItem[]>([]);

  useEffect(() => {
    listJobs().then(setJobs).catch(() => setJobs([]));
  }, []);

  return (
    <Box>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700 }} gutterBottom>
            Analysis projects
          </Typography>
          <Typography color="text.secondary" sx={{ maxWidth: 560 }}>
            Upload scRNA-seq data to discover cell-to-cell signaling hypotheses grounded in
            NicheNet priors and citable methods.
          </Typography>
        </Box>
        <Button
          component={Link}
          href="/projects/new"
          variant="contained"
          startIcon={<AddIcon />}
          sx={{ alignSelf: "flex-start" }}
        >
          New analysis
        </Button>
      </Box>

      <Paper>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Project ID</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Created</TableCell>
              <TableCell align="right">Open</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {jobs.length === 0 && (
              <TableRow>
                <TableCell colSpan={4}>
                  <Typography color="text.secondary" sx={{ py: 2 }}>
                    No analyses yet. Start with a new upload or a benchmark dataset.
                  </Typography>
                </TableCell>
              </TableRow>
            )}
            {jobs.map((j) => (
              <TableRow key={j.job_id} hover>
                <TableCell sx={{ fontFamily: "monospace", fontSize: 13 }}>
                  {j.job_id.slice(0, 8)}…
                </TableCell>
                <TableCell>
                  <Chip
                    size="small"
                    label={j.status}
                    color={
                      j.status === "completed"
                        ? "success"
                        : j.status === "failed"
                          ? "error"
                          : "primary"
                    }
                  />
                </TableCell>
                <TableCell>{j.created_at ? new Date(j.created_at).toLocaleString() : "—"}</TableCell>
                <TableCell align="right">
                  <Button component={Link} href={`/projects/${j.job_id}`} size="small">
                    View
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>
    </Box>
  );
}
