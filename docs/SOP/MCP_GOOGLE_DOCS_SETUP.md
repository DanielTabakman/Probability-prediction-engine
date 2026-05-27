# MCP_GOOGLE_DOCS_SETUP

Purpose: enable the **google-docs MCP** server for Cursor agents in this repo.

## Files

### `.cursor/mcp.json`

This repo configures the server like:

- command: `npx -y @a-bonus/google-docs-mcp`
- envFile: `${workspaceFolder}/.env.mcp`

### `.env.mcp` (local only; never commit)

Create a local `.env.mcp` at repo root with the required credentials for the google-docs MCP server.

**Do not commit** `.env.mcp` (or any `.env*` file). It may contain secrets.

## Quick verification

In Cursor, a working setup should allow the agent to:

- list/search Drive docs (read path)
- read the PPE Master doc (read-only policy)
- update the MSOS mirror doc’s marker block (write path)

Policy and refresh workflow: see [`GOOGLE_DOCS_CONTROL_PLANE_V1.md`](GOOGLE_DOCS_CONTROL_PLANE_V1.md).

## One-time GitHub secrets (automatic)

If Google Docs MCP already works in Cursor, your refresh token is stored locally at:

- `%USERPROFILE%\.config\google-docs-mcp\token.json`

From repo root, run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/set_google_docs_secrets_once.ps1
```

This reads `.env.mcp` + the MCP token file and sets GitHub secrets (no manual copy/paste).

If MCP is not authorized yet, run once (browser opens):

```bash
npx -y @a-bonus/google-docs-mcp auth
```

Then re-run the PowerShell script above.

