import ProjectWorkspace from "@/components/ProjectWorkspace";

export default async function ProjectCommunicationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ProjectWorkspace jobId={id} tab="communication" />;
}
