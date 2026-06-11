# Rank 186 / CME expiry postfix short BTC — survivor follow-up promote P2
- 时间：2026-03-26 17:21 UTC
- 对象：`Rank 186 / CME expiry postfix short BTC`
- 本轮角色：bot3 对 survivor 做唯一一次 decisive follow-up，只回答把月度 CME 到期事件样本与最小 `pre-ramp / placebo` 分层对齐后，这条 exact-time 事件后漂移是否足以升入 `P2`

## 结论
**单一收口 verdict：`promote_P2`。**

更具体地说，值得升入 `Active P2` 的不是泛泛的 `expiry effect`，而是这条已经收窄清楚的对象：

> **`CME 月度 BTC 到期（last Friday 16:00 London）后，在 Binance spot / perp 上做 `post 60~120m short BTC``。**

## 本轮补的 survivor 证据
### 1) placebo 对齐后，post-expiry 负漂移仍然够厚
直接复用 digest 产物 `expiry_minus_placebo_summary.csv`：

- Binance perp：
  - `post60` = **`-36.45 bp`**（expiry 相对普通周五同钟窗口）
  - `post120` = **`-41.36 bp`**
- Binance spot：
  - `post60` = **`-36.24 bp`**
  - `post120` = **`-41.16 bp`**

翻成人话：这不是“周五 16:00 本来就容易跌”，而是**月度到期那一下把同钟窗口从普通周五的正漂移，切成了明显更弱的负漂移**。

### 2) 最小 pre-ramp 分层后，方向没有被打掉
对同一份事件表按 `pre60 >= 0 / 20 / 40 bp` 做最小分层，结果 spot / perp 都一致：

- Binance perp：
  - `pre60 >= 0bp`：expiry `post60 ≈ -19.4bp`，普通周五 `+37.3bp`，差值 **`-56.7bp`**
  - `pre60 >= 20bp`：差值 **`-56.7bp`**
  - `pre60 >= 40bp`：差值 **`-58.8bp`**
- Binance spot：
  - `pre60 >= 0bp`：差值 **`-53.2bp`**
  - `pre60 >= 20bp`：差值 **`-56.0bp`**
  - `pre60 >= 40bp`：差值 **`-57.9bp`**

这说明 survivor follow-up 想回答的关键问题已经有了最低成本答案：**即便只看“到期前先有预热上冲”的那些样本，月度 expiry 后做空 BTC 的方向也没有塌；反而比无条件均值更清楚。**

### 3) time split 没显示“只靠单一年份撑起来”
按 expiry 事件年分桶看 `post60`：

- Binance perp：`2025` 共 `12` 次，均值 **`-19.27bp`**；`2026 YTD` 共 `2` 次，均值 **`-31.38bp`**
- Binance spot：`2025` 共 `12` 次，均值 **`-19.25bp`**；`2026 YTD` 共 `2` 次，均值 **`-30.02bp`**

当然样本仍然不大，但至少**当前没有出现“只靠 2025 某两次极端月份硬撑、2026 已经反向”的明显坏迹象**。

## 为什么这轮是 promote_P2，不是 park_to_background
- 不是 `park_to_background`：因为 survivor 唯一 follow-up 要回答的，不是“学术上是否完全定论”，而是**这条 exact-time raw alpha 在加上最小 placebo / pre-ramp 对齐后，还值不值得进更正式 admission**。当前答案是肯定的，而且 spot / perp 同向。
- 不是继续 `keep_P1`：policy 明确 survivor 只允许这唯一一次 follow-up；现在已经拿到会改变层级的答案，不能继续把它留在 P1 拖延。
- 是 `promote_P2`：因为前排对象已经收窄成一条足够具体、足够可测的 desk 候选——**月度 CME 到期后 `60~120m short BTC`，并优先关注到期前已有 `pre-ramp` 的 setup**。下一层该做的是正式 admission，而不是再讨论它是不是只是“有点意思”。

## P2 admission 应围绕的五项
1. `effectiveness / expected return`：补成本后净边、MAE/MFE、60m vs 120m 的真实可吃程度
2. `cross-asset stability`：至少回答 spot / perp 是否都能作为 production 入口，必要时再看跨 venue
3. `time stability`：把历史再往前扩，确认不是近一年单段现象
4. `parameter stability`：检查 `entry delay / hold 60~120m / pre-ramp threshold` 是否只在单点参数成立
5. `honesty / execution realism`：确认 event timestamp、London DST 对齐、入场切片与可成交口径都无 hidden leakage

## 本轮改变系统认知的一句话
`Rank 186` 已不只是“值得再看看”的 expiry 题材；在最小 `placebo + pre-ramp` survivor follow-up 下，它仍然稳定指向 **月度 CME 到期后 `60~120m short BTC`** 这条 exact-time 事件后漂移，因此应从 survivor 升入 `Active P2`。

## 复用产物
- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/btc_expiry_vs_friday_events.csv`
- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/bucket_summary.csv`
- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/expiry_minus_placebo_summary.csv`
