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

