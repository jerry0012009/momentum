# Rank 431 / cointegration maker-first + hard time-stop pairs — fresh intake keep_P1

- 时间：2026-04-21 08:58 UTC
- 执行者：bot3
- 对应 cycle_plan 小点：1
- target: `research/quant_digests/2026-04-21_0528_cointegration-maker-timestop-pairs-alpha.md`

## 本轮执行动作
对 `cointegration maker-first + hard time-stop pairs` 做 fresh intake first verdict，只补 1 个最小 decisive blocker：在双腿统一成本（默认双腿 `8bps`）与最小成交现实（maker 未成转 taker 或放弃）的口径下，确认该 pairs 壳是否仍保留非单 pair 的 after-cost spread-fade pocket。

## 读取到的最小证据
来自 digest 现成本地 artifact：
- `reports/artifacts/quant_digests/pairsbot_scan_1h_2026-04-21.csv`
- `reports/artifacts/quant_digests/pairsbot_trade_summary_1h_2026-04-21_costladder.csv`
- `reports/artifacts/quant_digests/pairsbot_transfer_summary_15m_2026-04-21_costladder.csv`

通过当前 `1h` scan、且 half-life 不夸张的 pair 主要有 3 对：
1. `AVAXUSDT-ATOMUSDT`：`p≈0.00020`，`half_life≈15.7h`
2. `AVAXUSDT-SUIUSDT`：`p≈0.00165`，`half_life≈17.7h`
3. `ADAUSDT-DOTUSDT`：`p≈0.00438`，`half_life≈28.2h`

### 15m child-monitor / zero-cross 结果
- `AVAXUSDT-ATOMUSDT`：`13` 笔，`mean_pnl≈38.01bps`，`net_after_8/12/16≈30.01/26.01/22.01bps`
- `AVAXUSDT-SUIUSDT`：`17` 笔，`mean_pnl≈45.61bps`，`net_after_8/12/16≈37.61/33.61/29.61bps`
- `ADAUSDT-DOTUSDT`：`11` 笔，`mean_pnl≈16.66bps`，`net_after_8/12/16≈8.66/4.66/0.66bps`

### 最小 honesty 读法
- 不是只有单一 pair 存活：至少 `AVAX-ATOM` 与 `AVAX-SUI` 两对，在 `15m` child-monitor 下经过 `8/12/16bps` 成本梯度后仍保持同向正净边际。
- `ADA-DOT` 只剩薄边，不应拿它当核心宿主；但它并没有推翻“至少两对仍存活”的结论。
- 当前证据窗口本身就是 recent public window（digest 的近 `1000` 根 `1h` scan + 对应 child-monitor），因此这一步已经满足“不是纯历史单对 lucky run”的最小 blocker；但还没回答 rolling admission / month-by-month 稳定性与真实 maker fill discipline。

## 本轮 verdict
`keep_P1`。

## 为什么不是 background/P0
按当前小点 success criterion，只有当不存在“至少两个 pair 在 recent 窗口与成本梯度下仍保留同向净边际”的情况时，才应直接收口 `background/P0`。现在最少已有 `AVAX-ATOM` 与 `AVAX-SUI` 两对满足该条件，因此不能诚实写成 `background/P0`。

## 为什么还不直接升 P2
当前 surviving 价值已经成立，但决定性 blocker 还剩一个很清楚：
- 还没完成 `rolling pair admission / month-slice` 检查，无法确认活下来的不是当前窗口里少数 pair 的阶段性 coincidence；
- repo 主卖点之一是 maker-first 执行，而当前 artifact 仍主要是粗成本代理，不是完整 `GTX 未成 / 单腿成交 / timeout / re-post` 现实回放。

所以本轮最合法的层级是：fresh intake -> `keep_P1`，进入 survivor，等待那唯一一次 cheap decisive follow-up。

## runtime 影响
- 分配正式 `Rank 431`
- 将该对象写入 `Surviving candidate slot`
- `followup_budget_remaining = 1`

## 一句话结果（写回 state 用）
`Rank 431 / cointegration maker-first + hard time-stop pairs` 的 fresh intake first verdict 已诚实收口：recent public scan 下至少 `AVAX-ATOM` 与 `AVAX-SUI` 两对在 `15m` child-monitor 与统一 `8/12/16bps` 成本梯度后仍保留同向 after-cost spread-fade pocket，不是单 pair lucky run，因此本轮直接 `keep_P1` 并进入 survivor；唯一剩余 blocker 收敛为 `rolling pair admission + maker fill realism`。

## 尾部执行状态（非阻断）
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步返回 `SIGKILL`，按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件通知：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py ...` 已成功发送。