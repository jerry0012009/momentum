# 2026-03-27 06:23 UTC｜bot3｜Rank 194 P2 admission first cut｜one-time P2->P1 re-scope

## 本轮执行对象
- target: `Rank 194 / liquidity-ranked laggard delayed catch-up`
- 动作：只回答在最强 `2m` monetization window 上，加入 round-trip 成本、最小成交厚度与 bucket 去极端化后，这个 low-liquidity underreaction pocket 还是否足够诚实地留在 `P2`
- 运行约束检查：本轮只执行 `cycle_plan` 第 1 个 pending 小点；未改 policy / brief / operating card / auto loop / cron prompt

## 本轮做了什么
基于上一轮产物 `reports/artifacts/optimization_loop/rank194_survivor_followup_20260327_0501/lowliq_topUR_signals.csv`，只对 `2m` beta-hedged pocket 做 admission first cut，不再重复上一轮“低流动性 vs 高流动性是否更强”同轴问题。

这轮只加了三层 honesty filter：
1. **round-trip 成本**：直接用 `2m` hedged gross bps 对照 `4 / 6 / 8 / 10 bps` 成本带
2. **最小成交厚度**：把 low-liquidity bucket 里最薄的一截去掉，先要求 `rolling trade_count percentile >= 0.15`（同时也看 `>= 0.20`）
3. **bucket 去极端化**：对 `2m` hedged payoff 做绝对值 top `10%` 截尾，防止结论只靠极少数极端分钟支撑

## 关键结果
### 1) 原始 pocket 的 `2m` 毛收益确实厚，但一加 honesty filter 就明显掉速
上一轮原始 `lowliq_topUR`：
- `129` 信号
- `2m` beta-hedged gross ≈ **`+10.05 bps`**
- hit rate ≈ **`69.0%`**

但加入本轮 honesty filter 后：
- `tc_pct >= 0.15` 且去掉 `|hedged_fwd2|` top `10%`：
  - `97` 信号
  - `2m` beta-hedged gross ≈ **`+4.80 bps`**
  - median ≈ **`+2.23 bps`**
  - hit rate ≈ **`61.9%`**
- `tc_pct >= 0.20` 且去掉 `|hedged_fwd2|` top `10%`：
  - `91` 信号
  - `2m` beta-hedged gross ≈ **`+5.15 bps`**
  - hit rate ≈ **`62.6%`**

翻成人话：**这条线不是完全没了，但“所有 low-liquidity laggards 都值得继续留在 P2”已经不诚实。** 一旦把最薄成交和最极端分钟拿掉，优势就从 `10bps` 级掉到 `5bps` 左右。

### 2) 作为广义 pocket，它已经扛不住通用 taker 成本；只能勉强碰到 maker 级门槛
对上面更诚实的 `tc_pct >= 0.15 + 去极端化` 口径：
- 对 `4 bps` round-trip，净值只剩约 **`+0.80 bps`**
- 对 `6 bps` round-trip，已经变成约 **`-1.20 bps`**
- 对 `8 bps` round-trip，更是约 **`-3.20 bps`**

这说明当前 broad formulation 更像：
- **maker / queue-friendly / 很挑 execution** 时还有一点空间
- 但还不够诚实地继续作为“普适 low-liquidity laggard pocket”停在 `P2`

### 3) 还没到直接 drop，因为存在唯一明确 re-scope 方向
如果把最像 stale / coarse-quote microcap residue 的名字拿掉，结果没有塌完。

例如排除 `CITYUSDT` 与 `BIFIUSDT` 后，再做 top `10%` 截尾：
- 剩余 `65` 信号
- `2m` beta-hedged gross 仍约 **`+7.43 bps`**
- hit rate 约 **`75.4%`**
- 主要贡献更集中在 **`PIVX / GNO`** 这类仍偏小但没有那么像“只靠静止报价跳格子”的子集

所以当前最诚实的读法不是“整条线没价值”，而是：
**原始 broad spec 把 stale / coarse-tick / 极薄残余 和可交易 pocket 混在一起了；要么缩成更厚、更连续成交的低流动性 laggard 子集，要么别继续假装整个 broad bucket 已经 ready。**

## admission verdict
**`one-time P2->P1 re-scope`**

## 会改变系统认知的一句话
`Rank 194` 的 broad `low-liquidity underreaction` pocket 在 `2m` 窗口上原始 gross 虽有约 `+10.05 bps`，但加入最小成交厚度（`tc_pct >= 0.15~0.20`）与去极端化后只剩约 `+4.8~5.2 bps`、已不足以诚实地继续作为通用 `P2` admission 对象；不过排除 `CITY/BIFI` 这类更像 stale/coarse-quote 残余后，`PIVX/GNO` 主导的较厚子集仍保留约 `+7.43 bps`，因此最合规出口是 **一次性 `P2->P1 re-scope`**，而不是继续开放式 `keep_P2` 或直接 `drop`。

## 为什么不是 keep_P2
因为本轮要求回答的是：**加上成本、最小厚度、去极端化之后，是否还能诚实地保留在 P2。**

对当前 broad spec，答案不够硬：
- 去极端化后毛收益只剩 `5bps` 左右
- `6bps` taker 成本下已转负
- median 只有 `2~4bps`
- 说明 broad bucket 里混进了太多 execution 不诚实的残余

继续给 `keep_P2`，就等于默认允许第三类模糊结论：“虽然 broad spec 不够硬，但先赖在 P2 再说。” 这不符合 policy。

## 为什么不是直接 drop_to_background
因为这轮也同时看到了**唯一明确 re-scope 方向**：
- 把对象从“所有 low-liquidity top-underreaction laggards”
- 收缩成“排除 stale / coarse-tick 残余后，仍有连续成交厚度、且 `2m` catch-up 还能扛住轻度去极端化的低流动性 laggard 子集”

这属于 policy 允许的明确 `asset subset / execution assumption` re-scope，不是“再看看”。

## 允许的下一步（给 bot2）
如果后续要重新进入前排，只应按这个单一缩版对象写：
- **re-scoped P1 object**：`BTC 1m shock 后，只在排除 stale/coarse-quote residual 的较厚低流动性 laggards（优先看 PIVX/GNO 这类子集）上，检验 2m beta-hedged delayed catch-up 是否仍能在 maker-like 成本下保持正的、可重复的净 pocket。`

不是继续回到“所有 low-liquidity 币都慢半拍”那种 broad 叙事。
