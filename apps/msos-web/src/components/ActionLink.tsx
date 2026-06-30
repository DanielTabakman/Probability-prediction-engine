"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useState, type ComponentProps, type ReactNode } from "react";

import { useNavigationProgress } from "@/components/NavigationProgressProvider";
import { warmStrategyLabEntry } from "@/lib/prefetchStrategyLab";

type ActionLinkProps = Omit<ComponentProps<typeof Link>, "onClick" | "onPointerEnter"> & {
  children: ReactNode;
  onNavigate?: () => void;
  /** Replaces link label while navigation is in flight. */
  pendingLabel?: string;
  /** Warm Strategy Lab API payloads on hover (auto when href targets strategy-lab). */
  warmupOnHover?: boolean;
};

function shouldWarmStrategyLab(href: ComponentProps<typeof Link>["href"], warmupOnHover?: boolean): boolean {
  if (warmupOnHover) {
    return true;
  }
  if (typeof href === "string") {
    return href.includes("/strategy-lab");
  }
  if (href && typeof href === "object" && "pathname" in href && typeof href.pathname === "string") {
    return href.pathname.includes("/strategy-lab");
  }
  return false;
}

function resolveHrefString(href: ComponentProps<typeof Link>["href"]): string | null {
  if (typeof href === "string") {
    return href;
  }
  if (href && typeof href === "object" && "pathname" in href && typeof href.pathname === "string") {
    const query = "query" in href && href.query && typeof href.query === "object"
      ? `?${new URLSearchParams(href.query as Record<string, string>).toString()}`
      : "";
    return `${href.pathname}${query}`;
  }
  return null;
}

/** Link with immediate pressed/pending feedback while navigation starts. */
export function ActionLink({
  children,
  className,
  href,
  onNavigate,
  pendingLabel,
  warmupOnHover,
  ...props
}: ActionLinkProps) {
  const router = useRouter();
  const { start } = useNavigationProgress();
  const [pending, setPending] = useState(false);

  const handleClick = useCallback(() => {
    setPending(true);
    start();
    onNavigate?.();
  }, [onNavigate, start]);

  const handlePointerEnter = useCallback(() => {
    const hrefString = resolveHrefString(href);
    if (!hrefString) {
      return;
    }
    router.prefetch(hrefString);
    if (shouldWarmStrategyLab(href, warmupOnHover)) {
      warmStrategyLabEntry(router, hrefString);
    }
  }, [href, router, warmupOnHover]);

  return (
    <Link
      {...props}
      href={href}
      prefetch
      className={[className, pending ? "btn-pending" : ""].filter(Boolean).join(" ")}
      onClick={handleClick}
      onPointerEnter={handlePointerEnter}
      aria-busy={pending || undefined}
    >
      {pending ? <span className="btn-feedback" aria-hidden="true" /> : null}
      {pending && pendingLabel ? pendingLabel : children}
    </Link>
  );
}

type ActionButtonProps = ComponentProps<"button"> & {
  children: ReactNode;
};

/** Button with hover/active feedback and optional pending spinner. */
export function ActionButton({
  children,
  className,
  disabled,
  onClick,
  type = "button",
  ...props
}: ActionButtonProps) {
  const [pending, setPending] = useState(false);

  return (
    <button
      {...props}
      type={type}
      disabled={disabled || pending}
      className={[className, pending ? "btn-pending" : ""].filter(Boolean).join(" ")}
      aria-busy={pending || undefined}
      onClick={(event) => {
        setPending(true);
        onClick?.(event);
        window.setTimeout(() => setPending(false), 400);
      }}
    >
      {pending ? <span className="btn-feedback" aria-hidden="true" /> : null}
      {children}
    </button>
  );
}
