# 别把这份 cointegration repo 只读成“又一个配对模板”：对 short-cycle crypto desk，更该先拆的是「spread z-score fade × zero-cross exit × kill-switch」这条完整 raw alpha 壳
- 时间：2026-04-21 12:31 UTC
- 类型：GitHub / repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：先找相对稳定的两腿价差关系；当 spread z-score 偏离过大时做回归（`z` 高就做空 spread，`z` 低就做多 spread），等 spread 回到中枢附近或过零后平仓
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / cointegration / mean-reversion / zero-cross / kill-switch / Binance USDⓈ-M / 5m / 15m / 1h
- 证据类型：工程经验 + repo rule shell + public-data first probe

## 1. 这次看了什么
这次看的是 2026 GitHub repo **ssanin82 / strat-test-cointegration**。它的价值不在“cointegration 这个词本身”，而在于把一条 **可直接运行的 pair mean-reversion 壳** 写得很直白：
- 默认 `ETHUSDT / LINKUSDT`
- `1h`、`200` 根历史窗口
- Engle-Granger + OLS hedge ratio
- rolling `21` 窗口 z-score
- `|z|` 过阈值就双腿同时用 market order 入场
- **zero-cross exit**（z-score 反号就平）
- 账户级 `KillSwitch`（回撤到阈值直接停机）

对 desk 更有用的点是：这不是只给一个信号，而是把 **entry / exit / sizing / risk-stop / state machine** 都摊开了。

## 2. 核心结论
- 这篇东西的 **base alpha 是清楚的**：不是“cointegration 很高级”，而是 **relative-value spread 偏离后的均值回复**。
- repo 值得看的不是 Engle-Granger 教科书部分，而是它把 **zero-cross exit + account-level kill-switch** 当成完整策略骨架的一部分；这比只写 `z>=2` / `z<=-2` 的静态研究更接近能落地的 desk 组件。
- 但 repo 默认参数里有一个很大的现实问题：README 写的 `SIGNAL_TRIGGER_THRESHOLD = 0.02` 对 z-score 来说几乎等于“轻微偏离也硬上”，对短周期 perp 太松，实盘里很容易把成本和噪音一起吃进去。
- 我用 Binance USDⓈ-M 公开 `10` 个 liquid majors（`BTC/ETH/BNB/SOL/XRP/DOGE/ADA/LINK/AVAX/LTC`）做 `45d` portability probe，把思路迁到 `15m/5m` 后，若对全体 pair 统一做 `|z|>=2` 入场、`zero-cross or timeout` 出场，**gross 仍为正，但成本后整体转负**：
  - `15m` 全池 `1986` 笔，gross `+2.70 bps/笔`，粗扣 `8 bps` 后 net `-5.30 bps/笔`
  - `5m` 全池 `2373` 笔，gross `+4.10 bps/笔`，粗扣 `8 bps` 后 net `-3.90 bps/笔`
- 如果只看训练期 residual half-life 较短的 pair（我这里用 `15m <= 48 bars`、`5m <= 144 bars` 做轻量 proxy），结果并没有明显变好：
  - `15m` short-half-life 子集 `173` 笔，net `-4.58 bps/笔`
  - `5m` short-half-life 子集 `252` 笔，net `-4.69 bps/笔`
- 更有意思的是，**看起来最赚钱的 gross pocket 往往不是最像“真 cointegration”那批**，而是一些 mid-cap 比值回归更强、但 half-life 很长的组合：
  - `15m` 上 `XRP/DOGE` gross 约 `+15.32 bps/笔`，`SOL/ADA` 约 `+13.49 bps/笔`
  - `5m` 上 `XRP/DOGE` gross 约 `+16.37 bps/笔`，`SOL/DOGE` 约 `+14.82 bps/笔`
  这说明：**真正有 transfer 价值的，也许不是“严格 cointegration 筛出的 pairs alpha”，而是“ratio-zscore 型 cross-alt relative-value MR”这条更宽的 raw alpha 家族。**

## 3. 为什么这轮仍值得写
虽然我们最近已经连续补过几篇 pairs / stat-arb，但这篇还有独立价值，因为它补的不是“又一个 pair entry”，而是 **完整策略里两个最容易被忽略的部件**：
1. **zero-cross exit**：不是固定拿 `0.5σ` 就走，而是让 spread 真正回到中枢再平；
2. **account-level kill-switch**：pair alpha 常被误以为“天然低风险”，这个 repo 明确把账户回撤当全局停机条件。

对当前 desk 来说，这两块都能直接服务后续 raw alpha 壳，不限于配对：
- zero-cross / center-reclaim 可以迁到 relative-value basket；
- kill-switch 可以迁到所有双腿或多腿策略的组合层。

## 4. 策略拆解
- 方向属性：pairs / stat-arb / relative-value / mean reversion
- 基础 alpha：spread 偏离大时回归中枢
- regime / admission：repo 原版靠 Engle-Granger；我这轮 public quick probe 额外看了 residual half-life proxy，发现“更像 cointegrated”不等于“更能赚钱”
- filter / veto：若沿用 repo，最该先补的不是更多指标，而是 **pair admission 更严 + threshold 更厚 + cost veto**
- risk / sizing / execution overlay：双腿等资本分配、账户级 drawdown kill-switch、zero-cross 平仓、timeout 兜底；实盘若继续迁移到 `5m/15m`，应把 market order 改成 maker-first 或至少更严格地估算四腿摩擦

## 5. 可复刻的最小实验
### 实验目标
验证这条线在 short-cycle crypto 上到底更像：
- A. 严格 cointegration pairs alpha
- 还是 B. 更宽的 cross-alt ratio / spread MR alpha

### 最小实验口径
1. universe 固定 liquid majors（先 8~12 个）
2. discovery 用 `1h` 或 `15m` rolling train window 重估 beta / spread / half-life
3. entry 对照：`|z|>=2.0 / 2.5 / 3.0`
4. exit 对照：`zero-cross` vs `|z|<=0.5` vs 固定 `8/16/24` bars timeout
5. friction ladder：`8 / 12 / 16 bps` round-trip
6. pair admission 对照：
   - 严格 cointegration / short half-life
   - 不做 cointegration，只做高相关 + 短 half-life 的 ratio MR
7. 统计：`trade_count / gross_bps / net_bps / timeout_rate / per-pair contribution / overlap risk`

## 6. 这轮我保留的判断
这份 repo 不是本轮最强的 production 候选，但它很适合进研究池，因为它把 **pair MR 的完整策略骨架** 讲清楚了。当前 public probe 给我的更强结论不是“cointegration pairs 还能直接做”，而是：

> **在 `5m/15m` 上，spread 偏离回归这条 raw alpha 还活着，但更像需要重新定义成更 desk 化的 relative-value MR；原版松阈值 + market order + zero-cross 直搬，多半会被成本吃掉。**

## 7. 下一步怎么测
- 先做一版 **更厚阈值** 对照：`|z|>=2.5/3.0`，看看 trade count 掉多少、单笔 bps 能不能明显变厚。
- 把 **pair admission** 拆成两路并行：`cointegration-first` vs `ratio-MR-first`，别默认前者一定更优。
- 做 **per-pair attribution**：重点盯 `XRP/DOGE`、`SOL/DOGE`、`SOL/ADA` 这类 gross 明显更厚的 pocket，看它们是不是只是阶段性 beta 残差，而不是长期稳定 pair。
- 若下一轮仍 gross 为正、cost 后接近打平，再补 **maker-first / queue patience / single-leg fill failure**，否则先别急着上 live shell。

## 8. 来源
- ssanin82 (2026), **strat-test-cointegration**. GitHub repo. Repo URL: <https://github.com/ssanin82/strat-test-cointegration>
- Readable README URL: <https://raw.githubusercontent.com/ssanin82/strat-test-cointegration/master/README.md>
- Source audit依据：repo landing page + `README.md`
- 本地 artifacts：
  - `reports/artifacts/quant_digests/cointegration_zero_cross_summary_2026-04-21.csv`
  - `reports/artifacts/quant_digests/cointegration_zero_cross_pairs_15m_2026-04-21.csv`
  - `reports/artifacts/quant_digests/cointegration_zero_cross_pairs_5m_2026-04-21.csv`
  - `reports/artifacts/quant_digests/cointegration_zero_cross_trades_15m_2026-04-21.csv`
  - `reports/artifacts/quant_digests/cointegration_zero_cross_trades_5m_2026-04-21.csv`
