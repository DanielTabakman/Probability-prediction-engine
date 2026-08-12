import { readdir, stat } from "fs/promises";
import path from "path";

const SOURCE_DIRS = ["ws", "txstream", "ndax", "jupiter"] as const;
const LIVE_AFTER_MS = 2 * 60 * 1000;

export type SignalCaptureProbeState = {
  status: "NOT CONNECTED" | "EMPTY" | "LIVE" | "STALE";
  detail: string;
  configuredPath: string | null;
  sourceStates: Array<{
    source: (typeof SOURCE_DIRS)[number];
    files: number;
    newestMtimeMs: number | null;
  }>;
  newestMtimeMs: number | null;
};

async function inspectSourceDir(root: string, source: (typeof SOURCE_DIRS)[number]) {
  const dir = path.join(root, "raw", source);
  try {
    const entries = await readdir(dir, { withFileTypes: true });
    const files = entries.filter((entry) => entry.isFile());
    let newestMtimeMs: number | null = null;
    for (const file of files) {
      try {
        const fileStat = await stat(path.join(dir, file.name));
        if (newestMtimeMs === null || fileStat.mtimeMs > newestMtimeMs) {
          newestMtimeMs = fileStat.mtimeMs;
        }
      } catch {
        // A writer may rotate a file between readdir and stat. Ignore that race.
      }
    }
    return { source, files: files.length, newestMtimeMs };
  } catch {
    return { source, files: 0, newestMtimeMs: null };
  }
}

function newestTimestamp(states: SignalCaptureProbeState["sourceStates"]): number | null {
  const values = states
    .map((state) => state.newestMtimeMs)
    .filter((value): value is number => typeof value === "number");
  return values.length > 0 ? Math.max(...values) : null;
}

export async function loadSignalCaptureProbeState(): Promise<SignalCaptureProbeState> {
  const configuredPath = process.env.OCT_SIGNAL_CAPTURE_DATA_DIR?.trim() || null;
  if (!configuredPath) {
    return {
      status: "NOT CONNECTED",
      detail: "Set OCT_SIGNAL_CAPTURE_DATA_DIR to the oct-signal-capture data directory to enable the live read-only probe.",
      configuredPath: null,
      sourceStates: SOURCE_DIRS.map((source) => ({ source, files: 0, newestMtimeMs: null })),
      newestMtimeMs: null,
    };
  }

  try {
    const rootStat = await stat(configuredPath);
    if (!rootStat.isDirectory()) {
      throw new Error("configured path is not a directory");
    }
  } catch {
    return {
      status: "NOT CONNECTED",
      detail: `Configured capture path is unavailable: ${configuredPath}`,
      configuredPath,
      sourceStates: SOURCE_DIRS.map((source) => ({ source, files: 0, newestMtimeMs: null })),
      newestMtimeMs: null,
    };
  }

  const sourceStates = await Promise.all(SOURCE_DIRS.map((source) => inspectSourceDir(configuredPath, source)));
  const totalFiles = sourceStates.reduce((sum, source) => sum + source.files, 0);
  const newestMtimeMs = newestTimestamp(sourceStates);

  if (totalFiles === 0 || newestMtimeMs === null) {
    return {
      status: "EMPTY",
      detail: "Capture data directory is connected, but no raw collector files have been observed yet.",
      configuredPath,
      sourceStates,
      newestMtimeMs,
    };
  }

  const ageMs = Date.now() - newestMtimeMs;
  const activeSources = sourceStates.filter((source) => source.newestMtimeMs !== null).map((source) => source.source);
  const status = ageMs <= LIVE_AFTER_MS ? "LIVE" : "STALE";
  const ageSeconds = Math.max(0, Math.round(ageMs / 1000));

  return {
    status,
    detail: `${activeSources.join(", ")} observed · ${totalFiles} raw files · newest write ${ageSeconds}s ago.`,
    configuredPath,
    sourceStates,
    newestMtimeMs,
  };
}
