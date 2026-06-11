# Deribit gamma wall × positive/negative gamma：给 breakout / fade 都能用的 shared router

- 时间：2026-04-05 20:55 UTC
- 类型：regime
- 主题标签：regime/filter/shared-gate/options/gamma-exposure/gamma-flip/put-wall/call-wall/router/breakout/mean-reversion/deribit/btc/5m/15m/3m/1m/repo/public-api/cost/risk
- 证据类型：2026 GitHub 新 repo source audit（GitHub API metadata + `README.md` + `docs/GEX.md` + `src/analytics/backtest.py` + `src/analytics/signal_model.py` + `docs/ANALYTICS.md`）+ Deribit 公共 API 文档可得性确认；辅以 2025 SSRN 标题/DOI 作主题锚点

## 1. 这次看了什么
这轮不再硬找又一条“像 raw alpha 的 headline 结论”，而是补一个**能同时服务至少两类 alpha 的 options-derived shared router**：用 Deribit 公共期权链算出来的 **total GEX / gamma flip / put wall / call wall**，把 BTC 短周期交易路由成两套不同打法——**negative gamma 走 breakout continuation，positive gamma 走 near-wall fade / mean reversion**。

## 2. 先回答：这篇东西的 base alpha 是什么？
- 主题类型：regime
- 基础 alpha：**negative gamma 下的 wall-break continuation**，以及 **positive gamma 下的 wall-reject fade / mean reversion**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

这里要说清楚：它**不是一个裸方向 raw alpha**，而是一个更像“短周期路由器”的 shared gate。
但它不像泛泛的宏观/情绪过滤层那样飘：它来自**可实时拉取的 BTC 期权链公开数据**，能直接落到 `5m / 15m`，并可把 `1m / 3m` 当 child execution。

## 3. 为什么这轮值得补它，而不是继续补另一条 raw alpha
因为当前 desk 已经在堆很多 raw alpha 候选，但**options-derived 的共享路由层仍偏薄**。这条线的价值不在“再发明一条主信号”，而在：
- 它能同时服务 **breakout / momentum** 与 **mean reversion / fade** 两类 alpha；
- 数据公开、抓取门槛低，不需要私有 feed；
- 它天然贴近 BTC 这类被 Deribit 期权链深度影响的资产；
- 它给的是**交易环境分类**，而不是只在一个固定 pattern 上打补丁。

如果这层路由有效，后续很多已有 alpha 都能直接受益：
- breakout 只在 `negative gamma` 做；
- fade 只在 `positive gamma` 且接近 wall 时做；
- sizing 按 `|GEX| percentile` 放缩；
- 在 `gamma flip` 附近直接降杠杆或禁做。

## 4. 核心资料里到底有什么
这次的主材料不是传统论文，而是一个 2026 新仓库：

1. **strebba (2026), `btc-institutional-flow` / `ibit-gamma-tracker`**
   - Repo URL：<https://github.com/strebba/btc-institutional-flow>
   - 重点模块：
     - `docs/GEX.md`
     - `src/gex/*`
     - `src/analytics/backtest.py`
     - `src/analytics/signal_model.py`
     - `docs/ANALYTICS.md`

2. **Pawel Lachowicz (2025), _Do Gamma Walls Actually Move Bitcoin Prices at Deribit?_**
   - Venue：SSRN working paper
   - DOI：<https://doi.org/10.2139/ssrn.5782822>
   - Readable URL：<https://doi.org/10.2139/ssrn.5782822>
   - 这篇这次没有拿到可稳定抓取的摘要/全文，所以**不把它当结论证据**，只把它当“这个主题正在形成研究对象”的旁证锚点。

## 5. 这份 repo 提供了哪些可直接拿来做实验的硬信息
从 `docs/GEX.md` 和源码里，至少有 6 个对 desk 有用的硬点：

1. **数据源完全公开**
- Deribit Public API，无需鉴权。
- 关键接口：
  - `get_instruments?currency=BTC&kind=option&expired=false`
  - `ticker?instrument_name=...`
  - `get_index_price?index_name=btc_usd`
- 仓库文档明确写了公开 API 的速率级别约 `~15 req/s`。

2. **GEX 的定义写得很实**
- 单个期权：`GEX = sign × gamma × OI × contract_size × spot² × 0.01`
- call 视作正向 gamma 暴露、put 视作负向 gamma 暴露，再聚合成净 GEX。
- 这意味着我们不需要“黑箱 AI 推断 gamma wall”，直接按公开链数据重建即可。

3. **repo 已把关键 level 定义好了**
- `Gamma Flip`：累计 GEX 变号的 strike。
- `Put Wall`：最负 GEX strike，文档解释成更偏“机械支撑”。
- `Call Wall`：最正 GEX strike，更偏“机械阻力”。
- `Max Pain`：可做辅助 level，但对短周期优先级低于 wall/flip。

4. **文档给了 live snapshot 量级**
- 一次实盘快照示例：
  - GEX 总量：`+$41.5M`
  - regime：`POSITIVE_GAMMA`
  - Gamma Flip：`$75,000`
  - Put Wall：`$60,000`
  - Call Wall：`$75,000`
  - 活跃 BTC 期权：`948` 个
  - 总 OI：`432,483` 合约
- 这些量级至少说明：这不是“几张冷门期权拼出来的噪音 level”。

5. **repo 已有可操作 alert 定义**
- `GAMMA FLIP`：GEX 符号切换。
- `NEAR PUT_WALL` / `NEAR CALL_WALL`：spot 距 wall 在 2% 内。
- `GEX ESTREMO NEGATIVO / POSITIVO`：历史分位极端值。

6. **repo 自己也承认了局限**
- 全量抓取 ~948 个 BTC 期权，文档说需要约 **2 分钟**。
- 历史 GEX 需要自己持续存快照。
- event study 当前还没有足够 barrier 命中样本。

这几个局限反而对我们有帮助：它提醒我们**不要把它当 1m 逐根重算信号**，而应当把它当 `5m / 15m` 的慢变量状态层。

## 6. 对 short-cycle desk 更值钱的“旁支读法”
repo 主线更像“GEX + ETF flows 的 BTC 日频多因子解释框架”。
但对我们 desk，**更值得偷的不是它的日频主线，而是 options wall + gamma sign 这个 intraday router**。

### 6.1 Negative gamma：更适合做 breakout continuation
直觉很简单：
- 在 `GEX < 0` 时，dealer hedge 更可能**顺着价格波动方向追**；
- 所以 wall 被穿时，更该防的是“加速”，不是“立刻回归”。

更适合的壳：
- 价格接近 `call wall` 后向上有效突破，顺势追多；
- 价格接近 `put wall` 后向下有效跌破，顺势追空；
- `gamma flip` 附近若刚从正转负，可把它视作 breakout 策略的放行条件。

### 6.2 Positive gamma：更适合做 near-wall fade / mean reversion
- 在 `GEX > 0` 时，dealer hedge 更可能**对着波动反向做**；
- 所以价格靠近 wall 时，更容易出现钉住、停滞、反抽。

更适合的壳：
- 接近 `call wall` 做冲高回落 fade；
- 接近 `put wall` 做插针反弹 fade；
- 若 spot 卡在 `gamma flip` 与某一侧 wall 之间，优先缩短持有期，走短回转。

这就是它最像 shared gate 的地方：
**同一组公开数据，不是生成一个统一方向，而是先决定“今天该追还是该反”。**

## 7. 可直接落地的最小策略壳
下面给一个 desk 能直接测的、不是只会讲概念的版本。

### 7.1 Strategy A：negative-gamma wall-break continuation
适用：`5m` 主级别，`1m/3m` 做执行。

**Entry**
- 每 5 分钟更新一次期权状态层：`total_net_gex`、`gamma_flip`、`put_wall`、`call_wall`。
- 只在 `total_net_gex < 0` 且 `|total_net_gex|` 位于过去 20 个快照前 40% 极端区时启用。
- 若价格进入 wall 附近带（建议 `0.20% ~ 0.40%`），随后：
  - 向上穿 `call_wall`，且 5m 收盘站上 wall；做多。
  - 向下破 `put_wall`，且 5m 收盘跌破 wall；做空。
- 执行确认：用 `1m` child bar 做二次确认，避免单根影线误触发。

**Exit**
- 第一目标：到下一个 options level（另一侧 wall / gamma flip）的一半到三分之二路径。
- 第二目标：`1.2R ~ 1.8R` 固定止盈。
- 时间止盈：`3~6` 根 5m bar 未扩展则减仓/平仓。
- 若下一个 5m bar 回收到 wall 带内，则直接撤退。

**Sizing**
- 基础风险单位按常规 BTC perp 策略风险单位；
- 再乘 `min(1.5, |GEX_z|)` 的 regime 系数；
- 若 spot 距 `gamma_flip` 太近（如 `<0.25%`），仓位减半。

**Risk / Cost**
- 突破腿允许 taker，但要求预期路径至少覆盖 **2~3 倍单边成本**；
- 若 wall 带附近盘口明显变薄，只做最 liquid venue；
- expiry 前后 1~2 小时单独分层，不和普通时段混测。

### 7.2 Strategy B：positive-gamma wall-fade mean reversion
适用：`15m` 识别状态，`3m/5m` 进场。

**Entry**
- 只在 `total_net_gex > 0` 且处于自身历史 60% 以上分位时启用。
- spot 进入 `call_wall` / `put_wall` 附近带后，等待 `3m` 或 `5m` 出现拒绝：
  - 触 wall 但收不住，回到带内；
  - 第二根 bar 未能继续创新高/新低。
- 在 `call_wall` 失败时做空，在 `put_wall` 失败时做多。

**Exit**
- 第一目标：回到 intraday VWAP / session mid；
- 第二目标：回到 `gamma_flip`；
- 时间止盈：`2~4` 根 5m bar 仍无回归则走人。

**Sizing**
- fade 模式优先 maker；
- 仓位与 wall 距离成反比，但在 `gamma_flip` 附近不加仓；
- 若 total GEX 只是轻微为正，不做满仓 fade。

**Risk / Cost**
- 止损放在 wall 外 `0.35 ~ 0.60 ATR(5m)`；
- 若 breakout 成交量 / 冲击明显超平时，禁止逆着 negative-gamma 环境硬 fade。

## 8. 最小可复现实验怎么做
### 实验 1：先只测“路由价值”，不测复杂多因子
目标：回答一个最核心问题——
**同样的 wall touch 事件，在 `GEX>0` 和 `GEX<0` 下，后续 3 / 6 / 12 根 5m bar 的路径是否显著不同？**

实现：
1. 每 5 分钟拉一次 Deribit BTC 全链并存快照。
2. 生成事件：spot 首次进入 `put_wall/call_wall ±0.30%` 区域。
3. 按 `GEX sign` 分组。
4. 统计：
   - 之后 15m / 30m / 60m 的方向收益；
   - 最大顺行 / 逆行 excursion；
   - wall 穿透率与回带率。

如果这一步没有明显分层，后面的 router 就没必要继续加花活。

### 实验 2：把 router 套到已有 breakout alpha 上
目标：验证它能否提高已有 raw alpha 的质量。

做法：
- 选一个你们现成的 breakout 壳；
- 对照组：原规则直接跑；
- 实验组：只在 `negative gamma` 时放行，且要求突破方向与最近 wall 关系一致。

看四个指标：
- trade count
- win rate
- avg MFE / MAE
- net after-cost Sharpe

### 实验 3：把 router 套到已有 fade / mean-reversion alpha 上
- 只在 `positive gamma` 做；
- spot 必须接近 `call/put wall`；
- 其余进场规则不变。

看结果是否出现：
- 次数下降，但单笔质量上升；
- 被趋势腿拖死的次数减少；
- 手续费占比下降。

## 9. 数据口径与现实限制
### 9.1 数据源
- Deribit BTC options：公开、可直接抓。
- BTC spot/index：Deribit index 或执行 venue 自己的现货/指数。
- 若执行在 Binance / Bybit perp，需要统一成同一个 BTC 指数坐标，避免 wall level 和执行价格体系错位。

### 9.2 更新频率
- 期权全链重算不适合每分钟暴力刷。
- 更现实的口径：
  - `5m` 刷新一次全链；
  - `1m/3m` 只拿上一轮算好的 wall / flip 做 child execution。

### 9.3 不能误读的地方
- `IBIT flow → BTC` 这条是 repo 的日频主线，不要硬伪装成逐根 intraday alpha。
- `wall` 不是 magic number；它更像**状态依赖 level**。
- expiry、节假日、集中换仓时，wall 的解释力可能剧烈漂移。

## 10. 我对这条主题的判断
如果把它当“又一个方向指标”，我不喜欢；太容易变成故事。
但如果把它当成：
- **breakout / fade 的 shared router**，
- **基于公开期权链的 level-state layer**，
- **BTC 专属、可嫁接到现有 alpha 池的 execution gate**，
那它很值得进研究池。

它最适合的定位不是“单独拎出来裸跑一年”，而是：
**先做 wall-touch 分层实验，再拿来给现有 raw alpha 做 regime split。**

## 11. 下一步怎么测
只做一件最小但关键的事：

1. 连续抓 **7~14 天** Deribit BTC options 全链快照（建议每 `5m` 一次）。
2. 生成 `total_net_gex / gamma_flip / put_wall / call_wall / distance_to_wall`。
3. 在 BTC `5m` 上定义 wall-touch 事件。
4. 分 `GEX>0` 与 `GEX<0` 两组，比较后续 `3/6/12` 根 bar 的：
   - continuation hit rate
   - fade hit rate
   - MFE / MAE
   - after-cost expectancy
5. 如果分层成立，再把它分别接到：
   - 一个现有 breakout alpha
   - 一个现有 mean-reversion alpha
   做 router A/B test。

这一步如果跑不出显著分层，就直接把主题降级；别继续往上堆复杂因子。

## 12. 来源
1. **strebba (2026)**, `btc-institutional-flow` / `ibit-gamma-tracker`
   - Repo URL：<https://github.com/strebba/btc-institutional-flow>
   - 直接阅读材料：`README.md`, `docs/GEX.md`, `src/analytics/backtest.py`, `src/analytics/signal_model.py`, `docs/ANALYTICS.md`

2. **Pawel Lachowicz (2025)**, _Do Gamma Walls Actually Move Bitcoin Prices at Deribit?_
   - Venue：SSRN working paper
   - DOI：<https://doi.org/10.2139/ssrn.5782822>
   - Readable URL：<https://doi.org/10.2139/ssrn.5782822>

3. **Deribit Public API**
   - Docs / reference root：<https://docs.deribit.com/>
   - Public endpoints used in repo：`get_instruments`, `ticker`, `get_index_price`
