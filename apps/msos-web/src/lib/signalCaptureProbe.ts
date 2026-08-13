import { execFile } from "child_process";
import { readdir, stat } from "fs/promises";
import path from "path";
import { promisify } from "util";

const SOURCE_DIRS = ["ws", "txstream", "ndax", "jupiter"] as const;
const LIVE_AFTER_MS = 2 * 60 * 1000;
const execFileAsync = promisify(execFile);

export type NdaxMarketQualityWindow = {
  status: "OK" | "NO_L1_DATA" | "ERROR";
  window_seconds?: number;
  index_files_considered?: number;
  truncated_active_files?: number;
  recent_event_count?: number;
  l1_observations?: number;
  coverage_seconds?: number | null;
  freshness_seconds?: number | null;
  event_rate_hz?: number | null;
  first_mid_cad?: number | null;
  last_mid_cad?: number | null;
  min_mid_cad?: number | null;
  max_mid_cad?: number | null;
  move_pct?: number | null;
  range_pct?: number | null;
  median_spread_cad?: number | null;
  mean_spread_bps?: number | null;
  median_spread_bps?: number | null;
  p95_spread_bps?: number | null;
  median_gap_seconds?: number | null;
  max_gap_seconds?: number | null;
  error?: string;
};

export type SignalCaptureProbeState = {
  status: "NOT CONNECTED" | "STOPPED" | "EMPTY" | "LIVE" | "STALE";
  detail: string;
  origin: "local" | "vm" | "https" | "none";
  configuredPath: string | null;
  sourceStates: Array<{
    source: (typeof SOURCE_DIRS)[number];
    files: number;
    newestMtimeMs: number | null;
  }>;
  newestMtimeMs: number | null;
  ndax15m: NdaxMarketQualityWindow | null;
};

type RemoteStatusPayload = {
  status: "STOPPED" | "EMPTY" | "LIVE" | "STALE";
  container_running?: boolean;
  total_files: number;
  age_seconds: number | null;
  sources: Array<{
    source: string;
    files: number;
    newest_mtime: number | null;
  }>;
  ndax_15m?: NdaxMarketQualityWindow;
};

function emptySources(): SignalCaptureProbeState["sourceStates"] {
  return SOURCE_DIRS.map((source) => ({ source, files: 0, newestMtimeMs: null }));
}

function normalizeRemoteState(
  payload: RemoteStatusPayload,
  origin: "vm" | "https",
  label: string,
): SignalCaptureProbeState {
  const sourceStates = SOURCE_DIRS.map((source) => {
    const remote = payload.sources.find((candidate) => candidate.source === source);
    return {
      source,
      files: remote?.files ?? 0,
      newestMtimeMs: remote?.newest_mtime == null ? null : remote.newest_mtime * 1000,
    };
  });
  const activeSources = sourceStates.filter((source) => source.files > 0).map((source) => source.source);
  const newestMtimeMs = newestTimestamp(sourceStates);
  const detail =
    payload.status === "STOPPED"
      ? `${label} is reachable, but signal capture is stopped.`
      : payload.status === "EMPTY"
        ? `${label} is connected; capture is running but has not written raw files yet.`
        : `${label} · ${activeSources.join(", ")} observed · ${payload.total_files} raw files · newest write ${payload.age_seconds ?? "?"}s ago.`;

  return {
    status: payload.status,
    detail,
    origin,
    configuredPath: null,
    sourceStates,
    newestMtimeMs,
    ndax15m: payload.ndax_15m ?? null,
  };
}

async function loadHttpState(statusUrl: string, token: string): Promise<SignalCaptureProbeState> {
  try {
    const response = await fetch(statusUrl, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
      signal: AbortSignal.timeout(7000),
    });
    if (!response.ok) {
      throw new Error(`status ${response.status}`);
    }
    const payload = (await response.json()) as RemoteStatusPayload;
    return normalizeRemoteState(payload, "https", "Condor status endpoint");
  } catch {
    return {
      status: "NOT CONNECTED",
      detail: "Could not read the token-protected Condor status endpoint.",
      origin: "https",
      configuredPath: null,
      sourceStates: emptySources(),
      newestMtimeMs: null,
      ndax15m: null,
    };
  }
}

async function loadVmState(sshHost: string): Promise<SignalCaptureProbeState> {
  try {
    const remoteCommand = 'cd "$HOME/oct/oct-signal-capture" && python3 deploy/status_json.py';
    const { stdout } = await execFileAsync(
      "ssh",
      ["-o", "BatchMode=yes", "-o", "ConnectTimeout=5", sshHost, remoteCommand],
      { timeout: 7000, maxBuffer: 64 * 1024 },
    );
    const payload = JSON.parse(stdout.trim()) as RemoteStatusPayload;
    return normalizeRemoteState(payload, "vm", `VM ${sshHost}`);
  } catch {
    return {
      status: "NOT CONNECTED",
      detail: `Could not read capture status from VM ${sshHost}. Ensure SSH works non-interactively and deploy/status_json.py exists on the VM.`,
      origin: "vm",
      configuredPath: null,
      sourceStates: emptySources(),
      newestMtimeMs: null,
      ndax15m: null,
    };
  }
}

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

async function loadLocalState(configuredPath: string): Promise<SignalCaptureProbeState> {
  try {
    const rootStat = await stat(configuredPath);
    if (!rootStat.isDirectory()) {
      throw new Error("configured path is not a directory");
    }
  } catch {
    return {
      status: "NOT CONNECTED",
      detail: `Configured capture path is unavailable: ${configuredPath}`,
      origin: "local",
      configuredPath,
      sourceStates: emptySources(),
      newestMtimeMs: null,
      ndax15m: null,
    };
  }

  const sourceStates = await Promise.all(SOURCE_DIRS.map((source) => inspectSourceDir(configuredPath, source)));
  const totalFiles = sourceStates.reduce((sum, source) => sum + source.files, 0);
  const newestMtimeMs = newestTimestamp(sourceStates);

  if (totalFiles === 0 || newestMtimeMs === null) {
    return {
      status: "EMPTY",
      detail: "Local capture data directory is connected, but no raw collector files have been observed yet.",
      origin: "local",
      configuredPath,
      sourceStates,
      newestMtimeMs,
      ndax15m: null,
    };
  }

  const ageMs = Date.now() - newestMtimeMs;
  const activeSources = sourceStates.filter((source) => source.newestMtimeMs !== null).map((source) => source.source);
  const status = ageMs <= LIVE_AFTER_MS ? "LIVE" : "STALE";
  const ageSeconds = Math.max(0, Math.round(ageMs / 1000));

  return {
    status,
    detail: `Local · ${activeSources.join(", ")} observed · ${totalFiles} raw files · newest write ${ageSeconds}s ago.`,
    origin: "local",
    configuredPath,
    sourceStates,
    newestMtimeMs,
    ndax15m: null,
  };
}

export async function loadSignalCaptureProbeState(): Promise<SignalCaptureProbeState> {
  const statusUrl = process.env.OCT_SIGNAL_CAPTURE_STATUS_URL?.trim();
  const statusToken = process.env.OCT_SIGNAL_CAPTURE_STATUS_TOKEN?.trim();
  if (statusUrl && statusToken) {
    return loadHttpState(statusUrl, statusToken);
  }

  const sshHost = process.env.OCT_SIGNAL_CAPTURE_SSH_HOST?.trim();
  if (sshHost) {
    return loadVmState(sshHost);
  }

  const configuredPath = process.env.OCT_SIGNAL_CAPTURE_DATA_DIR?.trim();
  if (configuredPath) {
    return loadLocalState(configuredPath);
  }

  return {
    status: "NOT CONNECTED",
    detail:
      "Set OCT_SIGNAL_CAPTURE_STATUS_URL + OCT_SIGNAL_CAPTURE_STATUS_TOKEN for shared web status, OCT_SIGNAL_CAPTURE_SSH_HOST for VM status, or OCT_SIGNAL_CAPTURE_DATA_DIR for a local read-only probe.",
    origin: "none",
    configuredPath: null,
    sourceStates: emptySources(),
    newestMtimeMs: null,
    ndax15m: null,
  };
}
