# Rank 63 / Fib 0.618 hold / 0.5 fail gate source intake + guard-passed

## 为什么这次选这个
- 先按 `Run 1` 重新核对 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：当前全 desk 仍无新的 `due-now / overdue` lane，最早仍是 `美股 1d+1wk -> 2026-03-18 20:00 UTC`，因此 `Paper Seat / EMA` 继续按 **`running paper / waiting_not_due`** 处理。
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json` 最新一次仍是 `new_closed_trades_appended=0`，说明没有新的 `P3 status-changing event` 值得回头挤占 continuity。
- 按 `docs/TODO.md` 当前 `Next 3 bot3 runs`，`Rank 62` 已在上一轮完成 minimal clean replication 并被压回 `park / evidence pool`，因此这轮合法主动作就是切到 **`Run 2 / Rank 63 source intake + 两条轻量诚实守门`**。

## 做了什么改动
1. 读取 `research/quant_digests/2026-03-18_1810_fib-0618-hold-05-failure-gate.md`，确认新 source 的 desk 读法不是“Fib 自己能赚钱”，而是 `0.618 hold / 0.5 fail` 这组更诚实的 through/fail 定义。
2. 拉取并复核外部 repo `11Muhil/FibTrend-Pro-Strategy_Pinescript` 的 `README.md`、`FibTrend_ATR.pine`、`FibTrend_1%_TP.pine`：
   - 可复刻核心：`fib618` 通过线、`fib50` 失败线、`volume > SMA24`、`close > SMA200`。
   - 当前不该偷渡进第一轮的部分：`ATR take profit`、`EMA9/26`、`trailing stop`、高周期胜率叙事。
3. 产出 `Rank 63` 的 source intake artifact：
   - `reports/artifacts/literature/scout_rank63_fib0618_hold05_fail_source_intake_card.csv`
   - `reports/site/reading/repo_scout/rank63_fib0618_hold05_fail_source_intake.html`
4. 更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs`，把当前 active Scout 顺序与 `Run 2 / Run 3` 默认动作写回权威板。

## 验证 / 证据
### 守门 1：trade on / trade off 是否能写清
可以。当前最小冻结读法：
- `trade on`：base setup 继续负责方向与价位；Fib gate 只回答回踩后有没有真正守住。第一轮冻结成：rolling `50`-bar high/low 生成 `fib618 / fib50`；long 侧只有 `close > fib618`、`volume > SMA24`、且 `close > SMA200` 时才允许确认通过；若之后任一根 `close < fib50`，则记为 fail line。
- `trade off`：若只是靠高周期叙事、ATR/EMA/trailing exit 一起偷渡，或 `volume>SMA24` 只是在砍交易数却没有改善 `failure-before-target / target-hit / MAE`，则不能当 desk 可部署 gate。

### 守门 2：有没有明显 lookahead / repaint / data leakage
当前未见一眼可判死刑的硬伤：
- `fib618 / fib50`、`SMA200`、`volume>SMA24` 都可用 signal 当根及之前数据计算；
- 但 desk 迁移时必须统一到 **`signal 当根及之前数据 + next-bar open + no-overlap`**；
- 同时要把 rolling `50`-bar high/low 明确视为预先冻结的近似 swing，禁止事后重选更好看的锚点美化结果。

### 当前 hard verdict
**`Rank 63 / Fib 0.618 hold / 0.5 fail gate = guard-passed / admit_to_clean_replication_queue`**。

## 风险 / 边界
- repo 自己已经明说 `4H / 1D` 比 `15m / 30m` 更可靠，所以这条线现在仍只是 fresh repo skeleton，不是已验证 alpha。
- rolling high/low 版本的 Fib 可能带来 level 漂移；若 clean replication 发现 15m 上 `fib50 fail line` 只是噪音 stop，就应快速压回 `park / evidence pool`。
- 这一轮没有做 minimal clean replication；严格遵守预算，只完成 source intake + 两条轻量诚实守门。

## 下一步建议
- 下一轮若 `EMA` 仍 `waiting_not_due`，只允许给 `Rank 63` **1 次最小 clean replication**：固定 `BTC/ETH/SOL 120d 15m` cache，比 `fib618_reclaim_raw`、`+volume_gate`、`+volume_gate+fib50_fail_line`、`+volume_gate+fib50_fail_line+sma200_filter` 四臂；统一 `next-bar open + no-overlap`。
- 首先回答 5 个便宜指标：`post_cost_return@6bps`、`failure_before_target_rate`、`target_hit_within_12bars`、`MAE/ATR`、`trade_count_retention`。
- 若改善只来自极端砍单、只在单一资产成立，或 `fib50 fail line` 对 15m 噪音过度敏感，就直接 `park`，不要继续写 admission wording。

## Commit hash
- 未提交。

## 为什么未提交
- 当前 git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；为避免混提，这轮只做最小必要落点、日志、首页刷新与邮件摘要，不做 selective commit。
