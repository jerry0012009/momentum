# 别把 `sspoisk/-Loud-DIVER_1.1` 只读成“CVD 扫描器”：对 short-cycle crypto desk，更该先测的是「price extreme × non-confirming CVD」这条 raw alpha 壳，但当前更像 `30m context -> 15m/5m child execution`，不是裸 `15m` 主信号

- 时间：2026-04-18 07:15 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `cvd_strategy.py` + `scanner_worker.py` + `config.json`）+ Binance USDⓈ-M `30m/15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**价格刚创出一段局部新低/新高，但 taker 主导的 CVD 没再同步恶化/扩张，说明最后一脚更像衰竭而不是趋势确认；做短持有 fade / snapback**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 已给出 `entry + ATR stop + ATR take-profit + strength/rvol/liquidity gate`；但对我们 desk 更诚实的落地方式是 `30m 扫描 + 15m/5m 子执行`）
- 主题标签：raw-alpha / single-asset / mean-reversion / exhaustion-fade / cvd / taker-delta / volume-imbalance / atr-stop / atr-tp / binance-perpetual / 30m / 15m / 5m / repo / public-data / cost / risk
- 证据类型：repo 源码规则 + public-data portability probe

先回答一句：**这篇东西的 base alpha 是什么？**
不是“量能过滤器”，也不是“trend overlay”。它的 base alpha 很直接：

> **价格已经把局部极值推出来了，但 CVD 没再跟着确认，最后一脚更像 exhaustion，后面先收一段短窗回摆。**

所以这轮我把它归成 **raw alpha / 单资产短持有 mean reversion**，而不是 filter。

---

## 1. 这次看了什么
主来源是 GitHub 仓：
- **Author / Repo owner：** `sspoisk`
- **Year：** 2026（repo 最近更新见本地 clone metadata）
- **Title：** *SpreadMaker v10.15 — CVD Divergence Hunter & Trailing Grid*
- **Venue：** GitHub repository
- **Readable URL：** <https://github.com/sspoisk/-Loud-DIVER_1.1>
- **Repo URL：** <https://github.com/sspoisk/-Loud-DIVER_1.1>
- **Raw README：** <https://raw.githubusercontent.com/sspoisk/-Loud-DIVER_1.1/main/README.md>
- **Raw strategy：** <https://raw.githubusercontent.com/sspoisk/-Loud-DIVER_1.1/main/cvd_strategy.py>
- **Raw scanner：** <https://raw.githubusercontent.com/sspoisk/-Loud-DIVER_1.1/main/scanner_worker.py>
- **Raw config：** <https://raw.githubusercontent.com/sspoisk/-Loud-DIVER_1.1/main/config.json>

repo 不是学术论文，工程质量也偏“个人交易终端”而不是干净研究库，但它有一个优点：**规则写得够直白，能快速转成最小实验。**

我额外做了一个 Binance public-data probe，直接用 `klines` 里的：
- `close`
- `volume`
- `taker_buy_base`

重建 repo 里的 CVD 近似口径，再按它的“两段窗口找 bullish / bearish divergence”做 first verdict。

相关 artifact：
- `reports/artifacts/quant_digests/2026-04-18_cvd-divergence_30m_events.csv`
- `reports/artifacts/quant_digests/2026-04-18_cvd-divergence_30m_summary.csv`
- `reports/artifacts/quant_digests/2026-04-18_cvd-divergence_15m_events.csv`
- `reports/artifacts/quant_digests/2026-04-18_cvd-divergence_15m_summary.csv`
- `reports/artifacts/quant_digests/2026-04-18_cvd-divergence_portfolio.json`

---

## 2. 一句话核心结论
**这条 alpha 不是完全不能做，但当前明显不是“压到 15m 就能直接开跑”的裸短周期主信号；更像 `30m` 上只做强信号，再交给 `15m/5m` 去挑更好的 child entry。**

**一句话证明方式：** repo 把 divergence 规则、ATR 风控和扫描阈值写成了可计算条件；我再用 Binance `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK` 近 `90d` 公共数据重做同口径 probe，结果看到：**`30m` 强信号还有 gross edge，但 `15m` 压缩版整体转负。**

---

## 3. repo 里最值得保留的，不是 UI，而是这层 raw alpha 骨架
`cvd_strategy.py` 的核心不是“扫描器”，而是这组很清楚的条件：
- 在最近窗口里，价格创更低低点 / 更高高点；
- 但 CVD 对应位置没有同步创更差极值；
- 两个极值之间要拉开最小 bar distance，避免贴得太近；
- 再加 `strength`、`RR`、`ATR stop/tp` 做完整壳。

翻成人话：
- **创新低但卖盘没更凶** → 先别继续追空，偏向做反抽；
- **创新高但买盘没更猛** → 先别继续追多，偏向做回落。

这和“看 RSI 超买超卖”不一样。这里盯的是：**最后一脚价格推进，是否真的还得到 taker flow 确认。**

---

## 3.5 策略拆解（必填）
- 方向属性：**逆势 / 单资产 mean reversion / exhaustion fade**
- 基础 alpha：**price extreme × non-confirming CVD divergence**
- regime：优先高流动、非超低波动、且最近一脚价格推进已足够明显的窗口
- filter / veto：`strength`、`min_price_change_pct`、`min_cvd_change_pct`、`RR >= threshold`、必要时再加 RVOL / liquidity
- risk / sizing / execution overlay：ATR 止损、ATR 止盈、只做强信号分位、`30m` 扫描后用 `15m/5m` 找 child entry，最后再走 friction ladder

---

## 4. portability probe：当前真正值得记住的 3 个数据点
样本：Binance USDⓈ-M，`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`，近约 `90d`。

### 4.1 `30m` 全样本不是很强，但开始有“慢一点的回摆”味道
`30m` 全部信号共 `6879` 笔：
- next `4 bar`（约 `2h`）gross **`+2.49 bps`**，win rate **`52.22%`**
- next `8 bar`（约 `4h`）gross **`+3.15 bps`**，win rate **`52.93%`**

单看这个，还不够过 taker 成本线，但已经说明：
**这条线更像慢一点的 snapback，不是下一根就立刻反。**

### 4.2 真正有意思的是 `30m` 强信号分位
把 `strength` 提到样本内 `q75` 后，`1721` 笔强信号变明显：
- next `4 bar` gross **`+15.91 bps`**，按 `8 bps` round-trip 粗扣后 net **`+7.91 bps`**
- next `8 bar` gross **`+24.48 bps`**，net **`+16.48 bps`**
- `4 bar` win rate **`56.71%`**，`8 bar` win rate **`58.69%`**

这说明：
> **不是“有 divergence 就做”，而是“只做够强的 divergence”，这条壳才开始接近可交易。**

### 4.3 一旦硬压到 `15m`，这条 edge 当前明显坏掉
`15m` 全样本 `12526` 笔：
- next `4 bar` gross **`-3.34 bps`**
- 强信号 `q75` 反而更差，next `4 bar` gross **`-6.33 bps`**
- next `8 bar` 也仍是负的：gross **`-12.53 bps`**

这轮最重要的 desk 结论就是：
**别把 repo 的 divergence scanner 直接压成“15m 裸主信号”。当前更合理的是保留它的 `30m` context，然后把实际执行下沉到 `15m/5m`。**

---

## 5. 为什么这和当前 desk 仍然有关
当前我们不是缺“又一个模糊 filter”，而是缺：
- 能独立定义的 raw alpha；
- 以及能说清楚“该放在哪一层”的完整策略零件。

这条线的价值就在于：
1. **base alpha 能答清楚**：是 exhaustion fade，不是假装成 filter；
2. **规则够可编程**：双窗口极值 + CVD 非确认 + ATR 风控；
3. **first verdict 不含糊**：`30m` 强信号可留，`15m` 压缩版先别碰；
4. **很适合拆成完整策略壳**：scan → score → child entry → ATR risk → friction ladder。

所以它值得进研究池，但不是因为“repo 很炫”，而是因为：
**它给了我们一条已经做出 first verdict 的 mean-reversion raw alpha 壳。**

---

## 6. 可复刻的最小实验
### 研究假设
在 liquid majors 上，**`30m` 级别价格极值若未被 CVD 确认，后续 `2h~4h` 更容易先回摆；但这条 edge 需要 strength gate，且不应直接压成裸 `15m`。**

### 一个可计算定义
先按 repo 原型：
- bullish：最近窗口价格新低、但 CVD 比上一个低点更高；
- bearish：最近窗口价格新高、但 CVD 比上一个高点更低；
- `strength >= q75` 才允许交易。

### 最小回测切口
- 标的：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`
- 扫描周期：`30m`
- 子执行：`15m` 或 `5m`
- 样本：最近 `90d`
- 入场：`30m` divergence 触发后，不立刻追价；等下一根 `15m` 出现 first reversal close / micro pullback fill
- 出场：`ATR(14)` 止损 + `2~4 bar` time stop + repo 原始 RR 约束并行比较

### 最先看哪 2 个指标
1. **friction ladder 后的 net bps / trade**（`0 / 4 / 8 / 12 bps`）
2. **强信号 bucket 的 positive-window ratio / hit rate**，别只看全样本均值

---

## 7. 风险与保留意见
- 这类 divergence 很容易被误写成“看图说话”；一定要锁死窗口、极值定义和 signal timestamp。
- `klines` 重建的 CVD 只是 taker-buy vs sell 的 bar 级近似，不等于逐笔订单流；真实 edge 可能更依赖更细颗粒数据。
- 当前 probe 明确说明：**15m 压缩版失效**。如果后续 child execution 也救不回来，就该把它降级成 `PARKED`，不要硬拗。
- repo 自带 GUI / grid / paper/live 终端噪音很重，真正值得抄的只有 divergence logic + ATR shell，不要把整套终端当 alpha 本体。

---

## 8. 下一步怎么测
下一轮别再做“大而全重写”，直接做这 3 件事：
1. **固定 `30m strength q75`**，把 `15m/5m` child entry 做成 2 个版本：`close-confirm` vs `pullback-limit`；
2. **加入一层最小去重**：同币同向信号在 `8 bar` 内不重复开仓，避免信号簇把均值吹高；
3. **跑 friction ladder + maker/taker 双口径**，确认这条线到底是 `taker 可做`，还是只能当 `maker-first fade pocket`。

如果这三步里，`30m strong divergence` 经过 child entry 后还能留住正 net，那么它就值得从研究池进入下一轮 admission check；反之就该诚实地标记为“**有 raw alpha 形状，但当前只够做概念母体，不够直接上线**”。
