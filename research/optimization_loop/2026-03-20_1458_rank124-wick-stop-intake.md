# 2026-03-20 14:58 UTC · Rank 124 / interim wick + ATR stop anchor / source intake

## 本轮一句话
先按 desk 规则执行 `EMA due-check first`；结果继续 `waiting_not_due`，因此本轮主动作回到 fresh Scout，并把 `2026-03-20 14:49 UTC` 的 repo digest 正式冻结为 **`Rank 124 / interim wick + ATR stop anchor`**，完成 `source intake + 两条轻量诚实守门`。当前 hard verdict：**`guard-passed / admit_to_clean_replication_queue`**。

## 先检查了什么
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：继续 `waiting_not_due`
  - 最近 due 约为：`美股 1d+1wk -> 5.0h`、`Crypto 1d+1wk -> 9.0h`、`创业板ETF 1d -> 64.0h`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json`
  - `run_at_utc=2026-03-20T14:10:29Z`
  - `new_closed_trades_appended=0`
  - 说明：hosted `P3` lanes 没有新的 status-changing event 抢主资源
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 开工前 authoritative `Next 3`：`Run 1 = EMA due-check first -> Run 2 = fresh intake -> Run 3 = 若 fresh intake guard-pass，则给 1 次最小 clean replication`
- repo status：工作区仍很脏，不混提；本轮只做 selective write-back

## 为什么这轮认领 Rank 124
这轮最诚实的动作不是回头磨 `Rank 112 / 111`，也不是继续消耗 `Rank 122` 的 `P3 continuity` 预算，而是比较 fresh source 的边际价值后，选一个**最接近 deployable artifact** 的候选。

在 `14:29 UTC` 的“retest tolerance 与 stop 解耦”和 `14:49 UTC` 的“interim wick + ATR stop anchor”之间，我优先认领后者，原因很直接：
- 它不再发明新 alpha；
- 它直接服务三条主线都共用的 **initial risk anchor / 初始止损锚**；
- 它比继续讨论参数耦合更像一个会马上改变 desk 执行口径的 shared risk overlay 候选。

## 本轮主点
### Rank 124 source intake + 两条轻量诚实守门
把 `TheVision333/trading-bot` 里三种初始 stop 锚法收窄成 desk 可执行的 queue-facing 描述：
- `ATR-only`：`entry ± 1.5 ATR`
- `wick+ATR`：最近一根反向 K 线影线外，再加 `0.25 ATR`
- `wick+pct`：最近一根反向 K 线影线外，再加固定百分比 buffer

翻成人话：这条线回答的不是“现在该不该开仓”，而是**“既然已经按现有 setup 进场了，初始 stop 该围着 entry 画圆，还是更诚实地挂在最近那次反向对抗过趋势的位置外？”**

### trade on
- 只配先当 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 的 **shared initial risk anchor** 去测。
- 下一轮 clean replication 默认只比较 `ATR-only` 与 `wick+ATR`；必要时再保留 `wick+pct` 做对照。
- 入场仍沿用现有 base setup；这条线只负责“初始 stop 该挂在哪里更诚实”。

### trade off
- 不是独立 alpha。
- 不是新的 entry trigger。
- 不是 broad sizing engine。
- 若 clean replication 发现改善只来自 stop 更宽、风险半径更大，而不是更诚实地避开近端噪声，就应继续留在 risk overlay，不能偷渡成 alpha 改善。

### honesty gate 1：规则是否写得清楚
能写清楚，而且写清楚以后边界更明确：
- 这是 **初始风险锚**，不是策略主信号；
- 这是 **entry 之后立刻生效的 stop 角色**，不是事后 swing 重画器；
- 这是 **shared risk overlay 候选**，不是 breakout-short / Fib / EMA 的某一条独立新 seat。

### honesty gate 2：有没有明显 leakage / repaint / data leakage
- 当前定义可以完全写成因果版：最近反向 K 线、其 wick 极值、以及 ATR buffer 都只来自 `signal 当根及之前` 的已完成 15m bar。
- 下一轮 clean replication 只需要统一冻结：
  - `signal 当根及之前数据`
  - `next-bar open`
  - `no-overlap`
  - stop 角色固定为 `entry 后即生效的初始风险锚`
- 因而当前看不到先天 lookahead / repaint 结构，够资格进入最小 clean replication。

## 关键代理证据
来自 digest 附带的 `BTC/ETH/SOL | 15m` 最小快检：
- `entry ± 1.5 ATR`：stop 中位距离约 **0.66%**，`8-bar stop-hit ≈ 52.0%`
- `反向影线 ± 0.25 ATR`：stop 中位距离约 **0.95%**，`8-bar stop-hit ≈ 31.8%`
- `反向影线 ± 0.2%`：stop 中位距离约 **1.01%**，`8-bar stop-hit ≈ 26.8%`
- 对 `breakout-short` 最明显：`8-bar stop-hit` 从 **45.9%** 压到 **16.4%**（wick+ATR）
- 但风险代价也必须如实保留：`stopDistancePct > 1.5%` 的占比从 ATR-only 的 **3.5%** 抬到大约 **24~26%**

这套证据已经足够回答 source-intake 阶段最关键的问题：
**它值得先拿 1 次最小 clean replication 预算，但当前只配做 shared initial risk anchor 候选，不配直接被误写成 alpha 改善。**

## authoritative verdict
**`Rank 124 / interim wick + ATR stop anchor = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：
- 这条线值得拿 **1 次最小 clean replication**；
- 但当前只配验证“结构锚是否比 ATR-only 更诚实地定义初始风险”，而不是改写整个策略方向；
- 更不配抢 `Live Seat`。

## 本轮交付
### reader-facing
- `reports/site/reading/repo_scout/rank124_interim_wick_atr_stop_anchor_source_intake.html`

### artifact
- `reports/artifacts/literature/scout_rank124_interim_wick_atr_stop_anchor_source_intake_card.csv`

### board update
- 已把 desk board 的 active Scout 主点前推为：`Rank 124 = P1 / guard-passed / clean replication next`
- 并把下一轮 `Run 2 / Run 3` 改写成：`Rank 124 最小 clean replication -> 若保留 honest uplift，则 keep_P1 / promote_P2 / park；否则回 fresh intake`

## 验证 / 证据
- 已执行：`python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：继续 `waiting_not_due`
- 已生成并核对：
  - `reports/artifacts/literature/scout_rank124_interim_wick_atr_stop_anchor_source_intake_card.csv`
  - `reports/site/reading/repo_scout/rank124_interim_wick_atr_stop_anchor_source_intake.html`
  - `docs/TODO.md`

## 风险 / 边界
- 当前仍是 repo 结构证据 + 公开行情代理快检，不是完整 clean-room 回测；
- 这条线极容易把“更少被打 stop”误读成“alpha 更强”，所以下一轮必须同时盯住 `stopDistancePct distribution` 与 `post-cost expectancy`；
- 若只有“更宽 stop”才改善，应诚实地把它留在 risk overlay，不要偷渡成策略升级。

## 下一步建议
- `Run 1 = EMA due-check first`
- 若仍 `waiting_not_due`：
  - `Run 2 = 只给 Rank 124 1 次最小 clean replication`
  - `Run 3 = 若 Rank 124 保留 honest uplift 且无 decisive fail，则直接给 keep_P1 / promote_P2 / park；若 hard-fail，则回 fresh intake`

## Commit hash
- 未提交。
- 原因：repo 当前仍有大量与本轮无关的既有脏文件；本轮只安全写入了 `Rank 124` 直接相关的最小文件，不适合混提。
