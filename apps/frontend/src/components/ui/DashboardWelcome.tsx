import { ArrowUpRight, Sparkles } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "../../features/auth/useAuth";

export function DashboardWelcome({ subtitle, action, to }: { subtitle: string; action: string; to: string }) {
  const { user } = useAuth();
  const firstName = user?.fullName?.split(" ")[0] ?? "there";
  const hour = new Date().getHours();
  return <section className="dashboard-welcome"><div><div className="welcome-eyebrow"><Sparkles size={14} /> A LITTLE FOCUS. A LOT OF POSSIBILITY.</div><h1>Good {hour < 12 ? "morning" : hour < 18 ? "afternoon" : "evening"}, {firstName}<span>.</span></h1><p>{subtitle}</p><Link className="welcome-action" to={to}>{action}<ArrowUpRight size={16} /></Link></div><div className="welcome-orbit" aria-hidden="true"><span /><span /><span /><div>e<span>EDUSPHERE</span></div></div></section>;
}
