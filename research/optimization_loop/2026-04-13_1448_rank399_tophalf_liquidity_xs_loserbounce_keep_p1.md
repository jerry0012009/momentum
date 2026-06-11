# 2026-04-13 14:48 UTC — Rank 399 fresh intake first verdict（top-half liquidity XS loser-bounce shell）

## 执行小点
- target: `research/quant_digests/2026-04-13_1428_tophalf-liquidity-xs-loserbounce-shell.md`
- action: fresh intake first-verdict（统一成本口径 + 最小 honesty 检查）

## 本轮结论（改变系统认知）
- 分配新正式身份：`Rank 399 / top-half liquidity XS loser-bounce shell`。
- verdict: `keep_P1`（进入 survivor 槽位，保留 1 次唯一 follow-up）。
- 依据：现有 `15m/5m` portability probe 显示费前横截面反转边际持续为正，但 `4~8 bps` taker 成本即把净值快速压穿；因此当前不能进 `P2`，但也不足以直接 `P0`，应先做一次低成本、单 blocker 的 survivor 收口。

## 最小 honesty / execution realism 子检查
- 检查点：`top-half liquidity` 分层是否依赖同窗成交量排序（潜在同窗信息泄漏）。
- 结果：当前 digest 的分层描述为“按 quote volume 排前 50%”且未显式声明 `t-1` 固定，存在同窗排序泄漏风险；该风险与执行可行性（换手是否能在降频后翻正）同轴，适合作为 survivor 唯一 blocker 一次性收口。

## 锁定的唯一 survivor follow-up blocker
- 必做一轮合并检查：
  1) `t-1 lagged liquidity ranking`（防同窗 volume 泄漏）；
  2) `2/3/4-bar staggered rebalance`（在同一信号下压 turnover）；
  3) 统一成本口径复核净后是否可从成本悬崖翻正。
- 退出规则：若仍无法形成稳定净后边际，直接 `background/P0`，不再拖长。

## 回写
- 已更新：`docs/BOT2_BOT3_STATE.md`
  - `cycle_plan[1] -> done`
  - Fresh intake latest_result / latest_result_record
  - Surviving candidate slot 迁移至 `Rank 399`，`followup_budget_remaining = 1`
