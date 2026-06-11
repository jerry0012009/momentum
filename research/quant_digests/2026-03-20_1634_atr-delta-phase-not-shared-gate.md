# 别把 ATR 变化方向硬写成 shared gate：`signal→confirm ATR delta` 在 15m 上呈 setup 分裂，更适合分线收口
- 时间：2026-03-20 16:34 UTC
- 类型：GitHub 仓库 + 本地公共数据代理快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/atr/delta/volatility-phase/continuation/failure/filter/repo/crypto/15m
- 证据类型：仓库代码（工程证据）+ 本地 15m 代理事件快检

## 1. 这次看了什么
这轮继续读近 5 年新仓库 **ilahuerta-IA/backtrader-pullback-window-xauusd（2025）**，但不重复它的“4 阶段状态机”headline，而是只拎一个更适合当前三条收口线的旁支：

- 在 `sunrise_ogle_xauusd.py` 里，ATR 不是只在入场点看一次，而是拆成了**两段**：
  1) signal 阶段 ATR 区间过滤；
  2) pullback→breakout 阶段再看 ATR increment/decrement（波动是扩张还是收敛）。
- 这比“ATR 只做静态阈值”更像 desk 现在真缺的东西：**确认阶段的质量判别**。

我先用该仓库自报统计做外部证据，再用本地 `BTC/ETH/SOL 15m` 代理事件（3 条 setup）做最小切片，检查 `ATR delta` 是否能 shared。

## 2. 核心结论
- **一句话核心结论：** `ATR delta` 有信息，但**不是 shared 同一把尺**；它在三条线上的方向相反，应该先做“分 setup gate”，而不是一刀切。
- **一句话证明方式：** 仓库给了可执行的 ATR 两段过滤代码与分桶统计；我再在本地 15m 事件上按 `atr_delta1` 三分位做对照，比较 4-bar 成本后 signed return 与胜率。

关键数据点：
1. **仓库自报结果提示“确认段优于快进段”**：`Window Breakout` 162 笔，胜率 **56.2%**、均值 **+267.45**；`Quick Entry` 13 笔，胜率 **46.2%**、均值 **+89.12**。说明“等确认+看阶段波动”不是空话。  
2. **breakout_short 不支持“越扩张越好”**（本地代理，6bps/side）：`mid ATR delta` 组均值约 **-10.85 bps**，优于 `contracting -25.23` 与 `expanding -18.84`。  
3. **Fib 与 EMA/PSAR 对 ATR delta 的偏好相反**：`fib_retest_long` 的 `expanding` 组约 **+25.52 bps**（最好），但 `ema_psar_long` 的 `expanding` 组约 **-41.09 bps**（最差），其 `mid` 组约 **+5.15 bps**。

## 3. 为什么和当前三条收口线有关
- **V3 final-verdict / breakout-short follow-up**：更像要避开 ATR delta 两端（过冷/过热），优先保留中段 re-arm。  
- **Fibonacci confirmation / retest_hold**：反而可能需要“有一点重新扩张”才更像真 hold 后再发动。  
- **EMA / PSAR raw alpha focus**：最怕追在 ATR 突扩张段；这条线更像应先做 expansion veto。

=> 结论不是“ATR 没用”，而是**ATR delta 的角色必须 setup-specific**。

## 4. 最值得复用/复现的点
1. **两段 ATR 读法**：`signal ATR range` + `confirm ATR delta`（而非单点阈值）。  
2. **把 ATR delta 下沉到确认/否决层**：不替代方向信号，只判“这枪值不值得打”。  
3. **先分线后共享**：先各线找有效相位，再考虑有没有 shared 区间。

## 5. 这轮最小代理快检口径
- 数据：项目内已有 `BTC/ETH/SOL` 15m feature frame（公共交易所行情缓存）  
- 事件：`breakout_short` / `fib_retest_long` / `ema_psar_long`  
- 执行：`signal 当根及之前数据 + next-bar open + hold 4 bars`  
- 成本：`6 bps/side`（round-trip 12 bps）  
- 分组：每个 setup 内按 `atr_delta1 = ATR14_t / ATR14_{t-1} - 1` 做三分位（contracting / mid / expanding）

## 6. 下一步怎么测（最小可复现实验）
### 研究假设
`ATR delta` 只能先作为 **setup-specific confirmation/veto** 成立；shared 单阈值大概率会把至少一条线搞坏。

### 第一轮 ablation（直接可跑）
对每条线各跑 3 臂：
1. `baseline`（不加 ATR delta）
2. `shared_gate`（三条线同一 ATR delta 规则）
3. `setup_specific_gate`（分线规则）

建议先验分线规则：
- breakout_short：仅保留 `mid` 分位；
- fib_retest_long：仅保留 `expanding` 分位；
- ema_psar_long：否决 `expanding` 分位。

### 最小回测切口
- 资产：BTC/ETH/SOL perpetual
- 周期：15m（可选 5m 执行层二轮再加）
- 执行：next-bar open、no-overlap
- 成本：6 / 10 / 15 bps per side

### 先看 3 个指标
1. `post-cost expectancy`
2. `trade_count_retention`
3. `false-follow / 4-bar failure rate`

## 7. 风险与保留意见
- 仓库绩效为作者自报，且标的是 XAUUSD，不可直接外推到 crypto；
- 本地仅是代理事件快检（4-bar 持有），不是完整策略回测；
- 当前样本规模不大，且时间窗口偏近，需补 rolling OOS 与时段切片；
- 因此这轮应定性为：**P1/P2 之间的可执行候选**，不是可部署结论。

## 8. 来源
1. **ilahuerta-IA. (2025). _backtrader-pullback-window-xauusd_. GitHub repository.**  
   - Authors: ilahuerta-IA  
   - Year: 2025  
   - Title: Backtrader Gold (XAU/USD) Pullback Window Strategy  
   - Venue: GitHub  
   - DOI: `N/A`  
   - Readable URL: `https://github.com/ilahuerta-IA/backtrader-pullback-window-xauusd`  
   - Repo URL: `https://github.com/ilahuerta-IA/backtrader-pullback-window-xauusd`  
   - Key code: `https://github.com/ilahuerta-IA/backtrader-pullback-window-xauusd/blob/main/src/strategy/sunrise_ogle_xauusd.py`

2. **ilahuerta-IA. (2025). _PERFORMANCE_METRICS.md_ (project report).**  
   - Authors: ilahuerta-IA  
   - Year: 2025  
   - Title: Performance Metrics - Detailed Analysis  
   - Venue: GitHub repository document  
   - DOI: `N/A`  
   - Readable URL: `https://github.com/ilahuerta-IA/backtrader-pullback-window-xauusd/blob/main/PERFORMANCE_METRICS.md`  
   - Repo URL: `https://github.com/ilahuerta-IA/backtrader-pullback-window-xauusd`

---
快检文件：
- `reports/artifacts/literature/atr-delta-signal-proxy_events_2026-03-20.csv`
- `reports/artifacts/literature/atr-delta-signal-proxy_summary_2026-03-20.csv`
- `reports/artifacts/literature/atr-delta-signal-proxy_setup_2026-03-20.csv`
