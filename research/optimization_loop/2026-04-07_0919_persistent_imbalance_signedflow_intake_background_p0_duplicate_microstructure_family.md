# 2026-04-07 09:19 UTC — persistent imbalance × signed-flow continuation fresh intake first verdict

## Target
- `research/quant_digests/2026-04-07_0640_persistent-imbalance-signedflow-continuation-alpha.md`

## Policy / state frame used
- 按 `BOT2_BOT3_POLICY.md` 执行当前轮首个 `pending` fresh intake
- 不重排 `cycle_plan`，只处理这一项

## What changed
**First verdict：`persistent L1 imbalance × signed-flow autocorr continuation` 不进入前排，直接记为 `background / P0`。**

## Why
1. **独立主语不够新。** 这条线的核心仍是 `order-book / imbalance / aggressive-flow persistence -> next short-horizon continuation`，与池内已 intake 过的 `Rank 275 / order-book-taker-flow imbalance × confidence threshold`、`Rank 290 / L2 imbalance × aggressive trade delta × EMA vote`，以及已归档的 `OFI / L1 imbalance / VWAP pressure / spread gate` 单资产 microstructure continuation 家族高度同构；当前新增更多是把同一族命题拆成 `signed-flow autocorr + drift-vs-imbalance` 的分析三件套，而不是提出一个新的独立 raw alpha 主语。
2. **repo 给的是秒级分析证据，不是已压清的 1m/3m/5m 可迁移 pocket。** digest 自己也承认原生证据主要在 `500ms~1000ms`，后续真正关键的问题是“能不能迁移成 bar-level admission”；这说明当前 first verdict 面对的核心不是“对象已经清楚”，而是“能否从超短 microstructure 漂移上岸到 desk 可交易壳”。在这个问题没被回答前，不值得占用 `keep_P1` survivor 锁位。
3. **执行诚实边界仍停在想定层。** 虽然 repo 同时给了 `impact curves` 与高性能回放框架，但当前公开 digest 里还没有任何 recent-window 的 `post-cost markout`、跨资产 retention、或至少一个 `fee + spread + impact veto` 后仍保留净边的 pocket；这比已有前排 microstructure intake 并没有把 after-cost honesty 往前推进。
4. **它更像“研究骨架 / feature extraction infra”，而不是一个已压清 admission skeleton 的新候选。** `drift vs imbalance + oflow autocorr + impact` 很适合作为后续复核别的 microstructure 候选的公共分析框架，但这不等于它本身已经形成值得独占前排槽位的新对象。

## Comparison against existing pool
- `research/optimization_loop/2026-04-01_0040_rank275_orderbook_confidence_threshold_keep_p1.md` 已 intake `order-book / taker-flow imbalance × confidence threshold`
- `research/optimization_loop/2026-04-02_0614_rank290_l2_delta_vote_keep_p1.md` 已 intake `L2 imbalance × aggressive trade delta × EMA vote`
- `research/optimization_loop/2026-04-06_1317_adverse_selection_cost_continuation_intake_background_p0.md` 也已诚实归档一条与 `information-bearing aggressive flow -> next 1~3 bar continuation` 高度重叠的 microstructure continuation 学术变体
- 本轮对象新增的最强信息，是 repo 把 `microstructure diagnostics` 做得更系统；但这仍不足以让它脱离既有 family、形成独立 fresh intake 身份

## Runtime consequence
- 不分配新 `Rank`
- 不进入 `Surviving candidate slot`
- 不占用 `Active P2 / Paper launch queue`
- 直接写入 `Background pool`

## Result sentence for state
`persistent L1 imbalance × signed-flow autocorr continuation` 的 fresh intake first verdict 已完成：对象本质仍属于既有 `order-book / OFI / taker-flow continuation` microstructure 家族，当前新增主要是秒级 `drift-vs-imbalance + signed-flow autocorr + impact` 分析骨架，尚未压出独立于旧 family 的新 raw alpha 主语，也没有公开 `1m/3m/5m` 成本后 pocket 证据，因此本轮直接记为 `background / P0`。

## Publish note
- 已按要求执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
- 本次脚本在当前运行环境中长时间无输出、未在可接受窗口内完成，因此已中止；不影响本轮 state / first verdict 已生效
