# 别把这份 2026 StandX OBI maker repo 只读成基础设施：对 short-cycle desk，更该先测的是「OBI z-score fair-value shift × inventory skew × min-spread floor」这条完整 raw alpha
- 时间：2026-04-01 05:56 UTC
- 类型：2026 GitHub 新仓库 `README.md` + `backtest_standx_OBI.py` + `optuna_obi_config.json` + `config.json` source audit
- 主题类型：raw alpha
- 基础 alpha：**盘口买卖盘失衡（OBI）的 rolling z-score 会把短期 fair value 从 mid 推开；maker 只要围绕这个偏移后的 fair value 做带 inventory skew 的双边挂单，就不是纯赚 spread，而是在赚“被动成交后 adverse selection 更少”的 microstructure edge**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/market-making/liquidity-provision/order-book-imbalance/obi/fair-value-shift/inventory-skew/microstructure/single-asset/btc/crypto/repo/public-data/1m/3m/5m/15m/cost/execution
- 证据类型：repo source audit（完整策略骨架清晰，但**暂无独立本地 PnL 复核**）

## 1. 这次看了什么
这次主看的是 **djienne (2026)** 的 GitHub 仓库 **StandX_Market_Making_Backtest_BTC**。它不是单纯的数据管道，而是一条相当完整的 maker research pipeline：**WebSocket 采集 order book / trades → Parquet → NPZ → hftbacktest 回放 → OBI maker 策略回测 / Optuna 调参**。对我们更有价值的点不在“又一个 market-making repo”，而在它把 **base alpha、挂单逻辑、库存偏斜、最小价差下限、费用、延迟、数据缺口处理** 都写进了同一个可复现实验骨架里。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得进素材池的，不是“做市基础设施”，而是 **“OBI 失衡 z-score 驱动 fair value 偏移” 本身就是 base alpha；spread capture 只是承载它的执行壳。**
- **一句话说明它怎么证明：** 代码把 alpha 写得很直白：先在 `looking_depth=2.5%` 的盘口范围内计算 `sum_bid_qty - sum_ask_qty`，再做 rolling z-score，把结果乘上 `c1` 推到 `fair_price = mid + c1 * alpha`，最后围绕这个 fair value 做带 inventory skew 的 maker-only 双边挂单。
- 从源码看，它默认不是按分钟线，而是按 **`step_ns = 100,000,000`（100ms）** 更新状态；`window_steps = 6000` 对应 **10 分钟滚动窗口**，`update_interval_steps = 50` 对应 **每 5 秒重估一次 alpha / vol**。这很适合我们把它先归类到 `1m/3m` 主实验，再往 `5m` 压成低频 maker overlay。
- 风险参数也不是空白：仓库默认 `maker_fee = 1 bps`、`taker_fee = 4 bps`，并且在 BBO clamp 之后仍强制 **`min_half_spread_bps = 1.0`**；意思很明确——**它默认承认“价差太窄时，哪怕 alpha 对，也不值得挂”。**
- inventory control 也给得很实：`normalized_position = notional_position / max_position_dollar`，然后通过 `bid_depth_tick = half_spread * (1 + skew * position)`、`ask_depth_tick = half_spread * (1 - skew * position)` 做双边不对称扩缩。也就是说，**库存越偏多，就把 bid 往外撤、ask 往里收；库存越偏空则反过来。**
- 默认执行骨架已经足够像策略：主脚本 CLI 默认 `order_qty_dollar = 20`、`max_position_dollar = 500`、`grid_num = 1`、`vol_to_half_spread = 32`、`skew = 0.5`、`c1_ticks = 605`；Optuna 配置里则把搜索版切成 `order_qty_dollar = 100`、`max_position_dollar = 400`、`latency_ns = 1,000,000`（1ms）和 `looking_depth = 0.025`。这说明它不是“讲概念”，而是**已经把 sizing / quote width / latency 假设都钉进实验口径**。
- 对我们 desk 来说，真正值得拿走的不是 StandX 本身，而是这套拆法：**raw alpha = OBI fair-value shift；regime / overlay = min spread floor + inventory skew + gap flatten；执行形式 = maker-only GTX orders。**

## 3. 为什么和当前项目有关
- 最近素材池已经补了很多 taker 型 directional alpha、pairs、basis、cross-sectional reversal，但 **maker / liquidity-provision 这类“完整策略骨架”卡片还不够多**。这份 repo 正好补这个缺口。
- 它和 `1m/3m/5m/15m` 的关系也很清楚：**alpha 生成发生在 100ms–秒级，主战场更像 `1m/3m`；但我们完全可以把它压缩成 `5m/15m` 的 maker admission / quoting overlay，而不是只把 short-cycle 理解成追涨杀跌。**
- 它也提醒我们：做市不一定只是 execution layer。若 fair value 是被 OBI 系统性推开的，**maker quote placement 本身就是方向性极弱、但信息优势极强的 raw alpha**。

## 3.5 策略拆解（必填）
- 方向属性：单资产双边做市 / liquidity provision / microstructure alpha
- 基础 alpha：盘口失衡 z-score 推动短期 fair value 偏离中间价，围绕偏移后的 fair value 做被动挂单
- regime：流动性足够深、盘口更新稳定、实际可拿到 maker rebate 或低 maker fee 的 BTC/ETH 等主流合约；价差过窄时不应强做
- filter / veto：
  - `min_half_spread_bps >= 1`，价差太窄直接 veto
  - 数据 gap 超过阈值（代码默认 `gap_threshold_minutes = 10`）时撤单 / flatten
  - 盘口失衡标准差塌陷、alpha 不再有 z-score 区分度时不扩张仓位
- risk / sizing / execution overlay：
  - entry：持续双边挂单，但挂单中心不是 `mid`，而是 `fair_price = mid + c1 * alpha`
  - exit：靠反向成交 / inventory 回补 / gap flatten / quote 撤单完成；不是传统 bar-close exit
  - sizing：先从小 clip（源码默认 `20 USD` 或搜索版 `100 USD`）开始，净敞口上限 `400~500 USD`
  - inventory：用 `skew` 控制 bid/ask 的不对称扩缩，防止单边库存累积
  - cost：先诚实按 `maker 1 bps / taker 4 bps` 记账，再单独测是否需要 maker rebate 才能过线

## 4. 可复刻的最小实验
- **研究假设：** 若主流 crypto 合约的短期 microprice / fair value 真的会被盘口失衡 z-score 稳定推开，那么“围绕 OBI-shifted fair value 的 maker quote”应该优于“围绕 raw mid 的对称 maker quote”。
- **公开数据源：** Binance/Bybit/Hyperliquid 的公开 L2 depth + trades WebSocket；只要能拿到 top-20 depth 和逐笔成交，就够做第一版。
- **公开性与更新频率：** 都是公开实时流；最小复现建议存成 **100ms 或 250ms** 快照 / 事件驱动序列。
- **最小可复现实验口径：**
  1. 选 `BTCUSDT` perpetual，先抓 `3~7` 天连续 L2 + trade 数据；
  2. 用 `±2%~2.5%` depth 算 `OBI = bid_qty - ask_qty`；
  3. 做 rolling z-score，得到 `alpha_t`；
  4. 对照两套 quote：A) `mid ± half_spread`，B) `(mid + c1*alpha) ± half_spread`；
  5. 都加上同样的 `inventory skew` 和 `min spread floor`；
  6. 比较净收益、fill 后 adverse selection、库存波动与撤单频率。
- **最先看哪 1~2 个指标：**
  - `net_bps_per_day` 或 `net_bps_per_1000_fills`
  - `post_fill_1s/5s markout`（成交后 1 秒 / 5 秒不利漂移）
  - 第三个再看 `inventory_turnover / max_inventory`

## 5. 风险与保留意见
- 这篇目前更像 **高信号 repo intake**，还不是“已验证可上线 alpha”。原因很简单：仓库 README 和代码给了完整策略骨架，但 **没有附上足够扎实、可直接复核的结果表**。
- StandX 不是 Binance / Bybit。小场地上的盘口形状、tick size、maker 激励、队列填单机制，未必能直接迁到大所；**base alpha 可迁，参数未必可迁。**
- 代码里 `latency_ns = 1ms`、100ms step 这些假设，对大多数普通部署都偏乐观。若实盘拿不到这么快，edge 可能大幅收缩。
- 这类策略最大的坑不是“方向错”，而是 **fill model / queue model / cancel latency**。如果回放里把挂单成交想得太容易，P&L 会比真实世界漂亮很多。

## 6. 来源
1. **djienne (2026). _StandX_Market_Making_Backtest_BTC_. GitHub Repository.**
- Venue: GitHub
- DOI: N/A
- Readable URL: `https://github.com/djienne/StandX_Market_Making_Backtest_BTC`
- Repo URL: `https://github.com/djienne/StandX_Market_Making_Backtest_BTC`
- 重点文件：
  - `README.md`
  - `backtest_standx_OBI.py`
  - `optuna_obi_config.json`
  - `config.json`

2. **djienne (2026). _maket_making_alpha_OBI.pdf_（仓库内技术说明）. Repo bundled document.**
- Venue: GitHub repo docs
- DOI: N/A
- Readable URL: `https://raw.githubusercontent.com/djienne/StandX_Market_Making_Backtest_BTC/main/docs/maket_making_alpha_OBI.pdf`
- Repo URL: `https://github.com/djienne/StandX_Market_Making_Backtest_BTC`

## 7. 下一步怎么测
1. 先别急着复刻 StandX 全栈，直接在 `BTCUSDT` perpetual 上做 **A/B quote placement**：`raw mid` vs `OBI-shifted fair value`；
2. 固定 `min_half_spread_bps ∈ {0.5, 1.0, 1.5}`、`skew ∈ {0.25, 0.5, 1.0}`、`looking_depth ∈ {1%, 2.5%, 5%}` 三组网格，先找“markout 改善”而不是先看总 PnL；
3. 若 `post_fill_1s/5s markout` 明显改善，再补真实 fee / queue / cancel latency；
4. 若在 Binance/Bybit 上只有 maker rebate 场景才转正，就把它降级成 **execution alpha / overlay**；若即使不靠 rebate 也能改善 markout，再升格为 desk 的 maker raw alpha 主线。