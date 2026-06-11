# 2026-03-17 02:49 UTC — Rank 18 EMA neighborhood consensus intake

## 本轮定位
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 执行。
- `Paper Seat = EMA` 当前是 **`running paper pilot / waiting_not_due`**，没有 due-now refresh 可做，因此不能在 waiting-window 空转。
- 再比较当前 active Scout 候选的边际价值：
  - `Rank 17 pullback recovery confirmation` 已进入 `paper candidate pool`，但上一轮已经继续补到 `paper candidate wiring`；若没有 genuinely new honest evidence，这轮继续磨它会变成低边际近义卡。
  - `Rank 2 combo_all` 仍是 `narrow paper pilot approved`，当前也只允许在真实 append/review need 时再继续。
  - `Rank 7~16` 已完成 `clean replication + Light Stability Pack`，当前都在 `park / evidence pool`。
- 因此本轮最诚实的主资源动作，是按 `Run 2` 的 fresh paper/repo intake 路线，开一条新的 **paper-based 15m crypto Scout intake**。

## 开工前检查
### repo / dirty state
- `git status --short --branch` 显示工作区存在大量历史脏文件与站点产物；本轮不做混提，不碰与本轮无关的历史脏文件。
- 本轮只新增 / 更新与 `Rank 18` 直接相关的最小集合：
  - `scripts/build_ema_plateau_consensus_scout_spec.py`
  - `reports/artifacts/scout_ema_plateau_consensus_15m/clean_room_spec_v1.csv`
  - `reports/artifacts/scout_ema_plateau_consensus_15m/spec_meta.csv`
  - `reports/site/factors/scout_ema_plateau_consensus_15m/report.html`
  - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
  - `docs/TODO.md`
  - 本日志文件

### 当前席位状态
- `Paper Seat`：`EMA baseline family`，当前读法=`running paper pilot / waiting_not_due`
- `Live Seat`：继续暂空
- `Scout Seat`：本轮默认应从 fresh paper/repo intake 里找新的 `source intake / clean replication next`

## 本轮主点
**新增 `Rank 18 EMA neighborhood consensus / plateau-stable crossover`（Chiu et al. 2023）并把它压到 `source intake / clean replication next`。**

### 为什么这条线现在边际价值最高
一句话：**不是再赌单一“神奇 EMA 参数”，而是把论文里的“先看参数平台，再决定值不值得继续”翻成当前 desk 可执行的 15m crypto 小邻域 consensus 候选。**

相对其他可认领对象：
1. `Rank 17`
   - 当前最诚实状态仍是 `paper candidate only`；
   - 继续补它，除非能拿 genuinely verdict-changing evidence，否则只会继续堆 wiring。
2. `Rank 2`
   - 已进入 `narrow paper pilot approved`；
   - 这轮没有真实 append/review need。
3. `Rank 7~16`
   - 都已给出 `park / evidence pool`；
   - 继续重看只是 closeout copy。

所以本轮更诚实的动作是：**给一条新的 crypto / paper-based EMA 候选做 `source intake -> implementation-ready clean-room spec`，缩短下一轮 time-to-clean-replication。**

## 本轮做了什么
### 1) 新增 clean-room spec 生成脚本
新增：
- `scripts/build_ema_plateau_consensus_scout_spec.py`

它把 Chiu et al. (2023) 的 heatmap / plateau 思路压成最小、可执行的 desk spec：
- `candidate_id = scout_ema_plateau_consensus_15m_v1`
- 样本固定：`BTC / ETH / SOL | Binance 120d | 15m`
- 小邻域固定：
  - `fast ∈ {8, 10, 12}`
  - `slow ∈ {34, 40, 50}`
- `trade on / trade off` 明确写死：
  - `trade on = 邻域 long votes 达阈值（2/3 或 5/9）`
  - `trade off = 票数回落，或 spread guard 不足`
- v1 只做 `long-or-flat`，不把 short 侧硬写成镜像
- 第一轮实验矩阵固定为：
  - `anchor_10_40`
  - `row_consensus_2of3`
  - `plateau_vote_5of9`
  - `plateau_vote_5of9_spread_guard`
- 执行口径与当前 Scout 快筛保持一致：
  - `next-bar open`
  - `1 ATR stop`
  - `2 ATR target`
  - `8-bar time stop`
  - `6 bps/side`

### 2) 生成 reader-facing artifact
落地产物：
- `reports/artifacts/scout_ema_plateau_consensus_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_ema_plateau_consensus_15m/spec_meta.csv`
- `reports/site/factors/scout_ema_plateau_consensus_15m/report.html`

reader-facing 页明确写死两点：
1. 这页是 **clean replication 输入页**，不是成绩宣判页；
2. 当前 hard verdict 只是：**已通过 source intake / clean-room spec，但还没有通过 clean replication，因此不能误写成 `paper candidate`。**

### 3) 同步 desk board / shortlist
更新：
- `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
  - 新增 `Rank 18 EMA neighborhood consensus / plateau-stable crossover`
- `docs/TODO.md`
  - 在 Scout 候选阶段表中新增 `Rank 18`，状态写成 `source intake / clean replication next`
  - 把当前窗口排班更新为：`Rank 18 clean replication next；Rank 17 只在 genuinely verdict-changing check 时继续`
  - 在 `Run 2` 具体顺序里新增 `2l`，明确下一轮默认优先做 `Rank 18` 的最小 clean replication

## 最小验证
已执行并通过：
1. `python3 scripts/build_ema_plateau_consensus_scout_spec.py`
2. `bash scripts/publish_homepage_index.sh`

验证结果：
- 新 artifact 已生成；
- 新网页页签已落到：
  - `reports/site/factors/scout_ema_plateau_consensus_15m/report.html`
- 首页索引已刷新并发布：
  - `https://jp.jerrypsy.top/momentum/`

## 硬结论（hard verdict）
- **`Rank 18 EMA neighborhood consensus / plateau-stable crossover` 当前应读作：`source intake / clean replication next`。**
- 它当前边际价值高于继续给 `Rank 17` 补近义 wiring，因为它能最快回答：
  - EMA 结果是不是只在单点参数上发亮；
  - 还是相邻参数确实存在可复核的小平台。
- 但在补完最小 clean replication 前，**它还不是 `paper candidate`，更不是 `Live Seat` 候选。**

## 对 desk 主线的意义
- 这轮减少的是 `Scout Seat` 的 fresh intake 断层：
  - 避免 `EMA waiting_not_due` 时，bot3 继续在 `Rank 17` wiring 与已 park 候选之间来回打转；
  - 给当前 board 要求的 `paper / repo based 5m / 15m crypto` fast lane 补上一条新的实现入口；
  - 而且这条线不再强调 breakout，而是把当前 desk 已熟悉的 EMA 家族收窄成一个更可诚实快筛的邻域稳定性候选。

## 风险 / 边界
- 这轮没有产出新的收益数字，也没有完成 clean replication；
- 它没有改变现有 seat verdict：
  - `Paper Seat = EMA` 不变；
  - `Live Seat = 暂空` 不变；
  - `Rank 17` 仍是 `paper candidate pool`；
- 这轮唯一新增的是：**新的 Scout 候选已从 digest / source idea 推进到 implementation-ready spec。**

## 下一轮建议
- 优先按这张 spec 做最小 clean replication；
- 第一刀重点先看：
  - `post_cost_return`
  - `positive_asset_ratio`
  - `no_trade_ratio`
  - `cost_survival`
- 若 plateau 版本只是靠 `no_trade_ratio > 80%` 才勉强转正，或相对 `anchor_10_40` 没有更诚实的跨资产改善，则应直接 `park`，不要把“更少交易”误写成平台稳定性。

## 网页可见落点
- `reports/site/factors/scout_ema_plateau_consensus_15m/report.html`
- `docs/TODO.md`（及其站点镜像 / Control Tower）
- `https://jp.jerrypsy.top/momentum/`

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
