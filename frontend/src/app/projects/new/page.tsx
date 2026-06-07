"use client";

import { useRouter } from "next/navigation";
import { Typography } from "@mui/material";
import UploadForm from "@/components/UploadForm";

export default function NewProjectPage() {
  const router = useRouter();

  return (
    <>
      <Typography variant="h4" sx={{ fontWeight: 700 }} gutterBottom>
        New analysis
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3, maxWidth: 640 }}>
        Upload .h5ad, 10x Genomics (.zip), or expression matrix with optional metadata.
        Communication analysis requires NicheNet priors — see docs/VALIDATION.md.
      </Typography>
      <UploadForm onJobCreated={(id) => router.push(`/projects/${id}`)} />
    </>
  );
}
