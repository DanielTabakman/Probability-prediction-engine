import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

export type CommandCenterKpi = {
  label: string;
  value: string;
  sub: string;
  tone?: string;
};

export type CommandCenterWorkItem = {
  name: string;
  tag: string;
  detail: string;
  tagTone?: string;
};

export type CommandCenterSummary = {
  status: "live" | "degraded";
  reason?: string;
  sourceLabel: string;
  kpis: CommandCenterKpi[];
  currentWork: CommandCenterWorkItem[];
};

const DEGRADED: CommandCenterSummary = {
  status: "degraded",
  reason: "PPE snapshot database not configured or unreachable.",
  sourceLabel: "From PPE snapshots",
  kpis: [],
  currentWork: [],
};

function repoRoot(): string | null {
  const env = (process.env.PPE_REPO_ROOT ?? "").trim();
  if (env && fs.existsSync(path.join(env, "src", "viz", "command_center_snapshot_summary.py"))) {
    return env;
  }
  let dir = process.cwd();
  for (let i = 0; i < 8; i += 1) {
    const helper = path.join(dir, "src", "viz", "command_center_snapshot_summary.py");
    if (fs.existsSync(helper)) {
      return dir;
    }
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return null;
}

export function loadCommandCenterSummary(): CommandCenterSummary {
  const dbPath = (process.env.PPE_SNAPSHOT_DB_PATH ?? "").trim();
  if (!dbPath) {
    return {
      ...DEGRADED,
      reason: "PPE_SNAPSHOT_DB_PATH is not set on msos_web.",
    };
  }
  const root = repoRoot();
  if (!root) {
    return {
      ...DEGRADED,
      reason: "PPE snapshot reader unavailable (repo root not found).",
    };
  }
  const python = (process.env.PPE_PYTHON ?? process.env.PYTHON ?? "python").trim();
  const proc = spawnSync(
    python,
    ["-m", "src.viz.command_center_snapshot_summary"],
    {
      cwd: root,
      env: { ...process.env, PYTHONPATH: root, PPE_SNAPSHOT_DB_PATH: dbPath },
      encoding: "utf-8",
      maxBuffer: 2 * 1024 * 1024,
    },
  );
  if (proc.status !== 0 || !proc.stdout?.trim()) {
    return {
      ...DEGRADED,
      reason: proc.stderr?.trim() || "Could not read snapshot summary from PPE store.",
    };
  }
  try {
    return JSON.parse(proc.stdout) as CommandCenterSummary;
  } catch {
    return {
      ...DEGRADED,
      reason: "Invalid snapshot summary payload from PPE reader.",
    };
  }
}
