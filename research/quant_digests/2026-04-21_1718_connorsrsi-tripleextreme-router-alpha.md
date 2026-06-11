# 别把 ConnorsRSI 只读成“老派超买超卖指标”：对 short-cycle crypto desk，更该先拆的是「triple-extreme overshoot × cross-back exit」这条 mean-reversion raw alpha / router
- 时间：2026-04-21 17:18 UTC
- 类型：GitHub / repo source audit + classic practitioner basis + behavioral-paper support + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：当 `RSI(3)`、`streak RSI(2)`、`1-bar return percent-rank(100)` 同时极端时，说明这不是普通回撤，而是 **短窗方向 + 连续性 + 当下冲击幅度** 三重过度伸展；这类过冲在 crypto perp 上更容易在随后几根 bar 内回吐，交易上可写成 `CRSI < 15 做多 / CRSI > 85 做空`，并用 `CRSI cross back through 50` 或 `time-stop` 离场
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：mean reversion / ConnorsRSI / streak / percent-rank / overshoot / router / Binance / 15m / 5m
- 证据类型：repo 工程骨架 + 经典策略文献/实践来源 + public-data first probe

## 1. 这次看了什么
这轮主来源不是论文 headline，而是 **RexRenatus (2026), The-Art-of-Finance** 这个策略库里 `mean-reversion/connors-rsi.md` 那条规则卡。它把 `ConnorsRSI` 写成了非常 desk-friendly 的 raw alpha 壳：
- `RSI(3)`：价格短动量是否已经很极端
- `RSI(2)` on streak：连续涨/跌天数是否已经拉到极限
- `PercentRank(100)`：当前 1-bar 变动在最近 100 根里是不是极端大/极端小

真正值得 intake 的，不是“又一个 RSI 指标”，而是这三块一起回答了一个更适合短周期 desk 的问题：**现在看到的是普通 pullback，还是已经到了“方向、持续性、冲击幅度”三件事同时极端的过冲点。**

### 来源
- **Repo / 策略库**：RexRenatus (2026), *The-Art-of-Finance: 165 quantitative trading strategies for crypto perpetual futures*  
  Repo URL: <https://github.com/RexRenatus/The-Art-of-Finance>
- **具体策略卡**：`mean-reversion/connors-rsi.md`  
  Readable URL: <https://github.com/RexRenatus/The-Art-of-Finance/blob/master/mean-reversion/connors-rsi.md>  
  Raw URL: <https://raw.githubusercontent.com/RexRenatus/The-Art-of-Finance/master/mean-reversion/connors-rsi.md>
- **经典实践来源**：Larry Connors, Cesar Alvarez (2012), *An Introduction to ConnorsRSI*  
  Venue: practitioner whitepaper / note  
  DOI: 无  
  Readable URL: <https://pdfcoffee.com/an-introduction-to-connorsrsi-2012-09-pdf-free.html>  
  说明：不是近 5 年论文，但它是这个 alpha 壳的概念母体
- **行为支撑论文**：Shimon Kogan, Igor Makarov, Marina Niessner, Antoinette Schoar (2024), *Are cryptos different? Evidence from retail trading*  
  Venue: *Journal of Financial Economics*  
  DOI: <https://doi.org/10.1016/j.jfineco.2024.103897>  
  Readable URL: <https://researchonline.lse.ac.uk/id/eprint/122266/>

## 2. 核心结论
- **一句话核心结论：**ConnorsRSI 在短周期 crypto perp 上不是 broad taker alpha，但它作为 **“三重极端过冲” 检测器** 仍然有价值，尤其更适合被读成 **router / pocket selector**，而不是全池无脑双向抄底摸顶。
- Binance USDⓈ-M、10 个 liquid majors、最近约 `45d(15m)` / `20d(5m)` quick probe：
  - `15m` 全池、`CRSI<15 / >85` 入场、`CRSI 回到 50` 或 `8-bar` time-stop 离场，合计 **`2924` 笔**，gross 约 **`+2.19 bps/笔`**，胜率 **`60.09%`**，但粗扣 `8 bps` round-trip 后约 **`-5.81 bps/笔`**。
  - `5m` 全池同口径、合计 **`4102` 笔**，gross 约 **`+0.94 bps/笔`**，胜率 **`58.43%`**，粗扣后约 **`-7.06 bps/笔`**。
- 但 symbol pocket 还在：
  - `15m` 单币 gross 较厚的是 **`LTC +6.02 bps/笔`**、`ADA +5.61`、`DOGE +3.86`、`BTC +2.71`；`SOL` 反而是 **`-3.48 bps/笔`**。
  - `5m` 单币里 **`ETH +5.04 bps/笔`** 明显最厚，`BTC +1.77`、`ADA +1.48` 还行，其余大多偏薄。
- 如果改成 strongest-only router，而不是同刻多币一起做：
  - `15m top1` strongest 信号，next `8` bars 平均约 **`+5.73 bps`**；其中 `BTC ≈ +20.93 bps`、`ETH ≈ +12.29`、`DOGE ≈ +10.45`、`BNB ≈ +7.89`。
  - `5m top1` strongest，next `12` bars 平均约 **`+1.74 bps`**；其中 `SOL ≈ +11.38 bps`、`XRP ≈ +8.62`、`DOGE ≈ +5.79`，但仍不足以直接覆盖 taker 成本。

**第一性结论：**这条 base alpha 是真的，但更像 **“极端过冲打分器 + router”**，不是“所有币、所有时刻都值得反手”的 standalone 主策略。

## 3. 为什么和当前项目有关
这轮最值得 intake 的地方，不是 ConnorsRSI 的名字，而是它对 mean reversion 做了一个很适合当前 desk 的拆解：

- `RSI(3)` = 短期方向是否已经过头
- `streak RSI(2)` = 这段 move 是否已经“连续太久”
- `PercentRank(100)` = 当前 bar 的冲击在最近窗口里是不是异常大

这比只看 `RSI<30` 更像真正可复现的 **raw alpha skeleton**，因为它把“过冲”从单一价格位置，扩展成了 **幅度 × 连续性 × 相对极端度** 三个维度。对我们现在持续补充的 raw alpha 素材池，这条线正好补的是：
- 单资产 mean reversion
- 适配 `5m/15m`
- 不依赖外部数据
- 还能自然长出 `router / symbol admission / execution veto`

## 3.5 策略拆解（必填）
- 方向属性：逆势 / mean reversion
- 基础 alpha：`ConnorsRSI` 极端值代表短窗三重过冲，随后几根 bar 内更容易向中性回摆
- regime：当前策略卡默认无独立 regime gate
- filter / veto：`CRSI<15` 做多、`CRSI>85` 做空，本质上已经是极端过滤；但还没有 volume / trend / funding veto
- risk / sizing / execution overlay：策略卡有 FSM 与 cooldown，但没有给出 desk-ready 的成本、仓位上限、maker/taker admission、ATR stop 细化

## 4. base alpha 到底是什么
先按用户要求，明确回答一句：

> **这篇东西的 base alpha 是什么？**
>
> **答：是 `triple-extreme overshoot mean reversion`。**
>
> 不是“RSI 指标本身”，也不是“技术分析大全”，而是：**当价格短动量、连续涨跌长度、单根冲击在各自维度同时达到极端时，后续更容易出现反向回摆。**

因此它是标准 **raw alpha**，不是 filter / overlay。

## 5. 这条壳为什么可能在 crypto 上成立
经典 ConnorsRSI 最早是在 equity short-term MR 语境下提出；迁到 crypto 的逻辑并不是“照搬美股”，而是：

1. **crypto 零售资金更容易顺着价格追，而不是立刻逆向再平衡。**  
   Kogan et al. (2024) 给的是账户级证据：同样的散户，在 crypto 上比在股票/黄金上更 momentum-like。这个行为会制造短窗过冲。

2. **perp 市场里，短时拥挤经常配合杠杆与止损链条放大。**  
   所以单看 `RSI` 容易太粗，但把 **连续性** 和 **冲击 rank** 加进去，更接近真正的“过冲而非正常趋势延续”。

3. **PercentRank 这一维有自适应波动的价值。**  
   它不是固定 `x%` 涨跌阈值，而是问：**“这一根，在最近 100 根里算不算大？”**  这对 crypto 这种波动时高时低的市场尤其重要。

## 6. 可复刻的最小实验
### 本轮 public-data quick probe 口径
- 市场：Binance USDⓈ-M perpetual
- universe：`BTC/ETH/SOL/XRP/DOGE/ADA/BNB/LINK/AVAX/LTC`
- 周期：`15m` 主测 + `5m` child 对照
- 指标实现：
  - `RSI(3)` on close
  - `streak` = 连续上涨/下跌 bar 计数
  - `RSI(2)` on streak
  - `PercentRank(100)` on `1-bar return`
  - `CRSI = (RSI3 + RSI2_streak + PercentRank100) / 3`
- 入场：信号后下一根开盘
- 出场：`long` 在 `CRSI >= 50` 或 `max_hold` 离场；`short` 在 `CRSI <= 50` 或 `max_hold` 离场
- time-stop：`15m = 8 bars`，`5m = 12 bars`
- 粗成本：`8 bps` round-trip，仅做 first verdict

### 本轮产物
- `reports/artifacts/quant_digests/2026-04-21_connorsrsi_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-21_connorsrsi_probe_router.csv`
- `reports/artifacts/quant_digests/2026-04-21_connorsrsi_probe_trades.csv`

## 7. first verdict：怎么读这些数字
### 7.1 15m：全池不够厚，但 router 价值比裸做更大
`15m` 全池 gross `+2.19 bps/笔` 不算弱到毫无信息，因为它有 **60%+ 胜率**，说明“反向回摆”方向判断并不差；问题在于厚度不足，撑不起 taker 成本。

这类形态最合适的读法不是“直接判死”，而是：
- **别做 broad pool**
- 先做 **strongest-only / symbol pocket / maker-first**
- 再决定是否值得进入正式 replication

尤其 `BTC / ETH / DOGE / LTC / ADA` 这些 pocket，明显比 `SOL / XRP / AVAX` 更有希望。

### 7.2 5m：更适合当 child timing，不适合直接当主信号
`5m` 全池 gross 只有 `+0.94 bps/笔`，但 strongest `5m` router 在 `SOL / XRP / DOGE` 这几个币上，未来 `12` 根有一定延续回摆厚度。说明它在更快周期上：
- 可以当 **child execution timing**
- 可以做 **parent 15m pocket signal 的 finer entry**
- 但不太像能独立站住的 taker main alpha

## 8. 和最近 digest 的关系：为什么这轮没重复
虽然最近已经写过不少 mean reversion / oversold / BB / RSI 相关壳，但这条线和前几篇仍有明确差异：
- 它不是 `BB touch + RSI extreme` 的价格位置逻辑；
- 也不是 `high-volume selloff bounce` 那类 volume-shock 逻辑；
- 它更接近 **“过冲是否同时满足 3 个维度极端”** 的 composite scorer。

因此它补的是 **同属单资产 MR，但更偏 composite-exhaustion 打分器** 这一层，不是重复抄同一主题。

## 9. 下一步怎么测
1. **先做 symbol admission，不要全池同权。**  
   第一轮先锁 `BTC/ETH/DOGE/LTC/ADA`，把 `SOL/AVAX/XRP` 先排除，验证 pocket 是否稳定存在。

2. **把 strongest-only 改成真正的 router 回测。**  
   同一时刻只允许 1 个仓位，按 `abs(CRSI-50)` 或 `threshold distance` 排 strongest，测 `gross/net/trade overlap/capacity`，别再按“每个币都能做”理解。

3. **补 cheapest gate：trend-veto。**  
   在 `EMA50 slope` 很陡、或过去 `N` bar 单边效率很强时，均值回复会被顺趋势碾压。下一轮最便宜的增强，不是先加更多指标，而是先测：
   - 只在 `ADX` 低于阈值时启用
   - 或只在 `|ret_z|` 极端但 `path efficiency` 不高时启用

4. **把 5m 改成 child entry，不要独立开火。**  
   先由 `15m` 决定“是否值得做这次反打”，再让 `5m` 的 ConnorsRSI 极端作为 finer trigger，测试能否改善 entry bps。

5. **补 friction ladder 与 maker-first。**  
   当前 biggest problem 不是方向，而是厚度。下一轮至少测 `0 / 4 / 8 / 12 bps`，并单独看 maker-first fill 假设下还能剩多少。

## 10. 风险与提醒
- 这条壳当前还不是完整策略：没有正式 sizing、没有成熟 risk overlay、没有严肃 execution 建模。
- `ConnorsRSI` 这种逆势信号，在单边 trend day 很容易被连续碾压；如果不补 regime / trend veto，就会把“正常趋势延续”错当成“过冲结束”。
- 经典实践来源不是近 5 年论文，因此这轮的更强价值在 **repo 工程骨架 + crypto 行为支撑 + 我们自己的 portability probe**，而不是把它包装成“最新学术大发现”。

## 11. 一句话收尾
**ConnorsRSI 在 short-cycle crypto 上更值得被保留成“极端过冲 router”，而不是被误读成一个可以全池无脑抄底摸顶的老派摆设指标。**
