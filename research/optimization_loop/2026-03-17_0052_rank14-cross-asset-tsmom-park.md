# 2026-03-17 00:52 UTC｜Scout Seat：Rank 14 cross-asset TSMOM confirmation gate（park）

## 为什么这轮选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- `Run 1 / Paper Seat`：`EMA` 上一轮已完成 crypto due-now refresh，当前回到 `waiting_not_due`，这轮不能停在 waiting-window 空转；
- `Run 2 / Scout Seat`：当前默认主资源位；
- `Run 3 / tiny-live plumbing`：只有在 `Scout Seat` 也没有合格动作时才回退。

本轮先比较 active Scout 候选的边际价值：

1. `Rank 2 combo_all`
   - 仍是 `narrow paper pilot approved`；
   - 但当前没有新的真实 `append/review need`，继续做大概率又会滑回近义 wiring。
2. `Rank 7 ~ Rank 13`
   - 都已完成 `clean replication + Light Stability Pack` 并压回 `park / evidence pool`；
   - 当前没有新的数据源 / 新 spec / bot2 重开指令，不该继续吃默认主资源。
3. 新鲜候选里，`Pitkäjärvi, Suominen, Vaittinen (2020)` 这条 `cross-asset TSMOM confirmation gate`
   - 仍是 paper-based 逻辑，可直接写成清楚的 `trade on / trade off`；
   - 能完全复用现有 `Binance 120d 15m` cache；
   - 能在一轮内直接回答：**单币 momentum 再叠 peer-basket 共振过滤，能不能更快把 15m crypto 动量从 evidence 推向 candidate。**

因此这轮主点定为：**把 cross-asset TSMOM confirmation gate 从 paper digest 直接推进到最小 clean replication，并在同一轮给出 `paper candidate / park` verdict。**

## 本轮主点（1 个）
- 新增脚本：`scripts/build_cross_asset_tsmom_gate_clean_replication.py`
- 用现有 `BTC/ETH/SOL` 的 `120d / 15m` cache，把下面几档最小 clean-room 规则一次跑完：
  - `baseline_sign_mom`
  - `peer_1h_gate`
  - `peer_4h_gate`
  - `peer_dual_gate`
  - `peer_dual_strict`
- clean-room 读法：
  - `mom_16 = close / close.shift(16) - 1`
  - baseline：`mom > 0` 做多，`mom < 0` 做空
  - peer gate：其余两币的 peer basket 回报必须与本币方向同向
  - `peer_1h_gate` 看近 `4` 根 15m 收益和；`peer_4h_gate` 看近 `16` 根；`peer_dual_gate` 两档都要同向
  - 成本按持仓切换收 `6/10/15/20 bps/side`

## 紧邻子点（1 个）
- 最小回写 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `scout_seat_fast_cycle_crypto_shortlist_v1.csv`：
  - 新增 `Rank 14 cross-asset TSMOM confirmation gate`
  - 明确它已完成 `clean replication + Light Stability Pack`
  - 并把当前 hard verdict 回写为 `park / evidence pool`

## 产物 / deployable artifact
### 新脚本
- `scripts/build_cross_asset_tsmom_gate_clean_replication.py`

### 新 artifacts
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/bar_level_simulation.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/nav_series.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/asset_summary.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/overall_summary.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/primary_asset_summary.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/time_stability_drycheck.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/time_stability_detail.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/parameter_stability_drycheck.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/parameter_stability_detail.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/cross_asset_stability_drycheck.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/cost_trade_stability_drycheck.csv`
- `reports/artifacts/scout_cross_asset_tsmom_gate_15m/clean_replication_meta.csv`

### 网页可见落点
- `reports/site/factors/scout_cross_asset_tsmom_gate_15m/report.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`（Control Tower 会同步）

## 最小验证
已执行：

1. `python3 scripts/build_cross_asset_tsmom_gate_clean_replication.py`
2. 读取并核对：
   - `clean_replication_meta.csv`
   - `overall_summary.csv`
   - `primary_asset_summary.csv`
   - 四张 `Light Stability Pack` gate 表
3. 确认 `docs/TODO.md` 与 `scout_seat_fast_cycle_crypto_shortlist_v1.csv` 已写回 `Rank 14`

执行结果：
- 脚本成功输出：`[ok] cross-asset tsmom gate clean replication generated`

## 硬结论（hard verdict）
### Primary variant
- `winner / primary variant`：`peer_dual_gate`
- `primary cost`：`6 bps / side`

### 关键数值
来自 `reports/artifacts/scout_cross_asset_tsmom_gate_15m/clean_replication_meta.csv` 与相关 summary：

- `mean_total_return ≈ -87.28%`
- `positive_asset_ratio = 0/3`
- `mean_trade_events ≈ 3600`
- `mean_max_drawdown ≈ -87.71%`
- 三个资产分别约：
  - `BTC ≈ -89.37%`
  - `ETH ≈ -86.06%`
  - `SOL ≈ -86.40%`

对比看，cross-asset gate 不但没有救活单币 momentum，连 baseline `sign(momentum)`（约 `-78.35%`）都不如，说明这条最小共振过滤在当前 15m crypto 口径下更像负增量，而不是确认层 alpha。

## Light Stability Pack
### 1) 时间稳定性
- `positive_bucket_floor = fail`（`0/3 positive buckets`）
- `worst_bucket_watch = watch`（最差 bucket 约 `-56.05%`）

### 2) 参数稳定性
- `neighbor_positive_floor = fail`（`0/5 positive configs`）
- `trade_density_floor = pass`（不是因为样本太薄才负）

### 3) 跨标的稳定性
- `positive_asset_floor = fail`（`0/3 positive assets`）
- `worst_asset_watch = watch`（最差资产约 `-89.37%`）

### 4) 成本 / 交易数稳定性
- `positive_cost_levels = fail`（`0/4 positive cost levels`）
- `worst_cost_watch = watch`（20bps 下约 `-99.93%`）
- `trade_floor = pass`（也不是因为过滤后几乎没交易）

## 这轮最诚实的 desk 读法
- 这条线**不是**一个接近 `paper candidate` 的快筛 winner；
- 更像一个说明“**单币动量再叠 peer-basket 共振过滤，也不足以救活 15m crypto sign-momentum**”的反例证据；
- 因此当前最诚实 verdict 是：
  - **`Rank 14 cross-asset TSMOM confirmation gate` → `park / evidence pool`**
  - 当前只适合作为后续 `EMA / TSMOM confirmation` 的参考证据，**不进入 `paper candidate pool`**。

## 对主线的意义
- 这轮没有改变 `Paper Seat = EMA` 的席位判断；
- 也没有给 `Live Seat` 送出新的 promoted candidate；
- 但它确实把一个 paper-based fast-lane 候选在一轮内完成了闭环：
  - `source intake -> clean replication -> Light Stability Pack -> park`
- 这比继续在 `Rank 2` 上补近义 wiring 更符合当前 board 的资源分配规则。

## 风险 / 边界
1. 这条 clean-room 规则是论文设计原则迁移，不是 faithful 复刻原论文的跨国家资产月频实现；
2. 当前实现只用了 `BTC/ETH/SOL` 三币 peer basket，所以结论应解读成：
   - “在这组主流币、这个 120d / 15m 样本、这层最小 peer-basket gate 下，不值得继续推进”；
   - 不是“所有 cross-asset confirmation 都永远没用”。
3. 如果后续要重开，最合理的方向应是把它当作 **已有方向层的稀疏 confirmation** 或换更合理的 leader/follower universe，而不是继续把当前三币同频 gate 当独立 candidate 打磨。

## Git / 提交
- 未提交。
- 原因：工作区里存在大量与本轮无关的脏文件与未跟踪文件，不适合安全 selective commit。

## 下一轮建议
- 若 `EMA` 仍是 `waiting_not_due`：继续 `Scout Seat`，但默认应再换一条新的 paper / repo based 5m/15m crypto 候选，而不是重开 `Rank 14`。
- `Rank 2` 仍只在出现真实 `append/review need` 或会改变 paper verdict 的最小检查时再继续认领。
- `Rank 14` 当前默认不再占主资源，除非 bot2 明确要求把它当 cross-asset confirmation 反例重看。
