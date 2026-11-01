# KPI Dashboard Handoff
**Date:** June 22, 2026  
**Project:** SRO Finance & Operational KPI Dashboard — Notion Native Build

---

## Goal

Replicate the SRO Finance KPI dashboard (currently an HTML Claude artifact) inside Notion using only native Notion features, so the team doesn't have to leave Notion to view KPIs. The dashboard needs to show current metrics, year-over-year comparisons, trend charts, and weekly subscription activity.

---

## Databases in Play

All live under `Chess Box > Native kpi graph revamp v1`:

| Database | Format | Purpose |
|---|---|---|
| **FINANCE KPI DUP** | Wide, one row/week | Financial KPIs — ARR, MRR, Subscriptions, Revenue |
| **dashboard-test-1** | Wide, one row/week | Operational KPIs — Lane Miles, Equipment, Reports, Users |
| **Long table demo** | Long (one metric/row) | Operational data in long format, used by some chart views |

---

## What We Built This Session

### FINANCE KPI DUP
- Dashboard view with number cards for: ARR, MRR, ARR % YoY, MRR % YoY, Total/New/Renewed/Cancelled/Organic Subscriptions
- Added: **ARR Trend** chart (line, average ARR by date, blue)
- Added: **Monthly Recognized Revenue** chart (column, max YTD by date, orange, filtered to 2026)
- The YoY % cards use same-row formula columns (`2024 ARR`, `2024 MRR` → `ARR % Change`, `MRR % Change`)

### dashboard-test-1
- Added `Prior Year Week` self-referential relation property
- Added `PY Automated Reports` rollup property (sum through relation)
- These were added to test whether rollup values could display in number cards — they cannot (see findings below)

---

## Key Findings

### What works natively in Notion
- Plain number properties → display fine in number cards with sum/average
- Same-row formula properties (e.g. `ARR % Change = (ARR - 2024 ARR) / 2024 ARR`) → display fine in number cards
- Trend charts, column charts, donut charts → functional for visual review
- Weekly subscription metric cards → clean and reliable

### What doesn't work
- **Rollup properties cannot be used in number cards or charts.** Confirmed through testing. Sum/average aggregators are not offered for rollup columns.
- **HTML embedding in Notion is a dead end.** No workaround exists.
- **Custom Y-axis minimums** are not supported in Notion charts — only a binary "start at zero" toggle.
- **Date filter windows on number cards are fragile.** A "last 6 days" filter on weekly data will show blank if data entry is a few days late.
- **No forecasting capability** in Notion charts.

### The YoY workaround that does work
Store prior year values as plain number columns on the same row (`2024 ARR`, `2024 MRR`). Formula does the math on the same row. This makes YoY % displayable in cards. Dollar delta (`ARR - 2024 ARR`) still needs a formula column added.

---

## Immediate Next Steps

1. **Add missing formula columns to FINANCE KPI DUP:**
   - `ARR YoY Δ` = `ARR - 2024 ARR`
   - `MRR YoY Δ` = `MRR - 2024 MRR`

2. **Fix number card date filters** — widen from "last 6 days" to "last 14 days" so cards don't go blank between weekly entries.

3. **Research: Google Sheets → Notion sync** — the remaining pain point is that prior year values and weekly data must be entered manually. If data already exists in Google Sheets, automating the write-back to Notion as plain number properties would eliminate the double-entry problem and enable more sophisticated pre-computation (e.g. rolling averages, week-over-week delta).

---

## Reference Files

| File | Contents |
|---|---|
| `sro-finance-dashboard.pdf` | The HTML artifact dashboard we are trying to replicate |
| `notion-yoy-research.md` | What we tried for YoY display and why each approach failed |
| `current-setup-assessment.md` | Full pros/cons, pain points, and KPI coverage analysis |
