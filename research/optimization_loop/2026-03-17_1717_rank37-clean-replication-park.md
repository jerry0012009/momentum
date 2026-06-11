# 2026-03-17 17:17 UTC · Rank 37 classic sparse TSMOM clean replication park

## 本轮归属
- Desk lane：`Run 2 / Scout Seat fresh intake -> clean replication`
- 触发原因：
  - `Paper Seat / EMA` 当前仍是 `waiting_not_due`，最新 due guardrail 没有新的 `due-now / overdue` lane；
  - `Rank 17 / Rank 2 / Rank 29` 都属于 `P3 continuity`，当前没有真实 `append/review need`，且不该继续消耗当日预算；
  - `Rank 30~36` 当前允许动作都已消耗并 `park`；
  - 上一轮刚把 `Rank 37 / classic sparse TSMOM / own-past persistence pocket` 认领进 `clean replication queue`，按指挥板本轮只允许做这 **1 次最小 clean replication**，不给它额外预算。

## 开工前检查
- 已先读：`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做 selective 写入，不混提
- 当前席位判断：
  - `Run 1 / EMA paper`：当前无新的 `due-now / overdue`
  - `Run 2 / Scout Seat`：`Rank 37` 是当前唯一还没消费掉的 fresh intake 最小 clean replication
  - `Run 3 / tiny-live plumbing`：本轮不该抢主资源

## 本轮主点 + 紧邻子点
- **主点**：完成 `Rank 37 / classic sparse TSMOM` 的最小 clean replication
- **紧邻子点**：把 hard verdict 写回 `docs/TODO.md` 顶部 authoritative override，并同步 reader-facing factor 页面

## 为什么选这条线
上一轮已经把问题钉得很清楚：
- 当前 15m crypto 动量家族失败，到底是 own-past persistence 本身就不成立，
- 还是我们之前拿得太快、太密、太重叠。

所以本轮最值得做的，不是再补解释页，而是把这条 `slow / sparse / no-overlap` 口径真的跑一遍，快速得到 **继续给预算还是直接 park** 的硬结论。

## 本轮做了什么
### 1) 新增最小 clean replication 脚本
新增：
- `scripts/build_rank37_classic_sparse_tsmom_clean_replication.py`

冻结后的 clean-room 口径：
- 样本：`BTC / ETH / SOL | Binance 120d | 15m`
- 执行：`signal bar close -> next-bar open` 入场，固定持有，默认 `no-overlap`
- 只比较三档最小规则：
  1. `slow_4h_sign_hold_4h`
  2. `slow_12h_sign_hold_8h`
  3. `slow_4h_12h_agree_hold_8h`
- 先只看：`post_cost_return / positive_asset_ratio / trade_count / time-pocket honesty`

### 2) 生成 artifact + 网页落点
执行：
- `python3 scripts/build_rank37_classic_sparse_tsmom_clean_replication.py`

生成：
- `reports/artifacts/scout_rank37_classic_sparse_tsmom_15m/overall_summary.csv`
- `reports/artifacts/scout_rank37_classic_sparse_tsmom_15m/asset_summary.csv`
- `reports/artifacts/scout_rank37_classic_sparse_tsmom_15m/time_bucket_summary.csv`
- `reports/artifacts/scout_rank37_classic_sparse_tsmom_15m/primary_trades_6bps.csv`
- `reports/site/factors/scout_rank37_classic_sparse_tsmom_15m/report.html`

### 3) 写回交易台指挥板
更新：
- `docs/TODO.md`

写回内容：
- 顶部 authoritative override 改成：`Rank 37` 的最小 clean replication 已消耗，且当前 hard verdict = `park / evidence pool`
- `Rank 37` 条目从 `admit_to_clean_replication_queue` 改为 **`park / evidence pool`**
- 下一手默认仍留在 `Run 2 / Scout Fast Lane`，继续认领新的本地 `paper / repo based 5m / 15m crypto` fresh intake；不是直接回头磨 `P3 continuity`

## 验证 / 证据
### 主结果（6bps/side）
- `slow_12h_sign_hold_8h`：`mean_total_return≈-37.61%`、`positive_asset_ratio=0/3`、`mean_trades≈347.0`
- `slow_4h_sign_hold_4h`：`mean_total_return≈-35.60%`、`positive_asset_ratio=0/3`、`mean_trades≈677.0`
- `slow_4h_12h_agree_hold_8h`：`mean_total_return≈-35.24%`、`positive_asset_ratio=0/3`、`mean_trades≈330.3`

### time-pocket honesty（主变体）
- `bucket_1≈-34.30%`
- `bucket_2≈-14.78%`
- `bucket_3≈+11.28%`

更直白地说：
- 把 pocket 放慢、放稀、去重叠之后，并没有救回 own-past persistence；
- 它不是“交易数太少才显得不差”，恰恰相反，交易数并不稀薄，却依然三腿全负；
- 因此这轮已经足够回答是否值得继续给默认预算：**不值得。**

## Hard verdict
- `Rank 37 / classic sparse TSMOM / own-past persistence pocket` → **`park / evidence pool`**

一句话结论：
- **慢一点、稀一点、少重叠，并没有把 classic TSMOM 在当前 15m crypto 样本里救活。**

证据怎么支持：
- **三档最小变体在 `6bps/side` 下全部跨资产转负，`positive_asset_ratio=0/3`，而主变体 time-pocket 也只有最后一段为正，因此不满足继续晋级的最小 admission 味道。**

## 风险 / 边界
- 这仍是当前 desk 的最小 clean-room 映射，不是对原论文全市场结论的反驳；
- 但对当前 `BTC / ETH / SOL 120d 15m` fast-lane 来说，已经足够说明：这条线不该继续占默认 Scout 预算；
- 后续若要重开，必须有新的 genuinely verdict-changing 证据，而不是再做近义 micro-slicing。

## 最小验证
已执行：
- `python3 scripts/build_rank37_classic_sparse_tsmom_clean_replication.py`

已抽查：
- `reports/artifacts/scout_rank37_classic_sparse_tsmom_15m/overall_summary.csv`
- `reports/artifacts/scout_rank37_classic_sparse_tsmom_15m/asset_summary.csv`
- `reports/artifacts/scout_rank37_classic_sparse_tsmom_15m/time_bucket_summary.csv`
- `reports/site/factors/scout_rank37_classic_sparse_tsmom_15m/report.html`
- `docs/TODO.md`

结果：
- clean replication 脚本成功退出（code 0）
- artifact 与 reader-facing factor 页面已落地
- `TODO` 顶部排班与 `Rank 37` 状态已同步

## 下一步建议
- 继续留在 `Run 2 / Scout Seat`，从剩余 `paper / repo based 5m / 15m crypto` seeds 里再认领 1 条新的 `fresh intake`
- 默认不要回头磨 `Rank 37` 的近义说明页，也不要继续给它额外 clean check 预算
- 只有本地 shortlist 这一轮确实拿不到合格 source，才允许回退到 `Run 3 / tiny-live plumbing`

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提
