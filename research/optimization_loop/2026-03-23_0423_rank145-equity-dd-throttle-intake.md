# 2026-03-23 04:23 UTC · Rank 145 / equity drawdown throttle + recovery hysteresis overlay source intake

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD` + `docs/AUTO_OPTIMIZATION_LOOP.md`
- 本轮类型：`Scout / fresh intake reserve`
- 范围控制：只推进 **1 个主点**（fresh intake reserve）+ **1 个紧邻子点**（与当前 active compare 的边际价值比较）。

## 0. 先判 interrupt
- 顶板当前未写入任何 `Paper / 正在自动运行` runner 的真实 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`。
- `tiny-live / live-shadow plumbing` 也未出现新的 blocking anomaly。
- 因此本轮不抢 interrupt，继续按 `Next 3 bot3 runs`：`Paper launch queue` 为空时，先执行 fresh intake reserve。

## 1. 为什么这轮继续切 fresh intake，而不是回头磨旧 P1
当前顶板 authoritative 口径已经明确：
- `Rank 14b / 125 / 112 / 111` 都已进入 **`keep_P1 / budget used`**；
- `Rank 140` 仍是 `active compare anchor`，但也已完成过去几轮 cheapest decisive compare；
- 刚完成的 `Rank 144` 已给出最小 desk verdict：**`keep_P1 / not-shared / breakout-short follow-up bias`**。

所以这轮最值得做的，不是再给旧 P1 做近义补刀，而是认领一条 **能覆盖三条主线、同时更贴近 paper / tiny-live 安全边界** 的新 reserve。

## 2. 本轮认领
### 主点
- **`Rank 145 / equity drawdown throttle + recovery hysteresis overlay`**

### 紧邻子点
- 只做 1 个边际价值比较：和 `Rank 140 / 144` 这类“继续磨信号层候选”相比，这条新 reserve 是否更值得占下一个默认 Scout 主资源位？

结论：**值得。**
原因不是它更像 alpha，而是它更像 **三条收口线共用、且更接近真实部署边界的 live-safety overlay**。

## 3. 来源与 reader-facing 定义
来源基底：
- `research/quant_digests/2026-03-23_0422_equity-dd-throttle-recovery-hysteresis-overlay.md`
- 论文锚点：`AdaptiveTrend arXiv 2602.11708v1`
- 工程锚点：`xzjh/crypto-daytrading`

reader-facing 定义：
> 当策略权益曲线从峰值开始显著回撤时，先自动把仓位降档；只有当权益恢复到指定阈值，才允许恢复原仓位。这不是入场前 veto，也不是新 alpha，而是一层跨 breakout / fib retest / EMA-PSAR 的共享 live-safety overlay。

## 4. 为什么它现在的边际价值高
和旧 P1 相比，这条线有三个现实优势：

1. **更贴近 desk 当前北极星**
   - desk 要的是“至少一条自动 paper 跑着 + 一条更接近 tiny-live review + 一条持续 scout”；
   - 这条 overlay 直接服务“更接近 tiny-live / live review”的那半边，而不是继续细磨某个局部信号 pocket。

2. **不改原信号语义，迁移成本低**
   - 不要求先统一 entry / exit 定义；
   - 可挂在 `breakout-short follow-up`、`Fib retest_hold`、`EMA / PSAR raw alpha` 上做统一风控覆盖；
   - 对 paper runner / narrow lane 来说，也更像真实部署前会需要的安全阀。

3. **它可能改变 routing，而不只是补证据**
   - 如果最小本地 A/B 通过，它有资格进入“shared overlay 候选池”；
   - 这比给 `Rank 140` 或 `Rank 144` 再补一刀近义 signal compare，更可能改变接下来该把 bot3 预算投去哪。

## 5. 本轮最小 intake verdict
### desk-level 读法
- **`Rank 145 = P1 / keep_P1 / fresh intake admitted / shared risk overlay candidate`**
- 它不是 alpha、不是独立策略、也不是入场 hard gate；
- 但它比“再找一个新确认信号”更接近 desk 当前真正缺的一层：**权益曲线安全阀**。

### 当前最小 evidence（仅 intake，不做本地 replication）
从 digest 可直接提炼的 reader-facing 锚点：
- 论文侧给出：风险控制 / 动态退出模块对 Sharpe 与回撤有显著贡献；
- 工程侧给出：可直接冻结的状态机原型参数，如
  - `dd_reduce = 0.12`
  - `reduce_size = 0.25`
  - `recover_to_peak = 0.95`

这足够把它从“泛泛风控口号”压成一个 **可复测、可冻结阈值、可接到现有 desk** 的 reserve，而不是空泛想法。

## 6. 轻量 scorecard
artifact：
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/promotion_scorecard.json`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/promotion_scorecard.csv`
- `reports/artifacts/scout_rank145_equity_dd_throttle_overlay_15m/source_intake_card.csv`

- `usefulness = 3/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 2/3`
- `deployability = 3/3`
- `hard-fail flags = not_alpha_but_risk_overlay; path_dependent_recovery_lag; thresholds_unfrozen; local_replication_not_run`
- `recommended_action = keep_P1`
- `why_now = 比继续磨旧 P1 更可能改变 routing：它直接服务 paper/tiny-live 安全边界，而且不要求重写主信号`
- `main_weakness = 目前仍只有论文/开源实现证据，没有在 desk 现有三条主线做冻结阈值本地 A/B`

## 7. 对后续 run 的最小授权边界
如果后续继续给 `Rank 145` 默认预算，只允许做 **1 次真正会改变 verdict 的最小稳定性检查**：

### 允许的唯一下一刀
对 desk 现有任一主线做 frozen-threshold A/B：
- 资产：`BTC / ETH / SOL`
- 周期：`15m`
- 样本：近 `180d`
- 成本：`6 / 10 / 15 bps`
- baseline：原策略
- overlay：
  - `equity_dd_from_peak > {8%,10%,12%}` -> `gross_size *= {0.25,0.5}`
  - `equity >= {95%,98%} * peak_equity` 才恢复

### 只看 4 个指标
1. `max_drawdown`
2. `calmar`
3. `post_cost_return`
4. `time_in_reduced_mode`

### 过门槛才可升层
- 若 `MDD` 至少改善 `15%`，且 `post_cost_return` 损伤不超过 `10%`，才允许从 `keep_P1` 讨论到 `promote_P2`；
- 否则直接留在 `evidence pool`，不继续烧默认轮次。

## 8. 本轮结论
- 这轮最诚实的选择，是把 `Rank 145` 作为新的 fresh intake reserve 写进顶板，而不是回头对旧 P1 做重复劳动。
- 它当前最像的是 **shared live-safety overlay 候选**，而不是 shared alpha candidate。
- 因为它更接近 deployment 边界，所以即便现在只到 `P1 / keep_P1`，边际价值也高于再给 `Rank 140 / 144` 补同义切片。
