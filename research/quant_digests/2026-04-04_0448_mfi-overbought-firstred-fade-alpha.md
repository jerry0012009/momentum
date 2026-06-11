# 别把这份 2026 Binance Futures MFI bot repo 只读成指标脚本：对 short-cycle desk，更该先测的是「6H overbought exhaustion × 15m delayed confirm × fast time-box」这条完整 raw alpha
- 时间：2026-04-04 04:48 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `mfi_live_trader_8083.py` + `htf_mfi_paper_trader.py` + `liq_zone_trader_8089.py` + `CHANGELOG.md`）+ Binance Futures 公共 `6h` 最小便携性快检
- 主题类型：raw alpha
- 基础 alpha：**高位资金流/成交量驱动的过热推进，在连续 3 根 6H 顺势阳线后，常在“第一根转红”阶段出现短促均值回归**；repo 真正能给我们 desk 直接复现的，不是 `MFI` 这个指标名词本身，而是「**6H overbought exhaustion fade**」这条 raw alpha，再叠 `15m delayed confirm / cooldown / HTF alignment` 这些过滤与执行层
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / mean-reversion / single-asset / exhaustion-fade / mfi / volume-flow / first-red / delayed-confirm / cooldown / session-filter / binance-futures / top-liquid-universe / 15m / 5m / 3m / 1m / 6h-anchor / repo / public-data / cost / risk
- 证据类型：repo（策略脚本 + 参数演化日志）+ 公共行情最小快检

**先回答 base alpha：这篇东西的 base alpha 是清楚的——不是“因为 MFI 很神”，而是“高位连续推进之后，第一根转弱 bar 往往先给出一段短促回吐”。所以它配当本轮主 digest。`MFI / 1D confluence / 24H cooldown / bull-bear regime switch` 都是围绕这条 raw alpha 服务的 filter、确认或仓控层。**

## 1. 这次看了什么
这轮主看的是一个 2026 年的 GitHub repo：

1. **Pavan Raheja (2026), _crypto-trading-bots_**  
   - Venue：GitHub repository  
   - Author：`pavanraheja`（GitHub owner）  
   - Repo URL：<https://github.com/pavanraheja/crypto-trading-bots>  
   - README：<https://github.com/pavanraheja/crypto-trading-bots/blob/main/README.md>  
   - 本轮重点读的文件：
     - `mfi_live_trader_8083.py`
     - `htf_mfi_paper_trader.py`
     - `liq_zone_trader_8089.py`
     - `CHANGELOG.md`

2. 这份 repo 不是单一脚本，而是一个围绕 **MFI exhaustion / reversal** 演化出来的小策略簇：
   - `8083`：**6H overbought → 3 green → first red → SHORT** 的 live trader；
   - `8085`：更偏 **direction-filter + 1M MFI pullback entry** 的高周期对齐版；
   - `8089`：把 **BTC 6H MFI reversal** 当主触发，再映射到 alt basket 的 zone follower。

3. 这轮真正值得 intake 的，不是“把所有脚本都抄下来”，而是把 repo 反翻译成 desk 可用的那条主线：
   - **raw alpha**：过热推进后的 first-red exhaustion fade；
   - **execution / filter**：15 分钟延迟确认、MFI decay guard、daily confluence、loser cooldown、session 限制；
   - **扩展空间**：可继续拆成 regime-specific universe、side-specific symbol selection、fast time-box exit。

## 2. 这条 raw alpha 的人话版：不是“指标神奇”，而是“高位连续推进后的第一脚松动”
如果只看 repo 名字，你很容易把它误读成：

> “又一个拿 MFI > 80 / < 20 乱触发的 retail bot。”

但把代码顺下来后，真正的交易假设其实更具体：

1. 市场先出现 **持续的高位推进**；
2. 这个推进不是单根 spike，而是 **至少 3 根 6H 连续顺势 bar**；
3. 然后当前 6H bar 开始 **由强转弱**（第一根转红）；
4. 在转弱的早段而不是后半段进场，吃的是 **短促回吐 / 均值回归**，不是长持看大崩。

所以它本质上更像：

> **impulse exhaustion → early fade**

这很适合当前 desk，因为它不是纯解释型主题，而是可以直接落成 `entry / expiry / stop / cooldown / session / symbol ranking` 的完整单币 raw alpha 壳。

## 3. 代码里最值钱的那条完整策略壳
### 3.1 Universe 不是单币拍脑袋，而是全市场扫描
`README.md` 和 `mfi_live_trader_8083.py` 给的 baseline 很清楚：
- Venue：**Binance USDⓈ-M Futures**
- Universe：约 **211 个** Binance futures pairs
- 流动性门槛：`MIN_VOLUME_USDT = 5_000_000`
- 扫描周期：每 `30` 分钟做一次 overbought / oversold scan
- 最大并发：`MAX_CONCURRENT = 6`

翻成人话：
- 这不是“BTC 专用故事”，而是一个 **全宇宙找过热币，再等 first-red** 的横截面 single-asset mean-reversion 壳；
- 但 repo 后面的演化也说明：**广谱 universes 不等于广谱有效**，后面还得做 symbol admission。

### 3.2 真正的 raw signal：6H overbought + 三连阳 + 第一根转红
`mfi_live_trader_8083.py` 的核心信号定义非常明确：

- `MFI_OB = 80`
- `MIN_GREENS = 3`
- 先在最近 3 根已完成 `6H` bar 里找 `MFI > 80` 的 overbought；
- 再要求最近 3 根已完成 `6H` bar 全部为 green；
- 当前 live `6H` bar 转成 red 时 arm signal；
- 等待 `ENTRY_CONFIRM_MIN = 15` 分钟后检查是否入场；
- 超过 `ENTRY_EXPIRE_MIN = 180` 分钟则 signal 失效。

这是这篇 digest 最该记住的一句：

> **repo 不是在做“见 overbought 就空”，而是在做“连续推进后的第一根转弱 bar 的早段 fade”。**

### 3.3 不是立刻冲进去，而是做 delayed confirm
repo 很聪明的一点，是它没有在 first-red 一出现就硬开仓，而是加了一段 **延迟确认窗口**：

- armed 之后先等 `15` 分钟；
- 但必须在 `3` 小时内完成入场，否则不追；
- live MFI 不能太低（`MFI_MIN_ENTRY = 75`），否则说明信号已经衰减过头；
- live MFI 也不能太高（`MFI_MAX_ENTRY = 85`），否则说明热度还没松；
- 若从 signal 到 entry 的 MFI 衰减超过 `8` 点，则取消；
- `recently_ob` 的边缘信号，要求 entry MFI 至少 `77`。

这套 delayed confirm 其实非常 desk-friendly，因为它直接回答了 short-cycle 最痛的一个问题：

> **不是“有没有反转”，而是“你会不会在最烂的位置才进去”。**

### 3.4 风控壳不是花哨，而是相当完整
`8083` 里的 execution / risk shell 已经很完整：
- `ATR_SL_MULT = 1.5`，并对 stop distance 加 `8%` 硬上限；
- 初始 take profit 先按 `2:1 RR` 定义；
- 中途 `50%` partial close at `1:1 RR`；
- 剩余头寸用 ATR trailing 管理；
- 亏损后同币 `24H cooldown`；
- session 有明确时间限制；
- 并发头寸上限固定。

所以它不是“只有 entry，没有完整交易壳”的半成品，而是一个可直接映射到我们 `1m / 3m / 5m / 15m` 研究栈里的完整 raw-alpha candidate。

## 4. repo 自己的演化日志，反而暴露了这条 alpha 真正在哪里
`CHANGELOG.md` 很有价值，因为它不是只说“我觉得有效”，而是把策略迭代写成了数据驱动日志。几个最重要的数据点：

1. **entry MFI 区间明显不对称**  
   2026-04-01 的记录写得很直白：
   - `80–85` 区间胜率约 **67%**；
   - `85–90` 区间胜率约 **22%**；
   - `90–95` / `95–99+` 更差，接近 **0–25%**。  
   这说明：**太热的时候别急着 fade，edge 反而更差。**

2. **24H loser cooldown 是从实战亏损里逼出来的**  
   changelog 里提到同一币种无 cooldown 重复进场，曾把单币亏损从 `-1.08%` 扩成 `-9.16%`。  
   这类 raw alpha 最大的风险之一就是：**第一脚没结束时，你会不断把“继续趋势”误判成“第二次反转”。**

3. **SL 不是越紧越好**  
   `8085` 的 paired-signal A/B 里，`SL-1.5%` 比 `SL-1.0%` 更优：
   - `SL-1.5%`：净值 `+6.6%`，WR `80%`，PF `6.40`
   - `SL-1.0%`：净值 `+4.0%`，WR `60%`，PF `2.20`  
   说明这类 fade 不是纯 knife-catch，而是经常先被 wick 再回落；**stop 太紧，反而会被洗掉。**

这三个点拼起来，给 desk 的启发非常明确：
- alpha 本体成立的位置，是 **“刚开始松动，但没完全衰竭”**；
- 一旦太极端、太后手、太重复，edge 会迅速崩；
- 所以真正可迁移的东西不是 MFI 数值，而是 **delayed confirm + anti-chasing + anti-reentry** 这套壳。

## 5. 我们自己做的最小便携性快检：这条 edge 更像“快回吐”，不像“长持空单”
为了避免只照单全收 repo 自报成绩，我额外用 **Binance Futures 公共 6H K 线** 做了一个最小快检（artifact 已落盘）：

- 数据源：Binance USDⓈ-M Futures 公共 `klines`
- 标的：`BTC / ETH / SOL / XRP / DOGE / ADA / DOT / AVAX / BNB / LINK`
- 时间：`2024-01-01` 到 `2026-04-04`
- 代理信号：
  - 最近 3 根 `6H` 已完成 bar 连续 green；
  - 当前 bar red；
  - 前 3 根 bar 的 `MFI peak > 80`；
- 这是 **closed-bar proxy**，不是 repo 的原样 intrabar 15m 执行，所以只能当 portability sanity check，不当正式复刻结果。

### 5.1 全样本：6–12 小时有一点回吐，但 24 小时明显失真
在 `10` 个主流 perp 上共抓到 `233` 个 proxy signals：

- 下一个 `6H` 平均收益：`-6.35 bps`（做空视角是正）
- 下两个 `6H`（约 `12H`）平均收益：`-11.12 bps`
- 下四个 `6H`（约 `24H`）平均收益：`+120.45 bps`

翻成人话：

> **这条 edge 更像“先回吐一小段”，不是“抱着空单等大波段”。**

也就是说，如果你把它误做成 swing short，很可能把短促 alpha 持成趋势反向暴露。

### 5.2 edge 主要集中在少数币，不适合无脑全市场平权
在这组 proxy 里，最像样的名字其实集中在少数 alt：

- `ADA`：`26` 个信号，后 `12H` 平均 `-140.00 bps`，负收益占比 `69.2%`
- `SOL`：`22` 个信号，后 `12H` 平均 `-105.47 bps`，负收益占比 `63.6%`
- `BTC`：`30` 个信号，后 `12H` 平均 `-21.48 bps`

但也有明显失败样本：
- `ETH`：后 `12H` 平均 `+57.85 bps`
- `DOGE`：后 `24H` 平均 `+452.37 bps`

所以更合理的 desk 读法不是“这是全宇宙通杀 MFI 空头系统”，而是：

> **这是一条需要 symbol ranking / universe admission 的 raw alpha。**

### 5.3 极端过热（90+）反而最不该硬 fade
我额外把 `MFI peak` 做了粗分桶：

- `80–85`：`109` 个信号，后 `12H` 平均 `-2.88 bps`
- `85–90`：`67` 个信号，后 `12H` 平均 `-58.51 bps`
- `90+`：`53` 个信号，后 `12H` 平均 `+32.50 bps`，后 `24H` 平均 `+338.82 bps`

这和 repo changelog 的经验是同向的：
- **太热的时候不是更好空，而是更容易继续被顶着走。**

只是要注意：
- repo 用的是 **entry 时 live MFI**；
- 我这边做的是 **closed-bar peak MFI proxy**；
- 所以不能拿数值一一对应，但大方向是一致的。

## 6. 这条策略最适合当前 desk 的地方：它直接补的是“single-asset exhaustion fade”素材池
这轮为什么值得写，而不是继续围着旧 breakout / retest 打转？因为它补的是当前很缺的一条独立 raw alpha：

- 家族：`single-asset mean reversion / exhaustion fade`
- 不是 pairs、不是 maker、不是 prediction market cross-map
- 而且天然能接入 `1m / 3m / 5m / 15m` execution 层

更重要的是，它把策略拆成了很适合 desk 迭代的模块：
- **base alpha**：6H first-red exhaustion fade
- **signal timing**：15m delayed confirm
- **anti-chase**：MFI decay guard / max-entry cap
- **risk**：ATR stop / partial / trail
- **portfolio hygiene**：24H loser cooldown / max concurrent
- **regime extension**：side-specific universe（`8085` 的 `BULL_MODE / BEAR_MODE`）

这意味着它不是“只能拿来做一篇说明文”的主题，而是能继续分解成多轮实证：
- 哪些币有效？
- 哪个 time-box 最好？
- cooldown 值不值？
- delayed confirm 究竟减少了多少坏 trade？

## 7. desk 版不该照抄 repo，而该这样翻译
### 7.1 我会怎么落成 short-cycle 版 baseline
如果把它翻译成更贴近我们 desk 的首轮 baseline，我会建议：

- **Universe**：先做 `8~12` 个最液态 perp，不要一上来全市场扫
- **Anchor timeframe**：`6H`
- **Execution timeframe**：`15m`（必要时下钻 `5m`）
- **Signal**：
  - 最近 3 根已完成 `6H` 为 green
  - 最近 3 根 `6H` 内出现 `MFI peak > 80`
  - 当前 `6H` bar 开始转红
- **Entry**：
  - 信号出现后延迟 `15m`
  - 只在前 `15~180m` 内允许进场
  - 若 `15m` 已出现明显 V 型收回或 intrabar MFI 衰减过头，则取消
- **Exit**：
  - baseline 先用 `1.25~1.75 × 6H ATR` stop
  - 先平 `50%` 在 `1R`
  - 剩余部分二选一：`12H time-box` 或轻 trailing
- **Portfolio rules**：
  - loser cooldown
  - same-coin no reentry
  - max concurrent cap

### 7.2 当前最值得 desk 主动改的，不是 entry，而是 exit time-box
repo 原始 live 版本更偏 RR + trailing，但我这轮最小快检给了一个很清楚的提醒：

> **如果 alpha 主要集中在 6–12 小时的快回吐，那 exit 设计比 entry 微调更重要。**

所以对 desk，最值得优先测的不是再把 `MFI_MIN_ENTRY 75/76/77` 无限打磨，而是：

1. `6H flat`
2. `12H flat`
3. `1R partial + 12H hard stop`
4. `repo-style trail`

谁最能保住短促回吐，谁才是这条 alpha 真正的 executable shell。

## 8. 下一步怎么测
### 第一步：先做一版“近源码”的 15m 执行复刻
最小实验建议：
- 标的：`BTC / SOL / ADA / DOT / SUI / BNB / LINK / AVAX`
- 数据：Binance Futures 公共 `15m + 6H`
- 核心：
  - `6H` 负责产生 overbought-first-red signal
  - `15m` 负责 delayed confirm 和实际入场
- 先只测 SHORT 版，不要急着做 long symmetry

目标：回答 **repo 的 delayed confirm 壳，放到我们自己的数据栈里后还剩多少 edge**。

### 第二步：专门做 exit shell A/B
固定 entry，不动 signal，只比较：
- `12H flat`
- `1R partial + 12H flat`
- `repo trail`
- `24H hold`

如果 `24H hold` 明显最差，那就说明这条 alpha 的正确读法确实是 **fast time-box mean reversion**，而不是 swing fade。

### 第三步：做 symbol ranking，而不是默认平权
按近 `90d / 180d` 条件 edge 给币排序：
- signal count
- 后 `6H / 12H` 平均回吐
- adverse excursion
- cooldown 后 reentry loss clustering

若排名稳定，再决定是否：
- 固定白名单；
- 或改成 rolling top-N symbol admission。

## 9. 资料与数据源
### 9.1 Repo / code sources
1. **Pavan Raheja (2026), _crypto-trading-bots_. GitHub repository.**  
   - Repo URL：<https://github.com/pavanraheja/crypto-trading-bots>
2. **README.md**  
   - Readable URL：<https://github.com/pavanraheja/crypto-trading-bots/blob/main/README.md>
3. **`mfi_live_trader_8083.py`**  
   - Raw URL：<https://raw.githubusercontent.com/pavanraheja/crypto-trading-bots/main/mfi_live_trader_8083.py>
4. **`htf_mfi_paper_trader.py`**  
   - Raw URL：<https://raw.githubusercontent.com/pavanraheja/crypto-trading-bots/main/htf_mfi_paper_trader.py>
5. **`liq_zone_trader_8089.py`**  
   - Raw URL：<https://raw.githubusercontent.com/pavanraheja/crypto-trading-bots/main/liq_zone_trader_8089.py>
6. **`CHANGELOG.md`**  
   - Raw URL：<https://raw.githubusercontent.com/pavanraheja/crypto-trading-bots/main/CHANGELOG.md>

### 9.2 公开数据口径
- 数据源：**Binance USDⓈ-M Futures 公共 klines API**
- 公开性：公开可得，无需私有 key 即可复核基础 K 线
- 更新频率：按交易所 bar 频率实时滚动（本轮最小实验用 `6H`，下一步建议加 `15m` 执行层）
- 本轮快检 artifact：
  - `reports/artifacts/quant_digests/mfi_overbought_exhaustion_20260404/symbol_summary.csv`
  - `reports/artifacts/quant_digests/mfi_overbought_exhaustion_20260404/mfi_peak_buckets.csv`
  - `reports/artifacts/quant_digests/mfi_overbought_exhaustion_20260404/signal_sample.csv`

## 10. 一句话结论
这份 repo 值得 intake 的地方，不是“又一个 MFI bot”，而是它把 **6H overbought exhaustion fade** 这条 single-asset raw alpha，包成了一个已经有 **delayed confirm / anti-chase / cooldown / ATR risk shell** 的完整候选；而我这轮最小快检进一步提示：**这条 edge 更像 6–12 小时的快回吐，不像 24 小时以上的长持空单。**