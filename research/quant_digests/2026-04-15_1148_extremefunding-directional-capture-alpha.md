# 别把这份 Hyperliquid funding bot 只读成“收租脚本”：对 short-cycle desk，更该先拆的是「extreme funding directional capture × next-settlement timebox」这条 raw alpha
- 时间：2026-04-15 11:48 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：当 perp 预测 funding 进入极端区间时，拥挤的一侧更容易在下一次 funding 结算窗里被反向持仓者同时赚到 **funding transfer + 局部价格回摆**；实现上即 `positive funding -> short perp`，`negative funding -> long perp`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：funding / carry / crowding / directional / Hyperliquid / 1m / 5m / 15m / hourly settlement
- 证据类型：工程经验 + live public-data read

## 1. 这次看了什么
看的是 2026 GitHub 仓库 `atlasdetitan/hyperliquid-trading-bots` 里的 `strategies/funding_arb/bot.py` 与配套 README。它不是 delta-neutral 套利，而是把 **极端 funding 当成拥挤信号**，直接在 Hyperliquid 上做单腿方向 carry。

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：`|hourly funding|` 够极端时，反向站位，至少扛到下一次整点 funding 结算。
- repo 最值得学的不是“看 funding 排名”，而是把 **开仓-持有-退出时钟** 写得很明确：默认阈值 `0.01%/hr`，开仓后最少持有到下一个 top-of-hour funding settlement；若 funding 归零、翻向或超过 `max_hold_hours` 再退出。
- 我补了一次 Hyperliquid live scan（artifact: `reports/artifacts/quant_digests/2026-04-15_hyperliquid_directional_funding_scan.json`）：当前约 `190` 个活跃合约里，`|funding| >= 0.01%/hr` 的只有 `13` 个，`>=0.02%/hr` 的 `7` 个，`>=0.05%/hr` 的只剩 `2` 个；全市场 `|funding|` 中位数只有约 `0.00125%/hr`，说明这条规则本质上是 **极端拥挤 pocket 扫描器**，不是全天候连续信号。
- 当前最极端的几个名字是 `BIO -0.1924%/hr`、`YZY -0.1297%/hr`、`MAVIA +0.0458%/hr`，一眼就能看出：**触发大多集中在小币/高波动尾部**，所以价格风险很可能远大于 funding 本身。

## 3. 为什么和当前项目有关
这条线直接补的是我们当前更缺的 **carry / funding / crowding raw alpha** 素材，而且比“delta-neutral funding 套壳”更像一个可快速做最小实验的方向：
- 触发变量公开可得（funding）
- 时钟明确（整点结算）
- 可直接映射到 `1m/5m/15m` 执行层
- 能自然衍生出 `basis veto / microcap veto / liquidity gate / delta-hedged 对照组`

换句话说，它不是“又一个 funding 面板”，而是一条可单独验证的 **event-driven carry / crowding alpha**。

## 3.5 策略拆解（必填）
- 方向属性：逆拥挤 / carry / 单资产方向
- 基础 alpha：extreme funding directional capture
- regime：只在 `|funding|` 超阈值的极端拥挤状态下开机
- filter / veto：repo 里只有阈值与 `max_positions`；对 desk 更该补 `liquidity / basis / spread / market-cap` veto
- risk / sizing / execution overlay：隔离保证金、整点 funding 结算最短持有、`max_hold_hours` 上限；但 sizing 还是**跨币统一 asset units**，这点很不 production

## 4. 可复刻的最小实验
- 研究假设：Hyperliquid/同类 perp 上，极端正 funding 更容易在接下来一个 funding 窗里兑现为 `short` 收益，极端负 funding 则更容易兑现为 `long` 收益。
- 可计算定义：每 `5m` 记录一次 predicted funding；若 `funding >= +1bp/hr`，下一根 `1m/5m` 做空；若 `funding <= -1bp/hr`，下一根做多。
- 最小回测切口：Hyperliquid 或 Binance 可替代 funding 数据；资产先只做 liquid-midcap 与 microcap 分层；持有窗比较 `到下一次 funding settlement`、`settlement+15m`、固定 `60m`。
- 最该先看：`post-cost avg bps/trade`、`按市值/点差分层后的 hit rate`。第二优先才是 headline Sharpe。
- 必做对照：`裸方向` vs `加 basis veto` vs `delta-hedged`。如果 edge 主要来自 price snapback 而不是 funding，本体就更像 crowding fade，而不是 carry。

## 5. 风险与保留意见
最大保留意见有四个：
1. repo 没有显式 fee hurdle / post-cost 录取线；
2. `--size` 用的是统一 asset units，不是 USD notional，跨币风险严重失真；
3. 触发大多落在小币，容易被点差、冲击成本和单边行情吃穿；
4. bot 重启后不继承已开仓位的“bot-managed state”，不适合作为无状态生产壳直接照搬。

所以我会把它定性为：**raw alpha 清楚、可独立复现，但还不是可直接上线的完整策略**。真正值得复用的是它的 `event clock`：`funding extreme -> next-settlement minimum hold -> normalize/flip exit`。

## 6. 来源
- atlasdetitan. (2026). *Hyperliquid Trading Bots*. GitHub.
- Repo URL: `https://github.com/atlasdetitan/hyperliquid-trading-bots`
- Readable URL: `https://github.com/atlasdetitan/hyperliquid-trading-bots/blob/master/strategies/funding_arb/README.md`
- Strategy URL: `https://github.com/atlasdetitan/hyperliquid-trading-bots/blob/master/strategies/funding_arb/bot.py`
- Live public-data artifact: `reports/artifacts/quant_digests/2026-04-15_hyperliquid_directional_funding_scan.json`
