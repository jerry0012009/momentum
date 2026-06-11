# 2026-03-17 01:39 UTC｜Scout Seat：Rank 16 ORB threshold + protective closing session gate intake

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- `Run 1 / Paper Seat`：`EMA` 的 crypto due-now 窗口已在 `00:20 UTC` 被实际消化，当前是 `waiting_not_due`；
- `Run 2 / Scout Seat`：当前默认主资源位；
- `Run 3 / tiny-live plumbing`：只有 `Scout Seat` 也没有合格动作时才回退。

本轮先比较 active Scout 候选的边际价值：

1. `Rank 2 combo_all`
   - 已是 `narrow paper pilot approved`；
   - 当前没有新的真实 `append/review` need，再补 wiring 只会继续磨近义卡。
2. `Rank 7~15`
   - 都已完成 `clean replication + Light Stability Pack` 并压回 `park / evidence pool`；
   - 当前没有 bot2 重开指令，不应继续吃默认主资源。
3. shortlist 里的剩余 fresh 候选里，`Rank 5 / Rank 6`
   - 一个更偏 prediction-market execution、一个更偏跨资产 proxy spread；
   - 都不如当前 `paper-based / 15m crypto / 可直接复用现有 cache` 的 fast lane 贴题。
4. `ORB threshold + protective closing session gate`（Wu et al. 2021；Syu et al. 2020）
   - 虽仍属 breakout 家族，但当前不是回到旧 breakout 主线，而是把它当作 **session threshold + confirmation + protective exit** 的新 fast intake；
   - 不需要新数据源，可直接复用现有 `Binance 120d 15m` cache；
   - 能最快把一个 fresh 候选压到 **implementation-ready clean-room spec**，为下一轮直接进入 clean replication 做准备。

因此本轮主点定为：**把 ORB 的 `threshold / confirmation / protective closing` 三层压成新的 Rank 16 clean-room spec，并回写当前 desk board。**

## 本轮主点（1 个）
- 新增脚本：`scripts/build_orb_protective_closing_scout_spec.py`
- 产出新的 paper-based 15m crypto intake：
  - `candidate_id = scout_orb_protective_closing_15m_v1`
  - `BTC / ETH / SOL | Binance 120d | 15m`
  - `00:00 / 08:00 / 13:30 UTC` 三个 pseudo opens
  - 前 `2~3` 根 15m bar 形成 opening range
  - 五档最小对照：
    - `raw_orb`
    - `confirm1_outside`
    - `confirm2of3_outside`
    - `retest_hold`
    - `protective_close_overlay`
  - 执行口径固定：
    - `next-bar open`
    - `1 ATR stop`
    - `+1R break-even lift`
    - `8-bar time stop`
    - `6/10/15/20 bps per side`

## 紧邻子点（1 个）
- 将 `Rank 16` 的状态最小回写到：
  - `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
- 明确它当前状态是：`source intake / clean replication next`
- 并把 `Next 3 bot3 runs` 更新为：`Rank 16 clean replication first`

## 产物 / deployable artifact
### 新脚本
- `scripts/build_orb_protective_closing_scout_spec.py`

### 新 artifacts
- `reports/artifacts/scout_orb_protective_closing_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_orb_protective_closing_15m/spec_meta.csv`

### 网页可见落点
- `reports/site/factors/scout_orb_protective_closing_15m/report.html`
- `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 首页发布后将出现在：`https://jp.jerrypsy.top/momentum/`

## 最小验证
已执行：

1. `python3 /root/clawd/jerry/momentum/scripts/build_orb_protective_closing_scout_spec.py`
2. `python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_orb_protective_closing_scout_spec.py`
3. 复核输出：
   - `reports/artifacts/scout_orb_protective_closing_15m/clean_room_spec_v1.csv`
   - `reports/artifacts/scout_orb_protective_closing_15m/spec_meta.csv`
   - `reports/site/factors/scout_orb_protective_closing_15m/report.html`
4. 写回并复核：
   - `docs/TODO.md`
   - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`

执行结果：
- 脚本成功输出：`[ok] orb protective-closing scout spec generated`
- `py_compile` 通过

## 硬结论（hard verdict）
- **`Rank 16 ORB threshold + protective closing session gate` 当前最诚实的 desk 读法是：`source intake / clean replication next`。**
- 当前还不能把它写成 `paper candidate`，因为它只完成了 clean-room spec，没有完成 clean replication。
- 但和继续打磨已 `park` 的旧候选相比，这条线现在更适合拿下一轮 `Scout Seat` 主资源，去回答一个更尖锐的问题：
  - `pseudo-session opening range` 在 15m crypto 上是否有最小事件价值？
  - `threshold / confirm1 / confirm2of3 / retest_hold / protective close` 中，哪一层真的能减少假突破并改善成本后收益？
- 一句话说：**这轮不是重开 breakout 叙事，而是把 ORB 收窄成一个可被快速证伪/证实的 session-threshold 候选。**

## 风险 / 边界
1. 论文原场景是股票 ORB，不是 crypto 24/7；当前迁移的是 `threshold + confirmation + protective closing` 设计原则，不是原始市场假设；
2. 当前 pseudo open（`00:00 / 08:00 / 13:30 UTC`）只是 clean-room 起点，是否有效必须等 clean replication；
3. 当前明确只做 `long-or-flat`，不把 breakout short 带回默认主舞台；
4. 若下一轮 clean replication 显示它只是靠 `no_trade_ratio` 飙升或 protective close 过度收紧才显得更稳，默认应直接 `park`。

## Git / 提交
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件与未跟踪文件（包括历史 artifacts / site / memory 等），不适合安全 selective commit。

## 下一轮建议
- 若 `EMA` 仍是 `waiting_not_due`：`Run 2` 默认优先认领 `Rank 16` 的最小 clean replication。
- 第一刀重点先看：
  - `post_cost_return`
  - `false_break_ratio`
  - `max_drawdown`
  - `positive_asset_ratio`
  - `trades_per_asset`
  - `no_trade_ratio`
  - `cost_survival`
- 若 ORB clean replication 后仍只是典型 breakout 假改善（收益不增、交易数塌、靠 protective close 挤出表面稳定），默认直接 `park / evidence pool`。
