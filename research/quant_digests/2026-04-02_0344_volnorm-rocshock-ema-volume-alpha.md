# 别把 15m 动量继续写成固定 lookback 均线：这份 2026 新 repo 更适合先测的是「vol-normalized ROC shock × EMA displacement × volume confirmation」这条完整 raw alpha
- 时间：2026-04-02 03:44 UTC
- 类型：2026 GitHub 新仓库 source audit（`walk_forward_optimization.py` + `README.md` + GitHub API metadata）+ 2022 crypto TA 成本文献作 sanity anchor
- 主题类型：raw alpha
- 基础 alpha：当短周期收益冲击已经显著超过其自身近期波动、且价格已脱离均线并伴随放量时，后续数个 bar 更容易继续沿冲击方向走出短段延续；alpha 本体是“shock continuation”，不是 EMA filter 本身，也不是纯 volume gate。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/trend/momentum/single-asset/roc-shock/vol-normalized/ema-displacement/volume-confirmation/walk-forward/optuna/trailing-stop/binance/btc/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：2026 GitHub repo source audit（主证据）+ 2022 论文元数据（成本诚实性背景）

## 1. 这次看了什么
### 一句话核心结论
**这轮更值得 intake 的，不是“又一个动量回测脚本”，而是 repo 已经写成完整策略骨架的一条 directional raw alpha：`ROC > k×ROC_std` 的异常收益冲击，只有在 `price > EMA + m×EMA_std` 且 `volume > volume_MA` 时才入场，随后用 `EMA 跌回/穿回 + trailing stop` 出场。**

### 一句话它是怎么证明的
**证明方式不是论文 headline，而是源码直接把 alpha 的四层都摆出来了：波动标准化冲击阈值、趋势位移确认、成交量确认、walk-forward 参数搜索。** 这让它比“单纯 RSI/MA 交叉”更像一张可直接下场做最小实验的完整策略卡。

## 2. base alpha 是什么
这次的 **base alpha 很清楚**：

1. 用 `ROC = (P_t - P_{t-L}) / P_{t-L}` 衡量最近一段价格加速度；
2. 不是看绝对 ROC，而是看它相对自己近期波动是否异常：`ROC > k × rolling_std(ROC)` 才算真正的 upward shock，`ROC < -k × rolling_std(ROC)` 才算 downward shock；
3. 只有当价格已经明显站上/跌破均线结构，且成交量高于自身均量时，才承认这次 shock 不是噪音；
4. 入场后不赌固定持有期，而是让价格继续跑，直到 **跌回 EMA / 涨回 EMA** 或被 trailing stop 赶出去。

翻成人话：**它不是“均线多头就买”，而是“只有当异常强的收益冲击，已经穿透均线结构且有量能支持时，才去吃接下来那一小段延续”。**

## 3. 为什么这轮值得写
- 最近 intake 里 `pairs / stat-arb / carry / cross-market` 已经很多；这条线补的是一个**更容易直接落到执行层的单币方向性 raw alpha**。
- 它和当前项目的学习轨迹是顺的：
  - `LEARNING_TRACK.md` 里一直在补 **多周期动量、量价确认、ATR/止损、市场状态过滤**；
  - `FACTOR_BACKLOG.md` 里也明确提到 **trailing stop / volume / EMA 结构**这些组件值得被抽成正式对象；
  - 但 bot7 当前优先级又要求别继续围着旧 breakout 模板内循环。这个 repo 刚好给的是 **不同于“突破一根线”的 shock-continuation 骨架**。
- 它还自带 **walk-forward + 参数搜索** 壳子，比只写一个 entry rule 的 repo 更适合做 desk 化最小复现。

## 4. 来源信息
### 主工程来源
- **Author / Repo owner：** `SigmaFlowX`（GitHub owner）；当前唯一提交作者显示为 **Dmitrii Bakaev**
- **Year：** 2026（repo 最后 push 在 2026-01-31）
- **Title：** `Crypto-Momentum-Driven-Strategy`
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/SigmaFlowX/Crypto-Momentum-Driven-Strategy>
- **Repo URL：** <https://github.com/SigmaFlowX/Crypto-Momentum-Driven-Strategy>
- **GitHub metadata：** created `2025-11-15T07:57:38Z`，pushed `2026-01-31T06:56:53Z`，default branch `main`
- **关键文件：**
  - `walk_forward_optimization.py`
  - `README.md`（内容几乎为空，核心证据主要在代码）

### 成本诚实性背景来源（不是这条 alpha 的主证据）
- **Authors：** Pablo Svogun, Sergio Bazán-Palomino
- **Year：** 2022
- **Title：** *Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?*
- **Venue：** *Journal of International Financial Markets, Institutions and Money*
- **DOI：** <https://doi.org/10.1016/j.intfin.2022.101601>
- **Readable URL：** <https://www.sciencedirect.com/science/article/pii/S1042443122000130>
- **这篇在本文中的角色：** 不是用来“证明 repo 这条 alpha 一定成立”，而是提醒我们：**crypto TA 类 raw alpha 一开始就该带成本梯子，不能只看毛收益。**

## 5. repo 具体是怎么把这条 alpha 写出来的
### 5.1 数据与 frequency
`walk_forward_optimization.py` 直接读：
- `BTCUSDT_1m.csv`

然后先做一次 desk 友好的降采样：
- 把 `1m` OHLCV 聚合成 `15m`
- `open=first`，`high=max`，`low=min`，`close=last`，`volume=sum`

这点很重要：**repo 的输入虽然是 1m，但 alpha 判定主框架其实已经落在 15m。** 这正好贴近我们当前 desk 默认主频。

### 5.2 Train / test shell：不是随便挑一组参数就宣布胜利
repo 把 walk-forward 明确写成：
- `6` 个月 train
- `3` 个月 test
- 每次窗口向前滚 `3` 个月

也就是说，它不是在全样本上找最优参数然后自我感动，而是至少有一个**滚动 OOS 壳子**。

### 5.3 Entry：异常收益冲击 × 均线位移 × 放量确认
源码里 long 条件是：
- `curr_roc > roc_threshold * curr_roc_std`
- `curr_price > curr_ema`
- `curr_vol > curr_vol_ma`
- `curr_roc > roc_prev`
- `curr_price > curr_ema + ema_threshold * ema_std`

short 则完全镜像：
- `curr_roc < -roc_threshold * curr_roc_std`
- `curr_price < curr_ema`
- `curr_vol > curr_vol_ma`
- `curr_roc < roc_prev`
- `curr_price < curr_ema - ema_threshold * ema_std`

这条设计里，**真正的 alpha 本体** 是第一条：
`ROC 相对自身波动显著异常`。

后面几条更像 admission / confirmation：
- `price vs EMA`：方向结构别和 shock 打架；
- `volume > volume_MA`：别在无量时追；
- `curr_roc > roc_prev`：要求冲击还在加速；
- `price > EMA + m×EMA_std`：要求不是刚碰到均线，而是已经明显偏离。

所以更准确的 desk 读法应该是：
**raw alpha = shock continuation；EMA / volume / displacement 是 admission layer，而不是 alpha 本体本身。**

### 5.4 Exit：不是固定 hold，而是结构失效就走
repo 的出场没有搞太多花活：
- long：`price < EMA` 或 `price < trailing_stop`
- short：`price > EMA` 或 `price > trailing_stop`

这比“永远持有 N 根 bar”更适合短周期 desk，因为它自然允许：
- 有些 shock 只延续 2~3 根；
- 有些冲击会拉出一段 trend leg；
- trailing stop 帮你留住继续加速的样本，而 EMA 回归负责切掉结构失效。

### 5.5 Sizing 与成本：很粗，但至少不是零
代码里：
- `risk_percent = 10`
- `fee = 0.02`
- PnL 扣减口径是 `2 * fee / 100`

翻成更直观的口径：
- 每笔交易按约 **10% 资金权重**计入收益；
- round-trip fee 约 **4 bps**。

这里要非常诚实：
- `10%` 更像固定 notional fraction，不是完整风险预算；
- `4 bps` 对很多真实 perp 执行场景都偏乐观；
- repo 没有显式 funding、冲击成本、挂吃单差异、延迟/队列成本。

所以它更像一张 **alpha existence card**，而不是可直接拿去实盘的成本口径。

## 6. 5 个最值得记住的硬数据点
1. **主频其实已经是 `15m`，不是 repo 简介里那句“1m 数据”本身。** 因为源码先把 `1m` 聚合成了 `15m` 再判信号。
2. **walk-forward 不是装饰。** 训练/测试壳子是 `6m train / 3m test / 3m step`。
3. **参数搜索空间很宽。** `EMA_length / volume_ma_period / roc_period / roc_std_window` 全都在 `10~300` 间搜索。
4. **冲击阈值不是固定 return，而是波动标准化阈值。** `roc_threshold` 搜 `0.5~10.0`，避免把不同波动环境下的同样绝对涨跌幅混为一谈。
5. **位移确认与风控也被参数化了。** `ema_threshold` 搜 `1~5` 个 rolling std，`trailing_pct` 搜 `0.5%~10%`。

这 5 个点说明：repo 最值钱的不只是“做 momentum”，而是它把 **冲击、确认、退出、WFO** 四层都工程化了。

## 7. desk 最该偷走的，不是“Optuna 优化”这几个字
如果按 repo 自己的包装去读，很容易把重点放在参数搜索。但对我们更值钱的其实是下面这条 skeleton：

- **raw alpha：** vol-normalized return shock continuation
- **admission：** EMA 同向 + volume 确认 + displacement 够大
- **exit：** EMA 回归 / trailing stop
- **research shell：** rolling train/test + 宽参数区间

也就是说，**Optuna 只是外壳，alpha 内核是“异常冲击后的短段延续”。**

## 8. 和当前 1m / 3m / 5m / 15m 的关系
### 8.1 这条线和我们当前主频是对得上的
repo 的判定层本来就是 `15m`。因此它最适合：
- `15m`：做主实验与 first verdict；
- `5m`：细化入场时机、做 execution refinement；
- `1m / 3m`：只在确认 15m after-cost 活着后，再用于更细的追价/回撤优化。

### 8.2 不要错翻成“任何短涨跌都追”
真正可 desk 化的翻法不是：
- “5m 涨了就追”；

而是：
- “最近一段收益冲击，已经显著超过它自己近期常态波动”；
- “而且这次冲击不是 dry move，而是有量、有结构位移”；
- “这时才允许追第二段 continuation”。

### 8.3 它属于哪类 raw alpha
它不是 pairs，不是 carry，不是 funding，也不是单纯 breakout 画线。
它更接近：
- **single-asset trend / momentum**
- **shock continuation**
- **volatility-normalized directional alpha**

## 9. 最小可复现实验
### 实验 A：15m baseline existence test（最优先）
- **标的：** `BTC / ETH / SOL / BNB` 永续；可先从 BTC+ETH 起步
- **bar：** `15m`
- **signal window：** `roc_period ∈ {12, 24, 36, 48}`（约 `3h / 6h / 9h / 12h`）
- **shock 定义：** `ROC / rolling_std(ROC) > k` 做多；`< -k` 做空，`k ∈ {1.0, 1.5, 2.0, 2.5}`
- **admission：**
  - `price > EMA_L` / `< EMA_L`
  - `volume > rolling_volume_ma`
  - `|price - EMA| / rolling_std(price) > m`
- **exit：** `EMA cross-back` vs `1.0% / 1.5% / 2.0% trailing` vs 二者并用
- **成本：** round-trip `6 / 10 / 14 / 20 / 30 bps`

先回答一个最朴素的问题：**after-cost 下，shock continuation 在 15m perp 上到底有没有生存空间。**

### 实验 B：5m execution refinement
若实验 A 成立，再做：
- `15m signal confirmed` 后，比较
  - 下一根 `5m` 立即追；
  - 等第一根 `5m` 小回踩后追；
  - 用 `VWAP pullback` 进；
- 看哪个 entry 能把追涨/追跌的 adverse selection 压下来。

### 实验 C：shared veto / overlay（不要反客为主）
在 alpha 本体成立后，再叠：
1. 高 funding 逆向拥挤 veto；
2. 重大 news / liquidation cascade veto；
3. 超高 realized vol 环境下降杠杆。

注意顺序：**先验证 raw alpha，再加 overlay；不要让 overlay 冒充 alpha。**

## 10. 下一步怎么测
1. **先做“去优化版”复刻。** 不要一上来就大网格 + Optuna；先固定 1~2 组合理参数，看 existence。否则很容易把 WFO 壳子误当成 alpha。
2. **优先测 cross-asset transfer。** repo 只喂了 `BTCUSDT_1m.csv`；我们更该看 BTC 以外，ETH / SOL / BNB 是否也有类似结构。
3. **先把成本打厚。** repo 默认约 `4bps` round-trip 太乐观；desk 版 first pass 应至少看 `10~30bps`。
4. **把 alpha 与 admission 拆开做 ablation。** 依次比较：
   - shock only
   - shock + EMA
   - shock + EMA + volume
   - shock + EMA + volume + displacement
   这样才知道 edge 到底来自哪一层。
5. **比较 fixed hold vs structure exit。** 很多 shock alpha 的好坏不止取决于 entry，也取决于“要不要让赢家多跑一段”。

## 11. 这条线最容易错在哪
- **把 admission layer 当 alpha 本体。** 其实真正的 raw alpha 是异常冲击后的延续，EMA/volume/displacement 只是筛选器。
- **把 Optuna 当护身符。** 有 walk-forward 不等于一定稳；如果 alpha 本体弱，优化只是在放大噪音。
- **低估执行摩擦。** 追强/追弱类策略最怕滑点和追单成本，repo 的 fee 口径明显偏薄。
- **只做 BTC 就宣布 universality。** 单币 directional alpha 最怕只是在某段 BTC regime 中看起来好看。
- **把它硬说成 breakout。** 它和经典 Donchian/通道突破不同：这里更核心的是 **异常收益冲击的标准化与加速**，不是一根线被穿。

## 12. 对当前项目的直接意义
这条主题值得进研究池，因为它满足当前高优先级条件：
- **主题类型：raw alpha**
- **基础 alpha 清楚**
- **可以直接写成 entry / exit / sizing / risk / cost**
- **数据公开可得（Binance 1m → 15m）**
- **和当前学习层匹配：动量 + 量价确认 + trailing 风控**

如果要一句话概括：**这份 repo 最值钱的不是“自动调参”，而是它把一条 short-cycle directional raw alpha 诚实拆成了四层：`异常冲击`、`结构确认`、`量能确认`、`结构失效退出`。**

## 13. 来源链接
### 主来源
- Repo：<https://github.com/SigmaFlowX/Crypto-Momentum-Driven-Strategy>
- GitHub API metadata：<https://api.github.com/repos/SigmaFlowX/Crypto-Momentum-Driven-Strategy>
- Core file：<https://raw.githubusercontent.com/SigmaFlowX/Crypto-Momentum-Driven-Strategy/main/walk_forward_optimization.py>

### 背景来源
- Paper DOI：<https://doi.org/10.1016/j.intfin.2022.101601>
- Readable article page：<https://www.sciencedirect.com/science/article/pii/S1042443122000130>
