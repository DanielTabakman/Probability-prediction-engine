"use client";

import {
  REGION_BET_RESUME_CLEAN_START_COPY,
  REGION_BET_RESUME_LIMITATION,
  regionBetResumeRestoredFields,
  type RegionBetResumeReason,
  type RegionBetResumeState,
} from "@/lib/regionBetResume";

type RegionBetResumeCardProps = {
  resume: RegionBetResumeState;
  onResume: () => void;
  onCleanStart: () => void;
};

function reasonCopy(reason: RegionBetResumeReason): string {
  if (reason === "valid") {
    return "Resume your most recent valid paper Region Bet and last safe guided step.";
  }
  if (reason === "malformed") {
    return "Saved state was malformed and was ignored.";
  }
  if (reason === "cross_owner") {
    return "This workspace does not own that Region Bet. Start clean instead of substituting another owner's data.";
  }
  if (reason === "stale") {
    return "The saved Region Bet is stale and was ignored.";
  }
  return REGION_BET_RESUME_CLEAN_START_COPY;
}

export function RegionBetResumeCard({
  resume,
  onResume,
  onCleanStart,
}: RegionBetResumeCardProps) {
  const canResume = resume.mode === "resume" && resume.regionBet !== null;
  const restored = resume.regionBet
    ? regionBetResumeRestoredFields(resume.regionBet)
    : null;

  return (
    <div className="panel chart" data-testid="region-bet-resume-card">
      <div className="panel-head">
        <div>
          <h2>Resume Region Bet</h2>
          <div className="panel-sub">Owner-scoped paper draft only.</div>
        </div>
        <span className="tag teal">Paper</span>
      </div>
      <p>{reasonCopy(resume.reason)}</p>
      {canResume && restored ? (
        <div className="score" aria-label="Restored Region Bet">
          <div className="small-panel">
            <div className="k">Asset</div>
            <div className="v teal">{restored.asset_id}</div>
          </div>
          <div className="small-panel">
            <div className="k">Window</div>
            <div className="v">{restored.expiry_utc.slice(0, 10)}</div>
          </div>
          <div className="small-panel">
            <div className="k">Region</div>
            <div className="v amber">
              {restored.selected_region.price_min_usd} to{" "}
              {restored.selected_region.price_max_usd}
            </div>
          </div>
          <div className="small-panel">
            <div className="k">Expression</div>
            <div className="v">
              {restored.selected_expression_ref?.expression_id ?? "None selected"}
            </div>
          </div>
          <div className="small-panel">
            <div className="k">Step</div>
            <div className="v">{resume.step}</div>
          </div>
        </div>
      ) : null}
      <p className="micro">
        {REGION_BET_RESUME_LIMITATION} Not financial advice, not a recommendation, and not
        order execution.
      </p>
      <div className="lab-setup-actions">
        {canResume ? (
          <button type="button" className="btn slim primary" onClick={onResume}>
            Resume saved draft
          </button>
        ) : null}
        <button type="button" className="btn slim" onClick={onCleanStart}>
          Start clean
        </button>
      </div>
    </div>
  );
}
