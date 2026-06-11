# Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade — P2 exit promote_P3

## 本轮执行小点
- target: `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`
- action: `P2 admission / exit decision`，只做 `pair stale-break × slippage-realism` 合并出口判定
- verdict: `promote_P3`

## 结论
`Rank 424` 已足够进入 `P3 / Paper launch queue`：排除已衰减的 `LINK/LTC` 后，`SOL/LTC` core 在统一双腿 round-trip `16bps` 与月份/前后半样本切片下仍保住可复制净边；`LINK/AVAX` 只保留为 secondary/watch，不作为 paper 核心；5m child probe 为负不是把它打回 P1/P0 的致命 blocker，而是要求首版 paper runner 采用 `15m bar-close / fixed time-stop` 的保守接线，不继续开放式停留在 P2。

## 最小证据
使用既有 artifacts：
- `reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_router_15m.csv`
- `reports/artifacts/quant_digests/2026-04-19_cointegration_pairs_probe_summary.json`

### 1) 排除 stale pair 后，core+secondary 仍正
对 `SOL/LTC + LINK/AVAX` 组合：
- `n=1012`
- `12-bar gross mean = +26.98bps`
- `net@12bps = +14.98bps`
- `net@16bps = +10.98bps`
- `net@20bps = +6.98bps`
- `net@24bps = +2.98bps`

月度 / 半样本：
- Feb：`gross +45.34bps / net@16 +29.34bps`
- Mar：`gross +26.14bps / net@16 +10.14bps`
- Apr：`gross +19.65bps / net@16 +3.65bps`
- first half：`gross +37.65bps / net@16 +21.65bps`
- second half：`gross +17.95bps / net@16 +1.95bps`

这说明 `LINK/LTC` 的 stale-break 可以通过 scope 排除处理，不构成全策略 fatal flaw。

### 2) `SOL/LTC` core 单独足够厚
`SOL/LTC`：
- `n=458`
- `12-bar gross mean = +37.38bps`
- `net@16bps = +21.38bps`
- `net@20bps = +17.38bps`
- `net@24bps = +13.38bps`

月份 / 半样本：
- Feb：`net@16 +26.42bps`
- Mar：`net@16 +20.32bps`
- Apr：`net@16 +20.36bps`
- first half：`net@16 +40.26bps`
- second half：`net@16 +6.48bps`

这是本轮 promotion 的主证据：core pair 未被 stale-break 打穿。

### 3) `LINK/AVAX` 只能 secondary/watch
`LINK/AVAX`：
- `n=554`
- `12-bar gross mean = +18.38bps`
- `net@16bps = +2.38bps`
- `net@20bps = -1.62bps`
- Apr `net@16 = -6.01bps`
- second half `net@16 = -2.03bps`

因此它不应作为 paper 核心，只能作为 secondary/watch 或后续 offload runner 的低权重旁路。

### 4) 5m child execution 为负，约束接线方式但不是否决
summary 中 5m child 口径：
- pair events `ret5_12 mean = -1.63bps`
- strongest router `ret5_12 mean = -0.83bps`

这说明“用 5m child entry 改善执行”暂时不成立；但 P2 出口问题是是否存在单一致命 blocker。由于 `SOL/LTC` 在 `15m / 12-bar` bar-close time-stop 口径下仍有足够费后余量，最诚实动作不是继续 `keep_P2`，而是升级到 P3，并把首版 runner 的执行假设写窄为：
- universe/core：`SOLUSDT/LTCUSDT`
- secondary/watch：`LINKUSDT/AVAXUSDT`
- exclude：`LINKUSDT/LTCUSDT`
- execution：15m bar-close / next-bar conservative paper fill，不启用 5m child entry 作为 alpha 改善项
- exit：fixed `12 bar (~3h)` time-stop

## 对 runtime 的影响
- `Paper launch queue.current_target` 写为 `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`。
- `Active P2 slot` 清空为 `none`。
- `cycle_plan` 第 1 项写为 `done`，结果为 `promote_P3`。
- 下一轮合法前排动作应优先对 `Rank 424` 做 `P3 launch wiring`：dedicated runner script + scheduler + first verified run，而不是继续做开放式 P2 研究。
