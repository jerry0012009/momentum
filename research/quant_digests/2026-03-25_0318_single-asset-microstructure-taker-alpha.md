# 别把 microstructure 只做成 OBI 做市：这篇 2026 论文+同名仓库更值得先复现的是「单资产 OFI + VWAP pressure taker raw alpha」
- 时间：2026-03-25 03:18 UTC
- 类型：2026 arXiv 论文 + 2026 GitHub 同名工程仓库 + Binance 公共原始数据最小快检
- 主题类型：raw alpha
- 基础 alpha：顶档深度失衡、主动成交失衡与买卖 VWAP 相对 mid 的偏离，可直接预测未来 `3s` 中间价收益；当预测值超过阈值时，按预测方向立即吃单
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/time-series/order-flow/imbalance/vwap-pressure/taker/maker/binance/perpetual/1s/1m/3m/paper/repo/execution
- 证据类型：论文证据 + 工程证据 + 本地快检

> 先回答 base alpha：**不是 filter，不是纯解释。base alpha 就是“当前盘口/成交流微观结构状态 → 未来几秒收益方向”的单资产 directional raw alpha。**

## 1. 这次看了什么
主线材料是：
- **Bartosz Bieganowski, Robert Ślepaczuk (2026), _Explainable Patterns in Cryptocurrency Microstructure_**（arXiv）
- **amazingchow/epcm**（2026，同名复现工程仓库）

这轮我不把它读成“又一个 OBI 解释文”或者“又一个做市教程”，而是把它拎回最适合我们 desk 的形态：

**单资产、事件驱动、极短持有、可直接吃单执行的 microstructure raw alpha。**

它和我们前面已经看过的两类东西不一样：
1. 不是把 OBI 塞进双边做市 reservation price 的那条线；
2. 也不是横截面 taker-flow 排名那条线；
3. 它更像是：**用统一的微观结构特征库，直接预测单币未来 `3s` 收益，然后做阈值型 taker 交易。**

## 2. 核心结论
- 一句话核心结论：**这篇 2026 论文真正值得先复现的，不是“SHAP 很好看”，而是“OFI + spread + VWAP pressure”这套统一特征库本身就是可独立交易的单资产 raw alpha。**
- 一句话证明方式：**论文给了完整 taker/maker 回测；同名仓库把数据构建、特征工程、CatBoost/Optuna、SHAP、回测全部工程化；我再用 Binance 公共原始 `bookTicker + trades` 做了 1 天最小快检，确认最基础的方向信息确实还在。**

关键数据点（论文）：
1. **数据口径**：Binance Futures 永续，`1s` 级 order book + trades，样本从 **2022-01-01 到 2025-10-12**，覆盖 **BTC / LTC / ETC / ENJ / ROSE**。目标变量是未来 **`3s` mid log return**。
2. **taker 回测最强的不是 BTC，而是中小币**：
   - `ETC`：`ARC 5.78`，`IR* 8.97`，t-test `p=0.0431`
   - `ENJ`：`ARC 4.06`，`IR* 6.58`，t-test `p=0.0368`
   - `ROSE`：`ARC 7.00`，`IR* 5.28`，t-test `p=0.0192`
3. **maker 并不天然更优**：
   - `BTC` maker 还不错：`ARC 2.93`，`IR* 5.47`
   - 但 `ENJ / ETC / ROSE` maker 明显弱很多，甚至接近负收益，说明这条 edge **更先像 taker directional alpha**，不是“先验适合做市”的 alpha。
4. **极端行情验证**：2025-10-10 flash crash 中，论文写到 taker 策略的异常持仓时间大约 **20 秒**，而平时多是 **1~2 秒**；maker 则因为逆向选择在崩盘中被持续打穿。

关键数据点（我做的本地最小快检，公开 Binance 原始数据，1 天样本，仅作方向复核）：
1. `ROSEUSDT`（2024-01-15）：用 `order_flow_imbalance + depth_imbalance + vwap_pressure + relative_spread` 的简单线性 proxy，在测试半天内，对未来 `3s` 收益的相关系数约 **0.137**；强信号多头事件平均下一段收益约 **+0.684 bps**，强信号空头事件约 **-0.812 bps**。
2. `ENJUSDT` 同口径相关系数约 **0.191**；强信号多头约 **+1.043 bps**，强信号空头约 **-0.929 bps**。
3. 但把秒级信号**粗暴压成 bar-close `1m/3m/5m` 因子后并不稳定**：ROSE 在 `3m` 还有一点形状，ENJ 则明显发散。这说明它更适合做 **event-driven micro alpha / execution alpha**，而不是直接硬改造成逐根 `5m/15m` 主信号。

## 3. 为什么和当前项目直接相关
- 这是**raw alpha**，不是 shared gate。
- 它扩充的是我们当前素材池里仍然值得继续加深的一类：**单资产 microstructure directional alpha**。
- 它天然适配 `1m / 3m` 的高强度短周期研发；对 `5m / 15m` 也不是没用，但更应先定位成：
  - 更优入场时点选择
  - taker/maker 执行切换
  - 极端 spread / adverse-selection veto
- 更重要的是：这条线已经自带完整策略骨架，不是只有“某个解释变量很重要”。

## 3.5 策略拆解（必填）
- 方向属性：单资产 / 时间序列 / 微观结构 directional alpha
- 基础 alpha：
  - `depth_imbalance = (bid_size - ask_size) / (bid_size + ask_size)`
  - `order_flow_imbalance = (buy_volume - sell_volume) / (buy_volume + sell_volume)`
  - `buy_vwap_dev = (buy_vwap - mid) / mid`
  - `sell_vwap_dev = (sell_vwap - mid) / mid`
  - `vwap_pressure = ((buy_vwap*buy_volume) - (sell_vwap*sell_volume)) / ((buy_volume+sell_volume)*mid)`
  - 用上述特征预测 `r_{t→t+3s}`，当 `|prediction| > θ` 时按符号开仓
- entry：`prediction > θ` 做多；`prediction < -θ` 做空
- exit：
  - 信号反向
  - 信号回落至阈值内
  - 或设置最大持有秒数（如 `3s / 5s / 10s / 20s`）
- sizing：先用固定 notional；后续可按 `|prediction| / rolling_vol / spread state` 做分层仓位
- risk：
  - `max_position_notional`
  - spread 突然放宽时强制降档 / 停机
  - 延迟、滑点、盘口真空单独建 kill-switch
- cost：
  - taker 手续费必须显式进回测
  - maker 版本不能只看 spread capture，必须单独记 adverse selection

## 4. 这条线最有价值的，不是“预测对不对”，而是“怎么映射到 desk”
如果强行问：它对我们 `1m / 3m / 5m / 15m` 有什么直接意义？

我的判断是：
- **最适合：`1m / 3m` 的 event-driven alpha**
- **次适合：`5m / 15m` 的 execution / veto / timing layer**
- **暂不建议：直接把秒级平均值变成 `5m/15m` 主 raw alpha**

原因很简单：这条 edge 的生成机制是**微观结构状态的瞬时偏移**，不是慢变量。
你把它压得太粗，信号会被 bar 内路径抵消掉。

所以对 desk 更合理的读法不是：
- “把它改写成 15m 因子”；
而是：
- “当 `1m / 3m` bar 内出现持续 `N` 秒的一致微观结构压力时，触发一笔独立 micro-trade”；或
- “当 5m 主信号准备入场时，用它判断该不该立刻吃单，还是等一脚回撤/盘口修复再进。”

## 5. 可复刻的最小实验（下一步怎么测）
**研究假设**：
`OFI + depth imbalance + VWAP pressure` 在 Binance perp 上可形成可交易的超短周期单资产 raw alpha，但真实可交易性高度依赖 `threshold × hold_seconds × fee/slippage × spread state`。

**数据源与公开性**：
- 数据源：Binance USDⓈ-M Futures 公共历史数据 `bookTicker` 与 `trades`
- 公开性：公开可得，无私钥
- 更新频率：毫秒事件，可聚合到 `1s`
- 最小可复现实验口径：公共 daily zip 即可

**最小实验设计**（最应该先做这个，而不是先上复杂网络）：
1. **标的**：`BTCUSDT / ETHUSDT / ROSEUSDT` 三档流动性
2. **采样**：先做最近 `14~30` 天 `1s` 数据
3. **信号**：先只用 4~6 个 paper 原生特征，不加花哨深度学习
4. **训练/验证**：walk-forward，至少做 `train 7d / test 1d` 滚动
5. **持有期网格**：`3s / 5s / 10s / 20s`
6. **阈值网格**：按预测分布分位数（如 `80/90/95/97.5`）而不是拍脑袋固定值
7. **成本阶梯**：`fee only / fee+0.5tick / fee+1tick / latency stress`

**最先看 5 个指标**：
- `IC(score, next_ret_3s)`
- `avg bps per triggered event`
- `events/day`
- `post-cost pnl`
- `spread-conditioned pnl`（窄 spread vs 宽 spread）

**最关键的下一步，不是再调模型，而是这 3 个实验：**
1. **signal persistence**：只有信号连续 `N` 秒同向才触发，看看能否把噪声降下去
2. **hold-seconds sweep**：检验这条 alpha 是 `3s` 即衰减，还是能拖到 `10~20s`
3. **taker-only vs maker-off switch**：在 spread 扩大或盘口失衡极端时，maker 是否应该直接关闭

## 6. 风险与保留意见
- 论文里的方向信息很强，但**高频回测天然会高估实盘**，因为 latency / queue / network jitter 很难完全诚实模拟。
- 这条线对交易所状态极敏感：一旦 spread 扩大、深度塌陷、出现假挂单，信号质量和成交质量会一起掉。
- flash crash 里的高收益也意味着另一面：**如果大家都在盯同样的 imbalance，alpha 可能会在极端时刻放大市场脆弱性。**
- 对我们现在的 desk 来说，最现实的落地顺序应是：
  1. 先做 **taker event-driven 版本**
  2. 再把它接到 `1m/3m` 的 execution layer
  3. 最后才考虑 maker 化或更复杂的 queue 模型

## 7. 来源
1. **Bieganowski, B., & Ślepaczuk, R. (2026). _Explainable Patterns in Cryptocurrency Microstructure_. arXiv.**
   - DOI: `10.48550/arXiv.2602.00776`
   - Readable URL: `https://arxiv.org/abs/2602.00776`
   - HTML URL: `https://arxiv.org/html/2602.00776v1`
   - PDF URL: `https://arxiv.org/pdf/2602.00776.pdf`
2. **amazingchow. (2026). _epcm_. GitHub repository.**
   - Repo URL: `https://github.com/amazingchow/epcm`
   - Readable URL: `https://github.com/amazingchow/epcm`
3. **Binance Data Vision. USDⓈ-M Futures public historical data (`bookTicker`, `trades`).**
   - URL: `https://data.binance.vision/`

## 8. 本地快检产物
- `reports/artifacts/quant_digests/epcm_microstructure_probe_20260325/summary_1s.csv`
- `reports/artifacts/quant_digests/epcm_microstructure_probe_20260325/summary_bars.csv`
- `reports/artifacts/quant_digests/epcm_microstructure_probe_20260325/roseusdt_test_predictions_head.csv`
- `reports/artifacts/quant_digests/epcm_microstructure_probe_20260325/enjusdt_test_predictions_head.csv`
