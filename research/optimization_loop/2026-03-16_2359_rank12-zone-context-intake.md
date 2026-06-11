# 2026-03-16 23:59 UTC — Rank 12 averaged support/resistance zone + context intake

## 本轮先看了什么
- 先检查了 `git status`、`docs/TODO.md` 顶部 `TRADING DESK BOARD`、最近几轮 optimization logs。
- 当前 desk 状态：
  - `Paper Seat = EMA`，但处于 `waiting_not_due / due_soon`，本轮不该在 waiting-window 空转。
  - `Live Seat = 暂空`。
  - `Scout Seat` 应优先服务新的 `paper / repo based 15m crypto` 候选。
- active Scout 候选边际价值比较：
  - `Rank 7 / 8 / 9 / 10 / 11` 都已完成 `clean replication + Light Stability Pack` 并压回 `park / evidence pool`；继续认领它们默认只会新增近义说明，不会继续减少真实 gate。
  - `Rank 2` 已是 `narrow paper pilot approved`，但当前没有真实 `append/review` need 或 verdict-changing check；继续做它会落回 wiring。
  - shortlist 剩余 `Rank 5 / 6` 分别偏 `prediction market` 与 `跨资产 proxy spread`，和当前 desk 强调的 `paper-based 15m crypto fast lane` 不够贴。
- 因此本轮主点切到新的 zone 候选：**`Rank 12 averaged support/resistance zone + context gate`**（Zhang & Zhou 2024）。

## 本轮主动作
### 1) 产出新的 deployable artifact：Rank 12 clean-room spec
新增：
- `scripts/build_sr_zone_context_scout_spec.py`
- `reports/artifacts/scout_sr_zone_context_15m/clean_room_spec_v1.csv`
- `reports/artifacts/scout_sr_zone_context_15m/spec_meta.csv`
- `reports/site/factors/scout_sr_zone_context_15m/report.html`

本轮把论文里最值钱的那部分压成了当前 desk 可直接执行的最小 clean-room spec：
- 不是继续喊 breakout，而是改成：**averaged nearby resistance levels + trend/channel context**。
- 默认只做 `long-side`，不再把 short breakout 当镜像主角。
- 第一刀冻结四档最小 clean replication 对照：
  - `single_line_break`
  - `averaged_zone_break`
  - `averaged_zone_retest`
  - `averaged_zone_context_gate`
- 执行口径继续沿用当前 Scout fast lane：
  - `next-bar open`
  - `1 ATR stop`
  - `2 ATR target`
  - `8-bar time stop`
  - `6 bps/side`

## 本轮硬结论
**当前最诚实的新 fresh intake，是把 averaged support/resistance zone + context gate 压成因果、可复核的 15m crypto clean-room spec；它已通过 source intake，但还没有通过 clean replication，因此不能误写成 paper candidate。**

换句话说：
- 这轮不是要宣称 Rank 12 已经赢；
- 这轮是把它推进到 **implementation-ready / clean replication next**；
- 相比继续磨 Rank 2 或重开 Rank 7/8/9/10/11，这一步的边际价值更高。

## 紧邻子点：刷新 TRADING DESK BOARD / shortlist
已同步更新：
- `docs/TODO.md`
  - 候选阶段表新增 `Rank 12`，状态标成 `source intake / clean replication next`
  - `Next 3 bot3 runs` 的 authoritative override 改成：在 `EMA waiting_not_due` 时，默认先走 **`Rank 12 clean replication next`**
  - `Run 2` 当前具体执行顺序里新增 `2f`，明确 Rank 12 是新的 Scout fast-lane 主资源位
- `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
  - 新增 `Rank 12 averaged support/resistance zone + context gate`

## 为什么这轮不去做别的
- **没有继续做 Rank 2**：当前没有真实 append/review need，继续做大概率只是 wiring/card polishing。
- **没有重开 Rank 11**：它刚完成 clean replication + Light Stability Pack，已是 `park / evidence pool`。
- **没有切 Rank 5 / 6**：prediction-market / BTC-equity proxy 这两条线当前都不如新的 paper-based 15m crypto zone candidate 贴主线。
- **没有做 Run 3 tiny-live plumbing**：Scout Seat 仍有更高边际价值动作，尚未到“允许动作都被卡住”的程度，因此不能写 `NO_PROGRESS`。

## 最小验证
已执行：
- `python3 scripts/build_sr_zone_context_scout_spec.py`
- `bash scripts/publish_homepage_index.sh`

结果：
- 新 artifact 与 reader-facing 页面均已生成
- 首页 index 已刷新并发布到：`https://jp.jerrypsy.top/momentum/`

## 工作区/脏文件说明
- `git status` 显示 repo 中原本就存在大量与本轮无关的脏文件/未跟踪文件。
- 本轮只修改/新增与 `Rank 12 intake` 直接相关的最小集合：
  - `docs/TODO.md`
  - `reports/artifacts/literature/scout_seat_fast_cycle_crypto_shortlist_v1.csv`
  - `scripts/build_sr_zone_context_scout_spec.py`
  - `reports/artifacts/scout_sr_zone_context_15m/*`
  - `reports/site/factors/scout_sr_zone_context_15m/report.html`
  - 以及首页 publish 生成物
- 未做 git commit，避免把无关脏文件混提。

## 下一步（默认）
下一轮若 `EMA` 仍是 `waiting_not_due`，默认直接认领：
1. `Rank 12 clean replication`
2. 最小对照：`single_line_break vs averaged_zone_break vs averaged_zone_retest vs averaged_zone_context_gate`
3. 然后至少补 `Light Stability Pack` 一项；理想是一次性把 `时间 / 参数 / 跨标的 / 成本-交易数` 四项都补齐后给出 `park / paper candidate / narrow paper pilot` 三选一。
