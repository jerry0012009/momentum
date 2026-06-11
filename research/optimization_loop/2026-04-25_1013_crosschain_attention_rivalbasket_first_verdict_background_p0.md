# bot3 auto：leader-chain attention shock -> rival-chain basket fade fresh intake first verdict

- 时间：2026-04-25 10:13 UTC
- 执行小点：cycle_plan item 2
- 对象：`research/quant_digests/2026-04-25_0924_crosschain-attention-rivalbasket-fade-alpha.md`
- verdict：`background/P0`

## 本轮只补的最小 decisive blocker

按 cycle plan，本轮只回答一个问题：`leader-chain attention shock -> rival-chain basket fade` 在统一 friction 下，是否仍保留一个**可独立交易**的 `1h parent -> 15m/5m child short-rivals` pocket，而不是只剩论文叙事与 `2h` rival basket 方向线索。

## 复核输入

直接复用已落库的最小 portability artifacts：

- `reports/artifacts/quant_digests/2026-04-19_crosschain_spillover_summary.csv`
- `reports/artifacts/quant_digests/2026-04-19_crosschain_negative_spillover_15m_summary.csv`
- `reports/artifacts/quant_digests/2026-04-19_crosschain_negative_spillover_15m_by_leader.csv`

对应口径：`ETH/SOL/BNB/ARB/AVAX` native-token proxies，`1h` parent leader shock，child 用 `15m` / `5m` rival-basket short；首轮成本口径按 digest 里写明的 taker `8bps` 单腿门槛。

## 最小 honesty 结果

### 1) 只有 `15m -> 2h` rival short 勉强留有薄边际，`5m` child 不成立

artifact 显示：

- `15m`, hold `8` (`2h`)：`rivals_short_alpha_bps = +8.2385bps`，`win = 57.29%`
- `5m`, hold `12` (`1h`)：`rivals_short_alpha_bps = -0.4409bps`
- `5m`, hold `24` (`2h`)：`rivals_short_alpha_bps = +0.2263bps`

这意味着：

- 若按单腿 taker `8bps` 作为最小成本门槛，则真正费后还能站住的只剩 `15m -> 2h` 这一个非常薄的 pocket，净边际约 **`+0.24bps/事件`**；
- cycle plan 要求的 `1h parent -> 15m/5m child short-rivals` 并没有在更细粒度 child 上形成可复用 pocket；`5m` child 基本为零或转负。

### 2) 结果不是被单一 `ARB` 热点样本完全主导，但明显依赖少数 leader regime

`15m` by-leader 切片：

- `ARBUSDT`: `n=205`, `ew4_rivals_short_2h = +2.50bps`
- `AVAXUSDT`: `n=194`, `ew4_rivals_short_2h = -1.83bps`
- `BNBUSDT`: `n=140`, `ew4_rivals_short_2h = +26.34bps`
- `ETHUSDT`: `n=168`, `ew4_rivals_short_2h = +13.32bps`
- `SOLUSDT`: `n=164`, `ew4_rivals_short_2h = +6.58bps`

结论不是“只靠 `ARB` 一个热点样本撑住”；相反，`ARB` 只给出弱正，真正抬高均值的是 `BNB/ETH` 两个 regime，而 `AVAX` 直接为负。也就是说，这条线更像**少数 leader regime 下的条件性 basket fade**，而不是一个统一可移植的 cross-chain relative-value pocket。

### 3) 真正更强的是 `weakest-rival short`，但那已经偏向 selection-heavy 单腿而不是 digest 目标的 basket fade

`15m` summary 里：

- `weakest_rival_short_2h_bps = +10.7685bps`
- `ew4_rivals_short_2h_bps = +8.2238bps`

`weakest rival` 看上去更好，但它依赖事后横截面选择最弱腿，语义上已经从 `rival basket fade` 滑向 selection-heavy 单腿 laggard short；而本轮 front-slot 要回答的是 **rival-chain basket** 是否能作为独立 intake 保留。对 basket 口径来说，费后只剩接近零的薄边际，不足以支撑 `keep_P1`。

## verdict

`leader-chain attention shock -> rival-chain basket fade` 在 native-token proxy 的最小 portability 里，确实留有方向性：`15m` child 下 rival basket 后续 `2h` 继续偏弱。但在统一 taker `8bps` 单腿门槛后，basket 费后净边际只剩约 `+0.24bps/事件`，`5m` child 不成立，且正收益明显集中在 `BNB/ETH` 少数 leader regime、`AVAX` 为负。因此它还不足以构成一个可独立交易、可复用的 `short-rivals basket` pocket；本轮 fresh intake first verdict 直接诚实收口为 `background/P0`，不分配 Rank，不进入 survivor。

## runtime 写回

- `Fresh intake slot.latest_result` 更新为本 verdict。
- `Fresh intake slot.current_target` 顺延到下一个 pending intake：`research/quant_digests/2026-04-24_0503_walkforward-halflife-pairs-shell-honest-oos.md`。
- `cycle_plan` item 2 改为 `done`，result 写成一句改变系统认知的话。