# 2026-04-01 02:57 UTC — Rank 276 P2 admission（time stability）收口：OOS 净值主要由少数周段驱动，`drop_to_background`

## 本轮执行对象
- target: `Rank 276 / BTC 15m Donchian overshoot fade × 10bps breach threshold`
- 当前层级：`Active P2`
- 本轮只执行 `cycle_plan` 第 1 个 pending 小点：`P2 admission / time stability`
- 结论：`drop_to_background`

## 本轮只回答一个问题
不是再问这条 pocket 存不存在，而是问：

> 这条 BTC 单币 overextension fade 在 OOS 的净值 / Sharpe，是否足够分散到不同时间段，还是主要靠 1~2 个 burst 周段独撑？

如果答案是后者，就不能继续把它写成稳定可纸上交易的 P2 候选。

## 方法
沿用上一轮已经 source-faithful 对齐的完全同源规格，不重复改 spec：
- 数据：source repo `data/raw/BTCUSDT_15m_raw.csv`
- 规则：`N=200`、`VOL_WINDOW=50`、`threshold=10bps`、`MAX_HOLD=40`
- `vol_filter`：rolling vol 高于 in-sample `60th percentile`
- 成本口径：延续 admission 主口径 `5bps`
- OOS 窗口：`2026-01-01 ~ 2026-02-28`

本轮新增的只是**时间切片**：把同一条 source-faithful OOS 净值拆成 month / week 贡献，检查是否为少数 burst 独撑。

## 关键结果
### 1) OOS 月度并不均匀，2 月贡献占绝大头
- `2026-01`: net `+2976.40 USD`
- `2026-02`: net `+6896.43 USD`
- OOS 合计：`+9872.83 USD`

也就是说，**接近 70% 的 OOS 净值都来自 2 月**，已经不是那种“两个自然月都比较平均地赚钱”的轮廓。

### 2) 周度贡献高度集中，头部 1 周几乎独自撑起整段 OOS
按自然周拆分后，OOS 一共只有 `9` 个周段：
- 正收益周：`4`
- 负收益周：`4`
- 零收益周：`1`

其中最关键的周度贡献如下：
- `2026-02-09 ~ 2026-02-15`: net `+7446.53 USD`
- `2026-01-19 ~ 2026-01-25`: net `+3167.84 USD`
- `2026-02-16 ~ 2026-02-22`: net `+2910.90 USD`
- `2026-01-12 ~ 2026-01-18`: net `+2336.95 USD`

而负贡献周也不小：
- `2026-02-23 ~ 2026-03-01`: net `-2605.60 USD`
- `2026-01-26 ~ 2026-02-01`: net `-2259.60 USD`
- `2026-02-02 ~ 2026-02-08`: net `-792.05 USD`
- `2025-12-29 ~ 2026-01-04`: net `-332.13 USD`

最刺眼的一点是：

> **仅 `2026-02-09 ~ 2026-02-15` 这一周，就贡献了约 `75.4%` 的全部 OOS 净值。**

换句话说，整段 OOS 并不是“周周都在稳定兑现”；它更像是**少数极端 snap-back 周段把总体成绩抬起来，其余周段有明显对冲和回吐**。

### 3) 这已经足以把它从“可 paper 的稳定边”拉回“存在 pocket 但时间上不稳”
上一轮 survivor follow-up 回答的是：
- source-faithful pocket 真实存在；
- 不是纯 coursework headline；
- OOS 到 `8/10bps` 仍然保留正值。

但本轮 time stability 新增的信息是：

> **这个 OOS pocket 的兑现并不分散，而是高度依赖少数 burst 周段。**

这会直接改变层级判断：
- 它仍然可以算“存在过 after-cost pocket”；
- 但还不足以诚实地写成当前值得继续向 `P3 / paper trade` 靠拢的稳定 admission 通过者。

## 为什么不是 `keep_P2`
因为这会把一个已经暴露出明显时间集中度的问题，继续包装成开放式 admission。

本轮已经得到足够明确的 admission 证据：
- OOS 只有 `9` 个周段；
- `4` 正、`4` 负、`1` 零；
- 头号周段独占约 `75%` 的总净值；
- 前两大正收益周相加已超过整段 OOS 总净值，说明其余周段在明显回吐。

这不是“还差一点点再看看”的形状，而是已经足够回答：

> **当前规格下，它更像 burst-dependent pocket，而不是时间上可稳定托底的 paper 候选。**

## 为什么也不是 `one-time P2->P1 re-scope`
policy 只允许在存在**唯一明确** re-scope 方向时才走 `P2->P1`。

本轮看到的只是：
- 收益对时间段高度集中；
- 可能与某类高波动 / 事件驱动周更相关；
- 但还没有唯一清楚到足以直接重写 spec 的单一方向。

现在如果硬写成：
- “只做某类周”
- “只做某类 regime”
- “只做某个 session”

都还是猜测，不是已经被这一步直接证明的唯一 re-scope。

因此最诚实的出口不是继续留在前排重猜新版本，而是：

**先回 `background/P0`。**

## 本轮 verdict
**`drop_to_background`**

### 会改变系统认知的一句话
`Rank 276` 的 source-faithful OOS after-cost pocket 虽然真实存在，但时间分布明显不稳：仅 `2026-02-09~2026-02-15` 单周就贡献约 `75%` 的 OOS 净值，且 `9` 个 OOS 周段里只有 `4` 个正周、`4` 个负周，因此它更像少数 burst 周段驱动的 pocket，而不是当前足以继续保留在 `Active P2` 甚至推进 `P3` 的稳定 paper 候选，应回 `background/P0`。

## 产物
- 时间稳定性拆分：`reports/artifacts/rank276_donchian_source_faithful_followup/rank276_time_stability_tmp.json`
