# 别把 pump 检测只当风控：这份 2026 新仓库更值得先测的是「大幅拉盘后的 5m/15m exhaustion fade」事件驱动 raw alpha
- 时间：2026-03-24 15:20 UTC
- 类型：2026 GitHub 新仓库 + 近 5 年 / 经典 pump-dump 文献 + 仓库 source artifact 本地抽取
- 主题类型：raw alpha
- 基础 alpha：post-pump exhaustion fade（极端拉盘后的短窗衰竭反转 / short mean reversion）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/event-driven/mean-reversion/exhaustion/pump-fade/short-bias/structure-break/rsi/volume/open-interest/funding/cost/crypto/1m/3m/5m/15m/repo/paper
- 证据类型：论文证据 + 工程仓库 + 仓库内事件统计本地抽取

## 1. 这次看了什么
一句话先答：这篇东西的 **base alpha** 不是“pump 检测模型”本身，而是 **极端拉盘后，价格在 5m/15m 上出现衰竭 + 结构转弱时，去做 short fade / 回撤均值回归**。这轮选题用的是 2026 新仓库 `crypto-pump-fade-bot`，再用 La Morgia et al. (2023) / Xu & Livshits (2019) 的 pump-and-dump 文献打地基，判断它能不能进入我们 `1m/3m/5m/15m` 的事件驱动 raw alpha 素材池。

## 2. 核心结论
- 这条线是 **可独立成策略** 的 raw alpha，不只是 filter：先定义“已发生大幅 pump”，再用 `RSI 回落 + volume decline + lower highs + 结构破坏` 去抓随后的短窗反转。
- 我对仓库自带样本做了本地 source probe（`reports/artifacts/quant_digests/pump_fade_source_probe_20260324/summary.json`）：20 个已标注 pump 事件里，**中位 pump 幅度约 174.1%**、**中位回撤约 83.0%**、**中位 dump 时间仅 1 小时**；**83.3% 在 1 小时内开始明显回落**，这很符合 `1m/3m/5m` 快节奏事件 alpha 的节拍。
- 同一份 source probe 里，事件峰值特征也相当一致：**77.8% 的事件峰值 RSI ≥ 70**、**77.8% 的事件成交量 ≥ 平均 2 倍**、**100% 出现 3 个以上 lower highs**。这说明“不是一看到拉盘就反手空”，而是要等 **exhaustion + path deterioration**。
- 仓库给出的 exit 对比值得借：在其 25 笔 validated trades 的回测对比里，**staged exits（50%/20%/30% 分批）收益 7.78%，优于单一 TP 的 7.16%，且最大回撤更低（2.87% vs 3.22%）**。这条线更像“先抓第一段回撤，再留尾仓吃 deeper retrace”。
- 但仓库证据 **不够干净**：另一份 repo 结果文件只给出 **5 笔交易、60% 胜率、总收益 -1.69%**。也就是说，这条线有形状、有逻辑、有工程模板，但 **PnL 证据仍明显不稳定**，必须把它当作“高优先级 raw alpha 候选”，而不是“已经毕业可实盘”的成品。

## 3. 为什么和当前项目有关
这条线对当前 desk 的价值，不在于它“又是一个老派超买反转”，而在于它补的是我们池子里相对少的一类：
- **事件驱动 raw alpha**，不是连续时序动量，也不是横截面排序；
- 更偏 `1m/3m/5m` 的高强度 pocket，而不是全天候一直开机；
- 可以天然接上 `funding / OI / spread / BTC vol` 这些我们已经在做的 risk overlay；
- 若后面验证成立，它和 trend / basis / pairs 的相关性可能低于常规慢频 alpha，适合作为“稀疏但尖锐”的补充组件。

## 3.5 策略拆解（必填）
- 方向属性：事件驱动、short-bias、均值回归 / exhaustion reversal
- 基础 alpha：单币在短时间内出现异常拉盘后，后续 1~6 小时往往出现高概率深回撤；真正可交易的是 **确认后的 fade**，不是裸空 spike 顶点
- regime：
  - 更适合低到中等流动性的 alt / meme / news-driven perp
  - 不适合 BTC/ETH 这类深流动、宏观 beta 更强的主流币直接照搬
- filter / veto：
  - `pump_pct` 必须足够大（先测 `1h/4h/12h/24h` 窗口）
  - 峰值 RSI 过热、volume spike、随后 volume decline
  - 至少出现 `2~3` 个 lower highs 或 first close below prior swing low
  - spread 过宽、BTC 波动过大、funding 不利、OI 没有回落时 veto
- risk / sizing / execution overlay：
  - 入场后止损放在峰值 swing high 上方 + buffer（例如 2%~3%）
  - 仓位按事件质量分层，而不是固定满仓：`quality score = pump size + RSI peak + volume ratio + structure break + OI roll`
  - 出场优先用 staged retracement：小 pump 先看 `38.2/50/61.8`，大 pump 看 `61.8/78.6/88.6`
  - 必须显式计入 taker fee、滑点、资金费、可成交深度，不然这类 microcap fade 很容易纸上富贵

## 4. 可复刻的最小实验
- 研究假设：
  1) 极端拉盘后的 **确认式 fade**，在 `5m` 上比“见顶裸空”更有成本后生存力；
  2) `3m` 能提高响应速度，但更容易被 spread / wick 噪音吃掉；
  3) `15m` 可能更适合做保守版，只抓更大的 pump 和更深的结构破坏。
- 一个可计算定义：
  - 先定义 rolling pump：`pump_{w,t} = high_t / low_{t-w:t} - 1`，`w ∈ {1h, 4h, 12h, 24h}`
  - 候选事件：`pump_{w,t} ∈ [60%, 250%]`，且 `vol_ratio >= 2`，峰值 `RSI >= 70`
  - 入场：出现 **第一根完成的 5m bar** 满足 `close < prior 2-bar low`，同时 RSI 从最近峰值回落至少 `3~5` 点，并伴随 volume decline / OI drop
  - 止损：`peak_high * (1 + 2%~3%)` 或最近 swing high 上方 buffer
  - 出场：分批止盈 + time stop（先测 `2h / 6h / 12h`）
- 最小回测切口（资产 / 周期 / 样本）：
  - 资产：先不碰全市场，优先 `Gate / Bybit / Bitget` 有充足 microcap perp 的交易所；只留 `24h notional >= 1m USDT` 的标的
  - 周期：执行层优先 `5m`，对照 `3m` 与 `15m`
  - 样本：先做 2025-01 至今 event study；每次只抽 top-N pump events，避免把大量平庸样本稀释掉
- 最该先看 3 个指标：
  - 指标 1：`hit_50pct_retrace_within_2h`（事件后 2 小时内是否吃到 50% 回撤）
  - 指标 2：成本后 `net bps / event`
  - 指标 3：`MAE / MFE` 与可成交 spread，确认是不是“统计上会跌，但实盘上空不到”
- **下一步怎么测**：
  1) 先做 event-study，不先做全量连续回测：把所有 `pump>60%` 事件切出来，看 `0.5h / 1h / 2h / 6h` 的 forward return 与回撤分布；
  2) 再做两个版本 A/B：`immediate fade` vs `wait-for-lower-high + break`，验证“等确认”有没有真的改善成本后收益；
  3) 最后加上 `BTC 波动 veto + max spread veto + OI/funding overlay`，看哪些 overlay 是提升 hit rate，哪些只是把交易数砍光。

## 5. 风险与保留意见
- 这条 alpha **天然带执行风险**：越像真实 pump，往往越在深度差、滑点大、插针狠的币上发生；“能看见回撤”不等于“能优雅做空”。
- 仓库样本口径不完全透明，而且内部结果互相打架：一份文件偏正，一份文件偏负，说明这条线很可能对样本选取、入场确认和成本假设高度敏感。
- 文献证明的是 pump-and-dump 普遍存在、回撤显著，但 **不自动等于 perp 做空可稳定赚钱**；是否有借贷 / 合约 / 做空通道、是否会被强平 wick 扫掉，都得单独验证。
- 这条线不应该伪装成“全天候 alpha”。更诚实的定位是：**稀疏事件 raw alpha + 严格 execution veto**。

## 6. 来源
1) La Morgia, M., Mei, A., Sassi, F., & Stefa, J. (2023). *The Doge of Wall Street: Analysis and Detection of Pump and Dump Cryptocurrency Manipulations*. ACM Transactions on Internet Technology, 23(1), Article 11.  
   - DOI: `10.1145/3561300`  
   - DOI URL: `https://doi.org/10.1145/3561300`  
   - Readable URL: `https://arxiv.org/abs/2105.00733`  
   - PDF URL: `https://arxiv.org/pdf/2105.00733`

2) Xu, J., & Livshits, B. (2019). *The Anatomy of a Cryptocurrency Pump-and-Dump Scheme*. 28th USENIX Security Symposium.  
   - DOI: `10.5555/3361338.3361450`  
   - Readable URL: `https://arxiv.org/abs/1811.10109`  
   - PDF URL: `https://arxiv.org/pdf/1811.10109`

3) tocsnostrap (GitHub, 2026). *crypto-pump-fade-bot*.  
   - Repo URL: `https://github.com/tocsnostrap/crypto-pump-fade-bot`  
   - Readable URL: `https://github.com/tocsnostrap/crypto-pump-fade-bot`

4) 本地 source artifact probe（2026-03-24）  
   - Artifact: `reports/artifacts/quant_digests/pump_fade_source_probe_20260324/summary.json`
