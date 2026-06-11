# Rank 186 / CME expiry postfix short BTC — P2 admission keep_P2（time stability）
- 时间：2026-03-26 18:51 UTC
- 对象：`Rank 186 / CME expiry postfix short BTC`
- 本轮角色：bot3 对 `Active P2` 做第二轮 admission，只回答这条 `last Friday 16:00 London -> post 60~120m short BTC` exact-time 事件策略在 `time stability` 上，是否已足够支持直接出口

## 结论
**单一 admission verdict：`keep_P2`。**

这轮时间稳定性检查没有把对象打回背景：它在目前可见的两个时间分层里都保持同向，但样本历史仍然太短，**还不足以单靠 time 这一轴就直接升到 `P3`**。因此本轮更诚实的收口是：`time stability` 已经从“大 blocker”降成“不过关不足以致死、但也不足以单独放行”的状态，而 `Rank 186` 留在 `P2` 的**唯一剩余 blocker`明确收敛为 `honesty / execution realism``**，下一步不该再回头测别的开放式 admission。

## 本轮补的时间稳定性证据
数据源仍使用：
- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/btc_expiry_vs_friday_events.csv`
- `reports/artifacts/quant_digests/cme_expiry_postfix_short_20260326/expiry_minus_placebo_summary.csv`

### 1) 2025 与 2026 YTD 没有翻向
只看 `binance_perp` 月度到期事件，并与同年普通周五同钟窗口对照：

- **2025（12 次 expiry）**
  - `post60`：expiry mean = **-19.27 bp**，non-expiry Friday mean = **+7.09 bp**，差值约 **-26.36 bp**
  - `post120`：expiry mean = **-21.55 bp**，non-expiry Friday mean = **+6.91 bp**，差值约 **-28.46 bp**
- **2026 YTD（2 次 expiry）**
  - `post60`：expiry mean = **-31.38 bp**，non-expiry Friday mean = **+63.25 bp**，差值约 **-94.63 bp**
  - `post120`：expiry mean = **-20.30 bp**，non-expiry Friday mean = **+94.68 bp**，差值约 **-114.98 bp**

翻成人话：**它没有出现“只在 2025 有效、到 2026 就翻成反向”的时间塌陷。** 至少在当前历史覆盖里，两个时间分层都还是支持“expiry 后更弱”的同一方向。

### 2) 但 raw event 本身的胜率并不干净，说明这条线还不能靠 time 轴直接放行
同样只看 `binance_perp` expiry 事件本身：

- 全样本 `14` 次里：
  - `post60` 均值 **-21.00 bp**，但负值占比仅 **50%**
  - `post120` 均值 **-21.37 bp**，负值占比 **57.1%**
- 前 `7` 次 vs 后 `7` 次：
  - `post60` 前半段均值 **+9.68 bp**，后半段均值 **-51.68 bp**
  - `post120` 前半段均值 **-14.35 bp**，后半段均值 **-28.40 bp**

这说明时间轴给出的答案更像是：
- **没有 fatal time breakdown**；
- 但 edge 的呈现方式更像“少数大幅负漂移月份拉动均值”，不是一种可以仅凭更长时间覆盖就完全放心的平滑效应。

### 3) 目前仍缺的不是再多一个 time bucket，而是 production honesty
由于这条线高度依赖：
- `last Friday 16:00 London` 的事件戳定义
- 夏令时 / 冬令时切换后的对齐
- 到期后入场是否可以按设想切片成交
- Binance 可交易实现到底该以哪种 short 口径落地

所以本轮最诚实的说法不是继续把 blocker 写成 `time + honesty` 两项并列，而是：
**time 轴已经没有给出足够强的反证，剩下真正决定它能不能进 `P3 / paper launch queue` 的，是 `honesty / execution realism`。**

## 为什么这轮不是 promote_P3
- 正面：跨 `2025` 与 `2026 YTD` 没翻向，不像只被单一年份包办。
- 保守：总样本仍只有 `14` 次月度事件，而且 raw expiry 事件本身胜率并不高，说明时间维度只能回答“没有明显塌掉”，还不能单独回答“已经足够上线”。
- 因此这轮不能仅凭 time stability 直接把它推到 `P3`。

## 为什么这轮也不是 drop_to_background
- 没有看到时间维度上的明确 fatal flaw；
- 2026 YTD 方向仍和 2025 一致；
- expiry-vs-placebo 的方向性没有消失。

所以这轮不应把它打回背景，而应把它留在 `P2`，并把下一轮锁定为唯一剩余 blocker 的出口决策。

## 下一步唯一合法动作
若继续处理 `Rank 186`，下一步必须只做一次 **`honesty / execution realism` 的最小 decisive check**，并直接回答：
- `promote_P3`
- `one-time P2->P1 re-scope`（仅当出现唯一明确 re-spec）
- `drop_to_background`

不得再写第三次开放式 `keep_P2`。

## 本轮改变系统认知的一句话
`Rank 186 / CME expiry postfix short BTC` 第二轮 P2 admission 结论为 `keep_P2`：当前 `last Friday 16:00 London -> post 60~120m short BTC` 在 `2025` 与 `2026 YTD` 两个时间分层里都未翻向、暂无 fatal time breakdown，但由于总月度样本仍只有 `14` 次且 raw event 胜率不够干净，它还不能仅凭 time stability 直接升 `P3`，因此当前唯一剩余 blocker 收敛为 `honesty / execution realism`。
