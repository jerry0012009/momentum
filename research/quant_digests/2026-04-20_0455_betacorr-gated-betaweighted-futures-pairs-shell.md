# 别把这份今天新建的 CT-OS 仓库只读成“又一个 pairs 面板”：对 short-cycle desk，更该先拆的是「beta-corr gated pair admission × beta-weighted spread fade × asset-exclusivity guard」这条完整 raw alpha 壳

- 时间：2026-04-20 04:55 UTC
- 类型：2026 GitHub 新仓库 source audit（`README.md` + `auto_universe_sync.php` + `pair_scanner.php` + `functions.php` + `backtesting.php`）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**高相关/经筛过的 perp pair 在相对价格（ratio / spread）偏离历史均衡后，会向均值回归；执行时不是简单 1:1 对冲，而是按 `beta` 做两腿权重分配，并避免同一资产在多个 pair 同时占用。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（至少能先落成一版完整 baseline；仓库原实现仍有数据链路与统计口径要复核）
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/beta-weighted/correlation-gate/asset-exclusivity/liquidity-guard/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：repo 工程证据 + 公共数据最小快检

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha 不是“相关性高就买”，也不是“资金费率套利”。它的本体就是：pair 的相对错价回归。**

更具体地说，这份 CT-OS 里最值得我们 intake 的，不是 Web 面板，也不是 Telegram/2FA/多用户管理，而是这一条完整的交易骨架：

1. **先找高相关 pair**；
2. **再要求 pair 通过 cointegration / beta 有效性检查**；
3. **当 ratio / spread 的 `z-score` 偏离足够大时开仓**；
4. **按 `beta` 做两腿权重，不是裸 1:1**；
5. **不允许同一资产同时出现在多笔 open pair 里**；
6. **再叠加 liquidity / spike / cooldown / stale-data 等 veto。**

所以它不是 filter，不是 overlay，也不是“又一个 pairs 教学 demo”。它本体就是：

> **pairs / stat-arb / relative-value / mean-reversion raw alpha。**

而且是更偏 **production shell** 的那种 raw alpha，不只是 paper 风格的单条价差回归。

---

## 2. 为什么这轮值得写它

最近这条线我们已经看过不少：
- cointegration-first pairs
- correlation-first ratio z-score
- beta-neutral shell
- half-life constrained pairs
- matching / clustering / OU / Hurst admission

如果再写一篇“静态 z-score 开平仓”的 pairs 摘要，其实没什么意思。

这份今天新建的仓库真正补的，不是新的统计检验，而是：

> **把 pair alpha 从“研究脚本”往“可跑的 live OS”再推进半步。**

它最有价值的不是 admission 方法本身有多先进，而是它把几件 production 常见但论文里经常拆开的东西连起来了：

- `correlation gate`
- `cointegration / beta validity`
- `beta-weighted sizing`
- `dynamic threshold`
- `one-asset-one-open-pair`
- `liquidity / spike / stale / cooldown / min-notional` veto

对 short-cycle desk 来说，这种东西的意义很直接：

> **不是再教你“pairs 是什么”，而是提醒你：raw alpha 本体虽然还是 spread fade，但真正容易决定能不能落地的，是 admission + sizing + overlap governance。**

---

## 3. 这份仓库到底给了什么

### 3.1 来源与元数据
- **Repo / Owner：** `cryptoteamgr/CT-OS`
- **Repo URL：** <https://github.com/cryptoteamgr/CT-OS>
- **Readable URL：** <https://github.com/cryptoteamgr/CT-OS>
- **Description：** `The Ultimate Statistical Arbitrage Engine crypto pair trading`
- **Created：** `2026-04-19T21:52:35Z`
- **Updated：** `2026-04-19T21:53:45Z`
- **Default branch：** `main`
- **Language：** PHP
- **License：** 未声明
- **Authors / Maintainer：** GitHub 用户 `cryptoteamgr` / 文档署名 `cryptoteam.gr`

### 3.2 README 里最关键的 4 句
`README.md` 直接把它定义成：
- Binance futures 的 **Statistical Arbitrage / Pair Trading** 系统；
- 用 **Z-Score** 和 **Beta Correlation** 探测与执行交易；
- 历史深度默认 **500 小时**；
- 核心组件包括：`pair_scanner.php`、`auto_universe_sync.php`、`price_aggregator.php`、`backtesting.php`、`cron_monitor.php`。

翻成人话：

> **它不是一个“只会给信号”的 notebook，而是把 discovery、signal、execution、monitoring、backtest 都摆出来了。**

---

## 4. 源码里最值钱的不是“pair trading”，而是这几个 desk 化细节

### 4.1 `auto_universe_sync.php`：不是拍脑袋选 pair，而是先做 correlation universe
这个文件给了很明确的 universe 逻辑：

- 用历史收益率算两两相关性；
- `minCorrelationToAdd = 0.85`
- `minCorrelationToKeep = 0.75`
- universe 总数有硬上限（`maxTotalPairs = 200`）
- 再把每个活跃 pair 的 `last_z_score` 与 `last_beta` 同步回库

也就是说，这个仓库不是先固定几组 pair，而是：

> **先做“相关性发现 → 弱 pair 清退 → 强 pair 保留”的 pair admission 层。**

这点很重要，因为很多 pairs 仓库都只给你：
- 一个固定 pair 列表
- 或者一段 coint 脚本

但这里更接近 live universe manager。

### 4.2 `pair_scanner.php`：真正值得抄的是动态阈值 + overlap veto
`pair_scanner.php` 的交易入口不是裸 `abs(z) > threshold`，而是加了几层 production guard：

1. **pair 必须 active + cointegrated + beta>0**
2. **数据不能 stale**（超过 1h 不做）
3. **高相关 pair 放宽阈值**
   - `corr >= 0.95` → `entry_z = base * 0.90`
4. **较低相关 pair 收紧阈值**
   - `corr < 0.85` → `entry_z = base * 1.15`
5. **z-score 突然脏跳**（`ΔZ > 1.2`）直接跳过
6. **如果某一腿资产已在 open trade 中，整组 pair 禁开**
7. **5 分钟 cooldown** 防止刚平完又马上重开

这串逻辑其实比“协整 / OLS / z-score”本身更有 desk 价值，因为它回答的是：

> **同一个 raw alpha，怎么避免在 live 上因为重叠敞口、脏跳点、陈旧数据、pair 质量不稳定而把自己玩死。**

### 4.3 `functions.php`：它不是 1:1 对冲，而是显式 beta-weighted sizing
这里最值得记的是两个函数：
- `calculateQuantityFromCapital()`
- `calculateBetaWeighting()`

核心口径：
- 总 exposure = `capital × leverage`
- 两腿权重：
  - `weight_a = 1 / (1 + beta)`
  - `weight_b = beta / (1 + beta)`
- scanner 里还做了一个 **safety floor / cap**：把 `weight_a` 限在 `[0.30, 0.70]`

也就是说它的 sizing 逻辑不是：
- 每腿各买 50%
- 或者简陋美元中性

而是：

> **先用 beta 做相对对冲，再用 clamp 防止某一腿极端失衡。**

这对 perp desk 很实用，因为很多 crypto pair 的波动弹性差很多。裸 1:1 很容易把“看起来 market-neutral”的 trade 做成事实上的 directional bet。

### 4.4 `backtesting.php`：虽然回测口径还粗，但它至少给了完整策略表面
`backtesting.php` 暴露出来的是一整套 production-friendly 参数：

- `entry_z_score`
- `tp_dollar`
- `tp_zscore`
- `sl_dollar`
- `sl_zscore`
- `min_profit`
- `capital`
- `leverage`
- `max_trades`

而且它的回测逻辑不只做 TP，也做：
- 美元止盈/止损
- z-score 收敛止盈
- z-score 扩大止损

虽然它的统计口径仍然比较粗糙（更像 panel backtest，不像严谨研究回测），但至少说明：

> **这份仓库提供的不是“研究想法”，而是一整条可落成 baseline 的参数骨架。**

---

## 5. 这份仓库最值得我们保留的“旁支想法”是什么

如果只把 CT-OS 总结成“高相关 pair 做 z-score 回归”，那就没必要写这篇了。

我认为它真正值得 desk 保留的是下面这条旁支，而且它仍然服务于 raw alpha 本体：

> **beta-corr gated pair admission × beta-weighted spread fade × asset exclusivity**

拆开就是：

### 5.1 它服务的 raw alpha 仍然是 pair mean reversion
alpha 本体没变，还是：
- rich leg 太贵 → 做空 rich leg
- cheap leg 太便宜 → 做多 cheap leg
- 等价差回归

### 5.2 但它给 alpha 多加了一层“能活下来的治理外壳”
这层治理外壳不是 generic risk overlay，而是和 alpha 强耦合的：
- 相关性强 → 可以更早入场
- 相关性弱 → 必须更 extreme 才能入场
- beta 极端 → 权重限制
- 资产重叠 → 禁止叠仓
- 脏跳点 → 不交易

也就是说：

> **它不是把 raw alpha 改成 filter，而是把 filter / veto 直接镶进 raw alpha 的 admission 与 execution。**

这很适合我们当前 desk，因为最近 pairs 线已经不缺“怎么找 spread”，更缺“怎么把 pair book 管得不像事故现场”。

---

## 6. 最小可复现实验：这轮我怎么做的

### 6.1 数据源、公开性、更新频率
- **数据源：** Binance USDⓈ-M perpetual `fapi/v1/klines`
- **公开性：** 完全公开 REST
- **更新频率：** 交易所实时更新；本轮抽样 `15m`
- **实验 universe：** `BTC/ETH/BNB/SOL/XRP/ADA/DOGE/LINK/AVAX/LTC/DOT/TRX`
- **样本长度：** 最近 `1500` 根 `15m` bar（约 15.6 天）
- **训练 / 测试：** `1000 / 500` bars

### 6.2 我这轮映射的 CT-OS 口径
为了做 repo portability probe，我写了一个最小实验脚本：
- 路径：`scripts/run_quant_digest_ctos_beta_pair_probe.py`
- 产物目录：`reports/artifacts/quant_digests/ctos_beta_pairs_probe_20260420_0448/`

映射规则如下：
1. **pair admission：** train 段 return corr `>= 0.85`
2. **beta：** train 段 return beta，要求 `beta > 0`
3. **signal：** `ratio = A / B`，用 train 段均值/方差做 z-score
4. **dynamic threshold：**
   - `corr >= 0.95` → `entry_z = 1.8`
   - 否则默认 `2.0`
5. **dirty spike veto：** `|ΔZ| > 1.2` 不开
6. **exit：** `|z| <= 0.5` 或 `|z| >= 3.5` 或 `hold >= 32` 根
7. **sizing：** `beta-weighted`，并把 `weight_a` clamp 到 `[0.30, 0.70]`
8. **portfolio shell：** 不允许同一资产同时出现在两笔 open pair 中（asset exclusivity）
9. **cost ladder：** 双边 `4 / 8 / 12 bps`

注意：
- 这不是仓库原样精确复刻；
- 但它已经足够回答：**这套“相关性门槛 + beta 权重 + overlap veto”的 production 壳，迁到 Binance 15m 能不能先活。**

---

## 7. 这轮最值得记住的 5 个数据点

来自：
- `reports/artifacts/quant_digests/ctos_beta_pairs_probe_20260420_0448/summary.json`
- `pair_summary.csv`
- `portfolio_selected_trades.csv`

### 7.1 在 12 个 liquid majors 里，按 CT-OS 风格 admission，最近窗口只有 6 组 pair 过门槛
也就是说：

> **如果你真把 corr>=0.85 + beta>0 当 live admission，而不是“看起来像就交易”，当下可交易 pair 数并不多。**

这反而是好事：它说明这套壳天然偏 selective，不是满天撒网式 pair spam。

### 7.2 单 pair 层面，`ETHUSDT-SOLUSDT` 是这轮最像“能活下来的主 pair”
最近样本结果：
- `corr ≈ 0.866`
- `beta ≈ 0.903`
- `n_trades = 4`
- `gross_total ≈ +50.16 bps`
- `net_total @ 8bps ≈ +18.16 bps`
- `avg_hold ≈ 32 bars`

翻成人话：

> **这类高 beta、强共振 majors pair，在 15m 上还能留下正的成本后空间，但交易数不多，持仓也不短。**

所以它更像“慢一点的 short-cycle pair book 核心腿”，不是 ultra-HFT 信号。

### 7.3 `BTCUSDT-ETHUSDT` 也能过，但信号稀疏
结果：
- `corr ≈ 0.889`
- `beta ≈ 0.658`
- 仅 `1` 笔交易
- `gross ≈ +21.32 bps`
- `net @ 8bps ≈ +13.32 bps`

这说明：

> **最经典的 majors pair 不一定差，但往往问题不是胜率，而是密度太低。**

### 7.4 高频 pair 不等于好 pair：`XRPUSDT-LINKUSDT` 毛收益为正，但一扣成本就翻负
结果：
- `corr ≈ 0.865`
- `beta ≈ 0.665`
- `n_trades = 13`
- `gross_total ≈ +39.99 bps`
- `net_total @ 4bps ≈ -12.01 bps`
- `net_total @ 8bps ≈ -64.01 bps`
- `avg_hold ≈ 16.1 bars`

这正好给了一个很实用的 desk 教训：

> **CT-OS 这类 shell 的真风险，不在于“回归失效”，而在于 signal density 一高，毛边会被成本吃光。**

### 7.5 组合壳层面，asset exclusivity 很有意义：4bps 还能活，8bps 就不行
在“同一资产不能同时占多笔 pair” 的组合壳下：
- `selected_trades = 17`
- `distinct_pairs = 2`
- `gross_total ≈ +90.15 bps`
- `net_total @ 4bps ≈ +22.15 bps`
- `net_total @ 8bps ≈ -45.85 bps`
- 主要贡献来自：
  - `XRPUSDT-LINKUSDT`（13 笔）
  - `ETHUSDT-SOLUSDT`（4 笔）

这说明两个事：
1. **asset exclusivity 没把 edge 毁掉**；
2. **但策略对成本极敏感，taker-heavy 情况下很容易转负。**

所以这条线如果要继续做，关键已经不是“有没有 alpha”，而是：

> **能不能把 execution 做成 maker-first / selective-taker，或者进一步压缩无效 high-turnover pair。**

---

## 8. 这条东西对当前 desk 的真正价值

### 8.1 它补的是“完整 pair book 壳”，不是再补一篇统计检验论文
当前项目对 pairs / stat-arb 的研究已经不少，但大部分更偏：
- admission ranking
- threshold design
- coint / OU / Hurst / Kalman 这些研究层

CT-OS 这份仓库更稀缺的点是：

> **它把“pair 是什么”之后那一层——book overlap、beta 权重、dirty spike、liquidity veto、cooldown——也一起暴露出来了。**

### 8.2 它对 `5m / 15m` 的迁移非常自然
最自然的 desk 版本其实是：
- `1h`：更新 pair admission / corr / beta / coint
- `15m`：主信号层（spread fade）
- `5m`：执行层（细化入场与撤单，不一定重新算 admission）

也就是说它不是低频壳，而是非常适合做：

> **慢 admission + 快 execution**

### 8.3 它不是只适合 pairs，本质上还是 relative-value book governance 模板
这套东西以后还可以迁移到：
- funding / basis pair
- same-underlier multispread
- cross-venue spread
- ETF / proxy pressure relative-value sleeve

因为它抽象出来的其实是：
- 先 admission
- 再 weight
- 再 overlap veto
- 再 dirty-state veto

这是一种 **shared execution governance pattern**，但它服务的依然是 raw alpha 本体。

---

## 9. 风险与保留意见

### 9.1 仓库的统计链路并不完全一致
README 说的是 stat-arb / cointegration / beta correlation；
`auto_universe_sync.php` 主要做的是 correlation discovery + ratio z-score + beta；
`pair_scanner.php` 又要求数据库里 `is_cointegrated = 1`。

说明什么？

> **这套系统很可能依赖仓库中未完整展示的额外 cron / DB 流程来补 cointegration 标记。**

所以别把它直接当 paper-faithful 统计实现，更适合当工程壳来吸收。

### 9.2 `backtesting.php` 的回测比较粗
它有完整参数表面，但：
- 价格标准化比较粗；
- 没有真正处理 funding / maker-taker / fill quality；
- 更像 UI backtest，不像 research-grade engine。

所以它给我们的价值主要是：
- 参数壳
- 风控壳
- production-minded workflow

而不是直接给可信收益表。

### 9.3 成本是第一杀手
本轮 quick probe 已经很明显：
- `4bps` 还能勉强活
- `8bps` 很容易翻负

所以如果 desk 后续要真做这条：

> **执行质量比“再优化一点 z-score 参数”更重要。**

### 9.4 `asset exclusivity` 是优点，也是容量上限
禁止同一资产在多个 pair 同时占用，确实能减少 hidden directional overlap；
但它也会把可扩张性压低。

所以它更适合：
- 先做 `top few pairs`
- 再做 selective scaling

不适合一开始就把 pair 数开很大。

---

## 10. 下一步怎么测（直接可执行）

### 10.1 先把 admission 拆成两层 A/B
- **A：corr-first → coint confirm → beta sizing**（CT-OS 风格）
- **B：coint-first → corr ranking → beta sizing**

看哪种顺序在当前 Binance perp majors 上：
- 交易数更健康
- overlap 更低
- 成本后更稳

### 10.2 把 `asset exclusivity` 做成可调 governor
直接测三档：
1. **strict**：同资产绝对不可重叠
2. **sector-aware**：允许弱相关 pair overlap
3. **gross-cap**：允许 overlap，但限制 per-asset gross notional

这一步很关键，因为它决定 pair book 的容量上限。

### 10.3 做 maker-first / taker-fallback execution probe
当前 8bps 已经明显吃不消，下一步别再先卷信号，先测：
- maker-only fill rate
- maker-first 失败后 taker-fallback
- 只在 spread excursion 更极端时 taker

如果这个环节做不出来，alpha 再漂亮也没用。

### 10.4 把 CT-OS 的 `dirty spike veto` 系统化
本轮只用了 `|ΔZ| > 1.2` 的简单 veto。
下一步建议加：
- `ΔZ percentile veto`
- 单腿异动幅度 veto
- 短窗 realized vol veto
- 同时结合 order-book depth / quote spread

### 10.5 把 beta weight clamp 做成可学习参数
现在仓库风格是把 `weight_a` clamp 到 `[0.30, 0.70]`。
下一步可以做：
- `[0.25,0.75]`
- `[0.30,0.70]`
- `[0.40,0.60]`

看在：
- edge
- drawdown
- slippage proxy
- concentration

之间谁更平衡。

---

## 11. 结论（一句话版）

> **CT-OS 这份今天新建的仓库，不值得我们再把它读成“pairs 回归老故事”；它更该被保留成一条 production-minded raw alpha shell：`beta-corr gated pair admission × beta-weighted spread fade × asset exclusivity guard`。最近 Binance `15m` quick probe 也说明，这套壳不是没边，但高度成本敏感——真正该优先补的不是更多 pair，而是 overlap 治理与低成本执行。**

---

## 12. 来源
1. **cryptoteamgr / cryptoteam.gr (2026). _CT-OS_ (GitHub repository).**
   - Repo URL: <https://github.com/cryptoteamgr/CT-OS>
   - Readable URL: <https://github.com/cryptoteamgr/CT-OS>
   - GitHub API metadata: <https://api.github.com/repos/cryptoteamgr/CT-OS>
2. **CT-OS README**
   - <https://raw.githubusercontent.com/cryptoteamgr/CT-OS/main/README.md>
3. **CT-OS source files**
   - `auto_universe_sync.php`: <https://raw.githubusercontent.com/cryptoteamgr/CT-OS/main/auto_universe_sync.php>
   - `pair_scanner.php`: <https://raw.githubusercontent.com/cryptoteamgr/CT-OS/main/pair_scanner.php>
   - `functions.php`: <https://raw.githubusercontent.com/cryptoteamgr/CT-OS/main/functions.php>
   - `backtesting.php`: <https://raw.githubusercontent.com/cryptoteamgr/CT-OS/main/backtesting.php>
4. **Binance USDⓈ-M Futures API — Kline/Candlestick Data**
   - <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>

---

## 13. 本地产物
- 研究笔记：`research/quant_digests/2026-04-20_0455_betacorr-gated-betaweighted-futures-pairs-shell.md`
- 最小实验脚本：`scripts/run_quant_digest_ctos_beta_pair_probe.py`
- 实验产物目录：`reports/artifacts/quant_digests/ctos_beta_pairs_probe_20260420_0448/`
