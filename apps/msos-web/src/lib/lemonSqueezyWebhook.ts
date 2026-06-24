import crypto from "node:crypto";

import {
  grantEntitlement,
  type EntitlementTier,
  type SubscriptionStatus,
} from "@/lib/msosEntitlements";
import { normalizeOwnerEmail } from "@/lib/msosIdentity";

export type LemonSqueezyWebhookPayload = {
  meta: {
    event_name: string;
    custom_data?: Record<string, unknown>;
  };
  data: {
    type: string;
    id: string;
    attributes: Record<string, unknown>;
  };
};

export function verifyLemonSqueezySignature(
  rawBody: string,
  signatureHeader: string | null,
  secret: string,
): boolean {
  if (!signatureHeader || !rawBody) return false;
  const signature = Buffer.from(signatureHeader, "hex");
  if (signature.length === 0) return false;
  const hmac = Buffer.from(
    crypto.createHmac("sha256", secret).update(rawBody).digest("hex"),
    "hex",
  );
  if (hmac.length !== signature.length) return false;
  return crypto.timingSafeEqual(hmac, signature);
}

export function parseLemonSqueezyWebhook(rawBody: string): LemonSqueezyWebhookPayload | null {
  try {
    const parsed = JSON.parse(rawBody) as unknown;
    if (!parsed || typeof parsed !== "object") return null;
    const payload = parsed as LemonSqueezyWebhookPayload;
    if (!payload.meta?.event_name || !payload.data?.attributes) return null;
    return payload;
  } catch {
    return null;
  }
}

type BillingEffect = {
  tier: EntitlementTier;
  subscriptionStatus: SubscriptionStatus;
};

function mapSubscriptionStatus(rawStatus: string): BillingEffect {
  const status = rawStatus.toLowerCase();
  if (status === "active" || status === "on_trial") {
    return { tier: "paid", subscriptionStatus: "active" };
  }
  if (status === "past_due" || status === "unpaid") {
    return { tier: "paid", subscriptionStatus: "past_due" };
  }
  if (status === "cancelled" || status === "paused") {
    return { tier: "paid", subscriptionStatus: "canceled" };
  }
  if (status === "expired") {
    return { tier: "free", subscriptionStatus: "canceled" };
  }
  return { tier: "paid", subscriptionStatus: "active" };
}

function effectForEvent(eventName: string, attributes: Record<string, unknown>): BillingEffect | null {
  const status = String(attributes.status || "");

  switch (eventName) {
    case "subscription_created":
    case "subscription_resumed":
    case "subscription_payment_success":
    case "subscription_payment_recovered":
      return { tier: "paid", subscriptionStatus: "active" };
    case "subscription_payment_failed":
      return { tier: "paid", subscriptionStatus: "past_due" };
    case "subscription_cancelled":
      return { tier: "paid", subscriptionStatus: "canceled" };
    case "subscription_expired":
      return { tier: "free", subscriptionStatus: "canceled" };
    case "subscription_updated":
      return mapSubscriptionStatus(status);
    default:
      return null;
  }
}

export type LemonSqueezyApplyResult =
  | { ok: true; email: string; eventName: string; tier: EntitlementTier }
  | { ok: false; reason: string };

/** Apply a verified Lemon Squeezy webhook to entitlements (idempotent upsert). */
export function applyLemonSqueezyWebhook(payload: LemonSqueezyWebhookPayload): LemonSqueezyApplyResult {
  const eventName = payload.meta.event_name;
  if (!eventName.startsWith("subscription_")) {
    return { ok: false, reason: `ignored event ${eventName}` };
  }

  const email = normalizeOwnerEmail(String(payload.data.attributes.user_email || ""));
  if (!email) {
    return { ok: false, reason: "missing user_email on subscription payload" };
  }

  const effect = effectForEvent(eventName, payload.data.attributes);
  if (!effect) {
    return { ok: false, reason: `no entitlement mapping for ${eventName}` };
  }

  const customerId =
    payload.data.attributes.customer_id != null
      ? String(payload.data.attributes.customer_id)
      : null;

  const entitlement = grantEntitlement({
    ownerEmail: email,
    tier: effect.tier,
    grantedBy: "lemon_squeezy",
    notes: `Lemon Squeezy ${eventName}`,
    billingCustomerId: customerId,
    billingSubscriptionId: payload.data.id,
    subscriptionStatus: effect.subscriptionStatus,
  });

  if (!entitlement) {
    return { ok: false, reason: "grant failed" };
  }

  return { ok: true, email, eventName, tier: effect.tier };
}
