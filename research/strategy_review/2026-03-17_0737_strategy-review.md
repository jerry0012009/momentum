# 2026-03-17 07:37 UTC · Desk Board Review

## 本轮一句话判断

**这轮 desk judgment 的核心不是再换席，而是确认 07:04~07:32 这三刀已经把桌面重新收口：`Paper Seat = EMA` 且 A 股 due-follow-up 已真实消化、当前重新回到 `waiting_not_due`；`Live Seat` 继续暂空；`Rank 26` 那次 `P2 -> 升 P3 / 压回 park` 的最小检查已经做完并压回 `park`；`Rank 17` 当前最小 `P3 weekly review` 也已被压成 `writeback seed`。因此当前最诚实的 Scout 读法是：**桌上保留两个 `P3` 身份（`Rank 17`、`Rank 2`），但默认主资源已不该继续磨 `Rank 17 / Rank 26`；若 `Rank 2` 仍无新的真实 append/review need，就直接切新的 `paper / repo based 5m / 15m crypto` fresh intake。**

## 当前 strongest evidence

1. **Paper Seat 的 due-window 已在 07:04 UTC 被真实消化，当前重新回到 `waiting_not_due`**
   - 最新 optimization log：`2026-03-17_0706_ema-ashare-due-followup.md`
   - 实际执行了：
     - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 并真实追加了 1 条 refresh history：
     - `贵州茅台 1d+1wk | A股-1d | latest_completed_bar_utc = 2026-03-16 00:00 UTC`
   - 最新 due guardrail 现在显示全 desk **没有** `due-now / overdue` lane：
     - 美股下一次 close：`2026-03-17 20:00 UTC`
     - Crypto 下一次 close：`2026-03-18 00:00 UTC`
     - A 股三条 lane：`2026-03-18 07:00 UTC`
   - 结论：
     - **`Paper Seat = EMA running paper / waiting_not_due`**；
     - 下一轮不应再继续重复 A 股 due-follow-up。

2. **Live Seat 继续暂空，仍无值得升格者**
   - `Rank 17` 仍是 **`P3 / narrow paper pilot approved（ETH+SOL only）`**，但仍只是 `paper-only`；
   - `Rank 2` 仍是 **`P3 / narrow paper pilot approved`**；
   - `Rank 26` 已在 genuinely verdict-changing 的最小检查后压回 `park`；
   - 因此当前没有任何候选到达 `P4 / tiny-live review candidate`。

3. **Rank 26 的 P2 预算已经用完，本轮最关键的新变化就是它被压回 park**
   - `Rank 26 regime triplet state gate` 先前曾进入 `P2 / paper candidate`；
   - 但 `2026-03-17_0724_rank26-ethsol-recheck-park.md` 已完成那 1 次 genuinely verdict-changing 的最小检查：
     - 不改规则、不追新 bar；
     - 只把 `BTC` 诚实剥离，看 `ETH+SOL-only` 能否支持 `P3 narrow paper pilot`。
   - 结果：
     - `15bps/side` aggregate 约 `+2.29%`；
     - 但只剩 `1/2` 资产为正（`ETH≈+9.89%`、`SOL≈-5.31%`）；
     - 时间桶仍有明显前段破口（`bucket_1≈-8.44%`）。
   - 结论：
     - **`Rank 26 -> P0 / park / evidence pool`**；
     - 这条线已用完当前默认 Scout 预算，不再继续占主资源。

4. **Rank 17 的当前最小 P3 need 也已被如实消化**
   - 最新 optimization log：`2026-03-17_0732_rank17-weekly-review-writeback-seed.md`
   - 这轮不是再磨 wording，而是把已排队的 weekly review 正式压成：
     - `narrow_paper_pilot_ethsol_weekly_review_writeback_seed.csv`
   - 共 3 行 append-ready seed：
     - `ETH-USD | bucket_1`
     - `SOL-USD | bucket_1`
     - `SOL-USD | bucket_2`
   - 结论：
     - `Rank 17` 仍是 **`P3 / narrow paper pilot approved（ETH+SOL only）`**；
     - 但当前这条线的**现成最小合法维护已经被消化掉**；
     - 继续默认围着它补近义接线，边际价值会明显下降。

5. **因此当前 Scout 的真正 active 读法，已经不是 `P3 + P3 + P2`，而是“两条 P3 身份还在，但默认主资源应切向 fresh intake”**
   - `Rank 17`：P3 身份仍在，但当前最小 legal maintenance 已消化；
   - `Rank 2`：P3 身份仍在，但本轮没看到新的真实 `append/review need`；
   - `Rank 26`：P2 已结束并压回 park；
   - 所以当前最诚实的主资源顺序应改读为：
     - **先看 `Rank 2` 是否出现真实 P3 need；若没有，就直接切 fresh intake。**

## 当前 P0 / P1 / P2 / P3 / P4 分级（authoritative read）

- **P0 = park / evidence only**
  - `Rank 1 / 3 / 4 / 4b / 5 / 7 / 8 / 9 / 10 / 11 / 12 / 13 / 14 / 15 / 16 / 18 / 19 / 20 / 21 / 22 / 23 / 24 / 25 / 26`
  - `Rank 17` 的 `BTC` 单腿（`excluded red-watch leg`）
- **P1 = weak candidate**
  - **当前空缺**
- **P2 = paper candidate**
  - **当前空缺**
- **P3 = narrow paper pilot**
  - `Rank 17 pullback recovery confirmation（ETH+SOL only）`
  - `Rank 2 combo_all`
- **P4 = tiny-live review candidate**
  - **当前空缺**

## Desk verdict

- **Paper Seat**：继续由 `EMA baseline family` 占据，当前重新回到 **`waiting_not_due`**。
- **Live Seat**：继续暂空。
- **Scout Seat**：
  - 仍保留两个 `P3` 身份：
    1. `Rank 17`（`P3 / narrow paper pilot approved（ETH+SOL only）`）
    2. `Rank 2`（`P3 / narrow paper pilot approved`）
  - 但当前默认主资源判断已变成：
    - `Rank 17` 的现成最小 need 已被消化；
    - `Rank 26` 已 park；
    - 因此若 `Rank 2` 也无新 need，**就应直接切 fresh intake**。

## 接下来优先级 Top 1~3

1. **先确认 `Rank 2` 是否出现新的真实 P3 append/review need**
   - 当前这是桌上唯一还没被明确“本轮已消化掉最小 need”的 P3。
   - 只有存在真实 queue / ledger / monitoring / review append need，才值得回补。

2. **若 `Rank 2` 仍无真实 need，就直接切新的 fresh intake**
   - 继续限定在：**paper / repo based 的 `5m / 15m crypto` 候选**；
   - 目标仍是：`source intake -> clean replication -> Light Stability Pack -> park / paper candidate / narrow paper pilot` 的快筛闭环；
   - 不要再继续磨 `Rank 17 / Rank 26` 的近义接线。

3. **只有前两步都 blocked，才回退 tiny-live plumbing**
   - 继续遵守：`Scout Seat > tiny-live plumbing > 其他维护`。

## TODO / web / cron 的改动或建议

### 本轮不改顶板口径
- `docs/TODO.md` 顶部 `TRADING DESK BOARD` 在 `07:32 UTC` 已经同步到当前最准口径：
  - `EMA due-follow-up` 已消化
  - `Rank 26 -> park`
  - `Rank 17` 当前最小 P3 need 已压成 writeback seed
  - 若 `Rank 2` 无新 need，则默认切 fresh intake
- 因此这轮属于**无新 verdict 的巡检确认**，不再额外改 TODO 文案。

### 本轮已做
- 新增本轮 review：`research/strategy_review/2026-03-17_0737_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### cron
- 当前 cron 大体仍可维持：
  - `bot2-strategy-review-40m = running`
  - `bot3-momentum-auto-opt-13m = ok`
- 但有一条值得单独注意：
  - `bot7-quant-digest-4h = error`
- 这不影响本轮 desk 排兵，但建议在 desk 之外单开一个小排查，不要混进本轮主判断。

## 风险与不确定性

1. 现在 `P2` 又重新清空，说明 `Rank 25 / 26` 两条 fresh intake 都在最小诚实检查后被快速打回 `park`；这符合 desk 的“短、快、诚实”，但也意味着下一条新 intake 仍得继续找。
2. `Rank 17` 和 `Rank 2` 仍在桌上，但若接下来几轮主要都只是在补 writeback / operator packet / closeout 近义卡，就应继续降低它们的默认主资源优先级。
3. 当前 `Paper Seat` 已重新回到 `waiting_not_due`，所以 bot3 不能再借 A 股 due-follow-up 名义重复消耗 run。

## 本轮一句话结论（给 Jerry）

**这轮最重要的不是新升格，而是确认收口：A 股 EMA due-follow-up 已真实消化；`Rank 26` 那次 `P2` 检查已做完并压回 park；`Rank 17` 当前最小 P3 weekly-review 也已被写成 writeback seed。现在桌上虽然还挂着两个 `P3`（`Rank 17 / Rank 2`），但默认主资源已经不该继续磨 `Rank 17 / Rank 26`；如果 `Rank 2` 也没有新 need，下一轮就该直接切新的 fresh intake。**
