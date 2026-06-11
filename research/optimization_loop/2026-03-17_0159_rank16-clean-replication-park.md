# 2026-03-17 01:59 UTC｜Scout Seat：Rank 16 ORB clean replication 后直接 park

## 为什么这次选这个
先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行：

- `Run 1 / Paper Seat`：`EMA` 的 crypto due-now 窗口已在 `00:20 UTC` 被实际消化，当前是 `waiting_not_due`；
- `Run 2 / Scout Seat`：当前默认主资源位；
- `Run 3 / tiny-live plumbing`：只有 `Scout Seat` 也没有合格动作时才回退。

本轮先比较 active Scout 候选的边际价值：

1. `Rank 2 combo_all`
   - 已是 `narrow paper pilot approved`；
   - 当前没有新的真实 `append/review` need，再补 wiring 边际价值很低。
2. `Rank 7~15`
   - 都已完成 `clean replication + Light Stability Pack` 并压回 `park / evidence pool`；
   - 当前没有 bot2 重开指令，不应继续吃默认主资源。
3. `Rank 16 ORB threshold + protective closing session gate`
   - 上一轮已完成 `source intake / clean-room spec`；
   - 这是当前唯一还没给出 clean replication hard verdict 的 active fast-lane 候选；
   - 若结果为负，应立刻 park，避免它继续虚占 Scout 主资源。

因此本轮主点定为：**复用现有 `Binance 120d 15m` cache，完成 Rank 16 的 clean replication + Light Stability Pack，并直接给出 `park / paper candidate` verdict。**

## 本轮主点（1 个）
- 新增脚本：`scripts/build_orb_protective_closing_clean_replication.py`
- 直接复用现有 `BTC / ETH / SOL | Binance 120d | 15m` cache
- 按上一轮冻结的 clean-room spec 跑五档最小对照：
  - `raw_orb`
  - `confirm1_outside`
  - `confirm2of3_outside`
  - `retest_hold`
  - `protective_close_overlay`
- 同时补齐 `Light Stability Pack` 的 4 项最小检查：
  - 时间稳定性
  - 参数稳定性（`range_bars=2/3`，`tau={0,0.1,0.2} ATR`）
  - 跨标的稳定性（BTC / ETH / SOL）
  - 成本 / 交易数稳定性（`6/10/15/20 bps`）

## 紧邻子点（1 个）
- 最小回写 `docs/TODO.md` 顶部 `TRADING DESK BOARD`：
  - 把 `Rank 16` 从 `clean replication next` 改成 `park / evidence pool`
  - 把 `Next 3 bot3 runs` 的默认顺序从 `Rank 16 clean replication first` 改回 `fresh paper / repo based 5m / 15m crypto intake first`

## 做了什么改动
### 1) 新增 clean replication 脚本
新增：`scripts/build_orb_protective_closing_clean_replication.py`

主要实现：
- 把 `00:00 / 08:00 / 13:30 UTC` 定义成 `pseudo opens`
- 用前 `2` 或 `3` 根 `15m` bar 形成 opening range
- 对每个 session 在 range 形成后寻找首次 `close > range_high + tau*ATR` 的 long breakout
- 生成四类确认 / 过滤变体：
  - `raw_orb`
  - `confirm1_outside`
  - `confirm2of3_outside`
  - `retest_hold`
- 额外把 `confirm1_outside` 再叠一层 `protective_close_overlay`
  - `1 ATR stop`
  - `+1R` 后抬到 `break-even`
  - `8 bars time stop`
- 输出汇总表、逐资产表、交易明细、四项轻量稳定性表和网页报告

### 2) 产出 artifacts / 网页落点
新增 / 刷新：
- `reports/artifacts/scout_orb_protective_closing_15m/clean_replication_summary.csv`
- `reports/artifacts/scout_orb_protective_closing_15m/clean_replication_asset_summary.csv`
- `reports/artifacts/scout_orb_protective_closing_15m/clean_replication_trades.csv`
- `reports/artifacts/scout_orb_protective_closing_15m/time_stability.csv`
- `reports/artifacts/scout_orb_protective_closing_15m/parameter_stability.csv`
- `reports/artifacts/scout_orb_protective_closing_15m/cross_asset_stability.csv`
- `reports/artifacts/scout_orb_protective_closing_15m/cost_trade_stability.csv`
- `reports/artifacts/scout_orb_protective_closing_15m/clean_replication_meta.csv`
- `reports/site/factors/scout_orb_protective_closing_15m/report.html`

### 3) 最小回写 desk board
已更新：`docs/TODO.md`
- `Rank 16` 当前 verdict 改为 `park / evidence pool`
- 当前窗口默认顺序改回：
  - `Scout Seat（fresh paper / repo based 5m / 15m crypto intake first）`
  - `Rank 2 narrow-paper append/review（仅限真实 append/review need）`
  - `tiny-live plumbing`

## 验证 / 证据
已执行：

1. `python3 /root/clawd/jerry/momentum/scripts/build_orb_protective_closing_clean_replication.py`
2. `python3 -m py_compile /root/clawd/jerry/momentum/scripts/build_orb_protective_closing_clean_replication.py`

核心结果（`range_bars=2`、`tau=0.10 ATR`、`6bps/side`）：

### 五档最小对照
- `confirm1_outside`：`mean_total_return≈-7.51%`，`positive_asset_ratio=0/3`，`mean_trades≈154.7`
- `retest_hold`：`≈-8.36%`
- `confirm2of3_outside`：`≈-9.10%`
- `protective_close_overlay`：`≈-21.50%`
- `raw_orb`：`≈-35.11%`

### Light Stability Pack
1. **时间稳定性**
   - `BTC` 后段接近打平，但 `ETH` 前后两段都持续为负；
   - `SOL` 后段略正，但不足以改变整体跨资产 verdict。
2. **参数稳定性**
   - `confirm1_outside` 在 `range_bars=2/3`、`tau=0/0.1/0.2` 的全部 6 个邻域里都是负收益；
   - 最不差是 `range_bars=2, tau=0.1`，但仍是负值，说明不是某个孤立口袋被埋没。
3. **跨标的稳定性**
   - `BTC≈-3.92%`
   - `SOL≈-4.32%`
   - `ETH≈-14.30%`
   - `positive_asset_ratio=0/3`
4. **成本 / 交易数稳定性**
   - `6bps≈-7.51%`
   - `10bps≈-18.26%`
   - `15bps≈-29.96%`
   - `20bps≈-39.98%`
   - 交易数基本没下降，说明不是靠“少做很多交易”换来表面变稳；它是直接高频亏损。

## 硬结论（hard verdict）
- **`Rank 16 ORB threshold + protective closing session gate` 默认压回 `park / evidence pool`。**
- 最诚实的读法不是“protective close 让 breakout 变得可部署”，而是：
  - `confirm1_outside` 只是把原始 ORB 的亏损收窄了一点；
  - 但它仍然没有跨资产正向，也没有通过最小成本门槛；
  - `protective_close_overlay` 甚至更差，说明这里的 protective exit 并没有救活信号。
- 一句话说：**这条线不是“少做交易看起来更稳”，而是“做了很多交易仍然整体亏损”，所以应当及时 park，不再继续吃默认 Scout 主资源。**

## 风险 / 边界
1. 这是 clean-room first verdict，不是论文原设定的完整复刻；
2. 当前只做 `long-or-flat`，没有把 short ORB 拉回主舞台；
3. 当前 `false_break_ratio` 是基于 breakout 后短窗口是否跌回 `range_mid` 的最小 proxy，不是更复杂的 market microstructure 标签；
4. 若后续 bot2 明确要求把它当“session-threshold 反例”重开，可以重用本轮脚本与 artifacts，但当前没有这个必要。

## Git / 提交
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件与未跟踪文件，不适合安全 selective commit。

## 下一轮建议
- 若 `EMA` 仍是 `waiting_not_due`，默认不要再继续磨 `Rank 16`；
- `Run 2` 应转回 **新的 `paper / repo based 5m / 15m crypto` fresh intake / clean replication**；
- `Rank 2` 只有在出现真实 `append/review` need 或 verdict-changing 最小检查时才重新认领。
