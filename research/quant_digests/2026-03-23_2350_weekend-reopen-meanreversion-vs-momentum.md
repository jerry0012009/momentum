# 周末漂移不是都该追：更值得先复现的是 `Weekend→Reopen` 的均值回归 raw alpha（而非周末动量）
- 时间：2026-03-23 23:50 UTC
- 类型：2026 新仓库策略源码 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：周末低流动性下的偏离（相对周五参考价）在流动性恢复前后更可能回归，而非继续单边延续
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（已具备 entry/exit/stop/cost 基本骨架）
- 主题标签：raw-alpha/mean-reversion/weekend-reopen/event-driven/perpetual/crypto/5m/15m/1m/3m/cost
- 证据类型：仓库策略规则 + 本地公共数据快检

## 1) 这次看了什么
先回答 base alpha：**不是 breakout，也不是常规趋势跟随，而是“周末薄流动性漂移在 reopen 附近回归”**。  
本次主看 `hype-backtesting`（2026）里的 `WeekendReopen` 策略实现（含均值回归/动量双模式、止损与重开盘平仓逻辑），并在 Binance USDT 永续 15m 数据上做了成本口径最小快检。

## 2) 核心结论
- **一句话核心结论：** 在当前口径下，`Weekend→Reopen` 更像**事件驱动的均值回归 alpha**，把它当“周末动量追价”会明显变差。  
- **一句话证明方式：** 同一套时间窗、同一套参数与成本假设下，均值回归模式在 ETH/SOL 为正、动量模式三币全负，差异稳定且方向一致。

3 个关键数据点（本地 15m 快检，近 365 天，round-trip 成本 8 bps）：
1. **均值回归模式**：BTC `-2.32%`、ETH `+10.96%`、SOL `+9.21%`，三币乘积口径约 `+18.37%`。  
2. **动量模式**：BTC `-53.06%`、ETH `-44.84%`、SOL `-71.97%`（显著劣于均值回归）。  
3. 交易频次差异明显：均值回归约 `115/146/157` 笔（BTC/ETH/SOL），动量约 `295/370/427` 笔，动量端的过度换手与成本侵蚀更重。

## 3) 为什么和当前 desk 直接相关
- 这是可独立复现的 raw alpha（event-driven mean reversion），不是解释型综述。  
- 可直接映射到 `5m/15m`（并可下钻 `1m/3m`）做实盘前 first-verdict。  
- 与现有 momentum/breakout 主线形成机理互补：在“周末薄流动性时段”提供逆向 alpha 备选。

## 3.5) 策略拆解（必填）
- 方向属性：event-driven / mean-reversion（可切换 momentum 对照）
- 基础 alpha：周末漂移对周五参考价的回归倾向
- entry：周末状态且 `|drift| >= threshold`（默认 0.5%）触发；回归模式下反向开仓
- exit：reopen 强制平仓；或 pre-reopen 已回归参考价提前止盈；或 stop-loss 出场
- sizing：固定仓位（示例 10% equity，可扩展为波动率归一）
- risk / veto：单周末单次入场、2% 止损、重开盘前收敛检查
- cost：显式 round-trip 成本（本次快检 8 bps）

## 4) 可复刻最小实验（5m/15m 起步）
- 数据源：Binance USDⓈ-M Futures Klines（公开 REST）
- 公开性：公开可得，无需 API key
- 更新频率：支持 `1m/3m/5m/15m`
- 最小口径：
  - 资产：`BTCUSDT/ETHUSDT/SOLUSDT`
  - 样本：近 365 天 15m bars
  - 规则：`drift_threshold=0.5%`，`stop=2%`，mode 对照（mean_reversion vs momentum）
  - 首看指标：`cum_return / win_rate / trades / profit_factor`（含成本）

## 5) 下一步怎么测（直接可执行）
1. **先做阈值分层**：`drift_threshold` 改为分位数（如按过去 8 周周末漂移分位），避免固定 0.5% 在不同波动期失真。  
2. **加 microstructure veto**：仅在 `spread` 与 `成交量` 达标时允许开仓，压缩“薄流动性假回归”。  
3. **做 1m/3m 执行版**：信号仍在 15m 生成，执行下钻到 1m/3m，测试 maker/taker 混合成本。  
4. **加入 funding/basis overlay**：若周末漂移与 funding/basis 极端同向，分离“可回归偏离”与“信息性重定价”。

## 6) 风险与保留意见
- 本次为最小实验：止损按收盘价代理，未用盘口/成交簿级成交模型。  
- 周末定义采用 repo 给出的交易时段逻辑，仍需按目标交易所实际流动性时钟微调。  
- 结论更像“候选可行性筛查”，不是最终生产参数。

## 7) 来源
1. **Andrea Ambrosio (2026). _hype-backtesting_ (GitHub).**  
   - Repo URL: https://github.com/andreaambrosio/hype-backtesting  
   - Strategy code: `src/strategies/weekend_reopen.py`
2. **Binance Developers (Docs). USDⓈ-M Futures Kline/Candlestick Data.**  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
3. **Blockworks Research (2026). _HIP-3 Silver Microstructure: Hyperliquid vs. CME_**（仓库 README 引用）  
   - 说明：本次未直接抓到全文，仅作背景线索，不作为单独强证据。

## 8) 本地产物
- `reports/artifacts/quant_digests/weekend_reopen_probe_20260323/summary.csv`
- `reports/artifacts/quant_digests/weekend_reopen_probe_20260323/trades.csv`
- `reports/artifacts/quant_digests/weekend_reopen_probe_20260323/notes.txt`
