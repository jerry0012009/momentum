# 先别把 dynamic grid 当印钞机：这篇 2025 论文更值得 intake 的是「动态重置的波动收租」完整 raw alpha

- 时间：2026-03-25 23:58 UTC
- 类型：2025 arXiv 论文（全文 PDF 可读）+ 官方 GitHub repo + Binance Spot 公共 `5m/15m` 最小快检
- 主题标签：raw-alpha/mean-reversion/single-asset/grid/volatility-harvest/dynamic-reset/spot/btc/eth/5m/15m/1m/repo/paper/binance/execution/cost
- 证据类型：论文证据 + repo 代码审计 + 公共数据最小代理回测

- 主题类型：raw alpha
- 基础 alpha：单币种价格会反复穿越围绕“当前中心价”设置的窄带；用动态重置把中心价跟着市场移动，保留来回收租的均值回归/波动收割，而不是让静态 grid 一次走死
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 这次看了什么
这次看的是 **Kai-Yuan Chen / Kai-Hsin Chen / Jyh-Shing Roger Jang (2025)** 的论文 *Dynamic Grid Trading Strategy: From Zero Expectation to Market Outperformance*，以及作者给出的 GitHub 仓库 `colachenkc/Dynamic-Grid-Trading`。

先把最重要那句话说清楚：**base alpha 不是“网格形状”，而是“围绕当前中心价的反复往返穿越”这条单资产短周期均值回归 / volatility-harvest。** dynamic reset 只是把中心点不断搬到新价格上，避免传统 finite grid 一旦出框就失效。

这件事为什么值得进池子？因为它补的是一条**单资产、非横截面、非 pairs、可完整写成 entry/exit/sizing/risk/cost 的 mean-reversion 全栈骨架**。对 desk 来说，它不是最像 `1m` 高频 taker alpha 的那类东西，但很适合做 `15m` 的完整策略原型，再往 `5m` 压测成本与过度换手。

## 2. 核心结论
1. **论文先把传统 grid 的幻觉戳破了。** 在作者的简化假设下，有限边界的传统 grid 期望值约为 0；考虑费用后，静态 grid 更容易被拖成负期望。也就是说，真正值得研究的不是“继续加更多格子”，而是**出框以后怎么办**。
2. **作者给出的改法是 dynamic reset。** 价格突破上/下边界后，不停机，而是以当前价格重开一套新 grid，让策略继续围绕新中心价收波动，而不是抱着旧锚点等死。
3. **论文自己的 1m 回测非常强。** 文中报告 BTC/ETH 在 `2021-01 ~ 2024-07` 的 minute-level 回测里，DGT 的 IRR 大致能到 **60%~70%**；BTC 的 IRR 高于 buy-and-hold 且 MDD 更低，ETH 虽然 IRR 不一定明显高于买入持有，但在文中叙述里，**最大回撤被压到约 50%，而买入持有级别约在 80% 附近。**
4. **但 repo 里最值得我们学的，不是“神奇收益曲线”，而是完整策略零件。** 它把 `grid step / half-grid count / reset rule / fee` 都写成可复刻参数；同时也暴露出一个重要审计点：**论文口径说 geometric grid，但 repo 代码更接近围绕中心价的 arithmetic percentage bands。** 这提醒我们后面做 clean replication 时必须先锁定“到底复现哪一个版本”。
5. **我用 Binance Spot 公共 `5m/15m` 做的 repo-style 代理快检显示：15m 比 5m 更像它该待的地方。** 在 `2025-01-01 ~ 2026-03-25` 这段偏难样本里：
   - BTC `15m` 最优代理组合约为 `grid_size=1.5%, half_grids=3`，总收益 **-23.6%**，略好于 buy-and-hold 的 **-24.7%**，但 MDD 只有 **-34.8%**，显著好于 buy-and-hold 的 **-52.2%**；
   - ETH `15m` 最优代理组合约为 `grid_size=1.0%, half_grids=5`，总收益 **-34.9%**，略好于 buy-and-hold 的 **-35.5%**，MDD **-45.7%**，也明显好于 buy-and-hold 的 **-64.2%**；
   - `5m` 版本整体更容易被换手和重置次数拖累，说明**压到更快周期后，edge 更像被过度交易吃掉**。

一句话结论：**这篇东西最值得记住的，不是“grid 很赚钱”，而是“单资产波动收租要活下来，关键在 recenter/reset，而不是静态挂格本身”。**

一句话证明方式：**作者用数学推导先否掉静态 finite grid 的零期望，再用 BTC/ETH 的 1m 回测证明 dynamic reset 版本的收益/回撤更优；我这边再用 Binance `5m/15m` 做了一个 repo-style stress proxy，发现它更像 `15m` 完整策略骨架，而不是 `5m` 高频 alpha。**

## 3. 为什么和当前项目有关
这条线和当前 desk 直接相关，因为它补的是一条**single-asset mean-reversion full stack**：
- 不依赖 pairs 选对；
- 不依赖外部低频数据；
- 可以直接写成完整策略；
- 天生带有 `entry / exit / sizing / reset / fee guard`。

更实际地说，它给我们的不是“再加一个 filter”，而是一条可独立建模的 raw alpha 原型：**震荡里收波动，趋势里靠 reset 续命。** 这很适合拿来和我们现在手里的 breakout / momentum / pairs 形成互补，而不是继续只补 shared gate。

## 3.5 策略拆解（必填）
- 方向属性：逆势 / 波动收租 / 单资产
- 基础 alpha：中心价附近的反复穿越与均值回归
- regime：高 realized vol、非单边爆发、最好是宽幅震荡而不是持续趋势推进
- filter / veto：ADX/趋势斜率过高时停机；大单边 breakout 日 veto；费用/点差过高 veto
- risk / sizing / execution overlay：`grid_size`、`half_grids`、reset 触发、inventory 上限、maker fee guard、只在 `15m` 主跑、`5m` 只做 stress 版

## 4. 可复刻的最小实验
**研究假设**：dynamic reset grid 的可迁移 alpha，不在 `1m`“挂很多小单”，而在 `15m` 上把单资产震荡 harvesting 做成一个费用可承受的完整策略。

**最小回测切口**：
- 标的：`BTCUSDT`, `ETHUSDT` Spot 或 perp mid
- 周期：先 `15m`，再 `5m` 压测
- 参数：`grid_size ∈ {1.0%, 1.5%, 2.0%}`，`half_grids ∈ {3,5}`
- 出框：触边立刻 reset 到新中心价
- 指标：净收益、MDD、日均 trade count、单位波动捕获效率、费用敏感性（`0/4/8/12 bps`）

**最该先看的 2 个指标**：
1. `net return - buyhold` 是否在 `15m` 变正；
2. 在加入真实费用后，trade count 是否把策略拖回负期望。

## 5. 风险与保留意见
1. **论文样本偏有利期。** 2021~2024 对 crypto 多头资产天然友好，必须警惕把“beta 上行 + 波动收租”误当纯 alpha。
2. **repo 与论文口径并不完全一致。** 网格定义与路径处理需要 clean replication 时重新锁死。
3. **`5m` 可能太快。** 我这边的代理快检已经看到 5m 比 15m 更像过度换手版本。
4. **它非常怕单边趋势。** 所以若后续要上 desk，默认必须配 trend veto / regime gate，而不是裸跑。

## 6. 下一步怎么测
1. **先做 faithful replication 版**：按论文公式与 repo 代码分别各复现一版，别把二者混成一个口径。
2. **给 `15m` 加单边趋势 veto**：例如 ADX、rolling drift、或 4h directional efficiency，判断能否把 2025~2026 stress sample 的净收益拉正。
3. **补 fee ladder**：把 round-trip 成本从 `0 → 12 bps` 逐档扫一遍，看 `5m` 是否直接死、`15m` 是否还有生存带。
4. **拆 PnL 来源**：把收益分成“震荡段贡献”和“趋势段拖累”，确认它到底是 raw alpha 还是只是 beta smoother。

## 7. 来源
1. **Kai-Yuan Chen, Kai-Hsin Chen, Jyh-Shing Roger Jang. (2025). _Dynamic Grid Trading Strategy: From Zero Expectation to Market Outperformance_. arXiv.**
   - arXiv: `2506.11921`
   - Readable URL: https://arxiv.org/abs/2506.11921
   - PDF URL: https://arxiv.org/pdf/2506.11921

2. **colachenkc / Dynamic-Grid-Trading (GitHub repo)**
   - Repo URL: https://github.com/colachenkc/Dynamic-Grid-Trading
   - Readable URL: https://github.com/colachenkc/Dynamic-Grid-Trading

3. **Binance Spot API / Binance Vision public klines**
   - Docs: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data
   - Data bucket: https://data.binance.vision/

4. **本地最小实验 artifact**
   - `reports/artifacts/quant_digests/dynamic_grid_dgt_20260325_2355/proxy_backtest_summary.csv`
   - `reports/artifacts/quant_digests/dynamic_grid_dgt_20260325_2355/best_configs.json`
   - `reports/artifacts/quant_digests/dynamic_grid_dgt_20260325_2355/BTCUSDT_15m_best_equity_curve.csv`
   - `reports/artifacts/quant_digests/dynamic_grid_dgt_20260325_2355/ETHUSDT_15m_best_equity_curve.csv`
   - `reports/artifacts/quant_digests/dynamic_grid_dgt_20260325_2355/replication_window_2021_2024_15m.json`
