import ProjectWorkspace from "@/components/ProjectWorkspace";

export default async function ProjectCellsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ProjectWorkspace jobId={id} tab="cells" />;
}
