# 2026-03-16 18:38 UTC · Desk Board Review

## 本轮一句话判断

**这轮不是换席，但 Scout 桌面确实改了：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续保持暂空；真正变化在 `Scout Seat`——`Rank 2 combo_all` 已不再默认卡在 `paper_candidate_only / blocked`，而是被提升为 **`narrow paper pilot approved`**；同时原先已 `park` 的 stat-arb 方向现在开出了一个很窄的 `Rank 4b` 重开口，并且它已经完成 `clean replication v2`，当前最诚实位置是 **`one_more_light_check`**。**

## 当前 strongest evidence

1. **Paper Seat 继续是真实 waiting_not_due**
   - `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示各 lane 没有 `due-now / overdue`；
   - 因此 `EMA` 继续是 running paper，但本窗口只该做 waiting 状态维护与 next-close 核对，不应回到默认 bot3 主资源。

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `breakout` 仍是 bench/历史证据池，没有 genuinely new blocker reduction；
   - 因此本轮最诚实 desk call 仍是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 2 `combo_all` 已从“blocked closeout 文档打磨”释放成 `narrow paper pilot approved`**
   - 当前 board 已明确改口：
     - 历史上 `16:21–18:20 UTC` 的 `receipt-chain / closeout / replay` 一串产物，保留为 tiny-live 证据池即可；
     - 但它们**不再代表当前默认 desk 路线**；
     - `Rank 2` 现在更诚实的默认读法是：**已可进入窄范围 paper pilot**。
   - 这意味着：
     - 若继续认领 `Rank 2`，默认只允许补 `paper ledger / monitoring / refresh / review` 的最小接线；
     - 不应再把它当作 receipt-chain / closeout 文档打磨对象。

4. **`Rank 4b` 已拿到正式 `clean replication v2`，当前最诚实位置是 `one_more_light_check`**
   - `18:22` 的 sanity scan 先确认：当前最值得先改的是 **model calibration**，不是立刻扩 pair scope；
   - `18:38` 新增正式可复跑 artifact 与网页落点后，得到更硬结果：
     - `ETH/SOL`：`trade_count = 20`，`cumulative_net_return ≈ +2.28%`
     - `BTC/SOL`：`trade_count = 15`，`cumulative_net_return ≈ +0.74%`
     - `BTC/ETH`：`trade_count = 21`，`cumulative_net_return ≈ -6.99%`
   - 与原版 frozen-beta 三组全负相比，`Rank 4b` 已经不是直接 `park`；但因为 `BTC/ETH` 仍明显偏负，两组正 pocket 也仍偏薄，所以当前最诚实 verdict 只能是：
     - **`one_more_light_check`**
     - 还不是 `paper candidate`
     - 更不是 `Live Seat / tiny-live` 候选。

5. **其余候选继续维持 park**
   - `Rank 1 τ-band`：历史 verdict 仍弱，继续 `park`；
   - `Rank 3 third-touch + EMA/MACD`：样本与参数邻域已明确偏薄，继续 `park`；
   - 原版 `Rank 4 frozen-beta stat-arb`：原 verdict 仍是 `park`，没有被推翻；只是另外合法开了一个窄重开分支 `Rank 4b`。

## 当前 weakest / should-park lines

- 在没有 genuinely new blocker reduction 前重开 breakout heavy analysis：继续 park。
- 继续把 `Rank 2` 当作 receipt-chain / closeout 文档打磨对象：应停止。
- 把 `Rank 4b` 的 first-pass 正 pocket误读成已经够格 `paper candidate`：为时过早。
- 继续把 `Rank 1/3` 当默认主资源位：继续 park。

## Desk verdict

- **Paper Seat：`EMA`**
- **Paper Seat 当前读法：`running paper pilot / waiting_not_due`**
- **Live Seat：`暂空 / waiting for next promoted scout winner`**
- **Live Seat 当前判断：继续保持暂空；本轮没有候选值得被升格。**
- **Scout Seat：当前复刻的 paper / repo candidates 与阶段如下：**
  1. `τ-band / no-trade breakout filter`（De Angelis et al. 2021）→ `park`
  2. `volume + support-flip + higher-low / combo_all`（Yumna et al. 2024）→ **`narrow paper pilot approved`**
  3. `third-touch + EMA/MACD confluence`（Wiśniewski 2024）→ `park`
  4. `crypto pairs stat-arb`（原 frozen-beta 版本）→ `park`
  5. `Rank 4b crypto stat-arb reframe`（rolling-beta 窄重开）→ **`one_more_light_check`**

## 接下来优先级 Top 1~3

1. **优先把 `Rank 4b` 补成最小 `Light Stability Pack`，不要再回头打磨 Rank 2 closeout 文档**
   - 默认先做：
     - `time stability`
     - 或 `cost / trade-count stability`
   - 只要这两刀里任一明显翻弱，就更诚实地把 `Rank 4b` 压回 `park`。

2. **若继续认领 `Rank 2`，只允许做 `paper pilot` 的最小接线**
   - 例如：
     - `paper ledger`
     - `monitoring`
     - `refresh / review wiring`
   - 不再默认补 admission write-back / receipt-chain / closeout 近义卡。

3. **其余候选默认停在 evidence pool**
   - `Rank 1 / Rank 3 / 原 Rank 4` 不再占默认主资源；
   - 若要重开，必须由 bot2 明确点名。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-16_1838_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不改 `docs/TODO.md`**：当前顶板已经由最新 bot3 产物完成了关键 routing 改写：
  - `Rank 2 -> narrow paper pilot approved`
  - `Rank 4b -> one_more_light_check / clean replication v2`
- **不改 cron 频率**：当前 `bot2`/`bot3` 都显示 `ok`，上一轮看到的 bot2 timeout 已暂时恢复。

## 风险与不确定性

1. `Rank 4b` 虽然从全负推进到了有两个轻微正 pocket，但仍只是 clean replication v2；还没有通过最小 `Light Stability Pack`。
2. `Rank 2` 的提升是路线切换，不是已经完成 paper pilot wiring；若后续继续把时间花在 closeout 文档而不是 paper 接线，就会再次偏离。
3. `Live Seat` 长时间保持暂空仍然是诚实的，但也意味着 Scout 需要更快把 `Rank 4b` 这类窄重开候选判清楚：要么继续前推，要么及时压回 `park`。

## 本轮一句话结论（给 Jerry）

**这轮 Paper/Live 没换席，但 Scout 路线确实换挡了：`Rank 2 combo_all` 已从“blocked closeout 打磨对象”提升成 `narrow paper pilot approved`；同时 `Rank 4b` 已完成 rolling-beta 窄重开的正式 clean replication v2，当前最诚实的位置是 `one_more_light_check`。因此接下来 bot3 不该再默认围着 Rank 2 的 receipt-chain 文档转，而应优先用一刀最小稳定性检查把 `Rank 4b` 判清，再把 Rank 2 接到真正的 paper wiring 上。**
