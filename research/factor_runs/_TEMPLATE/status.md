# <Research Name> — Status

## Research Identity

- **name:** <research_name>
- **type:** <old_research_asset | factor | signal | strategy | filter | report>
- **version:** v0
- **created:** YYYY-MM-DD
- **human_reviewer:** <name>

## Status Fields

```yaml
research_status: REVIEW_REQUIRED
code_trust_initial: TBD
promotion_status: NOT_PAPER_OR_LIVE_ELIGIBLE
human_review_status: PENDING
human_decision: PENDING
```

## Status Rationale

Explain why the current status was assigned.

Minimum questions:

1. Is this a pure factor, signal, strategy, filter, report, or old research asset?
2. Was it AI-assisted?
3. Does it have frozen input data?
4. Does it have standalone factor values?
5. Does it have standalone signals?
6. Does it have standalone trades and metrics?
7. Does it have unresolved future-leak or same-bar execution risk?
8. Is it eligible for paper, shadow, or live?

## Blocking Issues

- [ ] Frozen input data or manifest missing
- [ ] Standalone factor values missing
- [ ] Standalone signals missing
- [ ] Standalone trades missing
- [ ] Cost model incomplete
- [ ] PnL / drawdown / Sharpe basis unclear
- [ ] Future-leak or timing issue unresolved
- [ ] Reproduction command missing or unverified
- [ ] Code Trust Map not reviewed

## Promotion Checklist

This item may not be promoted unless all required items are checked.

- [ ] Frozen input data or manifest
- [ ] Standalone factor values
- [ ] Standalone signals
- [ ] Standalone trades
- [ ] Explicit cost model
- [ ] Documented PnL / drawdown / Sharpe calculation
- [ ] No unresolved future-leak issue
- [ ] Factor memo completed
- [ ] Reproduction command verified
- [ ] Reviewed Code Trust status
- [ ] Human decision recorded

## Related Artifacts

| Artifact | Path | Notes |
|---|---|---|
| Source script | `<path>` | |
| Report | `<path>` | |
| Data snapshot | `<path>` | |
| Factor values | `<path>` | |
| Signals | `<path>` | |
| Trades | `<path>` | |
| Metrics | `<path>` | |

## Human Review

```yaml
human_review_status: PENDING
human_decision: PENDING
reviewed_by: TBD
reviewed_at: TBD
```

Human review notes:

- 
