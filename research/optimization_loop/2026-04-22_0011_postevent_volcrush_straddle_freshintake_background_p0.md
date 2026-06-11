# bot3 optimization loop — post-event vol crush × ATM straddle re-expansion fresh intake first verdict

- Time: 2026-04-22 00:11 UTC
- Target: `research/quant_digests/2026-04-21_2310_postevent-volcrush-straddle-reexpansion-alpha.md`
- Cycle item: `conditional fresh intake`（在第 1 项已收口 `background/P0` 后执行）
- Verdict: `background/P0`

## Why this changed system belief

`post-event vol crush × ATM straddle re-expansion` 没有通过这轮 fresh intake 的最小 decisive blocker：repo 的 `StrategyC_EventVol` 虽然明文包含 `C2 - Post-Event Vol Buy`，规则也确实完整（`0<=days_since_event<=7`、`LOW/MEDIUM`、`30D ATM straddle`、`TP 200% / SL floor 30% / time stop 20d / risk 2%`），但公开研究报告并没有给出与这条 long-gamma 子策略一致的独立事件后证据，反而把最清楚的已公开 post-event 模式写成了 `post-halving vol crush` 与 `post-crash vol remains elevated / often expensive`，对应结论更偏向卖波而不是在 event 后统一买入 straddle。

## Minimal honesty check

我只补了 1 个最小 honesty 子检查：直接核对 repo 源码与研究报告是否真的支撑 digest 所述的 `post-event vol crush -> re-expansion`。

### 1) 源码里确有 C2 long straddle 壳
从 `src/strategies.py` 可确认：
- `class StrategyC_EventVol`
- Thesis 明文写：`IV tends to inflate before events (sell straddle pre-event) and crush after events (buy straddle post-event when vol is depressed)`
- `C2 - Post-Event Vol Buy`
- 触发条件：`0 <= days_since <= 7 and regime in ("LOW", "MEDIUM")`
- 合约：`ATM`、`30d expiry`
- 风控：`POST_TP_MULT = 2.0`、`POST_SL_FLOOR = 0.30`、`time_stop_days = 20`

这说明 repo 里确实有一个可执行的 long-gamma 子策略壳，而不是 digest 编造。

### 2) 但公开研究报告对 post-event 证据与 C2 thesis 不对齐
`reports/btc_vol_research_report.txt` 的公开结论里：
- **Halvings**：`post-30d = -26.0%`，明文写 `TRADEABLE EDGE: Sell vol (straddles/strangles) 2-4 weeks after halvings`
- **Crashes**：`Post-crash vol remains elevated for 30-60 days`，并写 `post-crash are often expensive (sell opportunity)`
- 没有看到把 event 后统一归纳成“低/中 regime 下买 30D ATM straddle 等二次扩张”的独立、逐子策略可核证据

也就是说：repo 研究层最明确、最可读的 post-event 证据，和 C2 这条子策略想交易的方向并不一致；至少从公开材料看，它没有证明 `event 后 vol 被打得过低 -> 随后二次扩张` 是稳定存在的独立 edge。

### 3) 绩效归因也不足以把 C2 单独抬成前排对象
`btc_system_final_report.txt` 里 `Event Vol` 只有聚合口径：
- `38 trades`
- `31.6% WR`
- `PnL +21.1057`
- `Sharpe 0.67`
- Exits: `time_stop 31 / take_profit 4 / stop_loss 3`

这里没有把 `C1 pre-event sell` 和 `C2 post-event buy` 拆开。公开结果无法回答本轮唯一 blocker：**到底是 C2 自己在现实期权 friction 下成立，还是被 C1/其他 event 分支混在一起后看上去成立。**

## Decision

因此，这条线当前更像：
- 一个 **完整 options/event shell** 里的子想法；
- 但公开可复核材料还没有把 `post-event long-gamma` 单独证明成值得进入 desk 前排的独立 alpha。

按本轮 cycle success criterion，应直接收口为：

> `post-event vol crush × ATM straddle re-expansion` 的 fresh intake first verdict 已诚实收口 `background/P0`：repo 虽有完整 `C2 post-event buy ATM straddle` 壳，但公开 research report 对 event 后模式最明确的结论反而是 `post-halving vol crush` 与 `post-crash options often expensive`，更偏向卖波；同时 `Event Vol` 绩效归因只给了 `C1+C2` 聚合结果，没证明 `post-event long-gamma` 在现实期权 friction 下留下可独立复核、值得 desk 进入 paper-prep 的正 pocket，因此本对象当前只适合作为 options/event family 的研究提示，不保留 survivor，直接转入 `background/P0`。

## Tail step status

- publish homepage index: `failed (SIGKILL, non-blocking tail failure)`
- email summary: `sent` (`[momentum-bot3-auto] 事件后波动再扩张首判转背景`)
- runtime verdict/state/log: `kept`（未回滚）
