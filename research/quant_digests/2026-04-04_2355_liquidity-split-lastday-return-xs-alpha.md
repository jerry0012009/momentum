# Zaremba et al.（2021）+ Dobrynskaya（2023）：别把 crypto 横截面只写成统一的 momentum / reversal，`last-day return` 在 liquid majors 上更像 continuation，在 illiquid tail 上才更像 reversal
- 时间：2026-04-04 23:55 UTC
- 类型：paper
- 主题类型：raw alpha
- 基础 alpha：按过去 `1d / 24h` 横截面收益排序，但**先做 liquidity split**——在大币高流动性子宇宙里，`last-day return` 更像 continuation；在低流动性尾部里，才更像 reversal
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / cross-sectional / momentum / mean-reversion / liquidity-split / last-day-return / large-cap / liquid-major / relative-value / 1m / 3m / 5m / 15m
- 证据类型：同行评审论文摘要 + Crossref/OpenAlex 元数据 + 既有同主题论文链路

**先回答 base alpha：这篇东西的 base alpha 不是“流动性解释故事”，而是一条能直接交易的横截面多空——用过去 24 小时收益给币排序，但不要把全市场混成一个方向；对 liquid majors 更该先做 continuation，对 illiquid tail 才更可能出现 reversal。**

## 1) 这次看了什么
这次主材料是：

1. **Zaremba, Adam; Bilgin, Mehmet Huseyin; Long, Huaigang; Mercik, Aleksander; Szczygielski, Jan J. (2021)**, *Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets*, **International Review of Financial Analysis**, 79, 101908.
   - 我拿到的是 Crossref/OpenAlex 元数据与摘要。最关键的结论非常清楚：
   - 样本覆盖 **`3600+` 个币** 的日频价格；
   - **上一天跌得更多** 的币整体上会跑赢 **上一天涨得更多** 的币；
   - 但这个“daily reversal”并不是统一存在：**最大、最可交易的一小撮币，表现出来的是 daily momentum，而不是 reversal**。

2. **Dobrynskaya, Victoria (2023)**, *Cryptocurrency Momentum and Reversal*, **The Journal of Alternative Investments**。
   - 这篇不是本轮主 digest，但它给了很好的“母体背景”：在约 **`2,000` 个最大币**（2014–2020）里，crypto 横截面呈现**短期 momentum、较快切到 longer-horizon reversal** 的“快代谢”。
   - 对 desk 的意义是：**符号和 horizon 都比股票更快、更依赖 universe 定义**。

## 2) 核心结论（给 desk 的版本）
### 2.1 先别问“crypto 到底是 momentum 还是 reversal”
Zaremba et al.（2021）真正有价值的地方，是把这个老问题拆掉了：

- 若你把大量小币、低流动性尾部一起放进样本，看到的更像 **daily reversal**；
- 但若只看**最大、最可交易**的那一撮，符号会翻成 **daily momentum / continuation**；
- 所以很多“crypto 横截面天然爱反转”的结论，本质上可能只是**illiquidity-tail 驱动**，不等于 desk 真正能做的 liquid-major alpha。

翻成人话：
**不是整个 crypto 横截面只有一个统一符号，而是信号方向本身就依赖流动性分层。**

### 2.2 这为什么对我们现在更重要
因为我们最近已经补了不少：
- large-cap cross-sectional momentum
- market-maker style short-term reversal
- 各种 pairs / relative-value / carry

但仍然有一个很现实的坑：
**很多 raw alpha 一旦不先做 liquidity split，就会把“尾部不可交易 reversal”误当成“主战场可交易 alpha”。**

这篇 2021 paper 补的正是这个缺口：
- 它不是再给一个新花样 feature；
- 它是告诉你：**同一个 feature（last-day return），在不同 liquidity bucket 里，符号就可能反过来。**

### 2.3 对 short-cycle desk，最该 intake 的不是尾部 reversal，而是“liquid-major continuation 壳”
从 desk 视角看，最值得先抄的不是：
- 去全市场追 daily loser 反转；

而是：
- 先把 universe 缩到 **可交易大币 / 高 ADV / 低 spread 的 perp**；
- 再问：**rolling 24h return 排名在 5m / 15m 执行层上，是不是 continuation 更强？**

一句话：
**这条 digest 真正补进池子的，是“liquidity-conditioned sign choice”，尤其是 liquid-major 这边的 continuation raw alpha。**

## 3) 策略拆解（必填）
- 方向属性：横截面多空 / market-neutral
- 基础 alpha：`ret_24h = close_t / close_{t-24h} - 1` 的 cross-sectional rank，但**先按 liquidity bucket 分组**
- 主战场 raw alpha：
  - **Liquid-major bucket**：`long top ret_24h`，`short bottom ret_24h`（continuation）
- 备选 / 对照组：
  - **Illiquid-tail bucket**：`long bottom ret_24h`，`short top ret_24h`（reversal）
  - 但默认不作为主实盘方向，只当研究对照，因为成交质量很可能不够
- regime：
  - 只在 `7d ADV`、盘口 spread、可借券/可做空条件合格时启用
  - 若市场极端单边并导致横截面 beta 挤到一边，需要额外做 market beta / BTC beta 控制
- filter / veto：
  - `7d ADV` 低于阈值直接剔除
  - `median spread` 超阈值剔除
  - funding 极端、公告/上币/下架、重大宏观事件窗口可减仓或 veto
- sizing / risk：
  - long / short 等美元或 inverse-vol
  - 组合维持 `beta-to-BTC ≈ 0`
  - 单币权重上限 `5%~10%`
  - 固定 top/bottom 分位，避免权重全挤在极端单币
- exit：
  - 固定持有 `H` 根 bar
  - 或 rank 回到中位区间时提前平仓
  - 叠加 time stop + vol stop
- cost：
  - 必测 taker-only
  - 再测 maker-entry / taker-exit
  - 显式打 fee + slippage + funding

## 4) 对 1m / 3m / 5m / 15m 的 desk 翻译
### 4.1 不要机械复刻“日频论文”
论文原证据是**日频横截面 last-day return**，不是直接证明 `5m/15m` 就有效。

但它非常适合 desk 化成一个**短周期执行壳**：
- 信号生成仍然看 `24h` 回看窗口；
- 执行、风控、再平衡放在 `5m / 15m`；
- 真正要验证的是：**sign 是否随 liquidity split 稳定存在。**

### 4.2 desk 版最小信号定义
1. **Universe**
   - Binance / Bybit / Hyperliquid 最近 `7d` 名义成交额前 `15~30` 个 USDT perp
   - 再加最小门槛：
     - `7d ADV >= 5000万~1亿美元`
     - `median spread <= 4~6 bps`

2. **Feature**
   - `ret_24h = close / close[-N_24h] - 1`
   - `5m`：`N_24h = 288`
   - `15m`：`N_24h = 96`
   - `3m`：`N_24h = 480`
   - `1m`：`N_24h = 1440`

3. **Cross-sectional ranking**
   - 在每个 rebalance 时点，对 universe 内 `ret_24h` 做 rank / zscore
   - 主测 liquid-major continuation：
     - `long = top 20%`
     - `short = bottom 20%`
   - 对照测 illiquid-tail reversal：
     - `long = bottom 20%`
     - `short = top 20%`

4. **Holding / rebalance**
   - `5m` 主测：`H ∈ {6, 12, 24}` bars
   - `15m` 主测：`H ∈ {2, 4, 8}` bars
   - 可每根或每 `2~3` 根 bar 再平衡一次

5. **Risk & execution**
   - 组合美元中性 / beta 中性
   - 单币权重 cap + 相关性 cap
   - 成本先打 `4 / 6 / 8 bps round-trip` 三档
   - 额外记录 funding、换仓频率、拥挤度

## 5) 为什么它比继续补 generic raw alpha 更值得
因为这条线不是在加一个“又一个 feature”，而是在加一个**研究纪律**：

> **任何 cross-sectional momentum / reversal 线，在进入主池前，都必须先过 liquidity split。**

否则会出现两个常见错误：
1. 把尾部 illiquid alpha 误当成 desk 可交易 alpha；
2. 把 liquid-major continuation 和 illiquid-tail reversal 混掉，最后测出“什么都一般”的假结论。

这条 digest 的价值，就是让我们把 `ret_24h` 变成一条**带 sign-router 的 raw alpha 素材**，而不是再写一个“全市场统一做多/做空”的粗糙版本。

## 6) 下一步怎么测（这是本篇最重要的部分）
### 实验 A：先测“符号是否真的由流动性决定”
**目的**：验证这篇 paper 最核心的可迁移命题。

- 同一交易所、同一时段，把 universe 按 liquidity 分成：
  1. top bucket
  2. middle bucket
  3. tail bucket
- 在每个 bucket 内，分别回测：
  - `continuation`: `long top ret_24h / short bottom ret_24h`
  - `reversal`: `long bottom ret_24h / short top ret_24h`

**判定标准**：
- top bucket continuation 为正、tail bucket reversal 为正：说明“sign depends on liquidity”在 desk 口径下成立；
- 若 top bucket 也只剩 reversal，说明论文在 perp/liquid-major 映射失败。

### 实验 B：测 `24h` 信号该在 `5m` 还是 `15m` 执行
**目的**：确认 short-cycle 壳的最佳执行频率。

- 保持 signal 不变，只替换执行层：
  - `5m` rebalance
  - `15m` rebalance
- 比较：
  - gross spread return
  - turnover
  - net after costs
  - monotonicity

**预期**：
- `5m` 可能更灵敏，但 turnover 更高；
- `15m` 可能更像可交易版本。

### 实验 C：是否要把 tail reversal 直接禁用
**目的**：别被“样本里有 alpha”骗进不可交易尾部。

- 对 tail bucket 同时输出：
  - signal edge
  - median spread
  - notional capacity
  - maker fill feasibility
- 若 edge 只存在于高滑点、低容量币，则默认把 tail reversal 降级为“解释层”，**不进主池**。

### 实验 D：做一个简单 sign-router
**目的**：把论文结论变成 desk 组件，而不是只做读书笔记。

- router 规则：
  - 若 `liq_rank >= q80`：启用 continuation
  - 若 `liq_rank <= q20`：默认 no-trade（而不是直接做 reversal）
  - 中间 bucket：只做观察，不急着上线
- 问题不是“哪里都做”，而是：
  - **哪里值得做 continuation**
  - **哪里宁可不做**

## 7) 我对这条线的判断
**值得进研究池，而且优先级不低。**

原因不是它给了一个多复杂的 feature，而是它把一个经常被混淆的问题说清楚了：

1. `last-day return` 本身就是一个 raw alpha 候选；
2. 但它的**符号**不是全市场统一的；
3. 对我们 desk 真正重要的，是 **liquid-major continuation** 这条更可交易的分支；
4. 尾部 reversal 可以保留为研究对照，但默认不该当主战场。

如果后面实验支持，这条线可以扩成：
- 一个独立 raw alpha（liquid-major `24h rank` cross-sectional spread）
- 或一个 shared sign / universe gate（先决定是 continuation、reversal 还是 no-trade）

## 8) 风险与保留意见
- 主论文我拿到的是摘要与元数据，不是全文逐表核对；所以**方向性结论可信，精细参数还要靠后续实验自己定**。
- 论文是**日频 spot 全市场**，我们做的是**perp + short-cycle execution**；不能偷换成“论文已经证明 5m/15m 有效”。
- sign flip 很可能对 universe 定义敏感；若 liquidity proxy 选错，结论会被冲掉。
- liquid-major continuation 可能部分只是 market beta / leader effect 的投影，必须做 BTC / market beta 中性化检验。

## 9) 来源
### 主论文
- Zaremba, Adam; Bilgin, Mehmet Huseyin; Long, Huaigang; Mercik, Aleksander; Szczygielski, Jan J. (2021). *Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets*. **International Review of Financial Analysis**, 79, 101908.
- DOI: `10.1016/j.irfa.2021.101908`
- Readable URL: `https://doi.org/10.1016/j.irfa.2021.101908`
- Repo URL: 未见公开 repo

### 辅助论文（同主题背景）
- Dobrynskaya, Victoria (2023). *Cryptocurrency Momentum and Reversal*. **The Journal of Alternative Investments**.
- DOI: `10.3905/jai.2023.1.189`
- Readable URL: `https://doi.org/10.3905/jai.2023.1.189`
- PDF URL: `https://conference.hse.ru/files/download_file_ex?id=3B5EE9A5-0B18-458A-9458-B4ED0F6C6664&hash=FAE0AB2DC7A67656E89A0B1CB27D8C7D`
- Repo URL: 未见公开 repo
