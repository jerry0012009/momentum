# Rank 235 / richest-venue routing × hysteresis funding carry — P2 admission 首项（effectiveness / cross-asset）

- 时间：2026-03-29 12:26 UTC
- 执行者：bot3 auto 13m loop
- Source record: `research/optimization_loop/2026-03-29_1215_rank235_survivor_followup_promote_p2.md`
- Object: `Rank 235 / richest-venue routing × hysteresis funding carry`
- Verdict: `blocked`

## 本轮回答的唯一问题
在统一可交易样本里，`Binance-only`、`routing-only`、`routing+hysteresis` 三条手臂里，第一性增量是否已经能在 **多币、多 venue regime** 下被诚实确认，而不是只靠极少数币或某个单一时段撑住？

## 本轮实际拿到的证据
本轮直接检查 repo 的 `strategy.py`、`strategy_cross.py` 与 `notebook_cross.ipynb` 已公开输出，只使用其中已经显式写出的结构化结果。

### 1) cross-asset 覆盖不是单币 pocket
repo 的 cross 版本固定使用 7 币共同样本：
- `BTCUSDT`
- `ETHUSDT`
- `SOLUSDT`
- `BNBUSDT`
- `XRPUSDT`
- `DOGEUSDT`
- `AVAXUSDT`

`notebook_cross.ipynb` 对 2023+ 给出的 `Binance` vs `best exchange` 平均 8h funding 对比显示，7 个币全部都存在正的 richest-venue uplift，而不是只有 1~2 个币有效：

| Symbol | Binance FR (bps) | Best FR (bps) | Uplift (bps) |
|---|---:|---:|---:|
| BTCUSDT | 0.76 | 5.70 | +4.94 |
| ETHUSDT | 0.80 | 5.96 | +5.16 |
| SOLUSDT | 0.57 | 6.65 | +6.07 |
| BNBUSDT | -0.17 | 6.22 | +6.40 |
| XRPUSDT | 0.80 | 7.27 | +6.47 |
| DOGEUSDT | 0.83 | 8.12 | +7.28 |
| AVAXUSDT | 0.50 | 6.88 | +6.38 |

聚合后：
- Mean Binance 8h FR = `0.59 bps`
- Mean best-exchange 8h FR = `6.68 bps`
- Cross-exchange uplift = `+6.10 bps / 8h`（`+1041.6%`）

这说明 **routing uplift 本身是 broad-based 的**，并非显著集中在极少数币。

### 2) venue regime 也不只是一段偶然 pocket
repo 的分 regime 输出：
- `2020-01 → 2022-12`（仅 Binance）：`CAGR 3.8%`, `Sharpe 1.52`
- `2023-01 → 2023-05`（+ GateIO）：`CAGR 21.9%`, `Sharpe 5.64`
- `2023-05 → 2023-08`（+ Hyperliquid 刚加入）：`CAGR 3.0%`, `Sharpe -27.96`
- `2023-09 → 2026-02`（All 3 stable）：`CAGR 27.6%`, `Sharpe 4.02`, `Max DD 0.6%`

这表示当前对象的主增量并不是“单一短 pocket 恰好碰巧”，而是 **在三 venue 稳定共存后的主要区间里表现最强**。

### 3) 但 repo 仍然没有把本轮要求的 `routing-only` 手臂单独跑出来
这轮小点要求的关键不是只看 `cross-exchange net` 与 `Binance-only net` 的翻转，而是要把三条手臂拆开：
- A: `Binance-only`
- B: `routing-only`
- C: `routing + hysteresis`

repo 已显式给出：
- `Binance-only net = -10.0% CAGR`（2023-09+）
- `Cross-exchange net = +27.8% CAGR`（2023-09+）
- `Cross-exchange gross = +30.3% CAGR`（2023-09+）

但 **没有单独给出 B 手臂（routing-only, no hysteresis）的 post-cost 结果表**。`strategy_cross.py` 的注释只说明：
- `z_exit = z_entry` = 无 hysteresis 的旧行为
- `z_exit = 0 + min_hold = 3` 的作用是 `dramatically reducing turnover and fee drag`

这足够证明 hysteresis 是执行层的重要净化器，但还不足以回答本轮最核心的 admission 问题：

> `routing-only` 在统一成本后，是否已经能够在多币、多 venue regime 下保持正净边？

目前 repo 公开输出只能证明：
- routing uplift 在 7 币上是广泛存在的；
- `routing+hysteresis` 的整体验证在稳定三 venue 区间里很强；
- 但还不能把 `routing-only` 的成本后生存性直接钉死。

## 为什么本轮必须标记 blocked
这不是因为对象失效，而是因为 **这一条 evidence axis 缺最后一个必须显式存在的 B 手臂结果**。

如果没有 `routing-only` 独立表，就不能诚实完成本轮 success criterion 里那句：
- 要么确认 `routing-only` 已在多币/多 venue regime 下保留正净边；
- 要么确认 uplift 其实只是假象，应转向 `P1 re-scope / P0`。

现在能确认的是“routing uplift 很广、不是单币 pocket”；
但还 **不能** 仅凭现有 repo 输出，把 `routing-only` 直接判成已通过这一轮 admission。

## 改变系统认知的一句话
**Rank 235 的 routing uplift 已确认不是单币或单一 venue pocket：7 币全部存在 `best-exchange` 相对 Binance 的正 funding uplift，且 strongest performance 出现在 `2023-09+` 三 venue 稳定共存区间；但 repo 仍缺失 `routing-only` 独立 post-cost 手臂，因此这一条 `effectiveness / cross-asset` admission 轴目前只能诚实记为 `blocked:missing-routing-only-arm`。**

## 对 runtime 的直接含义
- `Rank 235` 不应因本轮证据被降到 `P1/P0`；
- 但也 **不能** 因这条 axis 单独通过就直接写成 `P3 admission passed`；
- 下一步若继续推进，必须由后续小点去完成 `time / parameter / honesty / realized carry` 的出口式判断，或补出 `routing-only` 独立手臂后再回到这条 axis。