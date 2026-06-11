# 2026-03-17 00:11 UTC — Rank 12 clean replication + Light Stability Pack (park)

## 本轮席位与认领
- 先读 `docs/TODO.md` 的 `TRADING DESK BOARD` 与 `Next 3 bot3 runs`。
- 当前 `Paper Seat=EMA` 仍是 `waiting_not_due / due_soon`，按规则切到 `Run 2 / Scout Seat`。
- active Scout 边际价值复核：`Rank 7/8/9/10/11` 已是 `park`；`Rank 2` 为 `narrow paper pilot` 且仅在真实 append/review need 时继续；因此本轮主点继续推进 `Rank 12`，把它从 `source intake` 直接推进到可判定的 `clean replication + Light Stability Pack`。

## 主点（1 个）
- 新增脚本：`scripts/build_sr_zone_context_clean_replication.py`
- 基于已有 `Binance 120d 15m` cache，执行四档最小对照：
  - `single_line_break`
  - `averaged_zone_break`
  - `averaged_zone_retest`
  - `averaged_zone_context_gate`
- 统一执行口径：`next-bar open | 1 ATR stop | 2 ATR target | 8-bar time stop | cost ladder 6/10/15/20 bps`。
- 并行产出 Light Stability Pack 四项：
  - 时间稳定性 `time_stability_drycheck.csv`
  - 参数稳定性 `parameter_stability_drycheck.csv`
  - 跨标的稳定性 `cross_asset_stability_drycheck.csv`
  - 成本/交易数稳定性 `cost_trade_stability_drycheck.csv`

## 紧邻子点（1 个）
- 回写 `docs/TODO.md` 的 `TRADING DESK BOARD`：
  - `Rank 12` 状态从 `source intake / clean replication next` 更新为 `park / evidence pool`
  - `Next 3 bot3 runs` authoritative override 与 `2f` 同步更新为：Rank 12 默认不再占主资源，下一轮默认转向新的 `paper/repo based 5m/15m crypto intake`。

## 硬结论（hard verdict）
- `reports/artifacts/scout_sr_zone_context_15m/clean_replication_meta.csv`：
  - `winner_variant=averaged_zone_context_gate`
  - `verdict_tag=park`
- 关键数值（6bps/side）：
  - `averaged_zone_context_gate mean_total_return ≈ -4.34%`
  - `positive_asset_ratio = 1/3`
- Light Stability Pack：
  - 时间稳定性：fail（`0/3 positive buckets`）
  - 参数稳定性：fail（`0/5 configs positive`）
  - 跨标的稳定性：fail（`1/3 assets positive`）
  - 成本稳定性：fail（`0/4 cost levels positive`，20bps 约 `-11.56%`）

结论：`Rank 12 averaged SR zone + context gate` 当前应压回 `park / evidence pool`，不进入 `paper candidate pool`。

## 可部署产物 / reader-facing
- 代码：`scripts/build_sr_zone_context_clean_replication.py`
- artifacts：`reports/artifacts/scout_sr_zone_context_15m/`（events/trades/nav/summary/meta + 四项稳定性）
- 网页：`reports/site/factors/scout_sr_zone_context_15m/report.html`

## 最小验证
- 运行：`python3 scripts/build_sr_zone_context_clean_replication.py`
- 成功输出：
  - `[ok] sr zone context clean replication generated`
  - artifact 与 site 路径已落盘

## 工作区与脏文件
- 本轮相关改动：
  - `scripts/build_sr_zone_context_clean_replication.py`（新增）
  - `reports/artifacts/scout_sr_zone_context_15m/*`（新增）
  - `reports/site/factors/scout_sr_zone_context_15m/report.html`（新增）
  - `docs/TODO.md`（更新）
- 未提交 commit，避免与仓库内既有大量无关脏文件混提。

## 下一轮默认
- 若 `EMA` 仍 `waiting_not_due`：Scout 默认转向新的 `paper/repo based 5m/15m crypto fresh intake`；若暂无可执行高边际 intake，再回退到 `Run 3 tiny-live plumbing`。
