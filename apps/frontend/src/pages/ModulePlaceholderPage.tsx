import { EmptyState } from "../components/ui/EmptyState";

export function ModulePlaceholderPage({ title, description }: { title: string; description: string }) {
  return (
    <div className="page-container">
      <h1 className="mb-6 text-3xl font-bold tracking-tight">{title}</h1>
      <EmptyState title={`${title} foundation ready`} description={description} />
    </div>
  );
}
