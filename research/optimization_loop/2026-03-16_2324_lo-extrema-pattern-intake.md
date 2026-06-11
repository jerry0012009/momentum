# 2026-03-16 23:24 UTC — Lo-style causal extrema pattern gate intake

## 为什么这轮选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 检查：`Paper Seat = EMA` 当前仍是 `waiting_not_due / due_soon`，所以本轮不能在 `Run 1` waiting-window 空转。
- 再比较 active Scout 候选的边际价值：
  - `Rank 2 combo_all` 已进入 `narrow paper pilot approved`，当前没有真实 `append/review` need，继续补 wiring 边际价值低；
  - `Rank 7 / 8 / 9 / 10` 已完成 `clean replication + Light Stability Pack` 并压回 `park / evidence pool`；
  - `Rank 5/6` 虽仍在 shortlist，但一个偏 prediction market、一个偏 BTC-美股 proxy，不如新的 **repo-based 15m crypto** intake 贴近当前 fast lane。
- 因此当前更诚实的主资源动作，不是继续打磨旧候选，也不是凭空开新框架，而是给一个**更贴近 desk 的 paper/repo based 15m crypto 新入口**做 `source intake -> clean-room spec`。

## 本轮主点
- 主点：新增 `Rank 11 Lo-style causal extrema pattern gate`，把第三方 repo 里的 `smoothing -> extrema -> pattern rule` 流程压成 `15m crypto` clean-room spec。
- 紧邻子点：把 `TODO` 顶部战板与 Scout shortlist 最小写回，让下一轮默认能直接认领 `clean replication next`。

## 做了什么
### 1) 新增 clean-room spec 生成脚本
新增：
- `scripts/build_lo_extrema_pattern_scout_spec.py`

它把 Lo / 第三方复现 repo 里最有价值的工程分层，收窄成当前 desk 可因果执行的最小 spec：
- `candidate_id = scout_lo_extrema_pattern_15m_v1`
- 样本固定：`BTC / ETH / SOL | Binance 120d | 15m`
- `causal_smoothing = one-sided EMA9(hlc3)`
- `confirmed_extrema = extrema 确认延迟固定 2 bars`
- `zone_construction = 最近 2~3 个 confirmed extrema 在 0.35 ATR 内时聚合为 zone`
- 第一轮实验矩阵固定为：
  - `swing_break_only`
  - `double_bottom_reclaim`
  - `pullback_recovery_gate`
  - `pattern_vote_guard`
- 执行口径继续与当前 Scout 快筛保持一致：
  - `next-bar open`
  - `1 ATR stop`
  - `2 ATR target`
  - `8-bar time stop`
  - `6 bps/side`

### 2) 生成 reader-facing artifact
落地产物：
- `reports/artifacts/scout_lo_extrema_pattern_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_lo_extrema_pattern_15m/spec_meta.csv`
- `reports/site/factors/scout_lo_extrema_pattern_15m/report.html`

reader-facing 页明确写死两点：
1. 这页是 **clean replication 输入页**，不是成绩宣判页；
2. 当前 hard verdict 只是：**已通过 source intake、足够进入 clean replication；但在补完 clean replication 之前，不能误写成 `paper candidate`。**

### 3) 同步 desk board / shortlist
最小更新：
- `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
  - 新增 `Rank 11 Lo-style causal extrema pattern gate` 行；
- `docs/TODO.md`
  - 在 `Scout Seat` 候选阶段表中新增 `Rank 11`，状态写成 `source intake / clean replication next`；
  - 把 `Next 3 bot3 runs` 的当前窗口排班更新为：`Rank 11 clean replication next；Rank 2 only on real append/review need`；
  - 在 `Run 2` 具体顺序里补上 `2e`，明确下一轮应优先补 `Rank 11` 的最小 clean replication，而不是继续补 intake 文案。

## 最小验证
已执行并通过：
1. `python3 scripts/build_lo_extrema_pattern_scout_spec.py`
2. `bash scripts/publish_homepage_index.sh`

验证结果：
- 新 artifact 已生成；
- 新 reader-facing 页已落到：
  - `reports/site/factors/scout_lo_extrema_pattern_15m/report.html`
- 首页索引已刷新并发布：
  - `https://jp.jerrypsy.top/momentum/`

## 硬结论（hard verdict）
- **`Rank 11 Lo-style causal extrema pattern gate` 当前应读作：`source intake / clean replication next`。**
- 它当前的边际价值高于继续磨 `Rank 2` 或重看 `Rank 7/8/9/10`，因为它同时满足：
  1. `repo-based / paper-based`；
  2. `15m crypto` 直接可落；
  3. 不需要新数据源；
  4. 规则可以写成清楚的 `trade on / trade off`；
  5. 已经提前把 lookahead / repaint 风险写进 clean-room guardrail。
- 但在补完最小 clean replication 前，**它还不是 `paper candidate`，更不是 `Live Seat` 候选。**

## 对 desk 主线的意义
- 这轮减少的是 `Scout Seat` 的 fresh intake 断层：
  - 避免 `EMA waiting_not_due` 时，bot3 只能在 `Rank 2` wiring 与一串已 park 候选之间打转；
  - 给当前 board 明确要求的 `paper / repo based 5m / 15m crypto` fast lane 补上一条新的实现入口；
  - 而且这条线默认是 **long/structure gate**，不需要重新把 bench 的 breakout short 拉回主舞台。

## 风险 / 边界
- 本轮没有产出新的收益数字，也没有完成 clean replication；
- 它没有改变现有 seat verdict：
  - `Paper Seat = EMA` 不变；
  - `Live Seat = 暂空` 不变；
  - `Rank 2 combo_all` 仍是 `narrow paper pilot approved`；
- 这轮唯一新增的是：**新的 Scout 候选已从 repo idea 推进到 implementation-ready spec。**

## 下一步建议
- 下一轮 `Run 2` 默认优先按这张 spec 做最小 clean replication；
- 第一刀重点先看：
  - `post_cost_return`
  - `positive_asset_ratio`
  - `trades_per_asset`
  - `no_trade_ratio`
  - `false_break_proxy`
  - `cost_survival`
- 若最优版本只是靠 `no_trade_ratio` 飙升才守住收益，或 extrema/zone 逻辑需要大量主观补丁，直接 `park`，不要继续把它漂成“结构研究态”。

## 网页可见落点
- `reports/site/factors/scout_lo_extrema_pattern_15m/report.html`
- `docs/TODO.md`（及其站点镜像 / Control Tower）
- `https://jp.jerrypsy.top/momentum/`

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
