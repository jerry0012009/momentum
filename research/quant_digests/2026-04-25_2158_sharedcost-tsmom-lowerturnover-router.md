# 别把这个 2026 alpha 对比仓只读成“趋势 vs 反转谁更强”：对 short-cycle crypto desk，更该先拆的是「7d vol-scaled TSMOM × shared cost budget」这条 raw alpha 壳
- 时间：2026-04-25 21:58 UTC
- 类型：GitHub repo source audit（`README.md` + `Code.ipynb` + repo metadata）+ Binance USDⓈ-M public-data portability probe（`BTC/ETH/BNB/XRP/ADA/DOGE`，`15m`，`2025-11 ~ 2026-04`）
- 主题类型：raw alpha
- 基础 alpha：同一资产的中周期收益延续（medium-horizon time-series momentum / continuation）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / trend / momentum / cross-sectional / mean-reversion / shared-cost / turnover / 15m / 1h-parent
- 证据类型：工程经验

## 1. 这次看了什么
看的是 `mhtkrmz/crypto-alpha-comparison`（GitHub，创建于 2026-03-30）。它的价值不在“又比较了一次 trend 和 mean reversion”，而在于：作者把两条 alpha 放进**同一套协方差、同一 gross cap、同一 turnover penalty、同一 slippage 框架**里比较，逼我们先回答——哪条 alpha 在真实换手约束下更像能活下来。

## 2. 核心结论
- 这份 repo 的 base alpha 其实很清楚：**中周期 TSMOM**。作者最终选中的 trend 分支是 `336` 根 `1h` bar lookback（约 `14d`），而 reversal 分支是 `24` 根 `1h` bar（约 `1d`）的横截面 loser→winner fade。
- 在 repo 自己的 `1h Binance spot` 框架里，trend 分支 validation Sharpe 约 `2.52`，平均每 bar turnover 约 `$2.53k`；reversal 分支 validation Sharpe 约 `-1.21`，平均 turnover 约 `$7.46k`。同样是 alpha，先输赢的不是“故事”，而是**换手厚度**。
- 作者估出的 one-way slippage 约 `8.68 bps`。在这个口径下，trend 分支 gross PnL 约 `$333.9k`，net 还剩约 `$243.4k`，成本拖累约占 gross 的 `27.1%`；reversal 分支 gross 本来就约 `-$141.9k`，加成本后 net 约 `-$354.5k`，成本拖累约为 gross 绝对值的 `149.9%`。
- 我补的 Binance USDⓈ-M `15m` portability probe 更残酷：把 repo 的信号骨架粗移植到 `BTC/ETH/BNB/XRP/ADA/DOGE` 后，`7d` vol-scaled TSMOM 平均 gross 仅约 `-0.15 bps/bar`，但换手约 `6.16%/bar`；`1d` xs reversal 平均 gross 约 `+0.14 bps/bar`，却有 `16.08%/bar` 换手，按 one-way `4 bps` 粗扣后 net 约 `-0.50 bps/bar`，说明**短周期上反转往往先死在 turnover**。
- 不过 trend 分支不是完全没东西：当 `7d` trend z-score 绝对值 `>=1` 时，顺着信号看后续 `4` 根 `15m`（约 `1h`）的 pooled signed return 仍有约 `+0.37 bps/event`；`BNB/BTC` 子样本分别约 `+1.01 / +0.97 bps/event`。它更像 `1h parent -> 15m child` 的方向 admission/router，而不是裸 `15m` taker 主策略。

## 3. 为什么和当前项目有关
这篇东西对 `momentum` 的价值，不是再教一遍“趋势好、反转坏”，而是给了一个很实用的研究姿势：**以后 intake 新 alpha，不要只看 gross edge，要先看 shared-cost / shared-turnover 下谁更厚。** 对我们当前短周期 desk 来说，真正该保留进素材池的是：
- `7d / 14d` 一类较慢的 continuation 作为 parent direction layer；
- `1d` 横截面 reversal 不要默认当 raw alpha 主角，更适合作为相对价值候选，先过 turnover/cost gate；
- 同一个 optimizer / cost model 下做 apples-to-apples 比较，比单看某条策略自己的回测更值钱。

## 3.5 策略拆解（必填）
- 方向属性：顺势（主分支）+ 横截面逆势（对照分支）
- 基础 alpha：中周期收益延续（TSMOM）
- regime：趋势强、横截面分散度不塌时更友好
- filter / veto：shared turnover penalty、slippage budget、gross cap、生存先看 net
- risk / sizing / execution overlay：协方差约束、vol scaling、gross exposure cap；对 short-cycle 需再加 maker-first / child execution

## 4. 可复刻的最小实验
- 研究假设：`1h` 级别较慢 continuation 比 `15m` 直接横截面反转更能穿过 short-cycle 的成本门槛。
- 可计算定义：
  - parent trend：`z_t = ln(P_t/P_{t-7d}) / (sigma_1 * sqrt(7d))`，`|z_t|>=1` 视为有效方向；
  - child exec：只在 parent 方向存在时，去测 `15m` pullback / breakout / microburst admission，而不是每根 `15m` 都裸追。
- 最小回测切口：`BTC/ETH/BNB/XRP/ADA/DOGE`，Binance USDⓈ-M，先做 `15m`，再把 parent 改成 `1h` 聚合信号；样本先跑最近 `6~12` 个月。
- 最该先看：`net bps per trade(or per bar)`、`avg turnover`，再看 `positive asset ratio`。

## 5. 风险与保留意见
- repo 的亮眼结果很依赖固定 `$100k` gross cap；作者自己也承认，这会比 self-financing live account 更好看。
- 我这次 `15m` portability probe 只是“骨架映射”，不是完整复制原 notebook 的优化器，所以只能当 first verdict，不是最终判决。
- 这条 raw alpha 当前**不够厚到直接做 `15m` taker 主系统**；更合理的定位是慢信号 parent / router，给更快的 `1m/3m/5m/15m` 触发层当方向许可。

## 6. 来源
- mhtkrmz. (2026). *crypto-alpha-comparison*. GitHub.
  - Repo URL: `https://github.com/mhtkrmz/crypto-alpha-comparison`
  - README: `https://raw.githubusercontent.com/mhtkrmz/crypto-alpha-comparison/main/README.md`
  - Notebook: `https://raw.githubusercontent.com/mhtkrmz/crypto-alpha-comparison/main/Code.ipynb`
- 本轮 portability probe artifacts：
  - `reports/artifacts/quant_digests/2026-04-25_tsmom-vs-xsreversal_sharedcost_probe.py`
  - `reports/artifacts/quant_digests/2026-04-25_tsmom-vs-xsreversal_sharedcost_probe_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-25_tsmom_parentchild_event_summary.csv`
