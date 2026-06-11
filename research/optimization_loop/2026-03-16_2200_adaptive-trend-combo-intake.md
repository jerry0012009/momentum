# 2026-03-16 22:00 UTC — adaptive trend combo intake

## 本轮定位
- 先读取 `docs/TODO.md` 顶部 `TRADING DESK BOARD`。
- 当前 `Paper Seat = EMA` 仍是 running paper，但处于 `waiting_not_due / due_soon`，本轮不该在 waiting-window 空转。
- 再比较 active Scout 候选的边际价值：
  - `Rank 1 / 3 / 4 / 5` 已经分别给出 `park`；
  - `Rank 2 combo_all` 已进入 `narrow paper pilot approved`，当前若没有真实 `append/review` need，再补 wiring 边际价值很低；
  - 因此本轮主资源转去 **新的 paper-based 15m crypto intake**，而不是继续磨旧候选。

## 开工前检查
### repo / dirty state
- `git status --short` 显示工作区本来就有大量历史脏文件与未跟踪产物；本轮不做混提，不碰与当前 intake 无关的历史产物。
- 本轮只新增 / 更新：
  - `scripts/build_adaptive_trend_combo_scout_spec.py`
  - `reports/artifacts/scout_adaptive_trend_combo_15m/clean_room_spec_v1.csv`
  - `reports/artifacts/scout_adaptive_trend_combo_15m/spec_meta.csv`
  - `reports/site/factors/scout_adaptive_trend_combo_15m/report.html`
  - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
  - 本日志文件

### 最近 runs（避免重复劳动）
- `2026-03-16_2052_ema-due-followup-reset-to-scout.md`
- `2026-03-16_2107_rank2-refresh-history-seed.md`
- `2026-03-16_2133_scout-routing-reset.md`
- `2026-03-16_2149_intraday-tsmom-session-park.md`

## 本轮主点
**新的 Scout intake：adaptive trend signal combination / state-weighted component vote（Mugueta-Aguinaga et al. 2023）**

### 为什么这条线现在更值得拿主资源
一句话：**不是再开一条更花的新框架，而是把现有 desk 已经有的 EMA / breakout / retest 组件，压成一条更适合 15m crypto 的手写状态切换候选。**

相对当前其余 active Scout 候选：
1. `Rank 2 combo_all`
   - 已经进入 `narrow paper pilot approved`；
   - 当前若没有真实 `append-ready refresh/review row`，继续补近义 wiring 会违反 board 对边际价值的要求。
2. `Rank 5 intraday TSMOM`
   - clean replication 与 Light Stability Pack 已完成，四项稳定性一起 fail；继续看只是 closeout copy。
3. `Rank 1 / 3 / 4 / 4b`
   - 都已 park，没有新数据源 / 新 pair universe / 新授权，不该继续占本轮主资源。

所以本轮更诚实的动作是：**给新的 paper-based 15m crypto 候选做 `source intake -> implementation-ready clean-room spec`，缩短下一轮 time-to-clean-replication。**

## 本轮做了什么
### 1) 新增 clean-room spec 生成脚本
新增：
- `scripts/build_adaptive_trend_combo_scout_spec.py`

它把这条候选压成一个明确、可执行的最小 spec：
- `candidate_id = scout_adaptive_trend_combo_15m_v1`
- 数据范围：`BTC / ETH / SOL | Binance 120d | 15m`
- 组件只允许复用当前 desk 已有家族：
  - `ema_direction = sign(EMA20 - EMA50)`
  - `combo_breakout = Rank 2 combo_all confirmation vote`
  - `retest_guard = 2-of-3 closes outside / support-flip persists`
- 状态定义只允许手写：`trend / turbulent / chop`
- 第一轮实验矩阵固定为：
  - `fixed_priority`
  - `equal_vote`
  - `state_weighted_vote`
- 执行口径固定：
  - `next-bar open`
  - `1 ATR stop`
  - `2 ATR target`
  - `8-bar time stop`
  - `6 bps/side`

### 2) 生成 reader-facing artifact
落地产物：
- `reports/artifacts/scout_adaptive_trend_combo_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_adaptive_trend_combo_15m/spec_meta.csv`
- `reports/site/factors/scout_adaptive_trend_combo_15m/report.html`

reader-facing 页明确写死两点：
1. 这页是 **clean replication 输入页**，不是成绩宣判页；
2. v1 **禁止**引入 ML 训练器，只允许固定权重 + 手写状态 + 现有组件，避免它滑成“新大框架”。

### 3) 补进 Scout shortlist
更新：
- `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`

新增一行：
- `Rank 7 adaptive trend signal combination / state-weighted component vote`
- 来源挂到现有 digest：`2026-03-15_1342_adaptive-trend-signal-combination.html`
- 角色定位：**新的 Scout intake 候补；先做 source intake + clean replication，不直接抢 Live Seat。**

## 最小验证
已执行并通过：
1. `python3 /root/clawd/jerry/momentum/scripts/build_adaptive_trend_combo_scout_spec.py`
2. `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`

验证结果：
- 新 artifact 已生成；
- 新网页页签已落到：
  - `reports/site/factors/scout_adaptive_trend_combo_15m/report.html`
- 首页索引已刷新：
  - `https://jp.jerrypsy.top/momentum/`

## 硬结论（hard verdict）
- **这条 adaptive trend combo 当前只通过了 `source intake / clean-room spec`，还没有通过 clean replication。**
- 但和当前其余 active Scout 候选相比，它是更合适的新 intake：
  - 不需要新数据源；
  - 不需要新大框架；
  - 可以复用现有 EMA / Rank 2 confirmation 组件；
  - 下一轮可以直接进入最小 clean replication。
- 因此当前最诚实的 desk call 是：
  - **保留为新的 Scout intake 候补，下一轮优先做 clean replication；**
  - **现在还不能写成 `paper candidate`，更不能写成 `Live Seat` 候选。**

## 对 desk 主线的意义
这轮减少的不是某条旧候选的 wording blocker，而是 **Scout Seat 的 intake 断层**：
- 避免 `EMA waiting_not_due` 时，bot3 只会在 `Rank 2` wiring 与已 park 候选之间来回打转；
- 给当前 board 要求的 `paper / repo based 5m / 15m crypto` fast lane 补上一条新的、可直接实现的入口。

## 风险 / 边界
- 这轮没有产出新的 alpha 收益数字；
- 它也没有改变现有 seat verdict：
  - `Paper Seat = EMA` 不变；
  - `Live Seat = 暂空` 不变；
  - `Rank 2 combo_all` 仍是 `narrow paper pilot approved`；
- 这轮唯一新增的是：**下一条 Scout 候选已从“论文想法”推进到“可直接做 clean replication 的 implementation-ready spec”。**

## 下一轮建议（不是本轮继续做）
- 优先按这张 spec 做 `fixed_priority / equal_vote / state_weighted_vote` 的最小 clean replication；
- 第一刀重点先看：
  - `post_cost_return`
  - `no_trade_ratio`
  - `cost_survival`
  - `positive_asset_ratio`
- 若 clean replication 后只是靠 `no-trade_ratio` 飙升才守住收益，则应直接 `park`，不要把“少做交易”误写成组合优势。

## 网页可见落点
- `reports/site/factors/scout_adaptive_trend_combo_15m/report.html`
- `https://jp.jerrypsy.top/momentum/`

## Git / 提交
- 未提交。
- 原因：当前工作区存在大量与本轮无关的脏文件 / 未跟踪文件，不适合安全 selective commit。
