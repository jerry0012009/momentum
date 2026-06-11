# Rank32B 策略停用声明

日期: 2026-05-04
决策: **永久停用**

## 策略概述

Rank32B (slope floor continuation) 是基于 1h 级别 EMA20/EMA50 趋势结构 + slope floor 确认 + 15m 级别入场的动量策略。曾部署为独立实盘 lane（global32b_live），使用 Binance USDⓈ-M 合约交易 BTC/ETH。

## 停用原因

### 1. Lookahead Bias — preview_unclosed_15m 模式

代码中存在两种信号计算模式：
- official_close_only：等 15m K 线收盘 → 聚合成完成的 1h K 线 → 计算 EMA → 生成信号。无未来函数。
- preview_unclosed_15m：用当前未收盘的 15m K 线实时价格估算当小时 EMA 值。等效于提前最多约 45 分钟预知未来。

相关代码：src/momentum/execution/canary32b/signal_adapter.py（6 处引用），run_rank32b_global_live.py、run_rank32b_canary_phase6.py 均从配置读取此开关。

### 2. Warmup 窗口膨胀

回测脚本 backtest_rank32b_global_shadow_live_like.py 将有效历史窗口扩展到超出 horizon + lookback 的范围，导致 180d/365d/720d 长期回测结果被撤回作废。

证据：reports/artifacts/rank32b_shadow_global_live_like_backtest/INVALIDATED_BY_WARMUP_AUDIT_2026-04-07.md

### 3. 实盘 vs 模拟严重不一致

| 指标 | 值 |
|---|---|
| 实盘总交易 | 41 笔 |
| 实盘净 PnL | -0.85 USDT |
| close match rate | 11.8% |
| exit bucket match rate | 76.5% |

11.8% 的 close match rate 说明实盘跑出来的信号和回测/模拟不是同一回事。

### 4. 去除 preview 后全面亏损

使用 official_close_only 模式的 live-like 回测：

| 时间窗口 | 交易数 | 净收益 | 胜率 |
|---|---|---|---|
| 3 天 | 12 | -0.15% | 33.3% |
| 10 天 | 84 | -0.09% | 43.2% |
| 30 天 | 296 | -0.05% | 44.3% |
| 60 天 | 632 | -0.35% | 41.5% |

没有任何时间窗口在成本后为正。

## 停用措施

1. **Systemd 全部停用**（2026-05-04 15:44 UTC）：
   - momentum-rank32b-global-live.timer / .service
   - momentum-rank32b-global-shadow.timer / .service
   - momentum-rank32b-beat-shadow.timer / .service
   - momentum-rank32b-canary-phase6.timer / .service
   - momentum-canary-doc.service
2. **配置关闭**：config/execution/rank32b_canary.yaml 中 trade_enabled: false、kill_switch: true
3. **Status JSON 关闭**：live_status.json 和 phase6_status.json 均已设为 trade_enabled: false
4. **网站标注**：所有 29 个相关入口页已注入永久停用声明横幅

## 残存价值

- **研究框架**：EMA slope floor + structure 的信号框架本身（1h 高级别趋势方向 + 15m 入场）是一个合理的交易思路
- **代码资产**：signal_adapter、depth_v2 paper、live-shadow 对比框架等可作为后续策略的参考
- **教训**：跨时间尺度信号必须严格区分 completed vs unclosed bar；回测 warmup 窗口必须有独立审计

## 关键文件存档

- 信号适配器：src/momentum/execution/canary32b/signal_adapter.py
- 实盘 runner：scripts/run_rank32b_global_live.py
- 最终门控审计：reports/artifacts/rank32b_final_goal_gate/active_goal_completion_audit.md
- Warmup 审计：reports/artifacts/rank32b_shadow_global_live_like_backtest/INVALIDATED_BY_WARMUP_AUDIT_2026-04-07.md
- Live vs Shadow 诊断：reports/artifacts/rank32b_final_goal_gate/live_shadow_diagnostic.md
