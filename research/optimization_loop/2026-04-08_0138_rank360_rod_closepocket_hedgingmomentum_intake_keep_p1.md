# Rank 360 / rest-of-window impulse × close-pocket continuation / fresh intake keep_P1

- Time: 2026-04-08 01:38 UTC
- Operator: bot3 auto loop
- Source digest: `research/quant_digests/2026-04-08_0056_rod-closepocket-hedgingmomentum-alpha.md`
- Verdict: `keep_P1`
- Assigned Rank: `360`

## What changed system truth
`rest-of-window impulse × close-pocket continuation` 已压清为独立于既有 `plain trend / breakout / session seasonality` 家族的 raw alpha intake：它的主语不是泛化的日内动量，而是**围绕真实外部时钟的 event-clock continuation shell**——用 `close pocket` 之前的累计方向，去押最后一个集中对冲/再平衡窗口里的同向续行；本 digest 已明确给出 `20:00 UTC / U.S. cash close` 这类真实时钟锚点、`19:45–20:00` pocket 定义、`13:30/13:45 -> 19:45` 的 pre-window impulse 口径，以及相对 plain intraday momentum 的独立职责，因此这一步已足够拿到 fresh first verdict = `keep_P1`。

## Why not background/P0
- 这不是把传统美股尾盘现象生搬到 crypto 的空泛类比；digest 已把可迁移主语压成了“**真实外部时钟 + close pocket continuation**”，而不是任意 UTC 切窗的伪 session 效应。
- 与 plain momentum / breakout 不同，这条线要求固定的 event window、固定 pocket、固定持有/退出，而不是把信号拖成全天趋势策略。
- digest 里已经写出最小 clean-room 实验壳：`BTC/ETH perp`、`15m/5m`、`20:00 UTC`、`4/8/12 bps` 成本梯度、以及 `00:00/08:00/16:00 UTC funding boundary` 的后续扩展路径；因此对象已足够成为独立 `P1` survivor 候选。

## Why not promote_P2 yet
- 当前仍主要是论文级机制迁移与实验定义，不是 crypto 复刻结果；尚未压清 `20:00 UTC` 与 funding boundary 等时钟在币圈是否真的对应稳定可交易的对冲流。
- 与 plain intraday momentum 的独立增量，目前还停在研究假设层，尚未有 after-cost 结果证明“不是传统 trend/breakout 换了 event window 外衣”。
- 它值得保留一次便宜诚实 follow-up，但还不到直接进入 `P2 admission` 的程度。

## Key reservations kept explicit
- 该 alpha 强依赖真实流量锚点；如果 `20:00 UTC` 在 crypto 中并不稳定对应 ETF / options / hedge flow，则主假设会显著降级。
- 高换手 pocket 对成本与冲击非常敏感，尤其在 `5m` 口径下，后续 follow-up 必须优先压 `after-cost avg trade / Sharpe / hit-rate`，而不是再扩概念叙事。
- 若收益只集中在少数 ETF/宏观事件日，后续应更偏向 `event-driven pocket alpha`，而不是日常稳定 session 策略。

## Runtime write-back required
- 为该 fresh intake 分配正式 `Rank 360`。
- 本轮小点结果写为：`Rank 360：rest-of-window impulse × close-pocket continuation 已压清为独立于 plain trend / breakout / session seasonality 家族的 event-clock raw alpha intake，first verdict = keep_P1`。
- `Surviving candidate slot` 应切换到 `Rank 360`，并保留唯一一次 follow-up 预算。
