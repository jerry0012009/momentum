# 别把这份 2026 funding-rate 仓库只读成“DL 课程项目”：对 short-cycle desk，更该先拆的是「post-cost threshold admission」这条 raw alpha 生死线

- 时间：2026-04-16 14:26 UTC
- 类型：GitHub repo source audit（`README.md` + `docs/features.md` + `docs/labels.md` + `docs/baselines.md` + `configs/models/baseline.yaml` + `configs/labels/default.yaml`）+ Binance public-data portability probe（`15m`）
- 主题类型：raw alpha
- 基础 alpha：`short rich perp + long spot`，赚 spread 回归 + funding carry（funding 只做增益，不是本体）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/carry/funding/basis/delta-neutral/post-cost/threshold-admission/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：工程实现证据 + public-data probe

## 1) 这次看了什么
- **Authors/Org**：MengerWen（GitHub）
- **Year**：2026
- **Title**：*Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates*
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL**：<https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates>
- **Repo URL**：<https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates>

这份仓库里最值得 desk 抄的，不是“用了 LSTM/Transformer”，而是它把问题写成了**post-cost 监督学习任务**：标签先扣费、阈值按验证集收益目标选，再决定是否交易。

## 2) base alpha 先说清
这篇东西的 base alpha 是：

> **同币种 spot-perp 的相对价值回归（perp 过贵就 short perp + long spot），funding 只作为 carry booster。**

所以它是 `raw alpha`；threshold search / calibration / walk-forward 都是 admission 与执行层，不是 alpha 本体。

## 3) 关键结论（这轮最值钱）
1. 仓库把标签定义成 `target_future_net_return_bps_*`（先扣 fee/slippage/gas），这一步直接把“看起来能赚”和“实际可交易”分开。  
2. baseline 配置把阈值目标明确设成 `avg_signal_return_bps`，说明它优化的是交易质量，不是纯分类准确率。  
3. 我做的 `15m` portability probe（BTC/ETH/SOL，160 天）显示：**gross 大多为正，但远低于 taker 成本门槛**，raw alpha 本体仍在，但还不具备直接 taker 上线资格。

## 4) 最小可复现实验（本轮已跑）
- 数据源：Binance public API（Spot/Futures `klines` + `fundingRate`）
- 频率：`15m`
- 样本：BTCUSDT / ETHUSDT / SOLUSDT，近 `160d`（每币 `15,360` bars）
- 规则：`z(spread,72h) >= 2` 且 `funding_ffill >= 0.5 bps` 入场，`z<=0` 或最长 `96` bars 出场
- 成本口径：round-trip `34 bps`（taker+slippage 粗口径）

关键数据点：
1. **145 笔交易里，gross 胜率 86.2%（125/145）**，说明“回归方向”本身并非完全失效。  
2. **gross 均值仅 +1.50 bps/笔，net 均值 -32.50 bps/笔**，被成本门槛整体吞没。  
3. **平均 funding 贡献仅 +0.048 bps/笔**，在短持有 (`median hold=4 bars`) 下几乎不够支付摩擦。

## 5) 为什么和当前 desk 直接相关
一句话核心结论：
> **这条 funding+basis raw alpha 不是“没信号”，而是“有信号但单位 edge 太薄”，必须先过 post-cost admission，不能直接按方向硬下。**

一句话证明方式：
> 通过仓库中的 post-cost 标签与阈值目标设计，再用公开 `15m` 数据跑最小复现实验，看到 gross 与 net 的系统性分叉。

## 6) 下一步怎么测（映射 `1m/3m/5m/15m`）
1. **1m/3m（事件型）**：只在 funding 结算前后窗口交易（例如 `[-20,+20]` 分钟），测试是否能把单笔 gross 从 `~1.5 bps` 提升到可覆盖成本。  
2. **5m（主战快检）**：把固定阈值改为分位阈值（按 spread/funding 联合分位），只做 top-decile dislocation。  
3. **15m（稳健基线）**：保留 current shell，增加 maker-first/排队成交假设，单独评估“费用结构变化”对生存线的影响。  
4. 四周期统一输出：`trade_count / gross_bps / net_bps / funding_share / implementation_shortfall`，先做 admission 再谈模型复杂度。

## 7) 风险与保留意见
- 本轮是公开数据 + 粗成本口径，未建完整盘口冲击模型；结论用于 first verdict，不是最终 production verdict。  
- funding 是低频结算变量，硬塞成逐 bar 主信号会过拟合；更适合作为 carry booster 与 regime gate。  
- 若未来切 maker-first 或跨所净额撮合，成本面可能显著改善，但需要独立执行回测验证。

## 8) 本轮产物
- `reports/artifacts/quant_digests/funding_spread_threshold_portability_probe_2026-04-16.csv`
- `reports/artifacts/quant_digests/funding_spread_threshold_portability_probe_2026-04-16_trades.csv`
- `reports/artifacts/quant_digests/funding_spread_threshold_portability_probe_2026-04-16_summary.json`

## 9) 来源
1. MengerWen. (2026). *Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates*. GitHub.  
   Readable URL / Repo URL: <https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates>
2. Binance Spot Klines API（public）: <https://api.binance.com/api/v3/klines>
3. Binance USDⓈ-M Futures Klines API（public）: <https://fapi.binance.com/fapi/v1/klines>
4. Binance USDⓈ-M Funding Rate API（public）: <https://fapi.binance.com/fapi/v1/fundingRate>
