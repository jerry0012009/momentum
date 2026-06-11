# Fičura（2023 working paper）+ Dobrynskaya（2023 JAI）：别把 crypto 横截面继续写成“全市场都做 reversal”，对 short-cycle desk 更该先测的是「large/liquid 距离近期高点（high-momentum）× market-neutral cross-sectional alpha」
- 时间：2026-04-03 15:10 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：`large/liquid` 币种里，**离近期高点更近** 的币未来继续跑赢，**离近期高点更远** 的币继续跑输；若把小币/低流动性尾部混进来，符号会翻成 reversal
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：cross-sectional / momentum / high-momentum / distance-to-high / liquidity-split / large-liquid / market-neutral / 1m / 3m / 5m / 15m
- 证据类型：同行评审论文 + 开放 working paper 全文

**先回答 base alpha：这篇东西的 base alpha 不是“size/liquidity 解释故事”，而是一个能直接交易的横截面多空——在大币高流动性子宇宙里，离近期高点更近的币继续强、离高点更远的币继续弱；真正该被抛弃的是“把全市场一把抓后看到的 generic reversal”。**

## 1) 这次看了什么
这次把两篇材料拼起来看：

1. **Dobrynskaya, Victoria (2023)**, *Cryptocurrency Momentum and Reversal*, **The Journal of Alternative Investments**。
   - 作用：给出更宽口径的“crypto 有短期 momentum、长周期 reversal，而且节奏比股票快很多”的母体结论。
2. **Fičura, Milan (2023)**, *Impact of size and volume on cryptocurrency momentum and reversal*, **FFA Working Paper 3/2023**。
   - 作用：把上面的母体结论进一步拆开，直接告诉我们：**大币高流动性** 与 **小币低流动性** 的信号方向根本不是一回事；对 desk 最有价值的是 large/liquid 子集上的 **high-momentum（距离滚动高点）**，而不是尾部小币 reversal。

## 2) 核心结论（给 desk 的版本）
### 2.1 先看母体结论：crypto 的“快代谢”确实存在
Dobrynskaya（2023）在约 `2,000` 个市值超过 `100 万美元` 的币上（2014–2020，周频）发现：
- **短周期 momentum** 存在于 `1–4 周` 排序/持有区间；
- **更长一点就转成 reversal**，而且切换速度比股票市场快得多；
- 最强 momentum 出现在 **`2/2`（看过去 2 周、持有未来 2 周）**，年化约 **`70%`**（PDF p.6）；
- 一旦把持有拉长到 `10–12 周`，原先的短排序信号会反噬成很强 reversal（PDF p.6–8）。

这部分对我们最重要的不是“照抄周频策略”，而是：**crypto 横截面确实比传统资产更快完成 underreaction → overreaction → reversal 的切换。**

### 2.2 真正对 desk 有用的，是 Fičura 的 liquidity split
Fičura（2023）把币按上周末的 **市值 + 成交额** 分成：
- **Large and Liquid**：`市值 >= 5000 万美元` 且 `上周成交额 >= 500 万美元`
- **Small or Illiquid**：其余仍保留在样本里的币

然后发现：
- **large/liquid 组的 1W / 2W 标准 momentum 为正**：
  - `mom_1W`：**`+1.36% / 周`，t=`2.33`**（PDF p.8）
  - `mom_2W`：**`+1.44% / 周`，t=`2.69`**（PDF p.8）
- **small/illiquid 组则是强 reversal**：
  - `mom_1W`：**`-3.91% / 周`，t=`-7.31`**（PDF p.8）

这其实把很多“crypto 天生爱反转”的旧印象拆穿了：
**不是 crypto 都爱反转，而是你把低流动性尾部混进来以后，尾部 illiquidity 把符号拖反了。**

### 2.3 比普通 lag-return 更值得先测的是 high-momentum
Fičura 进一步引入 **high-momentum**：
- 定义：`hmom_{t,h} = ln(C_t) - ln(H_{t,h})`
- 直观理解：**当前收盘离过去 h 周最高价有多远**；越接近高点，值越高（没那么负）

结果比普通 momentum 更适合 desk：
- **large/liquid 组**：
  - `hmom_1W` long-short：**`+2.68% / 周`，t=`4.93`**（PDF p.9）
  - 对 BTC CAPM 和 3 因子模型做 alpha 后仍显著：
    - `alpha_BTC = +2.64% / 周`，t=`5.61`
    - `alpha_3F = +2.22% / 周`，t=`5.72`（PDF p.12）
- **small/illiquid 组**：
  - `hmom_1W` long-short：**`-3.67% / 周`，t=`-9.03`**（PDF p.9）

**一句话翻成人话**：
对我们这种默认做大币、做流动性、做 perp 的 desk，**“离滚动高点近不近”比“上一段涨了多少”更值得先当 raw alpha 主信号去测。**

## 3) 为什么它比继续补 generic reversal 更值得
因为这条线直接解决了一个很现实的问题：

- 我们 desk 实际可交易的，主要是 **大币 / 高流动性永续**；
- 许多“reversal 很强”的论文结果，核心利润其实来自 **小币、低量、难成交** 的那一边；
- 如果不先做 liquidity split，就很容易把**尾部不可做的 reversal**误当成**主战场 raw alpha**；
- Fičura 这篇的价值不是又多讲一遍 momentum/reversal，而是明确告诉你：
  - **可交易大币子宇宙里，符号往往是 continuation，不是 reversal**；
  - 而且 **distance-to-high / high-momentum** 比简单 lag-return 更稳。

所以这条 digest 真正补的是：
**raw alpha 素材池里的“liquid-major cross-sectional continuation”组件**，而不是再往 illiquid tail reversal 里内卷。

## 3.5) 策略拆解（必填）
- 方向属性：横截面多空 / market-neutral
- 基础 alpha：`high_momentum = close 相对 rolling_high 的距离`，在 **large/liquid** 宇宙中越接近高点越偏多，越远离高点越偏空
- regime：只在 **高流动性、大市值** 宇宙启用；混入低量尾部时，信号可能翻成 reversal
- filter / veto：
  - `7d ADV` / `rolling notional volume` 不达标直接剔除
  - `spread` 过宽、`funding` 极端、临近重大事件（上币/解锁/宏观）时减仓或 veto
- sizing / risk：
  - 两腿等美元或等波动建仓
  - 单币权重上限 `5%~10%`
  - 组合维持 `beta-to-BTC ≈ 0`
  - 持仓桶数固定（如 top/bottom 各 20%）防止集中在单一币种
- exit：
  - 固定持有 `H` 根 bar
  - 或当 rank 穿回中位数、signal 衰减到阈值内时平仓
  - 叠加 time stop + vol stop
- cost：
  - 必测 taker-only
  - 再测 maker-entry / taker-exit
  - 显式打 fee + slippage + borrow/funding（若跨 venue 或需现货对冲）

## 4) 对 1m / 3m / 5m / 15m 的 desk 翻译
### 4.1 不要机械照搬“周频 1W/2W”
论文原始证据是**周频横截面**。这对我们有启发，但不能假装已经直接证明了 `5m/15m`。

正确做法是把它当成**结构母题**：
- 在 **large/liquid** 子宇宙，continuation 比 reversal 更可能成立；
- `distance-to-high` 这个特征，比简单 lagged return 更稳；
- 如果你把宇宙放宽到低流动性尾部，信号可能翻面。

### 4.2 desk 版最小信号定义
先做一个**短周期映射版**，不是字面复刻：

1. **Universe**
   - Binance / Bybit / Hyperliquid 中最近 `7d` 名义成交额前 `15~30` 个 USDT perp
   - 再加最小流动性门槛：
     - `7d ADV >= 5000万~1亿美元`
     - `median spread <= 4~6 bps`

2. **Feature**
   - `hmom_n = close / rolling_max(close, n) - 1`
   - 在 `5m` 上先测：
     - `n ∈ {48, 96, 288}` 对应约 `4h / 8h / 1d`
   - 在 `15m` 上先测：
     - `n ∈ {16, 32, 96}` 对应约 `4h / 8h / 1d`
   - baseline 同时保留：
     - `ret_n = close / close[-n] - 1`

3. **Cross-sectional ranking**
   - 每个 rebalance 时点，把 `hmom_n` 在 universe 内做 rank / zscore
   - `long = top 20%`
   - `short = bottom 20%`
   - 组合做等美元或 inverse-vol 配重

4. **Holding / rebalance**
   - `5m` 主测：`H ∈ {4, 12, 24}` bars
   - `15m` 主测：`H ∈ {2, 4, 8}` bars
   - 每个 bar 或每 3 bars rebalance 一次

5. **Risk & execution**
   - 组合 notional 中性
   - 单币 cap + 相关性 cap
   - 成本先打 `round-trip 4 / 6 / 8 bps` 三档
   - 额外记录 funding 拖累

## 5) 下一步怎么测（这是本篇最重要的部分）
### 实验 A：先验证“符号是否真由流动性决定”
**目的**：避免把 illiquid-tail reversal 当成 desk 主信号。

- 用同一交易所、同一时段，把 universe 分成：
  1. top liquidity bucket
  2. middle bucket
  3. tail bucket
- 分别回测：
  - `ret_n` 排名
  - `hmom_n` 排名
- 看每个 bucket 的 long-short 符号是否一致

**判定标准**：
- 只有 top bucket 为正，tail bucket 为负：说明论文结论在 desk 口径上成立；以后所有这类信号都必须先做 liquidity split。

### 实验 B：`hmom` 是否真的优于普通 momentum
**目的**：验证 paper 的 desk 版迁移是否保留。

- 同一 universe、同一持有期下比较：
  - `signal_1 = rank(ret_n)`
  - `signal_2 = rank(hmom_n)`
  - `signal_3 = 0.5*rank(ret_n)+0.5*rank(hmom_n)`
- 先看 `5m`，再降采样到 `15m`

**核心输出**：
- `net pnl / turnover`
- `IR / Sharpe`
- `t-stat of spread return`
- `top-minus-bottom monotonicity`

### 实验 C：long-short 还是 long-only + BTC hedge
Fičura 的结果说明：
- 标准 momentum 在 large/liquid 上**更偏短腿驱动**；
- high-momentum 虽然更稳，但 **long-only Q5 本身没强到足以直接当结论**（Q5 周收益 `1.98%`，t=`1.62`）。

所以必须明确测：
- `LS`: top vs bottom
- `LO+hedge`: long top bucket + short BTC beta-adjusted hedge
- `SO+hedge`: short bottom bucket + long BTC beta-adjusted hedge

**预期**：完整 long-short 仍应优于单腿版本；如果单腿版本完全不工作，这条线就更适合作为 market-neutral 组件，而不是裸方向信号。

### 实验 D：cost cliff
这条线虽然选的是 liquid majors，但 turnover 不会低。

必须输出：
- `gross edge`
- `turnover`
- `net edge after 4/6/8 bps`
- 不同 rebalance 频率下的衰减曲线

如果 alpha 只在 `2 bps` 假设下成立，而一到 `6 bps` 就死，那就别进主池。

## 6) 我对这条线的判断
**值得进研究池，而且优先级不低。**

原因不是“这篇 paper 很新”，而是它给了我们一个非常实用的 desk 决策：

1. **先做 liquidity split，再谈 momentum 还是 reversal**；
2. **在 liquid-major 子宇宙里，优先测 high-momentum / distance-to-high，而不是 generic one-bar reversal**；
3. **默认把它当 market-neutral 横截面策略，而不是 long-only 追强。**

如果后面实验支持，这条线可以扩成：
- 一个独立 raw alpha（top/bottom cross-sectional spread）
- 或者作为其他 alpha 的 shared ranking layer（例如只允许 base alpha 在 high-momentum top-half 里开多）

## 7) 风险与保留意见
- 论文是**周频**，我们做的是**短周期映射**；映射失败是正常可能性，不要偷换成“论文已经证明 5m 有效”。
- 标准 momentum 和 high-momentum 都有一定**短腿依赖**；若执行端不适合稳定做空，这条线的实盘价值会打折。
- 结果对 **universe 定义** 很敏感；若把尾部币混进来，符号可能直接翻面。
- `distance-to-high` 在强单边市场里可能退化成 market beta 曝露，必须做 BTC beta / market beta 控制。

## 8) 来源
### 论文 1（地基）
- Dobrynskaya, V. (2023). *Cryptocurrency Momentum and Reversal*. **The Journal of Alternative Investments**.
- DOI: `10.3905/jai.2023.1.189`
- Readable URL: `https://publications.hse.ru/en/articles/811744977`
- Full-text PDF URL: `https://conference.hse.ru/files/download_file_ex?id=3B5EE9A5-0B18-458A-9458-B4ED0F6C6664&hash=FAE0AB2DC7A67656E89A0B1CB27D8C7D`
- Repo URL: 未见公开 repo

### 论文 2（desk 直接可用分支）
- Fičura, M. (2023). *Impact of size and volume on cryptocurrency momentum and reversal*. **FFA Working Paper 3/2023**.
- DOI: 未见
- Readable URL: `https://econpapers.repec.org/RePEc:prg:jnlwps:v:5:y:2023:id:5.003`
- Full-text PDF URL: `https://wp.ffu.vse.cz/pdfs/wps/2023/01/03.pdf`
- Repo URL: 未见公开 repo
