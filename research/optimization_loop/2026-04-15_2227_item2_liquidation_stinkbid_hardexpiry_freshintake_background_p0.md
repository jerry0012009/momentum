# bot3 optimization loop log — 2026-04-15 22:27 UTC

## 执行小点
- cycle_plan item 2
- target: `research/quant_digests/2026-04-15_1930_liquidation-stinkbid-hardexpiry-alpha.md`
- action: fresh intake first-verdict（统一 `t+2 + 4/6/8bps` 口径 + 最小 honesty/execution realism 检查）

## 结果摘要（会改变系统认知）
`liquidation shock × 30% pullback stink-bid × 5m hard-expiry continuation` 在本轮统一口径下不通过 first-verdict：即便按 maker pullback fill 假设筛过样本，`t+2` 入场后 `4/6/8bps` 费后总体均值为负，且 Asia/EU/US 分时段全部为负；结论收口为 `background/P0`（不进入 survivor，不分配 Rank）。

## 关键证据
复核产物：
- `reports/artifacts/quant_digests/2026-04-15_liquidation_stinkbid_hardexpiry_t2_probe_summary.json`
- `reports/artifacts/quant_digests/2026-04-15_liquidation_stinkbid_hardexpiry_t2_probe_events.csv`

最小可复核口径（BTCUSDT 1m proxy）：
- 事件代理：`abs(1m return) >= p99` 作为 liquidation-shock proxy（避免伪造私有 liquidation feed）
- 方向：冲击方向延续（上冲做多、下冲做空）
- 执行：`t+2` 入场，`5m` hard-expiry（`t+7` 平仓）
- maker stink-bid realism：仅保留在后续 `2m` 内出现 `30%` 冲击幅度回撤、可视作“挂单可成交”的样本
- 成本：统一 round-trip `4/6/8bps`

结果：
- 样本数：`3460`
- gross 均值：`+0.53bps`
- 费后均值：`net4=-7.47bps`，`net6=-11.47bps`，`net8=-15.47bps`
- 分时段（net8）：`Asia -14.52bps`，`EU -15.54bps`，`US -16.44bps`（全部为负）

## 最小 honesty / execution realism 子检查
- **无前视**：事件触发仅用当下 `1m` 收盘冲击，统一 `t+2` 执行。
- **执行现实性（最小）**：已显式加入“30% pullback 可成交”过滤，避免把未成交挂单计入收益。
- **唯一 decisive blocker**：成本后 edge 不成立（非单一时段偶发失效，而是全时段同向为负）。

## 本轮执行结论
- verdict: `background/P0`
- rank_assignment: `none`（未达到 `keep_P1`）
- survivor: `not eligible`
- status: `done`

## 尾部执行状态（非阻断）
- homepage publish：`bash scripts/publish_homepage_index.sh` 在本轮尝试中被宿主 SIGKILL 终止（非研究结论失败，不回滚 state/verdict/log）。
- 邮件通知：`send_text_email.py` 已成功发送。
