# Explainable Microstructure（2026 arXiv + 2026 repo）：把 1 秒盘口失衡做成可迁移的短周期 raw alpha
- 时间：2026-04-03 07:32 UTC
- 类型：论文 + GitHub
- 主题类型：raw alpha
- 基础 alpha：`order_flow_imbalance + VWAP 相对 mid 偏离` 预测未来短窗收益，并用阈值化方向信号交易
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：microstructure / order-flow / OFI / VWAP / CatBoost / SHAP / taker-maker / 1m / 3m / 5m / 15m
- 证据类型：论文证据 + 工程实现证据

**先回答 base alpha：这篇东西的 base alpha 不是“宏观故事”，而是“盘口失衡与成交压力对下一小段收益的可预测性”，可直接写成入场/出场规则。**

## 1) 这次看了什么
看了 2026 arXiv 论文《Explainable Patterns in Cryptocurrency Microstructure》及其对应开源工程仓库 `amazingchow/epcm`。论文用 Binance Futures `1s` 盘口+成交数据（2022-01-01 到 2025-10-12）做跨币种验证；仓库把同一套流程工程化成可跑 CLI。

## 2) 核心结论（给 desk 的版本）
- **一句话核心结论**：同一套 1 秒微观结构特征（失衡/价差/VWAP 偏离）在不同市值币上都能形成可迁移的短周期方向 alpha，不是只在 BTC 偶然有效。
- **一句话证明方式**：论文用统一 CatBoost + walk-forward + SHAP 做跨资产稳定性检验，再用保守 taker/maker 回测验证“统计显著性 != 不可交易”。
- 跨资产 SHAP 排序与依赖形状相近，说明“特征机制”比“单币参数”更稳定。
- 论文 stress test 显示：极端行情下 taker 与 maker 表现分化明显（maker 更容易被 adverse selection 吃掉），这对实盘执行层非常关键。
- 仓库给了完整可复现管线：数据协议、特征、训练、解释、回测、风险报告，不是只有 PDF 观点。

## 3) 为什么和当前项目有关
这条线直接补的是 **raw alpha 素材池（microstructure/directional）**，且不是 breakout/retest 旧循环：
- 可作为 `1m/3m` 主信号，也可降采样成 `5m/15m` 的入场 gate；
- 还能天然拆出 execution 分层（taker 与 maker 分开评估），符合当前 desk 对“完整策略组件拆解”的需求。

## 3.5) 策略拆解（必填）
- 方向属性：短周期方向型（可做多空双向）
- 基础 alpha：`OFI + VWAP pressure (+ spread/depth state)` 对下一窗口收益方向的预测
- regime：高流动+非极端跳变时主做；极端波动时切到保护模式
- filter / veto：`spread` 过宽、深度骤降、盘口异常跳变时 veto
- risk / sizing / execution overlay：
  - 仓位：`size ∝ signal_strength / realized_vol`
  - 执行：默认 taker（先保成交），maker 仅在低 adverse-selection 时启用
  - 成本：显式计入 taker fee + 滑点惩罚

## 4) 可复刻的最小实验（1m/3m/5m/15m）
**研究假设**：`OFI/VWAP pressure` 在 1m 仍保留方向信息，且能迁移到 3m；5m/15m 用作低频执行壳时仍有净边。

**最小可计算定义**（先不用重型模型也能跑）：
1. 由 `1s` 数据构造：
   - `order_flow_imbalance = (buy_vol - sell_vol)/(buy_vol + sell_vol)`
   - `vwap_pressure = ((buy_vwap*buy_vol)-(sell_vwap*sell_vol))/((buy_vol+sell_vol)*mid)`
   - `relative_spread = (ask-bid)/mid`
2. 聚合到 `1m`：取均值/分位数（如 OFI 均值、VWAP pressure 均值、spread P75）
3. 信号：`score = z(OFI_1m) + 0.7*z(VWAP_pressure_1m) - 0.5*z(spread_1m)`
4. 交易：
   - `score > q80` 做多，`score < q20` 做空
   - 持有 1 bar（再测 2/3 bars），反向信号立即平仓

**最小回测切口**：
- 资产：BTC/ETH/2 个中市值币（先 4 币）
- 周期：`1m` 主测，`3m` 次测，`5m/15m` 做降采样验证
- 样本：最近 6~12 个月（含至少 1 段剧烈波动）

**先看 2 个指标**：
- 成本后 `net pnl / turnover`（先判断能否活）
- 分资产一致性（不是只靠单币单段）

## 5) 风险与保留意见
- 这是高频逻辑向低频映射，信号会衰减，`1m` 往上需要重新定阈值与持有期。
- maker 回测在仓库里是保守近似，不是完整队列仿真；别把 maker 收益直接当实盘可实现值。
- 极端事件中信号可能“太强反而拥挤”，需强制加 `spread/depth` 风险闸门。

## 6) 来源
### 论文
- Bieganowski, B., & Ślepaczuk, R. (2026). *Explainable Patterns in Cryptocurrency Microstructure*. arXiv (q-fin.TR).
- DOI: `10.48550/arXiv.2602.00776`
- Readable URL: `https://arxiv.org/abs/2602.00776`
- Full HTML: `https://arxiv.org/html/2602.00776v1`

### 仓库
- amazingchow. (2026). *epcm* (paper-oriented replication/engineering repo).
- Repo URL: `https://github.com/amazingchow/epcm`
- README: `https://raw.githubusercontent.com/amazingchow/epcm/master/README.md`
- NOTE: `https://raw.githubusercontent.com/amazingchow/epcm/master/NOTE.md`
- PROGRESS: `https://raw.githubusercontent.com/amazingchow/epcm/master/PROGRESS.md`
