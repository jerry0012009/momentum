# Strategy Review (bot2)

Time: 2026-03-23 05:37 UTC

## 本轮一句话判断
这轮不能再把任何已 budget-used 的 `P1` 硬写回默认 primary：`Rank 144` 已 park，`Rank 145` 已完成 frozen-threshold A/B 且确认 `no promote`，`Rank 140` 也在 `05:26 UTC` 被正式收口为 **`active compare anchor / balance-aware freeze / not default primary`**。因此 desk 顶板应最小改成：**Run 1 留给 fresh intake reserve，Run 2 才是 Rank 140 compare，Run 3 再给 Rank 111 这类 evidence anchor。**

## 1) 必检：repo / 最近 optimization / 最近 strategy review / cron
### Repo
- `git status` 仍是大面积 dirty workspace。
- 本轮只维护 `docs/TODO.md` 顶部 `TRADING DESK BOARD`，不做 cleanup。

### 最近 `research/optimization_loop/`
- `2026-03-23_0526_rank140_balance_aware_freeze.md`
- `2026-03-23_0501_rank144-clean-rep-park.md`
- `2026-03-23_0438_rank145-frozen-threshold-ab.md`
- `2026-03-23_0423_rank145-equity-dd-throttle-intake.md`
- `2026-03-23_0404_rank144-vol-commonality-intake.md`

### 最近 `research/strategy_review/`
- `2026-03-23_0454_strategy-review.md`
- `2026-03-23_0358_strategy-review.md`
- `2026-03-23_0317_strategy-review.md`
- `2026-03-23_0224_strategy-review.md`
- `2026-03-23_0135_strategy-review.md`

### 当前 cron（desk relevant）
- `bot2-strategy-review-40m`：enabled，当前运行中
- `bot3-momentum-auto-opt-13m`：enabled，最近 `ok`
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
1. `Rank 145 / equity drawdown throttle + recovery hysteresis overlay`
   - `P1 / keep_P1 / budget used / no promote / 不再作为默认 primary`
2. `Rank 14b / directional-breadth-coherence long-side continuation veto`
   - `P1 / keep_P1 / family-level evidence strengthened / budget used / 不再作为默认 primary`
3. `Rank 140 / pbo-cscv deflated sharpe honesty gate`
   - `P1 / keep_P1 / active compare anchor / balance-aware freeze / 不再作为默认 primary`
4. `Rank 125 / range location veto gate`
   - `P1 / keep_P1 / budget used`
5. `Rank 112 / basis dislocation short veto`
   - `P1 / keep_P1 / budget used`
6. `Rank 111 / abnormal-return event clock`
   - `P1 / keep_P1 / compare 价值高于继续单独烧预算`
7. `Rank 144 / Rank 143 / Rank 142 / Rank 141`
   - `P0 / park / evidence only`
8. `Rank 137 / 138 / 127 / 136...113`
   - `P0 / park / evidence pool`

### Next 3 bot3 runs
1. `Run 1 = fresh intake reserve / 当前唯一 guard-pass 的新 Scout`
   - 当前 queue 为空，因此首位必须留给下一条 fresh intake，而不是让 exhausted P1 回流成 primary。
2. `Run 2 = Rank 140 compare anchor / shortest decisive compare`
   - 若暂无新的 guard-pass intake，只允许做 `Rank 140` 与 `Rank 111` 的最短 decisive compare。
3. `Run 3 = Rank 111 evidence anchor / cheap decisive fallback`
   - 仅在仍无 fresh reserve 时使用；不回头重磨 `Rank 145`、`Rank 14b`、`Rank 125`、`Rank 112` 这些已 budget-used 的 P1。

## 3) 为什么本轮必须改顶板
上轮 `04:54 UTC` 还把 `Run 1` 回拨到 `Rank 144` 唯一允许的最小 replication；而 `05:00 UTC` 这条线已经被 clean replication 正式打回 `park`。

随后又有两条关键信息补全了 routing：
- `04:38 UTC`：`Rank 145` 的 frozen-threshold A/B 证明它当前连 desk 共享代理都触发不了，不能升 `P2`；
- `05:26 UTC`：`Rank 140` 被正式 freeze 为 `balance-aware compare anchor`，说明它可以留在比较位，但也不该回到默认主资源位。

因此如果顶板还继续写 `Run 1 = Rank 140`，就违反了 brief 里“连续两轮没有 promote / park / hard-fail / decisive routing gain 的 P1 不得继续占 primary”的纪律。

## 4) desk-level final call
- `recommended_action = update board minimally`
- `why_now = 05:26 UTC 的 Rank 140 freeze 已把最后一个可能被误写回 primary 的 active P1 也正式收口`
- `main_weakness = 当前 desk 缺的不是 compare anchor，而是一条新的 fresh intake reserve`

## 5) 本轮实际改动
- 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 把 `Rank 140` 的 active 口径补成 `balance-aware freeze`
  - 把 `Next 3` 改成 `fresh intake reserve -> Rank 140 compare -> Rank 111 fallback`
  - 用 `05:26 UTC` 的 `Rank 140` freeze 替换最旧 evidence 条目
