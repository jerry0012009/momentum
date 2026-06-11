# 2026-03-20 12:17 UTC · Rank 121 / PSAR trailing role fail-safe / source intake

## 本轮上下文
- 触发：bot3 13m desk auto loop
- 顶板 authority：`docs/TODO.md` 顶部 `2026-03-20 12:01 UTC` 最新补充
- Run 1 结果：再次实际执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，仍如实返回 `Paper Seat / EMA = running paper / waiting_not_due`
- 最近 due：美股 `1d+1wk -> 约 7.7h`；Crypto `1d+1wk -> 约 11.7h`；创业板ETF `1d -> 约 66.7h`
- repo 状态：工作区仍有大量与本轮无关的既有脏文件，不混提
- hosted P3 状态：这轮仍严格只从当前 `Next 3` 认领动作，不插队回头做 hosted continuity

## 为什么这轮选 Rank 121
按 `12:01 UTC` 顶板，这轮顺序已经被明确收紧为：
1. `Run 1 = EMA due-check first`
2. 若仍 `waiting_not_due`，则只给 **`Rank 121 / PSAR trailing role fail-safe`** 做 `source intake + 两条轻量诚实守门`
3. 只有当 `Rank 121` guard-pass，下一轮才配拿 `1` 次最小 clean replication

因此本轮不并开新的 fresh source，也不回头磨 `Rank 112 / 111`。

## source intake + 两条轻量诚实守门
### 这条线到底在说什么
这轮直接继承 `research/quant_digests/2026-03-20_1004_psar-trailing-role-not-default-exit.md` 的工程定义：
- `baseline exit`
- `immediate PSAR trailing exit`
- `handoff3 -> PSAR trailing exit`

翻成人话：它不是“PSAR 反转就开新单”，也不是“让 PSAR 统一接管三条主线的一切出场”；它更像一个**入场后先让 setup 自己走几根，再交给 PSAR 做 fail-safe 的后置风险阀**。

### trade on
- 只配先当 **optional fail-safe handoff after entry** 去测。
- 适合后续放进既有 breakout / Fib / EMA follow-up clean-room 里，回答“延迟接手的 PSAR 是否比 immediate PSAR 更诚实”。

### trade off
- 不得直接写成 breakout / Fib / EMA 的 **shared 默认 exit engine**。
- 如果改善主要来自更早急停、交易数明显塌缩、或跨资产一换就散，应直接 `park`。
- 若 clean replication 不能证明 delayed handoff 比 immediate PSAR 更诚实，也不应继续给稳定性预算。

### honesty gate 1：规则是否写得清楚
能写清楚，而且写清楚以后更能确认它的边界：
- 这是 **exit-role clarifier**，不是新 alpha
- 这是 **post-entry fail-safe**，不是 entry gate
- 这是 **conditional overlay**，不是 desk-wide shared default exit

### honesty gate 2：有没有明显 leakage / repaint / data leakage
- 当前定义可以完全写成因果版：信号触发后，前 `N` 根按 baseline，之后才用当时已完成 bar 可见的 `PSAR` 状态决定 trailing
- 下一轮 clean replication 只需要统一冻结：
  - `signal 当根及之前数据`
  - `next-bar open`
  - `no-overlap`
  - 训练段冻结 `handoff bars` 与 `PSAR params`
- 因而当前看不到明显先天 lookahead / repaint 结构，够资格进入最小 clean replication

## 关键证据
来自 digest 附带的 `BTC/ETH/SOL | 180d | 15m` 代理快检：
- 聚合 `baseline`：`weighted_expectancy_net ≈ -19.26 bps/trade`，`median_hold_bars = 3`
- 聚合 `immediate PSAR`：`weighted_expectancy_net ≈ -19.79 bps/trade`，`median_hold_bars = 1`
- 聚合 `handoff3`：`weighted_expectancy_net ≈ -18.94 bps/trade`，`median_hold_bars = 3`
- 分资产上：
  - `SOL`：`baseline -18.90 -> handoff3 -16.43 bps`，有改善
  - `BTC`：`baseline -19.48 -> handoff3 -20.21 bps`，变差
  - `ETH`：`baseline -19.35 -> handoff3 -19.82 bps`，略差

这套证据足够回答当前 source-intake 阶段最关键的问题：
**PSAR 值得被测，但当前最诚实的角色只能是 delayed handoff fail-safe，而不是 shared 默认 exit。**

## 本轮硬结论
**`Rank 121 / PSAR trailing role fail-safe = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：
- 这条线不是要继续扩写成“PSAR 统一接管全部出场”；
- 它值得的只是 **1 次最小 clean replication**；
- 下一轮若要继续，就只该验证“延迟 handoff 是否真的比 immediate PSAR 更诚实”。

## 本轮交付
### reader-facing
- `reports/site/reading/repo_scout/rank121_psar_trailing_role_fail_safe_source_intake.html`

### artifact
- `reports/artifacts/literature/scout_rank121_psar_trailing_role_fail_safe_source_intake_card.csv`

### board update
- 已把 desk board 的 active Scout 主点前推为：`Rank 121 = P1 / guard-passed / clean replication next`
- 并把下一轮 `Run 2 / Run 3` 改写成：`Rank 121 最小 clean replication -> 若有 honest uplift，再补 1 个最小 Light Stability Pack；否则 tiny-live plumbing fallback`

## 风险 / 边界
- 当前仍是 repo 规则 + 公开市场数据代理快检，不是完整策略级 clean-room 回测
- 跨资产不一致已经说明：即便下一轮 clean replication 通过，它也大概率只是条件化 overlay，不会直接升成 shared default exit
- 当前 repo 很脏，本轮不适合混提

## 下一步建议
- `Run 1 = EMA due-check first`
- 若仍 `waiting_not_due`：
  - `Run 2 = 只给 Rank 121 1 次最小 clean replication`
  - `Run 3 = 若 clean replication 仍显示 delayed handoff 比 immediate PSAR 更诚实，再补 1 个最小 Light Stability Pack（优先成本 / 交易数稳定性），并直接给出 P2 / park；若没有 honest uplift，则直接 park 并回 tiny-live plumbing fallback`

## Commit hash
- 未提交。
- 原因：repo 当前仍有大量与本轮无关的既有脏文件；本轮只安全写入了 `Rank 121` 直接相关的最小文件，不适合混提。
