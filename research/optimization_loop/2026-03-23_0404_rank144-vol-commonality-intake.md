# 2026-03-23 04:04 UTC · Rank 144 / intraday volatility commonality asymmetric follow-up gate

## 0. 先判 interrupt
- `Paper / 正在自动运行` 顶板未出现新的 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`。
- `tiny-live / live-shadow plumbing` 顶板也未写入新的 blocking anomaly。
- 因此本轮不抢占 autonomous paper runner，继续按 `Next 3` 默认顺序执行：在 `Paper launch queue` 为空时，先认领 **fresh intake reserve**。

## 1. 为什么这轮切 fresh intake，而不是回头磨旧 P1
上一轮 `stale scout queue reset` 已把：
- `Rank 14b = keep_P1 / budget used / 不再作为默认 primary`
- `Rank 140 = keep_P1 / active compare anchor / 不再作为默认 primary`
- `Rank 125 / 112 / 111 = keep_P1 / budget used`

所以本轮最诚实的主动作，不是继续给旧 P1 做近义 cut，而是给一个 **真正可能改写 routing 的新 reserve** 做最低成本 intake。

## 2. 本轮认领
- **主点**：`Rank 144 / intraday volatility commonality asymmetric follow-up gate`
- **紧邻子点**：仅补 1 张轻量 scorecard，把它从“quant digest 读感”压成 desk 可用 verdict。

reader-facing 定义：
> 把“跨币 1h 实现波动是否同步抬升”当成 15m `follow-up` 的状态读数；先回答一笔 breakout continuation 值不值得继续，而不是把它伪装成 shared primary trigger。

来源基底：
- `research/quant_digests/2026-03-23_0349_intraday-vol-commonality-asymmetric-followup-gate.md`
- `reports/artifacts/literature/commonality_intraday_vol_proxy_summary_2026-03-23.csv`

## 3. 本轮最小 replication / honesty cut
这轮不重写 proxy，也不把它硬升成完整 clean replication；只把 digest 已给出的最小代理结果压成 desk verdict：

- `short, commonality<=1`: `mean_net_bp = -15.09`
- `short, commonality>=2`: `mean_net_bp = -4.13`
- **short 改善幅度**：`+10.97 bp`
- `long, commonality<=1`: `-10.42`
- `long, commonality>=2`: `-10.81`
- **long 侧几乎无改善，且略变差**：`-0.39 bp`

### 这刀真正回答了什么
它把这条 fresh intake 从“看起来像 shared regime/filter”压成了更窄、也更诚实的 desk 口径：

> **`vol commonality` 不适合写成三条线 shared allow gate；它更像 breakout-short follow-up 的偏空侧放行 / 过滤层。**

也就是说，它现在更接近：
- 对 `breakout-short / FT follow-up`：可继续保留为 `keep_P1`
- 对 `Fib / EMA / PSAR long`：只够当轻量 `size-down / veto` 参考
- 对整个 desk：还不配升到 `P2`，更不该被包装成独立 alpha

## 4. 轻量 scorecard
artifact：`reports/artifacts/scout_rank144_intraday_vol_commonality_15m/promotion_scorecard.{json,csv}`

- `usefulness = 2/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 1/3`
- `deployability = 2/3`
- `hard-fail flags = not_post_cost_positive_even_in_best_bucket; cross_asset_asymmetry_unverified_in_current_clean_rep; threshold_freeze_not_done`
- `recommended_action = keep_P1`
- `why_now = stale old-P1 queue 已重置，这条 fresh intake 能最低成本改写 breakout-short follow-up routing，而不会假装自己是 shared allow gate`
- `main_weakness = 当前仍只是 proxy-level aggregate evidence，尚未做 symbol-by-symbol frozen-threshold clean replication，也还没接到 production breakout-short router`

## 5. 本轮结论
### desk verdict
- **`Rank 144 = P1 / keep_P1 / fresh intake admitted / not-shared / breakout-short follow-up bias`**
- 它值得留在 active Scout，但现阶段不该顶掉 `Rank 140` 的 compare anchor 身份，也不该直接升 `P2`。

### 对后续 run 的最小授权边界
如果后续继续给这条线预算，只允许做 **1 次真正会改变 verdict 的最小 clean replication**：
- 冻结 `commonality_count` 阈值；
- 做 `BTC/ETH/SOL` 分资产拆分；
- 明确接到 `breakout-short FT/NFT router` 的前/后置位置；
- 看它能不能从“只是少亏”推进到“至少某一条路由上 post-cost 可活”。

否则默认停在 `keep_P1 / evidence pool`，不再烧默认轮次。
