# 2026-03-20 13:59 UTC bot2 strategy review

## 本轮一句话判断
当前 desk **继续不换大座，但要换 Scout 主位**：`Paper Seat` 仍是 **EMA / 创业板ETF 1d active_primary / waiting_not_due**；`Live Seat` 继续**暂空**；而 `Rank 122` 已经升到 **`P3 / narrow paper pilot approved`**，不该再继续占 `Scout Seat`。在没有新的 `due-now / status-changing event` 前，bot3 应从 `P3 continuity` 撤回，转去新的 fresh repo source：**`Rank 123 / RSI enter→exit→re-enter state-machine admission`**。

## 本轮先检查了什么
- repo status：`master`；`git status --short | wc -l = 1823`，工作区很脏，不适合混提
- 最近 optimization logs：
  - `13:40 UTC / Rank 122 时间稳定性检查 -> 升到 P3 narrow paper pilot`
  - `13:29 UTC / Rank 122 clean replication -> P2`
  - `13:04 UTC / Rank 122 source intake -> guard-passed`
- 最近 strategy review：最新仍是 `12:56 UTC`
- 当前 cron：`bot2 40m`、`bot3 13m`、`momentum-narrow-paper-lanes 20m`、`bot6 2h`、`bot7 30m`、`Rank32b live maintenance` 仍在；本轮无需改 cron
- `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`：当前各 lane 继续 `waiting_not_due`
- `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-20T13:32:41Z`：`new_closed_trades_appended=0`
- 新 fresh source：`research/quant_digests/2026-03-20_1353_rsi-state-machine-admission-not-shared-short-gate.md`

## 直接回答本轮 5 个问题

### 1) 当前 `Paper Seat` 的 primary paper anchor 是谁？当前有哪些 hosted paper lanes 在跑？
- **Primary paper anchor**：`EMA / 创业板ETF 1d（active_primary）`
- EMA 家族内当前 hosted / backstop lanes：
  - `美股 1d+1wk（SPY/QQQ/AAPL）`
  - `Crypto 1d+1wk（BTC/ETH/SOL）`
  - `贵州茅台 1d+1wk`
  - `沪深300ETF 1d（shadow_watch）`
- 独立 hosted `P3 / narrow paper continuity` lanes（已在托管）：
  - `Rank 2`
  - `Rank 17`
  - `Rank 29`
  - `Rank 32b`
- **新增但不该抢主资源的 hosted narrow lane**：
  - `Rank 122 / ATR compression + ROC ignition short re-arm gate`
  - 当前状态：**`P3 / narrow paper pilot approved`**，但只限 `strict-only / short-side re-arm / paper-only / recent-month red-watch`
- 结论：当前 paper 托管层确实多 lane 并存，但**主 paper anchor 仍只有 EMA / 创业板ETF 1d**。

### 2) `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 原因：
  - `Rank 123` 还只是 fresh source，连正式 `source intake + 两条轻量诚实守门` 都还没走完；
  - `Rank 112 / 111` 都只是 **`P1 / evidence_pool / budget used`**；
  - `Rank 122` 虽已升到 `P3`，但它是 **paper-only narrow lane**，不是 live challenger；
  - 当前 **`P2` 为空、`P4` 为空**。
- 结论：宁可空着，也不为了桌上必须有 live challenger 而硬抬旧 rank 或刚进门的新 source。

### 3) `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前 queue-facing 主点只该有 1 条：**
  - **`Rank 123 / RSI enter→exit→re-enter state-machine admission`**
    - source=`MoDiggler75/crypto-trading-bot`
    - 当前角色先收窄为：**`Fib retest_hold + EMA/PSAR long-side sparse admission`**
    - 明确**不** shared 到 `breakout-short`
- 旧 `Rank 112 / 111` 只保留证据池身份，不算当前默认主复刻位。
- `Rank 122` 已退出 `Scout Seat`，当前应按 `P3 hosted paper continuity` 管理，而不是继续当 scout 主动作。

### 4) 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 123 / RSI state-machine admission` = **`P1`**（`fresh repo source intake next / long-side sparse admission only`）
- `Rank 112 / basis dislocation short veto` = **`P1`**（`weak candidate / evidence_pool / budget used`）
- `Rank 111 / abnormal-return event clock` = **`P1`**（`evidence_pool / budget used`）
- `Rank 122 / ATR compression + ROC ignition short re-arm gate` = **`P3`**（`narrow paper pilot approved / strict-only / paper-only / recent-month red-watch`）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` = **`P3`**（`hosted narrow paper continuity / sidecar only`）
- `Rank 121 / 120 / 119 / 118 / 117 / 115 / 114 / 113` = **`P0`**（`park / evidence pool`）
- 当前 **`P2` 为空、`P4` 为空**。

### 5) 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = EMA due-check first**
   - 继续先跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
   - 若仍 `waiting_not_due`，立刻离开 `Paper Seat`
2. **Run 2 = Rank 123 / RSI state-machine admission source intake + 两条轻量诚实守门**
   - 只做一件事：把它收紧成 **`Fib retest_hold / EMA-PSAR long-side sparse admission`**
   - 明确不 shared 到 `breakout-short`
3. **Run 3 = 唯一真正会改变 dispatch 的后手**
   - 若 `Rank 123` guard-pass：只给 **1 次最小 clean replication**
     - 默认只测 `fib_retest_long + ema_psar_long`
     - 统一 `signal 当根及之前数据 + next-bar open + no-overlap`
   - 若 `Rank 123` 当场 hard-fail / exhausted：
     - 先回 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist` 再认领 `1` 条新的 fresh intake
     - **只有 fresh source 这一轮也 exhausted 后**，才允许回到 `tiny-live plumbing fallback`

## Active Scout 边际价值比较（本轮显式比较）
1. **`Rank 123` = 当前最高边际价值**
   - 它是刚出现的 repo-based 15m crypto fresh source；
   - 直接满足当前默认优先级：paper / repo based + 5m/15m crypto + 不发明大框架；
   - 当前最值钱的不是“又多一个指标”，而是快速回答：`RSI state-machine` 到底是不是只配做 long-side sparse admission，而不是 breakout-short shared gate。
2. **`Rank 122` = 不该再占 Scout 主资源**
   - 它已经完成 `source intake -> clean replication -> 最小时间稳定性检查` 并升到 `P3`；
   - 再继续磨它，边际上更像在补 hosted continuity / operator packet，而不是继续减少真实 gate；
   - 在 `EMA waiting_not_due` 且没有新的 `due-now / status-changing event` 前，不应继续燃烧 `P3 continuity` 预算。
3. **`Rank 112 / 111` = 继续保留证据，不该抢默认主位**
   - 两条都已经是 `P1 / budget used`；
   - 继续磨更像把 evidence pool 伪装成 active scout。
4. **`P3 continuity` = 当前只做低频托管，不该让 bot3 接盘**
   - narrow-paper 专属 cron 已在跑；
   - 最新 `new_closed_trades_appended=0`，没有新的 status-changing event。

## strongest evidence
- due guardrail 继续明确显示全 desk `waiting_not_due`
- `manual_narrow_paper_last_run_summary.json @ 13:32:41Z = new_closed_trades_appended=0`
- 最新三条 bot3 logs 已把 `Rank 122` 从 `P1 -> P2 -> P3`
- `13:53 UTC` quant digest 刚补进一个合规的 **paper/repo-based 15m crypto** fresh source，因此当前不应继续把 bot3 停在 `P3 continuity`

## weakest / should-not-do
- 不应把 `Rank 122` 继续包装成 `Scout Seat` 主位
- 不应在 fresh source 已出现时，仍让 bot3 回头磨 `Rank 112 / 111`
- 不应因为 `Live Seat` 为空，就提前硬抬任何尚未过 `clean replication` 的 fresh intake
- 不应把 `P3 hosted continuity` 误写成新的 Scout 主位

## 本轮最小必要更新
- 已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 核心只做两件事：
  1. 明确把 `Rank 122` 从 `Scout Seat` 移出，冻结为 **`P3 hosted paper continuity / sidecar only`**
  2. 把新的 fresh source 编号冻结为 **`Rank 123 / RSI state-machine admission`**，并把 `Next 3` 改回 **`fresh intake -> minimal clean replication -> only then fallback`**
- 本轮不改 cron

## 文件变更
- `docs/TODO.md`
- `research/strategy_review/2026-03-20_1359_strategy-review.md`

## 结论（一句话）
当前最诚实的桌面读法是：**EMA 继续稳坐 `Paper Seat`，`Live Seat` 继续空着；`Rank 122` 已升到 hosted paper sidecar，不该再继续霸占 scout；bot3 现在该切去 `Rank 123 / RSI state-machine admission` 这条 fresh repo source。**
