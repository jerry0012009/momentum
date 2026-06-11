# 2026-03-16 19:18 UTC · Desk Board Review

## 本轮一句话判断

**这轮是按最新已生效作战板做的无额外换席巡检：`Paper Seat = EMA running paper / waiting_not_due` 不变；`Live Seat` 继续保持暂空；`Scout Seat` 这轮最重要的变化不是新升格，而是 `Rank 4b` 在补完唯一允许的一刀 `time stability` 后已被更诚实地压回 `park / evidence pool`。因此当前 desk 读法再次收缩为：`Rank 2 combo_all = narrow paper pilot approved` 是唯一仍保留前推资格的候选；`Rank 1 / Rank 3 / 原 Rank 4 / Rank 4b` 全部回到 `park`。**

## 当前 strongest evidence

1. **Paper Seat 继续是真实 waiting_not_due**
   - `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示：
     - 美股下一次 close：`2026-03-16 20:00 UTC`
     - Crypto 1d 下一次 close：`2026-03-17 00:00 UTC`
     - A 股下一次 close：`2026-03-17 07:00 UTC`
   - 因此 `EMA` 继续是 running paper，但本窗口只该做 waiting 状态维护与 next-close 核对，不应重回默认 bot3 主资源。

2. **Live Seat 继续保持暂空**
   - 当前没有任何候选已经走到足以抢占 `Live Seat` 的程度；
   - `breakout` 仍是历史 bench 证据池，无 genuinely new blocker reduction；
   - 因此当前最诚实 desk call 仍是：**`Live Seat = 暂空 / waiting for next promoted scout winner`**。

3. **Rank 2 `combo_all` 仍是唯一保留前推资格的 Scout 候选**
   - 当前顶板已明确：它已从 `paper candidate` 升为 **`narrow paper pilot approved`**；
   - 当前默认不再把它当作 receipt-chain / closeout 文档打磨对象；
   - 若继续认领 `Rank 2`，默认只允许补：
     - `paper ledger`
     - `monitoring`
     - `refresh / review wiring`
     - 或一个真正会改变 paper verdict 的最小检查。

4. **`Rank 4b` 已完成唯一允许的窄重开，并被压回 `park`**
   - `18:38` 时它刚完成 `clean replication v2`，当时最诚实位置是 `one_more_light_check`；
   - `18:53` 新补的 `time stability` 直接给了 hard verdict：
     - `BTC/SOL` overall 虽约 `+0.74%`，但最近 tercile 与最新月份都转负；
     - `ETH/SOL` overall 虽约 `+2.28%`，但最近 tercile 与最新月份也都转负；
   - 对这种 trade count 只有 `15~20` 的快速 Scout 候选来说，这已经足够更诚实地压回 `park / evidence pool`。

5. **其余候选继续维持 park**
   - `Rank 1 τ-band`：历史 verdict 仍弱，继续 `park`；
   - `Rank 3 third-touch + EMA/MACD`：样本与参数邻域都偏薄，继续 `park`；
   - 原版 `Rank 4 frozen-beta stat-arb`：原 verdict 仍是 `park`，没有被推翻。

## 当前 weakest / should-park lines

- 在没有 genuinely new blocker reduction 前重开 breakout heavy analysis：继续 park。
- 继续把 `Rank 4b` 当作当前默认 Scout 主资源位：应停止。
- 继续回头打磨 `Rank 2` 的 closeout / receipt-chain 近义文档：应停止。
- 继续把 `Rank 1/3/4` 包装成仍在前推的 active 候选：应停止。

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
  5. `Rank 4b crypto stat-arb reframe`（rolling-beta 窄重开）→ **`park`**

## 接下来优先级 Top 1~3

1. **若继续在 Scout Seat 上推进，默认先比较新的外部来源 intake / 新 gate，而不是回头继续磨已 park 的旧候选**
   - `Rank 4b` 已完成并关闭；
   - `Rank 1/3/原 Rank 4` 也都在 evidence pool；
   - 因此当前 Scout 若要继续拿默认主资源，优先应是新的高边际候选或新的更强 spec，而不是继续重复旧线。

2. **若继续认领 `Rank 2`，只允许做 narrow paper pilot 的最小接线**
   - 例如：
     - `paper ledger`
     - `monitoring`
     - `refresh / review wiring`
   - 不再默认补 admission / receipt / closeout 的近义卡。

3. **当 Scout 当前没有更高边际动作时，直接回退 tiny-live plumbing / reconciliation / parity / dry-run**
   - 让默认回退链维持干净，不被已 park 的旧候选抢占。

## TODO / web / cron 的改动或建议

### 本轮已改
- 新增本轮 review：`research/strategy_review/2026-03-16_1918_strategy-review.md`
- 刷新首页 index
- 发送中文邮件摘要

### 本轮不改
- **不改 `docs/TODO.md`**：当前顶板已经由最新 bot3 产物完成了这轮最关键的改判：`Rank 4b -> park / evidence pool`。
- **不改 cron 频率**：当前 `bot2` / `bot3` 状态都为 `running/ok`，节奏可先维持。

## 风险与不确定性

1. 当前 active Scout 候选里，真正仍保留前推资格的只剩 `Rank 2`；若后续继续回头磨它的文档而不是接上 paper wiring，就会再次浪费主资源。
2. `Rank 4b` 这次从 `one_more_light_check` 很快回到 `park` 是诚实的，但也说明 stat-arb 方向若要重开，后续需要新的 pair universe / 新数据源 / 更强 spec，而不是继续在现有三组 pairs 上小修小补。
3. `Live Seat` 长时间保持暂空仍是正确的，但这也要求 bot2 持续守纪律：不要为了桌上“看起来热闹”而反复重开已 park 线。

## 本轮一句话结论（给 Jerry）

**这轮真正的新变化不是谁升格，而是谁被更诚实地压回去：`Rank 4b` 在补完唯一允许的一刀 `time stability` 后回到 `park`。因此当前 desk 再次收缩为——`EMA` 继续 running paper 且 waiting_not_due，`Live Seat` 继续暂空，而 `Rank 2 combo_all` 是唯一仍保留前推资格、并且应该被按 `narrow paper pilot` 去接线的 Scout 候选。**
