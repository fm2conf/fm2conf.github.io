# pi agent config (replication)

This directory contains the `pi` agent configuration used to generate the configurators in this repository. Use it to replicate the setup on your own machine.

## Source

The files here were copied verbatim from `~/.pi/agent2/` on the generation host. Sensitive material (API keys, OAuth tokens, session logs) is intentionally **not** included — see `.gitignore` in this folder for the full exclusion list.

## Files

| Path | Purpose |
|---|---|
| `APPEND_SYSTEM.md` | Extra system-prompt block appended to every `pi` session (kanban / MCP rules, edit-tool formatting, Chrome DevTools reliability, etc.). |
| `prompts/orchestrator.md` | Operating-mode prompt used when `pi` is run as the top-level coordinator that decomposes work and spawns sub-agents. |
| `prompts/worker.md` | Operating-mode prompt used when `pi` is spawned as an implementation-focused sub-agent. |
| `settings.json` | Non-secret agent settings: default provider / model, theme, installed packages, default thinking level. |
| `mcp.json` | MCP server definitions available to the agent (here: `chrome-devtools`). |
| `.gitignore` | Lists the agent2 sub-paths that are intentionally **not** shipped in this repository (auth, sessions, caches, secrets). |

## How it was used

1. The user pointed their `pi` install at `~/.pi/agent2/` as the active agent home.
2. The MCP server in `mcp/` (this repository) was registered via the repository's `.mcp.json`.
3. For each configurator, the user ran the orchestrator with a prompt of the form:

   ```text
   Follow AGENTS.md. Create a configurator for <software>. Here is more information: <settings file>.
   ```

4. The orchestrator then either implemented the work itself or, for tasks that ran longer than a few minutes, decomposed it and spawned one or more worker `pi` instances using the prompts above.


## Installing pi

1. Install `pi` officially following the [installation guide](https://github.com/offline-ant/pi).
2. Once installed, overwrite your agent directory with this replication package:

   ```bash
   cp -r agent/ ~/.pi/agent
   ```

3. Start `pi` — it will pick up the settings, prompts, and extensions from `~/.pi/agent/`.
The `APPEND_SYSTEM.md` content is what each `pi` session sees in addition to its base system prompt; the orchestrator and worker `.md` files are the role-specific bodies that switch the agent into manager vs. implementer mode.
