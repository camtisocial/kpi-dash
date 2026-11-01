# Handoff: KPI Insight Charts — Context & Orientation

> **Status: orientation only.** This document brings you up to speed on a design
> discussion about adding new weekly charts/insights to the dashboard. **Do not
> start building anything yet** — wait for the user to give you a specific task.
> Several candidate work items are listed at the bottom under "Possible Next Work,"
> but none are approved. Your first job is to understand the data and the decisions,
> not to write code.

## Your Task (for now)

Absorb the context below so you can pick up the conversation about *which weekly
charts/insights to add and how to render them cleanly given gaps in the data*. The
user is improving an existing KPI dashboard for a company that wants weekly
charts/insights. When they give you a concrete task, you'll already understand the
data shape, the data-quality holes, the chart ideas on the table, and what's been
decided vs. left open.

## What NOT to Touch

- **Do not write or modify any chart/widget code, pipeline code, or data files yet.** No work is approved.
- **Do not overwrite `HANDOFF.md`** — that's the separate, broader project handoff. This file (`HANDOFF-kpi-insights.md`) is the scoped one.
- **Do not swap the generic public labels back to real metric names** — that's a separate production task tracked elsewhere.
- Don't start the Notion OAuth flow or pipeline runs unless asked.

## Project Context

A versioned HTML-widget dashboard that embeds KPI charts into Notion pages.
Data flows: data source → `tools/refresh.py` → `shared/kpi-data.js` (single source of
truth) → `tools/bundle.py` → `v3-widgets/dist/*.html` (self-contained, Chart.js
inlined) → GitHub Pages → Notion embed blocks. Auto-refreshed weekly via GitHub
Actions. Charts use Chart.js. The current `v3-widgets/` set is the active version.
See `HANDOFF.md` and the project memory for full pipeline detail.

## The Data (read this carefully — it drives every decision)

Source under review is an exported CSV (the eventual production source is a Notion DB,
not yet connected). Path:
`Private & Shared/REAL DATA TEST 5939b42d5f9482b8a2c201425acd3e3f.csv`

- **71 weekly rows**, Jan 2025 → Jun 2026, each row a week (dated by week start).
- Plus **annual lane-mile totals** for 2021–2024 at the bottom.
- The company does road/pavement-type work (lane miles = output; equipment = fleet;
  reports = field reports; users = app users — mobile field crews + web office staff).

**Column families:**
- **Output:** `Lane Miles`. (`Imported Data` is a redundant raw staging copy of it — ignore.)
- **Assets:** `Active Equipment`.
- **Reporting:** `Automated Reports` + `Manual Reports` = `Total Reports`.
- **Engagement:** `Mobile Users` + `Web Users` = `Monthly Active Users` (MAU).

**Coverage / holes (this is the crux):**

| Metric group | Coverage | Notes |
|---|---|---|
| Lane miles, equipment, all reports | **99%** | 1 bad week each; 55–56 week unbroken run. Plot beautifully. |
| Users (mobile/web/MAU) | **79%** | 8 blanks + 7 zeros = 15 scattered holes; longest clean run only 26 wks. Gappy as a weekly line. |

**Known bad/edge rows to handle:**
- `June 10–14, 2026` (top row) = the **current partial week**, all zeros → causes a cliff-to-zero on weekly charts every Monday. Exclude/mark as partial.
- `2026-02-19`: `equipment = 0` (bad). `2026-02-24`: `lane = 0` (bad). Filter these.

**Strong seasonality** (avg weekly lane miles by month): Jan ~2.0k → Aug ~46.3k → Dec ~5.1k. A ~23× trough-to-peak swing. Raw weekly views look misleading without accounting for this.

**Annual lane miles:** 2021 282k → 2022 478k → 2023 607k → 2024 735k → 2025 915k (weekly sum). Steady ~25%/yr growth. 2026 YTD (through ~Jun 3) ≈ 188k.

## Chart Ideas Discussed (tiered by how cleanly they render given the holes)

**Tier 1 — holes essentially invisible (best candidates):**
1. **Cumulative YTD pace vs. last year (lane miles)** — running total on a shared Jan→Dec axis, 2026 vs 2025 (vs 2024). Accumulation hides the single hole *and* strips seasonality. Most useful + most hole-proof. Pair with a "YTD vs. same week last year: +X%" card.
2. **Monthly aggregates** (they already have a monthly lane-miles bar) — aggregation absorbs bad weeks.

**Tier 2 — clean after dropping 1–2 known-bad weeks:**
3. **Automation rate %** trend (auto ÷ total; ~74% overall, ranges 69–83%). Guard the `total=0` week. 4-week average smooths the noise.
4. **Lane miles per active unit** (lane ÷ equipment; ~15 → ~29 into season). Drop the two bad weeks.

**Tier 3 — will look gappy as a weekly line (avoid weekly):**
5. **User-based series (MAU, mobile vs web)** — 79% coverage. Show **monthly** or as **"latest known value" cards/donuts**, not a raw weekly line.

## Key Design Insight: chart type/controls vs. data holes

The dashboard tool offers chart types **vertical/horizontal bar, line, donut** and
controls **range, cumulative, omit zero values**. These map almost one-to-one onto the
hole problems:
- `cumulative` = accumulate transform → hides seasonality + holes (pace chart).
- `omit zero values` → drops the partial week and the bad zero-weeks.
- `donut` → removes the time axis entirely, so no gaps possible. A **donut of auto vs
  manual** = current automation rate snapshot; a **donut of mobile vs web** = user split
  snapshot that sidesteps all 15 user-data holes.

**Two things chart choice canNOT fix:**
1. **`omit zero values` is blunt** — it hides *all* zeros, not just bad ones. Safe for
   lane/reports/equipment (real zeros don't occur in-season) but it's symptom-not-cause;
   a legitimately-zero week would be silently hidden too.
2. **Ratio *trends* need a precomputed column.** Bar/line/donut plot existing columns;
   they can't compute auto÷total or lane÷equip over time. A donut gives the ratio as a
   *current snapshot* for free, but "is automation % trending up?" requires adding the
   ratio as a column in the pipeline (one line in `refresh.py`).

**One open capability question:** can the dashboard tool overlay **two years on one
Jan–Dec axis** (2026 line vs 2025 line) for the pace chart? `cumulative` + `range` handle
the math; whether two date ranges can share an axis is unconfirmed.

## Notion Status

- The **Notion MCP is installed but NOT authenticated** — only `authenticate` /
  `complete_authentication` tools exist; no read/search/fetch. Cannot see Notion content
  in-session until OAuth is completed.
- Separately, the **production integration token** (for unattended `refresh.py` pulls) is
  blocked pending workspace-admin access. These are two different access paths.

## Relevant Files

- `Private & Shared/REAL DATA TEST 5939b42d5f9482b8a2c201425acd3e3f.csv` — the weekly data under analysis.
- `shared/kpi-data.js` — single source of truth the widgets read from.
- `tools/refresh.py` — fetches source data, rebuilds dist/. Where a precomputed ratio column would go.
- `tools/bundle.py` — bundles `v3-widgets/src/` → self-contained `v3-widgets/dist/`.
- `tools/scramble.py` — normalizes data to a 0–100 scale.
- `v3-widgets/src/*.html` — editable widget sources: `w-stats`, `w-lanes`, `w-reports`, `w-equipment`, `w-users`, `w-annual`. **Edit `src/`, then bundle — never edit `dist/` directly.**
- `v3-widgets/dist/*.html` — generated output (do not hand-edit).
- `shared/chart.umd.min.js`, `shared/kpi-style.css` — inlined Chart.js + shared styles.
- `HANDOFF.md` — the broader project handoff (pipeline, deploy, production TODOs).

## Decisions Already Made

- Existing dashboard is mostly **raw totals** (cards + one trend); the agreed opportunity is **ratios, pace-vs-last-year, and composition**, since raw weekly views are misleading under heavy seasonality.
- **Cumulative pace** and **automation-rate** identified as the two highest-value, most hole-robust additions.
- **Donuts** chosen as the clean way to show automation split and mobile/web split (snapshot, no time-axis holes, no new columns).
- User-engagement series stay **monthly or card-form**, not weekly lines, until coverage improves.
- New widgets must follow the existing pipeline: edit `v3-widgets/src/`, run `tools/bundle.py v3-widgets`; data comes via `shared/kpi-data.js`.

## Possible Next Work (NOT approved — await user instruction)

- Build the two Tier-1/2 winners (cumulative pace + automation-rate trend) as new `v3-widgets`.
- Add the two donuts (automation split, mobile/web split).
- Precompute ratio columns (automation rate, lane-miles-per-unit) in the pipeline so ratio *trends* are plottable.
- Add a reusable data-cleaning step (partial-week exclusion + bad zero-week filtering) all charts inherit.

## Getting Started

Read this file, then `HANDOFF.md`, then skim `v3-widgets/src/w-lanes.html` and
`v3-widgets/src/w-reports.html` to learn the existing widget pattern, and
`tools/refresh.py` to see where data/columns are produced. Then **ask the user which of
the "Possible Next Work" items to take on** before writing any code.
