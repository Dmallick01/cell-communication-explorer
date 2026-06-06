"use client";

import {
  Box,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
  Typography,
} from "@mui/material";
import CheckCircleIcon from "@mui/icons-material/CheckCircle";
import ErrorIcon from "@mui/icons-material/Error";
import HourglassEmptyIcon from "@mui/icons-material/HourglassEmpty";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import type { JobStatusResponse } from "@/lib/api";

const STEP_LABELS: Record<string, string> = {
  upload: "Data validation",
  qc: "Quality control",
  batch_correction: "Batch correction (Harmony)",
  clustering: "Clustering & UMAP",
  annotation: "Cell-type annotation",
  communication: "Cell-cell communication",
  export: "Report export",
};

function statusIcon(status: string) {
  switch (status) {
    case "completed":
      return <CheckCircleIcon color="success" />;
    case "running":
      return <PlayCircleIcon color="primary" />;
    case "failed":
      return <ErrorIcon color="error" />;
    default:
      return <HourglassEmptyIcon color="disabled" />;
  }
}

export default function PipelineProgress({ job }: { job: JobStatusResponse }) {
  const completed = job.steps.filter((s) => s.status === "completed").length;
  const progress = (completed / job.steps.length) * 100;

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
        <Typography variant="h6">Pipeline Progress</Typography>
        <Chip
          label={job.status}
          color={
            job.status === "completed"
              ? "success"
              : job.status === "failed"
                ? "error"
                : "primary"
          }
        />
      </Box>

      <LinearProgress variant="determinate" value={progress} sx={{ mb: 2, height: 8, borderRadius: 4 }} />

      <List dense>
        {job.steps.map((step) => (
          <ListItem key={step.step}>
            <ListItemIcon>{statusIcon(step.status)}</ListItemIcon>
            <ListItemText
              primary={STEP_LABELS[step.step] ?? step.step}
              secondary={step.message ?? step.status}
            />
            {step.checkpoint_passed === false && (
              <Chip label="checkpoint failed" size="small" color="warning" />
            )}
          </ListItem>
        ))}
      </List>

      {job.error && (
        <Typography color="error" sx={{ mt: 2 }}>
          {job.error}
        </Typography>
      )}
    </Paper>
  );
}
