# 2026-03-20 07:52 UTC bot2 strategy review

## 本轮先检查了什么
- repo status：`master`
- 当前工作区脏文件：`git status --short | wc -l = 1709`
- 最近 strategy review：`2026-03-20_0706_strategy-review.md`
- 最近 optimization logs（最新 4 条）：
  - `2026-03-20_0747_rank113-alpha-beta-intake.md`
  - `2026-03-20_0735_rank112-basis-clean-replication.md`
  - `2026-03-20_0715_rank112-basis-dislocation-intake.md`
  - `2026-03-20_0652_rank111_event_clock_clean_replication.md`
- 最近 quant digest 新证据：
  - `2026-03-20_0742_pullback-two-sided-window-verdict.md`
- 当前关键 cron：
  - `bot3-momentum-auto-opt-13m`：启用中，本轮查看时处于运行中，上一轮 `ok`
  - `momentum-narrow-paper-lanes-20m`：启用中，本轮查看时处于运行中，上一轮 `ok`
  - `bot2-strategy-review-40m`：启用中，上一轮 `ok`
  - `bot7-quant-digest-30m`：启用中，上一轮 `ok`
  - `bot6-park-reframe-2h`：启用中，上一轮 `ok`
- EMA / paper 实时核对：
  - `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv` 显示当前所有 lane 仍为 `waiting_not_due`
  - `创业板ETF 1d = active_primary / next_expected_close_utc=2026-03-23 07:00 UTC`
  - `美股 1d+1wk = active_secondary_backstop / next_expected_close_utc=2026-03-20 20:00 UTC`
  - `Crypto 1d+1wk = active_secondary_backstop / next_expected_close_utc=2026-03-21 00:00 UTC`
- narrow paper continuity 实时核对：
  - `manual_narrow_paper_last_run_summary.json @ 2026-03-20T07:24:44Z`
  - `new_closed_trades_appended = 0`
  - 说明 hosted `P3` lanes 当前没有新的 status-changing event 需要插队

## Desk verdict（直接回答本轮 5 个问题）

### 1. 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Primary paper anchor**：`EMA / 创业板ETF 1d（active_primary）`
- EMA 体系内仍在跑的 hosted / backstop paper lanes：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d` 仍为 `shadow_watch`
- 独立 hosted narrow-paper continuity lanes（已有专属 cron / sidecar 托管，不是新 seat）：
  - `Rank 2`
  - `Rank 17`
  - `Rank 29`
  - `Rank 32b`
- 结论：当前整桌仍是 **`Paper Seat = waiting_not_due`**，但这只说明 EMA primary lane 现在不 due；**不等于 bot3 可以空转**。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  - `Rank 113 / alpha-beta abstain / profit-window` 仅完成 `source intake + honesty gate`，还没做 `clean replication`
  - `Rank 112 / basis dislocation short veto` 已完成最小 clean replication，但结论只是 **`P1 weak candidate / evidence_pool / budget used`**，不足以升到 `P2`
  - `Rank 111 / abnormal-return event clock` 也只停在 **`P1 evidence_pool / budget used`**
- 因此当前没有任何候选够资格抢 `Live Seat`。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- 当前主点：**`Rank 113 / alpha-beta abstain / profit-window`**
  - 来源：论文 + repo 思路
  - 当前任务位：`1 次最小 clean replication`
- 当前紧邻后备 fresh-intake 位：**`Rank 114 / pullback → two-sided breakout window verdict`**
  - 来源：`2026-03-20 07:42` 的 GitHub repo digest
  - 当前只冻结为 `source intake reserve`，尚未抢占 `Rank 113`
- 已退到 evidence pool、不再默认占主资源位：
  - `Rank 112 / basis dislocation short veto`
  - `Rank 111 / abnormal-return event clock`

### 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 113 / alpha-beta abstain / profit-window` = **`P1`**（`guard-passed / clean replication next`）
- `Rank 114 / pullback → two-sided breakout window verdict` = **`P0`**（`source intake reserve / repo-based`）
- `Rank 112 / basis dislocation short veto` = **`P1`**（`clean replication done / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock` = **`P1`**（`clean replication done / evidence_pool / budget used`）
- `Rank 93 / 90 / 91 / 82 / 80 / 81` = **`P1`**（`older evidence_pool / budget used`）
- `Rank 110 / 109 / 108 / 107 / 106 / 105 / 104 / 103 / 102 / 101 / 100 / 99 / 98 / 97 / 96 / 95 / 94 / 92 / regression-channel-width` = **`P0`**（`park / evidence only`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` = **`P3`**（`hosted narrow paper continuity / sidecar only`）
- 当前 **`P2` 仍空，`P4` 仍空**。

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 若出现真实 `due-now / overdue`，先做 guarded refresh；否则不允许把 `waiting_not_due` 误读成整桌等待。
2. **Run 2 = 若 EMA 仍 waiting_not_due，则只给 `Rank 113 / alpha-beta abstain / profit-window` 1 次最小 clean replication**
   - 统一口径必须继续保持：`signal 当根及之前数据 + next-bar open + no-overlap`
3. **Run 3 = 分叉写死，不再含糊**
   - 若 `Rank 113` clean replication 显示 honest uplift 且无 decisive fail：**直接做最小 `P2 / paper candidate` 升格-or-park 写回**，不要继续停在模糊研究态
   - 若 `Rank 113` hard-fail / exhausted：**优先切 `Rank 114 / pullback → two-sided breakout window verdict` 的 source intake**
   - 只有这两层都 exhausted 后，才允许回退到 `tiny-live plumbing`

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 113 / alpha-beta abstain / profit-window`**
   - 刚完成 source intake + 两条轻量诚实守门
   - 当前正处在最值得花那 1 次最小 clean replication 预算的时点
   - 若 clean replication 不爆雷，理论上下一拍就应逼近 `P2 / paper candidate` 决策，而不是继续讲故事
2. **`Rank 114 / pullback → two-sided breakout window verdict`**
   - 07:42 新 digest 信号质量高，而且更像可复用的 shared execution skeleton
   - 但它现在仍属于 fresh intake reserve；在 `Rank 113` 还有一个高杠杆 cheap check 没做完之前，不该插队抢主位
3. **`Rank 112 / basis dislocation short veto`**
   - 已做过 source intake + 最小 clean replication
   - 当前结论已经收口为 `P1 evidence_pool / budget used`
   - 再继续磨它，边际价值明显低于把 `Rank 113` 走完，或把 `Rank 114` 真正 intake
4. **`Rank 111 / abnormal-return event clock`**
   - 同样已落到 `P1 evidence_pool / budget used`
   - 不应继续默认占主资源

结论：**本轮最值得的动作不是换掉 `Rank 113`，而是把它做完；但同时把 fresh intake 的下一位从泛泛 shortlist 明确收紧成 `Rank 114`。**

## 本轮最小必要更新
- 已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 新增 `2026-03-20 07:52 UTC` 的 bot2 desk review 补充
  - 明确写回：`Rank 113` 仍是主 Scout 位，不改主位
  - 把 `07:42` 新 repo digest 正式冻结为 **`Rank 114 / pullback → two-sided breakout window verdict`**，作为下一位 `fresh intake reserve`
  - 把 `Run 3` 从模糊的“generic fresh intake”改成 **明确分叉**：`Rank 113` 成功则立刻做 `P2 / park` 写回；失败才切 `Rank 114`

## 结论（一句话）
当前 desk 仍是：**`EMA` 继续坐稳 `Paper Seat` 且处于 `waiting_not_due`，`Live Seat` 继续留空，`Scout Seat` 先把 `Rank 113` 做完；如果它不成，下一位不再泛找，而是直接接 `Rank 114 / pullback → two-sided breakout window verdict`。**
