# 别把 funding divergence gate 当主角：这份 2026 Hyperliquid 新 repo 更该先测的是「bucket-neutral 1h return mean reversion × funding misalignment gate」
- 时间：2026-03-30 12:42 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：按 residual-correlation bucket 分组后的横截面 1 小时收益均值回归（long short-term losers / short short-term winners）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/mean-reversion/stat-arb/relative-value/hyperliquid/funding/divergence/gate/bucket-neutral/5m/15m/repo
- 证据类型：工程经验

## 1. 这次看了什么
看了 Jbdelrio 在 2026 年公开的 `hyperstat-arb-bot` 源码与配置，重点不是 README 口号，而是 4 个真正决定可复现性的模块：`src/hyperstat/data/universe.py`、`src/hyperstat/strategy/stat_arb.py`、`src/hyperstat/strategy/funding_divergence_signal.py`、`src/hyperstat/strategy/allocator.py`，以及 `configs/default.yaml`、`configs/strategy_stat_arb.yaml`。

这套骨架把一个短周期 relative-value 策略几乎完整写出来了：`5m` 数据、`30` 个币左右的 universe、每 `7` 天重做 bucket、`12 bar`（= `1h`）收益回看、`z_in=1.5 / z_out=0.5 / z_max=3.0`、`min_hold=30m / max_hold=24h`、组合 `gross_target=1.20`、单币上限 `12%`、单 bucket 上限 `35%`。成本也不是空白：默认 `next_open` 成交，`taker 6 bps / maker 2 bps`，滑点是 `8 bps + 10 bps × RV_1h(%)`，还有 `3%` 盘中回撤 kill-switch 与 `720m` cooldown。

更关键的是，它把 **base alpha** 和 **gate / overlay** 分得很清楚：
- `stat_arb.py` 只负责做 **bucket 内的横截面均值回归 raw signal**；
- `funding_divergence_signal.py` 只负责做 **乘法式 confidence gate**；
- `allocator.py` 再去做 **vol scaling / neutrality / caps / emergency flatten**。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值钱的不是“funding 会不会预测价格”，而是它给了我们一个可直接在 `5m/15m` 上做最小实验的 **bucket-neutral 横截面均值回归完整策略骨架**，而 funding divergence 只是后接的 gate。
- **一句话证明方式：** 结论来自 source code + config 的明确参数与调用顺序，而不是作者口头描述。
- 真正的 base alpha 很清楚：先用 `BTC` 作为市场因子，把各币种收益做 beta-neutral residual，再按 residual-return correlation 做层次聚类 bucket；然后在每个 bucket 内，对过去 `12` 根 `5m` bar 的 log return 做 **median + MAD** 标准化，long 最弱、short 最强，属于很干净的 cross-sectional mean reversion / stat-arb。
- 这里不是随便拿“赛道标签”分组，而是 `universe.py` 里每周根据 residual correlation 动态重建 `4~6` 个 bucket，每个 bucket 约 `4~10` 个币。对我们 desk 来说，这比手工 sector 标签更值钱，因为它更像真实可维护的 relative-value 配对/分桶流程。
- `stat_arb.py` 的入场/出场是完整可跑的：`abs(z) >= 1.5` 才激活；raw weight 是 `-clip(z, -3, 3)`；至少持有 `30` 分钟；之后只有在 `abs(z) <= 0.5` 才允许退出；超过 `24h` 强平。这个结构天然比“每根 bar 都跟着 z 值抖动”更适合短周期实盘。
- `funding_divergence_signal.py` 不是另一个独立 alpha，而是把 3 个 funding 侧特征合成为 `[-1, 1]` gate：`carry cross-section z-score`、`price/funding misalignment divergence`、`funding velocity`，默认权重分别是 `0.35 / 0.40 / 0.25`，再按 `w_final = w_stat * (1 + 0.6 * FDS)` 去放大或削弱原始 MR 权重。**重点不是它替代了 alpha，而是它告诉我们：MR 先单独测，gate 再后接测 uplift。**
- `allocator.py` 明确写了组合层：先做 regime gating，再做 FDS gate，再重新做 `dollar_neutral + beta_neutral`，再按 `gross_target=1.20` 标准化，然后套 `12%` 单币上限与 `35%` 单 bucket 上限，最后还有 `z > 3.5` 的 emergency flatten。这已经覆盖了 sizing / risk / exposure control。
- 默认执行假设也够诚实：不是 mid fill，而是 `next_open`；不是零成本，而是 `taker 6bps + 波动率挂钩滑点`。所以这更像一个能拿来做 honest first verdict 的骨架，而不是 PPT alpha。
- 对我们现在的研究池来说，最值得借的不是作者的“新故事”，而是这套拆法：**raw alpha（bucket MR）先单测，shared gate（FDS）后测，overlay（neutralization / caps / kill-switch）单独归因。** 这能直接服务后续的 pairs / cross-sectional / funding 类 alpha 组件化积累。

## 3. 为什么和当前项目有关
当前 desk 的缺口不是“再找一个会讲 funding crowding 的 filter”，而是继续补 **能直接落地的 raw alpha 骨架**。这份 repo 的主价值恰好在这里：
- 它是 `5m` 原生设计，天然贴近我们默认周期；
- base alpha 是相对价值 / 横截面均值回归，不是又一篇 breakout/retest 变体；
- entry / exit / sizing / neutrality / caps / cost 都写出来了，适合作为最小复现实验；
- 它把 funding 相关信息放在 gate 位置，而不是硬伪装成 alpha 本体，这和我们现在要求的“先说清楚 base alpha 是什么”完全一致。

如果这个 raw alpha 连 `raw-only` 版本都站不住，那就不该继续给它堆更多 filter；反过来，如果 `raw-only` 版本能勉强活，FDS 才值得作为 shared gate 去服务更多 relative-value alpha。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值 / stat-arb
- 基础 alpha：在动态 residual-correlation bucket 内，对 `1h` horizon return 做 robust z-score，long 短期相对跌过头的币，short 短期相对涨过头的币
- regime：更适合 bucket 内离散度抬升、均值回归半衰期不太长、整体市场不是单边强趋势碾压的环境
- filter / veto：Funding Divergence Signal 适合作为后接 confidence gate，不适合冒充 alpha 本体；另可继续加 universe liquidity floor / borrowability / jump veto
- risk / sizing / execution overlay：weekly rebucketing、vol scaling、dollar neutral、beta neutral、`gross 1.20`、单币 `12%` 上限、单 bucket `35%` 上限、`z>3.5` emergency flatten、`3%` intraday DD kill-switch、`next_open + fee/slippage` 成本模型

## 4. 可复刻的最小实验
- **研究假设：** 在 Hyperliquid `5m` perp 上，`residual-correlation bucket` 内的 `1h` 横截面均值回归是可交易 raw alpha；funding-price misalignment 作为 gate 只在第二步验证是否能提高 after-cost 质量。
- **数据口径：** 用 Hyperliquid 公开可得的 `5m` candles + funding rates；先做 `30d~60d` 样本；universe 先取 `20~30` 个高成交额币种；缺失率控制在 `1%` 内；剔除最差 `20%` Amihud illiquidity 和 funding-vol 过高币种。
- **bucket 构造：** 用 `BTC` 作为 base factor，先估 rolling beta，再取 residual returns；对 residual correlation 做层次聚类，每周重建 `4~6` 个 bucket，每 bucket 控制在 `4~10` 个币。
- **实验 A（先测 raw alpha）：** 直接复刻 repo 主体：`horizon=12 bars`、`z_in=1.5`、`z_out=0.5`、`min_hold=30m`、`max_hold=24h`、`gross=1.0~1.2`、`dollar+beta neutral`，**不加 FDS，不加 funding overlay**，先看它作为 bare-bones raw alpha 能不能在 `taker 6bps + 滑点模型` 下存活。
- **实验 B（再测 gate uplift）：** 在实验 A 存活前提下，加入 FDS：`fast=8`、`slow=72`、`divergence_window=24`、`weights=0.35/0.40/0.25`，`gate_scale` 先跑 `0.3` 再跑 `0.6`。核心不是看总收益有没有偶然抬升，而是看 **leg hit-rate、极端 adverse excursion、turnover 后的净改善**。
- **15m 映射：** 先把 raw alpha 做成更保守版：`horizon=4~8 bars`、`min_hold=45~60m`、`divergence_window=8~12 bars`。如果 `15m` 下 raw-only 更稳，说明 edge 可能主要死在 `5m` microstructure，而不是信号逻辑本身。
- **最先看 5 个指标：** `after-cost spread pnl`、`bucket neutrality leakage`、`turnover/day`、`long leg vs short leg attribution`、`FDS on/off uplift`。如果 raw-only 版本 already 负得很稳定，就不要继续浪费时间调 gate。
- **下一步怎么测：** 本周最值得先跑的是一个 **两阶段 honest verdict**：先做 `raw-only` 版本，再做 `raw + FDS gate` 版本；两者统一用同一套 universe、bucket、成本模型。只有 raw-only 过线，FDS 才进入后续组件池。

## 5. 风险与保留意见
- 这是一个 2026 新 repo，不是经论文同行评审或长期 OOS 验证的成熟策略，不能把代码存在本身误当成 alpha 已经成立。
- dynamic bucket clustering 可能制造额外换手与 bucket 漂移；如果 rebucketing 太频繁，回测很容易把“结构更新”误写成 alpha。
- FDS 的 divergence 分量本质上是 funding 与 return 的短窗错位关系，若数据时间戳对齐不严，极容易被伪 alpha 污染。
- `taker 6bps + base slippage 8bps` 对很多 alt perp 已经不低，若 raw signal 只在 gross PnL 上勉强成立，after-cost 可能直接归零。
- repo 默认 universe 规模与历史长度都不算很大，先做 honest first verdict 可以，但别急着把它当 production-ready engine。

## 6. 来源
- Jbdelrio. (2026). **hyperstat-arb-bot**. Venue: GitHub. DOI: N/A. Readable URL / Repo URL: `https://github.com/Jbdelrio/hyperstat-arb-bot`
- Key code 1（dynamic universe + residual buckets）: `https://github.com/Jbdelrio/hyperstat-arb-bot/blob/main/src/hyperstat/data/universe.py`
- Key code 2（raw alpha）: `https://github.com/Jbdelrio/hyperstat-arb-bot/blob/main/src/hyperstat/strategy/stat_arb.py`
- Key code 3（funding gate）: `https://github.com/Jbdelrio/hyperstat-arb-bot/blob/main/src/hyperstat/strategy/funding_divergence_signal.py`
- Key code 4（sizing/risk/allocation）: `https://github.com/Jbdelrio/hyperstat-arb-bot/blob/main/src/hyperstat/strategy/allocator.py`
- Key config: `https://github.com/Jbdelrio/hyperstat-arb-bot/blob/main/configs/default.yaml`
- Key strategy config: `https://github.com/Jbdelrio/hyperstat-arb-bot/blob/main/configs/strategy_stat_arb.yaml`
- Avellaneda, Marco; Lee, Jeong-Hyun. (2010). **Statistical arbitrage in the US equities market**. Venue: *Quantitative Finance*, 10(7). DOI: `10.1080/14697680903124632`. Readable URL: `https://doi.org/10.1080/14697680903124632`
- Fischer, Thomas; Krauss, Christopher; Deinert, Alexander. (2019). **Statistical Arbitrage in Cryptocurrency Markets**. Venue: *Journal of Risk and Financial Management*, 12(1). DOI: `10.3390/jrfm12010031`. Readable URL: `https://doi.org/10.3390/jrfm12010031`
- Makarov, Igor; Schoar, Antoinette. (2020). **Trading and arbitrage in cryptocurrency markets**. Venue: *Journal of Financial Economics*, 135(2). DOI: `10.1016/j.jfineco.2019.07.001`. Readable URL: `https://doi.org/10.1016/j.jfineco.2019.07.001`
