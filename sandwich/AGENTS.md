# AGENTS.md — Sandwich Maker Configurator

This is the agent instructions file used to generate the `sandwich/` configurator in this repository.

The original source of this file is `~/SandwichMaker/AGENTS.md`. This is the **modified** version of the standard SPL template: the food-domain-specific instructions below replace the generic Software Product Line framing. The instructions were used with a customised prompt template (see repository root README):

```
Follow AGENTS.md. Create a configurator for the Sandwich Maker. Here is more information: <sandwich ingredient / options description>.
```

The published artefact in this folder is the static `assets/` build output of the generated React + Vite project.

---

# AGENTS.md — Sandwich Maker Configurator

## Project Overview

This project builds a **Sandwich Maker Configurator** — a React + Vite application where users build and visualise sandwiches by selecting and deselecting ingredients from a structured SPL (Software Product Line) model. The underlying structure comes from `sandwich.uvl` which defines required ingredients, optional add-ons, constraints, and nutritional attributes.

The output is a working web app with **7 distinct views**, each presenting the sandwich configuration from a different angle. Every view lets the user toggle ingredients and contributes to a shared configuration state. The app produces:
- A **JSON configuration** of the final sandwich (downloadable)
- A **live SVG cross-section** of the sandwich (real-time preview)

## Inputs

The agent will receive:

1. **`sandwich.uvl`** — the UVL file defining the sandwich SPL with features, constraints, and attributes (Calories, Sugar, etc.)
2. **MCP Server** — Access to a React/Vite MCP server for generating the application

## The Sandwich SPL (from sandwich.uvl)

```
Sandwich
  mandatory
    Bread {Calories 100, Sugar 20}
  optional
    Sauce (OR)
      Ketchup {Calories 40, Sugar 35}
      Mustard {Calories 25, Sugar 5}
    Cheese [0..2]
      Cheddar {Calories 60}
      Gouda {Calories 50}
      Goat {Calories 35}
    Pickle [1..3]

Constraints:
  Ketchup => Cheese          (ketchup requires cheese)
  Total Sugar < 60           (sum of sugar attributes)
  Total Calories < 160       (sum of calories attributes)
```

The agent should model these constraints as **visible warnings** in the UI — not hard blocks. If you're over the calorie cap or forgot cheese with ketchup, show a wavy red underline with a tooltip explaining why.

## Required Output

A working React + Vite application with:

### 7 Distinct Views + a Config Inspector

Each view must be structurally different — different layout, different interaction pattern, different visual style.

The last view should be a inspector of the configs svg+json.

### Shared State

Lightweight React Context persisting ingredient selections across all views. Toggling ketchup in the Builder should reflect in the Nutrition Dashboard.

### Outputs

- **JSON file** — structured sandwich configuration (ingredients, attributes, computed totals)
- **SVG rendering** — cross-section of the sandwich built from stacked ingredient layers, updates live as the user toggles ingredients

### UVL Schema Files

- `src/config/schema.uvl` — the parsed UVL definition
- `src/config/schema.dot` — Graphviz representation
- `src/config/schema.svg` — rendered UVL tree as SVG
- `src/config/schema.ts` — TypeScript schema with ingredients, constraints, attributes

## Design Rules

### 1. Use food-friendly labels, not UVL keys

- Bad: `Sauce.Ketchup.sugar_35`
- Good: "Ketchup — adds sweetness (35g sugar)"

Every ingredient name, constraint label, and category must be translated into natural, food-context language.

### 2. Show conflicts as friendly warnings, not errors

Instead of hard-blocking, show inline notes:
- "⚠️ Ketchup without cheese? Bold choice. The UVL says ketchup usually pairs with cheese."
- "⚠️ You're at 155/160 calories. Adding another cheese will push you over."
- "⚠️ That's a lot of sugar — 55/60g. Watch it."

### 3. The SVG should look like a sandwich

Not a data table. A proper cross-section with recognisable layers:
- Bread = rounded rectangle, brownish
- Cheese = yellow/white layer
- Ketchup = red squiggle
- Pickle = green oval slices
- etc.

## Project Structure

```
/
+-- src/
|   +-- views/
|   |   +-- view_1/
|   |   +-- view_2/ ... view_7/
|   |   +-- ConfigInspector/
|   +-- config/
|   |   +-- schema.uvl
|   |   +-- schema.dot
|   |   +-- schema.svg
|   |   +-- schema.ts
|   |   +-- SandwichContext.tsx    # Shared state
|   +-- components/                # Shared primitives (Warning, Tooltip, IngredientTag, etc.)
|   +-- data/
|   |   +-- extracted.ts           # Raw UVL data
|   +-- App.tsx                    # Navigation between 7 views
+-- package.json
+-- vite.config.ts
```

## Tech Stack

- React 19+ with TypeScript
- Vite as the build tool
- **Variation required** across the 7 views: different UI approaches, CSS strategies, charting libraries
- Validation: `zod` for constraint rules
- SVG: custom SVG rendering for the sandwich cross-section (not a library)
- Charts: Recharts for Nutrition Dashboard, custom SVG for Flavour Profile radar

## Commands

```bash
npm install      # install dependencies
npm run dev      # start dev server
npm run build    # production build
npm run lint     # lint
```

## Definition of Done

Before considering the task complete, verify:

- [ ] All 7 views are reachable from the app's main navigation.
- [ ] Every view allows the user to select/deselect ingredients and contributes to shared state.
- [ ] Constraint violations (calorie cap, sugar cap, ketchup⇒cheese) trigger visible inline warnings.
- [ ] The 7 views are visibly and structurally distinct in layout and visual approach.
- [ ] JSON config can be downloaded and includes the user's selections with computed totals.
- [ ] Live SVG sandwich cross-section updates in real-time as ingredients are toggled.
- [ ] `src/config/schema.svg` exists — UVL tree rendered as SVG.
- [ ] `npm run build` succeeds with no errors.
- [ ] `npm run lint` passes.

After everything passes create a README.md containing screenshots and a short description of every view.

## Things to Avoid

- Producing 7 views that are essentially the same layout with different colours.
- Exposing UVL feature names as labels (e.g., `Sauce.Ketchup` → just "Ketchup").
- Silent constraint violations — always flag calorie/sugar overages and missing dependencies.
- Hard-blocking combinations — show warnings, let the user decide.
- Duplicating the sandwich schema across views — define it once in `src/config/`.
- Treating every view as an ingredient list — vary the visualisation (SVG, chart, stack, radar, etc.).
- Unit Tests — not necessary for this project.
- Generating `schema.svg` from UVL/dot before declaring the task complete.
- DO NOT LOOK INTO ._old_tries/
