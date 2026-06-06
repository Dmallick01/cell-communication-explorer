"use client";

import { useCallback, useEffect, useState } from "react";
import { AppBar, Box, Container, Toolbar, Typography } from "@mui/material";
import UploadForm from "@/components/UploadForm";
import PipelineProgress from "@/components/PipelineProgress";
import ResultsDashboard from "@/components/ResultsDashboard";
import {
  getJobResults,
  getJobStatus,
  type JobResultsResponse,
  type JobStatusResponse,
} from "@/lib/api";

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const [results, setResults] = useState<JobResultsResponse | null>(null);

  const pollJob = useCallback(async (id: string) => {
    const status = await getJobStatus(id);
    setJobStatus(status);

    if (status.status === "completed") {
      const res = await getJobResults(id);
      setResults(res);
      return true;
    }
    if (status.status === "failed") {
      return true;
    }
    return false;
  }, []);

  useEffect(() => {
    if (!jobId) return;

    let active = true;
    const interval = setInterval(async () => {
      if (!active) return;
      const done = await pollJob(jobId);
      if (done) clearInterval(interval);
    }, 2000);

    pollJob(jobId);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, [jobId, pollJob]);

  return (
    <>
      <AppBar position="static" elevation={0}>
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Cell Communication Explorer
          </Typography>
          <Typography variant="body2" sx={{ opacity: 0.8 }}>
            MVP v1.0
          </Typography>
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          From scRNA-seq to cell-cell signaling hypotheses
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 4, maxWidth: 720 }}>
          Upload single-cell RNA sequencing data to run QC, Harmony batch
          correction, Leiden clustering, CellTypist annotation, and ligand-receptor
          network inference — all in one reproducible pipeline.
        </Typography>

        {!jobId && <UploadForm onJobCreated={setJobId} />}

        {jobId && jobStatus && (
          <>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
              Job ID: {jobId}
            </Typography>
            <PipelineProgress job={jobStatus} />
          </>
        )}

        {results && results.status === "completed" && (
          <ResultsDashboard results={results} />
        )}
      </Container>

      <Box component="footer" sx={{ py: 3, textAlign: "center", color: "text.secondary" }}>
        <Typography variant="caption">
          Scientific pipeline: Scanpy · Harmony · CellTypist · NicheNet-style LR scoring
        </Typography>
      </Box>
    </>
  );
}
