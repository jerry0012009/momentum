# 2026-03-23 18:03 UTC · Rank 140 hard verdict freeze

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 路径判断：`Paper / 待开启自动运行 = empty`，且未见 `Interrupt` 级异常，因此认领顶板 `Next 3 bot3 runs / Run 1 = Rank 140`。

## 0. 本轮主点与紧邻子点
### 主点
- 基于已经冻结的 surviving pocket / routing compare / family board，给 `Rank 140 / pbo-cscv deflated sharpe honesty gate` 一个**更硬、可写回顶板的 keep / park / escalate 结论**。

### 紧邻子点
- 把该结论同步写回 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，避免下一轮继续把 `Rank 140` 当成默认 Run 1 反复切片。

## 1. 本轮使用的 authoritative 证据
1. `reports/artifacts/pbo_cscv_honesty_gate/rank140_rank137_surviving_pocket_scorecard_20260323.csv`
2. `reports/artifacts/pbo_cscv_honesty_gate/rank140_vs_rank145_vs_rank14b_routing_compare_20260323.csv`
3. `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.csv`

## 2. 核心读法
### 2.1 Rank 140 里真正过关的只有 Rank 137 的 family-specific pocket
在 `rank140_explicit_three_arm_family_board.csv` 里：
- `Rank 137 / confirm_window_12`
  - `kept_share = 66.63%`
  - `pbo = 0.0`
  - `gate_kept_mean_net_6bps = +25.49 bps`
  - `gate_veto_mean_net_6bps = -79.31 bps`
  - `kept_minus_veto = +104.80 bps`
  - `verdict = guard_passed`
- `Rank 137 / confirm12_entry24`
  - `kept_share = 58.44%`
  - `pbo = 0.0`
  - `gate_kept_mean_net_6bps = +13.14 bps`
  - `gate_veto_mean_net_6bps = -41.30 bps`
  - `kept_minus_veto = +54.44 bps`
  - `verdict = guard_passed`

而其他 family：
- `Rank 125 / rl_gate`：`guard_failed`
- `Rank 127 / shared_gate`：`guard_failed`，且 veto 侧反而更好
- `Rank 111` 两个 strict 变体：都 `guard_failed`
- `Rank 128 / max_high_only`：`guard_failed`

人话：
> `Rank 140` 并没有把“shared honesty gate”做成一个可推广的共享层；它现在唯一站得住的，只是 `Rank 137` 家族里的 surviving pocket，尤其是 `confirm_window_12`。

### 2.2 surviving pocket 本身仍值得保留，但不足以 escalate
在 surviving pocket scorecard 里：
- `confirm_window12_only`
  - `trades = 88`
  - `mean_net_bps_6bps_side = +100.6235`
  - `win_rate = 72.73%`
  - `positive_asset_count = 3/3`
- `confirm12_entry24_only`
  - `trades = 47`
  - `mean_net_bps_6bps_side = +37.5898`
  - `positive_asset_count = 2/3`
  - `BTC-USD = -2.8518 bps`

读法：
- 这足够支持 `keep_P1`；
- 但还不够支持 `escalate`，因为优势集中在 **single family / single surviving pocket**，不是共享 guard 已成立。

### 2.3 routing compare 已经说明：Rank 140 不该再占默认 Run 1
`rank140_vs_rank145_vs_rank14b_routing_compare_20260323.csv` 已固定：
- `Rank 140 = keep_P1`，但读法是 `stay active compare anchor`
- `Rank 145 = keep_P1 / reserve only`
- `Rank 14b = keep_P1 / cheap fallback only`

本轮补上的关键不是再做比较，而是把比较结论**落成路由动作**：
> `Rank 140` 仍该保留，但只保留为 compare anchor；默认 Run 1 应该让位给下一条需要收口的候选。

## 3. 本轮 hard verdict
### 对 Rank 140 的 authoritative 结论
- `recommended_action = keep_P1`
- `desk_role = active compare anchor`
- `promotion_read = not escalate`
- `routing_read = not default Run 1`

### 为什么不是 park
- `Rank 137 / confirm_window_12` 仍然给出干净且跨资产为正的 surviving pocket；
- 直接 park 会丢掉仍有信息量的 compare anchor。

### 为什么不是 escalate
- shared honesty layer 没成立；
- 其余 family 普遍 `guard_failed`；
- 当前胜出的是 pocket，不是机制层。

## 4. 写回顶板的改变
已同步更新 `docs/TODO.md` 顶部：
1. `Active Scout 排序`：把 `Rank 140` 改为 `hard verdict done / 不再占默认 Run 1`
2. `Next 3 bot3 runs`：把默认 Run 1 切到 `Rank 145`
3. `最近关键 evidence`：新增本轮 hard verdict 说明

## 5. 简短 scorecard
- `usefulness = medium`
- `time_stability = weak`
- `cross_asset_stability = medium`
- `cost_trade_stability = weak`
- `deployability = low`
- `recommended_action = keep_P1`
- `why_now = 顶板明确要求对 Rank 140 给出更硬结论；本轮把“继续留着”与“不再默认优先做”这两个动作拆清了。`
- `main_weakness = surviving evidence 仍是 family-specific pocket，不是可推广 shared honesty layer`

## 6. 本轮交付
- 日志：本文件
- 顶板 writeback：`docs/TODO.md`
- reader-facing 落点：刷新 homepage index 后，本轮日志将进入首页索引
