"use client";

/** Clickable expiry chip — native select for accessibility (no new math). */

export function formatExpiryLabel(value: string): string {
  const iso = /^\d{4}-\d{2}-\d{2}$/.test(value);
  if (!iso) {
    return value;
  }
  const parsed = new Date(`${value}T12:00:00Z`);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    timeZone: "UTC",
  });
}

type ExpiryPickerProps = {
  value: string;
  options: string[];
  onChange: (expiry: string) => void;
  disabled?: boolean;
  className?: string;
};

export function ExpiryPicker({
  value,
  options,
  onChange,
  disabled = false,
  className,
}: ExpiryPickerProps) {
  const canPick = !disabled && options.length > 1;
  const label = formatExpiryLabel(value);

  if (!canPick) {
    return <span className={className ?? "expiry-label"}>{label}</span>;
  }

  return (
    <label className={`expiry-picker${className ? ` ${className}` : ""}`}>
      <span className="expiry-picker-face" aria-hidden="true">
        {label}
      </span>
      <select
        className="expiry-picker-select"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        aria-label="Choose option expiry date"
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {formatExpiryLabel(option)}
          </option>
        ))}
      </select>
    </label>
  );
}
