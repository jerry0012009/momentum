# 2026-03-23 07:33 UTC · Rank 140 balance screen（最短 decisive compare）

## 本轮执行顺序（按顶板）

### 1) 先读 `TRADING DESK BOARD`
- `Paper / 待开启自动运行 = empty`
- 无新的 interrupt 证据进入顶板
- 因此本轮仍只能落在：
  - `Run 1`：`Rank 140` 的最短 decisive compare
  - `Run 2/3`：保留给 `Rank 111` 这类 residual evidence anchor，而不是继续给已 budget-used 的 P1 开近义二刀

### 2) interrupt check
仅按顶板允许的真实异常排查：
- `EMA / PSAR raw alpha focus`：未见新的 `stale / error / refresh 失步 / red-watch`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b / Rank 122 / Rank 139`：未见新的 `ledger 爆雷 / open-position 异常 / blocking anomaly`

结论：**无 interrupt，本轮继续执行 `Rank 140` compare anchor。**

---

## 本轮主点

不再给 `Rank 140` 新开 family，也不再用单个低 `PBO` 伪亮点继续拉扯。

本轮只做一张更短的 compare 卡：
> **先强制执行 kept:veto balance discipline，再看 `Rank 140` family board 里到底还剩几个真能站住的 family。**

具体规则：
- 只保留 `max(kept_share, veto_share) <= 0.70` 的 family，排除明显没拆开的 arms
- 在“拆得开”的 family 里，再看：
  - `verdict`
  - `PBO`
  - `kept_minus_veto_mean_net_6bps`

---

## 本轮新增 artifact
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_balance_screen_20260323.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_balance_screen_20260323.json`

上游来源：
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.csv`

---

## 结果摘要

### 1) 通过 balance discipline 的 family 数
- `balanced_family_count = 7`

### 2) 其中真正还能算 deployable candidate 的 family 数
- `deployable_family_count = 2`
- **两条都来自 `Rank 137`**：
  - `confirm_window_12`
  - `confirm12_entry24`

### 3) 其余“拆得开”的 family 仍没过 honesty 守门
- `Rank 125 / rl_gate`
  - `PBO = 0.5714`
  - `kept_minus_veto_mean_net_6bps ≈ +0.1116%`
  - 但仍 `guard_failed`
- `Rank 111 / same_window_only`
  - `PBO = 0.7143`
  - `kept_minus_veto_mean_net_6bps ≈ +0.0599%`
  - `guard_failed`
- `Rank 111 / window_plus_timeout`
  - `PBO = 0.8000`
  - `kept_minus_veto_mean_net_6bps ≈ +0.0171%`
  - `guard_failed`
- `Rank 128 / max_high_only`
  - `PBO = 0.8000`
  - `kept_minus_veto_mean_net_6bps ≈ +0.0107%`
  - `guard_failed`
- `Rank 127 / shared_gate`
  - `PBO = 0.6286`
  - `kept_minus_veto_mean_net_6bps < 0`
  - `guard_failed`

---

## 人话结论

这张卡把 `Rank 140` 的当前 desk 读法又收紧了一步：

1. **一旦先要求 kept:veto 真的拆开，`Rank 140` 里真正站得住的正例只剩 `Rank 137`。**
2. `Rank 125 / Rank 111 / Rank 128` 这些 family 不是完全没信息量，
   但它们现在更像“有一点 split 可读性”的 compare evidence，**不是可以把 `Rank 140` 拉回默认主位的 deployable honesty layer**。
3. 这也解释了为什么 `Rank 140` 该继续停在：
   - `keep_P1`
   - `active compare anchor`
   - `not default primary`

换句话说：
> **`Rank 140` 不是“shared honesty rule 快成了”，而是“只有 `Rank 137` 这条 family-specific pocket 还真过关，别的 family 仍主要提供比较价值”。**

---

## 对 desk 的最小结论

### 对 `Rank 140`
- 维持：`keep_P1 / active compare anchor / balance-aware freeze`
- 新增更硬的一句：
  - **如果先执行 kept:veto balance discipline，则当前唯一稳定 surviving pocket 仍只有 `Rank 137`。**
- 因此：**不恢复默认 primary。**

### 对 `Rank 111`
- 维持：`keep_P1 / residual evidence anchor`
- 本轮没有新升层证据；它的作用仍是帮助解释 `Rank 140` 的边界，而不是重新抢回主资源位。

---

## 轻量 scorecard
- `usefulness = medium`
- `time_stability = weak`
- `cross_asset_stability = medium`
- `cost_trade_stability = weak`
- `deployability = low`

### hard-fail flags
- `after_balance_screen_only_rank137_survives`
- `shared_core_not_recovered`
- `rank125_rank111_rank128_all_remain_guard_failed`
- `rank140_still_family_specific_not_shared`
- `no_new_p2_to_p3_signal`

### recommended_action
- **`keep_P1`**

### why_now
顶板已经把本轮资源压缩到“最短 decisive compare”。这张 balance screen 正好把 `Rank 140` 最容易反复争论的点一次说清：不是所有低 `PBO` 或小正差都值得继续烧预算，先过 balance discipline 之后，当前真正 surviving 的只剩 `Rank 137`。

### main_weakness
`Rank 140` 的正例仍是 **family-specific pocket**，不是一个共享、可直接部署的 honesty rule；这意味着它更适合作为 compare anchor，而不是恢复成默认 primary。

---

## TODO writeback
本轮**不修改** `docs/TODO.md`。
原因：
- 没有新的层级变化；
- 顶板当前口径已足够容纳这次结论，只需把过程细节留在 optimization log。

## 交付
- 日志：`research/optimization_loop/2026-03-23_0733_rank140-balance-screen.md`
- Artifact：
  - `reports/artifacts/pbo_cscv_honesty_gate/rank140_balance_screen_20260323.csv`
  - `reports/artifacts/pbo_cscv_honesty_gate/rank140_balance_screen_20260323.json`
