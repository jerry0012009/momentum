# 2026-03-23 05:26 UTC · Rank 140 balance-aware freeze

## 本轮执行顺序（按顶板）

### 1) 先读 `TRADING DESK BOARD`
- `Paper / 待开启自动运行 = empty`
- 顶板默认 `Run 1` 仍先落到 `Rank 140 / pbo-cscv deflated sharpe honesty gate`
- `Run 2` 的最短对照锚仍是 `Rank 111`

### 2) interrupt check
本轮先排除顶板允许抢占的真实异常：
- `EMA / PSAR raw alpha focus`：状态文件未见明确 `stale / error / red-watch`
- `manual narrow paper lanes`：最近 summary / status 文件虽有老化，但未看到顶板定义的 `ledger 爆雷 / open-position 异常 / refresh 失步` 证据
- `Rank 139 / Rank 122`：未见新的 blocking anomaly 信号

结论：**无 interrupt，本轮仍按默认队列执行。**

---

## 本轮主点：`Rank 140` 不再做新 family 扩写，只做 balance-aware freeze

原因很简单：
- `Rank 140` 在 03:14 UTC 已完成 desk-level 最小 verdict：**退出默认 primary，但保留为 active compare anchor**；
- 之后又有 `Rank 144`、`Rank 145` 两条 fresh / adjacent 线完成了最小 honest cut，进一步说明默认主资源位应优先留给更可能改层级的候选；
- 因此本轮如果还继续给 `Rank 140` 补近义切片，边际价值很低。

本轮只补一件事：
> 把 `Rank 140` 的当前读法正式收口为 **balance-aware freeze** —— 后续比较 family 时，不再只看 `PBO`，而要把 **split 是否真的拆开** 一起作为默认读法。

---

## 已有 evidence（本轮不重跑，只复核）

来自 `reports/artifacts/pbo_cscv_honesty_gate/rank140_explicit_three_arm_family_board.csv` 的当前核心 family：

| family | strict arm | kept:veto | PBO | 读法 |
|---|---|---:|---:|---|
| Rank 137 | `confirm_window_12` | `545:273` | `0.0000` | 唯一真正过关的正例 family，但它说明的是 **exclusive pocket / family-level winner**，不是共享 honesty rule |
| Rank 125 | `rl_gate` | `459:365` | `0.5714` | split 可读性最好之一，但仍 `guard_failed` |
| Rank 111 | `same_window_only` | `105:93` | `0.7143` | 很平衡，但稳定性仍不够 |
| Rank 111 | `window_plus_timeout` | `113:85` | `0.8000` | 放宽 strict 后没有变得更可信 |
| Rank 112 | `basis_extreme_plus_oi_veto` | `120:2` | `0.3143` | PBO 看着低，但 arms 几乎没拆开，不能误读成“最好” |

### 本轮更新的人话口径
- `Rank 140` 不是全废；因为它至少留下了 `Rank 137` 这条 **family-level positive pocket**。
- 但 `Rank 140` 也不是即将 deploy 的 shared honesty layer；因为除了 `Rank 137` 外，其余已完成 families 不是 `guard_failed`，就是 split 虽好但稳定性依然不够。
- 尤其 `Rank 112` 这类 **低 PBO + 极端失衡 split**，现在应被默认视为 **不可直接晋级的伪亮点**。

因此，当前更稳的 desk 规则应是：
> **先看 family 是否真的拆成可解释的 kept/veto，再看 PBO；不能只按 PBO 排名。**

---

## 本轮 hard verdict

### 对 `Rank 140`
- 维持：`keep_P1 / active compare anchor`
- 继续冻结：`not default primary`
- 额外补充默认读法：`balance-aware board first, PBO second`

### 为什么是现在
因为最近两轮新 evidence 已经表明：
1. `Rank 144` 已被最小 clean replication 打回 `P0 / park`
2. `Rank 145` 已被 frozen-threshold A/B 收口到 `keep_P1 / budget used / no promote`
3. 这反过来说明 bot3 预算更应该继续给 **fresh reserve / next decisive compare**，而不是再把 `Rank 140` 拿来做近义补刀

所以这轮最诚实的做法不是“硬找新切片”，而是把 `Rank 140` 的保留条件写清楚，避免后面又被默认拖回主资源位。

---

## 轻量 scorecard
- `usefulness = medium`
- `time_stability = weak`
- `cross_asset_stability = medium`
- `cost_trade_stability = weak`
- `deployability = low`

### hard-fail flags
- `shared_core_is_negative`
- `positive_edge_is_family_specific_not_shared`
- `most_families_guard_failed`
- `pbo_only_ranking_is_misleading`
- `no_cheaper_decisive_cut_left_for_default_primary`

### recommended_action
- **`keep_P1`**

### why_now
把 `Rank 140` 留在 compare 位是合理的，但继续把它误当默认主位已经不合理；这轮用一页 freeze 把边界写死，能减少后续重复劳动。

### main_weakness
最强证据仍是 `Rank 137` 这种 family-specific pocket，而不是一个可共享、可直接 reader-facing 的 deployable honesty rule。

---

## 本轮最小 desk writeback（不强制修改 TODO）
若后续需要最小写回顶板，建议只保留一句：
- `Rank 140 = keep_P1 / active compare anchor / balance-aware freeze / not default primary`

本轮先不改 `docs/TODO.md`，因为 03:14 UTC 顶板证据已足够表达“退出默认 primary”；这轮新增的是读法澄清，不是层级变化。

## 交付
- 日志：`research/optimization_loop/2026-03-23_0526_rank140_balance_aware_freeze.md`
- 可见落点：通过 homepage index 刷新纳入最新 optimization log
