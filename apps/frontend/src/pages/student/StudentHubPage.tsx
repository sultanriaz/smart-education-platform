import { PageHeader } from "../../components/ui/PageHeader";
import { CampusHubWayfindingEngine } from "../../components/campushub/CampusHubWayfindingEngine";

export function StudentHubPage() {
  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Campus Directory & Spatial Intelligence"
        title="Campus Hub, Directory & Spatial Wayfinding"
        description="Search faculty offices, inspect administrative queue tokens, browse equipment inventories across specialized labs, check live library seat availability, and explore interactive vector floor blueprints."
      />

      <CampusHubWayfindingEngine />
    </div>
  );
}
