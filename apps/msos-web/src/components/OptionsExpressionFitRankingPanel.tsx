import type { ExpressionFitRankingPayload } from "@/lib/optionsExpressionFitRanking";

type Props = {
  ranking: ExpressionFitRankingPayload | null;
};

export function OptionsExpressionFitRankingPanel({ ranking }: Props) {
  if (!ranking?.top_fit) {
    return null;
  }

  return (
    <div className="planner-advanced" aria-label="Educational expression fit ranking">
      <div className="panel-head">
        <div>
          <h2>Educational fit ranking</h2>
          <div className="panel-sub">Deterministic score from your view, horizon, max loss, and payoff preference.</div>
        </div>
      </div>
      {ranking.ranked.slice(0, 3).map((row) => (
        <div key={row.candidate_id} className={`option-row${row.rank === 1 ? "" : " dimmed"}`}>
          <div>
            <h3>
              {row.rank}. {row.label}
            </h3>
            <p>{row.rank === 1 ? row.why : row.why_lower[0] ?? row.why}</p>
          </div>
          <span className={`tag${row.rank === 1 ? " amber" : ""}`}>{row.score.toFixed(0)}</span>
        </div>
      ))}
      <p className="micro">{ranking.limitation}</p>
    </div>
  );
}
