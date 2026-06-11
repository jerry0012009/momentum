# 2026-03-17 09:37 UTC · Desk Board Review

## 本轮一句话判断

**这轮 desk judgment 不换席，但 Scout 结构确实发生了实质升级：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续暂空；`Rank 29 trendline breakout navigator` 已在 `09:21 UTC` 完成最小 clean replication，并在 `09:25 UTC` 通过唯一允许的 cheap honesty check（`no_overlap_guard`）后，从 fresh intake / weak candidate 一路推进到 **`paper candidate pool（P2）`**。因此当前最诚实的桌面读法是：`Scout Seat = Rank 17（P3） + Rank 2（P3） + Rank 29（P2）`；若继续认领，默认主资源不该回去磨旧 P3，而应优先给 `Rank 29` 那 1 次 genuinely verdict-changing 最小检查，直接回答它是 `升到 P3 narrow paper pilot` 还是 `压回 park`。**

## 当前 strongest evidence

1. **Paper Seat 继续由 EMA 占据，且当前仍是真实 `waiting_not_due`**
   - 最新 due guardrail 仍显示：
     - 美股下一次 close：`2026-03-17 20:00 UTC`
     - Crypto 下一次 close：`2026-03-18 00:00 UTC`
     - A 股三条 lane：`2026-03-18 07:00 UTC`
   - 当前全 desk **没有** `due-now / overdue` lane。
   - 结论：
     - **`Paper Seat = EMA running paper / waiting_not_due`**；
     - bot3 当前必须继续按 `Scout Seat > tiny-live plumbing > 其他维护` 的顺序导流，不能在 EMA waiting-window 空转。

2. **Live Seat 继续暂空，没有候选值得升格**
   - `Rank 17` 仍是 **`P3 / narrow paper pilot approved（ETH+SOL only）`**，但仍只是 `paper-only`；
   - `Rank 2` 仍是 **`P3 / narrow paper pilot approved`**；
   - `Rank 29` 虽然已经推进到 **`P2 / paper candidate`**，但还没有到 `P3`，更没有到 `P4 / tiny-live review candidate`；
   - 因此当前没有任何候选达到 `Live Seat` 的升格门槛。

3. **Rank 29 已从 fresh intake 正式推进到 `P2 / paper candidate`**
   - `2026-03-17_0921_rank29-clean-replication.md` 已完成最小 clean replication，主变体 `breakout_align_ge2` 的 first verdict 很强：
     - `6bps/side ≈ +75.23%`
     - `positive_asset_ratio = 3/3`
     - `mean_trades ≈ 160`
     - `mean_false_break_ratio ≈ 7.56%`
     - `10bps ≈ +54.18%`
     - `15bps ≈ +31.40%`
     - `20bps` 仍有 `2/3` 资产为正
   - 但那一轮仍保持克制：先只给了 **`P1 weak candidate / one cheap honesty check at most`**，没有直接偷升 `P2/P3`。
   - `2026-03-17_0925_rank29-no-overlap-honesty-check.md` 随后执行了那唯一允许的 cheap honesty check：
     - 对照 `overlap_allowed` vs `no_overlap_guard`
     - 结果：
       - `6bps ≈ +57.79%`，`3/3` 资产为正
       - `10bps ≈ +40.99%`，`3/3`
       - `15bps ≈ +22.49%`，`3/3`
       - `20bps ≈ +6.41%`，`2/3`
     - 交易数虽从 overlap 模式下修，但没有出现“去 overlap 即坍塌”的红旗。
   - 因此当前更诚实的 desk 口径应是：
     - **`Rank 29 -> paper candidate pool（P2）`**。

4. **Rank 28 已完成当前预算并压回 park，不再是 active 主线**
   - `Rank 28 cross-market intraday leader-laggard TSMOM` 已在 `08:41 UTC` 完成 clean replication + Light Stability Pack 并压回 `park`：
     - `funding_8h_q60 @ 6bps ≈ -16.58%`
     - `positive_asset_ratio = 0/3`
     - 时间 / 参数 / 跨标的 / 成本-交易数四项全部硬 fail
   - 因此当前不应继续把它当 active Scout 候选。

5. **Rank 17 / Rank 2 的 P3 身份仍保留，但当前都没有新的真实 append/review need**
   - `Rank 17` 当前最小 weekly-review writeback seed 已在 `07:32 UTC` 做完；
   - `Rank 2` 当前最小 weekly-review writeback seed 已在 `07:46 UTC` 做完；
   - 因此当前默认主资源不该继续围着这两条 P3 做近义 wiring。
   - 更诚实的当前 Scout 读法应是：
     - **旧 P3 只在有新 need 时回补；当前新增主点是 `Rank 29` 的 `P2 -> P3 / park` 决策刀。**

## 当前 P0 / P1 / P2 / P3 / P4 分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1 / 3 / 4 / 4b / 5 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20 / 21 / 22 / 23 / 24 / 25 / 26 / 27 / 28`
  - `Rank 17` 的 `BTC` 单腿（`excluded red-watch leg`）
- **P1 = weak candidate**
  - **当前空缺**（`Rank 29` 已在 no-overlap 检查后升到 `P2`）
- **P2 = paper candidate**
  - `Rank 29 trendline breakout navigator / multi-swing causal breakout state machine`
- **P3 = narrow paper pilot**
  - `Rank 17 pullback recovery confirmation（ETH+SOL only）`
  - `Rank 2 combo_all`
- **P4 = tiny-live review candidate**
  - **当前空缺**

## Desk verdict

- **Paper Seat**：继续由 `EMA baseline family` 占据，当前仍是 **`running paper / waiting_not_due`**。
- **Live Seat**：继续暂空。
- **Scout Seat**：当前真正的 active 候选结构是：
  1. `Rank 17`（`P3 / narrow paper pilot approved（ETH+SOL only）`）
  2. `Rank 2`（`P3 / narrow paper pilot approved`）
  3. `Rank 29`（`P2 / paper candidate`）
- 但默认主资源判断应明确写成：
  - `Rank 17 / Rank 2` 当前都没有新的真实 `append/review need`；
  - 因此若继续认领 `Scout Seat`，**优先落到 `Rank 29` 的那 1 次 genuinely verdict-changing 最小检查**；
  - `Rank 28` 已 park，不再继续占默认主资源。

## 接下来优先级 Top 1~3

1. **优先给 `Rank 29` 做 1 次 genuinely verdict-changing 的最小检查**
   - 目标固定为二选一：
     - **升到 `P3 / narrow paper pilot`**，或
     - **压回 `P0 / park`**
   - 默认不要让它长期停在 `P2` 研究态。

2. **若 `Rank 29` 被快速否掉，再回到新的 fresh intake 比较**
   - 继续限定在：**paper / repo based 的 `5m / 15m crypto` 候选**；
   - 先看 `Rank 5 / Rank 6` 是否仍因 prediction-market / equity proxy 外部依赖不够便宜诚实；
   - 若仍不够便宜诚实，就继续挑下一条新的 fresh intake。

3. **只有出现新的真实 `P3 append/review need` 时，才回补 `Rank 17 / Rank 2`**
   - 当前两条 P3 不该默认继续磨；
   - 只有真实 queue / ledger / monitoring / review append need 出现时，才重新拿到主资源。

## TODO / web / cron 的改动或建议

### 本轮不改顶板口径
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 在 `09:25 UTC` 已经同步到当前最准口径：
  - `EMA` 继续 `waiting_not_due`
  - `Rank 28 -> park`
  - `Rank 29 -> paper candidate pool（P2）`
  - 下一轮默认应给 `Rank 29` 那 1 次 `P2 -> P3 / park` 决策刀
- 因此这轮属于**无新 desk verdict 的巡检确认**，不再额外改 TODO 文案。

### 本轮已做
- 新增本轮 review：`research/strategy_review/2026-03-17_0937_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### cron
- 当前 desk 相关 cron 仍可维持：
  - `bot2-strategy-review-40m = running`
  - `bot3-momentum-auto-opt-13m = ok`
- 外围仍有一条需单独排查：
  - `bot7-quant-digest-4h = error`
- 这不影响本轮 desk judgment，但建议继续与交易台主线分开处理。

## 风险与不确定性

1. `Rank 29` 的 current read 很强，但当前还没做完整 `Light Stability Pack`；这正是为什么它现在只能是 `P2`，还不是 `P3`。
2. `Rank 17 / Rank 2` 虽仍在桌上，但如果接下来几轮主要都只剩 writeback / closeout 近义卡，就应继续压低它们的默认主资源优先级。
3. `Paper Seat` 继续 `waiting_not_due`，因此 bot3 不能再借 paper due-follow-up 名义空转。

## 本轮一句话结论（给 Jerry）

**这轮最大的变化不是换席，而是 `Rank 29` 已经从 fresh intake 真正推进到了 `paper candidate（P2）`：最小 clean replication 很强，而且 no-overlap 诚实检查也没把它打爆。桌上两个 `P3`（`Rank 17 / Rank 2`）仍保留身份，但当前默认主资源不该继续磨旧 P3；下一轮最该做的就是给 `Rank 29` 那 1 次 `P2 -> P3 / park` 的决策刀。**
