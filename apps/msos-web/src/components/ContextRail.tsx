"use client";

import { useEffect, useId, useState } from "react";

type ContextRailProps = {
  children: React.ReactNode;
  className?: string;
  "aria-label"?: string;
  sheetTitle?: string;
};

const MOBILE_MQ = "(max-width: 1100px)";

/** Right column on desktop; collapsible bottom sheet on narrow viewports. */
export function ContextRail({
  children,
  className,
  sheetTitle = "Summary & next steps",
  "aria-label": ariaLabel,
}: ContextRailProps) {
  const [mobile, setMobile] = useState(false);
  const [open, setOpen] = useState(false);
  const panelId = useId();

  useEffect(() => {
    const mq = window.matchMedia(MOBILE_MQ);
    const sync = () => setMobile(mq.matches);
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);

  useEffect(() => {
    if (!mobile) {
      setOpen(false);
    }
  }, [mobile]);

  const classes = [
    "context-rail",
    mobile ? "context-rail-mobile" : undefined,
    open ? "is-open" : undefined,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  if (!mobile) {
    return (
      <aside className={classes} aria-label={ariaLabel ?? "Step summary and next actions"}>
        {children}
      </aside>
    );
  }

  return (
    <>
      {open ? (
        <button
          type="button"
          className="context-rail-backdrop"
          aria-label="Close summary panel"
          onClick={() => setOpen(false)}
        />
      ) : null}
      <aside className={classes} aria-label={ariaLabel ?? "Step summary and next actions"}>
        <button
          type="button"
          className="context-rail-sheet-toggle"
          aria-expanded={open}
          aria-controls={panelId}
          onClick={() => setOpen((value) => !value)}
        >
          <span>{sheetTitle}</span>
          <span className="context-rail-sheet-chevron" aria-hidden="true">
            {open ? "▾" : "▴"}
          </span>
        </button>
        <div id={panelId} className="context-rail-sheet-body">
          {children}
        </div>
      </aside>
    </>
  );
}
