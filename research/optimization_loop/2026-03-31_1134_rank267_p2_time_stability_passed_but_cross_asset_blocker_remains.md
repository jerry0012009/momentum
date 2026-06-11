# Rank 267 P2 admission：time stability 通过，但 majors cross-asset blocker 仍未解除

- 时间：2026-03-31 11:34 UTC
- 对象：Rank 267 / crypto factor momentum × size/vol rotation
- 任务类型：P2 admission / time stability
- 结论：`done`（结论为 `time stability passed，保留出口决策中的 promote_P3 倾向，但不能覆盖已有 cross-asset blocker`）

## 本轮只执行这一个小点
按 `BOT2_BOT3_STATE.md` 当前最前的 pending 小点，只检查同一套已知最强骨架在时间切片上的连续性；不重复 cross-asset 轴，不新增 factor sleeves，也不扩表成新的 effectiveness 叙事。

固定口径：
- market：Binance USDⓈ-M perpetual
- universe：沿用 Rank 267 当前 24 个高流动 USDT perp 样本
- bar：`4h`
- ranking：`7d`
- holding：`24h`
- rotation：`1d` sleeve-level winner rotation
- sleeves：`momentum / size / low-vol`
- 成本：统一按单边 `10bps`
- time split：把可交易 rebalance 窗口等长切成 `early / mid / recent` 三段

原始 artifact：
- `reports/artifacts/rank267_time_stability_20260331/rank267_time_stability_summary.json`

## 关键结果
### 1) 不是“只靠最近一段才突然赚钱”
最佳 rotation（`7d rank + 24h hold + 1d sleeve rotation`）在三段样本里都保持正的成本后均值：
- `early`：`+78.13 bps/period`，hit rate `60.78%`
- `mid`：`+224.24 bps/period`，hit rate `65.09%`
- `recent`：`+187.82 bps/period`，hit rate `61.21%`

这说明当前 edge **不是单一近期窗口幻觉**。最强阶段确实在中段，但最近一段并没有塌回手续费边缘，早段也不是负值。

### 2) 静态 sleeves 的时间表现更不稳，但 rotation 在三段里都起到了收口作用
分段后的静态 sleeve 均值：
- `early`：`momentum -50.94` / `size -21.97` / `low-vol -70.96 bps`
- `mid`：`momentum +167.70` / `size +139.91` / `low-vol +122.46 bps`
- `recent`：`momentum +113.95` / `size -12.89` / `low-vol -29.02 bps`

也就是说，若只盯单个 sleeve，会看到明显 regime 依赖；但当前对象真正要进 admission 的主语本来就是 **3-sleeve winner rotation**。在这个口径下，它并没有表现出“只在最后一段突然活过来”的问题。

### 3) rotation 的选 sleeve 也不是最近才单点押注
三段的 winner picks：
- `early`：`momentum 112 / size 77 / low-vol 43`
- `mid`：`momentum 124 / size 59 / low-vol 49`
- `recent`：`momentum 121 / size 56 / low-vol 55`

pick 分布说明它并非最近才被某一个 sleeve 单点拯救；虽然 `momentum` 始终是主导，但 `size / low-vol` 也持续被轮到，符合“sleeve-level rotation 在不同阶段切换”的原始叙事。

## admission 结论
这一步改变的系统认知是：

> `Rank 267：time stability passed；当前最佳 3-sleeve winner rotation 在 early / mid / recent 三段样本里都保持正的成本后均值，不属于只靠最近单一窗口抬出来的幻觉，因此在时间维度上仍保留 promote_P3 倾向。`

但这一步**没有**推翻上一轮已经明确的 blocker：

> `majors cross-asset 不成立，当前净边仍主要由 ex-majors alt basket 支撑。`

因此，本轮应把对象理解为：**时间维度过关，但 cross-asset blocker 依旧存在，P2 已累计到第二次连续 keep_P2；下一步不得再做第三次开放式 keep_P2，而必须把 parameter + honesty 小点收口成明确出口决策。**

## 对 runtime 的直接影响
- `cycle_plan` 第 2 项应写为 `done`
- 当前小点 `result` 应写为 `Rank 267：time stability passed，保留 promote_P3 倾向，但 majors blocker 仍在`
- `Active P2` 的计数应推进到：
  - `p2_rounds_since_level_change: 2`
  - `p2_consecutive_keep_p2: 2`
  - `p2_last_evidence_axis: time_stability`

## 本轮出口句
`Rank 267：time stability passed；当前最佳 3-sleeve winner rotation 在 early / mid / recent 三段样本里都保持正的成本后均值，不是只靠最近单一窗口抬出来的幻觉，因此在时间维度上仍保留 promote_P3 倾向；但 majors cross-asset blocker 仍未解除，下一轮必须把 admission 收口成明确出口决策。`
