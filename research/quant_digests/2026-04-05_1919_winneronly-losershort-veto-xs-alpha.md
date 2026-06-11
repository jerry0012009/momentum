# 别把这篇 2024 crypto momentum 工作论文只读成“TSMOM 强、XSM 弱”：对 short-cycle desk，更该先测的是「winner-only × loser-short veto 的 cross-sectional continuation 壳」这条 raw alpha
- 时间：2026-04-05 19:19 UTC
- 类型：2024 SSRN working paper / AUT 可读全文 PDF source audit（全文方法 + 表格）
- 主题类型：raw alpha
- 基础 alpha：**横截面 recent winners continuation（只做 winner leg，不默认做 loser short）**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/cross-sectional/momentum/winner-only/loser-short-veto/long-only/beta-hedge/log-return/liquidation-risk/liquid-major/binance-futures/15m/5m/3m/1m/paper/public-data/cost/risk
- 证据类型：论文证据（可读全文 PDF）

## 1) 先回答一句：这篇东西的 base alpha 是什么？
**base alpha 不是“经典 winner-minus-loser 长短配对本身”，而是：近期相对强的币，在高流动性主池里，后续仍更容易继续强；真正拖垮策略的往往是 loser short 那条腿。**

所以这轮 intake 的主 digest，不该继续抄成“做多 winners、做空 losers 的 textbook XSM”，而更该直接改写成：
- **raw alpha 本体**：`winner-only cross-sectional continuation`
- **关键否决条件**：`loser-short veto`
- **评价口径升级**：`mean log return / liquidation-aware`，而不是只看 mean return t-stat

## 2) 这次看了什么
主看的是：

**Han, Chulwoo; Kang, Byeongguk; Ryu, Jehyeon (2024). _Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions_. SSRN working paper.**

这篇最有价值的点，不是“crypto 里还有没有 momentum”这种老问题，而是它把很多旧文献常跳过的东西都补上了：
- 交易成本
- 持有期内逐日 mark-to-market
- liquidation risk
- mean return vs **mean log return**
- short leg 在 crypto 里的 jump risk

对我们 desk 来说，这比再多一篇“动量有效/无效”更有用，因为它直接告诉你：**哪条腿是 alpha，哪条腿只是把你炸掉。**

## 3) 为什么这轮值得进研究池
它直接扩充的是 **cross-sectional / relative-strength raw alpha 素材池**，而不是再补一个 filter。

而且它跟当前 short-cycle desk 的关系很直接：
1. 我们已经有不少 `pairs / carry / funding / relative-value` 素材；
2. 但 **“能直接落成横截面 raw alpha、且不强依赖 loser short 才成立”** 的 clean shell 仍然值得补；
3. 这篇给出的不是抽象机制，而是很可操作的一句：**crypto 横截面里，收益更多来自 winner leg；loser leg 不只是弱，还可能因为 rebound/jump 直接把整本书打穿。**

换句话说，它比继续做一个纯 gate / 纯 overlay 更值得，因为它回答的是：
**“下一条可以直接上最小回测的 raw alpha 是什么？”**

答案就是：**winner-only continuation，而不是默认 WML。**

## 4) 核心结论（只留和 desk 最相关的）
### 4.1 这篇 paper 最值得拿走的 4 个结论
- **证据 1：** 论文明确写到，**cross-sectional momentum 证据整体偏弱**；在作者筛过的候选组合里，**21 个 XSM 组合中有 5 个在样本期内被 liquidate，只有 6 个跑赢市场**。
- **证据 2：** 论文给出的最佳 XSM 组合是 **14-day lookback + 7-day hold**，**Sharpe 约 1.28**，而市场组合约 **1.01**。
- **证据 3：** **收益主要来自 long leg**；作者直说 **short leg 暴露于高 jump risk 并带来亏损**。
- **证据 4：** **10 个** 组合有“平均收益率 t-stat > 2”，但只有 **3 个** 组合在 **mean log return t-stat > 2** 下仍站得住；也就是说，**只看 mean return 很容易把会爆仓/会负复利的东西误判成 alpha。**

### 4.2 这对 short-cycle desk 的翻译
把这篇翻成人话，就是：
- `winner continuation` 还能测；
- `loser short` 不能默认带进去；
- 评估时不能只看算术平均收益，要把 **路径、爆仓、跳涨回补** 一起算进去。

这就天然更适合改写成一条 **long-only / beta-hedged 的横截面 alpha 壳**。

## 5) desk 版策略拆解
### 5.1 策略定义
**主题类型：** raw alpha  
**基础 alpha：** 高流动性主池内的 recent winners continuation  
**执行读法：** 只做多相对强者；默认不做 bottom bucket short

### 5.2 最小可交易版本（适配 15m / 5m）
先定义：
- 交易池：`Binance USDⓈ-M perpetual` 的高流动性主池，初版可取 `top 12~20` by 最近 24h quote volume
- bar：`15m` 为主，`5m` 做更快版本
- lookback return：
  - `15m`：过去 `56 / 84 / 112` 根 bar（约 14h / 21h / 28h）
  - `5m`：过去 `168 / 252 / 336` 根 bar（同样对应约 14h / 21h / 28h）
- rank：按 lookback return 做横截面排序

**入场：**
- 仅当某币 rank 落在 top `20%~30%` 时考虑开多；
- 且最近 `1~3` 根 bar 不能已经出现极端一口气拉伸（避免追最后一脚）；
- 若 BTC 同步处于极端单边下杀，可先走 `cash` 而不硬开多。

**出场：**
- 固定持有 `H = 8 / 12 / 16` 根 bar（15m 版）或 `H = 24 / 36 / 48` 根 bar（5m 版）；
- 或当 rank 掉回中位数以下提前平仓；
- 或 hit `ATR / sigma stop` 提前止损。

**默认禁止：**
- 不做 bottom bucket short；
- 不做“winner vs loser”对冲，除非单独证明 loser short 在当前 universe / 当前成本下有正贡献。

### 5.3 sizing / risk / cost
**sizing：**
- 等权或 inverse-vol 都可，初版建议 `position cap = 1/N_active`；
- 单币 notional 上限不超过组合资金的 `10%~15%`；
- 若同方向相关性过高，可用 `BTC beta` 做轻量对冲，而不是直接 short loser basket。

**risk：**
- 单币止损：`1.5~2.0 x ATR(20)` 或 `1.8~2.2 x rolling sigma`
- 组合 kill-switch：当日净值回撤超过 `2.5~3 sigma` 或连续 `K` 次信号失败时，暂停新开仓
- 事件 veto：重大 liquidation cascade / funding 极端 / 币种公告异常波动时禁开

**cost：**
- 必须按 taker 为主先测，maker 只当上限优化；
- turnover 过高时，优先减小 rebalance 频率，而不是幻想 fee 优化能救回来；
- 评价指标必须保留 `after-cost mean log return`。

## 6) 为什么它比 textbook WML 更适合我们
传统横截面动量默认写成：
- long winners
- short losers
- market-neutral

但这篇 paper 给出的更现实结论是：
1. **crypto 的 short leg 不像股票里那样天然给你 alpha；**
2. loser 端经常不是“继续弱”，而是 **反抽 / 暴力回补 / 单点跳涨**；
3. 所以真正 portable 的，不一定是 `WML`，而更像：
   - `long winners + cash`
   - `long winners + light BTC hedge`
   - `long winners + position throttle`

这不是把策略“保守化”，而是在把 **会伤害复利的假 alpha 部分剥掉**。

## 7) 1m / 3m / 5m / 15m 的映射建议
### 15m（主战场）
- 最接近 paper 的节奏；
- 先测 `14h~28h` 的横截面强弱排序；
- holding 先测 `2h~6h`。

### 5m
- 保留同样的“物理时间”窗口，不直接照搬 bar 数；
- 更适合做 `winner continuation` 的 child strategy，但更容易被微结构噪声污染；
- 需额外加：spread / taker imbalance / BTC 同步方向 veto。

### 3m / 1m
- 不建议一开始就把它当主 alpha；
- 更适合作为 `execution layer`：
  - 15m / 5m 先给方向；
  - 3m / 1m 再找 pullback 或短暂失衡做更便宜的进场。

## 8) 最小可复现实验
### 实验 A：winner-only vs textbook WML
**目的：** 先验证“alpha 在 winner leg，伤害在 loser leg”是否在我们口径里仍成立。

- universe：Binance USDT perp `top 15` quote-volume coins
- bar：`15m`
- sort signal：过去 `84` 根收益率
- 三个组合并排：
  1. `winner-only long`
  2. `winner-minus-loser`（经典 WML）
  3. `winner-only + BTC beta hedge`
- 指标：
  - after-cost return
  - after-cost **mean log return**
  - MDD
  - 单日最大 adverse move
  - hit ratio
  - liquidation-style path stress（用高杠杆/保证金假设做压力测试）

### 实验 B：loser short 是否真的拖后腿
- 单独回测 `bottom quantile short-only`
- 看：
  - 是否经常出现单笔极端亏损
  - 收益是否依赖极少数行情日
  - mean return 为正但 mean log return 为负的频率

如果 B 成立，就把 `loser-short veto` 固化成默认规则，而不是可选项。

### 实验 C：5m child execution
- 先用 15m 生成 winner-only 方向；
- 5m 上只在小回踩、spread 不扩、BTC 不反向急杀时进；
- 比较 `15m 直接追` vs `5m child execution` 的成本后表现。

## 9) 风险与保留意见
- 这篇 paper 的主样本是日级别 crypto 横截面，不是 15m；我们拿走的是其**更适合 short-cycle 的结构结论**：`winner leg` 比 `loser leg` 更像真正可搬运的 alpha。
- winner-only 会放大市场 beta；所以它不能裸奔，至少要和 `cash / BTC light hedge / vol target` 做对照。
- 若最后结果显示：winner-only 的 edge 其实全来自 BTC 单边牛市，那它就不是合格的 XS alpha，而只是 market beta 的包装；这必须通过 beta-adjusted 归因验证。

## 10) 来源
1. **Han, C., Kang, B., & Ryu, J. (2024). _Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions_. SSRN Working Paper.**  
   - Authors: Chulwoo Han; Byeongguk Kang; Jehyeon Ryu  
   - Year: 2024  
   - Title: Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market: A Comprehensive Analysis under Realistic Assumptions  
   - Venue: SSRN Working Paper  
   - DOI: <https://doi.org/10.2139/ssrn.4675565>  
   - Readable URL: <https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4675565>  
   - PDF URL: <https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/918729/Time_Series_and_Cross_Sectional_Momentum_in_the_Cryptocurrency_Market_with_IA.pdf>  
   - Mirror PDF URL: <https://quanticfund.net/wp-content/uploads/2024/05/SSRN-id4675565.pdf>  
   - Repo URL: N/A
2. **Binance Developers. USDⓈ-M Futures market data docs（公开市场数据）**  
   - Readable URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api>

## 11) 下一步怎么测（一句话）
先在 `15m top-15` 主流 perp 池上并排回测 `winner-only long`、`WML`、`winner-only + BTC beta hedge` 三条线，并把 **after-cost mean log return + path-wise liquidation stress** 设成硬门槛；若 loser short 持续拉低复利或放大尾部亏损，就把 `loser-short veto` 固化为默认横截面动量底座。