# 别把这份 BTC options 系统只读成“六策略拼盘”：对 short-cycle crypto desk，更该先拆的是「post-event vol crush × ATM straddle re-expansion」这条 raw alpha

- 时间：2026-04-21 23:10 UTC
- 类型：GitHub repo source audit（`README.md` + `src/strategies.py` + `reports/btc_system_final_report.txt` + `reports/btc_vol_research_report.txt`）
- 主题类型：raw alpha
- 基础 alpha：`重大事件后隐波被快速打低（vol crush）且处于 LOW/MEDIUM regime 时，买入 30D ATM straddle，赌后续波动二次扩张而不是赌方向`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 已给出 entry/exit/sizing/kill-switch/cost 模型）
- 主题标签：raw-alpha / options / event-driven / volatility / long-gamma / straddle / vol-crush / re-expansion / deribit / 5m / 15m / 1m / 3m
- 证据类型：repo 规则明文 + 回测汇总（11.5y）

## 1) 这次 intake 的核心（先回答 base alpha）

这次不拆它“六策略全家桶”，只取 `StrategyC_EventVol` 里的 **C2 Post-Event Vol Buy**：

> 在已知事件（halving / crash / quarterly expiry）后 `0~7` 天内，若波动 regime 处于 `LOW/MEDIUM`，则买入 `30D ATM straddle`，以“后续波动再扩张”获利。

这条线的 base alpha 很清楚：**event 后的隐波压缩常有过冲，随后会出现二次扩张；用 delta-neutral 的 long straddle 吃这个波动回摆。**

## 2) 规则是否完整（entry / exit / sizing / risk / cost）

从 `src/strategies.py` 能直接抄到完整壳：

- **Entry（C2）**
  - 事件窗口：`0 <= days_since_event <= 7`
  - regime：`LOW` 或 `MEDIUM`
  - 合约：`ATM straddle`
  - 到期：`30 days`
- **Exit**
  - 止盈：`POST_TP_MULT = 2.0`（即盈利到约 200%）
  - 止损：`POST_SL_FLOOR = 0.30`（权利金价值跌到入场的 30%）
  - 时间止损：`time_stop_days = 20`
- **Sizing**
  - `POST_RISK_PCT = 0.02`，即单笔按权益 `2%` 风险预算
- **Risk**
  - kill-switch：连续 `3` 次亏损，暂停 `30` 天（`KILL_SWITCH_LOSSES=3`, `KILL_SWITCH_DAYS=30`）
- **Cost**
  - 同文件包含 Deribit friction 模型（fee / spread / slippage 假设）

结论：这不是“概念型论文想法”，而是可直接落地的策略壳。

## 3) 关键数据点（来自 repo 报告）

`reports/btc_system_final_report.txt` 给了该分支在组合中的结果：

1. **Event Vol 子策略：38 笔**
2. **胜率 31.6%**，但 **平均盈亏比约 3.32x**（低胜率高赔率）
3. **累计 PnL +21.1057（报告口径）**

这三点很像 long-gamma/event 策略该有的画像：**不是靠高命中，而是靠尾部收益覆盖小亏。**

## 4) 和当前 desk 的关系（为什么值得优先）

我们最近 intake 已经有很多 `pairs / coint / funding / grid / xs-reversal`。这条线的增量在于：

- 它是 **options/event-driven raw alpha**，家族多样性更高；
- 能直接给 `1m/3m/5m/15m` execution 层喂信号（不是只能日频讨论）；
- 自带完整风险组件（time stop + kill-switch + risk-budget），易接入现有实盘框架。

## 5) 最小可复现实验（直接映射 1m/3m/5m/15m）

先不跑六策略，只跑 C2：

- **标的与数据**
  - Deribit BTC 期权链（公开可得）+ BTC perp/spot 高频价格
  - 事件清单先用 repo 自带三类：halving / crash anniversary / quarterly expiry
- **信号层（日频触发）**
  - 每天判定是否 `days_since_event <= 7` 且 regime in `LOW/MEDIUM`
- **执行层（短周期）**
  - 在触发日内，用 `1m/3m/5m/15m` 分批建仓 ATM straddle（TWAP 30~120 分钟）
  - 盘中用 `5m` 滚动监控 Greeks 与组合价值，满足止盈/止损/超时即平
- **评估指标**
  - 每笔净收益（扣 fee/spread/slippage）
  - 触发后 `24h/72h/7d` realized vol 变化
  - time-stop 比例、尾部收益贡献、事件类型分层（halving/crash/quarterly）

## 6) 风险与保留意见

- repo 的 IV 口径里有 synthetic 成分，实盘需替换为真实链上 mid-IV / mark-IV；
- 事件样本天生不密集，容量受限，应定位为“事件窗口策略”，不是全天主引擎；
- 低胜率高赔率策略容易经历连亏，kill-switch 和仓位上限必须硬执行。

## 7) 来源（按可追溯口径）

1. **beetrootblues (2026)**. *BTC Options Quantitative Trading System*. GitHub Repository.  
   - Authors/Year/Title/Venue: `beetrootblues / 2026 / BTC Options Quantitative Trading System / GitHub repository`  
   - DOI: N/A  
   - Readable URL: `https://github.com/beetrootblues/btc-options-system`  
   - Repo URL: `https://github.com/beetrootblues/btc-options-system`

2. Source files audited:  
   - `https://raw.githubusercontent.com/beetrootblues/btc-options-system/main/README.md`  
   - `https://raw.githubusercontent.com/beetrootblues/btc-options-system/main/src/strategies.py`  
   - `https://raw.githubusercontent.com/beetrootblues/btc-options-system/main/reports/btc_system_final_report.txt`  
   - `https://raw.githubusercontent.com/beetrootblues/btc-options-system/main/reports/btc_vol_research_report.txt`
