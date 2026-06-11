# 2026-03-21 07:13 UTC — Rank 127 / signal→confirm ATR delta phase gate / cheap time-stability check → park

## 为什么这次选这个
这轮先按 desk 指挥板执行：
- `Run 1` 先看 `EMA due-check`，当前仍是 `waiting_not_due`；
- 因此合法切去 `Scout Seat`；
- 顶板把 `Run 2` 明确写成：给 `Rank 127` 最后 **1 次便宜诚实检查**（优先时间稳定性），做完必须直接给 `keep_P1 / promote_P2 / park`，不能继续 admission wording 回环。

所以这轮的正确动作不是再开新题，而是把 `Rank 127` 的最后一层不确定性砍掉。

## 本轮做了什么
### 1. 复用现有 clean replication 产物，不重跑重型实验
直接读取：
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/trade_log.csv`
- `overall_summary.csv`
- `asset_summary.csv`
- `cost_summary.csv`

只针对测试段补了这次 cheapest honesty check：`time stability`。

### 2. 新增时间稳定性 artifact
新增：
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/time_stability_monthly.csv`
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/time_stability_halves.csv`
- `reports/artifacts/scout_rank127_signal_confirm_atr_delta_phase_15m/promotion_scorecard.csv`

reader-facing：
- `reports/site/reading/repo_scout/rank127_signal_confirm_atr_delta_phase_time_stability.html`

### 3. 最小同步 desk 顶板
已把 `docs/TODO.md` 顶部 authoritative board 收紧为：
- `Rank 127` 从 `P1 / 最后 1 次 cheap check` 改成 `P0 / park`
- `Scout Seat` 主点切到 `Rank 139 / CUSUM event-bar confirm-veto gate`
- `Next 3 bot3 runs` 也同步改成：`EMA due-check -> Rank 139 source intake + honesty guards -> 若 guard-pass 再做最小 clean replication`

## 验证 / 证据
### 测试段总体复核（shared gate）
- `trade_retention ≈ 70.4%`
- `return_delta ≈ +2.90 bps`
- 绝对 post-cost 均值仍为负：`variant_return ≈ -3.62 bps`

这说明它最多只是“少亏一点”的弱 filter，不是已经能直接升 `P2` 的候选。

### 时间稳定性（月度）
按测试段月份拆开：
- `2026-01`：样本极薄（baseline 11 笔 / shared 5 笔），不值得高权重解释
- `2026-02`：`shared_return_delta ≈ +13.64 bps`
- `2026-03`：`shared_return_delta ≈ -15.13 bps`

关键信号：**这条线没有形成足够稳的时间一致性；2 月像样，3 月已经反转。**

### 时间稳定性（测试段前后半场）
- `shared_gate / first_half`：mean gross return `≈ +19.41 bps`
- `shared_gate / second_half`：mean gross return `≈ -2.53 bps`
- failure 也从 `≈45.2%` 升到 `≈56.9%`

翻成人话：前半段看起来像有点帮助，后半段就明显塌了。

### 跨标的补读（shared gate / test）
- `BTC`：只是 **少亏**，不是转成强正收益
- `ETH`：仍更差
- `SOL`：绝对收益才是真正明显转正的一腿

所以它并不是一个“多标的一致兑现”的 shared gate。

### 轻量 Promotion Scorecard
- `usefulness = 1`
- `time_stability = 1`
- `cross_asset_stability = 2`
- `cost_trade_stability = 2`
- `deployability = 1`
- `total_score = 7 / 15`
- `recommended_action = park`

不是完全没信息，但也远没到 desk 该继续给 `P2` 预算的程度。

## 硬结论
**`Rank 127 / signal→confirm ATR delta phase gate = park（P0）`**。

一句话版：
> 这条线在 clean replication 里只有很轻的 uplift，而最后这次 cheap time-stability check 又确认 uplift 主要集中在单一月份；进入 2026-03 后已经转负，因此不该升到 `P2 / paper candidate`。

## 对 desk 的含义
- `Paper Seat`：不变，仍是 `EMA / running paper / waiting_not_due`
- `Live Seat`：继续暂空
- `Scout Seat`：主资源位正式切到 **`Rank 139 / CUSUM event-bar confirm-veto gate`**
- 旧的 `Rank 125 / 112 / 111` 继续不该抢主资源；若没有新的会改变 verdict 的证据，默认不再回头磨

## 风险 / 边界
1. 这是 cheap honesty check，不是新一轮大规模复现；优点是快且诚实，缺点是只回答“还值不值得继续给预算”。
2. 工作区有大量与本轮无关的脏文件，不能安全 selective commit。
3. `Rank 127` 并不是“理论上永远无效”，只是按当前 desk 预算与证据口径，**不值得继续排在 `Rank 139` 前面**。

## 下一步建议
1. 下一轮继续先做 `EMA due-check`；若仍 `waiting_not_due`，直接认领 `Rank 139` 的 `source intake + 两条轻量诚实守门`。
2. 若 `Rank 139` guard-pass，再给它 **1 次最小 clean replication**；若不过，则切 fresh intake，不回头磨 `Rank 127`。
3. `P3 hosted lanes` 只有在出现真实 `due-now / overdue` refresh 或 status-changing event 时，才重新占 bot3 主资源位。

## Commit hash
未提交。

原因：repo 当前存在大量与本轮无关的脏文件与未跟踪文件，无法安全做 selective commit，按规则只留可审计 artifact + desk write-back + 邮件摘要。
