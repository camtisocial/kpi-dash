# KPI Dashboard — Why Visualization Options Are Constrained by Data Shape

> Summary prepared for leadership. Focus: how the *shape* of the database
> dictates which KPI/insight visualizations are possible, and why fuller
> coverage in Notion requires a concession (a second, reshaped table).

## Bottom line
The variety of charts we can build is limited not by the data itself, but by the
**shape** of the table it's stored in. Our source data is in "wide" format, which
is ideal for trends and totals but **cannot natively produce composition charts**
(e.g. a donut/pie of automated-vs-manual, or stacked breakdowns). Getting those in
Notion requires either restructuring the data or maintaining a second, reshaped
copy. This is a property of how no-code database tools chart data — not a flaw in
our data or our setup.

## The core concept: wide vs. long
The same numbers can be stored two ways:

- **Wide** — one row per week, each metric in its own column. Human-readable;
  great for single-metric **trends, totals, and KPI cards**.
- **Long ("tidy")** — one row per individual value, with a column naming *what* it
  is. Required for **composition and category-breakdown charts** (donuts, stacked
  bars).

A database chart can only **group rows by the values inside a column**. In wide
format, "Automated" and "Manual" are *column headers* (structure), which a chart
can't group on. In long format they're *values*, which it can. That single rule is
the entire limitation.

## Why this bites us specifically in Notion
Code-based or query-based tools (Excel, SQL/BI tools, or our own Chart.js pipeline)
**reshape the data on the fly** at the moment a chart is drawn — the reshaped
version exists for a microsecond and is discarded. **Notion cannot do this.** It has
no way to transform data at chart-time, so the only path to composition charts is to
**physically store a second, reshaped table** — which introduces data duplication
and sync risk.

## Options and trade-offs

| Approach | Chart coverage | Cost |
|---|---|---|
| **One wide table only (Notion)** | Trends, totals, cards — **no donuts/breakdowns** | Simple, but incomplete insights |
| **Wide + second long table (Notion)** | Full coverage | Data duplication; must keep the copy in sync |
| **Code pipeline (our Chart.js system)** | Full coverage, any chart | One source of truth, no duplication — but requires maintained code + hosting |

## Recommendation framing
This is best understood as: **"where should the reshaping live?"**

- In **no-code tools (Notion)**, the reshape must live in *stored data* →
  unavoidable second table.
- In **code (our pipeline)**, the reshape lives in *logic* → one source, no
  duplication.

If we keep the second table, the key discipline is to treat it as
**auto-generated from the source, never hand-edited** — that removes the
duplication risk (it becomes a derived output, like a report, not a competing
source of truth).

## Future state: is this permanent, or fixable with better infrastructure?
The *need to reshape* for composition charts is permanent (it's math, not tooling).
But the **friction** we hit — manual reshaping, a hand-maintained second table, and
public hosting — is purely a gap in deployed infrastructure, and the tools that
close it already exist today:

- **A workflow automation server (e.g. self-hosted n8n)** — auto-syncs the second
  (long) table from the source on every change, so it becomes a derived,
  always-in-sync projection nobody hand-edits. Could also run the HTML/Chart.js
  build on a schedule.
- **A self-hosted BI tool (Metabase, Superset)** — reshapes *at query time* like
  Excel/code, while staying live and shareable. Full chart coverage from one
  source, no second table, no custom code.
- **A small data warehouse + dbt** — provides materialized views (the exact feature
  Notion lacks): auto-maintained derived tables. Overkill now; the path if data grows.

Conclusion: this is an **infrastructure-maturity question, not a dead end.** With a
private server running one of the above, the limitation effectively dissolves.

## Serving it privately: the embedding vs. access-control trade-off
If we revive the HTML dashboard on private infrastructure, a second hard constraint
appears — separate from data shape, and worth understanding before committing.

The original HTML dashboard was embedded into Notion via **iframes**, and its only
fatal flaw was that it was hosted **publicly** (GitHub Pages), exposing real data.
The instinct is "host it privately" — but a Notion embed is a **cross-origin
iframe**, and putting a normal login wall in front of it **breaks the embed**:

- **Session cookies** are blocked by modern browsers in third-party iframes.
- **SSO / interactive login** can't run inside an iframe (redirect/frame-busting).
- The host must also explicitly allow Notion to frame it
  (`CSP: frame-ancestors notion.so notion.site`).

The access models that **do** work inside a Notion embed:

| Approach | Works in embed? | Security | Trade-off |
|---|---|---|---|
| **Unguessable / signed-token URL** | ✅ | Secret-in-URL; ≈ whoever can see the Notion page | Token visible in the embed; still **strictly better than public hosting** |
| **IP allowlist / VPN (Tailscale)** | ✅ (on-network viewers) | Strong | Breaks off-VPN / mobile |
| **Login wall (cookies/SSO)** | ❌ | Strong | Not viable inside an embed |

**The fundamental constraint:** you cannot have all three of — *embedded in Notion*
**+** *login-wall security* **+** *zero friction*. Pick two.

Two ways to escape the tension entirely:
1. **Native Notion charts** (the double-DB route) — charts live inside Notion, so
   they inherit Notion's own login. **No iframe, no embed-auth problem at all.** A
   real point in this approach's favor.
2. **Standalone internal dashboard** — host the HTML as its own private site with a
   normal login (no embedding). Strong security; you give up "it lives in Notion."

## Terminology (for reference)
- The two layouts: **wide** and **long** (a.k.a. "narrow" / "stacked") format.
- The guiding framework: **"tidy data"** (Hadley Wickham) — each variable a column,
  each observation a row, each value a cell.
- Converting between them: **pivoting / unpivoting** (also "melt/cast", "reshaping").
- The long storage pattern in databases: the **EAV model** (entity–attribute–value).
- Umbrella discipline: **data wrangling / data reshaping**.
