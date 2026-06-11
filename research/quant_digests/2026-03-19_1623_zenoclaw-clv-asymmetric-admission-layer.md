# 别把 `strong candle close` 当一句口号：`CLV(close-location value)` 更像 breakout-short / Fib / EMA-PSAR 的方向不对称 admission layer
- 时间：2026-03-19 16:23 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/clv/close-location-value/candle-quality/asymmetry/admission/filter/repo/crypto/15m
- 证据类型：repo 规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是一个很新的 15m 仓库：**zenoaiclawbot (2026) 的 `zenoclaw`**。它是个 BTC 15m breakout bot，但我没有照搬整套“突破 + 成交量 + 风险分级”，而是只抽它最值得我们 desk 先偷的一条旁支：

> repo 里的 `momentum_check()` 并不是抽象地说“强收盘”，而是直接把它写成 `pos = (close-low)/(high-low)`，并把 `pos >= 0.70` 当成可交易，`pos >= 0.50` 当成一般，低于此则视为 breakout quality poor。

也就是：**把“收盘站在整根 K 线的什么位置”规则化**。这比继续空喊“强势 candle / 弱势 candle”诚实得多，而且它正好击中我们三条收口线都反复遇到的同一个模糊位：**decision bar 到底要不要 close near the edge？**

## 2. 核心结论
1. **一句话核心结论**：`CLV` 值得测，但不要当成多空对称、处处通用的万能过滤——在当前 15m 代理口径里，它**对 short follow-up 更有用**，对 long continuation 单独使用反而不够好。  
2. **一句话证明方式**：复用公开 Binance Futures `BTC/ETH/SOL 120d 15m`，统一 `20-bar breakout → next-bar open → hold 4 bars → round-trip 12bps`，比较 `baseline / CLV>=0.70 / CLV>=0.80 / volume>=1.5 / CLV+volume`。  
3. 关键数据（跨 BTC/ETH/SOL 平均）：
   - **short baseline**：`mean_net_ret_h4 = -5.89 bps`；加 `CLV>=0.70` 后升到 `-2.36 bps`，保留率 `68.4%`；再收紧到 `CLV>=0.80`，升到 `-0.43 bps`，保留率 `49.3%`。
   - **short 的 volume>=1.5 单独作用不大**：只从 `-5.89 bps` 改到 `-4.85 bps`；但和 `CLV>=0.70` 叠加后可到 `-1.21 bps`，且 `positive_asset_ratio = 2/3`。
   - **long 侧相反**：baseline `-12.61 bps`，`CLV>=0.70` 反而变差到 `-13.97 bps`；long 真正有帮助的是 `volume>=1.5`（到 `-9.98 bps`），说明长侧不能把“靠近 bar 高点收盘”单独误读成 continuation 充分条件。

## 3. 为什么它直接服务当前三条收口线
- **V3 final-verdict / breakout-short follow-up（最直接）**：这轮其实在回答一个很具体的问题——post-break 那根决策 bar，是否必须“收在靠近低点的位置”才能继续相信 short follow-up。当前证据是：**值得优先把 strict CLV 放到 short 侧 admission**。  
- **Fibonacci confirmation / retest_hold**：Fib 的 reclaim / hold bar 也常被写成“收回去了就行”，但这轮提醒我们：长侧不能只看 close near high，最好和 `volume / acceptance / reclaim context` 绑一起，而不是单开 `CLV` 开关。  
- **EMA / PSAR raw alpha focus**：对 EMA continuation，`strong close` 更适合作为**和 volume 联动的 bar-quality 子项**，不适合单独升格为 long raw-alpha 核心 gate。  

如果问“为什么这题比继续做旧派生假设更值”：因为它来自**fresh 15m-native repo**，而且它解决的是三线共用的一个基础语义问题——**‘强 K 线’到底怎么量化**。

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：`zenoclaw` 仓库规则 + Binance Futures 公共 K 线 API  
- 公开性：公开可得  
- 更新频率：15m（下一轮可镜像到 5m 执行）  
- 本轮产物：
  - `reports/artifacts/quant_digests/zenoclaw_clv_proxy/asset_summary.csv`
  - `reports/artifacts/quant_digests/zenoclaw_clv_proxy/overall_summary.csv`
  - `reports/artifacts/quant_digests/zenoclaw_clv_proxy/event_log.csv`
  - `reports/artifacts/quant_digests/zenoclaw_clv_proxy/summary_snapshot.json`

### 4.2 最小可复现实验口径（建议先做这个）
不要把 `CLV` 当全局统一阈值，直接做**方向分拆**：
1. **breakout-short follow-up**：在当前 `V3 follow-up / final verdict` 上新增 `aligned_clv_short >= 0.75 / 0.80` 两档，对比 `no CLV / CLV-only / CLV+volume`；
2. **Fib retest_hold long**：不要先上 `CLV-only`，而是只测 `reclaim + volume + CLV` 组合臂，看它是否优于 `reclaim + volume`；
3. **EMA / PSAR long continuation**：把 `CLV` 降级成 admission score 里的一个子项（例如 25 分里的 5~10 分），不要单独 hard gate。

先看 4 个指标：
- `post_cost_expectancy`
- `trade_count_retention`
- `flip_to_fail_3bars_rate`
- `median_fwd4_ret`

## 5. 风险与保留意见
- 源 repo 是单仓库工程实现，不是学术论文；证据强度来自“规则清楚 + 可快速代理验证”，不是跨市场正式统计检验。  
- 本轮快检用的是 `20-bar breakout` 代理，不是你当前三条线的原始信号本体；因此结论是**bar-quality 层启发**，不是最终策略 verdict。  
- `CLV` 和此前的 `body-vs-wick` 有相邻性，但不完全相同：前者看**收盘落点**，后者看**实体/影线结构**；下一轮最好把二者并排测，避免重复加同一信息。  
- 当前数据更像在说“short 侧值得更严格，long 侧要配 volume/context”，不是在说 `CLV` 本身已经证明可单独赚钱。

## 6. 来源
1. **zenoaiclawbot. (2026). _zenoclaw_.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/zenoaiclawbot/zenoclaw>
   - Repo URL: <https://github.com/zenoaiclawbot/zenoclaw>
2. **核心源码**：`zenoclaw_bot.py`
   - 关键规则：`momentum_check()` 中 `pos = (close-low)/(high-low)`；`pos >= 0.70` 视为 strong close above resistance，`pos >= 0.50` 视为 moderate close
   - Readable URL: <https://github.com/zenoaiclawbot/zenoclaw/blob/main/zenoclaw_bot.py>
   - Raw URL: <https://raw.githubusercontent.com/zenoaiclawbot/zenoclaw/main/zenoclaw_bot.py>
3. **仓库元数据（创建/更新时间）**
   - URL: <https://api.github.com/repos/zenoaiclawbot/zenoclaw>
4. **公开行情数据源**
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>
