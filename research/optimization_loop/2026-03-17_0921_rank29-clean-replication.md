# 2026-03-17 09:21 UTC · Rank 29 trendline breakout navigator clean replication

## 本轮归属
- Desk lane：`Run 2 / Scout Fast Lane`
- 触发原因：`EMA` 当前仍是 `waiting_not_due`，`Run 1` 没有新的 due-now / overdue 动作；按 desk 规则转向 `Scout Seat`。
- active Scout 边际价值比较：
  - `Rank 17 / Rank 2`：当前没有新的真实 `append / review need`，继续补 wiring 的边际价值低。
  - `Rank 26 / Rank 27 / Rank 28`：当前默认预算已用完，维持 `park / evidence pool`。
  - `Rank 29`：上一轮刚完成 fresh intake，且 board 明确下一轮只允许做 **1 次最小 clean replication**；因此本轮主资源落到 `Rank 29`，不再同时打开别的候选。

## 本轮主点
- 对 `Rank 29 trendline breakout navigator / multi-swing causal breakout state machine` 完成 **1 次最小 clean replication**。
- 目标只回答三件事：
  1. trade count 够不够；
  2. 轻 friction 后 aggregate 还活不活；
  3. breakout 后是否经常很快被打回 active line（假突破）。
- 明确不做：
  - 不追最新 bar；
  - 不扩成完整 `Light Stability Pack`；
  - 不直接补 paper wiring；
  - 不把 rejection side 凭空包装成已验证 alpha。

## 冻结后的 clean-room 口径
- 样本：`BTC / ETH / SOL | Binance 120d | 15m` cache
- 模块：`src/momentum/signals/trendline_breakout_navigator.py`
- `trade on`：至少一档 timeframe 出现 `close-confirm breakout`，且 `|tbn_composite_trend|` 达到阈值；next-bar open 顺势入场，固定持有 `8` 根 15m bar。
- `trade off`：没有 breakout、只有 provisional line，或 composite state 不同向。
- 假突破定义：触发后 `4` 根内，收盘重新回到同一条 active line 的错误一侧。
- 变体：
  - `breakout_align_ge1`
  - `breakout_align_ge2`（主变体）

## 产物
1. 脚本：`scripts/build_rank29_trendline_breakout_clean_replication.py`
2. artifacts：`reports/artifacts/scout_rank29_trendline_breakout_navigator_15m/`
   - `overall_summary.csv`
   - `asset_summary.csv`
   - `trades.csv`
   - `wick_summary.csv`
   - `trial_meta.csv`
3. 网页：`reports/site/factors/scout_rank29_trendline_breakout_navigator_15m/report.html`
4. TODO 顶部 board：已把 `Rank 29` 从 `fresh intake only` 上调为 `P1 weak candidate / one cheap honesty check at most`

## 关键结果
### 1) 主变体 first verdict
- 主变体：`breakout_align_ge2`
- `6bps/side`：
  - `mean_total_return ≈ +75.23%`
  - `positive_asset_ratio = 3/3`
  - `mean_trades ≈ 160`
  - `mean_false_break_ratio ≈ 7.56%`
- 分资产：
  - `BTC ≈ +57.42%`（`171` trades，false-break `≈7.02%`）
  - `ETH ≈ +61.98%`（`150` trades，false-break `≈10.00%`）
  - `SOL ≈ +106.28%`（`159` trades，false-break `≈5.66%`）

### 2) friction 读法
- `10bps/side` aggregate 仍为正：`≈ +54.18%`
- `15bps/side` aggregate 仍为正：`≈ +31.40%`
- `20bps/side` aggregate 仍有 `2/3` 资产为正：
  - `BTC ≈ -2.53%`
  - `ETH ≈ +6.37%`
  - `SOL ≈ +32.09%`
- 这说明它不是“只在极轻摩擦下才刚好浮上来”的一碰就碎型口袋。

### 3) breakout vs rejection 读法
- 当前 clean-room 样本里，`wick-rejection` 事件极稀少：
  - `BTC = 1`
  - `ETH = 0`
  - `SOL = 2`
- 因此当前更诚实的读法是：**Rank 29 目前验证出来的是 breakout state machine，不是 breakout + rejection 双侧都已成立的完整 alpha。**
- 这轮不应该把 rejection side 过度包装，更不该据此直接升格成 paper candidate。

## 本轮 hard verdict
- **`P1 weak candidate / one cheap honesty check at most`**
- 原因：
  - 最小 clean replication 已给出足够强的 first verdict；
  - trade count 不是过薄样本；
  - 轻 friction 后仍能存活；
  - 假突破率不高；
  - 但当前还没做完整 `Light Stability Pack`，而且 rejection side 样本过薄，离 `paper candidate` 还差至少 1 个 genuinely verdict-changing 的便宜诚实检查。

## 对 desk board 的影响
- `Paper Seat / EMA` 继续按 `waiting_not_due` 处理。
- `Scout Seat` 默认不再立刻 fresh-intake 新候选；下一轮若继续认领，**优先给 `Rank 29` 那 1 次 cheap honesty check**。
- 便宜诚实检查优先顺序建议：
  1. `时间 pocket`（分早/中/晚段或 tercile）
  2. `hold-window`（例如 `4 / 8 / 12 bars`）
  3. `non-short-tf 依赖`（确认收益是否不是全绑死在短级别 breakout）
- 未做完这 1 次检查前，不直接补 `paper ledger / monitoring` 接线。

## 审计备注
- repo 工作区仍有大量与本轮无关的脏文件；本轮未做混提、未 commit。
- 本轮只新增最小必要脚本、artifact、reader-facing 网页和 log。
