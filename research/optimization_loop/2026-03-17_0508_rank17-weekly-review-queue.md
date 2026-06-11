# 2026-03-17 05:08 UTC · Rank 17 P3 最小 weekly-review 接线

## 为什么这轮选这个
- 先按 `TRADING DESK BOARD`：
  - `Paper Seat = EMA running paper / waiting_not_due`
  - `Live Seat = 暂空`
  - 因此本轮应回落 `Run 2 / Scout Seat`
- 先比较 active Scout 候选边际价值（只看当前仍 active 的 `P3`）：
  - `Rank 17`：`P3 narrow paper pilot (ETH+SOL only)`，已有 `refresh_history / monitoring_board / seed_rows`，但还缺一个把 `bucket watch` 直接落成操作队列的最小 review 接线
  - `Rank 2`：同为 `P3`，当前未见新的明确 append/review 缺口
- 因此本轮主资源给 `Rank 17`，做 **1 个最小且可部署的 P3 接线**，不再开新候选

## 本轮主点 + 紧邻子点
- 主点：为 `Rank 17` 补 `P3` 合法的 weekly review 队列 artifact
- 紧邻子点：把 `TODO` 顶板与 `2k` 条目同步到最新状态，明确“这是 P3 维护，不改席位判断”

## 做了什么
### 1) 新增 deployable artifact
新增：
- `reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_weekly_review_queue.csv`

生成逻辑（全复用现有历史样本，不追新 bar）：
- 输入：
  - `narrow_paper_pilot_ethsol_refresh_history.csv`
  - `narrow_paper_pilot_ethsol_monitoring_board.csv`
- 规则：
  - 只取 `scope_tag = narrow_paper_pilot_eth_sol_only`
  - 把 `weak_time_buckets`（`bucket_1 / bucket_2`）展开成可执行队列行
  - 固化 `operator_action = append_weekly_review_row_keep_ethsol_narrow_pilot`

队列结果（3 行）：
- `ETH-USD / bucket_1 / P3_review_now`
- `SOL-USD / bucket_1 / P3_review_now`
- `SOL-USD / bucket_2 / P3_review_now`

### 2) 同步作战板可见口径
更新：
- `docs/TODO.md`

更新点：
- `Next 3 bot3 runs` 顶部 override 增补：
  - `Rank 17` 本轮已补 `weekly review queue`，属于 `P3` 合法维护，不改变 `paper-only narrow pilot` 边界
- `2k. Rank 17 ...` 条目追加 artifact 说明：
  - 已补 `narrow_paper_pilot_ethsol_weekly_review_queue.csv`

## 本轮 hard verdict
- `Rank 17` 仍维持：**`P3 / narrow paper pilot approved（ETH+SOL only）`**
- 本轮动作性质：**最小 paper ledger/monitoring/review 接线完成**
- 不触发升降级，不改 `Live Seat`，不改 `BTC excluded red-watch` 边界

## 最小验证
1. 产物存在：
   - `reports/artifacts/scout_pullback_recovery_confirmation_15m/narrow_paper_pilot_ethsol_weekly_review_queue.csv`
2. 队列内容检查：
   - 仅 ETH/SOL
   - 仅 `bucket_1/2` watch 行
   - `operator_action` 固定为 weekly review append
3. `docs/TODO.md` 已写回：
   - 顶部 override 补充本轮 P3 接线说明
   - `2k` 条目补充 artifact 落点

## 风险 / 边界
- 本轮没有做新的 alpha claim、没有重跑重下载、没有扩写新框架
- 本轮只做 `P3` 允许的最小接线，避免继续磨 closeout 文案
- 若后续 1~2 轮 review 队列执行未爆雷，仍按板子规则维持 `narrow paper pilot` 节奏

## 网页可见落点
- `docs/TODO.md` 顶部 `TRADING DESK BOARD / Next 3 bot3 runs`
- 首页索引将在本轮结尾刷新

## Git / 提交
- 本轮未提交
- 原因：工作区有大量与本轮无关的脏文件 / 未跟踪文件，避免混提
