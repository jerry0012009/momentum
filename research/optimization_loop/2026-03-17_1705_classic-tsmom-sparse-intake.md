# 2026-03-17 17:05 UTC · Rank 37 classic sparse TSMOM source intake

## 本轮归属
- Desk lane：`Run 2 / Scout Seat fresh intake`
- 触发原因：
  - `Paper Seat / EMA` 当前仍是 `waiting_not_due`，最新 due guardrail 没有新的 `due-now / overdue` lane；
  - `Rank 17 / Rank 2 / Rank 29` 都属于 `P3 continuity`，当前没有真实 `append/review need`，且当日预算不该继续消耗；
  - `Rank 30~36` 当前允许动作都已消耗并 `park`；
  - 按 `TRADING DESK BOARD` 顶板规则，本轮应先从 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 再认领 1 条新的本地 `paper / repo based 5m / 15m crypto` source，而不是直接回退到 `Run 3`。

## 开工前检查
- 已先读：`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：工作区存在大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做 selective 写入，不混提
- 当前边际价值比较：
  - `P3 continuity`（`Rank 17 / Rank 2 / Rank 29`）当前没有 genuinely verdict-changing 的动作；
  - `Rank 30~36` 已完成当前预算并 park；
  - `Rank 5 / Rank 6` 仍偏 external-data，不符合当前 fast-lane 默认顺序；
  - 在剩余本地 seeds 里，`Moskowitz, Ooi, Pedersen (2012) / Time Series Momentum` 比 `Limited Attention Theory` 这类机制论文更适合当前这一轮，因为它不需要额外 proxy 假设，能直接翻成最小 clean-room 规则。

## 本轮主点 + 紧邻子点
- **主点**：新增 `Rank 37 / classic sparse TSMOM / own-past persistence pocket` fresh intake
- **紧邻子点**：把 hard verdict 写回 `docs/TODO.md` 顶部 authoritative override，并同步一个 reader-facing digest / 网页落点

## 为什么选这条线
当前最值得回答的问题不是“再给 15m sign-momentum 家族加什么过滤器”，而是：
- 当前 desk 看到的动量失败，究竟是 own-past persistence 本身不成立，
- 还是我们此前拿得太快、太密、太重叠，导致成本和翻单把 pocket 吃没了。

经典 TSMOM 给当前 desk 的最小启发，不是照搬月频参数，而是：
- **先回到更慢、更稀、更少重叠的 own-past persistence pocket**；
- 若连这条 slow-pocket 也不诚实，那当前 fast-lane 就应更快承认这条家族不值得默认预算。

## 本轮做了什么
### 1) 新增 fresh source intake digest
新增：
- `research/quant_digests/2026-03-17_1705_classic-tsmom-sparse-pocket.md`
- `reports/artifacts/literature/scout_rank37_classic_tsmom_sparse_source_intake_card.csv`

冻结后的 source-intake 口径：
- 候选名：`classic sparse TSMOM / own-past persistence pocket`
- `trade on`：过去更慢窗口（如 `4h~12h`）的 own-past cumulative return direction 为正/负，则沿该方向交易；若两档 slow window 同向，则只保留 agree leg
- `trade off`：slow-window sign 缺失、方向冲突、或固定持有期结束
- 执行约束：默认 `signal bar close -> next-bar open` 入场，优先 `no-overlap`

### 2) 同步 reader-facing 网页
执行：
- `python3 scripts/build_quant_digest_site.py`

网页落点：
- `reports/site/reading/quant_digests/2026-03-17_1705_classic-tsmom-sparse-pocket.html`
- `reports/site/reading/quant_digests/report.html`

### 3) 写回 desk 指挥板
更新：
- `docs/TODO.md`
- `research/quant_digests/INDEX.md`

写回内容：
- 新增 `Rank 37` 条目，状态为 **`admit_to_clean_replication_queue`**
- 顶部 authoritative override 改成：当前默认下一手不是 `Run 3`，而是继续留在 `Run 2`，只给 `Rank 37` 一次最小 clean replication 预算

## Hard verdict
- `Rank 37 / classic sparse TSMOM / own-past persistence pocket` → **`admit_to_clean_replication_queue`**

更直白地说：
- 这还不是 `paper candidate`
- 也不是 `narrow paper pilot`
- 它只是当前最值得花下一轮 `1` 次最小 clean replication 预算的本地 slow-pocket 候选

## 下一轮只允许做什么
固定复用 `BTC / ETH / SOL 120d 15m` cache，只比较三档最小规则：
1. `slow_4h_sign_hold_4h`
2. `slow_12h_sign_hold_8h`
3. `slow_4h_12h_agree_hold_8h`

先只看：
- `post_cost_return`
- `positive_asset_ratio`
- `trade_count`
- `time-pocket honesty`

若结果仍全面转负，或只是靠极低 trade count 勉强为正，就应快速压回 `park / evidence pool`，不要继续留在研究态。

## 最小验证
已执行：
- `python3 scripts/build_quant_digest_site.py`

已抽查：
- `research/quant_digests/2026-03-17_1705_classic-tsmom-sparse-pocket.md`
- `reports/site/reading/quant_digests/2026-03-17_1705_classic-tsmom-sparse-pocket.html`
- `docs/TODO.md`
- `research/quant_digests/INDEX.md`

结果：
- digest 站点构建成功退出（code 0）
- `TODO` 已同步 `Rank 37` 与新的 next-hand 排班
- reader-facing 网页已落地

## 风险 / 边界
- 论文原证据是跨资产、更慢周期，不是把月频参数原样搬到 15m crypto
- 这条线的价值，在于给当前 desk 一个更诚实的 slow-pocket 对照，不保证会产出新 alpha
- 若下一轮 clean replication 没有最小 admission 味道，应尽快 park

## Git
- 未提交
- 原因：repo 内仍有大量与本轮无关的脏文件 / 未跟踪文件，避免混提
