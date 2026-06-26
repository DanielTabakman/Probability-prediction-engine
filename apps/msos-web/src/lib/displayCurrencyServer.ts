import { cookies } from "next/headers";

import {
  DISPLAY_CURRENCY_COOKIE,
  parseDisplayCurrencyFromCookie,
  type DisplayCurrency,
} from "@/lib/displayCurrency";

/** Server components — read display currency from the msos_currency cookie. */
export async function resolveDisplayCurrency(): Promise<DisplayCurrency> {
  const jar = await cookies();
  return parseDisplayCurrencyFromCookie(jar.get(DISPLAY_CURRENCY_COOKIE)?.value);
}
