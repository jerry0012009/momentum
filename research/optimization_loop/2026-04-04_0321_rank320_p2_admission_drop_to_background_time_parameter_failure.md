# Rank 320 — P2 admission（time stability + parameter stability）：drop_to_background/P0

- Time: 2026-04-04 03:21 UTC
- Target: `Rank 320 / Wilder RSI breakout × EMA200/ADX/volume allow × fast RSI-45 exit`
- Action type: `Active P2` admission step 2
- Verdict: `drop_to_background/P0`

## 结论
`Rank 320` 在上一轮通过了 `honesty / execution realism + post-cost effectiveness`，但一旦把同一套 fast-exit shell 拉到更长时间窗，并同时检查邻近 `entry / exit` 扰动，结论就不再是“还有待收口的 P2”，而是更直接的 **时间/参数不稳定**：此前在 `2026-01-01 ~ 2026-04-03` 里看起来站得住的 `BTC/ETH/SOL × 5m/15m` best path，放到 `2025-01-01 ~ 2026-04-04` 后六条主腿全部转负，且邻近阈值也没有出现任何能把对象诚实救回来的单一稳健 lane。因此这一步应直接把对象从 `Active P2` 收口到 `background/P0`，而不是再给第三次开放式 `keep_P2`，也不存在值得保留的一次性 `P2->P1 re-scope`。

## 本轮怎么做的
为了避免重复上一轮已做过的 `honesty/post-cost` 轴，本轮只回答 policy 指定的剩余 admission 维度：`time stability + parameter stability`。

使用本地已有长期 perp cache：
- `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/exec_cache/{BTC,ETH,SOL}USDT__1825d__5m__perp.csv`
- `reports/artifacts/scout_rank32b_slope_floor_continuation_15m/perp_cache/{BTC,ETH,SOL}USDT__1825d__15m__perp.csv`

按与前两轮一致的 proxy 壳重跑：
- entry: `Wilder RSI breakout + close > EMA200 + ADX > 20 + volume > SMA20`
- bull regime: `close > EMA200 且 ADX > 25` 时把 `entry_base` 下调 5 点
- exit: `ATR trail 4x` + `RSI fast exit`
- cost: `10bps fee + 5bps slippage + scaled funding`

本轮新 artifact：
- `reports/artifacts/optimization_loop/2026-04-04_rank320_time_parameter_stability.csv`

检验口径：
1. **时间稳定性**：把样本从原先的 `2026-01-01 ~ 2026-04-03` 拉长到 `2025-01-01 ~ 2026-04-04`，并拆出 `2025` 与 `2026 YTD` 两段；
2. **参数稳定性**：围绕当前 admission best path，只看邻近 `entry_base ∈ {base-3, base-2, base, base+2, base+3}` 与 `exit_th ∈ {43,45,47}`，判断是不是只有一个幸运尖点为正。

## 结果
### 1) 原先六条主 admission 路径在长窗里全部转负
#### 5m
- `BTC 5m, entry 62 / exit 45`
  - `2025-01-01 ~ 2026-04-04`: total return `-87.4%`, PF `0.36`, trades `709`, max DD `-87.4%`
  - `2025`: `-82.8%`, PF `0.33`
  - `2026 YTD`: `-26.1%`, PF `0.47`
- `ETH 5m, entry 58 / exit 45`
  - 长窗: `-76.2%`, PF `0.60`, trades `635`, max DD `-79.4%`
  - `2025`: `-72.7%`, PF `0.56`
  - `2026 YTD`: `-12.4%`, PF `0.79`
- `SOL 5m, entry 58 / exit 45`
  - 长窗: `-81.1%`, PF `0.52`, trades `578`, max DD `-82.4%`
  - `2025`: `-76.2%`, PF `0.49`
  - `2026 YTD`: `-19.8%`, PF `0.63`

#### 15m
- `BTC 15m, entry 55 / exit 45`
  - 长窗: `-32.7%`, PF `0.65`, trades `201`, max DD `-36.2%`
  - `2025`: `-17.5%`, PF `0.77`
  - `2026 YTD`: `-18.7%`, PF `0.30`
- `ETH 15m, entry 60 / exit 45`
  - 长窗: `-32.4%`, PF `0.84`, trades `238`, max DD `-46.6%`
  - `2025`: `-25.4%`, PF `0.86`
  - `2026 YTD`: `-11.1%`, PF `0.73`
- `SOL 15m, entry 65 / exit 45`
  - 长窗: `-29.6%`, PF `0.88`, trades `253`, max DD `-45.1%`
  - `2025`: `-29.8%`, PF `0.85`
  - `2026 YTD`: `-2.8%`, PF `0.95`

这不是“强腿变弱一点”的图景，而是 **六条主腿全部失去正 expectancy**。换句话说，上一轮看到的 admission 更像最近窗口里的局部 lucky hit，而不是可跨时间保留的稳定 shell。

### 2) 邻近参数扰动也没有救回来，说明不是单一阈值写错
围绕 base path 做的小扰动里：
- `BTC 5m` 最好的邻近组合也只有 `entry 59 / exit 43`，长窗仍是 `-80.9%`, PF `0.39`
- `ETH 5m` 最好的邻近组合是 `entry 58 / exit 43`，长窗仍是 `-74.3%`, PF `0.62`
- `SOL 5m` 最好的邻近组合是 `entry 55 / exit 43`，长窗仍是 `-70.5%`, PF `0.63`
- `BTC 15m` base 自己就是最优邻近点，但仍是 `-32.7%`, PF `0.65`
- `ETH 15m` 最好的邻近组合是 `entry 63 / exit 43`，长窗仍是 `-21.3%`, PF `0.93`
- `SOL 15m` 最好的邻近组合是 `entry 65 / exit 43`，长窗仍是 `-28.5%`, PF `0.89`

因此这不是“只差把 exit 45 改成 43 就能稳定”的问题；参数面上没有出现一条清楚、唯一、可诚实复用的 re-spec 方向。

## 为什么这一步不是 one-time P2->P1 re-scope
Policy 允许 `P2->P1` 仅在存在**唯一明确** re-scope 方向时发生，比如明确改成某个资产子集、某个 regime、某个 entry/exit 结构。

本轮没有出现这种形状：
- 不是只有 `BTC 5m` 坏、`ETH/SOL 15m` 好；而是六条主腿一起翻负；
- 不是 exit 45 坏、exit 43 稳；而是邻近参数也普遍为负；
- 不是 `2025` 坏但 `2026` 明显厚到足以单独成 spec；`2026 YTD` 也多数仍负，只有 `SOL 15m` 接近打平。

所以此刻若硬写 `P2->P1 re-scope`，本质上只是“再看看能不能挑一条没那么差的腿”，不符合 policy 对唯一明确 re-spec 的要求。

## 为什么这一步也不能 keep_P2
`Active P2` 目前已出现过一次 `keep_P2`，policy 明确禁止把这种对象拖成第三次开放式 `keep_P2`。更重要的是，本轮已经得到足以改变层级的 admission 结论：

> 长窗稳定性失败，参数邻近也未出现能救活的唯一稳健 lane。

这就是一个应该直接收口成出口决策的结果，而不是继续开放研究。

## 本轮写回 runtime 的系统认知变化
- `Rank 320` 不再是当前唯一 `Active P2`；
- 系统不应再把它视为“离 P3 最近的 short-cycle trend continuation 壳”；
- 对这条 Wilder RSI fast-exit 线，当前更诚实的结论是：**recent-window admission 成立，但跨时间/参数不稳定，因此收口到 background/P0**。

## Reader-facing 一句话
`Rank 320` 通过了执行诚实性那一关，却没通过更关键的长窗稳定性：把样本拉到 `2025~2026` 并看邻近参数后，原先 `BTC/ETH/SOL × 5m/15m` 的六条主腿全部转负，因此本轮直接从 `Active P2` 收口到 `background/P0`。