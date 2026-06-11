# Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade — survivor follow-up promote_P2

## 本轮执行小点
- target: `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`
- action: survivor 唯一 follow-up，只补 `formal pair admission / break-risk` 这一个最小 honesty blocker
- verdict: `promote_P2`

## 结论
`Rank 424` 的 survivor 唯一 follow-up 已经回答 pair-admission / break-risk blocker：`SOL/LTC` 在所有月份与前后半样本下都保住 `12-bar (~3h)` after-cost 净边，`LINK/AVAX` 仍是可保留的次级 pair，而 `LINK/LTC` 已显著衰减、不能再作为核心依据；因此这不是单一 pair 幻觉，也不是可以直接丢弃的 P1，最诚实动作是升入 `Active P2`，后续 P2 admission 应围绕 `SOL/LTC core + LINK/AVAX secondary, LINK/LTC watch/exclude` 的正式 live spec 与 execution realism 收口。

## 最小证据
基于既有 artifact：
- `reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_router_15m.csv`
- `reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_summary.json`

### 1) strongest router 总体仍保住 after-cost pocket
- `n=1528`
- `12 bars (~3h)` gross mean `+23.69bps`
- 扣双腿 round-trip：
  - `net@12bps = +11.69bps`
  - `net@16bps = +7.69bps`

### 2) pair-level admission / break-risk 切片
- `SOLUSDT/LTCUSDT`：`n=458`，`12-bar gross=+37.38bps`，`net@12=+25.38bps`，`net@16=+21.38bps`；Feb/Mar/Apr 均为正，前后半样本 `net@12=+37.29/+13.47bps`，是当前唯一稳定核心。
- `LINKUSDT/AVAXUSDT`：`n=554`，`12-bar gross=+18.38bps`，`net@12=+6.38bps`，`net@16=+2.38bps`；后半样本仍为 `net@12=+2.97bps`，但 Apr 已转薄，适合作为 secondary，而非核心。
- `LINKUSDT/LTCUSDT`：`n=516`，全样本仍为 `net@12=+5.25bps`，但后半样本 `net@12=-16.04bps`、Apr `net@12=-5.77bps`，说明该 pair 已出现 regime-break 风险，不能支撑 P2 核心。

## 为什么升 P2，而不是 background/P0
本轮唯一 follow-up 的问题不是再重复 friction ladder，而是正式 pair admission / break-risk 是否把 P1 打穿。结果显示：
1. 当前 edge 已从“三组 pair 等权可信”收窄为 `SOL/LTC core + LINK/AVAX secondary + LINK/LTC watch/exclude`；
2. `SOL/LTC` 的时间切片稳定性足够强，不是单日或单月孤例；
3. `LINK/AVAX` 仍提供第二条非单一 pair 证据；
4. `LINK/LTC` 的衰减是 P2 admission 要处理的 scope 风险，不是整个对象的 fatal flaw。

因此 survivor 预算耗尽后不应收口 P0；它已经足够进入 `P2 / pre-paper`，但不能直接 P3，因为正式 live spec 仍需在 P2 内闭合 pair universe、剔除规则、execution/slippage 与 stale-pair veto。

## 对 runtime 的影响
- `Rank 424` 从 `Surviving candidate slot` 升入 `Active P2 slot`。
- `Surviving candidate slot` 清空，follow-up 预算归零。
- `cycle_plan` 第 2 项写为 done。
- 下一步若 bot2 排班，应优先安排 `Rank 424` 的 P2 admission / exit decision，而不是继续把它当作 fresh/survivor。
