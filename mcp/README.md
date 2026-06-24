# MCP server — React/Vite Setup

This folder contains the local MCP server that the `pi` coding agent used to scaffold and validate the React + Vite projects behind every published configurator in this repository.

## Contents

| Path | Purpose |
|---|---|
| `main.py` | FastMCP server (`ReactViteSetup`). Exposes the `setup`, `install_deps`, `run_dev`, `lint_check`, `build_check`, and related tools the agent calls during generation. |
| `pyproject.toml`, `uv.lock`, `.python-version` | Python project definition and lockfile. Run with `uv run --with fastmcp fastmcp run mcp/main.py`. |
| `.agents/skills/vercel-react-best-practices/` | Vercel React/Next.js best-practices rules (AGENTS.md + per-rule .md files), loaded into the agent by `SkillsDirectoryProvider`. |
| `.agents/skills/web-design-guidelines/` | Vercel Web Interface Guidelines review skill. |
| `skills-lock.json` | Pins the exact skill revisions so the agent sees consistent rules across runs. |
| `AGENTS.md` | How this server fits into replication — which tools and skills each agent used while generating a configurator. |

## Usage

The server is already wired up via the repository-root `.mcp.json`:

```json
{
  "mcpServers": {
    "react-vite-setup": {
      "command": "uv",
      "args": ["run", "--with", "fastmcp", "fastmcp", "run", "mcp/main.py"]
    }
  }
}
```

Any MCP-capable coding agent (OpenCode, Claude, Codex, Antigravity, etc.) that is started with this `.mcp.json` in scope will pick up the `react-vite-setup` tools and the bundled skills automatically.

See `AGENTS.md` in this folder for the full list of tools and skills, and the role each played during configurator generation.