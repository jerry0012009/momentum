# 2026-03-23 01:40 UTC · Rank 140 / Rank 137 breakout_short-only cut

## 本轮按顶板顺序执行

### Run 1 · TRADING DESK BOARD / interrupt check
- `docs/TODO.md` 顶板显示 `Paper / 待开启自动运行 = empty`
- 未见顶板定义的真实 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch`
- 因此本轮继续执行默认队列里的 `Scout / Rank 140`

### Run 2 · 当前主点
承接 `00:39 UTC` overlap cut、`01:05 UTC` shared pocket cut、`01:18 UTC` exclusive pocket shape：
- 本轮只做 `Rank 140 / Rank 137` **最后一刀便宜 decisive cut**
- 目标是把 `confirm_window12_only` 里真正的主体再剥一层：
  - **只保留 `breakout_short`**
  - 检查去掉零碎 `EMA/PSAR long` / `fib_retest_long` 后，正 pocket 是否仍保持 guard-passed 级别

### Run 3 · 唯一紧邻子点
- 只补最小诊断产物与 scorecard
- 不并开第二个 family
- 不回头继续磨 `Rank 14b`
- 不碰已自动运行的 paper runner

---

## 本轮产物
目录：`reports/artifacts/pbo_cscv_honesty_gate/rank137_confirm_window12_breakout_short_only/`

- `asset_summary.csv`
- `asset_hour_summary.csv`
- `asset_dow_summary.csv`
- `confirm_window12_setup_mix.csv`
- `summary.json`

输入口径：
- `reports/artifacts/pbo_cscv_honesty_gate/rank137_confirm_window12_entry24_overlap_matrix.csv`
- 只取：`segment = confirm_window12_only` 且 `setup = breakout_short`
- 统一计算：`net_6bps = gross_return - 12bps roundtrip`

---

## 核心结果

### 1) 去掉零碎 setup 后，`breakout_short` 主体仍为正
`confirm_window12_only / breakout_short only`：
- `trades = 73`
- `mean_net_6bps = +87.75 bps`
- `win_rate = 67.12%`

对照上一轮整块 `confirm_window12_only`：
- 整块：`88` 笔，`+100.62 bps`
- 本轮只留 `breakout_short`：`73` 笔，`+87.75 bps`

读法：
- 把零碎 `EMA/PSAR long`、`fib_retest_long` 剥掉后，收益确实下降了一些；
- 但 **主体并没有塌掉**，仍保留明显正 pocket；
- 说明上一轮看到的正值，不只是被少量 `EMA/PSAR long` 小样本“伪装”出来。

### 2) 三资产仍全部为正，但 BTC 边际最弱
分资产：
- `ETH-USD`：`27` 笔，`+96.08 bps`，`win_rate = 70.37%`
- `SOL-USD`：`33` 笔，`+86.37 bps`，`win_rate = 69.70%`
- `BTC-USD`：`13` 笔，`+73.99 bps`，`win_rate = 53.85%`

读法：
- 这刀之后，`breakout_short` 不再依赖单一资产；
- `ETH / SOL` 更像 pocket 主力；
- `BTC` 虽仍为正，但胜率已经明显更薄，离“稳定主力腿”还有距离。

### 3) 但它仍不是可直接部署的 shared honesty rule
虽然本轮把正 pocket 收窄到了更清楚的 `breakout_short` 主体，但仍有几个问题没被消掉：
- 这块 pocket 仍是 `confirm_window12_only` 的 **exclusive** 区，而不是 shared core；
- 它没有回答更长期时间稳定性 / 成本稳定性；
- `BTC` 已经明显比 `ETH/SOL` 薄；
- 这更像 **family 内一块可解释的正 pocket**，不是整个 `Rank 140` 可以直接升格的 deployable rule。

---

## 轻量 scorecard
- `usefulness = medium_to_high`
- `time_stability = weak`
- `cross_asset_stability = medium`
- `cost_trade_stability = weak`
- `deployability = low_to_medium`

### hard-fail flags
- `still_exclusive_pocket_not_shared_core`
- `btc_leg_is_thinner_than_eth_sol`
- `time_stability_not_proven`
- `cost_trade_stability_not_proven`

### recommended_action
- **`keep_P1`**

### why_now
顶板明确要求这轮只做 `Rank 140` 最后一刀便宜 decisive cut：把 `confirm_window12_only` 里的 `breakout_short` 主体单独剥出来。本轮结果回答了这个问题：**剥掉零碎 setup 后，主体仍是正 pocket，但仍不足以把 Rank 140 从 honesty-layer 证据板推到可部署层级。**

### main_weakness
当前最强证据已经收敛到 `confirm_window12_only / breakout_short` 这块 pocket，但它依然是 `exclusive pocket selection` 的胜利，不是一个干净、共享、可直接上桌的 strict honesty rule。

---

## Desk 结论更新
对 `Rank 140 / Rank 137` 当前最诚实的压缩读法：

1. `Rank 137` 仍是 `Rank 140` 当前最像样的正例 family；
2. `shared` core 为负，这点不变；
3. `confirm_window12_only` 的正值主体，确实主要来自 **`breakout_short` across BTC/ETH/SOL**；
4. 把零碎 `EMA/PSAR long` / `fib_retest_long` 拿掉后，这块主体仍保留 guard-passed 级别的正 pocket；
5. 但它仍属于 `exclusive pocket`，而非 deployable shared rule；因此本轮结论仍是 **`keep_P1`**，且这刀已经用完，下一轮应把主资源切回 `fresh intake reserve / next active Scout`。

## 本轮交付
- 日志：`research/optimization_loop/2026-03-23_0140_rank140-rank137-breakout-short-only-cut.md`
- 诊断产物：`reports/artifacts/pbo_cscv_honesty_gate/rank137_confirm_window12_breakout_short_only/`

## 对下一轮的最短提醒
- `Rank 140`：本轮 cheap decisive cut 已完成，默认不再继续占主资源位；保留为 `active compare anchor / evidence strengthened`。
- 下一轮应优先比较：`Rank 125 / Rank 112 / Rank 111` 与 `fresh intake reserve` 的当前边际价值，而不是继续给 `Rank 140` 或 `Rank 14b` 近义续磨。
