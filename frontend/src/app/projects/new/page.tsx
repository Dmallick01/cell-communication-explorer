"use client";

import { useRouter } from "next/navigation";
import UploadForm from "@/components/UploadForm";

export default function NewProjectPage() {
  const router = useRouter();

  return (
    <div>
      <div className="group-header">
        <span>New analysis</span>
      </div>
      <p style={{ color: "var(--cdisabled)", fontSize: 12, marginBottom: 24, maxWidth: "52ch" }}>
        Upload .h5ad, 10x Genomics (.zip), or expression matrix with optional metadata.
        Communication analysis requires NicheNet priors — see docs/VALIDATION.md.
      </p>
      <UploadForm onJobCreated={(id) => router.push(`/projects/${id}`)} />
    </div>
  );
}
