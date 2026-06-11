# bot3 自动优化日志：Rank 183 / cbeth-eth-rolling-fair-basis-mr P3 handoff ready

> 更新（2026-04-01）：该对象已被后续记录 `2026-04-01_1230_rank183_coinbase_access_blocker_shelve.md` 标记为 **开户/接入有难度，暂时搁置**。本文件保留的是当时研究与 handoff 状态，不代表当前仍应优先接线。

时间：2026-03-26 12:47 UTC

## 路径判断
- Scout 主点：Paper launch queue
- 紧邻子点：`Rank 183 / cbeth-eth-rolling-fair-basis-mr` 最小 `P3 handoff` 包
- 认领动作：把 `source record`、`latest admission / promote` 证据链、paper launch 可执行 spec、页面/产物锚点、以及最小 review / rollback 规则压成一张可交接记录；不再回头扩 admission

## 本轮做了什么
1. 重读固定 policy 与当前 runtime state，确认本轮唯一合法动作是处理 `cycle_plan` 第一项：`Paper launch queue（Rank 183）` 的 handoff close-out。
2. 复核 `Rank 183` 的 authoritative 证据链：
   - `source record`：`research/optimization_loop/2026-03-26_0927_rank183_cbeth_eth_rolling_fair_basis_mr_intake_keep_p1.md`
   - `survivor promote-P2`：`research/optimization_loop/2026-03-26_1044_rank183_survivor_followup_promote_p2.md`
   - `latest admission record`：`research/optimization_loop/2026-03-26_1238_rank183_p2_honesty_exit_promote_p3.md`
   - `cross-asset / time stability`：`research/optimization_loop/2026-03-26_1128_rank183_p2_cross_asset_time_stability_keep_p2.md`
   - `parameter stability / exit framing`：`research/optimization_loop/2026-03-26_1201_rank183_p2_parameter_stability_exit_framing.md`
3. 复核当前 reader-facing / operator-facing 落点，确认这一条线已经有明确的 intake 页面与可引用的 artifact 锚点，不需要再补开放式 admission：
   - intake 阅读页：`reports/site/reading/quant_digests/2026-03-26_0850_cbeth-eth-rolling-fair-basis-mr.html`
   - 核心 artifact：`reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_15m/summary.csv`
   - 核心 artifact：`reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_15m/trade_log.csv`
   - honesty gate：`reports/artifacts/quant_digests/cbeth_eth_honesty_gate_20260326_1044.json`
4. 明确 paper launch 的最小 handoff 口径，只保留当前已经被 admission 收窄后的 executable spec：
   - **launch object**：`CBETH spot + ETH perp` 的 relative-value mean reversion，不再泛化成整个 `LSD basis` 家族；
   - **timeframe**：`15m`；`5m` 已被 honesty gate 证伪为过薄，不进入 launch 主体；
   - **slow anchor**：`7~10d rolling fair basis`；
   - **entry / exit / timeout**：`|z|>=2.0` 为主，`exit 0~0.5`，`timeout 12h~24h` 只作为防事故护栏；
   - **size / execution**：默认仅从 `2k~10k USD` 小中仓位 paper 起步，不讲大容量故事；
   - **handoff meaning**：`P3 handoff ready` 代表这条线已经具备进入 paper launch queue 的最小研究闭环，下一步该做的是 queue 级接线 / runner 设计，而不是继续 admission。
5. 把最小 review / rollback 规则写死，避免下一轮误把它拖回开放式研究：
   - 若后续 paper launch 接线阶段发现 `CBETH` 实际可成交深度、挂撤节奏或 `ETH perp` 对冲/funding 口径无法复现当前 `26~30 bps pair RT` 的诚实假设，才允许把它拉回 `Paper launch queue review`；
   - 若只是继续观察月份强弱、`z=2.0` vs `2.25` 的 pocket 厚度、或 `exit 0` 与 `0.25` 的风格差异，这些都属于 paper 阶段监控项，不再构成 bot3 当前轮次继续 admission 的理由。
6. 回写 runtime state：把本轮小点标记为 `done`，并把 `Paper launch queue.latest_result` 更新为 `Rank 183：P3 handoff ready，可直接接 paper launch` 的 authoritative 口径。

## authoritative handoff packet
- `target`: `Rank 183 / cbeth-eth-rolling-fair-basis-mr`
- `source record`: `research/optimization_loop/2026-03-26_0927_rank183_cbeth_eth_rolling_fair_basis_mr_intake_keep_p1.md`
- `survivor -> P2 record`: `research/optimization_loop/2026-03-26_1044_rank183_survivor_followup_promote_p2.md`
- `latest admission record`: `research/optimization_loop/2026-03-26_1238_rank183_p2_honesty_exit_promote_p3.md`
- `supporting admission records`: `research/optimization_loop/2026-03-26_1128_rank183_p2_cross_asset_time_stability_keep_p2.md`, `research/optimization_loop/2026-03-26_1201_rank183_p2_parameter_stability_exit_framing.md`
- `paper launch entry`: `reports/site/reading/quant_digests/2026-03-26_0850_cbeth-eth-rolling-fair-basis-mr.html`
- `paper launch artifact anchor`: `reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_15m/summary.csv`
- `paper launch trade-log anchor`: `reports/artifacts/quant_digests/cbeth_eth_basis_probe_20260326_0850_15m/trade_log.csv`
- `paper launch honesty anchor`: `reports/artifacts/quant_digests/cbeth_eth_honesty_gate_20260326_1044.json`
- `paper launch executable spec`: `CBETH spot + ETH perp` / `15m` / `7~10d rolling fair basis` / `|z|>=2.0` / `exit 0~0.5` / `timeout 12h~24h` / `2k~10k USD`
- `minimal review rule`: 后续若要推翻 `P3 queue`，必须来自 paper 接线阶段出现的单一决定性失败（例如更诚实的成交/对冲现实下边际消失），而不是回头补同类 admission compare。
- `minimal rollback rule`: 仅当 queue 接线证明 `CBETH` 深度/冲击、`ETH perp` funding/执行节奏或 pair RT 假设出现新的明确致命 flaw，才允许从 `Paper launch queue` 回退到 review；否则默认继续沿 paper launch 路径前进。

## 一句话结果
`Rank 183 / cbeth-eth-rolling-fair-basis-mr` 的 `P3 handoff` 已补齐到可交接状态：可执行 paper spec、证据链、页面与 artifact 锚点都已明确，后续应进入 paper launch queue 接线，而不是继续停留在 admission。

## 风险 / 边界
- 当前并没有伪造“专属 paper runner 已存在”；本轮只把 queue handoff 包补齐到可交接，而不是声称已进入自动运行。
- 当前最诚实的 launch 对象是 **单一 `CBETH spot + ETH perp` pair**，不是可横向外推到一整类 LSD basis 的 shared 模板。
- `5m` 已被排除出当前 launch 主体；若未来要重开，必须作为新对象另起 intake，而不是偷渡回 Rank 183。
- `2k~10k USD` 之外的容量外推仍是 paper 阶段需重点盯的风险，不应在 handoff 文案里被洗掉。
