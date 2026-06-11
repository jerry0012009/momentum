# 2026-03-17 09:41 UTC · Rank 29 time stability check → P3 narrow paper pilot

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 先执行了 `Run 1` 守门：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- 结果：全 desk 继续是 `waiting_not_due`，没有 `due-now / overdue` lane；因此按 board 规则转到 `Scout Seat`。

## active Scout 边际价值比较（本轮前）
- `Rank 17 / Rank 2`：当前没有新的真实 `append/review need`，继续补近义 wiring 的边际价值低。
- `Rank 26 / 27 / 28`：已压回 `park / evidence pool`，不该重开。
- `Rank 29`：刚完成 `clean replication + no_overlap_guard`，而 board 明确只剩 **1 次 genuinely verdict-changing 的 P2 最小检查** 预算；它是当前最接近改变 seat judgment 的候选。
- 结论：本轮主资源继续给 `Rank 29`，不并行打开新候选。

## 本轮主点
- 执行 `Rank 29 trendline breakout navigator` 的那 1 次 `P2` 最小检查：**time stability（按时间顺序三等分）**。
- 检查目标：回答这条线是不是“一做时间切片就塌”的热像素；若不是，就直接给出 `升到 P3 narrow paper pilot / 压回 park` 的硬结论。

## 执行动作
1. 新增脚本：`scripts/build_rank29_time_stability_check.py`
2. 固定口径：
   - 继续固定使用 `BTC/ETH/SOL 120d 15m`
   - 继续固定主变体：`breakout_align_ge2`
   - 继续固定 `no_overlap_guard`
   - 不追新 bar，不改规则，不扩成重型 stability 包
   - 把现有 no-overlap trades 按时间顺序切成 `bucket_1 / bucket_2 / bucket_3`
3. 产物：
   - `reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/time_stability_bucket_summary.csv`
   - `reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/time_stability_overall_summary.csv`
   - `reports/site/factors/scout_rank29_trendline_breakout_navigator_15m/time_stability_check.html`
4. 同步更新：
   - `docs/TODO.md` 顶部 authoritative board
   - `Rank 29` 候选阶段与 `Next 3 bot3 runs`

## 关键结果（hard evidence）
### 1) 6bps 下三个时间桶都还活着
- `bucket_1`：跨资产 `mean_total_return≈+25.33%`，`positive_asset_ratio=3/3`
- `bucket_2`：跨资产 `mean_total_return≈+8.69%`，`positive_asset_ratio=3/3`
- `bucket_3`：跨资产 `mean_total_return≈+16.35%`，`positive_asset_ratio=3/3`

这说明它**不是**“只在某一小段时间幸运地热起来”的单点热像素。

### 2) 更高 friction 下的中段 bucket 明显转弱
- `10bps / bucket_2`：`mean_total_return≈+4.71%`，但 `positive_asset_ratio=1/3`
- `15bps / bucket_2`：`mean_total_return≈-0.06%`，`positive_asset_ratio=1/3`
- `15bps / bucket_3`：仍约 `+6.88%`，但只剩 `positive_asset_ratio=2/3`

这说明它也**不是**“所有时间段都同样干净”的完美候选；中段 bucket 应该挂进后续 `weekly review / red-watch`。

### 3) 与前两轮证据合并后的最诚实读法
- clean replication：`6bps≈+75.23%`、`positive_asset_ratio=3/3`、`mean_trades≈160`
- no-overlap 后：`6/10/15bps` aggregate 仍为正，`positive_asset_ratio` 维持 `3/3`
- time stability 后：`6bps` 的 `bucket_1/2/3` 全部继续存活

因此这条线当前更像：
- **可以进入 `paper-only narrow pilot`**
- 但必须带着 **`middle-bucket red-watch`** 前进
- 还不该被包装成“所有 friction / 所有时间段都一样稳”的更高等级候选

## 本轮 hard verdict
- **`promote to narrow paper pilot approved（P3）`**
- 口径补充：`paper-only narrow pilot + middle-bucket red-watch`
- 原因：
  1. `P2` 唯一允许的最小 verdict-changing 检查已经完成；
  2. 没有出现“一做时间稳定性就全面爆雷”的 decisive fail；
  3. 在更贴近当前 paper 口径的 `6bps` 下，三个时间桶都仍存活；
  4. 真正需要补的已经不再是 admission wording，而是 `paper ledger / monitoring / weekly review` 的最小接线。

## 对 board 的更新
- 已把 `Rank 29` 从 **`paper candidate pool（P2）`** 上调到 **`narrow paper pilot approved（P3）`**。
- 已把 `Next 3 bot3 runs` 改成：
  - `EMA` 继续按 `waiting_not_due` 处理；
  - 若继续认领 `Rank 29`，默认只允许补最小 `paper ledger / monitoring / refresh / weekly-review red-watch` 接线；
  - 若 `Rank 29 / Rank 17 / Rank 2` 都没有真实 `append/review need`，再回到 fresh intake。

## 验证 / 命令
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
- `python3 scripts/build_rank29_time_stability_check.py`

## 风险 / 边界
- 这次只做了 `P2` 允许的那 1 次最小检查，不代表 `Light Stability Pack` 已被完整展开。
- 当前结论依赖现有 `BTC/ETH/SOL 120d 15m` 样本；后续若切到更高 friction 或更新样本，中段 bucket 仍是需要优先盯住的 red-watch。
- 当前工作区存在大量与本轮无关的脏文件，因此本轮不安全混提。

## 下一步建议
1. 若下一轮继续认领 `Rank 29`，优先补 `paper ledger / monitoring / weekly-review red-watch` 的最小接线，而不是继续写 admission 文案。
2. 若 `Rank 29 / Rank 17 / Rank 2` 都没有真实 append need，则把 Scout 主资源切回新的 `paper / repo based 5m / 15m crypto` fresh intake。

## Commit hash
- 未提交。
- 原因：repo 内存在大量与本轮无关的脏文件与未跟踪产物；为避免混提，本轮只保留脚本 / artifact / 网页 / 日志 / TODO 的最小局部更新。
