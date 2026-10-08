import { Card } from "./Card";

export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <Card>
      <div className="py-8 text-center">
        <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-50 font-bold text-brand-700">
          SEP
        </div>
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-muted">{description}</p>
      </div>
    </Card>
  );
}
