# Google Docs MCP — give Cursor agents access to a doc

This project uses the community server [`@a-bonus/google-docs-mcp`](https://github.com/a-bonus/google-docs-mcp) over **stdio** (local). The **shared artifact** is your Google Doc; Cursor (and other MCP clients) reach it through that server after you complete OAuth once.

## What you are setting up

```text
You (browser OAuth once)
    → token in ~/.config/google-docs-mcp/token.json
Cursor Agent
    → .cursor/mcp.json → npx @a-bonus/google-docs-mcp
    → Google Docs/Drive API
    → your Doc (must be visible to the Google account you authorized)
```

**Read vs write:** Google OAuth scopes are granted at auth time. This server can read and write any Doc your account can access. Restrict access by (1) using a dedicated Google account, (2) sharing only specific docs to that account, and (3) disabling the MCP server in Cursor when you only want repo-local work.

---

## Step 1 — Pick the doc and copy its ID

Open the doc in the browser. The URL looks like:

```text
https://docs.google.com/document/d/DOCUMENT_ID_HERE/edit
```

Copy `DOCUMENT_ID_HERE`. You will paste it into `.env.mcp`:

- `PPE_MASTER_DOC_ID` — vision / canon (PPE Master)
- `MSOS_REPO_TRUTH_DOC_ID` — as-built repo truth ([MSOS Repo Truth](https://docs.google.com/document/d/1BlGsdaKgBCPHwHqMR52io0-IDKLrSWvqhMXdrDxap1w/edit))

---

## Step 2 — Google Cloud project and OAuth client

1. Open [Google Cloud Console](https://console.cloud.google.com/) and create or select a project.
2. **APIs & Services → Library** — enable:
   - Google Docs API
   - Google Drive API  
   (Sheets/Gmail/Calendar are optional; the MCP package may request broader scopes at auth.)
3. **APIs & Services → OAuth consent screen**
   - User type: **External** (or Internal if Workspace)
   - Add yourself as a **Test user** while the app is in Testing
4. **APIs & Services → Credentials → Create credentials → OAuth client ID**
   - Application type: **Desktop app**
   - Copy **Client ID** and **Client secret**

---

## Step 3 — Local secrets (never commit)

From the repo root:

```powershell
copy .env.mcp.example .env.mcp
```

Edit `.env.mcp`:

```env
GOOGLE_CLIENT_ID=....apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
PPE_MASTER_DOC_ID=your_ppe_master_document_id
MSOS_REPO_TRUTH_DOC_ID=your_msos_repo_truth_document_id
```

`.env.mcp` is gitignored.

---

## Step 4 — One-time browser authorization

Requires Node.js `npx` on your PATH (same machine as Cursor).

**Easiest (Windows):** from repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\auth_google_docs_mcp.ps1
```

**Manual:** paste this **entire block** at once (top → bottom):

```powershell
cd "d:\Users\User\Desktop\Probability prediction engine"
foreach ($line in Get-Content .env.mcp) {
  if ($line -match '^\s*GOOGLE_CLIENT_ID=(.+)$') { $env:GOOGLE_CLIENT_ID = $matches[1].Trim() }
  if ($line -match '^\s*GOOGLE_CLIENT_SECRET=(.+)$') { $env:GOOGLE_CLIENT_SECRET = $matches[1].Trim() }
}
npx.cmd -y @a-bonus/google-docs-mcp auth
```

(On Windows, prefer `npx.cmd` if `npx` fails with an execution-policy error.)

Do **not** paste OAuth secrets in Cursor chat — only in `.env.mcp`. See **Why not share client secret in chat?** below.

Complete the browser flow. Token is stored at:

```text
%USERPROFILE%\.config\google-docs-mcp\token.json
```

(on Linux/macOS: `~/.config/google-docs-mcp/token.json`)

---

## Step 5 — Enable MCP in this repo

This repo ships `.cursor/mcp.json` that starts `scripts/google_docs_mcp_launcher.ps1` (loads `.env.mcp`, then runs the MCP server). Cursor’s PATH often lacks `npx`; the launcher fixes that on Windows.

1. **Cursor → Settings → Features → Model Context Protocol** — ensure **google-docs** is enabled.
2. Reload MCP or restart Cursor if tools do not appear.
3. **View → Output → MCP Logs** — confirm the server starts without auth errors.

---

## Step 6 — Verify the agent can read your doc

In Cursor chat (Agent mode), try:

```text
Using the google-docs MCP, read PPE Master (PPE_MASTER_DOC_ID from .env.mcp)
and summarize the first section. Do not write to PPE Master; see GOOGLE_DOCS_CONTROL_PLANE_V1.md.
```

If tools are disabled by default, approve the MCP tool when prompted, or enable auto-run for that server in MCP settings.

**Useful tools** (from the upstream server): `readDocument`, `appendText`, `findAndReplace`, etc. Prefer read-only workflows until you trust write behavior.

---

## Sharing with other LLMs

| Goal | Approach |
|------|----------|
| Another app on **this PC** (Claude Desktop, etc.) | Same `npx` command + OAuth token path, or duplicate the `mcp.json` entry in that app’s config |
| **Another machine** | Run `npx ... auth` on that machine, or deploy the server’s **HTTP** mode (see upstream “Remote Deployment”) and point clients at the URL |
| **Cloud / unattended agents** | HTTP deployment only; stdio does not run on Cursor cloud VMs |

The doc must be shared with (or owned by) the **same Google account** you used in Step 4.

---

## Windows: PowerShell blocks `npx` / `npm`

If you see:

```text
npx.ps1 cannot be loaded because running scripts is disabled on this system
```

**Node is installed** (`node --version` works). PowerShell is blocking the `.ps1` shims.

**Fix A (recommended, once per user):** in PowerShell:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Close and reopen PowerShell, then:

```powershell
npx --version
npm -v
```

**Fix B (no policy change):** use the `.cmd` shims:

```powershell
npx.cmd --version
npm.cmd -v
```

For Google auth, use `npx.cmd` instead of `npx`:

```powershell
npx.cmd -y @a-bonus/google-docs-mcp auth
```

**Do not use Docker** for this setup unless you already run Docker Desktop. The nodejs.org “Docker” tab is optional; native Windows Node is enough.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| MCP log: `'npx' is not recognized` | Cursor’s PATH often omits Node. Project `.cursor/mcp.json` uses `scripts/google_docs_mcp_launcher.ps1`. Reload window. |
| `readDocument` permission denied but Drive search finds the file | Common with Workspace policies. Ask the agent to use **`downloadFile`** with `exportMimeType=text/markdown` and `extractText=true` (exports via Drive API). |
| `npx.ps1` / scripts disabled (Windows) | See **Windows: PowerShell blocks npx** above |
| MCP server fails to start | Output → **MCP Logs**; confirm `npx.cmd` works in a terminal |
| `invalid_client` | Client ID/secret mismatch; recreate Desktop OAuth client |
| `access_denied` / consent | Add your email as OAuth test user; publish consent screen if needed |
| Agent cannot see doc | Doc not in authorized account; share doc with that Google user |
| Token expired | Re-run `npx -y @a-bonus/google-docs-mcp auth` |
| Too many tools / noisy | Disable **google-docs** in MCP settings when not needed |

---

## Why not share client secret in chat?

The client ID + secret do **not** grant access to one document. They identify **your OAuth app** to Google. Access to a specific doc still requires:

1. You (or a service account) completing **browser OAuth** once, and  
2. That Google account being allowed to open the doc.

Putting the secret in chat is risky because:

- Chat history can be stored, synced, or shared beyond your machine.
- Anyone with the secret can impersonate your OAuth app and phish for tokens.
- The agent does **not** need the secret in chat — it uses **MCP tools** after **you** run auth locally; credentials stay in `.env.mcp` + `~/.config/google-docs-mcp/token.json`.

Sharing the **document ID** in chat is fine. Sharing the **rotated secret** only in `.env.mcp` is the right model.

---

## Security notes

- Do not commit `.env.mcp`, OAuth client JSON, or service account keys.
- The MCP server can access **all** Docs/Drive files your Google account can access unless you use a limited account.
- For production-style multi-tenant access, use upstream **Cloud Run** deployment and team OAuth, not shared refresh tokens on a laptop.

---

## Related

- **Doc roles (MSOS vs Master):** [`GOOGLE_DOCS_CONTROL_PLANE_V1.md`](GOOGLE_DOCS_CONTROL_PLANE_V1.md)
- Cursor MCP docs: https://cursor.com/docs/context/mcp
- Project config: `.cursor/mcp.json`
- Example env: `.env.mcp.example`
