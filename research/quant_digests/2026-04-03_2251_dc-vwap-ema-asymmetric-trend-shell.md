# 别把这份 2026 新 repo 只读成“参数寻优大合集”：对 crypto short-cycle desk，更该先测的是「VWAP-EMA directional change × 非对称入场 / 约 1% 反向退出」这条完整 trend raw alpha——但必须先过 asset-ranking admission
- 时间：2026-04-03 22:51 UTC
- 类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `engine.py` + `notes/note_38_master_synthesis_four_studies.md` + `note41_weighting_study.md`）+ Binance Futures 公共 `5m/15m` 最小便携性快检
- 主题类型：raw alpha
- 基础 alpha：**不是“VWAP 当确认线”那么简单，而是把 `VWAP 的 EMA` 当作一条更慢的“成交量加权趋势脊柱”，在下跌段结束、该脊柱从局部低点重新抬升足够多（buy threshold）时做趋势接力；持有到这条脊柱从局部高点回撤约 1% 左右（sell threshold）就退出。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / trend / momentum / single-asset / directional-change / vwap-ema / asymmetric-entry / reversal-exit / asset-ranking / admission-layer / binance-perp / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo（完整策略骨架 + 研究笔记）+ 本地 public-data portability probe

**先回答 base alpha：这篇东西的 base alpha 很清楚，属于 raw trend alpha，不是 filter。它赌的是：当“成交量加权后的慢趋势脊柱”结束下跌并重新抬升到足够幅度时，后面还有一段可吃的 continuation；而退出端不是拍脑袋止盈，而是等这条脊柱自己反向约 1% 才走。**

## 1）为什么这轮值得 intake
这轮我还是把它当主 digest，不是因为 repo 自报数字很夸张，而是因为它满足当前 `RESEARCH_AUTOMATION_BRIEF` 里更重要的几条：

- 它是**raw alpha 本体**，不是纯 regime / filter / overlay；
- 它是**完整策略壳**，entry / exit / cost / sizing 口径都能说清；
- 它是**最近几天的新仓库**，而且不是只有 README slogan，核心 `engine.py` 和研究 notes 都能直接读；
- 它还能帮我们补一个很关键的反面经验：**trend raw alpha 可以看，但不要把“跨资产无脑通用参数”当真**。

结合 `LEARNING_TRACK` 里“优先研究含回测与风控模块的开源实现”，这类 repo 比纯综述更值钱，因为它能直接进入 `first verdict`。

## 2）这次看了什么
### 2.1 主来源
1. **shehzadahmed-xx (2026), _arcus-dc-engine_, GitHub repository**  
   - Venue：GitHub  
   - DOI：N/A  
   - Readable URL：<https://github.com/shehzadahmed-xx/arcus-dc-engine>  
   - Repo URL：<https://github.com/shehzadahmed-xx/arcus-dc-engine>  
   - GitHub API metadata：创建于 `2026-03-31`，最近 push `2026-03-31`，描述为 `40 crypto studies / 4 research programs / 517+ assets / 78 notes`

2. 这次重点看的文件
   - `README.md`
   - `engine.py`
   - `notes/note_38_master_synthesis_four_studies.md`
   - `note41_weighting_study.md`

### 2.2 repo 自报里最值得记住的 4 个数字
- **4 个研究计划 / 517+ 资产 / 78 notes**：不是单一 toy repo
- **sell threshold 在四个研究里大致稳定在 `~1.0% - 1.8%`**
- **47×47 = 2,209 次 cross-asset test，找到 `0` 组 universal params**
- `note41` 的 15 资产组合比较里：
  - 11 个月共同窗口下，`Equal Weight +21.8%`，`Weekly-Stability +26.7%`
  - 24 个月窗口下，`Weekly-Stability +117.4%`，`Equal Weight +96.3%`，`Score Weight +96.1%`

翻成人话：

> repo 真正想表达的不是“这里有一组神参数”，而是：**DC + VWAP-EMA 这套机制可能有 edge，但 entry 参数强依赖资产和目标函数；真正最稳定的是 exit 端。**

## 3）repo 里真正能搬走的策略骨架
`engine.py` 把逻辑写得非常直接：

### 3.1 信号层
- 先按 `1h / 4h / 12h / 24h` 这类周期重置 VWAP
- 再对 VWAP 做一层长 EMA（默认 `ema_period=227`）
- 对 `VWAP-EMA` 跑 Directional Change：
  - 若当前在下跌段，只有当 `VWAP-EMA` 从局部低点反弹超过 `buy_threshold` 才给 `buy`
  - 若当前在上涨段，只要从局部高点回撤超过 `sell_threshold` 就给 `sell`

repo 的 live-bot 默认参数是：
- `buy_threshold = 4.3%`
- `sell_threshold = 1.09%`
- `ema_period = 227`
- `vwap_reset_period = 4h`

而四研究总结合成出来的三个 profile 更关键：
- **Standard trend**：买阈值约 `7.5%`，卖阈值约 `1.8%`
- **Swing trader**：买阈值约 `2.0%`，卖阈值约 `1.8%`
- **Patient trend**：买阈值约 `16.7%`，卖阈值约 `1.25%`

最重要的共识不是 entry，而是：

> **退出几乎总围绕 `~1%` 的反向 DC；变化最大的是你愿意等多大一级的“重新抬头”才入场。**

### 3.2 执行与成本层
`engine.py` 默认就把成本写进执行价：
- `fee_rate = 0.10%`
- `slippage = 0.05%`
- `capital_usage = 0.98`

也就是说，它不是“有信号、没壳子”的研究，而是至少把：
- entry
- exit
- cost
- deploy fraction

这几件最基本的实盘要素写清了。

### 3.3 这条 alpha 的正确命名
如果写进素材池，我会把它命名成：

**`VWAP-EMA directional-change continuation × ~1% reversal exit`**

这比笼统写“趋势跟随”更准确，因为它强调了：
- 触发不是均线金叉，而是**从局部低点抬升够多**；
- 退出不是固定止盈止损，而是**从局部高点回撤约 1%**；
- 核心不是 price-only，而是**volume-weighted trend spine**。

## 4）repo 最值得 desk 学的，不是 headline PnL，而是两条方法论
### 4.1 `sell threshold` 可能比 `buy threshold` 更像可迁移组件
`note_38` 里四个研究最稳的不是 entry 参数，而是 exit 端始终围绕 `1.0%~1.8%`。这对 desk 很值钱，因为它意味着：

- entry 可以换成别的 raw alpha（例如 OFI、RSI breakout、rolling-high break、leader-window continuation）；
- 但 exit 也许可以直接借这条**反向 DC 退出骨架**来做 A/B。

也就是说，这个 repo 不一定非得整条照抄；它也可以拆成：
- raw alpha：某个更适合我们的入场
- overlay / exit shell：`~1% reversal-on-smoothed-VWAP` 退出

### 4.2 这套东西默认**不是**“全市场统一模板”
repo 自己最强的一条结论反而是：

- 47 个资产做 cross-validation，**没有**任何一组 universal params；
- 某个资产自测好，不代表拿去别的资产还能活；
- 目标函数不同（Calmar / Sharpe / consistency），最优行为也完全不同。

翻成人话：

> 这条 alpha 更像“一个可移植的机制 + 必须有资产 admission”的组合，不像 `BTC/ETH/SOL` 上拿一套固定参数就能推全场的通用因子。

这点对当前 desk 很重要，因为 `FACTOR_BACKLOG` 已经明确不想继续围绕旧 baseline 无穷微调。这个 repo 给我们的更好启发是：

- 不要继续围绕旧趋势 baseline 小修小补；
- 直接把它当一条**新 raw alpha 壳**或**新 exit 模块**，跑 admission check。

## 5）Binance 公共数据最小便携性快检：通用化直搬并不漂亮
先强调：下面不是 repo 原始复现，而是我按 `engine.py` 的 exact logic 做的**最小 transfer check**，目的只是回答一个问题：

> 把这条骨架直接搬到我们关心的 `5m / 15m` perp 上，能不能先活下来？

结果文件：
- `reports/artifacts/quant_digests/2026-04-03_dc_vwap_ema_portability_probe.csv`

### 5.1 Probe A：Standard-trend 参数，测 majors
口径：
- 标的：`BTCUSDT / ETHUSDT / SOLUSDT`
- 周期：`5m / 15m`
- lookback：最近 `90d`
- 参数：`buy=7.5% / sell=1.8% / ema=227 / vwap_reset=4h`
- 成本：`7 bps / side`

结果很直白：**全负**。
- `BTCUSDT 5m`：`-6.2%`，`3` 笔，胜率 `0%`
- `ETHUSDT 5m`：`-10.0%`，`4` 笔，胜率 `25%`
- `SOLUSDT 5m`：`-24.2%`，`6` 笔，胜率 `0%`
- `15m` 也没救，`BTC/ETH/SOL` 仍全部为负

### 5.2 Probe B：live-XRP 默认参数，测更像 repo 风格的 alts
口径：
- 标的：`XRPUSDT / TRXUSDT / ADAUSDT / XLMUSDT`
- 周期：`5m / 15m`
- lookback：最近 `90d`
- 参数：`buy=4.3% / sell=1.09% / ema=227 / vwap_reset=4h`
- 成本：`15 bps / side`（按 engine 默认）

结果仍然不算好：
- `TRXUSDT 15m`：**`+1.66%`**，`2` 笔，胜率 `50%`，是唯一轻微为正的 pocket
- `TRXUSDT 5m`：`-1.09%`
- `XRPUSDT 15m`：`-7.52%`
- `ADAUSDT 15m`：`-20.44%`
- `XLMUSDT 15m`：`-15.80%`

### 5.3 这轮快检的 honest 结论
这条线**不是**“今天拿到 repo，明天就该在 majors 5m/15m 全市场铺开”的那种候选。

更诚实的读法是：
- **机制有意思**；
- **exit 端可能有可迁移价值**；
- 但**通用参数直搬当前 desk 主关注市场，证据很弱**；
- 若要继续推进，必须先做**asset-ranking / asset-specific admission**，而不是把它当天然 universal alpha。

## 6）所以它到底值不值得继续？
我会给的结论是：**值得继续，但只值得按“局部可用机制”推进，不值得按“通用完整策略”直接推进。**

### 值得继续的部分
1. **base alpha 清楚**：是 raw trend alpha，不是抽象 filter
2. **完整壳齐**：entry / exit / cost / deploy fraction 都有
3. **退出值得单独拆**：`~1% reversal exit` 很可能比 entry 更可迁移
4. **实验成本低**：只要公共 OHLCV 就能做 admission

### 不值得直接相信的部分
1. repo 里漂亮组合收益，本质上依赖**per-asset 参数 + 组合权重**
2. 最近 `90d` 的 majors / 常见 alts transfer，并没有支持“拿来就能用”
3. 若跳过 asset admission，直接把它当 universal strategy，很可能浪费复现资源

## 7）下一步怎么测（最重要）
### A. 先把它从“完整策略”拆成“两块组件”
分别测：
- **entry shell**：`DC on VWAP-EMA` 是否真比简单 breakout / RSI breakout 更好
- **exit shell**：`~1% reversal on smoothed VWAP` 能否作为跨策略共享退出

这一步能回答：edge 在 entry，还是主要在 exit。

### B. 做一个严格的 asset-ranking admission
不要先拿 `BTC/ETH/SOL` 代表全市场。应该在 top `30~50` liquid perp 上跑：
- `5m / 15m / 30m / 1h`
- 至少两组 profile：standard trend / patient trend
- 排序指标：成本后收益、trade count、max DD、连续亏损、跨月稳定性

如果最后只有少数币有效，那就把它定位成：
- **ranked-alt sleeve**，而不是 universal market beta。

### C. 单独测 `sell_threshold` 稳定性
固定 entry，直接 sweep：
- `sell = 0.8% / 1.0% / 1.25% / 1.5% / 1.8% / 2.2%`

配合我们现有的：
- RSI breakout
- OFI / taker imbalance
- rolling-high continuation

看是否真的存在一个跨 alpha 更稳的 exit 区间。

### D. 把 patient-trend profile 上移到更高周期
repo 的“Patient trend”本来就不是为了高频打点。对 desk 来说，先别急着只盯 `5m`：
- 可以把 `15m` 当主测
- `30m / 1h` 当结构确认层
- 再反向压缩到 `5m` 做 execution / add-on，而不是把它直接当 `5m` 裸信号

## 8）结论
如果只用一句话总结：

> **这份 2026 新 repo 真正值得 desk intake 的，不是“几百资产研究后找到万能参数”，而是它给出了一条很清楚的 raw trend alpha 母板：`VWAP-EMA directional change` 入场，配 `~1% reversal` 退出；但本地 `5m/15m` transfer check 明确提醒我们——它更像“必须先做 asset-ranking 的机制”，不是可直接通用部署的全市场 alpha。**

所以我会把它放进素材池，但标签会写得很明确：
- **主标签**：raw alpha / trend / directional change
- **次标签**：exit-shell candidate / asset-admission required
- **当前 verdict**：**值得继续做 admission，不值得直接当 universal strategy 上 production**

## Sources
1. **shehzadahmed-xx (2026), _arcus-dc-engine_, GitHub repository**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/shehzadahmed-xx/arcus-dc-engine>  
   - Repo URL: <https://github.com/shehzadahmed-xx/arcus-dc-engine>

2. **Repository README / engine**  
   - README: <https://raw.githubusercontent.com/shehzadahmed-xx/arcus-dc-engine/main/README.md>  
   - Engine: <https://raw.githubusercontent.com/shehzadahmed-xx/arcus-dc-engine/main/engine.py>

3. **Research notes used in this digest**  
   - Master synthesis: <https://raw.githubusercontent.com/shehzadahmed-xx/arcus-dc-engine/main/notes/note_38_master_synthesis_four_studies.md>  
   - Weighting study: <https://raw.githubusercontent.com/shehzadahmed-xx/arcus-dc-engine/main/note41_weighting_study.md>

4. **Local portability probe artifact**  
   - `reports/artifacts/quant_digests/2026-04-03_dc_vwap_ema_portability_probe.csv`
