# 2026-03-23 03:14 UTC · Rank 140 是否继续留在 active compare

## 本轮按顶板顺序执行

### Run 1 · TRADING DESK BOARD / interrupt check
- 已先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- `Paper / 待开启自动运行 = empty`
- 未见顶板定义的真实 interrupt：
  - `EMA / PSAR raw alpha focus`：顶板仍归类为 autonomous runner，未见 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`
  - `Rank 2 / 17 / 29 / 32b` manual narrow paper：仍属 background autonomous tracking，未见 blocking anomaly 信号
  - `Rank 139 / Rank 122`：顶板未记录新的 blocking anomaly
- 因此本轮仍按默认 `Next 3`，只认领 **Run 1 / Rank 140 最小 verdict**

### Run 2 · 主点范围控制
本轮不再重跑新切片，只复核 `Rank 140` 最近三刀已经得到的 decisive evidence：
1. `01:05 UTC`：`shared` pocket 三资产全负，说明 shared core 不能当默认 kept core；
2. `01:18 UTC`：`confirm_window12_only` 三资产全正，但仍是 pocket，而非简单 shared rule；
3. `01:40 UTC`：把 pocket 继续剥到 `breakout_short` 主体后仍为正，但依旧只是 `exclusive pocket`，不是 deployable shared honesty rule。

### Run 3 · 唯一紧邻子点
- 本轮只补一个 desk-level 结论：
  - `Rank 140` 还应不应该继续留在 `active compare`？
- 不新开 `Rank 14b / 125 / 112 / 111` 的第二动作
- 不碰已自动运行 paper runner
- 不补近义 health-check

---

## 本轮结论

### 1) `Rank 140` 不该再占主资源位，这点已经足够确定
过去三刀已经把最有杠杆、最便宜、最能改 verdict 的问题都问完：
- **shared core 是否成立？** 不成立；三资产都负。
- **exclusive pocket 是否只是单资产噪声？** 不是；`BTC/ETH/SOL` 都有正 pocket。
- **再剥到更清楚的主体后会不会塌？** 没塌；`breakout_short` 主体仍正。

这三步已经回答了它最关键的 desk 问题：
- `Rank 140` **不是伪亮点**；
- 但它也**不是即将升格的 deployable honesty rule**。

所以继续把它放在固定主资源位，只会重复劳动。

### 2) 但现在也还不该把它直接踢出 active compare
虽然 `Rank 140` 不能 promote，但它仍有保留价值：
- 它已经证明自己不是“shared 全负所以整条线全废”；
- 它在 `Rank 137` family 内确实留下一块跨资产、成本后仍为正的 `exclusive pocket`；
- 这使它仍适合作为后续对照锚：
  - 新候选若连这种 `exclusive pocket but not deployable` 的证据强度都达不到，就更不该占主资源；
  - `Rank 14b / 125 / 112 / 111` 若要接棒，至少要拿出能与它相当或更干净的 cheapest decisive evidence。

换句话说：
- **不再做 primary** 是确定的；
- **保留 active compare anchor** 也仍是更诚实的 desk 口径。

### 3) 真正该退出的是“默认 Run 1 身份”，不是 active compare 身份
本轮问题其实分两层：
1. 是否继续当默认主资源位？
2. 是否继续留在 active compare？

答案分别是：
- **默认主资源位：否，应该退出**
- **active compare：是，暂时保留**

因此最小、稳定、不会误导下一轮的 verdict 不是 `park`，而是：
- `keep_P1 / active compare anchor / no longer default Run 1`

---

## 轻量 scorecard（desk formalization）
- `usefulness = medium`
- `time_stability = weak`
- `cross_asset_stability = medium`
- `cost_trade_stability = weak`
- `deployability = low`

### hard-fail flags
- `shared_core_is_negative`
- `positive_alpha_still_exclusive_not_shared`
- `time_stability_not_proven`
- `cost_trade_stability_not_proven`
- `no_cheaper_decisive_cut_left`

### recommended_action
- **`keep_P1`**

### why_now
顶板本轮明确要求先回答：`Rank 140` 还配不配继续留在 active compare，还是该正式退出主资源位。经过最近三刀，答案已经稳定：**退出主资源位，但不退出 active compare。**

### main_weakness
它最强证据仍属于 `exclusive pocket`，不是一个共享、稳定、可以 reader-facing 简单表达的 deployable honesty rule；而且最便宜的 decisive cuts 已基本用完。

---

## Desk writeback（供 TODO 顶板最小更新）
最短口径：
- `Rank 140 = keep_P1 / active compare anchor / not default primary`
- 下一轮默认应从 `Rank 14b / Rank 125 / Rank 112 / Rank 111` 中挑 1 个最有杠杆对照点，而不是继续回头磨 `Rank 140`

## 本轮交付
- 日志：`research/optimization_loop/2026-03-23_0314_rank140-active-compare-exit.md`

## 对下一轮的最短提醒
- `Run 2` 默认切到：`Rank 14b / Rank 125 / Rank 112 / Rank 111` 中最有机会把 `P1 -> park / keep_P1` 说清的一条
- 除非出现真实 interrupt，否则不要再把 `Rank 140` 写回固定 primary
