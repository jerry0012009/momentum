# 2026-03-23 08:31 UTC · Rank 140 surviving pocket freeze（最短 decisive 收口）

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 顶板判定：`Paper / 待开启自动运行 = empty`，且未见新的 interrupt，因此继续执行 `Next 3 bot3 runs / Run 1 = Rank 140 的最短 decisive 验证`

## 0. 本轮主点与紧邻子点
### 主点
- 在上一轮 `Rank 140 balance shortlist` 基础上，再做 **最短一刀**：
  - `Rank 137` 当前 surviving 的两条 pocket（`confirm_window_12` / `confirm12_entry24`）里，谁应该被 desk 冻结成唯一主 pocket？

### 紧邻子点
- 同步更新 `reports/site/factors/pbo_cscv_honesty_gate/report.html`，避免 reader-facing 页面继续把两条 pocket 并列成同等 surviving 读法。

## 1. 为什么这刀值得做
前两轮已经把 `Rank 140` 收紧到：
- shared honesty gate 没成立；
- 真实 surviving family 只剩 `Rank 137`；
- 但 `Rank 137` 仍保留两条 pocket，容易在后续 routing / 邮件 / 网页里被误读成“还有双主 pocket 可继续拉扯”。

因此，本轮最有杠杆的一步不是再开新 family，而是把 `Rank 137` 自己内部也收口成 **一个主 pocket + 一个次级 pocket**。

## 2. 新增产物
### artifacts
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_rank137_surviving_pocket_scorecard_20260323.csv`
- `reports/artifacts/pbo_cscv_honesty_gate/rank140_rank137_surviving_pocket_scorecard_20260323.json`

### reader-facing 页面更新
- `reports/site/factors/pbo_cscv_honesty_gate/report.html`

## 3. 核心结果
数据源：
- `rank140_balance_shortlist_20260323.csv`
- `rank137_confirm_window12_entry24_asset_breakdown.json`

### 3.1 `confirm_window12_only` = 当前唯一应冻结的主 surviving pocket
- `trades = 88`
- `mean_net_bps_6bps_side = +100.6235`
- `win_rate = 72.73%`
- `sharpe_like_6bps_side = 5.9631`
- `positive_asset_count = 3/3`
- weakest asset 仍是 `BTC-USD = +83.5383 bps`

读法：
- 不只是 overall 最强；
- 也是 **BTC / ETH / SOL 三资产全部为正**；
- 因此这条 pocket 才配得上当前 `Rank 140` 里唯一主 surviving pocket 的位置。

### 3.2 `confirm12_entry24_only` = 次级 pocket，不再并列主位
- `trades = 47`
- `mean_net_bps_6bps_side = +37.5898`
- `win_rate = 59.57%`
- `sharpe_like_6bps_side = 2.4614`
- `positive_asset_count = 2/3`
- weakest asset = `BTC-USD = -2.8518 bps`

读法：
- 整体仍然为正，所以不需要直接 park；
- 但它 **不是 cross-asset clean pocket**，因为 BTC 侧已经转负；
- 更诚实的 desk 口径应是：它只是 **ETH/SOL 特异次级 pocket**，不再与 `confirm_window_12` 并列主 surviving pocket。

## 4. 人话结论
这轮最有杠杆的小步，是把 `Rank 140` 的 surviving 读法再收紧一句：

> **shared honesty gate 仍未成立；如果必须保留一个最短、最硬、最不容易误判的 surviving pocket，只剩 `Rank 137 / confirm_window_12`。**

`confirm12_entry24` 现在仍可留作次级 pocket 证据，但不该再被读成与 `confirm_window_12` 同级。

## 5. lightweight scorecard
- `usefulness = medium`
- `time_stability = weak`
- `cross_asset_stability = medium`
- `cost_trade_stability = weak`
- `deployability = low`
- `recommended_action = keep_P1`
- `main_weakness = 正例仍来自 family-specific pocket；shared honesty layer 仍未成立`

## 6. desk verdict
- 对 `Rank 140`：维持 `keep_P1 / active compare anchor / not default primary`
- 对 `Rank 137 / confirm_window_12`：冻结为当前唯一主 surviving pocket
- 对 `Rank 137 / confirm12_entry24`：降为次级 pocket（ETH/SOL 特异、非 cross-asset clean）

## 7. 本轮交付
- 日志：`research/optimization_loop/2026-03-23_0831_rank140-surviving-pocket-freeze.md`
- artifacts：
  - `reports/artifacts/pbo_cscv_honesty_gate/rank140_rank137_surviving_pocket_scorecard_20260323.csv`
  - `reports/artifacts/pbo_cscv_honesty_gate/rank140_rank137_surviving_pocket_scorecard_20260323.json`
- 页面：`reports/site/factors/pbo_cscv_honesty_gate/report.html`
