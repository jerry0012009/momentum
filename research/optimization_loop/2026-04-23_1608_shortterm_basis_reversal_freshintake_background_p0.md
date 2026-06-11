# bot3 optimization loop — short-term basis reversal fresh intake first verdict

- Time: 2026-04-23 16:08 UTC
- Target: `research/quant_digests/2026-04-23_1328_shortterm-basis-reversal-crypto-port.md`
- Action: fresh intake：对 `short-term basis reversal` 做 first verdict，只补 1 个最小 decisive blocker（它是否在 crypto 近远月结构里留下可独立排队、能与最小成本对话的 after-cost front-back spread-return fade pocket，而不是只剩 term-structure 提示）
- Success criterion: 必须直接输出 `keep_P1` 或 `background/P0`；只有当至少一个非单标的、非单阈值 lucky-run 的 after-cost short-term basis reversal pocket 明显成立，才 `keep_P1`
- Verdict: `background/P0`

## Why this step closes here
本轮只检查一个最小 decisive blocker：这条线是否已经留下可以独立排队的新 alpha pocket，而不是仅作为 term-structure shock 提示。

## Evidence used
1. `research/quant_digests/2026-04-23_1328_shortterm-basis-reversal-crypto-port.md`
2. `reports/artifacts/quant_digests/2026-04-23_1328_shortterm_basis_reversal_probe_summary.csv`
3. `reports/artifacts/quant_digests/2026-04-23_1328_shortterm_basis_reversal_probe_raw.csv`
4. 已 live pairs family 对照：`Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade`、`Rank 431 / cointegration maker-first + hard time-stop pairs`

## Minimal decisive read
从 probe summary 看，`BTCUSD/ETHUSD` 的 `15m` near-vs-far spread-return 确实有明显 lag-1 反转：

- BTC：`lag1 autocorr = -0.492`；无阈值 next-bar fade `+1.52 bps/bar`
- ETH：`lag1 autocorr = -0.524`；无阈值 next-bar fade `+1.89 bps/bar`
- 当 `|sig|>=3bps`：BTC `+2.81 bps`，ETH `+3.36 bps`
- 当 `|sig|>=4bps`：BTC `+3.48 bps`，ETH `+3.91 bps`

这说明“spread shock 后短窗回摆”作为统计现象是存在的，但它还没有跨过本轮需要的 admission 门槛：

1. **after-cost 厚度仍偏薄**
   文稿自己给出的 friction ladder 就是 `2/4/6 bps round-trip`。而当前最好的公开 probe 也主要只是 `3~4 bps` 量级的 next-bar 边际，尚不足以支持“默认可独立上线”的判断。

2. **样本仍停留在极窄对象集**
   当前只覆盖 Binance COIN-M `BTCUSD/ETHUSD` 的 `PERP vs CURRENT_QUARTER`，没有扩展到更多标的、更多 term bucket、更多真实 expiry/roll 口径；这还不构成“非单标的、非单阈值 lucky-run”之外的独立 pocket。

3. **新增价值更像已 live pairs family 的组件，而不是新主语**
   这条线目前最稳的可保留部分，是 `term-structure shock -> repair` 的 router / regime hint：可作为 near-vs-far spread 的 child execution、entry timing 或 veto 组件。但它尚未证明自己比已 live 的 `Rank 424 / 431` pairs family 多出一个必须单独排队的新 after-cost alpha 主体。

## Runtime result sentence
`short-term basis reversal` 已完成 fresh intake first verdict 并收口 `background/P0`：Binance COIN-M `BTCUSD/ETHUSD` 的 next-bar fade 虽显示短窗反转，但当前 after-cost 边际仍主要停留在 `1.5~3.9 bps/bar`，且价值更像可被已 live `Rank 424 / 431` pairs family 吸收的 term-structure shock/router 提示，没有形成可独立排队的新增 pocket，因此不保留 survivor。

## State writeback
- `Fresh intake slot.latest_result` 已更新为本次 verdict
- `cycle_plan` 第 2 项已写回 `done`
- 未分配新 `Rank`（因为结论为 `background/P0`）

## Tail steps (non-blocking)
- Homepage index publish: failed (`SIGKILL`, async session `tidal-canyon`)；按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- Email notify: success（`[momentum-bot3-auto] basis reversal 首判收口 P0` 已发送）。
