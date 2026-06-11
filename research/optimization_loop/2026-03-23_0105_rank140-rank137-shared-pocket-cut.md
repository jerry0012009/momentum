# 2026-03-23 01:05 UTC · Rank 140 / Rank 137 shared pocket cut

## 本轮按顶板顺序执行

### Run 1 · Paper / interrupt check
执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

结果：`waiting_not_due`
- 当前没有 `due-now / overdue` lane
- 最靠前 lane 为 A 股日频链路，约 `5.9h` 后到点
- 因此本轮 **不得伪造 refresh**

同时快速检查 autonomous runner：
- `manual narrow paper lanes` 最近一次 `run_at_utc = 2026-03-23T01:03:44Z`
- `new_closed_trades_appended = 0`
- 未见顶板定义的真实 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`

结论：**无 interrupt**，按默认队列继续 Scout。

### Run 2 · 当前最高优先级 Scout 是否还能继续占位
`Rank 14b` 已在 `00:01 UTC` 完成唯一允许的最小 clean-replication cut，并在 `00:51 UTC` 补齐显式 scorecard：
- 正式口径已经固定为 `keep_P1 / evidence strengthened / no promote yet`
- 按顶板纪律，本轮不能继续在同一 `P1` 候选上扩第二刀

因此本轮把 Scout 主资源切到下一 active compare：
- **`Rank 140 / pbo-cscv deflated sharpe honesty gate`**

### Run 3 · 仅做 1 个紧邻子点
承接 `00:39 UTC` 的 overlap cut，本轮只追问 1 个便宜但会改变读法的问题：

> `Rank 137` 两条 strict 变体（`confirm_window_12` 与 `confirm12_entry24`）都保留的 **shared pocket**，为什么反而是负的？

本轮 **不**：
- 新开第二个 family
- 回头做 `Rank 125 / 112 / 111`
- 继续扩 `entry latency` 新变体
- 做新的 paper continuity 近义巡检

---

## 本轮产物
目录：`reports/artifacts/pbo_cscv_honesty_gate/rank137_shared_pocket_diagnosis/`

- `asset_summary.csv`
- `setup_summary.csv`
- `hour_summary.csv`
- `dow_summary.csv`
- `shared_asset_hour_summary.csv`
- `shared_asset_setup_summary.csv`
- `summary.json`

口径：
- 输入：`reports/artifacts/pbo_cscv_honesty_gate/rank137_confirm_window12_entry24_overlap_matrix.csv`
- 对每笔交易统一计算：`net_6bps = gross_return - 12bps roundtrip`
- 只比较三段：
  1. `shared`
  2. `confirm_window12_only`
  3. `confirm12_entry24_only`

---

## 核心结果

### 1) shared pocket 的负值不是单一坏资产造成，而是三资产都偏负
`shared` 总体：
- `trades = 503`
- `mean_net_6bps = -18.96 bps`

分资产：
- `SOL-USD`：`177` 笔，`-29.77 bps`，`win_rate = 32.8%`
- `BTC-USD`：`176` 笔，`-14.72 bps`，`win_rate = 36.4%`
- `ETH-USD`：`150` 笔，`-11.18 bps`，`win_rate = 44.0%`

最重要的 desk 读法：
- `shared` 的差，不是“ETH 单独拖累”这种老问题；
- **三资产都一起偏负，尤其 `SOL` 更差**；
- 这说明 shared pocket 更像是“两个 strict 规则都同意保留的公共区，其实包含了大量普通 continuation 噪声”，而不是某个单一资产 pocket 偶然失真。

### 2) 真正的正 alpha 仍主要来自 exclusive pockets
正收益主要集中在两条变体各自切出来的独有区：
- `confirm_window12_only / SOL-USD`：`40` 笔，`+113.64 bps`
- `confirm_window12_only / ETH-USD`：`28` 笔，`+94.23 bps`
- `confirm_window12_only / BTC-USD`：`20` 笔，`+83.54 bps`
- `confirm12_entry24_only / ETH-USD`：`15` 笔，`+65.09 bps`

这进一步支持上一轮的判断：
- `confirm_window_12` 与 `confirm12_entry24` **不是父子嵌套**；
- 它们真正的价值更像来自 **各自独有 pocket**；
- 其中当前仍是 **`confirm_window12_only` 更强**。

### 3) shared pocket 还有轻微时间集中坏区，但不足以单靠时段解释全部问题
只看 `shared` 且样本数 `>=12` 的资产-小时：
- 最差：`BTC 13UTC ≈ -66.39 bps`（12 笔）
- 次差：`SOL 14UTC ≈ -63.28 bps`（16 笔）

但：
- `shared` 的负值并不只来自单一时段；
- 更像是**公共保留区整体质量就偏差**，小时只是放大镜，不是唯一病根。

---

## 轻量 scorecard
- `usefulness = medium`
- `time_stability = weak_to_medium`
- `cross_asset_stability = weak`
- `cost_trade_stability = weak`
- `deployability = low`

### hard-fail flags
- `shared_pocket_all_three_assets_negative`
- `sol_shared_drag_is_largest`
- `positive_alpha_concentrated_in_exclusive_pockets`
- `shared_zone_not_good_enough_as_default_kept_core`

### recommended_action
- **`keep_P1`**

### why_now
上一轮 overlap cut 已证明 `confirm_window_12` 与 `confirm12_entry24` 不是纯父子关系；本轮这刀把“为什么 shared 反而差”补成了更硬的 desk 解释，避免后续把 `shared overlap` 误读成可直接部署的共识核心。

### main_weakness
当前 `Rank 137` 的正 evidence 主要来自 exclusive pockets，而不是 shared core。也就是说，这个 family 还没有收敛成一个简单、稳定、读者友好的单一 strict rule；一旦强行把两条 strict 变体的公共区当主规则，三资产都会一起变差。

---

## Desk 结论更新
对 `Rank 140 / Rank 137` 当前最诚实的读法应改成：

1. `Rank 137` 仍然是 `Rank 140` 当前最像样的正例 family；
2. 但它的正值 **不是来自 shared overlap core**；
3. 更像是：
   - `confirm_window_12` 切出了一块最强 exclusive pocket；
   - `confirm12_entry24` 也切出了一小块独有正 pocket；
   - 两者共同保留的公共区反而偏负；
4. 因此现阶段更适合继续把它读作 **`keep_P1 / family evidence strengthened / not yet a deployable shared honesty rule`**，而不是向 `P2/P3` 误升级。

## 本轮交付
- 日志：`research/optimization_loop/2026-03-23_0105_rank140-rank137-shared-pocket-cut.md`
- 诊断产物：`reports/artifacts/pbo_cscv_honesty_gate/rank137_shared_pocket_diagnosis/`

## 对下一轮的最短提醒
- `Rank 14b`：本轮继续视为 exhausted，不要马上回头再磨第二刀。
- `Rank 140`：若还给预算，下一刀应优先是 **把 `confirm_window12_only` 组织成更明确的可解释 strict 语义**；
- 若做不到这一点，就应考虑把 `Rank 140` 继续留作 `active compare anchor` 而非主资源位，并切 fresh intake reserve。
