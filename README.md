# FM2C configurator artefacts

This repository contains the static GitHub Pages artefacts for the generated configurator prototypes. Each subdirectory is a rendered React/Vite application with seven generated views.

The views were generated with an MCP-enabled coding agent. The required generation files are included in this repository so the artefact can be published and reused without access to any other local directory.

## Included replication files

| Path | Purpose |
|---|---|
| `AGENTS.md` | Main agent instructions used for the software/SPL configurators. |
| `<config>/AGENTS.md` | The specific AGENTS.md used to generate each published configurator, copied into the configuration's own folder (see `firefox/AGENTS.md`, `docker/AGENTS.md`, `linux-kernel/AGENTS.md`, `windows-settings/AGENTS.md`, `windows-kernel/AGENTS.md`, `sandwich/AGENTS.md`, and `mcp/AGENTS.md`). The `sandwich/` one is the modified non-software variant; `mcp/AGENTS.md` documents the MCP server itself rather than a configurator. |
| `agent/` | Snapshot of the `pi` coding-agent configuration that drove generation (`APPEND_SYSTEM.md`, `prompts/orchestrator.md`, `prompts/worker.md`, `settings.json`, `mcp.json`). Secrets are excluded via `agent/.gitignore`. See `agent/README.md`. |
| `.mcp.json` | MCP server configuration for the local React/Vite setup server. |
| `mcp/` | Local MCP server used to scaffold and check React/Vite projects. |
| `Documentation/documentation.md` | Notes from the earlier documented generation attempts. |

## MCP server configuration

The repository-local MCP configuration is:

```json
{
  "mcpServers": {
    "react-vite-setup": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "fastmcp",
        "fastmcp",
        "run",
        "mcp/main.py"
      ]
    }
  }
}
```

The MCP server creates React/Vite projects under the current repository root. It does not require paths outside this repository.

## Prompt template

For each generated configurator, the prompt followed this structure:

```text
Follow <config>/AGENTS.md. Create a configurator for <software>. Here is more information: <settings file>.
```

`<software>` was replaced with the target system. `<settings file>` was replaced with the relevant source file, screenshot, UVL model, or textual settings description.

For the Sandwich Maker, the same workflow was used with `sandwich/AGENTS.md` (the food-domain variant of the standard SPL template). The prompt template was edited so it did not focus on software product lines, software constraints, or software-specific terminology.

## Published artefacts

| Published path | Generated configurator | Source information used |
|---|---|---|
| `/firefox/` | Firefox `user.js` configurator | Firefox preferences/profile settings, including `firefox/prefs.js` |
| `/docker/` | Docker Compose SPL configurator | Docker Compose/service configuration information for nginx, Node.js, and PostgreSQL services |
| `/linux-kernel/` | Linux kernel SPL configurator | `linux-kernel/linux-2.6.33.3.uvl` |
| `/windows-settings/` | Windows settings configurator | Windows settings source data, exported as a settings-style configuration file |
| `/windows-kernel/` | Windows kernel SPL visualiser | Windows kernel subsystem/module reference information |
| `/sandwich/` | Sandwich maker configurator | Sandwich ingredient/options description with the modified non-software instructions |

## Replication procedure

1. Clone or unpack this repository.
2. Configure an MCP-capable coding agent with `.mcp.json` (OpenCode, Claude, Codex, Antigravity, ...). For an exact re-run, point the agent at `agent/` (the `pi` agent home used during generation).
3. Provide the agent with the per-configuration `AGENTS.md` from the relevant `<config>/AGENTS.md` (or with the repository-root `AGENTS.md` for the standard SPL targets).
4. Provide the relevant source artefact for the target configurator.
5. Run the prompt template with the target software name, the chosen `<config>/AGENTS.md`, and the settings source.
6. Let the agent generate the React/Vite application and its seven views.
7. Build the generated project:

```bash
npm install
npm run build
```

Check VM
 pi --session 019ef9dd-a913-7925-b041-d6cb12ae788d
 
Check Docker
 pi --session 019ef9e3-96ef-7d2d-817b-69ad6ef828c0