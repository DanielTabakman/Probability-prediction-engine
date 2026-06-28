/**
 * Plain-language trade strengths / risks from PPE suggestion boundary (display only).
 */

import type {
  BeliefVsMarketGlance,
  StrategySuggestionSummary,
  TradeReviewBlock,
} from "@/lib/ppeStrategySuggestion";
import { ABSOLUTE_FALLBACK_ASSET_ID } from "@/lib/strategyLabAsset";

export function stripReviewMd(text: string): string {
  return text.replace(/\*\*(.*?)\*\*/g, "$1").replace(/\*(.*?)\*/g, "$1").trim();
}

function firstLines(lines: string[] | undefined, max: number): string[] {
  if (!lines?.length) return [];
  return lines
    .map((line) => stripReviewMd(String(line)))
    .filter(Boolean)
    .slice(0, max);
}

export type TradeProsCons = {
  strengths: string[];
  risks: string[];
};

export function buildPlainLegSummary(
  tradeReview: TradeReviewBlock | null | undefined,
  reviewPayoffLine: string | null | undefined,
  reviewStructureLine: string | null | undefined,
): string | null {
  const fromApi = tradeReview?.plain_leg_summary?.trim();
  if (fromApi) {
    return fromApi;
  }
  const payoff = reviewPayoffLine?.trim();
  if (payoff) {
    return stripReviewMd(payoff).replace(/^Payoff shape \(illustrative read\):\s*/i, "");
  }
  const structure = reviewStructureLine?.trim();
  if (structure) {
    return stripReviewMd(structure);
  }
  return null;
}

export function buildTradeProsCons(
  glance: BeliefVsMarketGlance | null | undefined,
  summary: StrategySuggestionSummary | null | undefined,
  reviewPayoffLine: string | null | undefined,
  formatMoney: (usd: number) => string,
  tradeReview?: TradeReviewBlock | null,
  assetTicker: string = ABSOLUTE_FALLBACK_ASSET_ID,
): TradeProsCons {
  const ticker = assetTicker.trim() || ABSOLUTE_FALLBACK_ASSET_ID;
  const apiStrengths = firstLines(tradeReview?.strengths, 4);
  const apiRisks = firstLines(tradeReview?.risks, 4);
  if (apiStrengths.length || apiRisks.length) {
    const strengths = [...apiStrengths];
    const risks = [...apiRisks];
    if (typeof summary?.max_loss_usd === "number" && strengths.length < 4) {
      strengths.push(`Worst case capped near ${formatMoney(Math.abs(summary.max_loss_usd))}.`);
    }
    if ((summary?.breakevens_usd?.length ?? 0) > 0 && risks.length < 4) {
      const be = summary!.breakevens_usd!.map((value) => formatMoney(value)).join(" and ");
      risks.push(`Break even near ${be} at expiry.`);
    }
    if (risks.length < 4) {
      risks.push("Illustrative paper plan — not advice and not a live order.");
    }
    return {
      strengths: [...new Set(strengths)].slice(0, 4),
      risks: [...new Set(risks)].slice(0, 4),
    };
  }

  const strengths: string[] = [];
  const risks: string[] = [];

  const fit =
    glance?.width_relation_label?.trim() ||
    glance?.disagreement_type_line?.trim();
  if (fit) {
    strengths.push(stripReviewMd(fit));
  }

  strengths.push(...firstLines(glance?.digest_lines, 2));

  if (typeof summary?.max_loss_usd === "number") {
    strengths.push(`Worst case is capped at about ${formatMoney(Math.abs(summary.max_loss_usd))}.`);
  } else if (summary?.max_loss_usd == null) {
    strengths.push("Defined-risk structure — loss is capped, not open-ended.");
  }

  if (typeof summary?.max_gain_usd === "number" && summary.max_gain_usd > 0) {
    strengths.push(
      `Best case is about ${formatMoney(summary.max_gain_usd)} if ${ticker} lands in your range.`,
    );
  }

  const payoff = reviewPayoffLine?.trim();
  if (payoff && strengths.length < 4) {
    const plain = stripReviewMd(payoff).replace(/^Payoff shape \(illustrative read\):\s*/i, "");
    if (plain) {
      strengths.push(plain);
    }
  }

  risks.push(...firstLines(glance?.fit_bridge_bullets, 2));

  if ((summary?.breakevens_usd?.length ?? 0) > 0) {
    const be = summary!.breakevens_usd!.map((value) => formatMoney(value)).join(" and ");
    risks.push(`You need ${ticker} near ${be} at expiry to break even on this sketch.`);
  }

  risks.push(
    `If ${ticker} moves outside the range you expect, profit shrinks or you take the max loss.`,
  );
  risks.push("This is an illustrative paper plan — not advice and not a live order.");

  return {
    strengths: [...new Set(strengths)].slice(0, 4),
    risks: [...new Set(risks)].slice(0, 4),
  };
}
