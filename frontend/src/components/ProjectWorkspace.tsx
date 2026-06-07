"use client";

import { useCallback, useEffect, useState } from "react";
import OverviewPanel from "@/components/panels/OverviewPanel";
import CellsPanel from "@/components/panels/CellsPanel";
import CommunicationPanel from "@/components/panels/CommunicationPanel";
import LiteraturePanel from "@/components/panels/LiteraturePanel";
import ChatPanel from "@/components/panels/ChatPanel";
import ReportPanel from "@/components/panels/ReportPanel";
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
    return <div className="empty-state">Loading project…</div>;
  }

  if (tab === "overview") {
    return <OverviewPanel job={jobStatus} results={results} />;
  }

  if (tab === "literature") {
    if (jobStatus.status !== "completed") {
      return <div className="alert alert-info">Analysis in progress. Literature loads when complete.</div>;
    }
    return <LiteraturePanel jobId={jobId} />;
  }

  if (tab === "chat") {
    return <ChatPanel jobId={jobId} />;
  }

  if (jobStatus.status !== "completed" || !results) {
    return (
      <div className="alert alert-info">
        Analysis in progress. Check Overview for pipeline status.
      </div>
    );
  }

  if (tab === "cells") return <CellsPanel results={results} />;
  if (tab === "communication") return <CommunicationPanel results={results} />;
  if (tab === "report") return <ReportPanel results={results} />;

  return <div className="alert alert-info">Select a tab from the sidebar.</div>;
}
