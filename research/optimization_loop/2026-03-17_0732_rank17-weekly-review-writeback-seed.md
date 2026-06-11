# 2026-03-17 07:32 UTC · Rank 17 weekly review writeback seed

## 为什么这轮选这个
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs`。
- `Paper Seat / EMA` 的 A 股 due-follow-up 已在 `07:04 UTC` 如实消化，当前全 desk 没有新的 `due-now / overdue` lane，因此本轮不能继续停在 `Run 1`。
- 再比较当前 active Scout 候选的边际价值：
  1. `Rank 17` 已是 `P3 / narrow paper pilot approved（ETH+SOL only）`，而且现成 `continuity_snapshot.csv` 明确显示两条绿腿都处于 `queued_weekly_review / append_ready_green`；
  2. `Rank 2` 这轮没有看到同等明确的 `append/review need` 证据；
  3. 因此这轮最诚实的主点不是 fresh intake，而是先把 `Rank 17` 已经排队的 `weekly review` 压成真正可 append 的 writeback seed。

## 本轮主点 + 紧邻子点
- 主点：把 `Rank 17` 的 `weekly review queue` 压成可直接续写的 `writeback seed rows`。
- 紧邻子点：把这份 `writeback seed` 同步挂到 reader-facing factor 页，并把 desk 顶部 override 改成“本轮已消化 Rank 17 当前最小 P3 need；若 `Rank 2` 仍无新 need，则下轮默认切 fresh intake”。

## 先过诚实边界
1. **trade on / trade off 不变**
   - 仍是已冻结的 `pullback recovery confirmation` 规则：`5m/15m baseline momentum 同向 + 最近 2 根缩量回调 + 当前 bar 放量突破前 1 根高/低点`。
2. **不追新 bar / 不改规则 / 不改 scope**
   - 只复用已有的：
     - `narrow_paper_pilot_ethsol_weekly_review_queue.csv`
     - `narrow_paper_pilot_ethsol_continuity_snapshot.csv`
   - `ETH+SOL-only` 的 narrow paper pilot 边界不变；`BTC` 继续保留在 excluded red-watch。

## 做了什么
### 1) 新增脚本
- `scripts/build_pullback_recovery_weekly_review_writeback_seed.py`

输入：
- `reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_weekly_review_queue.csv`
- `reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_continuity_snapshot.csv`

输出：
- `reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_weekly_review_writeback_seed.csv`
- `reports/site/factors/scout_pullback_recovery_confirmation_15m/weekly_review_writeback_seed.html`

### 2) 产出 append-ready writeback rows
共 3 行：
- `ETH-USD | bucket_1`
- `SOL-USD | bucket_1`
- `SOL-USD | bucket_2`

统一保持：
- `operator_action = append_weekly_review_writeback_seed`
- `writeback_target = narrow_paper_pilot_ethsol_refresh_history.csv`
- `gate_action = continue_paper_and_append_refresh_review`
- `promotion_boundary = paper_only_narrow_pilot_until_new_live_clearance`

### 3) 同步 reader-facing 页面
- 更新 `reports/site/factors/scout_pullback_recovery_confirmation_15m/report.html`
- 新增页面：`reports/site/factors/scout_pullback_recovery_confirmation_15m/weekly_review_writeback_seed.html`

### 4) 写回 desk 顶部板子
- 更新 `docs/TODO.md` 顶部 `authoritative override`：
  - 明确写清 `Rank 17` 当前这次 queued weekly review 已被消化成 `writeback seed`；
  - 因此后续若 `Rank 2` 仍无真实 need，则默认应直接切 fresh intake，而不是继续围着 `Rank 17 / Rank 26` 打磨近义接线。
- 同时在 `Rank 17` 条目下追加 `2026-03-17 07:32 UTC` 最新补充，记录这次 P3 writeback seed 已就位。

## 关键结果（hard verdict）
### 这轮没有改变 Rank 17 的席位判断
- `Rank 17` 仍然只是：**`narrow paper pilot approved（ETH+SOL only）`**
- `BTC` 仍然是：**`park / excluded red-watch leg`**
- 没有偷升 `tiny-live`，也没有用文档包装成更高等级。

### 这轮真正补齐的，是可部署的 P3 append artifact
- `narrow_paper_pilot_ethsol_weekly_review_writeback_seed.csv` 让 `queued_weekly_review` 不再只停在“需要做”的状态，而是变成同一张 narrow-paper ledger 可直接 append 的种子行。
- 它把 `ETH/SOL` 的当前 watch 具体压成：
  - `ETH = bucket_1`
  - `SOL = bucket_1 / bucket_2`
- 同时保留了 `watch_components = btc_exclusion_watch, time_pocket_watch`，确保后续不会把 `BTC` 弱腿洗回 pilot headline。

## 一句话结论
**这轮不是继续磨 Rank 17 的说明文字，而是把它已经排队的 weekly review 真正落成可 append 的 writeback seed；因此当前这条 P3 的最小合法维护已被如实消化。若 `Rank 2` 仍无真实 need，下一轮就该切 fresh intake。**

## 最小验证
已执行并通过：
1. `python3 -m py_compile scripts/build_pullback_recovery_weekly_review_writeback_seed.py`
2. `python3 scripts/build_pullback_recovery_weekly_review_writeback_seed.py`
3. `sed -n '1,12p' reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_weekly_review_writeback_seed.csv`
4. `sed -n '1,80p' reports/site/factors/scout_pullback_recovery_confirmation_15m/weekly_review_writeback_seed.html`

## reader-facing 落点
- 页面：`reports/site/factors/scout_pullback_recovery_confirmation_15m/weekly_review_writeback_seed.html`
- 主页入口：`reports/site/factors/scout_pullback_recovery_confirmation_15m/report.html`
- Desk 指挥板：`docs/TODO.md` 顶部 `TRADING DESK BOARD`

## 风险 / 边界
- 没有追最新 bar
- 没有重跑重型数据下载
- 没有改策略规则 / 参数 / scope
- 没有同时打开新的 fresh candidate
- 这轮只消化了 `Rank 17` 当前已经存在的 P3 review queue，不代表它接近 `tiny-live`

## Git
- 工作区仍存在大量与本轮无关的脏文件 / 未跟踪文件；本轮不做 commit，避免混提。
