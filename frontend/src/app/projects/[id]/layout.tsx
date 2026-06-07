"use client";

import AppShell from "@/components/layout/AppShell";
import { useParams } from "next/navigation";

export default function ProjectLayout({ children }: { children: React.ReactNode }) {
  const params = useParams();
  const id = typeof params.id === "string" ? params.id : "";
  return <AppShell projectId={id}>{children}</AppShell>;
}
