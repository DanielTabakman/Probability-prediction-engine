"use client";

import Link from "next/link";
import { useCallback, useState, type ComponentProps, type ReactNode } from "react";

type ActionLinkProps = Omit<ComponentProps<typeof Link>, "onClick"> & {
  children: ReactNode;
  onNavigate?: () => void;
  /** Replaces link label while navigation is in flight. */
  pendingLabel?: string;
};

/** Link with immediate pressed/pending feedback while navigation starts. */
export function ActionLink({
  children,
  className,
  onNavigate,
  pendingLabel,
  ...props
}: ActionLinkProps) {
  const [pending, setPending] = useState(false);

  const handleClick = useCallback(() => {
    setPending(true);
    onNavigate?.();
  }, [onNavigate]);

  return (
    <Link
      {...props}
      className={[className, pending ? "btn-pending" : ""].filter(Boolean).join(" ")}
      onClick={handleClick}
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
