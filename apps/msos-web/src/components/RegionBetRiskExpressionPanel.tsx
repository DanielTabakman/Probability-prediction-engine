"use client";

import { useEffect, useMemo, useState } from "react";

import { MARKET_TUNING } from "@/lib/beliefTuning";
import { fetchExposureMenuClient, type ExposureMenuPayload } from "@/lib/ppeExposureMenu";
import { fetchStrategySuggestion, type StrategySuggestionPayload } from "@/lib/ppeStrategySuggestion";
import type { RegionBetContract } from "@/lib/regionBet";
import type { RegionBetGuidedShellPatch } from "@/lib/regionBetGuidedShell";
import {
  REGION_BET_PAYOFF_PREFERENCES,
  buildRegionBetRiskExpression,
  inferRegionBetExpressionDirection,
  regionBetHorizonChip,
  regionBetRiskConstraintIssues,
  regionBetTargetHorizonDays,
  selectedRegionBetExpressionRef,
} from "@/lib/regionBetRiskExpression";

type RegionBetRiskExpressionPanelProps = {
  draft: RegionBetContract;
  onDraftChange: (patch: RegionBetGuidedShellPatch) => void;
};

function optionalNumberValue(value: number | undefined): string {
  return typeof value === "number" && Number.isFinite(value) ? String(value) : "";
}

function parseOptionalNumber(value: string): number | undefined {
  if (!value.trim()) return undefined;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : undefined;
}

export function RegionBetRiskExpressionPanel({
  draft,
  onDraftChange,
}: RegionBetRiskExpressionPanelProps) {
  const [loading, setLoading] = useState(true);
  const [exposureMenu, setExposureMenu] = useState<ExposureMenuPayload | null>(null);
  const [strategySuggestion, setStrategySuggestion] = useState<StrategySuggestionPayload | null>(
    null,
  );

  const direction = inferRegionBetExpressionDirection(draft);
  const horizonDays = regionBetTargetHorizonDays(draft);
  const horizon = regionBetHorizonChip(horizonDays);
  const expiryDate = draft.target.expiry_utc.slice(0, 10);
  const constraintIssues = regionBetRiskConstraintIssues(draft.risk_constraints);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    void Promise.all([
      fetchExposureMenuClient(draft.asset.asset_id, direction, horizon),
      fetchStrategySuggestion(expiryDate, MARKET_TUNING, draft.asset.asset_id),
    ])
      .then(([menu, suggestion]) => {
        if (cancelled) return;
        setExposureMenu(menu);
        setStrategySuggestion(suggestion);
        setLoading(false);
      })
      .catch(() => {
        if (cancelled) return;
        setExposureMenu(null);
        setStrategySuggestion(null);
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [direction, draft.asset.asset_id, expiryDate, horizon]);

  const payload = useMemo(
    () => buildRegionBetRiskExpression(draft, exposureMenu, strategySuggestion),
    [draft, exposureMenu, strategySuggestion],
  );

  const selectedId = draft.selected_expression_ref?.expression_id;

  return (
    <div className="panel chart" data-testid="region-bet-risk-expression-panel">
      <div className="panel-head">
        <div>
          <h2>Map risk to a paper expression</h2>
          <div className="panel-sub">
            State max-loss, premium, and payoff preference. The draft keeps only that
            choice and these limits.
          </div>
        </div>
        <span className="tag">Paper</span>
      </div>

      <div className="lab-setup-row">
        <label>
          <span>Max loss (USD)</span>
          <input
            type="number"
            min="0"
            step="1"
            value={optionalNumberValue(draft.risk_constraints.max_loss_usd)}
            onChange={(event) =>
              onDraftChange({
                risk_constraints: {
                  max_loss_usd: parseOptionalNumber(event.currentTarget.value),
                },
              })
            }
          />
        </label>
        <label>
          <span>Premium budget (USD)</span>
          <input
            type="number"
            min="0"
            step="1"
            value={optionalNumberValue(draft.risk_constraints.max_premium_usd)}
            onChange={(event) =>
              onDraftChange({
                risk_constraints: {
                  max_premium_usd: parseOptionalNumber(event.currentTarget.value),
                },
              })
            }
          />
        </label>
        <label>
          <span>Payoff preference</span>
          <select
            value={draft.risk_constraints.payoff_preference ?? ""}
            onChange={(event) =>
              onDraftChange({
                risk_constraints: {
                  payoff_preference: event.currentTarget.value || undefined,
                },
              })
            }
          >
            <option value="">Select a paper preference</option>
            {REGION_BET_PAYOFF_PREFERENCES.map((item) => (
              <option key={item.id} value={item.id}>
                {item.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      {constraintIssues.length > 0 ? (
        <p className="micro">
          Enter a max-loss, premium budget, and payoff preference to see paper
          expression choices. {constraintIssues[0]}.
        </p>
      ) : loading ? (
        <p className="micro">Loading paper expression choices...</p>
      ) : payload.status === "empty_candidates" ? (
        <p className="micro">
          No paper expression candidates fit these limits right now. Nothing was
          selected. Educational comparison only; not financial advice, not a recommendation, and not order execution.
        </p>
      ) : (
        <div aria-label="Paper expression choices">
          {payload.choices.map((choice) => {
            const active = selectedId === choice.ranked.candidate_id;
            return (
              <button
                key={choice.lane}
                type="button"
                className={`option-row${active ? "" : " dimmed"}`}
                aria-pressed={active}
                onClick={() =>
                  onDraftChange({
                    selected_expression_ref: selectedRegionBetExpressionRef(choice),
                    risk_constraints: {
                      max_loss_usd: draft.risk_constraints.max_loss_usd,
                      max_premium_usd: draft.risk_constraints.max_premium_usd,
                      payoff_preference: draft.risk_constraints.payoff_preference,
                    },
                  })
                }
              >
                <div>
                  <h3>
                    {choice.label}: {choice.ranked.label}
                  </h3>
                  <p>{choice.explanation}</p>
                </div>
                <span className={`tag${active ? " amber" : ""}`}>
                  {choice.ranked.score.toFixed(0)}
                </span>
              </button>
            );
          })}
        </div>
      )}

      <p className="micro">{payload.limitation}</p>
    </div>
  );
}
