# 别把这份 funding-rate repo 只读成 ML 作业：对 short-cycle desk，更该先测的是「post-cost funding+basis dislocation × delta-neutral carry admission」这条完整 raw alpha
- 时间：2026-04-09 21:46 UTC
- 类型：GitHub / repo source audit
- 主题类型：raw alpha
- 基础 alpha：`正 funding + perp 相对 spot 偏贵` 的状态，在未来持有窗里更可能通过 `funding 收取 + basis 回归` 兑现；对应交易是 `short perp + long spot` 的 delta-neutral carry / relative-value。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：carry / funding / basis / relative value / delta-neutral / post-cost / admission / binance
- 证据类型：工程证据（repo 文档 + 配置 + source audit）

## 1. 这次看了什么
看的是 MengerWen 2026 GitHub repo **Deep Learning-Based Delta-Neutral Statistical Arbitrage on Perpetual Funding Rates**。它最有价值的点不是“用了 LSTM”，而是把一条 desk 真能落地的 carry 策略写成了完整研究管线：`市场数据 -> feature -> post-cost label -> baseline/dl signal -> backtest`。

## 2. 核心结论
- **一句话核心结论：** 这份仓库真正值得抄的不是模型名，而是把 `funding + basis` 明确翻译成 **未来净收益（post-cost net return）** 的标签，先判断“这笔 delta-neutral carry 值不值得做”，再谈模型。
- **一句话证明方式：** 作者不是预测裸价格方向，而是直接把未来 `perp leg + spot leg + funding - 全部摩擦成本` 做成监督目标，属于很适合 desk 的“机会质量预测”。
- label 设计很硬：默认方向直接写死为 `short perp + long spot`，目标是未来 `8h/24h` 的 `future_net_return_bps`，并区分 `盈利` 与 `可交易（>5bps edge）` 两层标签。
- 成本没有被藏起来：默认成本模型是 `4 * (5bps taker fee + 3bps slippage) + 10bps gas + borrow`，也就是**仅四腿 taker+slippage 就先吃掉约 32bps**，这比很多“看 funding 排行榜就上”的 repo 诚实得多。
- 特征也不是玄学：主窗口是 `24h funding/basis`、`72h z-score`、`168h regime`，再叠 `open interest / volume / realized vol / shock`，本质是在做 **carry persistence + basis MR + crowding/risk state** 的联合 admission。

## 3. 为什么和当前项目有关
这条线比继续做“谁 funding 高就空谁”的粗糙 carry 更进一步，因为它已经把当前 desk 真正在意的四件事写清楚了：
1. **base alpha 是什么**：不是排行榜，而是 `funding+basis` 的 post-cost 可兑现性；
2. **什么时候不做**：edge 不够、shock 太大、regime 不对时不做；
3. **成本后还剩多少**：目标本身就是净收益；
4. **怎么迁到短周期**：虽然原 repo 先跑 `1h`，但完全可以把窗口映射到 `15m`，把它做成 `5m/15m` 的 entry router / carry admission 层。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / carry / delta-neutral
- 基础 alpha：`positive funding + positive spread/basis` 在未来持有窗继续兑现，`short perp + long spot` 收 funding 并等 basis 回归
- regime：`positive_funding_regime`、`high_vol_regime`、`wide_spread_regime`、`shock_regime`
- filter / veto：`min_expected_edge_bps=5`、`funding_rate_bps > 1~2`、`spread_zscore_72h > 1~1.5`、高 shock / 低 liquidity 可 veto
- risk / sizing / execution overlay：next-bar open 执行；默认 `position_notional=10,000 USD`、`max_open_positions=1`；显式扣 fee/slippage/gas/borrow

## 4. 可复刻的最小实验
- **研究假设：** `15m` 下，只要 `funding 持续为正 + spread_zscore 仍高 + OI/vol 不在极端 shock`，则未来 `8h/24h` 的 delta-neutral 净收益更高。
- **可计算定义：** 在 Binance `BTCUSDT perp + BTCUSDT spot` 上，把 repo 的 `8/24/72/168h` 窗口改写成 `32/96/288/672` 根 `15m`；目标仍定义为未来 `32/96` 根的 `perp leg + spot leg + funding - costs`。
- **最小回测切口：** 先只做 `BTCUSDT`，样本从 2024-01 到今；比较三组：`always-on carry`、`规则基线（funding>1bps & spread_z>1.5）`、`post-cost score top bucket`。
- **最先看 2 个指标：** `post-cost bps/trade` 与 `tradeable rate (>5bps net edge)`；第三个再看 `shock bucket 下的回撤`。

## 5. 风险与保留意见
- 这份 repo 目前更像 **课程项目级 research pipeline**，不是已经验证完的 production alpha。
- 先跑的是 `BTCUSDT 1h`；若硬压到 `1m/3m`，很可能会把本来是 carry/admission 的信号误用成逐 bar directional alpha。
- borrow、gas、资金费结算时间、spot/perp 实际可成交性都还是简化版，真实执行可能比 repo 默认更差。
- 如果后续 desk 要把它接到更快节奏，最合理的位置不是“每 15m 必开仓”，而是 **短周期 entry router + 8h funding window carry scheduler**。

## 6. 来源
- MengerWen. (2026). *Deep Learning-Based Delta-Neutral Statistical Arbitrage on Perpetual Funding Rates*. GitHub Repo.
- Repo URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
- Readable URL: `https://github.com/MengerWen/Deep-Learning-Based-Delta-Neutral-Statistical-Arbitrage-on-Perpetual-Funding-Rates`
- 关键源码/文档：
  - `README.md`
  - `docs/features.md`
  - `docs/labels.md`
  - `docs/signals.md`
  - `configs/backtests/default.yaml`
  - `configs/models/baseline.yaml`
