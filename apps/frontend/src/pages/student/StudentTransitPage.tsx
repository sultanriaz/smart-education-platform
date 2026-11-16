import { PageHeader } from "../../components/ui/PageHeader";
import { SmartTransitFleetTelemetry } from "../../components/transit/SmartTransitFleetTelemetry";

export function StudentTransitPage() {
  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Campus Logistics & Fleet Operations"
        title="Smart Transit & Fleet Telemetry"
        description="Monitor real-time city commuter buses, stop-by-stop arrival ETAs across Sahiwal, high-frequency intra-day campus shuttles, and instant disruption bulletins."
      />

      <SmartTransitFleetTelemetry initialCategory="CITY_ROUTE" />
    </div>
  );
}
