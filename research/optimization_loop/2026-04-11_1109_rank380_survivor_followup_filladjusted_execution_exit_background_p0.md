# 2026-04-11 11:09 UTC — Rank 380 survivor follow-up（fill-adjusted execution realism 出口判定）

## 执行小点
- cycle_plan 第 1 项：`Rank 380 / dynamic second-factor basket fade alpha (short-cycle proxy)`
- 动作：survivor 唯一一次 follow-up，验证 fill-adjusted maker execution realism 后给出口（`promote_P2` 或 `background/P0`）

## 本轮最小 honesty 子检查（唯一 blocker 直击）
- 读取同主题已有可复现实验产物：
  - `reports/artifacts/literature/dynamic_factor_shortcycle_probe_2026-04-11.json`
  - `reports/artifacts/literature/dynamic_factor_shortcycle_probe_2026-04-11.csv`
- 关键结果：
  - 在当前更接近“可执行稳定窗口”口径下：`stationary_like_share = 1.22%`、`trade_count = 0`（无可成交样本）
  - 在先前宽松 proxy 下虽有信号，但 gross 仅低个位数 bps/trade（8~12 bar 大致 2~5 bps 级）
- 结论：当前证据无法证明该 alpha 在 maker queue-position / cancel-latency / partial-fill 的 fill-adjusted 口径下仍能稳定跨过成本阈值；且在更严格稳定性门槛下机会密度已接近不可交易。

## 出口判定（改变系统认知）
- `Rank 380` survivor 唯一 follow-up 已用尽，判定为：`background / P0`（不升 `P2`）。
- 决策语义：该主题保留为研究线索，但在当前 short-cycle 执行现实性口径下不具备前排延续资格。

## 本轮回写
- `Surviving candidate slot`：释放（`current_target: none`，budget 归零）
- `Background pool`：登记 `Rank 380` 本轮因 fill-adjusted execution realism 未通过而转入背景
- `cycle_plan` 第 1 项：`status: done`，写入出口结果

## 尾部动作
- homepage 刷新：按默认尾步尝试执行，若失败按非阻断处理。
- 邮件通知：按默认尾步发送中文摘要，若失败仅记通知失败，不回滚 verdict/state/log。
