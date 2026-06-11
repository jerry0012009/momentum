# Rank213 rollout progress

更新时间：2026-05-10

## Cross-strategy close-out note（2026-05-10）

`Rank 154 / Crypto-Stat-Arb` 与 `Rank154b / young funding continuation` 已正式关闭并归档，不再作为当前 paper / P2 / release candidate 推进。最终入口：`docs/RANK154_ARCHIVE_CLOSEOUT.md`，网页：`paper/rank154_archive_closeout.html`。本 `progress.md` 的主体仍是 Rank213 rollout；154 系列只在这里保留一条交叉项目状态提示，避免后续误把旧 paper runner 当成当前活跃主线。

## 版本命名规范

| 版本号 | 策略名称 | Universe | Cadence | Legs | 状态 |
|---|---|---|---|---|---|
| **213a** | `rank213_largecap_xs_jump_veto` | frozen30 (静态) | 15m | 3L3S | archived |
| **213b** | `rank213_age90_14d_skip1d_voladj` | monthly_volume_top30 | daily | 3L3S | superseded |
| **213c** | `rank213_age90_top50_4x4` | monthly_volume_top50 | daily | 4L4S | **live canary** |

命名规则：213 为原始 Rank 编号，a/b/c 按演进顺序递增。重大参数调整（universe 扩大、leg 数变化、信号公式修改）升级版本号。子版本可用 213c1、213c2 表示参数微调。

详见版本总览页：`paper/rank213_version_overview.html`

## 当前活跃策略

**213c: `rank213_age90_14d_skip1d_voladj_top50_4x4`** — 日频动量多空，已接入真钱 canary。

- 状态：**live canary active**；2026-05-06 已完成 3L3S 首次真钱 entry/exit 测试，后续正式窗口切换到 Top50 4L4S
- 信号公式：`return(t-15d → t-1d) / realized_vol(t-15d → t-1d)`
- Universe：上月 Binance UM perp 1d quote_volume Top50，age ≥ 90 天
- 持仓：daily rebalance，4 long + 4 short，等权 $20/leg，$160 gross
- Entry：maker limit ±2bps，20s TTL，market fallback
- Exit：horizon_only market order at decision_ts + 1d（00:00 UTC next day）
- Gate：eligible universe ≥ 6

## 关键入口

| 入口 | 路径 / URL |
|---|---|
| **版本总览页** | `paper/rank213_version_overview.html` |
| **213c 架构与组件分析页** | `paper/rank213c_architecture.html` |
| 213c 执行成本与稳定性 | `paper/213c_execution_stability.html` |
| 213c 第五轮利润厚度 | `paper/213c_round5_thickness.html` |
| 213c Buffer 专题研究 | `paper/213c_buffer_research.html` |
| 213c 研究路线图 | `paper/213c_roadmap.html` |
| Evidence map | `paper/rank213_evidence_map.html` |
| 信号引擎 | `scripts/rank213_age90_signal_engine.py` |
| Shadow runner | `scripts/run_rank213_age90_daily_shadow_runner.py` |
| Live canary wrapper | `scripts/run_rank213_age90_live_canary.py` |
| 共享执行引擎 | `scripts/run_rank213_largecap_xs_jump_veto_live_canary.py` |
| 执行配置 | `config/execution/rank213_age90_live_canary.yaml` |
| 213c Live Launch | `paper/213c_live_launch.html` |
| 213c Shadow Runner | `paper/213c_shadow_runner.html` |
| 213c Short Leg 研究 | `paper/213c_short_leg_research.html` |

## 审计结论（2026-05-06）

明早首次真钱运行前已完成全面审计：

| 检查项 | 结果 |
|---|---|
| 信号公式一致性 | **通过** — live engine 已切 Top50 4L4S，新 shadow 产出 4L+4S、eligible=44 |
| Universe 动态 fallback | **通过** — monthly CSV 只有 Top30 时，live engine 会动态计算 Top50 |
| Horizon 时间对齐 | **通过** — `planned_exit_ts = decision_ts + 1d = 00:00 UTC` |
| Entry Window 时序 | **通过** — shadow(00:01) → canary(00:02:15) → window(00:02-00:10) |
| Gate 逻辑 | **通过** — 回测和实盘都只检查 `eligible >= 6` |
| Basket 构造 | **通过** — 4L+4S 等权中性，20U/leg |

已知设计层面差异（不可消除，需接受）：entry 价格偏离 close 几个 bps（maker limit vs close）、exit 价格偏离 close 几个 bps（market order vs close）、成本假设 4bps flat vs 实际 maker 2bps / taker 5bps。

## 旧版 15m 策略（archived）

旧版 `rank213_largecap_xs_jump_veto`（15m cadence、3h hold、frozen30 universe）已完成执行链路开发但**不再作为当前活跃策略**。主要遗留价值：

- 共享执行引擎 `run_rank213_largecap_xs_jump_veto_live_canary.py` 被 age90 复用
- Maker-first + TTL fallback + horizon close 的完整 entry/exit 语义
- Basket safety、residual reconciliation、exchange-truth 对账机制
- Live-vs-backtest checklist 框架

旧版 15m 策略在 monthly_volume_causal 口径下 plain baseline 为 -98.09%，baseline+veto+gate 为 -37.13%，已不适合继续推进。详见 `docs/RANK213_EVIDENCE_MAP.md`。

## age90 策略研发历程

### Phase 1: 第二轮验证（second_round_validation）
- 样本：monthly_volume_top30，age ≥ 90d，score = return(14d skip 1d) / vol
- 结果：最强 replacement-baseline 候选，但仍有成本敏感、2022-2023 弱势问题
- 页面：`paper/rank213_age90_14d_second_round_validation.html`

### Phase 2: Phase 3 执行/前瞻验证
- 新增 15m TWAP/VWAP 执行压力测试
- 新增 predeclared gates、walk-forward 稳定性检查
- 结论：**不通过 live promotion** — 高回撤、成本敏感、空头归因弱
- 页面：`paper/rank213_age90_14d_phase3_validation.html`

### Phase 3: 实盘部署（当前）
- 用户决定在 Phase 3 未通过的情况下先跑 tiny-live canary；2026-05-06 后根据第四轮扩展研究切换到 Top50 4L4S
- 信号引擎 `rank213_age90_signal_engine.py` 独立实现，与回测口径一致
- 复用 15m 策略的共享执行引擎，配置切到 daily cadence
- 3 个 systemd timer：shadow runner (00:01)、live canary (00:02:15)、pending manager (5s)

### Phase 4: Top50 4L4S 切换（2026-05-06）

- 第四轮扩展显示 `Top50 + 4L4S` 是当前最强候选：flat 4bps/day 累计 +1283.52%，最大回撤 -42.65%
- flat 12bps/day 仍为 +127.25%，flat 16bps/day 转负，说明真实成本必须严控
- live engine/config 已切为 Top50 4L4S；下一次正式 UTC 日线 entry window 开始使用新 basket
- 页面：`paper/213c_execution_stability.html`

### 213c 架构与组件分析页（2026-05-07）

- 将五轮研发的分散结果整合为单一架构页面，标准化评价指标（净收益bps、累计收益%、最大回撤%、夏普、胜率%、换手x、多空半边收益bps）
- Baseline 定义：Top50 4L4S，flat 4bps → 14.52 bps / 1283.52% cum / -42.65% DD
- 组件评估：Buffer（有效，buffer8 最优但可能过拟合）、Short Gate（边际改善）、Turnover Control（降换手有效）、Capital Mix（仅诊断用）、Dispersion（监控标签）
- 过拟合风险评估：~76 变体测试，~3.8 个预期假阳性，buffer 机制方向稳健但 buffer8+weekly 组合可能过拟合
- 页面：`paper/rank213c_architecture.html`

### 页面目录全面重命名（2026-05-07）

- 36 个 rank213 页面全面重命名：`213x_short_name.html` 格式，版本前缀统一
- 213a（21 页，frozen30 归档）、213b（2 页，Top30 3L3S）、213c（9 页，Top50 4L4S 当前）、跨版本（3 页）
- 所有内部 href 链接已更新，版本总览页已建立完整分类目录
- 命名规则：`213x_` 前缀 + 语义化简写，如 `213c_execution_stability.html`

### Short Leg Gate 深度研究（2026-05-07）

- 目标：在 4bps+ 成本假设下，研究不同 gate 和仓位控制是否能改善 213c short 腿
- 24 个变体（21 新 + 3 参考），5 组：组合 AND gate、阈值 gate、自适应仓位、新指标 gate、weekly 组合
- 全样本最佳 @ 4bps：`buffer8_weekly_short_btc_prior7_positive` = 8.95 bps（Watch，DD -54.63%）
- 新变体中 Promising：`buffer8_adaptive_cap_btc_regime_3level` = 7.23 bps（DD -47.58%）
- **Walk-forward 验证结果**：IS 表现好的变体 OOS 普遍变差或变负，过拟合风险显著
  - `buffer8_eligible_prior7_negative_AND_dispersion_mid_high` 被选中 3/5 folds，IS mean 12-34 bps，OOS mean -10.71 bps
  - 没有变体在 OOS 中稳定正收益
- 累计变体数 ~100，预期 ~5 假阳性 @95%
- 关键发现：**短期 gate 优化的过拟合风险极高，不建议基于全样本结果调整 short 腿参数**
- 页面：`paper/213c_short_leg_research.html`
- 脚本：`scripts/build_rank213c_short_leg_depth_study.py`

### 首次真钱测试（2026-05-06 07:40 UTC）

- 手动触发 live canary，临时扩大 entry window 至 100000s
- 6 条腿全部成交：2 条 maker fill（ZEC、1000PEPE），4 条 TTL fallback to market（DOGE、ENJ、ARIA、TRUMP）
- Basket: DOGE/ZEC/1000PEPE long + ENJ/ARIA/TRUMP short，$20/leg
- Exchange reconciliation: 6/6 claimed, 0 residual, 0 qty_mismatch
- Horizon close: 2026-05-07T00:00:00Z

### Horizon Close 手动测试（2026-05-06 10:18 UTC）

- 修改 `live_state.json` 中所有 `planned_exit_ts` 为已过去时间 `2026-05-06T08:00:00Z`
- 运行 canary，horizon close 逻辑检测到 `now >= planned_exit_ts` 后提交 6 笔 market close
- 结果：**6/6 平仓全部 FILLED**
  - DOGEUSDT long: entry 0.11611 → exit 0.1162, +$0.02
  - ZECUSDT long: entry 585.05 → exit 572.59, -$0.42
  - 1000PEPEUSDT long: entry 0.0042406 → exit 0.0042682, +$0.13
  - ENJUSDT short: entry 0.04986 → exit 0.05002, -$0.06
  - ARIAUSDT short: entry 0.0596 → exit 0.0601, -$0.17
  - TRUMPUSDT short: entry 2.393 → exit 2.449, -$0.47
- Total PnL: **-$0.98**（含 entry/exit 成本）
- Exchange reconciliation: 0 positions, 0 residual, 0 qty_mismatch
- Basket status: closed

**关键发现**：修改 state 文件后必须先停止 pending manager timer（5s cadence），否则 timer 会覆盖修改。

**发现并修复的 bug**：
1. **`collect_exchange_open_positions()` 空 universe 过滤**（`run_rank213_largecap_xs_jump_veto_live_canary.py:1276`）：当 `cfg.universe.symbols` 为空（动态 universe）时，所有仓位被过滤掉，导致 exchange snapshot 始终为 `[]`。修复：`if enabled and symbol not in enabled` 替代 `if symbol not in enabled`。这个 bug 会导致 reconciliation 无法检测残仓和 qty mismatch。

### Delta Rebalance 实盘测试（2026-05-06 16:37-16:41 UTC）

- 新增 `rebalance.mode=delta_symbol_side`：同标的同方向只 carry，不平再开；剔除/反向腿先平；新增腿再开；小额 notional 漂移暂不 resize。
- 新增 BTC/大最小开仓额适配审计字段：每条新 entry 记录 `requested_target_notional_usdt`、`adjusted_target_notional_usdt`、`exchange_effective_min_notional_usdt`、`min_notional_buffer_mult`。
- 小额实盘流程完成：
  - 开仓：Top50 4L4S 8/8 live，$20/leg，maker 未成交腿按 TTL fallback。
  - 换仓：保留 SKYAI/DOGE/ZEC/ENJ/XPL/ARIA，平 PENGU long + TRUMP short，新开 ORCA long + NEAR short。
  - 修复状态 bug：carry 后 `basket_id` 曾被 metadata 还原为旧 basket；已改为 rebalance-carried row 不再被旧 metadata 覆盖。
  - 平仓：8/8 manual market close filled。
- 最终状态：exchange open positions = 0，pending = 0，live = 0，residual = 0，qty_mismatch = 0。
- 测试结束后已关闭 `rebalance.allow_manual_test_window_override=false`。

## Delta Rebalance 优化与 Horizon Close 修复（2026-05-08）

**问题**：两个关联问题：
1. 时序竞争：horizon close 在 sync 中自动平掉所有旧仓，delta rebalance 在 sync 之后才运行，来不及做 carry/close/open
2. 不必要换仓：即使新旧 basket 完全相同，也会全量平仓再全量开仓，产生大量交易成本

**修复**：当 `rebalance.enabled = true` 时，跳过 `sync_phase6_runtime` 中的 horizon close，让 delta rebalance 统一管理持仓生命周期。
- `rank213_manage_live_positions` 添加 `skip_horizon_close` 参数（line 2080）
- `sync_phase6_runtime` 传递 `skip_horizon_close`（line 2408）
- canary main() 根据 `rebalance_cfg.enabled` 设置 `skip_hz`（line 2941）
- 删除了之前的时序 bug fix（`had_active_basket_at_run_start` 重置逻辑）

**效果**：
- 新旧 basket 完全相同 → carry 8 条腿，0 close，0 open（零换仓）
- 新旧 basket 部分相同 → carry 匹配腿，只 close/open 差异腿
- 新旧 basket 完全不同 → 等价于全量换仓

**待办**：需要禁用 pending manager timer（它没有 skip_horizon_close，会在 delta rebalance 之前平掉持仓）：
```bash
systemctl stop momentum-rank213-age90-live-pending.timer
systemctl disable momentum-rank213-age90-live-pending.timer
```

**已完成**：pending manager timer 已禁用（2026-05-08）。

**P&L 复盘**：实盘总净亏损 -12.50 USDT（24 笔），主要来自 05-07 basket（-10.90 USDT）：
- HIGH short +25.2%（-5.06）、SKYAI long -22.5%（-4.37）为最大亏损
- 这是市场风险（极端波动），不是执行问题
- 实际手续费 ~6 bps/leg RT（硬编码估算，不含 slippage）
- 真实成本（含 slippage）估计 15-25 bps/leg RT，策略 alpha 薄弱

## 当前 blocker / 下一步

1. ✅ Entry 全流程已验证（6/6 legs filled）
2. ✅ Horizon close 全流程已验证（6/6 legs closed）
3. ✅ Delta rebalance 全流程已验证（carry / close removed / open added / final close）
4. ✅ Horizon close 时序 bug 已修复（2026-05-08）
5. ✅ Delta rebalance 集成到 basket 过渡流程（skip_horizon_close）
6. ✅ Pending manager timer 已禁用（避免干扰 delta rebalance）
7. 等待 05-09 00:02:15 验证：首次 entry 应走 Path A（fresh open），05-10 起应走 delta rebalance（carry/close/open）
8. 接入交易所账单 API，获取精确手续费（当前 6 bps 是硬编码估算）
9. 单独记录 slippage（entry/exit signal→fill 偏差）
10. 积累 50+ 笔样本后做 go/no-go 决策（真实成本 vs alpha）
11. 基于实盘数据决定是否扩大 notional 或放弃策略

## 关键经验

- **版本命名规范**：213a (frozen30) → 213b (Top30 3L3S) → 213c (Top50 4L4S)。每次重大参数调整升级版本号，便于团队沟通和文档管理。

- 动态 universe（`universe.symbols` 为空）会导致 `collect_exchange_open_positions()` 过滤掉所有仓位。当 config 使用动态 universe 时，必须确保 exchange snapshot 不依赖静态 symbol 列表。

- 手动修改 state 文件前必须先停止 pending manager timer（`systemctl stop momentum-rank213-age90-live-pending.timer`），否则 5s cadence 的 timer 会覆盖修改。

- `had_active_basket_at_run_start` 是"延迟一轮"门控：即使 sync 在同一 run 中平掉所有旧仓，仍通过 `turnover_close_only` 阻止新 entry。当 canary 是唯一执行 horizon close 的进程时，这会导致新 basket 丢失 entry window。修复：sync 后如果旧仓全部清空，重置该 flag。

- 实盘手续费估算（`ESTIMATED_FEE_BPS_ROUND_TRIP = 6.0`）是硬编码常量，不含 slippage。真实 round-trip 成本（含 entry/exit slippage）估计 15-25 bps。需接入交易所账单 API 获取精确数据。

- horizon close 和 delta rebalance 不能共存：如果 sync 中的 `rank213_manage_live_positions` 先平掉到期持仓，delta rebalance 就没有持仓可以对比。正确做法是当 `rebalance.enabled` 时跳过 horizon close，让 delta rebalance 统一管理持仓生命周期。

- pending manager timer（5s cadence）和 canary 的 delta rebalance 冲突：pending manager 没有 `skip_horizon_close` 逻辑，会在 canary 的 delta rebalance 之前平掉持仓。当启用 delta rebalance 时，应禁用 pending manager timer。

- frozen30 是运行/执行口径，monthly_volume_causal 才是历史 sanity check
- 旧 frozen30 结果被静态名单/幸存者偏差放大，不能直接引用
- age90 策略 Phase 3 未通过但先跑 tiny-live，属于有意的实盘 falsification
- 信号引擎与回测公式必须完全一致，已交叉验证
- 共享执行引擎经过大量 bug 修复，当前状态稳定

## Phase 2c Carry Harvest 研究进展（2026-05-12）

### 研究背景
Rank 450 事件研究项目已发现核心 alpha 来源：**neg_extreme + stall 组合**
- 涨幅榜事件后，币种没有暴跌而是横盘（stall结构）
- 低资金费率横盘（neg_extreme funding，均值 -0.75%）
- 空头持续被挤压（负funding carry收益 +10个百分点增厚）

**关键数据**：
- G_neg_extreme_stall 组合：101样本，5天价格收益 +10.47%，含资金费 +17.00%
- neg_extreme + stall_t3 + 放量：52样本，5天含资金费 +26.17%

### 研究目标
使用 1h 数据构建**实时可观测信号**，避免事后偏差，验证 Phase 2c 策略的可交易性。

### 简化回测结果

**测试方案**：基于 funding 阈值信号，测试不同 funding 分位数阈值（5%-50%）的收益表现。

**关键发现**：
1. **简单 funding 阈值策略不可行**：所有变体净收益为负（-0.17% 到 -0.21%）
2. **neg_extreme funding bucket 表现最好**：+2.76%/4h, +3.71%/8h，胜率 56.8%/60.4%
3. **stall_t2 结构表现最好**：+1.86%/8h，胜率 56.8%
4. **需要更复杂的信号组合**才能获得正收益

**最优变体**：
- funding_pctl < 0.50 + net_8h
- 净收益：-0.17%
- 胜率：42.6%
- 夏普比率：-2.20
- 交易数：50,263

### 下一步建议
1. **优先级1**：测试组合信号（neg_extreme funding + stall_t2 结构）
2. **优先级2**：添加成交额/价格过滤器减少假信号
3. **优先级3**：样本外验证（30% holdout）
4. **优先级4**：Walk-forward 验证（5-fold）
5. **优先级5**：全市场反偏差测试
6. **优先级6**：Paper lane 模拟交易

### 产物索引
- 研究报告：`paper/binance_event_study_phase2c.html`
- 回测脚本：`scripts/backtest_phase2c_simplified.py`
- 分析脚本：`scripts/analyze_phase2c_results.py`
- 报告脚本：`scripts/build_phase2c_report.py`
- 结果数据：`reports/artifacts/binance_event_study_phase2c/`

### 关键经验
- 简单的 funding 阈值策略不可行，需要结合结构过滤
- neg_extreme funding 是最强 alpha 来源，但需要配合其他信号
- stall_t2 结构表现最好，可以作为入场过滤器
- 事后分类偏差是主要挑战，需要实时信号设计

---

## Phase 2b: Short-Side Reversal Strategy (2026-05-12)

更新时间：2026-05-12

### 策略概述

涨幅榜事件后做空回撤策略：在异常拉盘后，利用均值回归特性做空获利。

### 数据基础
- 面板：4.5M 行小时级事件面板（31,368 events × 434 symbols）
- 事件窗口：[-1d, +5d)
- 中位峰值时间：h=51（约2.1天）
- 8h平均回撤：-5.39%

### 信号设计（4类，30变体）

| 信号 | 描述 | 核心逻辑 |
|------|------|----------|
| A | 缩量回撤 | vr20 ≤ vc + ret ≤ pb |
| B | 冲高回落 | 12h内曾放量≥sv倍+涨幅>1% + 当前回落≤dr |
| C | 资金费回撤 | funding>0 + 从高点回落≥pd + 当前跌幅≤dt |
| D | 买盘衰竭 | 6h内tbr曾>55%/65% + 当前tbr≤td |

### 关键结论

1. **Signal B（冲高回落）是唯一持续盈利的信号类型**
   - 最优组合：B_sv5.0_dr-2 + 8h TP5%
   - 净收益：+0.83%，胜率60.0%，PF=1.38
   - 5,201笔交易（2022-2026）

2. **资金费率是最强过滤器**
   - neg_extreme bucket: +1.47% net
   - pos_extreme bucket: -0.29% net

3. **事件结构影响显著**
   - immediate_reversal: +1.37% net
   - continuation: -0.66% net

4. **成本韧性好**
   - B_sv5.0_dr-2 在50bps成本下仍盈利（+0.46% net）

5. **年度稳定性**
   - 2022: +1.19%, 2023: +0.86%, 2024: +0.32%, 2025: +1.00%, 2026: +0.69%
   - 2024最弱但仍为正

### Verdict: WATCH

Signal B（冲高回落+TP5%）显示潜力，但：
- 信号频率低（~3/day across 434 symbols）
- 依赖资金费率条件
- 需要OOS验证和实盘模拟

### 产物索引
- 研究报告：`paper/binance_event_study_v1_6_2b_short_reversal.html`
- 回测脚本：`scripts/backtest_v1_6_2b_short_reversal.py`
- 报告脚本：`scripts/build_v1_6_2b_report.py`
- 结果数据：`reports/artifacts/binance_event_study_v1_6_2b/`

### 关键经验
- 冲高回落（surge-then-drop）比单纯缩量回撤更有效
- 资金费率方向是做空策略的关键过滤器
- 止盈（TP5%）对做空策略至关重要，纯hold收益不稳定
- immediate_reversal结构的事件最适合做空
- 累积乘积法（cumprod）实现O(1)固定持仓收益查询，避免O(N*M)循环
