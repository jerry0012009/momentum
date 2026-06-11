# 2026-03-23 08:17 UTC · Rank 140 balance shortlist（最短 decisive 收口）

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 顶板判定：`Paper / 待开启自动运行 = empty`，且未见新的 interrupt，因此继续执行 `Next 3 bot3 runs / Run 1 = Rank 140 的最短 decisive compare`

## 0. 运行前检查
- repo 有大量既有脏文件，本轮只新增 `Rank 140` shortlist artifact + 对应 reader-facing 页面，不触碰无关改动。
- 最近 optimization logs 已经把 `Rank 140` 收紧到：
  - `keep_P1 / active compare anchor / balance-aware freeze`
  - 当前 surviving pocket 主要来自 `Rank 137`
- 因此本轮不再开新 family，也不再重跑近义 compare，而是把这个读法收口成一张最短 shortlist。

## 1. 本轮只做什么
### 主点
- 把 `Rank 140` 的 balance-aware freeze 变成一张 **可直接引用的 shortlist**：
  - 先强制 `max(kept_share, veto_share) <= 0.70`
  - 再看谁还是真正 surviving family

### 紧邻子点
- 顺手把 `pbo_cscv_honesty_gate` reader-facing 页面更新成同样口径，避免首页/站点继续停在昨天的 `Rank 125 vs Rank 112` 旧主叙事。

## 2. 新增产物
### artifacts
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_balance_shortlist_20260323.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_balance_shortlist_20260323.json`

### reader-facing 页面更新
- `reports/site/factors/pbo_cscv_honesty_gate/report.html`

## 3. 核心结果
### 3.1 balance 约束后的 family 数
- `balanced_family_count = 7`
- 规则：`max(kept_share, veto_share) <= 0.70`

### 3.2 真正 surviving 的 deployable family 数
- `deployable_family_count = 2`
- **两条都来自 `Rank 137`**：
  1. `confirm_window_12`
  2. `confirm12_entry24`

### 3.3 surviving pockets 的最小读法
- `Rank 137 / confirm_window_12`
  - `kept:veto = 545:273`
  - `PBO = 0.0000`
  - `kept_minus_veto_mean_net_6bps ≈ +1.0480%`
  - 读法：当前最强 surviving pocket
- `Rank 137 / confirm12_entry24`
  - `kept:veto = 478:340`
  - `PBO = 0.0000`
  - `kept_minus_veto_mean_net_6bps ≈ +0.5444%`
  - 读法：次级 pocket，但强度明显弱于 `confirm_window_12`

### 3.4 其余 balanced families 为什么仍不能升层
- `Rank 125 / rl_gate`
  - `kept:veto = 459:365`
  - `PBO = 0.5714`
  - `kept_minus_veto_mean_net_6bps ≈ +0.1116%`
  - 读法：split 很健康，但 OOS 排名稳定性仍不够
- `Rank 111 / same_window_only`
  - `kept:veto = 105:93`
  - `PBO = 0.7143`
  - `kept_minus_veto_mean_net_6bps ≈ +0.0599%`
  - 读法：仍只是 residual evidence
- `Rank 127 / shared_gate`
  - `kept:veto = 525:299`
  - `PBO = 0.6286`
  - `kept_minus_veto_mean_net_6bps < 0`
  - 读法：连 kept 都不比 veto 好，shared gate 解释力继续变弱

## 4. 人话结论
这轮最有杠杆的小步，不是再给 `Rank 140` 新开 family，而是把一句话彻底写死：

> **在 balance 约束之后，Rank 140 当前真正保留下来的，只是 Rank 137 的 family-specific surviving pockets；它仍不是一个已接近 deploy 的 shared honesty gate。**

这意味着：
1. `Rank 140` 值得继续留在 **active compare anchor** 位；
2. 但不该再被误读成默认 primary；
3. 站点页面也应该同步这个收口，而不是继续停留在旧的 `Rank125 vs Rank112` 演示口径。

## 5. lightweight scorecard
- `usefulness = medium`
- `time_stability = weak`
- `cross_asset_stability = medium`
- `cost_trade_stability = weak`
- `deployability = low`
- `recommended_action = keep_P1`
- `why_now = 顶板要求本轮只做最短 decisive compare；把 Rank 140 收口成 shortlist 比继续补近义 family 更能减少后续误判`
- `main_weakness = 正例仍来自 Rank 137 的 family-specific pocket，而不是 shared、可部署的统一 honesty rule`

## 6. desk verdict
- 对 `Rank 140`：维持 `keep_P1 / active compare anchor / balance-aware freeze / not default primary`
- 对紧邻子点（reader-facing 页面）：已同步为 `Rank 140 balance shortlist` 口径

## 7. 本轮交付
- 日志：`research/optimization_loop/2026-03-23_0817_rank140-balance-shortlist.md`
- artifacts：
  - `reports/artifacts/pbo_cscv_honesty_gate/rank140_balance_shortlist_20260323.csv`
  - `reports/artifacts/pbo_cscv_honesty_gate/rank140_balance_shortlist_20260323.json`
- 页面：`reports/site/factors/pbo_cscv_honesty_gate/report.html`
