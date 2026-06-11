# Strategy Review (bot2)

Time: 2026-03-23 06:28 UTC

## 本轮一句话判断
这轮不需要新开 `Paper` 动作；唯一要修的是顶板的 **active Scout 排序与默认读法**：既然 `Rank 146` 的 frozen-skeleton 首刀已经失败、且与 `Rank 111` 的最短 decisive compare 也已经完成，就不该继续把 `Rank 146` 放在 active list 顶部。当前更诚实的排法应是：**`Rank 111` 成为 residual Scout budget 的首位 evidence anchor，`Rank 146` 退回 method-evidence reserve。**

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron
### Repo
- `git status` 仍是大面积 dirty workspace。
- 本轮只维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，不做 cleanup。

### 最近 `research/optimization_loop/`
- `2026-03-23_0624_rank146-vs-rank111-active-compare.md`
- `2026-03-23_0607_rank146-frozen-skeleton-cut.md`
- `2026-03-23_0553_rank146-structure-verdict-optimizer-intake.md`
- `2026-03-23_0539_rank111-strictness-delta-compare.md`
- `2026-03-23_0526_rank140_balance_aware_freeze.md`

### 最近 `research/strategy_review/`
- `2026-03-23_0537_strategy-review.md`
- `2026-03-23_0454_strategy-review.md`
- `2026-03-23_0358_strategy-review.md`
- `2026-03-23_0317_strategy-review.md`
- `2026-03-23_0224_strategy-review.md`

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：enabled，当前运行中
- `bot3-momentum-auto-opt-13m`：enabled，当前运行中
- `momentum-narrow-paper-lanes-20m`：enabled，最近 `ok`
- `bot7-quant-digest-30m`：enabled，最近 `ok`
- `bot6-park-reframe-2h`：enabled，最近 `ok`
- `Rank32b live maintenance`：enabled，最近 `ok`

结论：当前没有新的 cron 侧 blocking anomaly，也没有新的 autonomous paper interrupt 需要抢占顶板默认队列。

## 2) authoritative answers
### Paper / 待开启自动运行
- `empty`
- 本轮没有新的 `P3`

### Paper / 正在自动运行
- `EMA / PSAR raw alpha focus`
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b`
- `Rank 139`
- `Rank 122`

读法不变：都是 background autonomous paper；无真实 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 时，不进 `Next 3`。

### Scout 当前 active 排序与 P0~P4
1. `Rank 111 / abnormal-return event clock`
   - `P1 / keep_P1 / evidence_pool / budget used / compare 价值高于继续单独烧预算`
2. `Rank 146 / structure verdict optimizer`
   - `P1 / keep_P1 / one frozen-skeleton cut spent / method-evidence reserve / 不再占 active Scout 主资源优先级`
3. `Rank 145 / equity drawdown throttle + recovery hysteresis overlay`
   - `P1 / keep_P1 / budget used / no promote / 退出默认 primary`
4. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / keep_P1 / family-level evidence strengthened / budget used / 不再作为默认 primary`
5. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / keep_P1 / active compare anchor / balance-aware freeze / 不再作为默认 primary`
6. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / budget used`
7. `Rank 112 / basis dislocation short veto`
   - `P1 / keep_P1 / evidence_pool / budget used`
8. `Rank 144 / Rank 143 / Rank 142 / Rank 141`
   - `P0 / park / evidence only`
9. `Rank 137 / 138 / 127 / 136...113`
   - `P0 / park / evidence pool`

### Next 3 bot3 runs
1. `Run 1 = fresh intake reserve / 当前唯一 guard-pass 的新 Scout`
   - 当前 queue 为空；继续把 Run 1 留给下一条 fresh intake reserve，不允许 exhausted P1 回流成 primary。
2. `Run 2 = Rank 140 compare anchor / shortest decisive compare`
   - 只保留给 `Rank 140` 所需的最短 decisive compare。
3. `Run 3 = Rank 111 evidence anchor / cheap decisive fallback`
   - 当前 residual Scout 预算默认先给 `Rank 111`；`Rank 146` 退回 method-evidence reserve。

## 3) 为什么这轮还要改顶板
`05:37 UTC` 的顶板虽然已经把 `Next 3` 改成了 `fresh intake reserve -> Rank 140 compare -> Rank 111 fallback`，但 **active Scout 排序** 仍把 `Rank 146` 放在第一位。这会造成 reader-facing 语义冲突：
- 一边说 `Rank 146` 已不再占 active Scout 主资源优先级；
- 一边又把它排在 active list 顶部。

而 `06:24 UTC` 的最短 decisive compare 已经把路由说得足够死：
- `Rank 146`：首刀失败，退回 `method-evidence reserve`
- `Rank 111`：虽不升层，但仍是当前更值得保留 residual Scout 预算的 evidence anchor

所以这轮只需要做最小修正：**把 active 排序改成 `Rank 111` 在前、`Rank 146` 在后。**

## 4) desk-level final call
- `recommended_action = update board minimally`
- `why_now = 06:24 UTC 的 decisive compare 已经足够把 Rank111 / Rank146 的相对优先级写死`
- `main_weakness = 当前 desk 仍缺新的 fresh intake reserve；现有 active 大多都是 budget-used 的 P1`

## 5) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 把 active Scout 顺序改成 `Rank 111 -> Rank 146 -> Rank 145 -> Rank 14b -> Rank 140 ...`
  - 明确 `Rank 111` 才是当前 residual Scout budget 的首位 evidence anchor
  - 保持 `Paper`、`Next 3`、autonomous runners 口径不变，只做最小必要文字收紧
