import ProjectWorkspace from "@/components/ProjectWorkspace";

export default async function ProjectChatPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <ProjectWorkspace jobId={id} tab="chat" />;
}
