# Research Lifecycle

This document defines the standard workflow for turning old research assets, new factor ideas, signals, strategies, and published reports into auditable research assets.

It is the process-level companion to `docs/AUDITABLE_FACTOR_RESEARCH_SKILL.md`.

- `AUDITABLE_FACTOR_RESEARCH_SKILL.md` defines the minimum audit standard.
- `RESEARCH_LIFECYCLE.md` defines how a research item moves through the repository.
- `research/factor_runs/_TEMPLATE/` provides the standard file templates.
- `docs/CODE_TRUST_MAP.md` records file-level trust ratings.
- `docs/FACTOR_BACKLOG.md` records research priority and status.

The goal is not to make every idea profitable. The goal is to make every idea reproducible, inspectable, falsifiable, and correctly archived or rebuilt.

---

## 1. Research Item Types

Every research item must first be classified.

| Type | Meaning | Example |
|---|---|---|
| `old_research_asset` | Existing AI-assisted or exploratory research that already has code, reports, or artifacts | `rank444_rsi_bb` |
| `new_factor_idea` | A new hypothesis that has not yet been implemented | `volatility_regime_filter_v0` |
| `factor` | A numeric value observed at a timestamp | RSI, BB z-score, funding z-score |
| `signal` | A discrete decision derived from one or more factors | long entry, short entry, risk-off flag |
| `strategy` | signal + entry + exit + sizing + cost model | RSI+BB mean reversion strategy |
| `report` | Human-readable research output | HTML report, markdown digest |

Important rule:

> A strategy can contain factors, but a strategy is not automatically a clean factor.

---

## 2. Standard Workflow

Every research item should move through this sequence:

```text
old research asset / new idea
  -> intake
  -> audit folder
  -> code trust classification
  -> human decision
  -> archive / rebuild / promote / drop
  -> standard artifacts if rebuilt or promoted
  -> backlog and trust map update
  -> next research object
```

Expanded workflow:

```text
1. Intake
2. Create research folder
3. Fill audit documents
4. Rate related code in Code Trust Map
5. Human decision
6. Archive or rebuild
7. Produce standard artifacts if needed
8. Update backlog / status / trust map
9. Move to the next item
```

---

## 3. Step 1 — Intake

Purpose: identify what the object is before judging it.

Required questions:

1. What is the research item called?
2. Is it a factor, signal, strategy, filter, report, or old research asset?
3. Does code already exist?
4. Does a report already exist?
5. Does it have frozen input data?
6. Does it have standalone factor values, signals, trades, and metrics?
7. Was it AI-assisted?
8. Is it intended for archive, rebuild, paper, shadow, or live?

Output:

```text
research/factor_runs/<name>/status.md
```

Default status for AI-assisted research:

```text
REVIEW_REQUIRED
```

---

## 4. Step 2 — Create Research Folder

Every auditable item must have a dedicated folder:

```text
research/factor_runs/<name>/
  status.md
  factor_memo.md
  data_contract.md
  audit_notes.md
  reproduction.md
  decision.md
```

Use the template folder:

```text
research/factor_runs/_TEMPLATE/
```

Do not use old scripts as the research record. Scripts are implementation artifacts. The research folder is the audit dossier.

---

## 5. Step 3 — Code Trust Classification

Related code files must be added to or reviewed against:

```text
docs/CODE_TRUST_MAP.md
```

Trust levels:

| Level | Meaning |
|---|---|
| A | trusted core |
| B | research usable |
| C | archived/reference |
| D | high risk, audit required |

Rules:

- Code trust is file-level.
- Research status is project-level.
- A strategy may be `REVIEW_REQUIRED` even if some utility code is A-level.
- A script may be C-level while the idea remains useful as a rebuild candidate.

A file cannot be A-level simply because it runs. It needs clear inputs/outputs, tests or fixed reproduction cases, documented assumptions, and verified timestamp logic where relevant.

---

## 6. Step 4 — Human Decision

The human reviewer must decide what happens next.

Allowed decisions:

| Decision | Meaning |
|---|---|
| `ARCHIVE_OLD_CODE` | Preserve old code/report as historical evidence; do not extend it |
| `REBUILD_CLEAN_BASELINE` | Extract the idea and rebuild using the auditable standard |
| `PROMOTE_TO_PAPER` | Promote only if all required artifacts exist and no blocking issue remains |
| `DROP` | Stop investing in the idea |
| `PARK` | Keep the idea in backlog without immediate work |

This decision must be recorded in:

```text
research/factor_runs/<name>/decision.md
```

Human decision is required before any old AI-assisted research is expanded.

---

## 7. Step 5 — Archive or Rebuild

### Archive

Use archive when:

- the old code is useful as a record but not trustworthy enough to extend;
- the report is informative but not supported by standard artifacts;
- the idea is worth remembering but the implementation is not reusable.

Archive means:

```text
keep the files
stop extending old scripts
record the decision
optionally extract a clean rebuild candidate
```

Archive does not mean deleting.

### Rebuild

Use rebuild when:

- the idea is still useful;
- old implementation is not clean enough;
- you want a reusable baseline, factor, signal, or strategy.

A rebuild must start from the auditable standard, not by patching old exploratory scripts.

---

## 8. Step 6 — Standard Artifacts

Only rebuilt or promoted items need full standard artifacts.

Required artifacts:

```text
data/cache/<name>/manifest.json
data/cache/<name>/bars.parquet

data/features/<name>/factor_values.parquet
data/features/<name>/signals.parquet

reports/artifacts/<name>/trades.parquet
reports/artifacts/<name>/metrics.json
reports/artifacts/<name>/result_summary.md
```

Do not create full artifacts for every archived old script unless the item is being rebuilt or promoted.

---

## 9. Step 7 — Backlog and Map Update

After a decision, update as needed:

```text
docs/CODE_TRUST_MAP.md
docs/FACTOR_BACKLOG.md
research/factor_runs/<name>/status.md
research/factor_runs/<name>/decision.md
```

Minimum updates:

- If old code is archived, mark related scripts as C-level or keep existing C-level rating.
- If a clean rebuild is opened, create a new folder rather than mutating the old one.
- If an idea is dropped, record the falsification reason.
- If promoted, record the exact evidence and artifact paths.

---

## 10. Human vs AI Responsibilities

### AI responsibilities

AI may:

- scan code and reports;
- draft audit documents;
- identify data sources and output paths;
- extract formulas and signal rules;
- write tests and artifact-generation scripts;
- compare same-bar and next-bar execution;
- generate first-pass Code Trust Map entries.

### Human responsibilities

The human reviewer must:

- approve the research identity;
- decide whether assumptions are acceptable;
- approve archive/rebuild/promote/drop decisions;
- verify high-impact claims;
- review any result that changes capital allocation or publication status;
- decide whether an idea deserves more time.

AI output is not final audit evidence until a human reviewer has checked the blocking assumptions.

---

## 11. Promotion Gate

No item may be promoted to `PAPER_CANDIDATE`, `SHADOW_CANDIDATE`, `TINY_LIVE`, or `LIVE` unless it satisfies the promotion rule in `AUDITABLE_FACTOR_RESEARCH_SKILL.md`.

At minimum, it must have:

- frozen input data or manifest;
- standalone factor values;
- standalone signals;
- standalone trades;
- explicit cost model;
- documented PnL and Sharpe calculation;
- resolved future-leak issues;
- factor memo;
- reproduction command;
- reviewed Code Trust status.

---

## 12. Current Recommended Repository Practice

For the current `momentum` repository:

1. Do not delete old scripts first.
2. Create audit dossiers first.
3. Rate code in `CODE_TRUST_MAP.md`.
4. Make a human decision.
5. Archive old exploratory scripts unless they meet the trusted-core standard.
6. Rebuild useful ideas as clean baselines in new folders.
7. Only after several completed dossiers, consider structural cleanup.

Default rule:

> Mark first, decide second, archive or rebuild third, delete last — and usually do not delete.
