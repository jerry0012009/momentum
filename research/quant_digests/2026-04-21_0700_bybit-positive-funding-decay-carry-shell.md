# 别把这个 Bybit funding bot 只读成“又一个收租脚本”：对 short-cycle crypto desk，更该先回答的是「high positive funding persistence × exit-threshold」这条 carry raw alpha 到底够不够厚
- 时间：2026-04-21 07:00 UTC
- 类型：GitHub repo + public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：同所 `positive funding` 足够高、且在接下来 `1~3` 个 funding windows 内持续不塌；交易上对应 `long spot + short perp`，赚 funding carry，直到 funding 低于退出阈值
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：carry / funding / basis / relative value / same-venue / bybit / spot-perp / 15m child execution / cost
- 证据类型：工程证据 + public-data probe

## 1. 这次看了什么
看的是 `NikoSAN02/crypto-trading-bot`（2026）的 Bybit funding-arb repo，核心文件是 `strategies/funding_arb.py`、`risk/position_manager.py`、`simulate.py`。它不是在讲“预测涨跌”，而是在讲一个完整 carry 壳：`entry=annualized funding >= 15%`，`exit=annualized funding < 5%`，同所现货对冲，外加持仓上限、reserve、drawdown stop。

## 2. 核心结论
- 这份 repo 的 base alpha 很清楚：**不是 funding 高这一刻本身，而是 funding 高了之后还能继续高 enough to pay costs**。
- 它值得学的不是“Bybit API 接法”，而是**把 carry 写成完整策略壳**：entry / exit / sizing / liquidity floor / drawdown guard 都给了。
- 我用 Bybit 公共 funding history 对 `BTC/ETH/SOL/XRP/DOGE/ADA/LINK/AVAX/LTC/BCH` 做了 `180d` portability probe：若按 repo 风格把 round-trip 粗扣成 `17 bps`，`entry >= 10% APY` 的 `1087` 个事件里，未来 `2` 次 funding 的平均 gross 仅 `+1.42 bps`，净值约 `-15.58 bps`。
- 更狠一点按 repo 原阈值 `entry >= 15% APY` 看，这个 10-major bucket 里最近 `180d` **直接 0 个事件**；当前 live snapshot 里最高也只是 `BCHUSDT ≈ +1.0 bps/8h ≈ 10.95% APY`。
- 所以这条线目前更像：**完整 raw alpha 壳成立，但 broad liquid-major same-venue 版明显不够厚**；若要救，得去更小币、更极端 funding spike，或降成 `15m` child execution / maker-first / pre-funded` execution sleeve`。

## 3. 为什么和当前项目有关
这条线和 desk 现在要补的 raw alpha 素材池直接相关，因为它属于 `carry / funding / basis` 家族，而且 repo 已经把完整交易骨架写出来了。它的价值不在“今天就能开机”，而在于告诉我们：**carry raw alpha 不是看 funding 排行榜就行，关键是 funding persistence 能不能覆盖真实摩擦。** 这对后续所有 funding / basis / cross-venue intake 都是共通 admission 逻辑。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / carry
- 基础 alpha：`high positive funding persistence`，即高正 funding 在后续若干结算窗里继续为正并维持足够厚度
- regime：高拥挤、多头杠杆需求强、perp 相对 spot 偏贵的阶段更容易出现
- filter / veto：spot twin 可交易、`24h` 流动性下限、entry APY 阈值、exit APY 阈值
- risk / sizing / execution overlay：单笔上限、总曝险上限、reserve、drawdown halt；对 short-cycle desk 更该补 `15m` maker-first child execution 与 basis/borrow veto

## 4. 可复刻的最小实验
- 研究假设：在 Bybit/币安这类同所 spot-perp 市场里，**高正 funding 事件之后的 `1~3` 次 funding payment 是否足以覆盖 round-trip 成本**。
- 一个可计算定义：`entry = funding_annualized >= {10%,15%,20%}`；`exit = funding_annualized < 5%`；收益先只看 `sum(next_k funding)`，再粗扣 `fees + slippage`。
- 最小回测切口：先跑 liquid majors，再单独跑 mid-cap bucket；bar 级别用 `15m` 只负责 child execution，不要硬伪装成逐根方向信号。
- 最该先看指标：`事件数 / 平均 gross carry bps / 成本后 net bps / next-1 funding persistence`。

## 5. 风险与保留意见
- 我这轮 public probe 只验证了 **funding persistence**，没把真实 basis 变化、maker fill、borrow frictions、inventory 占用 fully 加进去；因此这里是偏乐观的第一层筛子。
- repo 里还写了负 funding 分支（long perp 收 funding），但那一侧不再是严格 delta-neutral，价格风险会重新回来；对我们 desk，不该直接和 spot-hedged positive-funding 壳混成一类。
- 结论不是“funding carry 不存在”，而是：**同所、liquid-major、粗暴 taker/半被动版现在明显不过线。**

## 6. 下一步怎么测
先别继续把 same-venue majors funding shell 当主 alpha 加仓；下一步更值钱的是两条：
1. 做 `mid-cap positive-funding spike` 的事件研究，按 `maker-first 15m child execution` 重算 break-even；
2. 同时补一个 `cross-venue funding/basis spread` 版本，对照“单所 funding persistence 不够厚”到底是 alpha 不存在，还是 venue 选错了。

## 7. 来源
- NikoSAN02. (2026). *crypto-trading-bot*. GitHub.
  - Repo URL: `https://github.com/NikoSAN02/crypto-trading-bot`
  - Readable URL: `https://github.com/NikoSAN02/crypto-trading-bot/blob/main/README.md`
- Key source files:
  - `https://raw.githubusercontent.com/NikoSAN02/crypto-trading-bot/main/strategies/funding_arb.py`
  - `https://raw.githubusercontent.com/NikoSAN02/crypto-trading-bot/main/risk/position_manager.py`
  - `https://raw.githubusercontent.com/NikoSAN02/crypto-trading-bot/main/simulate.py`
- Public data:
  - Bybit V5 Market API — funding history / tickers
  - `https://bybit-exchange.github.io/docs/v5/market/history-fund-rate`
  - `https://bybit-exchange.github.io/docs/v5/market/tickers`
- Local artifacts:
  - `reports/artifacts/quant_digests/bybit_positive_funding_decay_summary_2026-04-21.csv`
  - `reports/artifacts/quant_digests/bybit_positive_funding_decay_detail_2026-04-21.csv`
