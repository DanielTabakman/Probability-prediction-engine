import assert from "node:assert/strict";
import test from "node:test";

import {
  parseOptionsMarketQuestion,
  targetDateFromPreset,
} from "../src/lib/optionsMarketReadQuery.ts";

const AS_OF = "2026-09-17T18:49:12Z";

test("ordinary question without a date uses the stable API default", () => {
  assert.deepEqual(parseOptionsMarketQuestion("What is BTC options saying?", AS_OF), {
    ok: true,
    targetDate: null,
    explanation: "No date was mentioned, so this uses the API's standard 30-day target.",
  });
});

test("parses ISO, named, and numeric calendar dates", () => {
  assert.equal(parseOptionsMarketQuestion("BTC on 2026-12-25", AS_OF).targetDate, "2026-12-25");
  assert.equal(
    parseOptionsMarketQuestion("What about December 25, 2026?", AS_OF).targetDate,
    "2026-12-25",
  );
  assert.equal(parseOptionsMarketQuestion("BTC 12/25/2026", AS_OF).targetDate, "2026-12-25");
});

test("relative phrases use the snapshot date, not the device clock", () => {
  assert.equal(parseOptionsMarketQuestion("in 30 days", AS_OF).targetDate, "2026-10-17");
  assert.equal(parseOptionsMarketQuestion("3 weeks from now", AS_OF).targetDate, "2026-10-08");
  assert.equal(parseOptionsMarketQuestion("next month", AS_OF).targetDate, "2026-10-17");
});

test("recognizes useful calendar phrases", () => {
  assert.equal(parseOptionsMarketQuestion("BTC next Friday", AS_OF).targetDate, "2026-09-18");
  assert.equal(parseOptionsMarketQuestion("BTC at Christmas", AS_OF).targetDate, "2026-12-25");
  assert.equal(parseOptionsMarketQuestion("What about year-end?", AS_OF).targetDate, "2026-12-31");
});

test("does not silently guess invalid or unclear date requests", () => {
  const invalid = parseOptionsMarketQuestion("February 31, 2027", AS_OF);
  assert.equal(invalid.ok, false);
  const unclear = parseOptionsMarketQuestion("some time in month 13", AS_OF);
  assert.equal(unclear.ok, false);
});

test("rejects past dates and unsupported assets before calling the API", () => {
  assert.equal(parseOptionsMarketQuestion("BTC on 2026-09-01", AS_OF).ok, false);
  assert.equal(parseOptionsMarketQuestion("What is ETH saying in 30 days?", AS_OF).ok, false);
});

test("preset targets are deterministic", () => {
  assert.equal(targetDateFromPreset("default", AS_OF).targetDate, null);
  assert.equal(targetDateFromPreset("7d", AS_OF).targetDate, "2026-09-24");
  assert.equal(targetDateFromPreset("90d", AS_OF).targetDate, "2026-12-16");
  assert.equal(targetDateFromPreset("year-end", AS_OF).targetDate, "2026-12-31");
});
