# 2026-03-16 18:53 UTC｜Rank 4b time stability：窄重开补完唯一决策刀后压回 `park`

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD` 检查：`EMA` 仍处于 `waiting_not_due`，所以不能在 Paper Seat 空转，默认切到 `Scout Seat`。
- 当前 active Scout 候选里：
  - `Rank 2 combo_all` 已被 desk 明确降成 **`narrow paper pilot approved`** 后的最小 wiring / refresh 对象，不应再继续占用默认 scout 主资源去打磨 closeout 近义卡；
  - `Rank 4b crypto stat-arb reframe` 上一轮刚完成 `clean replication v2`，而且上一轮口径已经明确：`one_more_light_check` 只允许作为一次性例外，**下一轮必须在 `promote / park` 间二选一**。
- 因此本轮主点固定为：给 `Rank 4b` 补完唯一允许的一刀 `Light Stability Pack`，并直接形成 hard verdict。

## 先检查了什么
- `git status --short`：repo 内外存在大量与本轮无关的脏文件 / 未跟踪文件，因此本轮仍不适合做安全 selective commit。
- 最近 runs：`18:22` 做了 `Rank 4b` reframe sanity scan；`18:38` 做了正式 `clean replication v2`；中间 `Rank 2` 连续多轮主要新增的是 replay / receipt / closeout 类最小接线，边际价值已明显低于一个能直接改变 scout verdict 的检查。
- 当前 Scout 边际价值比较：
  - `Rank 2`：再认领默认只能补 paper wiring / review；
  - `Rank 4b`：只差一刀就能从 `one_more_light_check` 进入明确 `promote / park`；
  - 因此本轮资源给 `Rank 4b` 更符合 desk 主线。

## 本轮做了什么
1. 复用现成 `reports/artifacts/scout_crypto_pairs_stat_arb_15m_rank4b/trades.csv`，不重拉数据，不扩 universe。
2. 扩充脚本 `scripts/build_crypto_pairs_stat_arb_rank4b_report.py`：
   - 新增 `time_stability_check.csv` artifact；
   - 用交易序列的 `time_tercile` 与 `calendar_month` 两种切片，检查 surviving pairs 的时间稳定性；
   - 把这轮时间稳定性结论直接并入 reader-facing 报告页；
   - 将 report headline / hard verdict 从上轮的 `one_more_light_check` 推进到本轮的 `park` 或 `paper_candidate` 二选一。
3. 重新运行：
   - `python3 scripts/build_crypto_pairs_stat_arb_rank4b_report.py`
4. 同步更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
   - 将 `Rank 4b` 从“唯一允许的窄重开动作”改写为“窄重开已完成并关闭，当前默认回到 `park / evidence pool`”。

## 验证 / 关键证据
生成 / 刷新的核心产物：
- `reports/artifacts/scout_crypto_pairs_stat_arb_15m_rank4b/time_stability_check.csv`
- `reports/artifacts/scout_crypto_pairs_stat_arb_15m_rank4b/trial_meta.csv`
- `reports/site/factors/scout_crypto_pairs_stat_arb_15m_rank4b/report.html`

关键时间稳定性结果（基于上轮 surviving positive pairs）：

### `BTC/SOL`
- overall `cumulative_net_return ≈ +0.74%`
- 但 `time_tercile`：
  - `tercile_1 ≈ +1.17%`
  - `tercile_2 ≈ +0.62%`
  - `tercile_3 ≈ -1.04%`
- 且 `calendar_month`：
  - `2026-01 ≈ +0.49%`
  - `2026-02 ≈ +1.46%`
  - `2026-03 ≈ -1.20%`

### `ETH/SOL`
- overall `cumulative_net_return ≈ +2.28%`
- 但 `time_tercile`：
  - `tercile_1 ≈ +1.51%`
  - `tercile_2 ≈ +2.38%`
  - `tercile_3 ≈ -1.58%`
- 且 `calendar_month`：
  - `2026-01 ≈ +1.01%`
  - `2026-02 ≈ +1.99%`
  - `2026-03 ≈ -0.72%`

### 读法
- `BTC/SOL`、`ETH/SOL` 虽然 overall first pass 转正，但**最近 tercile 与最新月份都一起转负**；
- 这说明 surviving pocket 主要来自样本前段，而不是近期仍站得住；
- 对当前这种 trade count 只有 `15~20` 的快速 scout 候选来说，这已经足够把本轮 verdict 更诚实地压回 `park`，而不是硬升成 `paper candidate`。

## 硬结论（本轮 desk 口径）
- `Rank 4` 原 verdict 继续保持 `park`；
- `Rank 4b` 允许的唯一窄重开已完成：
  - `clean replication v2` 通过；
  - `time stability` 不通过 desk promotion 口径；
- 因此本轮 hard verdict：**`Rank 4b = park / evidence pool`**。
- 当前默认**不把 stat-arb 继续留在 Scout 主资源位**；除非后续出现：
  1. 新的 pair universe，
  2. 新的数据源，
  3. 或 bot2 明确点名新的更强 spec。

## 对 TRADING DESK BOARD 的影响
- `Run 2` 里的 `Rank 4b` 已从“可优先执行的窄重开动作”改成“已完成且关闭的 evidence pool”；
- 后续 `Scout Seat` 默认应继续比较其他 active 候选 / 新 intake 的边际价值，而不是再磨同一条 stat-arb 线。

## 最小验证
已执行：
```bash
python3 scripts/build_crypto_pairs_stat_arb_rank4b_report.py
```
结果：脚本成功完成，并生成更新后的 artifact / site page。

## 编辑 fallback 记录
- 在改 `scripts/build_crypto_pairs_stat_arb_rank4b_report.py` 的 HTML section 时，`edit` 曾因 exact text 不匹配失败；
- 已按要求立即 fallback 到 `read + python 脚本定位插入` 的更稳健改写方式，随后成功完成修改；
- `docs/TODO.md` 第一处替换也出现过一次 exact text 不匹配，随后通过重新 `read` 精确定位后完成修正。

## Git / 提交
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
