# AGENTS.md — React/Vite Setup MCP Server

This folder is **not** a generated configurator like the others in this repository. It is the **MCP server that every agent used during generation** to scaffold and check the React + Vite projects behind the published `firefox/`, `docker/`, `linux-kernel/`, `windows-settings/`, `windows-kernel/`, and `sandwich/` artefacts.

The server is registered in the repository's `.mcp.json` under the name `react-vite-setup`, and is launched as:

```bash
uv run --with fastmcp fastmcp run mcp/main.py
```

## What the server provides to the agent

`mcp/main.py` (FastMCP) exposes three categories of functionality:

1. **Project scaffolding tools** — `setup` (scaffold a new React + TypeScript + Vite project), `install_deps` (run `npm install`), `run_dev` (start the Vite dev server). These let the agent create and run a new project directly, with no copy-paste from a terminal.
2. **Code-review tools** — `lint_check`, `build_check`, and similar utilities the agent can call after writing code to confirm the generated project still passes `eslint` and `vite build`.
3. **Agent skills** — mounted via `SkillsDirectoryProvider` from `mcp/.agents/skills/`. Each skill is an `AGENTS.md` / `SKILL.md` pair that the agent automatically picks up and applies when relevant. The two skills shipped here are:
   - `vercel-react-best-practices` — Vercel's React / Next.js performance and structure rules (see `mcp/.agents/skills/vercel-react-best-practices/AGENTS.md`, 40+ rules across 8 categories).
   - `web-design-guidelines` — Vercel's Web Interface Guidelines review skill (see `mcp/.agents/skills/web-design-guidelines/SKILL.md`).
   - The lockfile `mcp/skills-lock.json` pins the exact revisions of these skills so the agent sees the same rules across runs.

## How it was used during generation

For each published configurator, the agent:

1. Called `setup(name="<config>")` to scaffold a fresh React + TypeScript + Vite project under this repository root (so paths like `firefox/`, `docker/`, etc. were created as the scaffold landed).
2. Read the relevant `AGENTS.md` (the one in `<config>/AGENTS.md` and the repository-root `AGENTS.md`) and the input source (prefs.js, UVL model, INI file, etc.).
3. Wrote the 7 (or 3) views, the shared `src/config/schema.*`, and the per-view bundles, applying the rules in `mcp/.agents/skills/vercel-react-best-practices/AGENTS.md` as it went.
4. Called the MCP review tools to confirm the generated project still lints and builds.
5. Ran `npm run build` to produce the static `dist/` / `assets/` output that is now committed under each `<config>/` folder.

## Reusing it for replication

To re-run a configurator generation with this MCP server:

```bash
# 1. Register the MCP server (already done in this repository's .mcp.json)
# 2. Launch your MCP-capable coding agent against the repository root.
# 3. Provide the agent with the target <config>/AGENTS.md.
# 4. Run the prompt template from the repository root README.
# 5. The agent will call mcp.setup() to create the project, then
#    mcp.lint_check() / mcp.build_check() before publishing the dist output.
```

The server itself is hermetic — it only writes under the repository root and pulls the skill set from `mcp/.agents/skills/`. No external paths, no secrets, no remote services.
