"use client";

import { useCallback, useEffect, useState } from "react";
import { Alert, Box, Typography } from "@mui/material";
import PipelineProgress from "@/components/PipelineProgress";
import ResultsDashboard from "@/components/ResultsDashboard";
import {
  getJobResults,
  getJobStatus,
  type JobResultsResponse,
  type JobStatusResponse,
} from "@/lib/api";

export function useProjectJob(jobId: string) {
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const [results, setResults] = useState<JobResultsResponse | null>(null);

  const pollJob = useCallback(async (id: string) => {
    const status = await getJobStatus(id);
    setJobStatus(status);
    if (status.status === "completed") {
      setResults(await getJobResults(id));
      return true;
    }
    if (status.status === "failed") return true;
    return false;
  }, []);

  useEffect(() => {
    let active = true;
    const run = async () => {
      const done = await pollJob(jobId);
      if (!done && active) {
        const t = setInterval(async () => {
          if (!active) return;
          if (await pollJob(jobId)) clearInterval(t);
        }, 2000);
        return () => clearInterval(t);
      }
    };
    const cleanup = run();
    return () => {
      active = false;
      cleanup.then((fn) => fn?.());
    };
  }, [jobId, pollJob]);

  return { jobStatus, results };
}

export default function ProjectWorkspace({
  jobId,
  tab,
}: {
  jobId: string;
  tab: "overview" | "cells" | "communication" | "literature" | "chat" | "report";
}) {
  const { jobStatus, results } = useProjectJob(jobId);

  if (!jobStatus) {
    return <Typography>Loading project…</Typography>;
  }

  if (tab === "overview") {
    return (
      <Box>
        <Typography variant="h5" gutterBottom>
          Overview
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Job {jobId}
        </Typography>
        <PipelineProgress job={jobStatus} />
        {jobStatus.error && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {jobStatus.error}
          </Alert>
        )}
        {results?.status === "completed" && (
          <Box sx={{ mt: 3 }}>
            <ResultsDashboard results={results} />
          </Box>
        )}
      </Box>
    );
  }

  if (tab === "cells" && results) {
    return (
      <Box>
        <Typography variant="h5" gutterBottom>
          Cell Types
        </Typography>
        <ResultsDashboard results={results} />
      </Box>
    );
  }

  if (tab === "communication" && results) {
    return (
      <Box>
        <Typography variant="h5" gutterBottom>
          Cell–Cell Communication (NicheNet)
        </Typography>
        <ResultsDashboard results={results} />
      </Box>
    );
  }

  if (tab === "report" && results?.exports) {
    const e = results.exports;
    return (
      <Box>
        <Typography variant="h5" gutterBottom>
          Report & Provenance
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Publication-ready exports with methods paragraph and provenance JSON.
        </Typography>
        <ResultsDashboard results={results} />
      </Box>
    );
  }

  if (tab === "literature") {
    return (
      <Alert severity="info">
        Literature evidence panel — Phase 2. PubMed/Europe PMC links per ligand–receptor edge
        (no AI summarization until Phase 3).
      </Alert>
    );
  }

  if (tab === "chat") {
    return (
      <Alert severity="info">
        Research chat — Phase 4. RAG over your analysis results and cited literature.
      </Alert>
    );
  }

  if (jobStatus.status !== "completed") {
    return <Alert severity="info">Analysis in progress. Check Overview for status.</Alert>;
  }

  return <Alert severity="warning">Results not available.</Alert>;
}
