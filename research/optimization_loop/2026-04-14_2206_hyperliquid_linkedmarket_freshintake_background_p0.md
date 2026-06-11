# bot3 optimization loop log — 2026-04-14 22:06 UTC

## 执行小点
- target: `research/quant_digests/2026-04-14_1638_hyperliquid-linkedmarket-spreadfade-shell.md`
- action: fresh intake first-verdict（统一成本/延迟口径 + 最小 honesty/execution 子检查：双腿 freshness admission + stale-leg 过滤可执行性）

## 本轮最小检查（honesty / execution realism）
使用既有 live probe 原始采样 `reports/artifacts/quant_digests/hyperliquid_linked_market_spread_probe_2026-04-14_raw.csv`（120 秒，1s 采样）重算 pair freshness：

- `XAUT0_vs_GLD`
  - left/right updates: `17 / 0`
  - both_leg_updates_per_5m（按 120s 外推）: `0.00`
  - active_overlap_ratio (`|last_update_gap|<=3s`): `0.000`
- `SPY_vs_QQQ`
  - left/right updates: `0 / 0`
  - both_leg_updates_per_5m: `0.00`
  - active_overlap_ratio: `0.000`
- `BNB_vs_BNB1`
  - left/right updates: `68 / 2`
  - both_leg_updates_per_5m: `5.00`
  - stale_gap_p95_s: `46.67s`
  - active_overlap_ratio: `0.078`

判定口径（来自 intake 文档中已声明的 admission 方向）：
- `both_leg_updates_per_5m >= 10`
- `stale_gap_p95_s <= 3`
- `active_overlap_ratio >= 0.6`

结果：观测到的三个 linked pairs 全部未通过最小 freshness admission，且失败维度直接指向执行真实性（stale leg / 非同步更新），因此当前样本下不具备进入费后收益评估的前置可执行性。

## 结论（改变系统认知）
`hyperliquid linked-market spread-fade` 本轮 fresh intake 首判为 `background/P0`：在最小 honesty admission（双腿 freshness/同步更新）下直接失败，当前证据不支持进入 `keep_P1`。

- rank: 不分配（`background/P0`）
- 层级变化: fresh intake -> background

## 回写目标
- 更新 `BOT2_BOT3_STATE.md`：
  - `Fresh intake slot.latest_result` / `latest_result_record`
  - `Background pool.latest_parked` / `latest_parked_record`
  - `cycle_plan` 第 2 项 `result/status`

## 尾部动作记录
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 本轮未返回输出且长时间未结束，已按非阻断尾部失败处理（不回滚本轮 verdict/state/log）。
- 邮件通知：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] Hyperliquid linked-market fresh intake判定P0" --body-file ...` 已成功发送。
