# Tana connector

This repository prepares a **least-privilege Codex tool surface** for Tana's
hosted MCP server. The connection is project-scoped, uses Tana's OAuth flow, and
does not store a Tana token in the repository.

> [!IMPORTANT]
> Tana does not currently advertise separate read and write OAuth scopes. Its
> live OAuth metadata lists only `openid`, `profile`, and `offline_access`.
> Therefore the token itself is **not guaranteed to be read-only**. This repo
> restricts Codex with an explicit tool allow-list. Do not complete OAuth if
> read-only must be enforced by Tana itself.

## Connect

1. Trust/open this repository in the ChatGPT desktop app, Codex CLI, or the Codex
   IDE extension.
2. Restart the client so it loads [`.codex/config.toml`](.codex/config.toml).
3. If client-side read-only enforcement is sufficient, authenticate the `tana`
   MCP server:

   ```powershell
   codex mcp login tana
   ```

   Alternatively, open the client's **MCP servers** settings and choose
   **Authenticate** beside `tana`.
4. Complete Tana's browser-based OAuth flow.
5. Start a new Codex session and verify the connection:

   ```powershell
   codex mcp list
   ```

Then try: `Search Tana for my most recently updated documents.`

Tana exposes both read and write tools. This project's `enabled_tools` list makes
its documented search, read, schema, graph, transcript, event, and
calendar-listing tools available, plus `createItems` for the repository import.
No update, delete, move, access-control, or proposal-approval tool is exposed.

## If you meant Tana Outliner

Tana Outliner uses a different MCP server hosted by its desktop app. Keep Tana
Outliner Desktop open, then replace the URL in `.codex/config.toml` with:

```toml
[mcp_servers.tana]
url = "http://localhost:8262/mcp"
auth = "oauth"
enabled_tools = [
  "list_workspaces",
  "search_nodes",
  "read_node",
  "get_children",
  "list_tags",
  "get_tag_schema",
]
```

The local service can be checked at `http://localhost:8262/health`. After
changing the URL, restart Codex and run `codex mcp login tana`. Tana Outliner
will show an approval dialog before browser confirmation.

## Troubleshooting

- Server missing: make sure the repository is trusted, then restart the Codex
  client and run `codex mcp list`.
- OAuth is required: run `codex mcp login tana` or use **Authenticate** in MCP
  settings.
- Strict read-only OAuth required: stop here; Tana's hosted MCP does not
  currently advertise a read-only API scope. The tool allow-list is a Codex-side
  control only.
- Outliner connection refused: open the latest Tana Outliner Desktop app and
  load the workspace you want Codex to access.
- Tools are not visible in an existing chat: start a new session after changing
  MCP configuration.

## References

- [Tana hosted MCP documentation](https://tana.inc/learn/features/mcp)
- [Tana Outliner Local API/MCP documentation](https://outliner.tana.inc/learn/features/local-api-mcp)
- [Codex MCP configuration documentation](https://developers.openai.com/codex/mcp)
