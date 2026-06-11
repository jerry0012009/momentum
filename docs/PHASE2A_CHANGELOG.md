# Phase2a V4 Trail 参数与逻辑变更记录

> 本文件记录 Phase2a Event+V4+Trail 策略的每次参数/逻辑变更，供回测同步时参考。
> 每次变更必须注明：改了什么、为什么改、影响哪些回测参数。

---

## 2026-05-14：首批优化（基于5笔paper亏损诊断）

### 变更背景

Paper前5笔交易全部亏损（中位 -2.14%，胜率 0%）。通过1分钟K线逐笔分析发现：

1. **MFE过低**（平均仅 +0.67%），远小于2% trail阈值，价格未充分上涨即被洗出
2. **1分钟K线振幅大**（均值 151bps = 1.5%），噪音触发trail stop
3. **滑点无上限**：AINUSDT入场滑点高达 403bps，远超预期盈利
4. **仓位过大**：1000 USDT paper notional 与 75 USDT live notional 差距过大，且小币流动性不支持大单

### 变更清单

| # | 参数/逻辑 | 旧值 | 新值 | 变更原因 |
|---|-----------|------|------|----------|
| 1 | `trail_pct` | 0.02 (2%) | **0.04 (4%)** | MFE均值仅0.67%，2%太窄被噪音洗出；4%给价格更多呼吸空间 |
| 2 | `notional_usdt` (paper) | 1000 | **25** | 降低单笔风险敞口，与live对齐 |
| 3 | `notional_usdt` (live) | 75 | **25** | Jerry要求降至25U |
| 4 | `max_effective_notional_usdt` (live) | 80 | **30** | 配合notional调整 |
| 5 | `max_entry_slippage_bps` | (不存在) | **50** | 新增：入场滑点超过50bps（0.5%）直接跳过，防止追高被宰 |
| 6 | Trail判定价格源 | tick级best_bid | **5分钟K线收盘价** | 减少1分钟噪音对trail stop的敏感性 |
| 7 | 入场延迟确认 | — | **暂不修改** | V4信号本身已滞后，再延迟可能更追高；未来考虑提前入场窗口 |

### 回测同步要点

回测需要对应修改以下参数才能与paper口径对齐：

```
trail_pct: 0.02 → 0.04
notional_usdt: (回测中此参数不影响收益百分比，可忽略)
max_entry_slippage_bps: 新增过滤条件
trail价格源: 回测中使用5分钟K线close判定trail stop触发（而非tick级价格）
```

**关键**：回测中的trail stop逻辑需要从"逐tick判定"改为"逐5分钟K线close判定"。具体来说：
- 每根5分钟K线的close价格用于更新高水位和判定是否触发trail stop
- 如果5分钟K线的close ≤ 高水位 × (1 - 4%)，则触发退出
- 退出价格仍使用该K线的close（回测口径）或下一根K线的open（更严格口径）

### 代码变更位置

**配置文件**: `config/execution/phase2a_event_v4_trail_paper.json`
- line 18: `trail_pct`
- line 20: `notional_usdt`
- line 29: `max_entry_slippage_bps` (新增)
- line 43-44: live `notional_usdt` / `max_effective_notional_usdt`

**脚本文件**: `scripts/run_phase2a_event_v4_trail_paper.py`
- `open_position()` 函数 (~line 677): 新增滑点cap检查
- `fetch_latest_5m_close()` 函数 (~line 351): 新增，获取最新完成5分钟K线close
- `monitor()` 函数 (~line 1346): trail判定改用5分钟close
- `monitor_live_positions()` 函数 (~line 1258): 同上

### 预期效果

| 指标 | 变更前 | 预期变更后 |
|------|--------|-----------|
| 平均持仓时长 | ~8分钟 | 更长（5分钟K线延迟了trail触发） |
| 被噪音洗出概率 | 高（1分钟振幅1.5% vs 2% trail） | 降低（5分钟close更平滑） |
| 入场滑点极端值 | 403bps (AINUSDT) | 超过50bps的被过滤 |
| 单笔亏损幅度 | 最大 -4.45% (AINUSDT) | 受4% trail + 50bps滑点cap限制 |

### 待观察

- 4% trail是否导致利润回吐过多（如果MFE提升但退出时利润缩减）
- 5分钟close判定是否导致退出时机过于滞后
- 50bps滑点cap是否过滤掉太多交易（小币spread本身可能就偏大）

---

## 2026-05-14 | 回测 trail 触发逻辑对比分析

**变更类型**: 分析（非代码变更）

**背景**: 实盘将 trail 触发从 tick 级 bid 改为 5 分钟 close。需要验证回测中等价变更的影响。

**实验设计**: 在 1,951 笔事件+V4交易上，用 1 小时 K 线对比两种 trail 触发方式：
- **low 触发（原回测）**: K 线最低价触及 trail stop → 以 trail stop 价格离场
- **close 触发（新逻辑）**: K 线收盘价低于 trail stop → 以收盘价离场

**结果**:

| 配置 | median(0bp) | PF(0bp) | 胜率 |
|------|-------------|---------|------|
| trail 2% + low（原）| +1.42% | 11.27 | 67.5% |
| trail 2% + close（新）| -1.05% | 1.03 | 40.3% |
| trail 4% + low | -0.28% | 2.49 | 47.2% |
| trail 4% + close | -1.86% | 1.09 | 37.6% |

**结论**: close 触发在所有配置下都大幅差于 low 触发。原因：
1. low 触发等价于止损单，精确在目标价执行
2. close 触发等到收盘才判断，错过盘中反弹前的止损点，或在更低位置离场

**对实盘的影响**: 当前 Paper 使用 close_5m 判断 trail 触发，逻辑上等价于回测的 close 触发。建议改为 5 分钟内最低 bid 判断（等价于 low 触发）。

**产出**: 
- `reports/artifacts/binance_event_study_v1_6a_trail_close_vs_low/comparison.json`
- `reports/artifacts/binance_event_study_v1_6a_trail_close_vs_low/yearly_comparison.csv`
- 报告页面已更新: https://jp.jerrypsy.top/momentum/factors/paper_phase2a_event_v4_trail/report.html

---

## 2026-05-14 | 止损单等价实现 + trail_pct 回退

**变更类型**: 代码 + 配置

**背景**: 回测对比分析显示：
1. trail_pct 4% 比 2% 胜率降 20pp（67.5% → 47.2%），PF 从 11.27 降到 2.49
2. close 触发比 low 触发大幅变差（PF 从 11.27 降到 1.03）
3. Paper 交易 0% 胜率的根因是"轮询 bid"和"止损单"是两种完全不同的执行逻辑

**变更清单**:

| # | 参数/逻辑 | 旧值 | 新值 | 变更原因 |
|---|-----------|------|------|----------|
| 1 | `trail_pct` | 0.04 (4%) | **0.02 (2%)** | 回测明确显示 2% 优于 4%，回退 |
| 2 | 离场价格 | 当前 bid | **止损线价格** | 模拟 Stop-Market Order，匹配回测的 low 触发逻辑 |
| 3 | HWM 更新 | bid | **bid（不变）** | 我们无法实时知道 K 线 high，这是不可避免的差异 |
| 4 | Trail 触发 | bid ≤ trail_stop | **bid ≤ trail_stop（不变）** | 触发条件不变，变化的是离场价 |

**核心改动说明**:

`close_position()` 函数中，当 `reason == "trailing_stop"` 时：
- 旧逻辑：`exit_px = bid`（当前买一价，通常低于止损线）
- 新逻辑：`exit_px = trail_stop`（止损线价格，与回测一致）

这消除了"离场价"差异。剩余差异仅为 HWM 更新（回测用 high，实盘用 bid），影响约 1-1.5%。

**代码变更位置**:

- `scripts/run_phase2a_event_v4_trail_paper.py`:
  - `close_position()` 函数 (~line 1057): 离场价改为 trail_stop（当 reason=trailing_stop）
  - 移除所有 `close_5m` / `trail_ref` 引用
- `config/execution/phase2a_event_v4_trail_paper.json`:
  - `trail_pct`: 0.04 → 0.02

**报告页面更新**:
- 新增"回测 vs 实盘：为什么胜率差这么多？"章节
- 详细解释三个差异点（HWM、触发条件、离场价）
- 通俗比喻帮助理解
- 更新"一致与不一致"表格

