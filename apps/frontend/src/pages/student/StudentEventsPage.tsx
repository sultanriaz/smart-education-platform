import { PageHeader } from "../../components/ui/PageHeader";
import { MarqueeEventsPortal } from "../../components/events/MarqueeEventsPortal";

export function StudentEventsPage() {
  return (
    <div className="page-container space-y-6">
      <PageHeader
        eyebrow="Campus Life & University Calendar"
        title="Marquee Events, Sports Olympiad & Gala Portal"
        description="Live match scores, knockout elimination brackets, department points table, seasonal Hackathons, and career interview FastPasses."
      />

      <MarqueeEventsPortal initialMode="SPORTS_GALA" />
    </div>
  );
}
