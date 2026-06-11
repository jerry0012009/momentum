# 别把 consolidation breakout 当多空对称：`close-range compression` 更像 breakout-short / Fib / EMA-PSAR 的 shared long-admission + short-veto gate
- 时间：2026-03-19 10:34 UTC
- 类型：GitHub + 快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/consolidation/breakout/asymmetry/long-admission/short-veto/repo/crypto/15m
- 证据类型：repo 代码规则（工程证据）+ 公开行情快检（待进一步 OOS）

## 1. 这次看了什么
这轮主看 **stockalgo/stolgo** 的 `Breakout` 实现（`lib/stolgo/breakout.py`），它把“先盘整再突破”写成非常明确的布尔规则：
- `is_consolidating`: 过去 N 根收盘价是否压在一个窄区间内；
- `is_breaking_out / is_breaking_down`: 先满足盘整，再由最后一根收盘价穿越前窗极值。

我额外做了一个 15m 快检（Binance 公共 K 线，BTC/ETH 各 1500 根）来确认它在我们 desk 三条收口线里更像哪种角色。

## 2. 核心结论
1. **一句话核心结论：** `stolgo` 这套“先盘整后突破”更像 **入场许可层（admission gate）**，而且在 15m 上呈现明显多空不对称——更适合当 long-continuation admission，不适合裸用作 short-continuation。
2. 代码里的核心定义非常干净（可直接复刻）：
   - 盘整判定：`min_close_N > max_close_N * (1 - pct)`（默认 `N=13, pct=2%`）
   - 向上突破：`consolidating(t-1) && close_t > max(close_{t-N..t-1})`
   - 向下突破：`consolidating(t-1) && close_t < min(close_{t-N..t-1})`
3. 15m 快检（horizon=4 bars）显示：
   - **BTC long**：从 baseline `win=44.5%, avg=-6.13bps`，到 `cons(2%)` 后 `win=46.8%, avg=-2.87bps`；
   - **BTC long（更紧 1%）**：`n=94, win=53.2%, avg=+3.23bps`（交易数下降但质量改善）；
   - **ETH long**：baseline `win=48.2%, avg=-1.86bps`，`cons(2%)` 后 `win=51.8%, avg=+6.37bps`。
4. 但 **short 侧并不对称**：BTC/ETH 的 `cons` short 在这次快检里平均 bps 多数更差（例如 BTC `-11.94bps`），说明它更像 short-veto 提示器，而不是 short 放大器。
5. **一句话证明方式：** 先用 repo 的布尔规则重建事件，再在公开 15m 行情上比较“裸突破 vs 盘整后突破”的事件分布、胜率与未来 4 根收益，直接看可交易统计差异。

## 3. 为什么和当前三条收口线有关
- **V3 final-verdict / breakout-short follow-up**：这条结论直接给 short 侧一个“别急着追”的证据——`consolidation breakdown` 在当前快检并不天然更优，优先当 **veto**。
- **Fibonacci confirmation / retest_hold**：可把 `consolidating` 作为 Fib 回踩前置条件（先确认市场在“压缩→释放”语境），减少把随机波动误判成“回踩守住”。
- **EMA / PSAR raw alpha focus**：EMA/PSAR 负责方向触发；`consolidation gate` 负责是否放行，形成 shared admission layer，先提升成本后存活率。

## 4. 下一步怎么测（5m/15m 最小实验）
### 4.1 数据与公开性
- 数据源：Binance 公共 OHLCV（`/api/v3/klines`，公开可得）
- 更新频率：5m / 15m
- 首轮样本：BTC/ETH/SOL，`180d IS + 60d OOS`

### 4.2 最小可复现实验口径
保持三条主策略触发不变，仅新增 `consolidation gate`：
- `gate_on = min_close_N > max_close_N*(1-pct)`，`N∈{13,21}`，`pct∈{0.8,1.0,1.2,1.5,2.0}`
- A 组：原策略（无 gate）
- B 组：仅 long 侧启用 gate（admission）
- C 组：short 侧启用 gate 但默认作为 veto（触发后减仓或不做）
- 统一执行冻结：`signal@close_t -> trade@open_{t+1}`，`no-overlap`，成本 `6/10/15 bps per side`

### 4.3 首轮判据
优先看三项：
1. `post_cost_expectancy`
2. `trade_count_retention`
3. `continuation_fail_ratio`（入场后 3~4 根内失效）

首轮过线建议（相对 A 组）：
- B 组 `post_cost_expectancy` 提升且 `trade_count_retention ≥ 45%`
- C 组若不能改善 expectancy，则 short 侧固定为 veto，不当独立放行条件

## 5. 风险与保留意见
- `stolgo` 的代码是规则骨架，不包含完整交易成本、撮合与资金管理模块；
- `N=13,pct=2%` 只是默认值，不是最优参数；
- 快检只覆盖近期样本与少数币种，结论必须经过 OOS + friction ladder 才能升格；
- `trend.py` 里的 `is_giant_uptrend/downtrend`（连续同色且单调 close）在 15m 上非常稀疏，不宜直接拿来做主过滤。

## 6. 来源
1. **stockalgo. (2020). _stolgo: Price Action Trading APIs_. GitHub.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/stockalgo/stolgo>
   - Repo URL: <https://github.com/stockalgo/stolgo>
2. **核心实现：`lib/stolgo/breakout.py`**
   - Readable URL: <https://github.com/stockalgo/stolgo/blob/master/lib/stolgo/breakout.py>
   - Raw URL: <https://raw.githubusercontent.com/stockalgo/stolgo/master/lib/stolgo/breakout.py>
3. **相关实现：`lib/stolgo/trend.py`**
   - Readable URL: <https://github.com/stockalgo/stolgo/blob/master/lib/stolgo/trend.py>
   - Raw URL: <https://raw.githubusercontent.com/stockalgo/stolgo/master/lib/stolgo/trend.py>
4. **公开行情接口（用于本次最小快检）**
   - Binance Spot Klines API: <https://api.binance.com/api/v3/klines>
