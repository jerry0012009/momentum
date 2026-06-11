# bot3 optimization loop — Rank139 thr_mult {0.6, 0.8} + scorecard

时间：2026-03-21 23:55 UTC

## 本轮按 desk board 的 Next 3 bot3 runs 顺序执行

### Run 1 — EMA due-check first（Paper Seat）
- 执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due --skip-build`
- 结果：**waiting_not_due（无 due-now / overdue lane）**
  - 最近到点：Crypto 1d+1wk（BTC/ETH/SOL）≈ 23.8h 后
  - 创业板ETF 1d ≈ 2.3d 后
  - 贵州茅台 1d+1wk ≈ 2.3d 后
- 结论：按规则切换到 **Scout Seat**，不做伪 refresh。

### Run 2 — Scout Seat：把 Rank139 从 P2 推向最小决策包（只做 1 个动作）
目标：固定 baseline（BTC/ETH/SOL 15m），仅比较 `thr_mult ∈ {0.6, 0.8}`，并补 1 页轻量 scorecard。

- 执行：`python3 scripts/build_rank139_cusum_event_bar_confirm_veto_clean_replication.py`
- 产物：
  - `reports/artifacts/scout_rank139_cusum_event_bar_confirm_veto_15m/summary_by_arm.csv`
  - `reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`

#### 关键对比（只摘 thr=0.6 vs 0.8；成本 6bps）

基线（baseline，三组阈值相同）：
- trades=141
- mean_net@6bps = **-0.1548%**（负）

thr_mult=0.6：
- **veto_opp_dir**：trades=66，retention=0.468，mean_net=**+0.1957%**，pos_ratio=0.485，timeout(no_event)=0.212
- **confirm_same_dir_only**：trades=52，retention=0.369，mean_net=**+0.1909%**，pos_ratio=0.500

thr_mult=0.8：
- **veto_opp_dir**：trades=70，retention=0.496，mean_net=**+0.3423%**，pos_ratio=0.514，timeout(no_event)=0.386
- **confirm_same_dir_only**：trades=43，retention=0.305，mean_net=**+0.5363%**，pos_ratio=0.605

直觉解读（用于决策，不装懂）：
- `thr=0.8` 更“严格”，**留下的交易更少**（retention 更低），但留下来的质量更高（mean_net 更高、正收益占比更高）。
- `thr=0.6` 更“宽松”，**保留更多交易**，但增量较弱。

#### Scout Promotion Scorecard（5项 0~3 分 + hard-fail flags）
对象：Rank139 / CUSUM event-bar confirm/veto gate（作为 post-entry confirm/veto layer）

Hard-fail flags（硬伤一票否决）：
- Leakage/未来函数：**未发现（设计上仅使用 entry 之后 1m close 的阈值穿越；需在 P3 再做一次代码审计抽查）**
- 规则不可执行：**否（规则可在交易后 45min 内给出 confirm/veto）**
- post-cost collapse：**否（当前增量是在 net@6bps 层体现）**

五项打分（0~3）：
1) 诚实性（trade-on/off、时序、可复现）：**3/3**（已通过 clean replication；严格 post-entry）
2) 增量强度（相对 baseline）：**3/3**（baseline -0.1548%，confirm@0.8 +0.5363%）
3) 稳健性（参数敏感/是否只靠一点点巧合）：**2/3**（0.6→0.8 方向一致；但仅两点比较，仍需最小 OOS/时间切片 sanity）
4) 执行可落地（延迟、频率、复杂度）：**2/3**（45min latency 可接受；但 timeout 比例在 0.8 下较高，意味着很多交易不会触发事件 → 需要清晰 fallback 口径）
5) 监控可解释（出问题能定位）：**2/3**（事件=阈值穿越易解释；但需要把“timeout/no-event”当作一类显式状态写进监控）

合计：**12/15** → 建议：**promote_P3（narrow paper pilot）**，但要求把“timeout/no-event 的处理口径”写进 paper spec。

### Run 3 — 硬结论分支（本轮选择 1 个）
选择：**promote_P3（narrow paper pilot）**

最小 paper spec（只写接线口径，不在本轮铺开实现）：
- 基线 entry：维持现有 15m baseline setups（ema_psar_long / fib_retest_long / breakout_short）。
- Post-entry gate：优先采用 **confirm_same_dir_only @ thr_mult=0.8** 作为“更严格的放行”。
- latency window：45min（1m closes）；若 **timeout/no-event**：
  - 口径 A（更保守）：视为 **不确认 → 直接 veto/不交易**（更贴近 confirm-only 的语义）；
  - 口径 B（更中性）：视为 **不加成也不否决 → 走 baseline**。
  - 本轮建议：先从 **口径 A** 做纸上试跑（可最大化防伪增量），并把 timeout 比例作为核心监控项。

需要在下一轮（或另起任务）完成的最小接线：
- 给 P3 lane 增加 1 个可见监控页：每日/每 20m 刷新展示 trades、retention、timeout 占比、net@6bps。

## 网页可见落点
- `reports/site/factors/scout_rank139_cusum_event_bar_confirm_veto_15m/report.html`

