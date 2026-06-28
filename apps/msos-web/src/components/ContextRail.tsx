type ContextRailProps = {
  children: React.ReactNode;
  className?: string;
  "aria-label"?: string;
};

/** Right column for workflow pages — consistent width and stacking. */
export function ContextRail({ children, className, "aria-label": ariaLabel }: ContextRailProps) {
  const classes = ["context-rail", className].filter(Boolean).join(" ");
  return (
    <aside className={classes} aria-label={ariaLabel ?? "Step summary and next actions"}>
      {children}
    </aside>
  );
}
