# 别把这份 2026 Kraken mean-reversion bot 只读成“布林带抄底脚本”：对 short-cycle crypto desk，更该先保留的是「BB 下轨偏离 × RSI/波动率/Monte Carlo 置信度 admission」这条 raw alpha 壳
- 时间：2026-04-19 21:56 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：价格短时明显跌到局部均值下方后，下一小段时间更容易向布林中轨回归；交易上对应 `lower-band deviation -> long mean reversion`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / mean-reversion / bollinger-band / RSI / volatility / monte-carlo / long-only / kraken / 5m / 15m / repo
- 证据类型：工程经验

## 1. 这次看了什么
看的是 2026-04-10 新建的 GitHub 仓 `GenesisBots/KrakenMeanReversionBot`。公开可见材料主要是 `README.md`，没有完整回测报告，但已经把策略壳讲得很直白：只做**均值回复 long**，核心 admission 由 `Bollinger 偏离 + RSI 不过热 + 波动率在安全区间 + Monte Carlo 回归概率` 组成，出场则用 `hard stop / take profit / trailing stop`。

## 2. 核心结论
- 这东西的 **base alpha 很清楚**：不是“AI bot”也不是“HODL 管理器”，就是 `price below Bollinger mean` 之后赌短时回归的单资产均值回复。
- 对我们 desk 更值钱的不是它挂在 Kraken，而是它把 **raw alpha、admission、sizing、exit** 明确拆层了：`BB 偏离` 是 alpha，本体之外的 `RSI / vol / Monte Carlo confidence` 更像 filter 和 sizing。
- repo 明确写了 **dynamic top-30 universe**、**paper mode 默认开启**、**30 秒 HUD**、**JSONL 订单日志**、**position size scaled by Monte Carlo confidence**，说明它已经是一个可直接借骨架的研究壳，而不只是公式片段。
- 但也别高估：当前公开材料几乎只有 README，没有给手续费、滑点、成交约束，也没给 out-of-sample 指标；所以它现在更像**完整策略骨架候选**，还不是可直接信任的已验证 alpha。
- 一句话核心结论：**可以先保留“BB 下轨偏离做多均值回复”，但真正值得抄的是它把 filter / sizing / exit 分层写清楚的方式。**
- 一句话证明方式：**证据主要来自 repo 的策略描述与工程接口，而不是公开的严肃回测结果。**

## 3. 为什么和当前项目有关
这轮仍然值得收进研究池，因为它服务的是我们当前更缺的东西：**一个可独立复现、可迅速改写成 `5m/15m` 实验的单资产 MR raw alpha 壳**。相比继续围绕固定 price-action 形态内循环，这种 repo 至少能直接回答：
- raw alpha 是什么：`布林带下轨偏离后的回归`
- filter 是什么：`RSI / vol / Monte Carlo confidence`
- sizing 怎么接：`confidence-weighted sizing`
- exit 怎么写：`hard stop / TP / trailing stop`

这对短周期 desk 的价值在于：即便最后 Monte Carlo 这层不保留，`BB 偏离本体 + 轻量 filter + bracket/trailing exit` 也能很快拆成最小可测版本。

## 3.5 策略拆解（必填）
- 方向属性：逆势
- 基础 alpha：`close` 显著跌破局部均值/下轨后的短时向中轨回归
- regime：更适合非单边瀑布、但也不能是极低波动死水；repo 明确要求 volatility 落在安全区间
- filter / veto：`RSI 不过热`、`volatility guardrails`、`Monte Carlo 回归置信度` 共同决定是否准入
- risk / sizing / execution overlay：仓位按 Monte Carlo confidence 缩放；离场用 `hard stop + take profit + trailing stop`；当前缺的仍是 fee/slippage/容量建模

## 4. 可复刻的最小实验
- 研究假设：在 Binance 或 Kraken 的 liquid majors 上，`15m` 下轨偏离后的 long MR 是否在成本前仍有肉；如果有，哪一层 filter 真正在加分。
- 一个可计算定义：
  - `bb_mid = SMA(close, 20)`，`bb_std = rolling_std(close, 20)`，`bb_lower = bb_mid - 2 * bb_std`
  - 基础入场：`close < bb_lower`
  - 过滤 1：`RSI(14) < 35`
  - 过滤 2：`realized_vol_z` 落在 `[-0.5, 1.5]`
  - 过滤 3（轻量替代 Monte Carlo）：用过去 `20` 根 bar 的一阶漂移+波动做 200 次 bootstrap path，若 `P(next 4 bars touch bb_mid) >= 60%` 才入场
- 最小回测切口：`BTC/ETH/SOL/LINK`，`15m` 先测近 `90d`，`5m` 只作为 child execution；先做 long-only，持有 `4/8/12` bars，对比 `tp at bb_mid` vs `fixed-hold`。
- 最该先看哪 1~2 个指标：`gross bps/trade` 与 `hit rate after 8bps round-trip`。第二层再看 `filter 拆解后的 trade count`，避免只靠过度删信号变好看。

## 5. 风险与保留意见
- 这是 **README-heavy** 来源，不是论文，也不是带完整 artifact 的严肃策略仓；证据强度明显低于我们最近那些带 backtest 明细的 repo/paper。
- `Monte Carlo confidence` 很容易沦为噪音包装：若只是用同一窗口估漂移与波动再做短 path simulation，可能只是把当前偏离程度重新说一遍。
- long-only MR 在 crypto 上特别怕**单边 trend day**；如果没有更强的 regime veto，很容易把“接飞刀”误写成“均值回复”。
- 仓库没公开成本、滑点、盘口深度与成交方式；所以现在最多只能说它是**可借骨架**，还不能说是**可直接上桌的完整策略**。

## 6. 来源
- GenesisBots. (2026). *KrakenMeanReversionBot*.
- Repo URL: `https://github.com/GenesisBots/KrakenMeanReversionBot`
- Readable URL: `https://raw.githubusercontent.com/GenesisBots/KrakenMeanReversionBot/main/README.md`
- GitHub API metadata: `https://api.github.com/repos/GenesisBots/KrakenMeanReversionBot`
