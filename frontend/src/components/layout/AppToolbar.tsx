"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTheme } from "@/components/ThemeProvider";

export default function AppToolbar() {
  const { theme, toggle } = useTheme();
  const pathname = usePathname();
  const onProjects = pathname.startsWith("/projects");

  return (
    <nav className="dtube-toolbar" aria-label="CCE controls">
      <span className="brand">CCE</span>
      <span className="sep">|</span>
      <button type="button" onClick={toggle}>
        {theme === "dark" ? "☀ Light" : "☾ Dark"}
      </button>
      <Link href="/projects" className={pathname === "/projects" ? "active" : ""}>
        Projects
      </Link>
      <Link href="/projects/new" className={pathname === "/projects/new" ? "active" : ""}>
        New analysis
      </Link>
      {onProjects && (
        <>
          <span className="sep">|</span>
          <span style={{ color: "var(--cdisabled)" }}>Cell Communication Explorer</span>
        </>
      )}
    </nav>
  );
}
