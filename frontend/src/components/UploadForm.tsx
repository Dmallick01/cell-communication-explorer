"use client";

import { useState } from "react";
import {
  Alert,
  Box,
  Button,
  LinearProgress,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";
import { createJob } from "@/lib/api";

interface UploadFormProps {
  onJobCreated: (jobId: string) => void;
}

export default function UploadForm({ onJobCreated }: UploadFormProps) {
  const [dataFile, setDataFile] = useState<File | null>(null);
  const [metaFile, setMetaFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!dataFile) {
      setError("Please select a data file (.h5ad, .mtx, or expression matrix)");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const { job_id } = await createJob(dataFile, metaFile);
      onJobCreated(job_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Paper sx={{ p: 4 }}>
      <Typography variant="h5" gutterBottom>
        Upload scRNA-seq Data
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Supported formats: .h5ad, 10x MTX, CSV/TSV expression matrix. Optional
        metadata CSV with cell barcodes as row index.
      </Typography>

      <Box component="form" onSubmit={handleSubmit}>
        <Stack spacing={2}>
          <Button variant="outlined" component="label" startIcon={<CloudUploadIcon />}>
            {dataFile ? dataFile.name : "Select expression data"}
            <input
              type="file"
              hidden
              accept=".h5ad,.mtx,.csv,.tsv,.txt,.gz"
              onChange={(e) => setDataFile(e.target.files?.[0] ?? null)}
            />
          </Button>

          <Button variant="outlined" component="label" color="secondary">
            {metaFile ? metaFile.name : "Select metadata (optional)"}
            <input
              type="file"
              hidden
              accept=".csv,.tsv,.txt"
              onChange={(e) => setMetaFile(e.target.files?.[0] ?? null)}
            />
          </Button>

          {error && <Alert severity="error">{error}</Alert>}
          {loading && <LinearProgress />}

          <Button
            type="submit"
            variant="contained"
            size="large"
            disabled={loading || !dataFile}
          >
            Run Analysis Pipeline
          </Button>

          <Button
            variant="text"
            disabled={loading}
            onClick={async () => {
              const blob = new Blob(["demo"], { type: "text/plain" });
              const file = new File([blob], "demo.h5ad", { type: "application/octet-stream" });
              setDataFile(file);
              setLoading(true);
              setError(null);
              try {
                const { job_id } = await createJob(file, null, true);
                onJobCreated(job_id);
              } catch (err) {
                setError(err instanceof Error ? err.message : "Demo failed");
              } finally {
                setLoading(false);
              }
            }}
          >
            Run demo with synthetic data
          </Button>
        </Stack>
      </Box>
    </Paper>
  );
}
