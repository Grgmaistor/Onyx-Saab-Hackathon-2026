import { cn } from "@/lib/utils";

export function Panel({
  title,
  children,
  className,
  badge,
  actions,
}: {
  title?: string;
  children: React.ReactNode;
  className?: string;
  badge?: string;
  actions?: React.ReactNode;
}) {
  return (
    <div className={cn("mil-panel", className)}>
      {title && (
        <div className="mil-panel-header">
          <span className="flex items-center gap-2">
            <span className="mil-dot mil-dot-active" />
            {title}
            {badge && <span className="mil-badge mil-badge-dim ml-2">{badge}</span>}
          </span>
          {actions && <span>{actions}</span>}
        </div>
      )}
      <div className="mil-panel-body">{children}</div>
    </div>
  );
}

export function MetricRow({ label, value, accent }: { label: string; value: React.ReactNode; accent?: boolean }) {
  return (
    <div className="mil-metric">
      <span className="mil-metric-label">{label}</span>
      <span className={cn("mil-metric-value", accent && "text-accent mil-glow")}>{value}</span>
    </div>
  );
}

export function OutcomeBadge({ outcome }: { outcome: string }) {
  const cls =
    outcome === "WIN" ? "mil-badge-win" :
    outcome === "LOSS" ? "mil-badge-loss" :
    outcome === "TIMEOUT" ? "mil-badge-timeout" :
    "mil-badge-dim";
  return <span className={`mil-badge ${cls}`}>{outcome}</span>;
}
