# 2026-03-23 06:37 UTC · Rank 140 / Rank 137 overlap pocket asset breakdown

## 本轮执行顺序（按顶板）

### 1) 先读 `TRADING DESK BOARD`
- `Paper / 待开启自动运行 = empty`
- 未见新的 fresh guard-pass Scout 写入顶板
- 因此本轮按 authoritative 默认队列，落到 **Run 2 = `Rank 140` 所需的最短 decisive compare**

### 2) interrupt check
本轮先按顶板规则排除 interrupt：
- `Paper / 正在自动运行` 未见被明确写成 `stale / error / refresh 失步 / ledger 爆雷 / open-position 异常 / red-watch` 的真实事件
- 未见 tiny-live / live-shadow plumbing 的 blocking anomaly 被顶板提升为本轮抢占项

结论：**无 interrupt，继续默认队列。**

---

## 本轮主点
主点仍是：**`Rank 140 / pbo-cscv deflated sharpe honesty gate`**  
紧邻子点只取一个：**`Rank 137` 上一轮 overlap cut 的按资产拆分**。

原因：
- `Rank 140` 现在是 `active compare anchor`，不是 default primary；
- 03:39 UTC 的 overlap cut 已证明：`confirm_window_12` 与 `confirm12_entry24` 的优势主要来自各自独有 pocket，而不是 shared 区；
- 本轮最便宜且最可能改变读法的一刀，不是再开新 family，而是回答：
  > 这个 shared pocket 的坏表现，到底是单一资产拖累，还是跨资产都坏？

这会直接影响 desk 对 `Rank 140` 的人话结论：
- 如果只是单一资产拖累，那更像可修剪 pocket；
- 如果三资产都坏，那就更像 **family-specific exclusive pocket 才有价值**，shared honesty rule 仍不可 deploy。

---

## 产物
- `reports/artifacts/pbo_cscv_honesty_gate/rank137_confirm_window12_entry24_asset_breakdown.json`

数据源沿用上一轮 overlap 矩阵：
- `reports/artifacts/pbo_cscv_honesty_gate/rank137_confirm_window12_entry24_overlap_matrix.csv`

成本口径：
- `6bps/side`，即 round-trip 扣 `12bps`

---

## 核心结果

### 1) shared pocket 不是单一资产事故，而是三资产全负
`shared` 段：
- `BTC-USD`: `176` 笔，`mean_net = -14.72 bps`，`win_rate = 36.36%`
- `ETH-USD`: `150` 笔，`mean_net = -11.18 bps`，`win_rate = 44.00%`
- `SOL-USD`: `177` 笔，`mean_net = -29.77 bps`，`win_rate = 32.77%`
- 合计：`503` 笔，`mean_net = -18.96 bps`

读法：
- shared 区并不是“BTC/ETH 还行，只被 SOL 拖死”；
- 更诚实的结论是：**三资产都过不了成本，SOL 只是最差，不是唯一问题源。**

### 2) `confirm_window12_only` 是跨资产都成立的正 pocket
- `BTC-USD`: `20` 笔，`+83.54 bps`
- `ETH-USD`: `28` 笔，`+94.23 bps`
- `SOL-USD`: `40` 笔，`+113.64 bps`
- 合计：`88` 笔，`+100.62 bps`

读法：
- 这不是某个单币偶然冲高；
- `confirm_window_12` 独有 pocket 在三资产上都为正，且 SOL 反而最好。

### 3) `confirm12_entry24_only` 仍是 pocket，但更像 ETH/SOL 特异 pocket
- `BTC-USD`: `13` 笔，`-2.85 bps`
- `ETH-USD`: `15` 笔，`+65.09 bps`
- `SOL-USD`: `19` 笔，`+43.55 bps`
- 合计：`47` 笔，`+37.59 bps`

读法：
- 这条独有 pocket 仍有正值，但稳定度弱于 `confirm_window12_only`；
- 它更像 ETH/SOL pocket，**BTC 侧没有提供正贡献**。

---

## 对 Rank 140 / Rank 137 的最小更新读法

现在可以把上一轮 overlap 结论再收紧一步：

1. `Rank 137` 的 shared 区是**跨资产一起坏**，不是单币噪声。
2. 目前真正值得保留的，不是 shared honesty rule，而是 **exclusive pockets**。
3. 其中：
   - **`confirm_window12_only`** = 当前更强、且跨资产都为正的 pocket；
   - **`confirm12_entry24_only`** = 次级 pocket，更偏 ETH/SOL，BTC 不成立。

因此，`Rank 140` 现在最诚实的 desk 读法应是：
> 它留下了一条 family-level 的 pocket 发现器，但还没有留下一个可共享、可跨资产 deploy 的 honesty gate。

---

## lightweight scorecard
- `usefulness = medium`
- `time_stability = weak`
- `cross_asset_stability = medium`
- `cost_trade_stability = weak`
- `deployability = low`

### hard-fail flags
- `shared_pocket_negative_on_all_three_assets`
- `exclusive_pocket_drives_edge`
- `entry24_only_not_positive_on_btc`
- `shared_rule_not_deployable_as_general_honesty_gate`
- `family_specific_positive_pocket_only`

### recommended_action
- **`keep_P1`**

### why_now
因为这是一刀真正会改变读法的最小补充：它把“shared 区为什么差”从含糊状态变成了明确的跨资产否定，从而避免后续再把 `Rank 140` 误读成接近 deploy 的 shared gate。

### main_weakness
正收益来自 family-specific exclusive pockets，而不是可共享、可规模化复用的统一守门规则。

---

## 对顶板的影响
本轮**不需要**回写 `docs/TODO.md`：
- 没有层级变化；
- 没有新的 `P2 -> P3` 或 `Paper launch queue` 事件；
- 只是在 `Rank 140 = keep_P1 / active compare anchor / not default primary` 的既有口径上，把原因写得更硬。

若后续需要最小引用，可压缩成人话一句：
- `Rank 140 / Rank137` 的 shared 区三资产全负，当前可保留的只是 `confirm_window12_only` 这类 exclusive positive pocket，而不是 shared deployable gate。

## 交付
- 日志：`research/optimization_loop/2026-03-23_0637_rank140-rank137-asset-breakdown.md`
- artifact：`reports/artifacts/pbo_cscv_honesty_gate/rank137_confirm_window12_entry24_asset_breakdown.json`
