# 别把这份 2026 stat-arb repo 只读成“日频 market-neutral 框架”：对 short-cycle crypto desk，更该先拆的是「cointegration-first pair admission × strongest residual z-score spread fade」这条 raw alpha

- **主题类型：** raw alpha
- **基础 alpha：** 两个高相关、关系相对稳定的币种，若价差（更准确说是 `log(A) - beta*log(B)` 残差）短时间偏得过远，后面几个 `15m` bar 往往会向均值回归；交易上对应 **多便宜腿、空偏贵腿** 的 spread fade。
- **是否可独立复现：** 是
- **是否可直接落地完整策略（entry/exit/sizing/risk/cost）：** 是

## 先回答一句：这篇东西的 base alpha 是什么？

**base alpha 很清楚：`cointegration / residual spread mean reversion`。**

不是“market neutral 很好听”，也不是“相关性高就能做 pairs”，而是：

> **先筛出关系相对稳的 pair，再在残差 z-score 极端时做回归。**

所以这轮我没有把 repo 只当成“又一个 stat-arb 大框架”，而是直接把最像 desk 可交易原型的那一层拎出来：

> **`pair admission` 用相关性 + 残差稳定性，`entry` 用 residual z-score extreme，`exit` 先看 `1h~3h` 的 fixed-hold / time-box fade。**

---

## 这次看了什么，为什么值得 intake

**来源**
- **作者：** Atharva Joshi
- **年份：** 2026（GitHub 活跃仓）
- **标题：** `crypto-stat-arb`
- **Repo URL：** <https://github.com/atharvajoshi01/crypto-stat-arb>
- **关键文件：**
  - `README.md`
  - `cryptoarb/pairs.py`
  - `cryptoarb/signals.py`
  - `cryptoarb/backtest.py`
  - `results/backtest_results.json`

**我为什么选它**
1. 它不是“pairs trading 概念文”，而是把 **pair discovery / hedge ratio / z-score entry-exit / cost / WFO** 都写出来了；
2. 它自己很诚实：repo 公布的日频真实样本 OOS 表现是负的，但 **BTC 相关性接近 0**，说明骨架不是假 market-neutral；
3. 对我们 desk 来说，真正值钱的不是把整套日频外壳照抄，而是把里面最硬的那层翻成 **`15m` residual fade router**。

一句话核心结论：

> **这份 repo 的价值不在“日频 WFO 成绩单”，而在它把 pairs/stat-arb 最该先保留的 raw alpha 骨架写得很干净：先做 pair admission，再做 residual extreme fade。**

一句话证明方式：

> **作者用 Engle-Granger pair discovery、rolling hedge ratio、残差 z-score 进出场、显式成本和 walk-forward backtest 来支撑这条线。**

---

## repo 里最值得记的几个硬点

1. **pair discovery 不是只看相关性。**
   `pairs.py` 先相关性预筛，再做 Engle-Granger residual test，并要求 half-life 落在区间内；这比“看到两条线长得像就上”靠谱得多。

2. **signal 层很朴素，但足够可交易。**
   `signals.py` 的核心是：
   - `z > entry_z`：做空 spread
   - `z < -entry_z`：做多 spread
   - `|z| < exit_z`：平仓
   - `|z| > stop_z`：止损
   这就是完整的 raw alpha 壳，不是只有 admission 没有 exits。

3. **repo 自己的日频真实样本并不漂亮。**
   `results/backtest_results.json` 里，作者公开给出的 OOS 结果约是：
   - raw annual return `-18.77%`
   - risk-managed annual return `-15.72%`
   - BTC correlation `0.0257`
   这很重要：**说明“market-neutral 结构成立”不等于“当前版本就能赚钱”。**

4. **但这恰好更适合我们 desk 的读法。**
   既然日频大而全版本不厚，就不要迷恋长样本组合壳；更该回到短周期去测：
   **极端 residual 偏离后，未来 `1h~3h` 有没有 pocket mean reversion。**

---

## 本轮 portability probe：更像 `15m` raw alpha，而不是 `5m` 硬压执行

### Probe 口径
- **市场：** Binance USDⓈ-M perpetual
- **周期：** `15m` 主实验，`5m` 只做 child-execution sanity check
- **样本：** `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`
- **时间：** `15m` 近约 `60d`，`5m` 近约 `21d`
- **本地简化说明：** repo 原版 pair admission 用 Engle-Granger + ADF；本轮 portability probe 先用 **高相关 + residual finite half-life** 做 lightweight proxy，再看 residual z-score extreme 的后续 spread 回归。
- **artifact：**
  - `reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_pairs.csv`
  - `reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_events_15m.csv`
  - `reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_router_15m.csv`
  - `reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_events_5mchild.csv`
  - `reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_router_5mchild.csv`
  - `reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_summary.json`

### 结果 1：当前最像 pocket 的 pair，不在 BTC/ETH，而在 mid-cap 组合
本轮 proxy 里筛出来的 3 组代表性 pair 是：
- `LINKUSDT / LTCUSDT`：corr≈`0.924`，half-life≈`76` bars
- `SOLUSDT / LTCUSDT`：corr≈`0.904`，half-life≈`82` bars
- `LINKUSDT / AVAXUSDT`：corr≈`0.937`，half-life≈`86` bars

这和很多短周期 stat-arb 的经验一致：**majors 最干净，但也最容易被卷平；mid-cap 某些结构 pocket 反而更厚。**

### 结果 2：`15m` residual extreme fade 当前是正的，而且越拉长到 `2h~3h` 越像样
对这些入选 pair，用 residual `|z|>=2` 作为事件，方向按“偏离就反手回归”处理：
- 全事件样本 `n=2083`
- next `4/8/12` bars（约 `1h/2h/3h`）mean gross ≈ `+7.39 / +15.59 / +23.08 bps`
- 胜率约 `56.8% / 60.9% / 62.3%`

若同一时点多个 pair 同时触发，只做 **`abs(z)` 最大** 的 strongest-only router：
- `n=1528`
- next `4/8/12` bars mean gross ≈ `+8.13 / +15.97 / +23.69 bps`
- 胜率约 `57.7% / 61.7% / 63.4%`

也就是说，这条线当前更像：

> **`15m` pair-admission + strongest residual dislocation router + `2h~3h` time-box fade**

而不是高频秒杀策略。

### 结果 3：硬把它压成 `5m` child execution，当前反而转负
把同样的 `15m` 事件拿去看 `5m` 子窗口：
- strongest-only next `3/6/12` 个 `5m` bars mean gross ≈ `-5.39 / -3.34 / -0.83 bps`

这很关键：**不要看见 spread fade 就本能想“越快越好”。**
当前更合理的 desk 读法反而是：
- alpha 识别在 `15m`
- 持有窗至少给到 `1h~3h`
- `5m` 只适合做更细的挂单/分批，不适合拿来重写信号本体

---

## 3.5 策略拆解（必填）

- **方向属性：** 相对价值 / pairs / stat-arb / 逆势回归
- **基础 alpha：** `cointegration-first residual spread mean reversion`
- **regime：** pair 关系稳定、残差 half-life 有限、不要在结构断裂时硬做
- **filter / veto：** 相关性预筛；更严格版本用 Engle-Granger / ADF；只做 `abs(z)` 足够大、且 strongest-only 的 dislocation
- **risk / sizing / execution overlay：** beta-neutral 配腿；`|z|<exit_z` 平仓或 `1h~3h` time-box；`|z|>stop_z` 止损；成本要按双腿进出场估算，而不是单腿 thinking

---

## 为什么这轮值得进研究池

因为它补的是 **raw alpha 素材池**，不是又一个“shared gate”。

而且它服务的是我们最近持续在补的空缺：
- 不是 trend / breakout
- 不是单币 direction
- 而是 **relative-value / stat-arb**

更具体地说，这轮先回答了一个很直接的问题：

> **对 short-cycle crypto desk，pairs/stat-arb 该先押注在哪一层？**

当前答案不是“复杂图聚类”也不是“先上 Kalman 全家桶”，而是：

> **先把 `pair admission` 和 `residual extreme fade` 这条最朴素的 raw alpha 壳测扎实。**

---

## 最小可复刻实验

1. 选 `10~20` 个 liquid perp；
2. 每天/每周重算一次 pair admission：相关性预筛 + residual stationarity/half-life；
3. 每根 `15m` 更新 residual z-score；
4. 若 `|z|>=2`，做 beta-neutral spread fade；若多组同时触发，只做 `abs(z)` 最大的 1 组；
5. 固定持有 `8~12` 根 `15m`，或 `|z|<0.5` 提前出；
6. 粗扣双腿 round-trip 成本后，再看这条线是不是还活着。

**先看两个指标：**
- `gross / net bps per trade`
- `pair breakdown`：edge 是否被少数 mid-cap pair 独占

**下一步怎么测：**
1. **把本轮 lightweight proxy 升级成正式 Engle-Granger / ADF admission；**
2. **做 friction ladder：** `8 / 12 / 16 / 20 bps` 的双腿 round-trip 生死线；
3. **加 break-risk veto：** 当 BTC 单边大波动或 funding/event 边界来临时，pair 关系是否更容易断裂；
4. **做 horse race：** 和现有 `ratio-zscore pairs`、`cluster deviation stat-arb`、`residual loser-bounce basket` 比，确认它是不是独立 pocket。

---

## 风险与保留意见

1. **本轮本地 probe 不是 repo 的严格复刻。**
   repo 有更完整的 Engle-Granger / ADF / WFO / cost 结构；我这轮先做的是 short-cycle portability proxy。

2. **成本非常关键。**
   这是双腿进、双腿出；gross `15~24bps` 看着不错，但如果 taker/slippage 合计上到 `16~20bps`，很多边际样本就会被吃掉。

3. **pair break 是真风险，不是 paper risk。**
   crypto 里叙事切换、funding、链上事件、上币/下币消息，都会让原本稳定的 pair 突然失效。

4. **当前 pocket 更偏 mid-cap。**
   这意味着 edge 可能更厚，但容量、滑点、冲击成本也会更差。

---

## 我对这条线的当前判断

这轮我会把它放进：

> **可独立复现、且可直接落成完整策略壳的 raw alpha 候选。**

不是因为 repo 的日频成绩单很漂亮，恰恰相反——
**正因为 repo 把骨架写清楚、但原版成绩并不神，我们才更容易老老实实地把它拆成 desk 真正该先测的那一层。**

当前最值得保留的，不是“大而全 stat-arb 平台”这件事，而是：

> **`pair admission × strongest residual dislocation fade` 在 `15m` 上有 pocket evidence，但不适合直接压成 `5m` 高频执行。**

---

## 来源

- Atharva Joshi. (2026). *crypto-stat-arb*. GitHub repository.
- Repo URL: <https://github.com/atharvajoshi01/crypto-stat-arb>
- README: <https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/README.md>
- Pairs module: <https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/cryptoarb/pairs.py>
- Signals module: <https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/cryptoarb/signals.py>
- Backtest module: <https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/cryptoarb/backtest.py>
- Backtest results: <https://raw.githubusercontent.com/atharvajoshi01/crypto-stat-arb/main/results/backtest_results.json>
