# FM2C configurator artefacts

This repository contains the static GitHub Pages artefacts for the generated configurator prototypes. Each subdirectory is a rendered React/Vite application with seven generated views.

The views were generated with an MCP-enabled coding agent. The required generation files are included in this repository so the artefact can be published and reused without access to any other local directory.

## Included replication files

| Path | Purpose |
|---|---|
| `AGENTS.md` | Main agent instructions used for the software/SPL configurators. |
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
Follow AGENTS.md. Create a configurator for <software>. Here is more information: <settings file>.
```

`<software>` was replaced with the target system. `<settings file>` was replaced with the relevant source file, screenshot, UVL model, or textual settings description.

For the Sandwich Maker, the same workflow was used, but the instruction text was edited so it did not focus on software product lines, software constraints, or software-specific terminology.

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
2. Configure an MCP-capable coding agent with `.mcp.json` (OpenCode, Claude, Codex, Antigravity, ...)
3. Provide the agent with `AGENTS.md` from this repository.
4. Provide the relevant source artefact for the target configurator.
5. Run the prompt template with the target software name and settings source.
6. Let the agent generate the React/Vite application and its seven views.
7. Build the generated project:

```bash
npm install
npm run build
```
