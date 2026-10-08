import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import {
  useRecommendations,
  useResources
} from "../../features/student/hooks";
import { downloadLearningResource } from "../../features/student/student-api";
import { useToast } from "../../components/ui/useToast";
import { Button } from "../../components/ui/Button";
import type { LearningResource } from "../../features/student/types";

function ResourceCard({
  resource,
  recommended = false
}: {
  resource: LearningResource;
  recommended?: boolean;
}) {
  const toast = useToast();

  const download = async () => {
    try {
      await downloadLearningResource(resource.id);
    } catch (error) {
      toast.push(error instanceof Error ? error.message : "Download failed.", "error");
    }
  };

  return (
    <Card>
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-brand-700">
            {recommended ? "Recommended" : resource.resourceType ?? "Resource"}
          </p>
          <h2 className="mt-1 text-lg font-semibold">{resource.title}</h2>
        </div>
        {typeof resource.score === "number" ? (
          <span className="rounded-full bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-700">
            Score {resource.score}
          </span>
        ) : null}
      </div>

      {resource.description ? (
        <p className="mt-3 text-sm leading-6 text-muted">{resource.description}</p>
      ) : null}

      {resource.textContent ? (
        <details className="mt-5 rounded-xl border border-line p-4">
          <summary className="cursor-pointer font-semibold">Read notes</summary>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-7">{resource.textContent}</p>
        </details>
      ) : resource.externalUrl && /^https?:\/\//i.test(resource.externalUrl) ? (
        <a
          href={resource.externalUrl}
          target="_blank"
          rel="noreferrer"
          className="mt-5 inline-flex rounded-xl bg-brand-600 px-4 py-2 text-sm font-semibold text-white"
        >
          Open resource
        </a>
      ) : (
        <Button className="mt-5" onClick={() => void download()}>
          Download
        </Button>
      )}
    </Card>
  );
}

export function StudentLearningPage() {
  const resources = useResources();
  const recommendations = useRecommendations();

  if (resources.isLoading || recommendations.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading learning resources…" />
      </div>
    );
  }

  if (resources.error || recommendations.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Student" title="Learning resources" />
        <InlineError message="Learning resources could not be loaded." />
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Student"
        title="Learning resources"
        description="Explore your course materials and recommendations selected for your studies."
      />

      <section aria-labelledby="recommendations-heading">
        <h2 id="recommendations-heading" className="mb-4 text-xl font-bold">
          Recommended for you
        </h2>
        {recommendations.data?.length ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {recommendations.data.map((resource) => (
              <ResourceCard key={resource.id} resource={resource} recommended />
            ))}
          </div>
        ) : (
          <Card>
            <p className="text-sm text-muted">
              No personalized recommendations are available yet.
            </p>
          </Card>
        )}
      </section>

      <section className="mt-8" aria-labelledby="all-resources-heading">
        <h2 id="all-resources-heading" className="mb-4 text-xl font-bold">
          All available resources
        </h2>
        {resources.data?.length ? (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {resources.data.map((resource) => (
              <ResourceCard key={resource.id} resource={resource} />
            ))}
          </div>
        ) : (
          <Card>
            <p className="text-sm text-muted">No resources are published for your current sections.</p>
          </Card>
        )}
      </section>
    </div>
  );
}
