# 2026-03-18 06:22 UTC — Rank 48 / session-range active-hours gate source intake

## 为什么这次选这个
- 先按 `TRADING DESK BOARD -> Next 3 bot3 runs` 重读当前顺序：
  - `Run 1 / EMA` 仍是 **`running paper / waiting_not_due`**，A 股下一次 close 仍在 `2026-03-18 07:00 UTC`，没有新的 `due-now / overdue` bar；
  - `Rank 47 / EMA-ADX-VOL skeleton` 已在允许预算内完成最小 clean replication，并已给出 **`park / evidence pool`** hard verdict；
  - `Rank 35b` 当前仍只是 queue-only derived fallback，不该在 fresh repo / paper source 仍可认领时抢主资源。
- 因此本轮默认继续落到 `Run 2 / Scout Fast Lane`，并先比较当前 active Scout 候选的边际价值。
- 这轮最诚实的主资源位是 **新的 fresh intake：Rank 48 / session-range active-hours gate**（来源：`2026-03-18_0549_session-range-active-hours-gate.md`）。
  - 它是 fresh repo + paper based `15m crypto` 候选；
  - 它比 `Rank 35b` 更贴当前 desk 主线，因为它不是再造一条孤立 alpha，而是能同时服务 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 的共用 overlay；
  - 这轮只需要把它推进到 `source intake / honesty gate passed`，不提前扩成 clean replication 或新大框架。

## 这轮做了什么
### 主点
- 把 quant digest 里的 `session range + active-hours gate` 正式编号为 **`Rank 48`**，并推进到 **`source intake / honesty gate passed`**。
- 新增 artifact：
  - `reports/artifacts/literature/scout_rank48_session_range_active_hours_source_intake_card.csv`
  - `reports/site/reading/repo_scout/session_range_active_hours_source_intake.html`

### 紧邻子点
- 最小改写 `docs/TODO.md` 顶部 authoritative board，补写 `2026-03-18 06:22 UTC` 的新状态：
  - `Rank 48 / session-range active-hours gate` 当前定位为 **`P1 weak candidate（source intake / 两条轻量诚实守门已过）`**；
  - 下一轮若 `EMA` 仍 `waiting_not_due`，默认只允许给它 **1 次最小 clean replication**；
  - 当前 `Next 3` 顺序收紧为：
    - `Run 1 = EMA due-check only`
    - `Run 2 = Rank 48 / session-range active-hours gate minimal clean replication`
    - `Run 3 = Rank 35b（若 fresh intake 再次失效） / tiny-live plumbing`

## 验证 / 证据
- 当前已冻结的两条轻量诚实守门：
  1. **`trade on / trade off` 已可清楚写成规则**
     - `trade on`：只在更有参与度的时段（优先 `London / NY / overlap`）允许 setup 通过第一层 gate；再要求信号发生在最近 `session high/low` 被突破后的 `1~4` 根内，并叠最小确认（如 `volume > SMA20×1.3`、`ADX > 20` 或 `HTF EMA50` 同向）后才允许 continuation / retest 进场；
     - `trade off`：若落在 dead hours、离最近有效 session 结构位太远、没有 break 后 retest / continuation 关系，或过滤只是靠极端限时把 trade count 压没，则不交易。
  2. **未见一眼可判死刑的 `lookahead / repaint / leakage`**
     - `session bucket` 完全由 UTC 时间戳派生；
     - `session high/low` 只用 trailing 已完成 bar 构建；
     - 源码未见必须同 bar 成交的 future reference，但下一轮 replication 仍必须统一冻结到 **`next-bar open + no-overlap`**，避免把 session close 条件判断与同 bar 成交混成乐观填单。
- 最小文件存在性检查已通过：
  - `ok_csv = reports/artifacts/literature/scout_rank48_session_range_active_hours_source_intake_card.csv`
  - `ok_html = reports/site/reading/repo_scout/session_range_active_hours_source_intake.html`
  - `ok_todo_writeback = docs/TODO.md`

## 当前硬结论
- **`Rank 48 / session-range active-hours gate = guard-passed / admit_to_clean_replication_queue`**。
- 它当前不是新的独立 alpha，只是从 digest 线索推进到了可执行队列。
- 下一轮最诚实的问题已经冻结得很窄：
  - `active_hours_only` 与 `session_structure_gate` 是否真能在 **不过度砍样本** 的前提下压低 `2~4 bar fail rate`？
  - 还是说它只是换一种方式切样本，看起来更干净但没有改善 post-cost expectancy？

## 风险 / 边界
- 这轮没有重跑 clean replication；只是把 fresh repo + paper intake 先过诚实守门。
- 这个 source 的真正价值更像共用 execution / veto overlay，不该被误写成已经独立成立的新 raw-alpha 候选。
- 论文证据当前只是支持“15m 信号不该 24h 同权”的周期性提示，不是对具体 entry rule 的直接回测背书。

## 下一步建议
1. 若下一轮 `EMA` 仍是 `waiting_not_due`，默认只给 `Rank 48` **1 次最小 clean replication**：
   - 固定 `BTC / ETH / SOL 15m` 历史样本；
   - 统一 `next-bar open + no-overlap`；
   - 对现有 `breakout-short / Fib retest_hold / EMA-PSAR` base setup 比较 `raw_all_day`、`active_hours_only`、`session_structure_gate`、`+volume_gate`、`+ADX_or_HTF_gate`。
2. 最先回答五个便宜问题：
   - `4 / 8 / 12 bar follow-through`
   - `2~4 bar fail rate`
   - `post_cost_expectancy`
   - `trade_count_retention`
   - `session-bucket contribution`
3. 若它只是靠时段切样本却没有稳定改善 follow-through / expectancy，就快速压回 `park / evidence pool`；不要继续磨 source-intake wording。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，本轮不安全混提。
