export type OptionsMarketReadEnvironment = "production" | "staging";

export function optionsMarketReadEnvironment(
  forwardedHost: string | null | undefined,
  host: string | null | undefined,
  fallbackHost = "",
): OptionsMarketReadEnvironment {
  const candidate = forwardedHost?.split(",")[0].trim() || host || fallbackHost;
  return candidate.toLowerCase().startsWith("staging.") ? "staging" : "production";
}
