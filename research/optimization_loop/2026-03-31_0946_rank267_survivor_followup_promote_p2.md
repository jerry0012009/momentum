# Rank 267 survivor follow-up：最小 perp replication 后升入 P2

- 时间：2026-03-31 09:46 UTC
- 对象：Rank 267 / crypto factor momentum × size/vol rotation
- 任务类型：survivor 唯一一次 decisive follow-up
- 结论：`promote_P2`

## 本轮做了什么
按 cycle_plan 只做这一个 survivor follow-up，并把主语继续锁定为：
- `size sleeve`
- `low-vol sleeve`
- `short-horizon momentum sleeve`
- 以及 `sleeve-level winner rotation`

做了一个便宜但诚实的最小 replication：
- 市场：Binance USDⓈ-M perpetual
- universe：当前可交易且上市满 90 天、按 24h quote volume 取前 24 个 USDT perp
- bar：`4h`
- 样本：最近约 `700` 根 4h bar
- sleeve 排序 lookback：`24h / 72h / 7d`
- holding：`4h / 12h / 24h`
- 横截面分组：top/bottom `30%`
- 成本：统一按单边 `10 bps`，按换仓 overlap 近似扣减 turnover cost
- rotation：按三个 sleeves 自身过去 `1d / 3d / 5d` 的 realized long-short PnL，下一期只跟随最近最强 sleeve

原始结果落地：
- `reports/artifacts/rank267_survivor_followup_20260331/rank267_minimal_replication_summary.json`

## 最关键结果
### 1) 不是只有单一 momentum sleeve 活着
静态 sleeves 里，最强的是 short-horizon momentum；但不是唯一存活项：
- `momentum | 7d rank | 24h hold`：mean net ≈ `+94.26 bps/period`
- `momentum | 72h rank | 24h hold`：mean net ≈ `+89.33 bps/period`
- `size | 7d rank | 24h hold`：mean net ≈ `+50.06 bps/period`
- `low-vol` 不是前三，但在完整结果表里并非全面塌陷，因此这条线并未退化成“只有一个动量 sleeve 勉强活着”的伪 factor zoo

### 2) rotation 不只是装饰，最小版确实进一步增益
最佳 rotation 组合：
- `7d sleeve ranking + 24h hold + 1d sleeve-momentum rotation`
- mean net ≈ `+174.82 bps/period`
- hit rate ≈ `62.85%`
- pick counts：`momentum 334 / size 182 / lowvol 130`

这说明 rotation 不是只会反复选同一个 momentum sleeve；它确实会在不同阶段切到 `size / low-vol / momentum`，而且最小版 overlay 相对静态 sleeves 已出现明显增益。

## 为什么本轮给 promote_P2，而不是直接收口回 background
本轮要回答的是：在 Binance perp 现实 universe 与统一成本口径下，静态 sleeves 是否已有净边、rotation 是否真带来增益。

答案是：**是。**
- 静态层并非全灭，至少 `momentum` 与 `size` 已出现明显成本后净边；
- overlay 层并非空转，最小 rotation 的确比静态 sleeves 更强；
- 因此它已经超过 survivor 阶段“只停留在学术叙事”的门槛，值得进入 `Active P2`，做更正式的 admission。

## 但为什么只升 P2，不直接升 P3
这轮 replication 仍有明显诚实边界，够支持 `P1 -> P2`，还不够直接 paper launch：
1. universe 用的是**当前**高流动 perp 池，存在 survivorship / listing-selection 偏差；
2. `size` 代理暂时用的是 quote-volume/ADV 近似，不等于完整 cap / OI / float 定义；
3. beta-neutral / sector-neutral 还没做，当前只是 dollar-neutral long-short；
4. cost 只做了统一 turnover 近似，还没拆 maker/taker/slippage/funding；
5. rotation 用 realized trailing sleeve PnL 做切换，仍需补 time stability / parameter stability / honesty audit。

## P2 admission 下一步应回答什么
进入 P2 后，默认应尽快补 admission 五件套，而不是继续扩表：
1. `effectiveness / expected return`：统一 friction 后的净边是否还能站住；
2. `cross-asset stability`：是否只是少数 alt pocket 在抬结果；
3. `time stability`：分阶段/分 regime 后是否仍成立；
4. `parameter stability`：`24h/72h/7d`、`4h/12h/24h`、rotation `1d/3d/5d` 是否只是孤点；
5. `honesty / execution realism`：beta 中性、成分变动、上市/退市处理、可交易容量与更真实成本。

## 本轮出口句
`Rank 267：唯一 survivor follow-up 完成；在 Binance perp 当前高流动 universe、4h 横截面换仓与单边 10bps 成本下，short-horizon momentum 与 size sleeves 已出现明确净边，low-vol 未显示 fatal flaw，而基于 sleeve 自身近窗 PnL 的 winner rotation 进一步把最佳组合提升到约 +174.82 bps/period，因此该对象不再停留 P1，正式 promote_P2。`
