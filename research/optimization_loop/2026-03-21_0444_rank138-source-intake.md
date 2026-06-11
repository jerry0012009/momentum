# 2026-03-21 04:44 UTC — Rank 138 / funding × OI cross-symbol crowding breadth overlay / source intake + 两条轻量诚实守门

## 本轮一句话
先按 desk 规则执行 `EMA due-check first`；结果继续 `waiting_not_due`，所以本轮主动作切去 **Scout Seat**。比较当前 active Scout 的边际价值后，正式认领 **`Rank 138 / funding × OI cross-symbol crowding breadth overlay`**，并完成 `trade on / trade off` 与 `no leakage` 两条轻量诚实守门，硬结论是：**guard-passed / admit_to_clean_replication_queue**。

## 先检查了什么
- `git status --short --branch`
  - repo 仍有大量与本轮无关脏文件，继续 **不混提**。
- 最近 runs
  - 最近两轮 Scout 主资源已给过 `Rank 137`：`state expiry intake -> clean replication -> time-stability park`。
  - 当前顶板已把 active Scout 顺序收紧到 `Rank 138 > Rank 127 > Rank 125 > Rank 112 > Rank 111`。
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回：当前仍没有 `due-now / overdue` lane。
  - 最近 due：`Crypto 1d+1wk（BTC/ETH/SOL）` 约 `19.2h` 后到点。
  - 说明：本轮继续合法从 `Paper Seat` 切去 `Scout Seat`，不能在等待窗口里空转。

## 为什么这轮认领 Rank 138，而不是回旧 P1 / P3 continuity
当前 authoritative 顶板写的是：
1. `Run 1 = EMA due-check first`
2. `Run 2 = 若 EMA 仍 waiting_not_due，认领 Rank 138 的 source intake`
3. `Run 3 = 若 Rank 138 guard-pass，只给它 1 次最小 clean replication`

结合 active Scout 边际价值：
- `Rank 127 / 125 / 112 / 111`
  - 都已是 `P1 / weak candidate or evidence_pool / budget used`；按 desk 规则，本轮默认不该继续磨旧 `P1`。
- `Rank 2 / 17 / 29 / 32b / 122`
  - 都属于 `P3 continuity / sidecar only`；而且 `EMA = waiting_not_due` 时，默认预算要先给 fresh Scout，而不是继续消费 hosted continuity。
- `fixed partial → R/ATR partial`
  - 只有在 `Run 3` 且 `Rank 138 hard-fail / exhausted` 时才允许接棒；本轮还不到它。

**结论：** 本轮最该认领的是 `Rank 138` 这条 fresh repo/docs source，而不是回头打磨旧候选。

## 本轮主点：Rank 138 source intake
来源：
- digest：`research/quant_digests/2026-03-21_0302_funding-oi-crowding-breadth-overlay.md`
- 公开接口 / repo：Binance USDⓈ-M `24hr ticker` / `fundingRate` / `openInterestHist` + `binance-connector-python`

翻成人话：
这条线值钱，不是因为 funding 或 OI 本身有多新，而是因为它把两者从“单币方向键”改写成了一个**横截面 crowding breadth overlay**：
- 看的是一篮子 top-liquid 合约有没有同向拥挤扩散；
- 角色更像 shared `size / veto / extra-confirm` 风控层；
- 而不是继续给 breakout / fib / EMA 各自再加一条 raw trigger。

## 两条轻量诚实守门
### 1) trade on / trade off
- **trade on：**
  - 每个 `15m close` 只在 top-liquid `USDT perpetual` 上计算 `LongCrowdBreadth / ShortCrowdBreadth`；
  - 首轮 desk 翻译只允许是 **shared size discount / veto / extra-confirm overlay**；
  - 默认最小接法：breadth 极端时，对应方向 `size × 0.6`，或要求额外 `1` 根 confirm。
- **trade off：**
  - 它不是单币 funding 阈值方向键；
  - 不是逐根 raw alpha trigger；
  - 不是 tiny-live path-management；
  - 如果 clean replication 证明改善只来自极端砍交易数、只在单侧方向成立、或只在单次 snapshot 好看，就直接 `park`。

### 2) no lookahead / repaint / leakage
- funding 只允许使用 `bar close` 之前最近一次**已发布**的 funding；
- OI 只允许使用已经完成的 `5m openInterestHist` 聚合到 `15m` 的变化；
- breadth 的 top-liquid 选择也只能使用该 close 当下可见的 `24h ticker`；
- desk clean replication 必须统一冻结到 `next-bar open + no-overlap`；
- 不允许用未来 crowding 扩散、结算后 funding、或最终 outcome 去回填 overlay 阈值。

**本轮 hard verdict：`guard-passed / admit_to_clean_replication_queue`。**

## 本轮新增产物
### artifacts
- `reports/artifacts/literature/scout_rank138_funding_oi_crowding_breadth_source_intake_card.csv`

### reader-facing
- `reports/site/reading/repo_scout/rank138_funding_oi_crowding_breadth_source_intake.html`

### desk write-back
- `docs/TODO.md`
  - `Scout Seat 当前主点` 已改成 `guard-passed / minimal clean replication next`
  - `Run 2` 已推进为 `Rank 138 1 次最小 clean replication`
  - `最近关键 evidence` 已补入本轮 due-check 与 guard-pass 结论

## 对 desk 的含义
- `Paper Seat`：不变，仍是 `EMA / running paper / waiting_not_due`
- `Live Seat`：继续暂空
- `Scout Seat`：当前最诚实的下一手不是再写概念页，而是给 `Rank 138` **1 次最小 clean replication**，直接判它是否值得继续保留为 shared overlay 候选。

## 下一轮最小动作建议
若下一轮 `EMA` 仍非 due-now：
- 只给 `Rank 138` **1 次最小 clean replication**；
- 固定复用 `BTC/ETH/SOL 15m` 本地 cache；
- 只比较 `baseline vs overlay` 两臂；
- overlay 首轮只测：
  - `breadth percentile = p80 / p90`
  - 接法 = `size × 0.6` 或 `extra confirm`
- 主看：`post_cost_expectancy`、`failure_rate`、`trade_count_retention`、`max_drawdown`
- 若 retention / 成本后表现明显塌缩，就直接 `park`，不要继续磨 wording。

## 最小验证
已实际执行：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前无 `due-now / overdue` lane；最近 due 为 `Crypto 1d+1wk（BTC/ETH/SOL）`，约 `19.2h` 后到点。

## 风险 / 边界
- 这轮还只是 intake，不是假装已经完成 replication；
- 当前证据只够支持“它值得拿 1 次 clean replication 预算”，不够支持“它已经是 desk 默认 shared overlay”；
- funding 的更新频率天然慢于 `15m`，所以它更像 regime / crowding layer，而不是逐根主信号；
- 若后续 replication 发现它本质只是单次 snapshot 巧合，应该很快 `park`。

## Commit hash
- 未提交。
- 原因：工作区存在大量与本轮无关脏文件；本轮只做局部 intake card、reader-facing 页面、顶板 write-back 与 run log，不适合混提。
