/** @deprecated Import from msosIdentityCore or msosWorkflowAuth instead. */
export {
  ACCESS_EMAIL_HEADERS,
  devAllowsAnonymousIdentity,
  normalizeOwnerEmail,
  resolveMsosIdentityFromHeaders,
} from "@/lib/msosIdentityCore";
export { requireProtectedIdentity, type MsosIdentityResult } from "@/lib/msosWorkflowAuth";
