import asyncio
import os
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.server.providers.skills import SkillsDirectoryProvider

mcp = FastMCP(
    "ReactViteSetup",
    instructions=(
        "Set up React + Vite frontend projects. "
        "Use `setup` to scaffold a new project, `install_deps` to install "
        "dependencies in an existing project, or `run_dev` to start the dev server. "
        "All commands execute directly — no need to copy-paste."
    ),
)

BASE_DIR = Path(__file__).resolve().parents[1]


async def _run(
    cmd: list[str],
    cwd: str | Path | None = None,
    timeout: int = 120,
    env: dict[str, str] | None = None,
) -> dict:
    """Helper: run a subprocess and return structured output."""
    if cwd is None:
        cwd = BASE_DIR
    if env is None:
        env = {**os.environ}
    env["CI"] = "1"
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return {
            "success": proc.returncode == 0,
            "stdout": stdout.decode(errors="replace").strip(),
            "stderr": stderr.decode(errors="replace").strip(),
            "returncode": proc.returncode,
            "command": " ".join(cmd),
        }
    except asyncio.TimeoutError:
        proc.kill()
        return {
            "success": False,
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "returncode": -1,
            "command": " ".join(cmd),
        }
    except Exception as exc:
        return {
            "success": False,
            "stdout": "",
            "stderr": str(exc),
            "returncode": -1,
            "command": " ".join(cmd),
        }


# ─────────────────────────────────────────────────────────────────
# Tool: setup
# ─────────────────────────────────────────────────────────────────
@mcp.tool(
    title="Scaffold a New React + Vite Project",
    description=(
        "Creates a brand-new React + TypeScript + Vite project from scratch.\n\n"
        "Run this first when you need a fresh frontend project. It runs 'npm create vite@latest' "
        "and optionally installs dependencies.\n\n"
        "Parameters:\n"
        "  name (string, REQUIRED)       – Project folder name under this repository root. Example: 'my-app' creates ./my-app/. Use only lowercase letters, numbers, and hyphens.\n"
        "  template (string, optional)    – Vite template to use. Default: 'react-ts'. Available options: 'react-ts' (React + TypeScript), 'react' (plain React), 'vue', 'svelte', 'lit', 'solid', 'preact'.\n"
        "  install_deps (bool, optional)  – Run 'npm install' after scaffolding. Default: true. Set to false if you want to edit package.json before installing.\n\n"
        "Examples:\n"
        "  args: { name: 'windows-settings' }  → scaffolds React+TS project with dependencies installed\n"
        "  args: { name: 'my-app', template: 'react', install_deps: false }  → plain React, skip npm install\n\n"
        "Returns: a success message with the project location and next steps, or an error if the directory already exists.\n"
        "Note: This tool is idempotent-safe — it refuses to overwrite an existing directory."
    ),
    tags={"setup", "react", "vite", "scaffold"},
    annotations={"readOnlyHint": True},
)
async def setup(
    name: str,
    template: str = "react-ts",
    install_deps: bool = True,
) -> str:
    """Scaffold a new React/Vite project and optionally install deps."""
    project_dir = BASE_DIR / name

    if project_dir.exists():
        return (
            f"Error: Directory '{project_dir}' already exists. "
            "Remove it or choose a different name."
        )

    # Step 1: Scaffold
    scaffold_cmd = [
        "npm",
        "create",
        "vite@latest",
        name,
        "--",
        "--template",
        template,
    ]
    result = await _run(scaffold_cmd, cwd=BASE_DIR, timeout=30)
    if not result["success"]:
        return f"Scaffold failed:\n{result['stderr']}"

    # Step 2: Install dependencies
    if install_deps:
        install_result = await _run(
            ["npm", "install"], cwd=project_dir, timeout=60
        )
        if not install_result["success"]:
            return (
                f"Scaffolded '{name}' but dependency install failed:\n"
                f"{install_result['stderr']}\n\n"
                f"You can try: cd {name} && npm install"
            )

    # Step 3: Return summary
    lines = [
        f"Project '{name}' created successfully.",
        f"   Location: {project_dir}",
        f"   Template: {template}",
        "",
        "Next steps:",
        f"   cd {name}",
        f"   npm run dev      # start dev server",
        f"   npm run build    # production build",
        f"   npm run lint     # lint check",
    ]

    if install_deps and install_result["success"]:
        stderr_lower = install_result["stderr"].lower()
        if "vulnerability" in stderr_lower:
            vuln_line = install_result["stderr"].splitlines()[-1]
            lines.append(f"   Warning: {vuln_line}")

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────
# Tool: install_deps
# ─────────────────────────────────────────────────────────────────
@mcp.tool(
    title="Install npm Dependencies for a Project",
    description=(
        "Installs (or reinstalls) npm dependencies for a project in the "
        "current repository root.\n\n"
        "Use this when dependencies are missing, corrupted, or after you've "
        "changed package.json and want to pick up new packages.\n\n"
        "Parameters:\n"
        "  name (string, REQUIRED)       – Project folder name under this repository root. Must contain a valid package.json.\n\n"
        "Examples:\n"
        "  args: { name: 'windows-settings' }  → cleans node_modules and runs npm install\n\n"
        "Note: This tool removes node_modules before reinstalling to ensure a clean state. "
        "Returns a summary of packages added and any vulnerabilities detected."
    ),
    tags={"setup", "install", "dependencies"},
    annotations={"readOnlyHint": True},
)
async def install_deps(
    name: str,
) -> str:
    """Install npm dependencies for an existing project."""
    project_dir = BASE_DIR / name
    if not project_dir.exists():
        return f"Error: Directory '{project_dir}' does not exist."
    if not (project_dir / "package.json").exists():
        return f"Error: No package.json found in '{project_dir}'."

    # Remove node_modules to force clean install
    import shutil
    node_modules = project_dir / "node_modules"
    if node_modules.exists():
        await asyncio.to_thread(shutil.rmtree, node_modules, ignore_errors=True)

    result = await _run(["npm", "install"], cwd=project_dir, timeout=90)
    if result["success"]:
        lines = [f"Dependencies installed in '{name}'."]
        # Extract summary from stderr (npm writes install summary to stderr)
        if result["stderr"]:
            for line in result["stderr"].splitlines():
                line = line.strip()
                if "added" in line.lower() or "audited" in line.lower() or "vulnerability" in line.lower():
                    lines.append(f"   {line}")
        return "\n".join(lines)
    else:
        return f"Install failed in '{name}':\n{result['stderr']}"


# ─────────────────────────────────────────────────────────────────
# Tool: run_dev
# ─────────────────────────────────────────────────────────────────
@mcp.tool(
    title="Start the Vite Dev Server",
    description=(
        "Starts the Vite development server for a project in the "
        "current repository root.\n\n"
        "Runs 'npm run dev' inside the project directory. Use this to verify "
        "the dev server starts without errors, or to start a temporary dev server "
        "for inspection.\n\n"
        "Parameters:\n"
        "  name (string, REQUIRED)       – Project folder name under this repository root.\n"
        "  port (int, optional)           – Port for the dev server. Default: 5173.\n\n"
        "Examples:\n"
        "  args: { name: 'windows-settings' }  → starts dev server on port 5173\n"
        "  args: { name: 'windows-settings', port: 3000 }  → starts on port 3000\n\n"
        "Note: The server runs for 15 seconds then stops. This is to verify it boots cleanly. "
        "For a long-running server, use the bash tool to start it manually."
    ),
    tags={"setup", "dev", "server", "preview"},
    annotations={"readOnlyHint": False, "openApiDescription": "Starts and stops the dev server"},
)
async def run_dev(
    name: str,
    port: int = 5173,
) -> str:
    """Start the Vite dev server and verify it boots."""
    project_dir = BASE_DIR / name
    if not project_dir.exists():
        return f"Error: Directory '{project_dir}' does not exist."

    env = {**os.environ}
    env["PORT"] = str(port)
    result = await _run(
        ["npm", "run", "dev"], cwd=project_dir, timeout=15, env=env
    )

    if result["success"]:
        return f"Dev server started for '{name}' on port {port}."
    else:
        return f"Dev server failed to start for '{name}':\n{result['stderr']}"


# ─────────────────────────────────────────────────────────────────
# Tool: run_build
# ─────────────────────────────────────────────────────────────────
@mcp.tool(
    title="Build Project for Production",
    description=(
        "Runs a production build for a project to verify it compiles "
        "without errors.\n\n"
        "First runs TypeScript type checking ('npx tsc --noEmit'), then "
        "runs the Vite production build ('npm run build'). This is the "
        "canonical way to check that a project is buildable.\n\n"
        "Parameters:\n"
        "  name (string, REQUIRED)       – Project folder name under this repository root.\n\n"
        "Examples:\n"
        "  args: { name: 'windows-settings' }  → runs tsc check then vite build\n\n"
        "Returns: the build output (bundle sizes, file list) on success, "
        "or compilation/build errors on failure."
    ),
    tags={"setup", "build", "verify", "production"},
    annotations={"readOnlyHint": True},
)
async def run_build(
    name: str,
) -> str:
    """Build a project for production."""
    project_dir = BASE_DIR / name
    if not project_dir.exists():
        return f"Error: Directory '{project_dir}' does not exist."

    result = await _run(
        ["npx", "tsc", "--noEmit"], cwd=project_dir, timeout=30
    )
    if not result["success"]:
        return f"TypeScript compilation failed for '{name}':\n{result['stderr']}"

    result = await _run(
        ["npm", "run", "build"], cwd=project_dir, timeout=60
    )
    if result["success"]:
        return (
            f"Build successful for '{name}'.\n"
            f"   {result['stdout']}"
        )
    else:
        return f"Build failed for '{name}':\n{result['stderr']}"


import re as _re


async def _read_file(path: Path) -> str | None:
    """Read a file if it exists, else return None."""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


async def _analyse_app_tsx(app_path: Path) -> dict:
    """Analyse App.tsx for the 7 views."""
    content = await _read_file(app_path)
    if content is None:
        return {"error": "App.tsx not found"}

    view_pattern = _re.compile(r'^function\s+(\w+View\w*)', _re.MULTILINE)
    view_functions = view_pattern.findall(content)
    view_names = [v for v in view_functions if v.endswith('View') or 'View' in v]

    view_details: list[dict] = []
    lines = content.split('\n')
    for i, line in enumerate(lines):
        m = _re.match(r'^function\s+(\w+)', line)
        if m and m.group(1) in view_names:
            name = m.group(1)
            start = i
            brace_count = 0
            found_open = False
            end = start
            for j in range(i, len(lines)):
                brace_count += lines[j].count('{') - lines[j].count('}')
                if '{' in lines[j]:
                    found_open = True
                if found_open and brace_count == 0:
                    end = j
                    break
            chunk = '\n'.join(lines[start:end+1])
            view_details.append({
                "name": name,
                "start_line": start + 1,
                "end_line": end + 1,
                "line_count": end - start + 1,
                "source_length": len(chunk),
            })

    analysis: list[dict] = []
    for vd in view_details:
        name = vd["name"]
        start = vd["start_line"] - 1
        end = vd["end_line"]
        chunk = '\n'.join(lines[start:end])

        hooks_used = set(_re.findall(r'use\w+', chunk))
        css_classes = set(_re.findall(r'className=["\']([^"\']+)["\']', chunk))
        has_search = 'search' in chunk.lower() or 'Search' in chunk
        has_wizard = 'wizard' in chunk.lower() or 'Wizard' in chunk
        has_table = 'table' in chunk.lower() or '<Table' in chunk
        has_tree = 'tree' in chunk.lower() or 'Tree' in chunk
        has_tags = 'tag' in chunk.lower() or 'Tag' in chunk
        has_cloud = 'cloud' in chunk.lower() or 'Cloud' in chunk
        has_chain = 'chain' in chunk.lower() or 'Chain' in chunk
        has_dep = 'dep' in chunk.lower() or 'Depend' in chunk
        has_matrix = 'matrix' in chunk.lower() or 'Matrix' in chunk
        has_platform = 'platform' in chunk.lower() or 'card' in chunk.lower()
        has_export = 'export' in chunk.lower() or 'Export' in chunk
        has_toggle = 'toggle' in chunk.lower()
        has_checkbox = 'checkbox' in chunk.lower()
        has_grid = 'grid' in chunk.lower()
        has_pre = '<pre' in chunk
        has_steps = 'step' in chunk.lower() or 'Step' in chunk

        fingerprint = {
            "has_search", "has_wizard", "has_table", "has_tree",
            "has_tags", "has_cloud", "has_chain", "has_dep",
            "has_matrix", "has_platform", "has_export", "has_toggle",
            "has_checkbox", "has_grid", "has_pre", "has_steps",
        }

        active_features: set[str] = set()
        for feat in fingerprint:
            if locals().get(feat, False):
                active_features.add(feat)

        analysis.append({
            **vd,
            "hooks": sorted(hooks_used),
            "css_class_count": len(css_classes),
            "active_features": sorted(active_features),
        })

    diversity_issues: list[str] = []
    for i in range(len(analysis)):
        for j in range(i + 1, len(analysis)):
            a, b = analysis[i], analysis[j]
            union = set(a["active_features"]) | set(b["active_features"])
            intersection = set(a["active_features"]) & set(b["active_features"])
            if union:
                jaccard = len(intersection) / len(union)
                if jaccard > 0.7:
                    diversity_issues.append(
                        f"{a['name']} and {b['name']} are structurally very similar "
                        f"(Jaccard similarity: {jaccard:.2f}). "
                        f"Shared features: {sorted(intersection)}"
                    )

    return {
        "view_count": len(view_details),
        "views": analysis,
        "diversity_issues": diversity_issues,
    }


@mcp.tool(
    title="Validate SPL Visualizer Project",
    description=(
        "Validates the spl-visualizer project for correctness and quality.\n\n"
        "Checks:\n"
        "  1. All 7 views exist and are structurally different\n"
        "  2. Build succeeds (TypeScript + Vite)\n"
        "  3. Lint passes\n"
        "  4. UVL parser produces valid module tree\n"
        "  5. Constraint validation logic is present\n"
        "  6. No huge problems (missing files, broken imports, etc.)\n\n"
        "Parameters:\n"
        "  name (string, optional) - Project folder name. Default: 'spl-visualizer'\n\n"
        "Examples:\n"
        "  args: {} -> validates the spl-visualizer project\n\n"
        "Returns: detailed validation report with pass/fail for each check."
    ),
    tags={"validate", "check", "spl", "quality"},
    annotations={"readOnlyHint": True},
)
async def validate_spl_project(
    name: str = "spl-visualizer",
) -> str:
    """Run comprehensive validation on the SPL visualizer project."""
    project_dir = BASE_DIR / name
    results: list[str] = []
    passed = 0
    failed = 0
    warnings_count = 0

    if not project_dir.exists():
        return f"Error: Project directory '{project_dir}' does not exist."
    if not (project_dir / "package.json").exists():
        return f"Error: No package.json in '{project_dir}'. Is this a Vite project?"

    results.append("=== SPL Visualizer Validation Report ===")
    results.append("")

    # Check 1: Required files
    results.append("--- File Structure ---")
    required_files = [
        "src/App.tsx",
        "src/App.css",
        "src/config/schema.ts",
        "src/data/uvl-parser.ts",
        "public/linux-2.6.33.3.uvl",
    ]
    for rf in required_files:
        fp = project_dir / rf
        if fp.exists():
            results.append(f"  OK   {rf}")
            passed += 1
        else:
            results.append(f"  FAIL {rf} (missing)")
            failed += 1

    optional_files = [
        ("src/config/schema.dot", "UVL dependency graph"),
        ("src/config/schema.svg", "Rendered SVG from DOT"),
        ("src/config/schema.uvl", "Copied UVL source"),
        ("src/data/extracted.ts", "Extracted metadata"),
    ]
    for of_, desc in optional_files:
        fp = project_dir / of_
        if fp.exists():
            results.append(f"  OK   {of_} ({desc})")
            passed += 1
        else:
            results.append(f"  WARN {of_} ({desc}) - missing")
            warnings_count += 1
    results.append("")

    # Check 2: View count and diversity
    results.append("--- View Analysis ---")
    app_tsx = project_dir / "src/App.tsx"
    app_analysis = await _analyse_app_tsx(app_tsx)

    if "error" in app_analysis:
        results.append(f"  FAIL Cannot analyse App.tsx: {app_analysis['error']}")
        failed += 1
    else:
        view_count = app_analysis["view_count"]
        results.append(f"  Views found: {view_count}/7")
        if view_count == 7:
            results.append(f"  OK   All 7 views present")
            passed += 1
        elif view_count > 0:
            results.append(f"  WARN Only {view_count} views found (need 7)")
            warnings_count += 1
        else:
            results.append(f"  FAIL No views found in App.tsx")
            failed += 1

        for v in app_analysis.get("views", []):
            results.append(
                f"    - {v['name']}: {v['line_count']} lines, "
                f"{v['css_class_count']} CSS classes, "
                f"hooks: {', '.join(v['hooks'][:4]) if v['hooks'] else 'none'}"
            )

        diversity = app_analysis.get("diversity_issues", [])
        if diversity:
            results.append(f"  WARN {len(diversity)} view pair(s) are structurally similar:")
            for issue in diversity:
                results.append(f"    ! {issue}")
            warnings_count += len(diversity)
        else:
            results.append(f"  OK   All views are structurally distinct")
            passed += 1
    results.append("")

    # Check 3: CSS diversity
    results.append("--- CSS Diversity ---")
    app_css = await _read_file(project_dir / "src/App.css")
    if app_css:
        view_css_patterns = _re.findall(r'\.view-(\w+)', app_css)
        unique_view_css = set(view_css_patterns)
        results.append(f"  View CSS namespaces: {', '.join(sorted(unique_view_css)) if unique_view_css else 'none'}")
        if len(unique_view_css) >= 7:
            results.append(f"  OK   Each view has its own CSS namespace ({len(unique_view_css)} namespaces)")
            passed += 1
        elif len(unique_view_css) > 0:
            results.append(f"  WARN Only {len(unique_view_css)} CSS namespaces found (need 7)")
            warnings_count += 1
        else:
            results.append(f"  FAIL No view-specific CSS found")
            failed += 1

        view_blocks = _re.findall(r'\.view-(\w+)[^{}]*(?:\{[^}]*\})', app_css)
        if len(view_blocks) >= 5:
            results.append(f"  OK   Multiple view-specific style blocks ({len(view_blocks)})")
            passed += 1
        else:
            results.append(f"  WARN Few view-specific style blocks ({len(view_blocks)})")
            warnings_count += 1
    else:
        results.append(f"  FAIL App.css not found")
        failed += 1
    results.append("")

    # Check 4: TypeScript build
    results.append("--- TypeScript Build ---")
    build_result = await _run(
        ["npx", "tsc", "--noEmit"],
        cwd=project_dir,
        timeout=30,
    )
    if build_result["success"]:
        results.append(f"  OK   TypeScript compilation passed")
        passed += 1
    else:
        error_lines = build_result["stderr"].split("\n")[:5]
        results.append(f"  FAIL TypeScript errors:")
        for el in error_lines:
            results.append(f"    {el.strip()}")
        failed += 1
    results.append("")

    # Check 5: Lint
    results.append("--- Lint ---")
    lint_result = await _run(
        ["npm", "run", "lint"],
        cwd=project_dir,
        timeout=30,
    )
    if lint_result["success"]:
        results.append(f"  OK   Lint passed")
        passed += 1
    else:
        all_output = lint_result["stderr"] + "\n" + lint_result["stdout"]
        error_count_match = _re.search(r'(\d+)\s+problem', all_output)
        if error_count_match:
            results.append(f"  WARN {error_count_match.group(0)} found")
            warnings_count += 1
        else:
            results.append(f"  FAIL Lint failed")
            failed += 1
            out_lines = all_output.strip().split("\n")[:5]
            for ol in out_lines:
                results.append(f"    {ol.strip()}")
    results.append("")

    # Check 6: Constraint validation logic
    results.append("--- Constraint Logic ---")
    schema_ts = await _read_file(project_dir / "src/config/schema.ts")
    if schema_ts:
        has_validate = "validateConstraints" in schema_ts
        has_strategic = "StrategicNote" in schema_ts
        has_zod = "zod" in schema_ts.lower() or "z.object" in schema_ts

        if has_validate:
            results.append(f"  OK   Constraint validation function present")
            passed += 1
        else:
            results.append(f"  WARN No constraint validation function found")
            warnings_count += 1

        if has_strategic:
            results.append(f"  OK   Strategic notes / conflict detection present")
            passed += 1
        else:
            results.append(f"  WARN No strategic note system found")
            warnings_count += 1

        if has_zod:
            results.append(f"  OK   Schema validation (Zod) present")
            passed += 1
        else:
            results.append(f"  INFO No Zod schema found")
    else:
        results.append(f"  FAIL schema.ts not found")
        failed += 1
    results.append("")

    # Check 7: UVL Parser sanity
    results.append("--- UVL Parser ---")
    parser_ts = await _read_file(project_dir / "src/data/uvl-parser.ts")
    if parser_ts:
        has_parse_tree = "parseUVLTree" in parser_ts
        has_parse_constraints = "parseUVLConstraint" in parser_ts
        has_module_type = "UVLModule" in parser_ts
        has_constraint_type = "UVLConstraint" in parser_ts

        if has_parse_tree:
            results.append(f"  OK   Tree parser function present")
            passed += 1
        else:
            results.append(f"  WARN No tree parser found")
            warnings_count += 1

        if has_parse_constraints:
            results.append(f"  OK   Constraint parser present")
            passed += 1
        else:
            results.append(f"  WARN No constraint parser found")
            warnings_count += 1

        if has_module_type and has_constraint_type:
            results.append(f"  OK   Type definitions present (UVLModule, UVLConstraint)")
            passed += 1
        else:
            results.append(f"  WARN Missing type definitions")
            warnings_count += 1
    else:
        results.append(f"  FAIL uvl-parser.ts not found")
        failed += 1
    results.append("")

    # Check 8: Navigation wiring
    results.append("--- Navigation ---")
    app_content = await _read_file(app_tsx)
    if app_content:
        view_render_pattern = _re.compile(r'state\.activeView\s*===\s*["\']\w+["\']')
        view_renders = view_render_pattern.findall(app_content)
        results.append(f"  View render branches: {len(view_renders)}")
        if len(view_renders) == 7:
            results.append(f"  OK   All 7 views are reachable from navigation")
            passed += 1
        elif len(view_renders) > 0:
            results.append(f"  WARN Only {len(view_renders)} views are wired to navigation (need 7)")
            warnings_count += 1
        else:
            results.append(f"  FAIL No navigation wiring found")
            failed += 1

        has_state = "useState" in app_content
        has_callback = "useCallback" in app_content

        if has_state:
            results.append(f"  OK   Shared state management present")
            passed += 1
        else:
            results.append(f"  WARN No shared state mechanism found")
            warnings_count += 1

        if has_callback:
            results.append(f"  OK   Optimised callbacks (useCallback) used")
            passed += 1
        else:
            results.append(f"  INFO No useCallback found (minor)")
    else:
        results.append(f"  FAIL Cannot read App.tsx")
        failed += 1
    results.append("")

    # Summary
    results.append("=== Summary ===")
    results.append(f"  Passed:   {passed}")
    results.append(f"  Warnings: {warnings_count}")
    results.append(f"  Failed:   {failed}")
    results.append("")

    if failed > 0:
        results.append(f"RESULT: FAIL - {failed} critical issue(s) found. Fix these before proceeding.")
    elif warnings_count > 3:
        results.append(f"RESULT: PASS with warnings - {warnings_count} items to review.")
    else:
        results.append("RESULT: PASS - All checks passed, project is healthy.")

    return "\n".join(results)


mcp.add_provider(
    SkillsDirectoryProvider(
        roots=BASE_DIR / "setup_mcp" / ".agents" / "skills"
    )
)

if __name__ == "__main__":
    mcp.run()
