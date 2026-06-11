# 别把这篇 2024 Bitcoin minute 论文只读成“83.7% 准确率”：对 desk 更该先测的是「lagged tech bundle + 高阈值 abstain → 3m/5m continuation」raw alpha
- 时间：2026-03-27 23:22 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：1 分钟级 BTC 的价格、技术指标与短滞后组合里，存在可学习的超短方向信息；但更适合 desk 的落地方式不是死磕 next-minute sign，而是把它当作 `3m/5m` continuation 的高置信度触发器。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/directional/single-asset/bitcoin/minute-data/technical-indicators/lagged-features/separation-index/abstain/continuation/3m/5m/15m/paper/external-data/cost
- 证据类型：论文全文 + 公共数据最小快检

## 1. 这次看了什么
Zeinab Shahsafdari、Ahmad Kalhor 在 2024 年 arXiv 的 **Boosting Bitcoin Minute Trend Prediction Using the Separation Index**。论文主张：先不要急着堆更复杂的模型，而是先用 **Separation Index (SI)** 从可得特征里筛出更有区分度的 observation set，再把这组特征喂给 `BiLSTM + CNN + voting classifier` 去做 Bitcoin 的 next-minute direction / magnitude prediction。

## 2. 核心结论
- **base alpha 很明确**：这不是“SI 很聪明”或者“深度学习很强”，而是 **minute-level BTC direction 本身存在可学习 edge**；SI 只是帮你更快找到更有信息量的特征子集。
- 论文数据来自 **KuCoin 的 BTC 1m 数据（2018~2022）**，候选 observation set 依次包括：
  1. BTC 自身 `OHLCV`；
  2. 从 `BB_RPB_TSL` 策略里挑出的技术指标，并先做参数优化；
  3. 所有特征的 `1m/2m/3m` lag；
  4. 其他币（ETH / USDT / LTC）分钟数据。
- 论文最有价值的结论之一，不是 headline accuracy，而是 **feature ranking 结果**：
  - `BTC OHLCV`
  - `优化后的技术指标`
  - `lagged features`
  这三块加在一起，已经给出最好的 separability；**再加其他币并没有明显增益**。这对 desk 很重要：先把单资产方向信号挖干净，再谈跨币补特征。
- 论文给出的 test-set headline 数字：
  - **BiLSTM** next-minute direction accuracy：**78.14%**；
  - **CNN** next-minute magnitude accuracy：**79.72%**；
  - **Voting classifier**：15 次运行平均 **80.23%**，最好 **83.70%**。
- 我用 Binance Futures 公共 `BTCUSDT perp 1m` 做了一个更 desk 化的弱迁移：**不复刻整套 BiLSTM/CNN**，只拿论文里最可迁移的部分——`paper-style lagged tech bundle`——做 chronological `70/30` 的 Logit proxy。结果很有意思：
  - **直接打 next 1m sign 基本不够用**：OOS accuracy 只有 **50.21%**；
  - 但如果把它改读成 **3m/5m continuation**，效果反而更像可交易雏形：
    - `3m` horizon：整体 accuracy **51.22%**；`p>=0.55` 时 coverage **21.4%**、trade hit **52.6%**、gross mean **+0.11 bp/trade**；`p>=0.60` 时 hit **56.5%**、gross mean **+0.21 bp/trade**；
    - `5m` horizon：整体 accuracy **52.39%**；`p>=0.55` 时 coverage **24.6%**、trade hit **54.2%**、gross mean **+0.48 bp/trade**；`p>=0.60` 时 coverage **2.9%**、trade hit **58.7%**、gross mean **+1.20 bp/trade**。
- 这说明对我们 desk 来说，**最值得 intake 的不是“复刻 83.7%”本身，而是把 paper feature funnel 改写成 `高置信度短延续触发器`**：先在 `1m` 上算分，只交易后续 `3m/5m` 的较大 continuation。

## 3. 为什么和当前项目有关
- 最近 intake 里 `pairs / XS / relative value` 已经很多，这篇正好补一条 **single-asset directional raw alpha**。
- 它和当前主线也对得上：`MAINLINE1_STRATEGY_FACTOR_MAP` 明确允许 `1m/3m` 做更快验证、再向 `5m/15m` 迁移；这篇 paper 刚好给了一个 **minute-level alpha 素材池**。
- 更关键的是，它符合最近学习进展里反复强化的一点：**不要把 headline 方法整包吞下去，而要先拆清 base alpha、filter、execution**。这篇 paper 真正适合我们 desk 的，不是完整黑箱 voting classifier，而是“哪些分钟特征 + 哪些滞后最有用”。
- 它也很好接到 backlog 的现有底座：先把这个方向分数做成独立 raw alpha，再决定是否和现有 `trend/choppy gate`、`risk-on/off`、`multi-timeframe momentum` 组合，而不是反过来继续围绕旧 baseline 微调。

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 方向型 raw alpha
- 基础 alpha：paper-style lagged technical bundle 对后续 `3m/5m` 的方向 continuation 有弱但可提纯的预测力
- regime：优先 `BTC` 主合约、欧美活跃时段、单边波动刚启动但未大幅扩散的窗口
- filter / veto：只在 `p(up) >= 0.55` 做多、`p(up) <= 0.45` 做空；若 `p` 贴近 `0.5` 一律空仓
- risk / sizing / execution overlay：仓位按 `|p-0.5|` 分层；默认持有 `3m` 或 `5m`；若预计 round-trip cost 高于 `0.5~1.0 bp` 级别 gross edge，则必须 veto 或转 maker-only

## 4. 可复刻的最小实验
- **研究假设**：论文里的分钟方向信息并非只能服务 `next 1m sign`，改成 `1m score → 3m/5m continuation` 以后更接近真实可交易口径。
- **数据源**：Binance Futures 公共 `BTCUSDT` perpetual `1m klines`；完全公开可得，更新频率 1 分钟。
- **最小口径**：最近约 `15,000` 根 `1m` bar（约 10.4 天）；特征只用 paper 容易迁移的那一层：`EMA(8/50/100/200)`、`ROC(5/15)`、`RSI14`、`Williams %R(96/480)`、`CMF20`、`VWAP gap`、`volume/trades`，并附加 `lag 0/1/3`。
- **交易规则**：chronological `70/30` train/test；用 Logit 输出 `p(up)`；
  - `p>=0.55` 做多；
  - `p<=0.45` 做空；
  - 否则空仓；
  - 持有 `3m` 或 `5m` 后平仓。
- **我这轮快检结果**（gross、未扣成本）：
  - `1m` 直接打下一分钟方向：accuracy **50.21%**，几乎不可用；
  - `3m` continuation：accuracy **51.22%**；`0.55` 阈值时 trade hit **52.6%**、gross **+0.11 bp/trade**；`0.60` 阈值时 trade hit **56.5%**、gross **+0.21 bp/trade**；
  - `5m` continuation：accuracy **52.39%**；`0.55` 阈值时 trade hit **54.2%**、gross **+0.48 bp/trade**；`0.60` 阈值时 trade hit **58.7%**、gross **+1.20 bp/trade**。
- **一句话翻译**：这篇 paper 在我们 desk 这里，更像 **“分钟级特征选择 + 高阈值 abstain” 的短延续 alpha 原胚**，不是现成可 taker 重锤的 1m sign 策略。

相关快检产物：
- `reports/artifacts/quant_digests/bitcoin_si_minute_trend_transfer_20260327_2322/signal_summary.csv`
- `reports/artifacts/quant_digests/bitcoin_si_minute_trend_transfer_20260327_2322/summary.json`
- `reports/artifacts/quant_digests/bitcoin_si_minute_trend_transfer_20260327_2322/probe_notes.txt`

## 5. 风险与边界
- 论文 headline accuracy 非常高，但样本是 **KuCoin BTC 1m（2018~2022）**；直接外推到今天的 Binance perp，不能默认成立。
- 论文没有公开完整官方复现代码；文中引用的 `BB_RPB_TSL` GitHub 链接目前已不可直接访问，说明可重复性要打折扣。
- 我的迁移只做了 **简单 Logit proxy**，并没有复刻 BiLSTM/CNN/voting classifier，也没有拿到 KuCoin 原始分钟样本；所以这里的意义是 **判别“feature idea 值不值得继续做”**，不是对论文结论做终局判决。
- 当前 gross edge 量级仍偏薄：`5m` 版只有在 **很低成本 / maker / 只做高置信度** 的口袋里才可能活。

## 6. 下一步怎么测
1. **先做 exact-feature replication**：把论文列出的指标完整复刻，特别是 `CTI / CRSI / T3 / EWO / safe_dump_50` 这些本轮 proxy 没带上的特征，看 `5m` 口径能否把 gross edge 从 `0.5~1.2 bp` 再往上推。
2. **把 target 改成“超过成本阈值的 move”**：不要只预测涨跌，直接预测 `future 5m return > fee_floor`，更贴近实盘。
3. **做成本梯度 + 执行分层**：`0 / 1 / 2 / 4 bps` 全跑；同时区分 taker 与 maker-midpoint 模拟，确认这是 maker alpha 还是其实并不够厚。
4. **做 session / volatility split**：分亚洲、欧洲、美股时段，再按 realised vol 分层，看高置信度信号是否只在少数 regime 有效。
5. **接到 15m 上的组合框架**：若 `1m score → 5m trade` 成立，再把它上推成 `15m` 里的 intrabar trigger，而不是单独长期持有。

## 7. 来源
- Shahsafdari, Z.; Kalhor, A. (2024). *Boosting Bitcoin Minute Trend Prediction Using the Separation Index*. **arXiv preprint**.
- Readable URL: https://arxiv.org/abs/2406.17083
- PDF URL: https://arxiv.org/pdf/2406.17083
- Venue note：当前检索到的是 arXiv 版本，未见正式期刊 DOI
- Freqtrade URL: https://www.freqtrade.io/en/stable/
- Repo URL cited in paper: https://github.com/jilv220/BB_RPB_TSL （当前访问已失效/不可直接抓取）
