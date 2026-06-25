# FM2Conf

Configurator artefacts and replication package for software (and non-software) product-line prototypes generated with an MCP-enabled coding agent.

Each subdirectory is a rendered React/Vite application with seven generated views, complete with module selection and configuration output.

The required generation files are included in this repository so the artefact can be published and reused without access to any other local directory.

## Included replication files

| Path | Purpose |
|---|---|
| `AGENTS.md` | Main agent instructions used for the software/SPL configurators. |
| `<config>/AGENTS.md` | The specific AGENTS.md used to generate each published configurator (e.g. `firefox/AGENTS.md`, `docker/AGENTS.md`, `linux-kernel/AGENTS.md`, `windows-settings/AGENTS.md`, `windows-kernel/AGENTS.md`, `sandwich/AGENTS.md`). The `sandwich/` one is the modified non-software variant; `mcp/AGENTS.md` documents the MCP server itself. |
| `agent/` | Complete `pi` agent configuration snapshot. Includes prompts, extensions, skills, and settings. See `agent/README.md` for setup instructions. |
| `.mcp.json` | MCP server configuration for the local React/Vite setup server. |
| `mcp/` | Local MCP server used to scaffold and check React/Vite projects. |
| `Documentation/documentation.md` | Notes from earlier generation attempts. |

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

## Published artefacts

| Published path | Generated configurator | Source information used |
|---|---|---|
| `/firefox/` | Firefox `user.js` configurator | Firefox preferences/profile settings, including `firefox/prefs.js` |
| `/docker/` | Docker Compose SPL configurator | Docker Compose/service configuration information for nginx, Node.js, and PostgreSQL services |
| `/linux-kernel/` | Linux kernel SPL configurator | `linux-kernel/linux-2.6.33.3.uvl` |
| `/windows-settings/` | Windows settings configurator | Windows settings source data, exported as a settings-style configuration file |
| `/windows-kernel/` | Windows kernel SPL visualiser | Windows kernel subsystem/module reference information |
| `/sandwich/` | Sandwich maker configurator | Sandwich ingredient/options description with the modified non-software instructions |

## Replication

### 1. Set up the agent

Follow the instructions in [`agent/README.md`](agent/README.md) to install `pi` and apply the replication configuration.

### 2. Generate a new configurator

1. Clone this repository.
2. Point `pi` at `agent/` as your agent home (see `agent/README.md`).
3. Provide the relevant `AGENTS.md` — use `AGENTS.md` from the repo root for SPL targets, or `<config>/AGENTS.md` for customised variants (e.g. `sandwich/AGENTS.md`).
4. Run:

   ```text
   Follow AGENTS.md. Create a configurator for <software>. Here is more information: <settings file>.
   ```

5. Let the agent generate the project, then build:

   ```bash
   npm install
   npm run build
   ```