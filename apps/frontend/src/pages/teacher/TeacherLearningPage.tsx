import { useMemo, useState, type FormEvent } from "react";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { InlineError } from "../../components/ui/InlineError";
import { Input } from "../../components/ui/Input";
import { PageHeader } from "../../components/ui/PageHeader";
import { SectionLoader } from "../../components/ui/SectionLoader";
import { useToast } from "../../components/ui/useToast";
import {
  useAddLearningContentVersion,
  useArchiveLearningResource,
  useCreateLearningResource,
  usePublishLearningResource,
  useTeacherResources,
  useTeacherSections,
  useUploadLearningFile
} from "../../features/teacher/hooks";

type ResourceType = "NOTE" | "LINK" | "VIDEO" | "FILE";

export function TeacherLearningPage() {
  const toast = useToast();
  const sections = useTeacherSections();
  const resources = useTeacherResources();
  const createResource = useCreateLearningResource();
  const addVersion = useAddLearningContentVersion();
  const uploadFile = useUploadLearningFile();
  const publish = usePublishLearningResource();
  const archive = useArchiveLearningResource();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [resourceType, setResourceType] = useState<ResourceType>("NOTE");
  const [sectionId, setSectionId] = useState("");
  const [tags, setTags] = useState("");
  const [selectedResourceId, setSelectedResourceId] = useState("");
  const [textContent, setTextContent] = useState("");
  const [externalUrl, setExternalUrl] = useState("");
  const [changeNote, setChangeNote] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const selectedResource = useMemo(
    () => resources.data?.find((item) => item.id === selectedResourceId),
    [resources.data, selectedResourceId]
  );

  const create = async (event: FormEvent) => {
    event.preventDefault();
    if (!title.trim() || !sectionId) {
      toast.push("Provide a title and target section.", "error");
      return;
    }

    try {
      const created = await createResource.mutateAsync({
        title: title.trim(),
        description: description.trim() || undefined,
        resource_type: resourceType,
        tags: tags
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
        targets: [{ target_type: "SECTION", target_id: sectionId }]
      });
      setSelectedResourceId(created.id);
      setTitle("");
      setDescription("");
      setTags("");
      toast.push("Draft learning resource created.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not create resource.",
        "error"
      );
    }
  };

  const createVersion = async () => {
    if (!selectedResource) return;

    try {
      if (selectedResource.resourceType === "FILE") {
        if (!file) {
          toast.push("Choose a file to upload.", "error");
          return;
        }
        await uploadFile.mutateAsync({
          resourceId: selectedResource.id,
          file,
          changeNote: changeNote || undefined
        });
        setFile(null);
      } else {
        await addVersion.mutateAsync({
          resourceId: selectedResource.id,
          input: {
            text_content:
              selectedResource.resourceType === "NOTE" ? textContent : undefined,
            external_url:
              ["LINK", "VIDEO"].includes(selectedResource.resourceType)
                ? externalUrl
                : undefined,
            change_note: changeNote || undefined
          }
        });
      }

      setTextContent("");
      setExternalUrl("");
      setChangeNote("");
      toast.push("Resource version added.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not add resource version.",
        "error"
      );
    }
  };

  const publishResource = async (resourceId: string) => {
    try {
      await publish.mutateAsync(resourceId);
      toast.push("Resource published to its academic target.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not publish resource.",
        "error"
      );
    }
  };

  const archiveResource = async (resourceId: string) => {
    try {
      await archive.mutateAsync(resourceId);
      toast.push("Resource archived.", "success");
    } catch (error) {
      toast.push(
        error instanceof Error ? error.message : "Could not archive resource.",
        "error"
      );
    }
  };

  if (sections.isLoading || resources.isLoading) {
    return (
      <div className="page-container">
        <SectionLoader label="Loading learning resource workspace…" />
      </div>
    );
  }

  if (sections.error || resources.error) {
    return (
      <div className="page-container">
        <PageHeader eyebrow="Teacher" title="Learning resources" />
        <InlineError message="The learning resource workspace could not be loaded." />
      </div>
    );
  }

  return (
    <div className="page-container">
      <PageHeader
        eyebrow="Teacher"
        title="Learning resources"
        description="Create section-targeted learning material, add immutable content versions, publish, and archive resources."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card title="Create resource">
          <form className="space-y-4" onSubmit={(event) => void create(event)}>
            <Input
              label="Title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
            />

            <label className="block text-sm font-medium">
              Description
              <textarea
                className="mt-2 min-h-24 w-full rounded-xl border border-line px-3 py-2"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
              />
            </label>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block text-sm font-medium">
                Resource type
                <select
                  className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                  value={resourceType}
                  onChange={(event) =>
                    setResourceType(event.target.value as ResourceType)
                  }
                >
                  <option value="NOTE">Note</option>
                  <option value="LINK">Link</option>
                  <option value="VIDEO">Video</option>
                  <option value="FILE">File</option>
                </select>
              </label>

              <label className="block text-sm font-medium">
                Target section
                <select
                  className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
                  value={sectionId}
                  onChange={(event) => setSectionId(event.target.value)}
                >
                  <option value="">Select section</option>
                  {(sections.data ?? []).map((section) => (
                    <option key={section.id} value={section.id}>
                      {section.courseCode ? `${section.courseCode} · ` : ""}
                      {section.name}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <Input
              label="Tags"
              hint="Comma separated, e.g. lecture-3, recursion, revision"
              value={tags}
              onChange={(event) => setTags(event.target.value)}
            />

            <Button type="submit" disabled={createResource.isPending}>
              {createResource.isPending ? "Creating…" : "Create draft"}
            </Button>
          </form>
        </Card>

        <Card title="Add content version">
          <label className="block text-sm font-medium">
            Resource
            <select
              className="mt-2 w-full rounded-xl border border-line bg-panel px-3 py-2.5"
              value={selectedResourceId}
              onChange={(event) => setSelectedResourceId(event.target.value)}
            >
              <option value="">Select your resource</option>
              {(resources.data ?? [])
                .filter((resource) => resource.status !== "ARCHIVED")
                .map((resource) => (
                  <option key={resource.id} value={resource.id}>
                    {resource.title} · {resource.resourceType} · {resource.status}
                  </option>
                ))}
            </select>
          </label>

          {selectedResource ? (
            <div className="mt-4 space-y-4">
              {selectedResource.resourceType === "NOTE" ? (
                <label className="block text-sm font-medium">
                  Note content
                  <textarea
                    className="mt-2 min-h-40 w-full rounded-xl border border-line px-3 py-2"
                    value={textContent}
                    onChange={(event) => setTextContent(event.target.value)}
                  />
                </label>
              ) : null}

              {["LINK", "VIDEO"].includes(selectedResource.resourceType) ? (
                <Input
                  label="External URL"
                  type="url"
                  value={externalUrl}
                  onChange={(event) => setExternalUrl(event.target.value)}
                />
              ) : null}

              {selectedResource.resourceType === "FILE" ? (
                <label className="block text-sm font-medium">
                  File
                  <input
                    className="mt-2 block w-full rounded-xl border border-line bg-panel px-3 py-2"
                    type="file"
                    onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                  />
                </label>
              ) : null}

              <Input
                label="Change note"
                value={changeNote}
                onChange={(event) => setChangeNote(event.target.value)}
              />

              <Button
                onClick={() => void createVersion()}
                disabled={addVersion.isPending || uploadFile.isPending}
              >
                Add version
              </Button>
            </div>
          ) : (
            <p className="mt-4 text-sm text-muted">
              Select a resource to add its first or next content version.
            </p>
          )}
        </Card>
      </div>

      <section className="mt-8">
        <h2 className="mb-4 text-xl font-bold">My resources</h2>
        {(resources.data ?? []).length ? (
          <div className="grid gap-4 lg:grid-cols-2">
            {resources.data!.map((resource) => (
              <Card key={resource.id}>
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <h3 className="text-lg font-semibold">{resource.title}</h3>
                    <p className="mt-1 text-xs text-muted">
                      {resource.resourceType} · {resource.versions.length} version
                      {resource.versions.length === 1 ? "" : "s"}
                    </p>
                  </div>
                  <Badge>{resource.status}</Badge>
                </div>

                {resource.description ? (
                  <p className="mt-3 text-sm leading-6 text-muted">
                    {resource.description}
                  </p>
                ) : null}

                <div className="mt-4 flex flex-wrap gap-2">
                  {resource.status === "DRAFT" ? (
                    <Button
                      onClick={() => void publishResource(resource.id)}
                      disabled={publish.isPending}
                    >
                      Publish
                    </Button>
                  ) : null}
                  {resource.status !== "ARCHIVED" ? (
                    <Button
                      variant="secondary"
                      onClick={() => void archiveResource(resource.id)}
                      disabled={archive.isPending}
                    >
                      Archive
                    </Button>
                  ) : null}
                  <Button
                    variant="ghost"
                    onClick={() => setSelectedResourceId(resource.id)}
                  >
                    Add version
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <Card>
            <p className="text-sm text-muted">You have not created any learning resources yet.</p>
          </Card>
        )}
      </section>
    </div>
  );
}
