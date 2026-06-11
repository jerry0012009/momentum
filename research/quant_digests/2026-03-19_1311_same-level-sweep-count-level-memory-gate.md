# 别把第二次 sweep 当成第一根 wick 的复读：`same-level consecutive sweep count` 更像 breakout-short / Fib / EMA-PSAR 的 level-memory gate
- 时间：2026-03-19 13:11 UTC
- 类型：GitHub + 本地代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/liquidity-sweep/consecutive-sweep/same-level/level-memory/continuation/failure/filter/repo/crypto/15m
- 证据类型：repo 代码规则（工程证据）+ 公开行情代理快检

## 1. 这次看了什么
这轮看的是 **Capital41 / damianpitt (2026) 的 `capital41-indicators`**，重点不是整套指标库，而是其中 `Capital41 Liquidity Sweep Simple` 里那条很适合当前 desk 的旁支：
**不要只看“有没有一根 sweep”，还要记这个 level 在最近几根里是不是已经被 sweep 过一次。**

仓库里的实现是显式写出来的：
- 先找 `lookback=20` 的前高/前低；
- 只有 `break level -> close back inside range` 且 `volume >= 1.2x volume SMA` 才算有效 sweep；
- 若新 sweep 与上一次 sweep 处在“近似同一价位”（脚本默认 `0.5%` 容差）且间隔不超过 `10` 根 bar，就把它记成 `consecutive sweep`；
- `consec >= 2` 时单独标成 `high-prob`。

## 2. 核心结论
1. **一句话核心结论**：对 15m 来说，`same-level consecutive sweep count` 更像在量化“这个价位到底是被防守，还是还在随机扫流动性”，它适合做 **level-memory gate**，不是单独抬收益的主 alpha。
2. **一句话证明方式**：repo 把“同价位二次 sweep”写成了明确状态机；我再用 Binance Futures 公开 15m K 线（BTC/ETH/SOL，各 1500 bars）做代理快检，看 `单次 sweep` 和 `连续同价位 sweep` 的 4-bar 后路径有没有差异。
3. 聚合结果（bull side，对 Fib retest / EMA hold 更直接）：
   - `hold4`：**18.9% -> 27.3%**（`single n=74` -> `consec2+ n=22`）
   - `win4`：**44.6% -> 63.6%**
   - 但 `mean_ret4` 仍接近 0，说明它更像 **防守质量标签**，不是裸 long 加速器。
4. 聚合结果（bear side，对 breakout-short follow-up 更直接）：
   - `hold4`：**28.2% -> 32.1%**（`single n=103` -> `consec2+ n=53`）
   - `win4`：**41.7% -> 58.5%**
   - `mean 4-bar short proxy return`：**-0.18% -> +0.07%**
5. 更直白地说：**单根 wick/body 已经回答“这一根像不像拒绝”；连续同价位 sweep 在回答“这个 level 过去几根有没有记忆”。** 这正好是当前三条收口线还缺的那一层。

## 3. 为什么和当前三条收口线直接相关
- **V3 final-verdict / breakout-short follow-up**：若下破后不久，支撑附近出现 `bullish same-level sweep >= 2`，那更像“下面有人连续接”，不该把 short continuation 当默认延伸；反过来，顶部 `bearish same-level sweep >= 2` 才更像可继续 follow-up 的 pressure memory。
- **Fibonacci confirmation / retest_hold**：Fib 回踩最怕“第一次碰位看着像守住，第二次又被轻松扫穿”。`same-level bull sweep count` 刚好在量化“0.5 / 0.618 附近到底是真防守，还是反复流动性清扫”。
- **EMA / PSAR raw alpha focus**：EMA/PSAR 继续负责方向；这层只负责告诉我们：**当前这个回踩/翻面附近的价位，有没有被市场连续 defend/reject。**

## 4. 下一步怎么测（5m / 15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance Futures 公共 K 线（`/fapi/v1/klines`）
- 公开性：公开可得
- 更新频率：5m / 15m
- 本轮代理快检产物：
  - `reports/artifacts/quant_digests/2026-03-19_same_level_sweep_count_proxy_events.csv`
  - `reports/artifacts/quant_digests/2026-03-19_same_level_sweep_count_proxy_summary.csv`
  - `reports/artifacts/quant_digests/2026-03-19_same_level_sweep_count_proxy_summary.json`

### 4.2 最小可复现实验口径（建议）
把三条 archetype 都接一层同样的 `level-memory gate`：
1. 先按现有逻辑生成基础触发（`breakout_short` / `fib_retest_long` / `ema_psar_long`）；
2. 在信号 bar 及前 `10` 根 15m 内，统计与候选 level 对齐的 `same-level sweep count`：
   - bull gate：`low < priorLow && close >= priorLow && vol_ratio >= 1.2`
   - bear gate：`high > priorHigh && close <= priorHigh && vol_ratio >= 1.2`
   - level 对齐：`abs(level_now - level_prev) <= 0.5% * close`
3. 先做 4 臂：
   - A：baseline
   - B：只看 `single sweep`
   - C：`consec2+`（本轮主张）
   - D：`consec2+` 再叠加已有 `body-vs-wick` 或 `small-body retest` 规则
4. 统一执行：`next-bar open + no-overlap + hold 8 bars + 6/10/15 bps per side`。

先看 4 项：`post_cost_expectancy`、`hold4 / false_break_ratio`、`trade_count_retention`、`time-pocket stability`。

## 5. 风险与保留意见
- 原 repo 的默认语境是 **30m / 4h + BTC / 美股**，不是现成的 crypto 15m 成品模板；
- 本轮快检是事件级代理，不是完整策略回测；
- `consec2+` 样本比 `single` 少，说明它更像“严 admission / veto”，不是高频触发器；
- bull 侧虽然 `hold4/win4` 变好，但均值收益没同步抬升，意味着它更像 **守位质量过滤器**，不能被误读成单独 alpha；
- 若后续只在单一 archetype 生效，就应把它降级为 **专属 gate**，不要硬写成三线共用真理。

## 6. 来源
1. **damianpitt / Capital41. (2026). _capital41-indicators_.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/damianpitt/capital41-indicators>
   - Repo URL: <https://github.com/damianpitt/capital41-indicators>
2. **关键实现：`Capital41_Liquidity_Sweep/Capital41_Liquidity_Sweep_Simple.pine`**
   - Readable URL: <https://github.com/damianpitt/capital41-indicators/blob/main/Capital41_Liquidity_Sweep/Capital41_Liquidity_Sweep_Simple.pine>
   - Raw URL: <https://raw.githubusercontent.com/damianpitt/capital41-indicators/main/Capital41_Liquidity_Sweep/Capital41_Liquidity_Sweep_Simple.pine>
   - 关键规则：`close back inside range + volume ratio filter + consecutive same-level sweep tracking`
3. **说明文档：`README.md`**
   - Readable URL: <https://github.com/damianpitt/capital41-indicators/blob/main/README.md>
4. **公开行情数据源**
   - Binance Futures Klines API: <https://fapi.binance.com/fapi/v1/klines>
