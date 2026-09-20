export type MarketReadQuerySuccess = {
  ok: true;
  targetDate: string | null;
  explanation: string;
};

export type MarketReadQueryFailure = {
  ok: false;
  message: string;
};

export type MarketReadQueryResult = MarketReadQuerySuccess | MarketReadQueryFailure;

const MONTHS: Record<string, number> = {
  january: 1,
  jan: 1,
  february: 2,
  feb: 2,
  march: 3,
  mar: 3,
  april: 4,
  apr: 4,
  may: 5,
  june: 6,
  jun: 6,
  july: 7,
  jul: 7,
  august: 8,
  aug: 8,
  september: 9,
  sep: 9,
  sept: 9,
  october: 10,
  oct: 10,
  november: 11,
  nov: 11,
  december: 12,
  dec: 12,
};

const WEEKDAYS: Record<string, number> = {
  sunday: 0,
  monday: 1,
  tuesday: 2,
  wednesday: 3,
  thursday: 4,
  friday: 5,
  saturday: 6,
};

function utcDate(year: number, month: number, day: number): Date | null {
  const value = new Date(Date.UTC(year, month - 1, day));
  if (
    value.getUTCFullYear() !== year ||
    value.getUTCMonth() !== month - 1 ||
    value.getUTCDate() !== day
  ) {
    return null;
  }
  return value;
}

function parseIsoDate(value: string): Date | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) return null;
  return utcDate(Number(match[1]), Number(match[2]), Number(match[3]));
}

function isoDate(value: Date): string {
  return value.toISOString().slice(0, 10);
}

function addUtcDays(value: Date, days: number): Date {
  const result = new Date(value.getTime());
  result.setUTCDate(result.getUTCDate() + days);
  return result;
}

function addUtcMonths(value: Date, months: number): Date {
  const targetMonth = value.getUTCMonth() + months;
  const targetYear = value.getUTCFullYear() + Math.floor(targetMonth / 12);
  const normalizedMonth = ((targetMonth % 12) + 12) % 12;
  const lastDay = new Date(Date.UTC(targetYear, normalizedMonth + 1, 0)).getUTCDate();
  return new Date(
    Date.UTC(targetYear, normalizedMonth, Math.min(value.getUTCDate(), lastDay)),
  );
}

function nextOccurrence(base: Date, month: number, day: number, year?: number): Date | null {
  if (year !== undefined) return utcDate(year, month, day);
  const thisYear = utcDate(base.getUTCFullYear(), month, day);
  if (!thisYear) return null;
  if (thisYear >= base) return thisYear;
  return utcDate(base.getUTCFullYear() + 1, month, day);
}

function humanDate(value: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    timeZone: "UTC",
    year: "numeric",
    month: "long",
    day: "numeric",
  }).format(value);
}

function success(date: Date | null, explanation: string): MarketReadQuerySuccess {
  return { ok: true, targetDate: date ? isoDate(date) : null, explanation };
}

function rejectPast(date: Date, base: Date): MarketReadQueryResult {
  if (date < base) {
    return {
      ok: false,
      message: `${humanDate(date)} is before this market snapshot. Choose ${humanDate(base)} or a later date.`,
    };
  }
  return success(date, `Using ${humanDate(date)} as the target date.`);
}

/**
 * Convert a deliberately bounded set of ordinary date phrases into the API's
 * ISO target_date. The snapshot date is the only clock, so repeat requests on
 * the same snapshot parse relative phrases identically.
 */
export function parseOptionsMarketQuestion(
  rawQuestion: string,
  snapshotAsOf: string,
): MarketReadQueryResult {
  const question = rawQuestion.trim();
  const lower = question.toLowerCase();
  const base = parseIsoDate(snapshotAsOf.slice(0, 10));
  if (!base) {
    return { ok: false, message: "The market snapshot time is unavailable. Try again shortly." };
  }

  if (/\b(eth|ethereum|sol|solana|xrp|doge|dogecoin)\b/i.test(question)) {
    return {
      ok: false,
      message: "This testing version supports BTC only. Other assets will be added after their data passes the same checks.",
    };
  }

  if (!question || /\b(default|standard|usual)\b/.test(lower)) {
    return success(null, "Using the API's standard 30-day target.");
  }

  const isoMatch = /\b(\d{4}-\d{2}-\d{2})\b/.exec(question);
  if (isoMatch) {
    const parsed = parseIsoDate(isoMatch[1]);
    if (!parsed) {
      return { ok: false, message: `${isoMatch[1]} is not a valid calendar date.` };
    }
    return rejectPast(parsed, base);
  }

  const numericMatch = /\b(\d{1,2})\/(\d{1,2})\/(\d{4})\b/.exec(question);
  if (numericMatch) {
    const parsed = utcDate(
      Number(numericMatch[3]),
      Number(numericMatch[1]),
      Number(numericMatch[2]),
    );
    if (!parsed) {
      return { ok: false, message: `${numericMatch[0]} is not a valid calendar date.` };
    }
    return rejectPast(parsed, base);
  }

  const monthPattern = Object.keys(MONTHS).join("|");
  const namedMonth = new RegExp(
    `\\b(${monthPattern})\\.?\\s+(\\d{1,2})(?:st|nd|rd|th)?(?:,?\\s+(\\d{4}))?\\b`,
    "i",
  ).exec(question);
  if (namedMonth) {
    const parsed = nextOccurrence(
      base,
      MONTHS[namedMonth[1].toLowerCase()],
      Number(namedMonth[2]),
      namedMonth[3] ? Number(namedMonth[3]) : undefined,
    );
    if (!parsed) {
      return { ok: false, message: `${namedMonth[0]} is not a valid calendar date.` };
    }
    return rejectPast(parsed, base);
  }

  const relative = /\b(?:in\s+)?(\d{1,3})\s*(day|week|month)s?(?:\s+(?:from\s+now|out|away))?\b/i.exec(
    question,
  );
  if (relative) {
    const amount = Number(relative[1]);
    if (amount < 1 || amount > 730) {
      return { ok: false, message: "Choose a horizon between 1 day and 730 days." };
    }
    const unit = relative[2].toLowerCase();
    const parsed = unit === "month" ? addUtcMonths(base, amount) : addUtcDays(base, amount * (unit === "week" ? 7 : 1));
    return success(parsed, `${amount} ${unit}${amount === 1 ? "" : "s"} from the ${humanDate(base)} snapshot is ${humanDate(parsed)}.`);
  }

  if (/\btomorrow\b/.test(lower)) {
    const parsed = addUtcDays(base, 1);
    return success(parsed, `Tomorrow relative to the snapshot is ${humanDate(parsed)}.`);
  }
  if (/\btoday\b/.test(lower)) {
    return success(base, `Using the snapshot date, ${humanDate(base)}.`);
  }
  if (/\bnext\s+week\b/.test(lower)) {
    const parsed = addUtcDays(base, 7);
    return success(parsed, `One week after the snapshot is ${humanDate(parsed)}.`);
  }
  if (/\bnext\s+month\b/.test(lower)) {
    const parsed = addUtcMonths(base, 1);
    return success(parsed, `One month after the snapshot is ${humanDate(parsed)}.`);
  }

  const weekday = /\bnext\s+(sunday|monday|tuesday|wednesday|thursday|friday|saturday)\b/i.exec(
    question,
  );
  if (weekday) {
    const wanted = WEEKDAYS[weekday[1].toLowerCase()];
    const delta = ((wanted - base.getUTCDay() + 7) % 7) || 7;
    const parsed = addUtcDays(base, delta);
    return success(parsed, `The next ${weekday[1]} after the snapshot is ${humanDate(parsed)}.`);
  }

  if (/\b(christmas|christmas day)\b/.test(lower)) {
    const parsed = nextOccurrence(base, 12, 25);
    return parsed
      ? success(parsed, `Using Christmas Day, ${humanDate(parsed)}.`)
      : { ok: false, message: "Could not resolve Christmas Day." };
  }

  if (/\b(year[- ]?end|end of (?:the )?year)\b/.test(lower)) {
    const year = /\bnext year\b/.test(lower)
      ? base.getUTCFullYear() + 1
      : base.getUTCFullYear();
    const thisYear = utcDate(year, 12, 31);
    const parsed = thisYear && thisYear >= base ? thisYear : utcDate(year + 1, 12, 31);
    return parsed
      ? success(parsed, `Using year-end, ${humanDate(parsed)}.`)
      : { ok: false, message: "Could not resolve year-end." };
  }

  const dateLikeWords = /\b(date|day|week|month|year|january|february|march|april|may|june|july|august|september|october|november|december)\b/;
  if (dateLikeWords.test(lower) || /\d/.test(lower)) {
    return {
      ok: false,
      message: "I couldn't identify one date. Try “December 25, 2026”, “in 90 days”, “next Friday”, or use the date picker.",
    };
  }

  return success(null, "No date was mentioned, so this uses the API's standard 30-day target.");
}

export function targetDateFromPreset(
  preset: "default" | "7d" | "90d" | "year-end",
  snapshotAsOf: string,
): MarketReadQueryResult {
  if (preset === "default") {
    return success(null, "Using the API's standard 30-day target.");
  }
  if (preset === "7d") return parseOptionsMarketQuestion("in 7 days", snapshotAsOf);
  if (preset === "90d") return parseOptionsMarketQuestion("in 90 days", snapshotAsOf);
  return parseOptionsMarketQuestion("year-end", snapshotAsOf);
}
