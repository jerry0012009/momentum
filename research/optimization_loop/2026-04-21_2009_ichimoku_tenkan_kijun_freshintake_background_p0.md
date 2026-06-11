# Tenkan/Kijun cross fresh intake -> background/P0

- 时间：2026-04-21 20:09 UTC
- 对象：`research/quant_digests/2026-04-21_1548_ichimoku-tenkankijun-cross-feetrap.md`
- 执行动作：fresh intake first verdict
- 轮次角色：bot3 executor

## 本轮只回答的 decisive blocker
在 `15m/5m`、统一 `4bps roundtrip` 成本与最小 parent/child 现实约束下，`Tenkan/Kijun cross` 能否保住一个值得前排保留的独立 after-cost pocket；若不能，就不把它当成新的 `P1` raw alpha，只作为后续可能依附别的趋势母体的方向层提示。

## 读取到的最小证据
来自 digest 与本轮已落库 artifact：
- `reports/artifacts/quant_digests/2026-04-21_ichimoku_tk_cross_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-21_ichimoku_cross_variant_comparison.csv`

### Tenkan/Kijun 主体结果
- `5m bull hold8`: `1746` 笔，`avg_gross_bps≈+2.30`，`avg_net_bps≈-1.70`，虽然 `positive_symbols=8/8`，但统一成本后仍未转正。
- `5m bull hold4`: `avg_gross_bps≈+1.40`，`avg_net_bps≈-2.60`。
- `15m bear hold4`: `avg_gross_bps≈+0.69`，`avg_net_bps≈-3.31`，只是最薄的 gross pocket。
- 其余 `15m bull` 组合整体更弱，`avg_net_bps` 全部显著为负。

### 变体对照
- `close/Kijun cross` 虽在 `15m bull hold8` 录得 `avg_gross_bps≈+2.42`，但 `avg_net_bps≈-1.58`；其余大多也在成本后为负。
- 说明真正较像 raw alpha 的只有 `Tenkan/Kijun` 这层 faster directional state，但它当前仍只保留薄 gross，不足以独立承担 fresh-intake front object。

## 结论
`Tenkan/Kijun cross` 的 fresh intake first verdict 已诚实收口：当前 `5m` 最强 pocket 虽达到 `8/8` symbols 同向正 gross，但统一 `4bps roundtrip` 后最优也只有 `avg_net_bps≈-1.70`；`15m` 最强 `bear hold4` 也只有 `avg_net_bps≈-3.31`。这说明它在 short-cycle crypto desk 上更像可依附其他趋势母体的 `parent direction / filter hint`，而不是能独立覆盖统一成本的 raw alpha；本轮直接收口 `background/P0`，不保留 survivor。

## 对 runtime 的影响
- `Fresh intake slot` 当前对象已完成首判并移入 `background/P0`
- `cycle_plan` 第 3 小点完成并写成 `done`
- fresh intake 前排应顺延到下一条仍 pending 的对象：`research/quant_digests/2026-04-21_1506_crosscrypto-peer-spillover-laggardcatchup-alpha.md`

## 尾部动作状态（非阻断）
- homepage publish：`bash scripts/publish_homepage_index.sh` 异步返回 `signal SIGKILL`（记录时间：2026-04-21 20:13:58 UTC），按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件通知：`send_text_email.py` 已成功发送。
