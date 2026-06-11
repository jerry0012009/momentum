# 2026-03-17 16:53 UTC · Rank 36 TSM vs drift clean replication

## 本轮归属
- Desk lane：`Run 2 / Scout Seat`
- 触发原因：
  - `Paper Seat / EMA` 当前仍是 `waiting_not_due`，没有新的 `due-now / overdue` lane；
  - `TRADING DESK BOARD` 顶部 authoritative override 已明确：上一轮刚认领的 `Rank 36 / recent-return sign vs history-drift honesty gate` 是当前默认下一手；
  - `Rank 17 / Rank 2 / Rank 29` 的 `P3 continuity` 继续由专属 cron + 状态页托管，本轮不应再消耗 continuity 预算；
  - `Rank 30~35` 与 `Rank 6` 已完成当前允许动作并 park，因此本轮主资源只认领 `Rank 36` 的 **1 次最小 clean replication**。

## 开工前检查
- 已先读：`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做 selective 写入，不混提
- 当前 seat 读法：
  - `Run 1 / EMA`：waiting_not_due
  - `Run 2 / Scout`：`Rank 36` 是唯一刚 admitted 且仍有真实可执行动作的本地 fast-lane 候选
  - `Run 3 / tiny-live plumbing`：只有当 `Rank 36` 也被证明不合格时才允许回退

## active Scout 边际价值比较
- `P3 continuity（Rank 17 / 2 / 29）`：当前没有真实 `append/review need`，且有日总预算 hard cap，不该占本轮主资源。
- 已 park 线（`Rank 30~35`、`Rank 6`）：当前都没有新的 genuinely verdict-changing check；继续重开只会重复 closeout。
- `Rank 36`：刚完成 source intake，能直接复用 `BTC/ETH/SOL 120d 15m` cache 做 1 次 cheap honesty gate clean replication；边际价值最高。

## 本轮主点 + 紧邻子点
- **主点**：`Rank 36 / recent-return sign vs history-drift honesty gate` 最小 clean replication
- **紧邻子点**：把 hard verdict 写回 `docs/TODO.md` 顶部 authoritative override，并同步一个 reader-facing 因子页

## 本轮做了什么
### 1) 新增最小 clean replication builder
新增：
- `scripts/build_rank36_tsm_drift_clean_replication.py`

固定执行口径：
- 数据：复用 `reports/artifacts/scout_tau_band_breakout_15m/cache/{BTC,ETH,SOL}USDT__120d__15m.csv`
- 三档最小 clean-room 对照：
  1. `recent_sign_only`
  2. `history_drift_only`
  3. `recent_and_drift_agree`
- 参数冻结：
  - recent sign = 最近 `16` 根 `15m` bar 的累计收益方向
  - history drift = 最近 `96` 根 `15m` bar 的累计收益方向
- 执行冻结：`signal bar close -> next-bar open` 入场，固定持有 `8` 根 `15m` bar，默认 `no-overlap`
- 成本统一检查：`6 / 10 / 15 / 20 bps per side`

### 2) 产出 artifact / 网页
新增：
- `reports/artifacts/scout_rank36_tsm_drift_honesty_gate_15m/overall_summary.csv`
- `reports/artifacts/scout_rank36_tsm_drift_honesty_gate_15m/asset_summary.csv`
- `reports/artifacts/scout_rank36_tsm_drift_honesty_gate_15m/time_bucket_summary.csv`
- `reports/artifacts/scout_rank36_tsm_drift_honesty_gate_15m/primary_trades_6bps.csv`
- `reports/site/factors/scout_rank36_tsm_drift_honesty_gate_15m/report.html`

### 3) 写回指挥板
更新：
- `docs/TODO.md`

写回内容：
- `Rank 36` 从 `fresh source intake admitted / next = 最小 clean replication` 改成 **`park / evidence pool`**
- 顶部 authoritative override 改成：本轮已把 `Rank 36` 的 clean replication 如实落地；若这一轮还拿不到新的本地 `paper / repo based 5m / 15m crypto` source，下一优先动作允许回退到 `Run 3 / tiny-live plumbing fallback`

## 结果
### Hard verdict
- `Rank 36 / recent-return sign vs history-drift honesty gate` → **`park / evidence pool`**

### 最关键证据
在 `6bps/side` 下：
- `recent_sign_only`：`mean_total_return≈-53.20% / positive_asset_ratio=0/3 / mean_trades≈590.0`
- `history_drift_only`：`mean_total_return≈-18.13% / positive_asset_ratio=0/3 / mean_trades≈230.7`
- `recent_and_drift_agree`：`mean_total_return≈-49.58% / positive_asset_ratio=0/3 / mean_trades≈546.7`

更直白地说：
- `history_drift_only` 确实比 `recent_sign_only` 更不差，说明这条线里“慢 drift 比 recent sign 更像解释变量”这个怀疑不是空的；
- 但它本身仍然明显亏损，不够格当成可升格的替代 alpha；
- `agree-only gate` 也没有把 `recent sign` 这条线救回来；
- 所以这轮最诚实的结论不是继续给 stability budget，而是直接压回 `park / evidence pool`。

### time-pocket honesty（主变体 `recent_and_drift_agree`，6bps）
- `bucket_1≈-32.91% / positive_asset_ratio=0/3 / mean_trades≈182.7`
- `bucket_2≈-17.56% / positive_asset_ratio=0/3 / mean_trades≈182.0`
- `bucket_3≈-8.41% / positive_asset_ratio≈33.33% / mean_trades≈182.0`

这说明它不是“前两段差、最后一段特别强”的临界候选，而是三个时间桶都没有给出足够诚实的 admission 通过证据。

## 为什么这轮不继续升格
本轮的 cheap honesty gate 已经回答了真正会改 verdict 的问题：
- 这条 `recent sign` 邻近线到底是 recent-momentum alpha，还是只是 drift / beta 近义包装？

当前答案是：
- recent sign 本身很差；
- drift proxy 虽略不差，但也不足以升格；
- agree-only gate 没有把它修成可继续投资预算的候选。

因此再给 `Light Stability Pack` 预算已经不诚实，默认应停在 `park / evidence pool`。

## 最小验证
已执行：
- `python3 -m py_compile scripts/build_rank36_tsm_drift_clean_replication.py`
- `python3 scripts/build_rank36_tsm_drift_clean_replication.py`

已抽查：
- `reports/artifacts/scout_rank36_tsm_drift_honesty_gate_15m/overall_summary.csv`
- `reports/artifacts/scout_rank36_tsm_drift_honesty_gate_15m/time_bucket_summary.csv`
- `reports/site/factors/scout_rank36_tsm_drift_honesty_gate_15m/report.html`
- `docs/TODO.md`

结果：
- builder 成功退出（code 0）
- artifact / 网页均已生成
- `TODO` 已同步 hard verdict 与下一手回退条件

## 风险 / 边界
- 这轮是最小 clean replication，不是假装做完完整 stability pack
- `history drift` 当前只是一个便宜对照 proxy，不是论文原月频构造的逐字照搬版本
- 但作为当前 desk 的 cheap honesty gate，它已经足够给出 hard verdict：**不该继续给这条线预算**

## 当前 desk 含义
- `Paper Seat / EMA` 仍是 `waiting_not_due`
- `Rank 36` 已用掉这轮允许的最小 clean replication 预算，且结论已压回 `park`
- 因此从现在起：
  - 若能从 `docs/RECENT_PAPER_SEEDS.md` / `research/quant_digests/INDEX.md` / `validated_alpha_shortlist` 再拿到一条新的本地 `paper / repo based 5m / 15m crypto` source，就继续留在 `Run 2`
  - 若这一轮拿不到新的合格 source，则允许按 board 回退到 `Run 3 / tiny-live plumbing fallback`

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的既有脏文件 / 未跟踪文件，避免混提
