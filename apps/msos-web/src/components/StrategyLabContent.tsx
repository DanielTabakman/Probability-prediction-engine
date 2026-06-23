import { StrategyLabClientShell } from "@/components/StrategyLabClientShell";
import type { DisplayPayload } from "@/lib/ppeDisplayPayload";

type StrategyLabContentProps = {
  displayPayload?: DisplayPayload | null;
};

export function StrategyLabContent({ displayPayload = null }: StrategyLabContentProps) {
  return <StrategyLabClientShell initialPayload={displayPayload} />;
}
