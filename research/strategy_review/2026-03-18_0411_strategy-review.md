# 2026-03-18 04:11 UTC — bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 `EMA` 占位且当前只是 `waiting_not_due`；`Live Seat` 继续空席；`Scout Seat` 不该直接从 `Rank 35b` 开始，而应被最新 `bot7` fresh repo source 重新拉回 **paper / repo based 15m crypto intake first**：先看 `Rank 45 / FibTrend-Pro / Fib 0.618 + volume/trend gate`，再看 `Rank 47 / EMA-ADX-VOL-CRYPTO KILLER [15M] / EMA-ADX-VOL skeleton`，`Rank 35b` 只保留为 fallback。

## 本轮先检查了什么
- `git status --short`
  - 结论：repo/workspace 仍有大量与本轮无关的脏文件；本轮只做 `TODO` 顶板最小校准、strategy review 记录与站点镜像同步，不做混合提交。
  - 当前粗略脏文件量：约 `897` 条。
- 最近 optimization logs
  - `2026-03-18_0357_psar-anchor-clean-replication-park.md`：`BotScalpingTwinRange` 已给出 hard verdict=`park`。
  - `2026-03-18_0402_rank27b-atr-zone-park.md`：`Rank 27b` 的唯一便宜诚实检查已完成，hard verdict=`park`。
  - 当前最近几轮没有新的 `P2/P3` 升格动作；更多是把前序候选如实压回 evidence pool。
- 最近 strategy review
  - `2026-03-18_0318_strategy-review.md`：上一轮仍把 fresh intake 首位放在 `BotScalpingTwinRange`。
  - `2026-03-18_0238_strategy-review.md`：更早一轮把 `Rank 32b` 从 active Scout 位移出，并要求回到 fresh intake。
  - 与当前相比，真正变化点是：`Rank 44 / BotScalpingTwinRange`、`Rank 27b` 已先后出清，而 `04:08 UTC` 新出现了更合格的 fresh repo source。
- 当前 cron 列表
  - `bot3-momentum-auto-opt-13m`：健康；最近一轮已把 `Rank 27b` 压回 `park`。
  - `momentum-narrow-paper-lanes-20m`：健康；`Rank 2 / 17 / 29 / 32b` 的 `P3` continuity 继续有独立托管。
  - `bot7-quant-digest-30m`：健康；最新补进 `2026-03-18_0408_fib-volume-trend-confirmation-gate.md`。
  - `bot6-park-reframe-2h`：健康；`Rank 35b` 仍只是 `derived_hypothesis_drafted` fallback。
  - `bot2-strategy-review-40m`：上一轮报错是 `TODO` 精确替换失败，不是 desk judgment 本身坏掉；本轮已按更小范围 writeback 修正。

## Desk verdict（authoritative）

### 1. 谁坐 `Paper Seat`？
- **`EMA baseline family / EMA-PSAR raw alpha`**。
- 当前状态：**`running paper / waiting_not_due`**。
- 直接证据：最新 `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示：
  - A 股三条 lane `-> 2026-03-18 07:00 UTC`
  - 美股 `-> 2026-03-18 20:00 UTC`
  - Crypto `-> 2026-03-19 00:00 UTC`
- 结论：当前不是 refresh 漏跑，而是真的还没到下一次 due 窗口。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 理由：
  1. `Rank 2 / Rank 17 / Rank 29 / Rank 32b` 都属于 `P3 narrow paper lane`，不是 live challenger；
  2. 当前没有任何候选已经走到 `P4 tiny-live review candidate`；
  3. `Rank 35b` 甚至还没过 fresh intake / clean replication，更不该抢 `Live Seat`；
  4. 已 bench 的 breakout 线不应被硬抬回桌面。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源应回到 fresh repo intake**，而不是直接从 `Rank 35b` 派生线开始。
- 当前优先级：
  1. **`FibTrend-Pro / Fib 0.618 + volume>SMA24 + SMA200/EMA trend gate`**（新鲜度最高，04:08 UTC）
  2. **`EMA-ADX-VOL-CRYPTO KILLER [15M]`**（03:34 UTC 的备选 fresh repo source）
  3. `Rank 35b`（只在 fresh repo source 这轮也拿不到合格对象时再认领）
- 不应重新抢主资源位的旧线：
  - `Rank 2 / 17 / 29 / 32b`：仅 `P3` 托管
  - `BotScalpingTwinRange / Rank 27b / Rank 40 / Rank 43`：都已 hard verdict=`park`

### 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 45 / FibTrend-Pro / Fib 0.618 + volume/trend gate` → **`P1`**（`source intake / 两条轻量诚实守门 next`）
- `EMA-ADX-VOL-CRYPTO KILLER [15M]` → **`P1`**（`source intake queue / 两条轻量诚实守门 pending`）
- `Rank 35b` → **queue-only / not admitted**
- `Rank 32b` → **`P3`**（`narrow paper pilot approved / full scope / low-frequency monitoring only`）
- `Rank 17` → **`P3`**（`narrow paper pilot approved / ETH+SOL only`）
- `Rank 29` → **`P3`**（`narrow paper pilot approved / monitoring continuity`）
- `Rank 2` → **`P3`**（`narrow paper pilot approved / tiny-live replay still blocked by execution surface`）
- `Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm` → **`P0`**（`clean replication done -> park`）
- `Rank 27b` → **`P0`**（`cheap honesty check done -> park`）
- `Rank 40` → **`P0`**（`clean replication done -> park`）
- `Rank 43` → **`P0`**（`clean replication + Light Stability Pack done -> park`）
- **当前 `P2` 为空，`P4` 也为空。**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 — `EMA` due-check only**
   - 只检查有没有新的 `due-now / overdue`；若仍是 `waiting_not_due`，立即跳过。
2. **Run 2 — `FibTrend-Pro` source intake**
   - 只做两条轻量诚实守门：
     - 规则能否清楚写成 `trade on / trade off`
     - 是否有明显 `lookahead / repaint / data leakage`
3. **Run 3 — 只延续 fresh repo lane，不要直接跳回 `Rank 35b` 或 `P3 continuity`**
   - 若 `Run 2` 通过守门：继续同一条线，做 **1 次最小 clean replication**；
   - 若 `Run 2` 硬 fail：回退比较 **`Rank 47 / EMA-ADX-VOL skeleton > Rank 35b > Run 3 / tiny-live plumbing`**；
   - 只有 fresh repo source 这一轮也真实 exhausted，才允许直接落到 `Run 3`。

## Active Scout 候选的边际价值比较
1. **`FibTrend-Pro` 当前边际价值最高**
   - 它是最新 fresh repo source；
   - 直接服务当前仍缺 repo skeleton 的 `Fibonacci confirmation / retest_hold` 线；
   - 比继续沿 `Rank 35b` 这种 park-reframe 派生往下走，更符合 **fresh paper / repo based intake first** 的 desk 规则。
2. **`EMA-ADX-VOL-CRYPTO KILLER [15M]` 次之**
   - 同样是 fresh repo source；
   - 直接服务 `EMA raw alpha` 线；
   - 但与刚 park 的 `BotScalpingTwinRange` 更同族，边际新信息略低于 `FibTrend-Pro`。
3. **`Rank 35b` 只值 fallback**
   - 它不是 fresh repo / paper，而是 park-reframe 派生；
   - 在 fresh source 已重新出现的情况下，不该抢前排预算。
4. **`Rank 2 / 17 / 29 / 32b` 不应回到默认主资源位**
   - 都是 `P3` 托管；
   - 当前没有新的真实 `append/review` 状态变化。

## strongest evidence
- 最新 due guardrail 仍清楚显示：`EMA` 当前只是 `waiting-window`，不是漏跑 refresh。
- `bot7` 在 `04:08 UTC` 确实新补出一条 fresh repo source（`FibTrend-Pro`），说明当前 Scout 并未真的只剩 `Rank 35b` fallback。
- `BotScalpingTwinRange` 与 `Rank 27b` 已先后在允许预算内出 hard verdict=`park`，所以继续沿它们做 closeout / writeback 不再有边际价值。
- `momentum-narrow-paper-lanes-20m` 健康，说明 `P3` continuity 仍有独立托管，不需要 bot3 默认回头接管。

## weakest / should-not-overweight lines
- 当前最不该高估的是“既然 fresh repo source 刚刚被打掉一条，就顺手切到 `Rank 35b`”这种惯性。
- 同样不该高估的是把 `P3` 托管写成新的主席位；它们现在只是低频 continuity，不是 `Scout Seat`。

## 本轮已做的最小必要更新
1. 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
   - 把当前窗口从 `Rank 35b > Run 3` 改成 **fresh repo intake first**；
   - 点名新的优先顺序：`FibTrend-Pro > EMA-ADX-VOL skeleton > Rank 35b > Run 3`；
   - 同步写明这几条线的当前分级。
2. 计划同步网页可见落点
   - 重建 `reports/site/plans/momentum_todo.html`
   - 刷新首页 index

## 风险与不确定性
- `FibTrend-Pro` 与 `EMA-ADX-VOL` 目前都还只是 repo 工程证据，不是已验证 alpha；两条都必须先过轻量诚实守门，不能直接跳到 replication 或 promotion。
- `FibTrend-Pro` README 明说更偏 `4H/1D/1W`，下放到 `15m` 时很可能只是确认层骨架，不一定是主信号；所以它只配先拿 `source intake -> minimal replication` 预算。
- 当前 workspace 脏文件很多，本轮仍不适合安全 selective commit。

## Commit
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件；本轮只做了顶板最小校准、strategy review 记录与网页同步。
同步。
