"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Box,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Toolbar,
  Typography,
  AppBar,
} from "@mui/material";
import ScienceIcon from "@mui/icons-material/Science";
import FolderIcon from "@mui/icons-material/Folder";
import AddIcon from "@mui/icons-material/Add";
import DashboardIcon from "@mui/icons-material/Dashboard";
import ShareIcon from "@mui/icons-material/Share";
import AutoStoriesIcon from "@mui/icons-material/AutoStories";
import ForumIcon from "@mui/icons-material/Forum";
import ArticleIcon from "@mui/icons-material/Article";

const DRAWER_WIDTH = 240;

const NAV = [
  { label: "Projects", href: "/projects", icon: <FolderIcon /> },
  { label: "New analysis", href: "/projects/new", icon: <AddIcon /> },
];

const PROJECT_TABS = [
  { label: "Overview", slug: "", icon: <DashboardIcon /> },
  { label: "Cells", slug: "cells", icon: <ScienceIcon /> },
  { label: "Communication", slug: "communication", icon: <ShareIcon /> },
  { label: "Literature", slug: "literature", icon: <AutoStoriesIcon /> },
  { label: "Chat", slug: "chat", icon: <ForumIcon /> },
  { label: "Report", slug: "report", icon: <ArticleIcon /> },
];

export default function AppShell({
  children,
  projectId,
}: {
  children: React.ReactNode;
  projectId?: string;
}) {
  const pathname = usePathname();

  return (
    <Box sx={{ display: "flex", minHeight: "100vh", bgcolor: "background.default" }}>
      <AppBar
        position="fixed"
        sx={{ zIndex: (t) => t.zIndex.drawer + 1, bgcolor: "primary.main" }}
      >
        <Toolbar>
          <ScienceIcon sx={{ mr: 1.5 }} />
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700 }}>
            Cell Communication Explorer
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.85 }}>
            Research platform
          </Typography>
        </Toolbar>
      </AppBar>

      <Drawer
        variant="permanent"
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          [`& .MuiDrawer-paper`]: {
            width: DRAWER_WIDTH,
            boxSizing: "border-box",
            borderRight: "1px solid",
            borderColor: "divider",
            bgcolor: "background.paper",
          },
        }}
      >
        <Toolbar />
        <List sx={{ px: 1 }}>
          {NAV.map((item) => (
            <ListItemButton
              key={item.href}
              component={Link}
              href={item.href}
              selected={pathname === item.href}
              sx={{ borderRadius: 2, mb: 0.5 }}
            >
              <ListItemIcon sx={{ minWidth: 36 }}>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          ))}
        </List>

        {projectId && (
          <>
            <Typography
              variant="overline"
              sx={{ px: 2, pt: 2, pb: 1, color: "text.secondary", display: "block" }}
            >
              Analysis
            </Typography>
            <List sx={{ px: 1 }}>
              {PROJECT_TABS.map((tab) => {
                const href =
                  tab.slug === ""
                    ? `/projects/${projectId}`
                    : `/projects/${projectId}/${tab.slug}`;
                return (
                  <ListItemButton
                    key={tab.slug}
                    component={Link}
                    href={href}
                    selected={pathname === href}
                    sx={{ borderRadius: 2, mb: 0.5 }}
                  >
                    <ListItemIcon sx={{ minWidth: 36 }}>{tab.icon}</ListItemIcon>
                    <ListItemText primary={tab.label} />
                  </ListItemButton>
                );
              })}
            </List>
          </>
        )}
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8, maxWidth: "100%" }}>
        {children}
      </Box>
    </Box>
  );
}
