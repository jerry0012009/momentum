# 别把这份 2026 Polymarket maker repo 只读成“预测市场 bot”：对 short-cycle desk，更该先测的是「complementary-outcome sub-par spread × Binance latency shield」这条完整 raw alpha
- 时间：2026-04-07 11:29 UTC
- 类型：GitHub 新 repo source audit（`README.md` + `config.yaml` + `src/market_maker.py` + `src/window_tracker.py`）
- 主题类型：raw alpha
- 基础 alpha：同一 `5m` 二元市场里，若 `UP` / `DOWN` 两边 maker bid 合计明显低于 `$1.00`，就能买到一对“互补结果”；Binance 现货先行价格只负责在单腿成交后帮你及时撤掉更危险的另一腿
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / prediction-market / relative-value / stat-arb / market-making / complementary-outcomes / pair-sum / latency-shield / binance / polymarket / BTC / ETH / SOL / 5m / repo / public-data / cost / risk
- 证据类型：工程经验

## 1. 这次看了什么
这次看的是 **Jordan Maragliano (2026)** 的 GitHub 新 repo **`polymarket-spread-bot`**。它表面像“预测市场做市 bot”，但对我们 desk 真正更值钱的，不是押方向，而是 repo 里那条更像 **relative-value raw alpha** 的读法：**在同一 `5m` crypto up/down 市场里，同时在 `UP` 和 `DOWN` 两边挂 maker 买单；只要两腿最终总成本 `< $1`，到结算时天然只会有一边赔付、另一边兑付 `$1`，组合本身就锁定正毛利。**

更重要的是，作者没有把风险处理留在口号层。`market_maker.py` 把这条 alpha 明确拆成：**pair-sum edge**（本体）+ **Binance latency shield**（单腿成交后的毒性防守）+ **timebox / exposure cap**（仓位与尾盘管理）。这就不再是“预测市场看起来可能有价差”，而是一个能直接写成 entry / exit / sizing / risk 的完整壳。

## 2. 核心结论
- **一句话核心结论：** 真正值得抄的不是“去预测 5 分钟涨跌”，而是 **“当互补结果两边一起买还不到 `$1` 时，优先做 pair capture；Binance 只拿来防守 one-leg adverse selection。”**
- **一句话证明方式：** repo 直接在 `src/market_maker.py` 里写出 pair 评估、双腿下单、partial-fill 处理、shield cancel、到期结算与 guaranteed-profit 计算，不是只有概念图。
- `evaluate_spread()` 的核心公式很直接：`profit_per_share = 1.0 - (up_best_bid + down_best_bid)`。当前配置要求 `min_spread_profit: 0.04`，也就是 **至少留 4 美分/份** 才允许开 pair；这比“只要小于 1 就上”更像真交易，不是教材硬套。
- 这条线给了完整风控壳：`order_size: 5.0`、`max_position: 30.0`、`max_single_exposure: 10.0`、`partial_fill_timeout_sec: 10`、`cancel_time_remaining: 15`、全局 `max_drawdown: -20.0`。一句人话：**作者默认不是无限补腿，而是把“先保命、再吃 pair edge”写进了参数。**
- repo 在双腿都成交时把收益写得很明白：`Guaranteed profit = 1 - (up_fill + down_fill)`。也就是说，这条策略本质不是方向预测，而是 **complementary-outcome mispricing**。
- 还有一个很值钱的 source-audit 细节：当前 `config.yaml` 里 **`spread_capture_enabled: false`，但 `arb.enabled: true`**。这说明作者虽然把 pair-sum spread capture 这条壳写完整了，但默认运行更偏向另一条 directional lag-arb 分支。对我们是提醒：**这个 raw alpha 值得进池，但 first verdict 要先验证“pair completion rate + one-leg risk”是否真能活。**

## 3. 为什么和当前项目有关
这条线和当前 `momentum` 的关系很直接：它补的是我们还不够系统化的 **prediction-market / complementary-outcome stat-arb** 素材，而不是再做一篇 generic Polymarket 情绪观察。

对当前 desk，价值主要有三层：
1. **它是完整 raw alpha，不是 filter。** base alpha 很清楚：`UP + DOWN < 1` 的互补合约错价；Binance shield 只是 risk / execution overlay。
2. **它直接落在可接受的短周期。** repo 默认就是 `BTC / ETH / SOL` 的 `5m` crypto 市场，和我们当前允许的短周期窗口直接兼容。
3. **它提供了一个很可复用的“外部领先源 + 内部 pair edge”结构。** 以后即使不做 Polymarket，这种“pair mispricing 本体 + 外部快市场 veto / shield”思路，也能迁移到期权、跨 venue、甚至某些 basket RV 壳里。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / market-making
- 基础 alpha：同一 hard-expiry `5m` 二元市场中，互补结果 `UP` 与 `DOWN` 的双腿 maker 成本合计低于 `$1.00`
- regime：Polymarket order book 更新慢于 Binance、且 pair edge 还没被 taker / 其他 maker 完全吃掉的活跃窗口
- filter / veto：仅做 `BTC / ETH / SOL`、仅做 `5m`、最小 pair edge ≥ `4c`、距离结算不足 `15s` 不再开新 pair、partial fill 超 `10s` 进入保护
- risk / sizing / execution overlay：`$5` 单笔、总敞口上限 `$30`、单腿上限 `$10`、单腿成交后用 Binance 现货变动做 shield cancel，避免被更快的外部价格先行打穿

## 4. 可复刻的最小实验
- **研究假设：** 在 Polymarket `BTC / ETH / SOL 5m` 市场里，`UP_bid + DOWN_bid <= 0.96~0.98` 的 pair-sum 错价不是幻觉；若给单腿成交后的未成交腿加一个外部 `Binance` shield，净结果会明显好于裸做 pair。
- **一个可计算定义：**
  - `pair_edge_t = 1 - (best_bid_up_t + best_bid_down_t)`
  - 当 `pair_edge_t >= 0.04` 时，按相同 size 在两边各挂一笔 maker BUY
  - 若 `10s` 内仅单腿成交，且 Binance 从挂单时刻起对该 pair 不利移动超过阈值（先用 repo 的 0.1% 量级做起点），则取消另一腿
- **最小回测切口（公开可得）：**
  - 数据源：Polymarket CLOB 最优 bid/ask + Gamma 市场列表 + Binance 实时价格流
  - 标的：`BTC / ETH / SOL`
  - 周期：先只做 `5m`
  - 样本：先抓最近 `14~30d`
- **最该先看 2 个指标：**
  1. `both-filled rate` 与 `guaranteed-gross-edge`（真正吃到完整 pair 的比例）
  2. `shield save rate` 与 `one-leg adverse-selection PnL`（shield 到底是在救命，还是只是在制造 missed fill）

一个很值钱的 first verdict 问题不是“总收益多高”，而是：**在公开数据上，pair edge 触发频率 × 两腿最终都成交的概率，够不够支撑这条策略成为 desk 的可复现素材。**

## 5. 风险与保留意见
- **当前证据主要是源码与参数，不是公开回测表。** 也就是说，它首先是一条高质量工程线索，不是已经被论文级统计验证的现成金矿。
- **repo 默认把 `spread_capture` 关掉，本身就是一个警报。** 可能原因包括：pair-sum 机会太稀、queue priority 太重要、或单腿风险比想象中更难管。这个不能忽略。
- **Polymarket 的真问题不只是“有没有 edge”，而是能不能成交。** maker priority、订单队列位置、取消延迟、部分成交，都可能让 paper edge 变成 production 噪音。
- **这条线和我们过去写过的 Polymarket directional lag-arb 不是同一件事。** 这里真正值得测的是 complementary-outcome RV，不要把它又降级成“Binance 涨了就追 YES”。
- 如果 first verdict 显示 pair completion rate 很低，这条主题就应退回 `shared execution idea / niche raw alpha`，而不是硬抬进主策略线。

> **最值得复用/复现的点：** 用外部更快的现货市场，不是为了直接给预测市场做方向信号，而是为了给“互补合约错价”这条 raw alpha 提供单腿成交后的保护层。

## 6. 来源
1. **Jordan Maragliano. (2026). _polymarket-spread-bot_. GitHub repository.**
   - Repo URL：`https://github.com/jordanmaragliano-coder/polymarket-spread-bot`
   - README：`https://raw.githubusercontent.com/jordanmaragliano-coder/polymarket-spread-bot/main/README.md`
   - 首次提交（repo 历史）：`2026-03-20`，提交信息为 `Polymarket spread bot - two-sided market making with Binance latency shield`
2. **Polymarket Developers — CLOB Quickstart / Market Channel**
   - Readable URL：`https://docs.polymarket.com/developers/CLOB/quickstart`
   - Readable URL：`https://docs.polymarket.com/developers/CLOB/websocket/market-channel`
3. **公开市场发现与行情来源（repo 内使用）**
   - Gamma API endpoint：`https://gamma-api.polymarket.com/markets`
   - Binance Spot WebSocket docs：`https://developers.binance.com/docs/binance-spot-api-docs/web-socket-streams`
