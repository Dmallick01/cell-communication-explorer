import ProjectWorkspace from "@/components/ProjectWorkspace";

export default async function ProjectOverviewPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ProjectWorkspace jobId={id} tab="overview" />;
}
