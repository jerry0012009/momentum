# 2026-04-06 03:11 UTC — Rank 345 survivor follow-up drop to background

## 本轮执行小点
- target: `Rank 345 / GHE-Hurst pair selection × spread mean reversion`
- action: 对当前唯一 `Surviving candidate` 执行那唯一一次便宜且决定性的 follow-up，直接回答它是否已经拥有相对 plain corr/cointegration baseline 的 `high-liquidity perp / after-cost / walk-forward` 独立净增量，足以升入 `P2`

## 执行依据
- policy 规定：survivor 只能做 1 次决定性 follow-up，之后必须收口为 `promote_P2` 或 `drop_to_background`，不能继续开放式补研究。
- 当前 state 已把唯一问题写死：`GHE-ranked top-K pairbook -> beta-hedged z-score MR` 是否不止有 distinctness 叙事，而是真的比 plain pairs baseline 多出可迁移、成本后仍站得住的 pairbook quality / net edge。

## 本轮实际核对
1. 复核 `research/quant_digests/2026-04-06_0115_ghe-pair-selection-spread-meanreversion-alpha.md` 与对应 artifact：
   - `reports/artifacts/quant_digests/ghe_pairs_portability_20260406/results.json`
   - `reports/artifacts/quant_digests/ghe_pairs_portability_20260406/summary.csv`
2. 把当前对象的 strongest claim 压缩成 survivor 级问题：
   - 是否已经拿到 **after-cost** 证据？
   - 是否已经拿到 **walk-forward / baseline A/B** 证据？
   - 是否已经证明相对 plain corr/cointegration baseline 的 **独立净增量**，而不只是 `low-H spread 回得更快`？
3. 对照现有 plain baseline 记录：
   - `research/quant_digests/2026-03-26_1505_plain-pairs-longshort-vs-longonly.md`
   - 以及更早的 `Rank 157 / H<0.5 spread-band fast mean-reversion` survivor 收口记录

## 关键发现
### 1) 当前 strongest evidence 仍是「回归速度 / 命中率 pocket」，不是成本后基线增量
当前 artifact 最扎眼的结果集中在 `5m`：
- `ETHUSDT__DOGEUSDT @ 5m`：anti bucket hit rate `83.98%`，persistent bucket `21.05%`，median exit bars `13 vs 31.5`
- `ETHUSDT__BNBUSDT @ 5m`：anti bucket `67.76%`，neutral `39.13%`
- `SOLUSDT__DOGEUSDT @ 5m`：anti bucket `80.98%`

这足够说明：**low-H / rough spread 在某些大币 pair 上确实更像 fast-reversion admission pocket。**

但它仍然只是：
- 回到中线的 hit-rate / exit-speed 证据；
- 没有冻结真实交易成本；
- 没有冻结 walk-forward pair selection；
- 没有形成和 plain corr/cointegration baseline 的同口径 net A/B。

也就是说，这些结果可以支撑 `keep_P1`，却还不够支撑 `P2 admission`。

### 2) `15m` 没有把对象托成更稳的 admission 层，反而暴露 portability 仍混合
intake 时已经写过：`15m` 更像 admission/veto feature，不像主开火频率。复核 artifact 后这个判断没有变得更强，反而更明确：
- 有些 `15m` pair 在 anti bucket 更好；
- 也有不少 pair 出现 neutral / persistent 更优，或分桶样本过薄；
- 这说明对象还停留在“某些 pocket 上 low-H 很有信息”，而不是“GHE-ranked pairbook 在 desk 主口径上已足够稳到可进 P2”。

如果 survivor follow-up 后仍只能得到 `5m-first pocket / 15m mixed`，那它更像尚未完成 baseline honesty 的想法，而不是可以进入 P2 的对象。

### 3) 与 plain pairs baseline 对照后，独立净增量仍未被压实
现有 plain baseline 记录已经给出一条对照事实：
- `research/quant_digests/2026-03-26_1505_plain-pairs-longshort-vs-longonly.md` 的当前 Binance `15m` plain-vanilla pairs transfer 里，**gross 有、cost 后不活**；
- 更早 `Rank 157` 的 Hurst-based survivor 收口也已经说明：仅凭 `快回归 pocket` 和 proxy-style spread 结果，不足以宣称进入 `P2`。

而 `Rank 345` 这次虽然把 Hurst/GHE 从事后过滤前移到了 pair formation / pair ranking，但 **本轮没有新增一块能真正改变 admission 结论的证据**：
- 没有相对 baseline 的 frozen A/B net edge；
- 没有 `high-liquidity perp` 口径下的 after-cost pairbook PnL；
- 没有 walk-forward 下 `top-K GHE rank` 明显优于 plain corr/cointegration selection 的净结果。

换句话说：**distinctness 比 plain baseline 更清楚了，但 effectiveness / honesty 还没跨过 survivor->P2 那条线。**

## survivor 终局结论
**结论：`Rank 345` 本轮直接 `drop_to_background`，不升 `P2`。**

原因不是对象完全没东西，而是：
1. 它已经证明自己是一个值得记录的 pair formation idea；
2. 但 survivor 唯一一次 follow-up 要回答的是 `是不是足够值得升 P2`；
3. 当前答案仍然是否定的，因为最亮的证据还是 `5m low-H spread 回得更快`，而不是 `相对 plain corr/cointegration baseline 的 after-cost walk-forward 独立净增量`。

最诚实的 runtime 写法应是：
> `Rank 345 / GHE-Hurst pair selection × spread mean reversion` 已用尽唯一 survivor follow-up；现有亮点主要停留在 `5m` low-H 回归速度/命中率 pocket 与摘要级 superiority claim，尚未给出相对 plain corr/cointegration baseline 的 `high-liquidity perp / after-cost / walk-forward` 独立净增量，因此本轮直接退回 `Background pool / P0`，不升 `P2`。

## 对 runtime 的必要影响
- `Surviving candidate slot.current_target -> none`
- `followup_budget_remaining -> 0`
- `Surviving candidate.latest_result` 写成 `drop_to_background`
- `Background pool.latest_parked -> Rank 345`
- `cycle_plan #1.status -> done`

## 一句话结果（用于状态回写）
`Rank 345` 的唯一 survivor follow-up 已收口：现有证据仍未压实其相对 plain corr/cointegration baseline 的 `high-liquidity perp / after-cost / walk-forward` 独立净增量，亮点主要停留在 `5m` low-H 回归速度/命中率 pocket 与摘要级 superiority claim，因此本轮直接退回 `background / P0`，不升 `P2`。