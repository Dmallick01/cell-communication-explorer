"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import AppToolbar from "@/components/layout/AppToolbar";
import { getJobResults } from "@/lib/api";

const NAV = [
  { label: "Projects", href: "/projects" },
  { label: "New analysis", href: "/projects/new" },
];

const PROJECT_TABS = [
  { label: "Overview", slug: "" },
  { label: "Cells", slug: "cells" },
  { label: "Communication", slug: "communication" },
  { label: "Literature", slug: "literature" },
  { label: "Chat", slug: "chat" },
  { label: "Report", slug: "report" },
];

export default function AppShell({
  children,
  projectId,
  queue,
}: {
  children: React.ReactNode;
  projectId?: string;
  queue?: React.ReactNode;
}) {
  const pathname = usePathname();
  const [projectTitle, setProjectTitle] = useState<string | undefined>();
  const [projectMeta, setProjectMeta] = useState<string | undefined>();

  useEffect(() => {
    if (!projectId) return;

    getJobResults(projectId)
      .then((r) => {
        setProjectTitle(r.project_name || `Analysis ${projectId.slice(0, 8)}`);
        const parts = [r.tissue, r.disease].filter(Boolean);
        setProjectMeta(parts.join(" · ") || `Job ${projectId.slice(0, 8)}…`);
      })
      .catch(() => {
        setProjectTitle(`Analysis ${projectId.slice(0, 8)}`);
        setProjectMeta(`Job ${projectId.slice(0, 8)}…`);
      });
  }, [projectId]);

  return (
    <>
      <AppToolbar />
      <div className="app-shell">
        {projectId && (
          <header className="app-header">
            <div>
              <h1>{projectTitle || "Analysis"}</h1>
              <p className="header-meta">
                {projectMeta || `Job ${projectId.slice(0, 8)}…`}
              </p>
            </div>
            <div className="header-actions">
              <Link href="/projects/new" className="btn btn-primary">
                New analysis
              </Link>
              <Link href="/projects" className="btn">
                All projects
              </Link>
            </div>
          </header>
        )}

        <div className="main-layout">
          <aside className="sidebar-panel">
            <h2 className="sidebar-title">Library</h2>
            <ul className="nav-list">
              {NAV.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className={`btn ${pathname === item.href ? "active" : ""}`}
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>

            {projectId && (
              <>
                <h2 className="sidebar-title" style={{ marginTop: 24 }}>
                  Analysis
                </h2>
                <ul className="nav-list">
                  {PROJECT_TABS.map((tab) => {
                    const href =
                      tab.slug === ""
                        ? `/projects/${projectId}`
                        : `/projects/${projectId}/${tab.slug}`;
                    return (
                      <li key={tab.slug}>
                        <Link
                          href={href}
                          className={`btn ${pathname === href ? "active" : ""}`}
                        >
                          {tab.label}
                        </Link>
                      </li>
                    );
                  })}
                </ul>
              </>
            )}
          </aside>

          <main className="content-area">{children}</main>

          {queue && <aside className="queue-panel">{queue}</aside>}
        </div>
      </div>
    </>
  );
}
