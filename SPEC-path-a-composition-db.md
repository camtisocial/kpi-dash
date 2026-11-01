# Spec: Path A — Native Composition DB for Donut/Composition Charts

> **Status: design only — not yet built.** This specifies a fully-native Notion
> approach for feeding donut/stacked-bar charts. No external code, no AI agent.
> See `HANDOFF-kpi-insights.md` for the broader chart/insight context.

## Goal

A long-format **Composition** database that feeds donut and stacked-bar charts
(Automated vs. Manual reports, Mobile vs. Web users), populated automatically from
the wide **New dashboard test** DB using **native Notion database automations** —
no external code, no AI agent.

## Why a separate DB is required

The source DB is **wide format**: each metric is its own column. A Notion donut
chart slices by the *values inside one categorical column* and aggregates one
number — it cannot slice by *column identity*. So "Automated vs. Manual" (two
separate columns) isn't a grouping that exists in the wide table. The fix is to
**unpivot** into long format (`Week / Group / Type / Value`), where the distinction
lives in row values the chart can group by.

## Architecture

```
New dashboard test (wide, source of truth)
        |  trigger: "Page added"
        v
Database automation  --(4x "Add page to")-->  Composition DB (long format)
                                                      |
                                                      v
                                        Donut + stacked-bar chart views
                                        (charts do the aggregation)
```

Notion owns the trigger and the row fan-out; the **charts** own the aggregation
(sum across weeks). The automation never computes a total — it just copies one
week's four numbers into four typed rows.

## Composition DB schema

| Property | Type | Purpose |
|---|---|---|
| `Name`   | Title | Auto label, e.g. `2026-06-03 · Automated` (set by automation) |
| `Week`   | Date | Copied from the source row's `Date` |
| `Group`  | Select: `Reports`, `Users` | Which donut this row belongs to (chart filter) |
| `Type`   | Select: `Automated`, `Manual`, `Mobile`, `Web` | The donut slice (chart `GROUP BY`) |
| `Value`  | Number | The metric value (chart `AGGREGATE sum`) |
| `Source` | Relation -> New dashboard test *(optional)* | Traceability back to the source week |

## The automation

- **Lives on:** New dashboard test
- **Name:** `Fan out week → Composition`
- **Trigger:** `Page added`
- **Actions:** four `Add page to → Composition`, each mapping from the new row:

| # | Group | Type | Value ← source property | Week ← |
|---|---|---|---|---|
| 1 | `Reports` | `Automated` | `Automated Reports` | `Date` |
| 2 | `Reports` | `Manual` | `Manual Reports ` *(trailing space!)* | `Date` |
| 3 | `Users` | `Mobile` | `Mobile Users` | `Date` |
| 4 | `Users` | `Web` | `Web Users` | `Date` |

A single automation supports multiple action steps, so all four fit in one automation.

### Property-name booby traps

Two source-DB property names are easy to mis-map:

- **`Manual Reports `** has a **trailing space**.
- **`Date`** carries a leading **zero-width/BOM character**.

When wiring the automation's value mappings, pick properties from Notion's dropdown
rather than typing — a typed "obvious" name silently maps to nothing and yields
blank `Value`s.

### Design principle

The automation does **no math** — it copies four raw numbers. All summing/percentage
work happens in chart config (`donut AGGREGATE sum ON "Value" GROUP BY "Type"`).
Keeping the automation arithmetic-free is what makes it reliable: nothing to drift.

## Charts built on the Composition DB

- **Donut — Automation split (YTD):**
  `FILTER "Group" = "Reports"; FILTER "Week" >= 2026-01-01; GROUP BY "Type"; CHART donut AGGREGATE sum ON "Value"`
- **Donut — User split (YTD):**
  `FILTER "Group" = "Users"; FILTER "Week" >= 2026-01-01; FILTER "Value" > 0; GROUP BY "Type"; CHART donut AGGREGATE sum ON "Value"`
- **Bonus — Automated vs. Manual by month (stacked):**
  `FILTER "Group" = "Reports"; GROUP BY "Week"(month); CHART column AGGREGATE sum ON "Value" STACK BY "Type"`
  — the stacked-bar trend the wide format couldn't produce.

## Limitations (inherent to Path A)

1. **No retroactive updates.** Trigger is `Page added`. If someone *edits* a past
   week's value, composition rows won't change — `Add page` only creates, and native
   automations can't reliably find-and-update the matching long row. *Mitigation:*
   treat the wide DB as append-only; fix rare history corrections by hand, or revisit
   Path B (native trigger -> deterministic pipeline worker) later.
2. **Backfill is not automatic.** Automations fire only on *future* triggers, so the
   existing **71 weeks won't populate themselves.** A one-time seed is required (below).
3. **Zero/partial/blank rows fan out too.** The all-zero partial current week and the
   bad zero-weeks create zero-`Value` rows. Harmless in a *sum* donut (0 adds nothing),
   but a *current-week* donut would show empty — handle with `FILTER "Value" > 0` (or a
   date filter) on those views. Also ensure the pipeline stops emitting the ~25 blank
   padding rows, or they fan out into junk.
4. **Annual rows (2021–2024) excluded** — they have no reports/users breakdown, so the
   value mappings produce nothing meaningful; scope composition to weekly rows only.
5. **Paid plan required** (automations beyond Slack are paid-tier).
6. **Duplicate risk** if `Page added` ever double-fires or rows are recreated — low,
   but worth a periodic dedupe check.

## One-time backfill plan (separate from the automation)

To populate the existing 71 weeks, do a one-time API seed (`notion-create-pages`)
generating the ~4 typed rows per valid week (~200–280 rows, skipping blank/annual
rows). This is a *seed*, run once at green-light — distinct from the ongoing native
automation, which handles everything afterward.

## Build order (when approved)

1. Create the Composition DB with the schema above.
2. Build the automation (4 add-page actions, careful property mapping).
3. Add one test week to the wide DB -> confirm 4 correct rows appear.
4. One-time backfill seed of the 71 weeks.
5. Create the donut + stacked-bar chart views.
6. Verify totals against raw data (e.g. latest-week automation rate ≈ 70%).

## Decisions to confirm before building

- **Backfill:** seed the 71 weeks via the API, or start fresh from go-live?
- **Scope:** both donuts + the bonus stacked monthly trend, or just the two donuts?
- **Snapshot window:** YTD-2026 donuts, all-time, or latest-week-only?

## Reference: verified Notion capabilities (June 2026)

- **Triggers:** `Page added`, `Property edited` (with conditions), `Every {frequency}` (scheduled).
- **Actions:** `Edit property`, `Add page to` (any DB), `Edit pages in` (any DB),
  `Send notification`, `Send mail`, `Send webhook` (max 5/automation, POST-only),
  `Send Slack notification`, `Define variables`.
- **Plan:** paid plans only (free tier = Slack notifications only).
- Sources: [Database automations](https://www.notion.com/help/database-automations),
  [Webhook actions](https://www.notion.com/help/webhook-actions),
  [Notion API webhooks](https://developers.notion.com/reference/webhooks).
