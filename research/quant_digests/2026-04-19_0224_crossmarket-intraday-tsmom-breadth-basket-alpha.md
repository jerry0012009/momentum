# 别把 Xu et al. (2023) 只读成“跨市场日内 TSMOM working paper”：对 short-cycle crypto desk，更该先拆的是「broad-breadth long-side intraday TSMOM basket」这条 raw alpha

- **主题类型：** raw alpha
- **基础 alpha：** 单个币过去 `30m~1h` 的短窗上涨，不是孤立噪音，而是**伴随多数 liquid majors 同向上行**时，后续 `1h~3h` 更容易继续顺势漂移；在当前 crypto perp portability 里，真正更像可交易 pocket 的是 **long-only breadth-confirmed continuation**，不是把 longs / shorts 对称地一起做。
- **是否可独立复现：** 是
- **是否可直接落地完整策略（entry/exit/sizing/risk/cost）：** 是

## 先回答一句：这篇东西的 base alpha 是什么？

**base alpha 不是“很多市场之间有某种联动”这种泛说法，而是：`own intraday return continuation, strengthened by cross-market agreement`。**

翻成人话就是：

> **如果一个币刚涨过，而且同一时刻大多数主流币也在一起涨，这种上涨更像“全市场正在一起走”，后面再走一段的概率会高于“只有它自己在乱跳”。**

所以这轮我没有把这篇 working paper 写成抽象的跨市场 predictability 口号，而是直接把它翻成 desk 可测的策略壳：

> **`过去 1h return z-score` + `market breadth >= 80% 同向` + `volume_z > 0` + `long-only equal-weight basket` + 固定 `3h` time-box exit**

---

## 这篇东西讲了什么，为什么值得 intake

**来源**
- **Authors：** dezhong Xu, Bin Li, Tarlok Singh, Jinze Li
- **Year：** 2023
- **Title：** *Cross-Market Intraday Time-Series Momentum*
- **Venue：** SSRN working paper
- **DOI：** <https://doi.org/10.2139/ssrn.4651331>
- **Readable URL：** <https://www.ssrn.com/abstract=4651331>
- **Metadata used this round：** Crossref + OpenAlex
- **Repo URL：** 本轮未拿到作者官方仓库

**我为什么选它**
1. 主题非常贴近我们当前主线：不是慢周期资产配置，而是直接点名 **intraday** + **time-series momentum** + **cross-market**；
2. 它给的是一个很自然的 desk 问题：**“短窗顺势到底该不该做，关键是不是要看别的币有没有一起动？”**
3. 最近几轮已经做过不少 `strongest-only` / `single-name` raw alpha，这篇正好补一个重要缺口：**不是只看自己，而是看自己是否被全市场一起抬着走。**

需要诚实说明的一点：

> **这轮没稳定拿到全文，只拿到了 DOI / SSRN landing page / Crossref / OpenAlex 元数据。**

所以学术证据层级我把它记成 **metadata-level paper seed**，真正让它进入研究池的，不是标题本身，而是后面这轮 public-data portability probe。

一句话核心结论：

> **对当前 liquid-major crypto perp，更值得保留的不是“short 端也一起做”的对称 intraday TSMOM，而是“多数主流币同涨时的 long-side continuation basket”。**

一句话证明方式：

> **本轮直接把论文标题里的 cross-market intraday TSMOM 翻成 Binance USDⓈ-M `5m/15m` 公开数据规则，并比较 all / router / long-only / short-only 几种读法的 forward bps。**

---

## 对我们 desk 最有价值的翻译

如果只按标题理解，你可能会写出一个很空的说法：
- “跨市场日内动量存在”
- “别的市场也涨时，自己更该追”

这还不够 desk-friendly。

更可执行的翻译其实是：

### 1. 先把“cross-market”落成 breadth，而不是玄学联动
本轮我用 10 个 liquid majors（`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`）直接定义：
- `ret_1h`：过去 `4` 根 `15m` 收益；`ret_30m`：过去 `6` 根 `5m` 收益；
- `z`：各币自己的 rolling return z-score；
- `breadth`：同一时点 10 个币里有多少比例是同方向上涨/下跌；
- `breadth >= 0.8`：等于说**至少 80% 的 major 在一起往同一个方向走**；
- `volume_z > 0`：排除明显没量的假动作。

### 2. 当前更值钱的是 long basket，不是 strongest-only router
这条线和前几篇 digest 有个很关键的不同：

> **它不是“只挑当下最强那一个”更好，而是“当 market breadth 很整齐时，干脆把所有满足条件的 long 信号一起做成一个小篮子”更像完整策略。**

也就是说，这轮真正可保留的不是 `top1 router`，而是 **equal-weight breadth basket**。

---

## 本轮 portability probe：最值得记的 4 个数

### Probe 口径
- **市场：** Binance USDⓈ-M perpetual
- **样本币：** `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`
- **样本长度：**
  - `15m`：近约 `60d`（`6000` bars）
  - `5m`：近约 `22.5d`（`6500` bars）
- **统一规则：** `z >= 1.5`、`breadth >= 0.8`、`volume_z > 0`
- **artifact：**
  - `reports/artifacts/quant_digests/2026-04-19_crossmkt_intraday_tsmom_15m_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_crossmkt_intraday_tsmom_5m_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_crossmkt_intraday_tsmom_basket_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_crossmkt_intraday_tsmom_portfolio.json`

### 结果 1：`15m` 的 **all-signals 对称做法** 不差，但真正抬升来自 long 端
在 `15m` 上，把满足条件的所有信号都顺着做：
- next `12` bars（约 `3h`）**all-signals**：`n=6093`，mean ≈ **`+14.81bps gross`**，median ≈ **`+3.73bps`**，win ≈ **`51.39%`**。

但拆开以后会发现：
- **long-only**：`n=3220`，next `12` bars mean ≈ **`+21.42bps gross`**；
- **short-only**：`n=2873`，next `12` bars signed mean 只有 **`+7.40bps`**，而且更不稳定。

这说明在当前样本里，**多头 continuation 明显比空头更厚。**

### 结果 2：最像完整策略的是 `15m` long-only breadth basket，而不是 top1 router
把同一时点所有满足条件的 long 信号等权做成 basket：
- **事件数：** `3220`
- **独立决策时点：** `760`
- **平均每次持仓币数：** `4.24`
- **next `12` bars（约 `3h`）basket mean：** **`+17.51bps gross`**
- **basket median：** **`+1.30bps`**
- **basket win rate：** **`50.79%`**

如果先粗扣 `8bps` round-trip taker cost，仍大约还有 **`+9.5bps / basket`** 的空间。

### 结果 3：`strongest-only router` 反而被削弱
同样是 `15m`、同样条件，只留每个时点分数最高的 1 个币：
- next `12` bars 只有 **`+8.23bps gross`**；
- median 约 **`0bps`**；
- win 约 **`49.57%`**。

也就是说，这条线跟“极端冲击只做最强一档”的 pocket 不一样：

> **cross-market breadth 这个信息，当前更像“该一起做一篮子”，不是“只挑最猛那个”。**

### 结果 4：`5m` 也有 long 端漂移，但厚度明显不如 `15m`
`5m` long-only breadth basket：
- `n=3688`，独立时点 `897`；
- next `6` / `12` / `18` bars（约 `30m/1h/1.5h`）basket mean 约 **`+5.91 / +5.40 / +5.84bps gross`**。

这还没死，但明显比 `15m -> 3h` 的 pocket 薄得多；粗扣成本后已经很接近生死线。

所以这条线当前更像：

> **`15m` 母级别 raw alpha，必要时再下沉到 `5m` 做 child execution，而不是直接把 `5m` 裸信号当主策略。**

---

## 3.5 策略拆解（必填）

- **方向属性：** 顺势 / 多标的同向篮子
- **基础 alpha：** `cross-market-confirmed intraday continuation`
- **regime：** broad market breadth 明显同向（当前 portability 里用 `breadth >= 0.8` 代理）
- **filter / veto：** `return_z >= 1.5` + `volume_z > 0`；当前证据不支持默认做对称 short 端
- **risk / sizing / execution overlay：** 同一时点所有满足条件的 long 信号等权；固定 `12 x 15m` time-box exit；先按 `8bps` round-trip taker 成本做粗生死线

---

## 它为什么比继续补某个纯 filter 更值得

因为这轮补的是一个**可以直接单独落地**的 raw alpha，不只是“给已有策略加一层门”。

它回答的是：

> **当 market 已经进入短窗 risk-on、而且不是某一只币独涨时，到底该不该顺着做一篮子 continuation？**

当前答案是：
- **是，但更像做 long-only basket；**
- **不是 strongest-only；**
- **也不是默认 longs / shorts 对称开。**

这对素材池的价值，明显高于再补一篇“某个 gate 可能有帮助”的说明文。

---

## 最小可复刻实验

### 最小策略壳
在 10 个 liquid majors 的 `15m` 面板上，每根 bar 做：
1. 计算过去 `4` 根 `15m` 收益 `ret_1h`；
2. 对每个币计算 rolling `96` 根的 `z(ret_1h)`；
3. 计算市场 breadth：10 个币里上涨比例减去下跌比例；
4. 若某币满足：
   - `ret_1h > 0`
   - `z(ret_1h) >= 1.5`
   - `breadth >= 0.8`
   - `volume_z > 0`
   就把它加入当期 long basket；
5. 当期 basket 等权开仓；
6. 固定持有 `12` 根 `15m`（约 `3h`）后退出；
7. 先用 `8bps` round-trip cost 粗算，再决定要不要继续做 child execution。

### 先看哪两个指标
1. **basket-level gross / net bps**：别只看单币 event mean；
2. **overlap-aware exposure**：同一时点常常有 `4` 个以上币一起触发，必须看 gross cap 后还剩多少。

### 紧接着该测什么
1. **BTC 作为 market proxy 的简化版**：只用 `BTC/ETH` breadth 能否保留大部分 edge；
2. **去掉 short 端后的 long-only horse race**：对比 `own-return only` vs `breadth-only` vs `own-return + breadth`，确认超额到底来自哪一块；
3. **`15m` 母信号 + `5m` child execution**：试 `5m` pullback 入场，看能否把 `gross 17.5bps` 多留一点到 net；
4. **overlap cap / cluster cap**：限制同链 / 高相关币同时持仓，确认收益不是被 beta 暴露假撑起来。

---

## 风险与保留意见

1. **论文证据本轮偏弱。**
   这次没拿到全文，只能把 paper 当题目种子，而不是“已完整读懂并严格复刻”的强证据来源。

2. **当前 edge 很可能带着市场 beta。**
   breadth 很强时，本质上接近短窗 risk-on；如果不做 beta 调整，收益里会混进 market drift。

3. **持仓会扎堆。**
   `15m` 版本平均一轮约 `4.24` 个币，`p90` 甚至能到 `10` 个全开；真实落地必须加 gross / sector / correlation cap。

4. **short 端当前不够漂亮。**
   这条线不能被想当然写成 long-short 对称模型；至少在最近样本里，short 端明显更脆。

5. **`5m` 直接硬做偏薄。**
   所以别把这条线误读成“越快越好”的 HFT alpha；当前更像 `15m` raw alpha + `5m` 执行优化题。

---

## 我对这条线的当前判断

这轮我会把它放进：

> **可独立复现、且可以直接落地成完整策略壳的 raw alpha 候选。**

但保留方式不是“cross-market TSMOM 全都做”，而是更具体的：

> **`15m` long-only breadth-confirmed continuation basket**。

这条线最值钱的地方，不是又给了一句“动量有效”的废话，而是把一个本来很容易写空的论文标题，翻成了：
- 什么时候做（breadth 很整齐）
- 做哪边（先做 long-only）
- 做几个（不是 top1，而是一篮子）
- 做多久（先看 `3h`）
- 成本后还剩多少（粗看仍活着）

这就已经够进入下一轮 first-verdict / overlap / execution honesty check 了。

---

## 来源

- Xu, D., Li, B., Singh, T., & Li, J. (2023). *Cross-Market Intraday Time-Series Momentum*. SSRN working paper.
- DOI: <https://doi.org/10.2139/ssrn.4651331>
- Readable URL: <https://www.ssrn.com/abstract=4651331>
- Crossref metadata: <https://api.crossref.org/works/10.2139/ssrn.4651331>
- OpenAlex metadata: <https://api.openalex.org/works?filter=doi:10.2139/ssrn.4651331>
