"use client";

import { usePathname } from "next/navigation";
import AppShell from "@/components/layout/AppShell";
import ProjectQueue from "@/components/ProjectQueue";

export default function ProjectsLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const match = pathname.match(/^\/projects\/([^/]+)/);
  const segment = match?.[1];
  const projectId = segment && segment !== "new" ? segment : undefined;

  return (
    <AppShell
      projectId={projectId}
      queue={projectId ? <ProjectQueue activeId={projectId} /> : undefined}
    >
      {children}
    </AppShell>
  );
}
