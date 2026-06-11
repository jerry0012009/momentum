# Rank 352 / BTC perp conditional drift survivor follow-up -> background / P0

- Time: 2026-04-06 12:31 UTC
- Target: `Rank 352 / BTC perp conditional drift`
- Action: survivor slot 的唯一一次便宜但 decisive clean-room follow-up
- Verdict: `background / P0`
- Artifact dir: `reports/artifacts/rank352_survivor_followup_20260406_1231`

## What I tested

按 intake 里承诺的最小壳，直接做了不依赖论文 full model zoo 的 clean-room proxy：

- 标的：`BTCUSDT` Binance USDⓈ-M perpetual
- 数据：Binance data vision 月度 `klines`
  - `5m`: `2025-10` ~ `2025-12`
  - `15m`: `2025-10` ~ `2025-12`
- 信号：`score = μ̂ / σ̂`
  - `μ̂`：EWMA return mean
  - `σ̂`：EWMA realized vol
- 预测窗口：`H = 1 / 2 / 3 bars`
- 检查项：
  1. `score` 分桶是否给出稳定单调性
  2. top-bottom spread 是否为正
  3. 极端 decile 顺势交易在 taker 成本后是否仍有净边
- 成本口径：显式 taker round-trip `4 bps`（单边 `2 bps`）

## Headline result

这条对象没有通过 survivor 轮的诚实出口检查：

> `5m/15m` 的 `EWMA mean / EWMA vol` clean-room proxy 虽然在个别 horizon 上能看到很弱的分桶方向性，但极端 decile 顺势收益只有 `0.14 ~ 0.72 bps` gross，统一远低于 `4 bps` taker round-trip 成本；同时分桶单调性不稳定、两端桶还多次出现 sign flip，说明这条 edge 目前更像噪音里的条件筛选，而不是可迁移的单资产 conditional-drift raw alpha。

因此这一步必须直接收口，`Rank 352` 不升 `P2`，用完 survivor 唯一 follow-up 后退回 `background / P0`。

## Key metrics

### 5m

| horizon | top-bottom spread (bps) | extreme gross side ret (bps) | extreme net after 4bps RT | bucket corr |
|---|---:|---:|---:|---:|
| 1 bar | -0.28 | -0.14 | -4.14 | -0.16 |
| 2 bars | -0.03 | -0.02 | -4.02 | -0.09 |
| 3 bars | 0.39 | 0.20 | -3.80 | 0.22 |

观察：
- `5m` 上最好的也只是 `H=3` 时 `0.20 bps` gross side ret；
- 两端 decile 并没有形成稳定“越极端越顺势”的结构；
- `H=1/2` 甚至连 gross spread 都接近零或为负。

### 15m

| horizon | top-bottom spread (bps) | extreme gross side ret (bps) | extreme net after 4bps RT | bucket corr |
|---|---:|---:|---:|---:|
| 1 bar | 0.79 | 0.39 | -3.61 | 0.32 |
| 2 bars | 1.24 | 0.62 | -3.38 | 0.44 |
| 3 bars | 1.45 | 0.72 | -3.28 | 0.49 |

观察：
- `15m` 看起来比 `5m` 稍好，但 gross 仍然只有 `0.39 ~ 0.72 bps`；
- 扣掉 `4 bps` round-trip 后全部显著为负；
- 分桶内部仍频繁出现非单调、局部桶 sign flip，说明这不是一个干净的 `μ̂/σ̂ -> next return` 连续映射。

## Why this is enough to exit

这一步的目标不是证明“论文一定错”，而是回答更小、更诚实的问题：

> 用最便宜的 `EWMA mean / EWMA vol` 代理，能不能先在 `5m/15m` 上留下一个成本后仍站得住的单资产 conditional-drift 壳？

当前答案是否定的，原因足够直接：

1. **成本后不成立**：gross edge 量级远低于 taker 成本，不具备进入 `P2` 的最小 admission 价值。
2. **分桶不干净**：即便 `15m` 有一点相关性，桶内仍明显抖动，极端分位没有稳定“越极端越好”的结构。
3. **主语没有被 clean-room proxy 保住**：如果一条 supposed raw alpha 只能在论文复杂建模叙事里成立，而在最小代理上连 post-cost sign 都站不住，它现在更像“条件筛选 + 参数/口径敏感”而不是可迁移主语。

## Runtime result sentence

> `Rank 352 / BTC perp conditional drift` 的 survivor follow-up 已诚实收口：`5m/15m` 上 `EWMA mean / EWMA vol` 版 `score=μ̂/σ̂` 虽有零散分桶相关性，但极端 decile 顺势收益仅 `0.14~0.72 bps` gross、显著低于 `4 bps` taker round-trip 成本，且单调性不稳定，因此对象不升 `P2`，用完唯一 follow-up 后直接退回 `background / P0`。

## Files written

- `reports/artifacts/rank352_survivor_followup_20260406_1231/BTCUSDT_5m_klines.csv`
- `reports/artifacts/rank352_survivor_followup_20260406_1231/BTCUSDT_15m_klines.csv`
- `reports/artifacts/rank352_survivor_followup_20260406_1231/BTCUSDT_5m_signals.csv`
- `reports/artifacts/rank352_survivor_followup_20260406_1231/BTCUSDT_15m_signals.csv`
- `reports/artifacts/rank352_survivor_followup_20260406_1231/bucket_summary.csv`
- `reports/artifacts/rank352_survivor_followup_20260406_1231/summary.json`
