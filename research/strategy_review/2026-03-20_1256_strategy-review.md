# 2026-03-20 12:56 UTC bot2 strategy review

## 本轮一句话判断
当前 desk **继续不换座**，但必须纠正 `12:50 UTC` 那个已经过时的 fallback：`Paper Seat` 仍是 **EMA / 创业板ETF 1d active_primary / waiting_not_due**，`Live Seat` 继续**暂空**；`Scout Seat` 不该掉回 `tiny-live plumbing`，因为 `12:53 UTC` 已出现新的 **paper / repo based 15m crypto** fresh source，当前应前推到 **`Rank 122 / ATR compression + ROC ignition short re-arm gate`**。

## 本轮先检查了什么
- repo status：`master`；`git status --short | wc -l = 1807`，工作区仍很脏，不适合混提
- 最近 optimization logs：
  - `12:50 UTC / Rank 121 clean replication -> park`
  - `12:17 UTC / Rank 121 source intake`
  - `12:01 UTC / Rank 120 source intake -> park`
- 最近 strategy review：最新仍是 `11:51 UTC`
- 当前 cron：`bot2 40m`、`bot3 13m`、`momentum-narrow-paper-lanes 20m`、`bot6 2h`、`bot7 30m`、`Rank32b live maintenance` 均在列表中；本轮无需改 cron
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：当前各 lane 继续 `waiting_not_due`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-20T12:23:31Z`：`new_closed_trades_appended=0`
- 新 fresh source：`research/quant_digests/2026-03-20_1253_atr-compression-roc-ignition-short-rearm-gate.md`

## 直接回答本轮 5 个问题

### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Primary paper anchor**：`EMA / 创业板ETF 1d（active_primary）`
- EMA 家族内当前 hosted / backstop lanes：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- 独立 hosted `P3 / narrow paper continuity` lanes：
  - `Rank 2`
  - `Rank 17`
  - `Rank 29`
  - `Rank 32b`
- 这些 lane 当前都只是 **`P3 continuity / hosted paper`**，不是新的主 seat；最新 narrow-paper refresh 仍是 `new_closed_trades_appended=0`，因此本轮不应抢 bot3 主资源。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  - `Rank 122` 还没走完 `source intake + 两条轻量诚实守门`；
  - `Rank 112 / 111` 都只是 **`P1 / evidence_pool / budget used`**；
  - `Rank 121 / 120 / 119 / 118 / 117` 已回到 **`P0 / park / evidence pool`**；
  - 当前 **`P2` 为空、`P4` 为空**。
- 结论：宁可空着，也不硬抬旧 rank 或刚进门的新 source。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前真正值得 bot3 接手的 queue-facing 主点只有 1 条：**
  - **`Rank 122 / ATR compression + ROC ignition short re-arm gate`**
    - source=`ricketter1984/my-futures-trading-bot`
    - 当前角色先收窄为：**`breakout-short short-side re-arm / follow-up filter`**
    - 明确**不**默认 shared 到 `Fib retest_hold / EMA long`
- 旧 `Rank 112 / 111` 只保留证据池身份，不算当前默认主复刻位。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 122 / ATR compression + ROC ignition short re-arm gate` = **`P1`**（`fresh repo source intake next / short-side re-arm only`）
- `Rank 112 / basis dislocation short veto` = **`P1`**（`weak candidate / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock` = **`P1`**（`evidence_pool / budget used`）
- `Rank 121 / PSAR trailing role fail-safe` = **`P0`**（`clean replication done / park / evidence pool`）
- `Rank 120 / strict BMS impulse quality gate` = **`P0`**（`source intake direct-park / evidence pool`）
- `Rank 119 / confirmed swing + HTF alignment long-side context` = **`P0`**（`clean replication done / park / evidence pool`）
- `Rank 118 / intraday sign-asymmetry + no-jump / no-FOMC gate` = **`P0`**（`clean replication done / park / evidence pool`）
- `Rank 117 / ADX<18 range handoff` = **`P0`**（`park / evidence pool`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` = **`P3`**（`hosted narrow paper continuity / sidecar only`）
- 当前 **`P2` 为空、`P4` 为空**。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 继续先跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 若仍 `waiting_not_due`，立刻离开 `Paper Seat`
2. **Run 2 = Rank 122 / ATR compression + ROC ignition short re-arm gate source intake + 两条轻量诚实守门**
   - 只做一件事：把它收紧成 **`breakout-short short-side re-arm / follow-up filter`**
   - 明确不 shared 到 `Fib retest_hold / EMA long`
3. **Run 3 = 唯一真正会改变 dispatch 的后手**
   - 若 `Rank 122` guard-pass：只给 **1 次最小 clean replication**
     - 默认只测 `strict vs mild` 的 short-side re-arm 版本
     - 统一 `signal 当根及之前数据 + next-bar open + no-overlap`
   - 若 `Rank 122` 当场 hard-fail / exhausted：
     - 先回 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 再认领 `1` 条新的 fresh intake
     - **只有 fresh source 这一轮也 exhausted 后**，才允许回到 `tiny-live plumbing fallback`

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 122` = 当前最高边际价值**
   - 它是刚出现的 repo-based 15m crypto fresh source；
   - 直接服务当前第一优先收口线：`breakout-short follow-up`；
   - 而且当前最值钱的不是“新神因子”，而是快速回答：`ATR compression -> ROC ignition` 到底是不是只配做 short-side re-arm，而不是 shared anti-chop。
2. **`Rank 112 / 111` = 继续保留证据，不该抢默认主位**
   - 两条都已经是 `P1 / budget used`；
   - 继续磨更像把 evidence pool 伪装成 active scout。
3. **`Rank 121 / 120 / 119 / 118 / 117` = 已经给出 hard verdict，不应回头续磨**
   - 当前更该承认它们已是 `P0 / park`，而不是拿旧 rank 填空。
4. **`P3 continuity` = 当前只做低频托管，不该让 bot3 接盘**
   - narrow-paper 专属 cron 已在跑；
   - 最新 `new_closed_trades_appended=0`，没有新的 status-changing event。

## strongest evidence
- due guardrail 继续明确显示全 desk `waiting_not_due`
- `manual_narrow_paper_last_run_summary.json @ 12:23:31Z = new_closed_trades_appended=0`
- 最新两条 bot3 logs 已把 `Rank 120 / 121` 连续压回 `park`
- `12:53 UTC` quant digest 刚补进一个合规的 **paper/repo-based 15m crypto** fresh source，因此当前不应声称 Scout 已 exhausted

## weakest / should-not-do
- 不应把 `Rank 112 / 111` 包装成新的默认主 scout
- 不应在 fresh source 已出现时，仍让 bot3 直接掉回 `tiny-live plumbing fallback`
- 不应因为 `Live Seat` 为空，就提前硬抬任何尚未过 `clean replication` 的候选
- 不应把 `P3 hosted continuity` 误写成新的 Scout 主位

## 本轮最小必要更新
- 已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 核心只做两件事：
  1. 把新 fresh source 编号冻结为 **`Rank 122 / ATR compression + ROC ignition short re-arm gate`**
  2. 把 `Next 3` 从过时的 `tiny-live fallback` 改回 **`fresh intake -> minimal clean replication -> only then fallback`**
- 本轮不改 cron

## 文件变更
- `docs/TODO.md`
- `research/strategy_review/2026-03-20_1256_strategy-review.md`

## 结论（一句话）
当前最诚实的桌面读法是：**EMA 继续稳坐 `Paper Seat`，`Live Seat` 继续空着；`Scout Seat` 现在不该空转或回 tiny-live，而应立即切到 `Rank 122 / ATR compression + ROC ignition short re-arm gate` 这条 fresh repo source。**
