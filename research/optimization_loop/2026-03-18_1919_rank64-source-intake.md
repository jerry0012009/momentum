# Rank 64 / pullback-quality score gate source intake + guard-passed

## 为什么这次选这个
- 先按 `Run 1` 重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：当前全 desk 仍无新的 `due-now / overdue` lane，最早仍是 `美股 1d+1wk -> 2026-03-18 20:00 UTC`，因此 `Paper Seat / EMA` 继续按 **`running paper / waiting_not_due`** 处理。
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`，说明没有新的 `P3 status-changing event` 值得回头挤占 continuity。
- 按 `docs/TODO.md` 当前 `Next 3 bot3 runs`，`Rank 63` 已在上一轮完成 minimal clean replication 并被压回 `park / evidence pool`，因此这轮合法主动作就是切到 **`Run 2 / Rank 64 source intake + 两条轻量诚实守门`**。
- 这轮也先比较了所有 active fresh Scout 候选的边际价值：`Rank 64 / pullback-quality score gate` > `perp-stress resetComplete / re-arm gate` > `exec-TF switch alignment gate` > `regime-matrix shared-state gate`。当前先拿 `Rank 64`，不是因为它证据更强，而是因为它直接服务 desk 还缺的 shared `retest_hold / continuation quality` 读法，而且只需现有 `15m OHLCV + ATR + volume` 就能先给出最小诚实 verdict。

## 做了什么改动
1. 读取 `research/quant_digests/2026-03-18_1151_pullback-quality-score-gate.md`，确认这条线对 desk 最值钱的不是作者的高周期绩效，而是 `trendPts + zonePts + volPts + triggerPts` 这套 shared quality-score 骨架。
2. 复核外部 repo `nirujan123/Pullback-Quality-Strategy` 的 `README.md` 与 `src/CQI_v1_3_strategy.pine`：
   - 可复刻核心：`EMA 结构`、`ATR 计量回踩深度`、`缩量回踩`、`EMA reclaim / break previous high` 触发；
   - 当前不该偷渡进第一轮的部分：`4H / Daily` 绩效叙事、ATR 止盈止损、仓位管理、long-only 高周期优化口径。
3. 产出 `Rank 64` 的 source intake artifact：
   - `reports/artifacts/literature/scout_rank64_pullback_quality_score_source_intake_card.csv`
   - `reports/site/reading/repo_scout/rank64_pullback_quality_score_source_intake.html`
4. 更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`，把当前 active Scout 顺序与 `Run 2 / Run 3` 默认动作写回权威板。

## 验证 / 证据
### 守门 1：trade on / trade off 是否能写清
可以。当前最小冻结读法：
- `trade on`：base setup 继续负责方向与价位；CQI 只负责回答回踩 / 反抽质量够不够。第一轮冻结成 `trendPts(EMA 结构)` + `zonePts(ATR 深度)` + `volPts(缩量回踩)` + `triggerPts(reclaim / continuation break)` 四块，默认先测 `>=60` 与 `>=80` 两档。
- `trade off`：若它要靠高周期 long-only 绩效叙事、ATR 止盈止损、仓位管理或额外 regime 条件一起偷渡，说明它还只是 repo skeleton，不是 desk 可部署 gate。若 score 改善主要来自极端砍单、却没有同步改善 `false-hold / false-follow-through`，也不该升格。

### 守门 2：有没有明显 lookahead / repaint / data leakage
当前未见一眼可判死刑的硬伤：
- 脚本只用 trailing EMA、ATR、volume 均值、前一根高点等当根及之前数据；
- 但 desk 迁移时必须统一到 **`signal 当根及之前数据 + next-bar open + no-overlap`**；
- 同时必须先拆成 `base / +zone / +zone+vol / +full score` 分臂，防止把事后最优 `recentHigh` 锚点或入场后行为倒灌回评分。

### 当前 hard verdict
**`Rank 64 / pullback-quality score gate = guard-passed / admit_to_clean_replication_queue`**。

## 风险 / 边界
- 这是一个 **很新的小仓库**，社会证明几乎没有，当前只能当作规则骨架，不是 validated alpha。
- repo 主要测试 `4H / Daily` 且只有 long 侧；下放到 `15m`、再镜像到 short 侧，都会引入额外噪音与样本偏差。
- 这套 score 很容易变成“每项都看起来合理，但信息彼此重叠”；如果 clean replication 发现增量只来自极端砍样本或分项高度重叠，就应快速压回 `park / evidence pool`。

## 下一步建议
- 下一轮若 `EMA` 仍 `waiting_not_due`，只允许给 `Rank 64` **1 次最小 clean replication**：固定 `BTC/ETH/SOL 120d 15m` cache，比较 `base`、`base+zone`、`base+zone+vol`、`base+full_score` 四臂；统一 `next-bar open + no-overlap`。
- 第一轮优先回答 5 个便宜指标：`post_cost_return@6bps`、`false_hold_or_false_follow_rate`、`trade_count`、`trade_count_retention`、`positive_asset_ratio`。
- 若改善主要来自 trade-count 大幅塌缩、只在单一资产成立，或 `trend / zone / trigger` 明显重复表达同一件事，就直接 `park`，不要继续写 admission wording。

## Commit hash
- 未提交。

## 为什么未提交
- 当前 git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；为避免混提，这轮只做最小必要落点、日志、首页刷新与邮件摘要，不做 selective commit。
