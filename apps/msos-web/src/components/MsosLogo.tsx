import Image from "next/image";

const MARK_ASPECT = 72 / 56;

type MsosLogoProps = {
  size?: number;
  variant?: "color" | "mono";
  className?: string;
};

export function MsosLogo({ size = 38, variant = "color", className }: MsosLogoProps) {
  const src = variant === "mono" ? "/brand/msos-mark-mono.svg" : "/brand/msos-mark-color.svg";
  const height = Math.round(size * MARK_ASPECT);

  return (
    <Image
      src={src}
      alt=""
      width={size}
      height={height}
      className={className}
      aria-hidden
      priority
    />
  );
}
