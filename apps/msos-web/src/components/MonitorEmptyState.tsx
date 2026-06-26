import Link from "next/link";

export function MonitorEmptyState() {
  return (
    <div className="monitor-empty-state" role="status">
      <strong>No paper trades yet</strong>
      <p>
        Save a sketch in Strategy Lab after you confirm your view — we&apos;ll show live BTC versus
        your saved prices here. No broker connection required.
      </p>
      <Link href="/strategy-lab" className="btn slim primary">
        Open Strategy Lab
      </Link>
    </div>
  );
}
