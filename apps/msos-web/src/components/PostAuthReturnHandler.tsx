"use client";

import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef } from "react";

import {
  consumePostAuthReturnPath,
  currentAppPath,
  peekPostAuthReturnPath,
} from "@/lib/postAuthReturn";
import { hasWorkflowIdentity } from "@/lib/msosWorkflowClient";

/**
 * After Cloudflare Access (or session cookie), resume the path the user intended.
 * Uses URL returnTo when present; otherwise sessionStorage stashed before sign-in.
 */
export function PostAuthReturnHandler() {
  const router = useRouter();
  const pathname = usePathname();
  const attempted = useRef(false);

  useEffect(() => {
    if (attempted.current) return;
    const target = peekPostAuthReturnPath();
    if (!target) return;

    const here = currentAppPath();
    if (here === target || here.startsWith(`${target.split("?")[0]}`)) {
      consumePostAuthReturnPath();
      return;
    }

    attempted.current = true;

    void (async () => {
      for (let attempt = 0; attempt < 6; attempt += 1) {
        const signedIn = await hasWorkflowIdentity();
        if (signedIn) {
          consumePostAuthReturnPath();
          router.replace(target);
          return;
        }
        await new Promise((resolve) => window.setTimeout(resolve, 350));
      }
      attempted.current = false;
    })();
  }, [pathname, router]);

  return null;
}
