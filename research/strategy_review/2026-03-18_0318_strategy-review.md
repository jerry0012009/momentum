# 2026-03-18 03:18 UTC — bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 `EMA / PSAR raw alpha` 占位且当前只是 `waiting_not_due`；`Live Seat` 继续保持空席；`Scout Seat` 不应再回头磨刚刚已 `park` 的 `Rank 43 / Rank 40`，而应切回 **fresh paper / repo based 5m / 15m crypto intake**，当前优先级最高的新 source 是 **`Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm`**。`Rank 27b / Rank 35b` 只保留为次级 fallback，不应抢在 fresh repo intake 前面。

## 本轮先检查了什么
- `git status --short`
  - 结论：repo 仍有大量与本轮无关的脏文件 / 未跟踪文件（当前 `git status --short` 约 `886` 行），因此本轮继续只做最小必要 writeback，不做混合提交。
- 最近 optimization logs
  - `2026-03-18_0236_rank32b-scope-promotion.md`：`Rank 32b` 完成 promotion honesty，已升到 **`P3 narrow paper pilot approved（full scope）`**。
  - `2026-03-18_0248_rank43-atr-retest-intake.md`：`Rank 43` 先被 admitted 进 clean replication queue。
  - `2026-03-18_0308_rank43-clean-replication-park.md`：`Rank 43` 的 clean replication + Light Stability Pack 已跑完，最终 hard verdict = **`park / evidence pool`**。
  - `2026-03-18_0314_rank40-clean-replication-park.md`：`Rank 40` 的那 1 次最小 clean replication 已跑完，最终 hard verdict = **`park / evidence pool`**。
- 最近 strategy review
  - `2026-03-18_0238_strategy-review.md`：上一轮已经把 `Rank 32b` 从 active Scout 主资源位里移出，要求回到 fresh intake；但当时 fresh intake 首选还是 `Rank 43`。
  - 对比最新 bot3 结果：`Rank 43` 与 `Rank 40` 现都已消耗完各自唯一 fast-lane budget，且都已被压回 `park`，因此本轮必须再次校准 Scout 资源位。
- 当前 cron 列表
  - `bot3-momentum-auto-opt-13m`：健康，最近两轮分别完成 `Rank 43` 与 `Rank 40` 的 closeout verdict。
  - `momentum-narrow-paper-lanes-20m`：健康，`03:08 UTC` 刚正常刷新；说明 `Rank 2 / 17 / 29` 的 `P3` continuity 继续有独立低频托管。
  - `bot6-park-reframe-2h`：健康，当前 queue 中保留 `Rank 27b / Rank 35b` 等派生假设，但它们仍只是 fallback 备选。
  - `bot7-quant-digest-30m`：健康，`02:55 UTC` 新增了 `Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm` digest，可作为当前 fresh intake 首选来源。

## Desk verdict（authoritative）

### 1. 谁坐 `Paper Seat`？
- **`EMA baseline family / EMA-PSAR raw alpha`**。
- 当前状态：**`running paper / waiting_not_due`**。
- 直接证据：最新 `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示：
  - A 股三条 lane `-> 2026-03-18 07:00 UTC`
  - 美股 `-> 2026-03-18 20:00 UTC`
  - Crypto `-> 2026-03-19 00:00 UTC`
- 结论：`EMA` 当前不是停摆，而只是 market clock 还没到下一次真实 due 窗口。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 理由：
  1. `Rank 2 / Rank 17 / Rank 29 / Rank 32b` 当前都应读作 `P3 narrow paper lane`，不是 live challenger；
  2. `Rank 32b` 虽然刚升到 `P3`，但它仍是 **paper-only narrow pilot**，不是 tiny-live 候选；
  3. `Rank 2` 的 tiny-live 仍卡在 execution surface 缺席，不是“再补一点文档”就能升格；
  4. 已 bench 的 breakout 不应为了“桌上必须有 live 候选”而被硬抬回来。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源应重新落到 fresh repo intake，不再回头磨 `Rank 43 / Rank 40`。**
- 当前最值得优先认领的候选：
  - **`Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm`**
  - 来源：`research/quant_digests/2026-03-18_0255_psar-anchor-ema-confirmation-gate.md`
  - 为什么是它：
    - 新的 repo-based source；
    - 直接服务 `EMA / PSAR raw alpha focus`；
    - 给出了“PSAR 做结构锚、EMA slope 做 continuation 质量层、ATR 做 regime/仓位层”的工程化角色拆分；
    - 当前比继续磨已 park 的 `Rank 43 / 40`、或过早回退 `Run 3` 更贴 desk 主线。
- fallback 候选（本轮不应抢主资源）：
  - `Rank 27b`：`PARK_REFRAME_QUEUE` 的 derived hypothesis，价值高于 `Rank 35b`，但仍应排在 fresh repo intake 之后；
  - `Rank 35b`：同样只是 derived hypothesis，且现有 pocket 更稀、更弱。
- 低频托管、但不算当前 Scout 主资源位：
  - `Rank 32b`
  - `Rank 17`
  - `Rank 29`
  - `Rank 2`

### 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm` → **`P1`**（`source intake / 两条轻量诚实守门 next`）
  - 说明：当前只应先回答 `trade on / trade off` 是否能冻结清楚、以及是否存在明显 `lookahead / repaint / leakage`；过门后才配拿 1 次最小 clean replication。
- `Rank 32b` → **`P3`**（`narrow paper pilot approved / full scope / 仅 monitoring-review continuity`）
- `Rank 17` → **`P3`**（`narrow paper pilot approved / ETH+SOL only`）
- `Rank 29` → **`P3`**（`narrow paper pilot approved / monitoring continuity`）
- `Rank 2` → **`P3`**（`narrow paper pilot approved / tiny-live replay blocked by execution surface`）
- `Rank 27b` → **queue-only / not admitted yet**（只在 fresh repo source 失败后才比较是否认领）
- `Rank 35b` → **queue-only / not admitted yet**
- `Rank 43` → **`P0`**（`clean replication + Light Stability Pack 已完成 -> park / evidence pool`）
- `Rank 40` → **`P0`**（`clean replication 已完成 -> park / evidence pool`）
- **当前 `P2` 为空；`P4` 也为空。**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 — `EMA` due-check only**
   - 只检查有没有新的 `due-now / overdue`；若仍是 `waiting_not_due`，立即跳过。
2. **Run 2 — `Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm` source intake**
   - 只做两条轻量诚实守门：
     - 规则能否清楚写成 `trade on / trade off`
     - 是否有明显 `lookahead / repaint / data leakage`
   - 这一步若不过，直接 `park / source-template only`，不要拖。
3. **Run 3 — 只延续同一 fresh source，或再择一 fallback；不要回头磨 P3 continuity**
   - 若 `Run 2` 通过守门：继续同一条 fresh source，做 **1 次最小 clean replication**；
   - 若 `Run 2` 硬 fail：再比较 `Rank 27b > Rank 35b > Run 3 / tiny-live plumbing`；
   - 只有 fresh intake 这一轮也真实 exhausted，或某条 `P3` lane 出现真实 `append/review` 事件，才允许回到 `P3 continuity` 或 tiny-live。

## Active Scout 候选的边际价值比较
1. **`Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm` 当前边际价值最高**
   - 它是 fresh repo source，尚未消耗 fast-lane budget；
   - 直接服务当前仍在运行的 `EMA / PSAR raw alpha` 主线；
   - 问的也是“PSAR 到底该做信号还是 gate”这种真正会改变 desk judgment 的问题。
2. **`Rank 27b` 次之，但只适合当 fallback**
   - 它的唯一修改轴很清楚（把静态 neckline retest 改成 ATR 弹性回踩区 + bounce reclaim），而且刚被 `Rank 43` 的结果间接增强；
   - 但本质仍是 park-reframe 派生，不应抢在 fresh repo source 前面。
3. **`Rank 35b` 再次之**
   - 也是清楚的一刀派生，但现有 pocket 更稀、更弱，边际价值低于 `Rank 27b`。
4. **`Rank 32b / 17 / 29 / 2` 不应回到默认主资源位**
   - 它们都已是 `P3`，且当前没有新的 `append/review` 状态变化；
   - 继续认领它们更像在制造 continuity 幻觉，而不是继续减少真实 gate。
5. **`Rank 43 / 40` 当前边际价值最低**
   - 因为各自唯一的 fast-lane 检查已做完，结论也已是 `park / evidence pool`；
   - 再继续磨只会是 intake / admission 近义文案。

## strongest evidence
- `EMA` 最新 due guardrail 仍清楚显示：当前只是 waiting-window，不是 paper lane 故障。
- `Rank 32b` 已完成 `P1 -> P2 -> P3` 的三连晋级，并且 full-scope 在 `15/20bps` 下仍保留 `3/3` 资产为正，说明它已经脱离 active Scout 位。
- `Rank 43` 与 `Rank 40` 已在最近两轮分别完成 closeout verdict，且都被压回 `park`，这使得继续磨旧 rank 的边际价值快速下降。
- `bot7` 在 `02:55 UTC` 已给出新的 repo-based PSAR/EMA 角色拆分 source，满足 fresh intake 优先于 park-reframe 的 desk 规则。

## weakest / should-not-overweight lines
- 当前最不该被高估的是“既然刚做完 `Rank 43 / Rank 40`，就继续围着它们补说明页”的惯性读法。
- 同样不该再默认高估的是 `Rank 2` tiny-live 文档链；execution surface 不出现，它就继续只是 blocked lane。

## 本轮已做的最小必要更新
1. 更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
   - 把 `Scout Seat` 最新口径从“`Rank 43 / Rank 40` 之后的模糊 fresh intake”收紧为：
     - `Rank 43 / 40` 已 park；
     - fresh intake 主资源位转给 `Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm`；
     - 失败后再比较 `Rank 27b > Rank 35b > Run 3`。
2. 同步站点镜像
   - 运行 `python3 scripts/build_todo_page.py`
   - 已写出：`reports/site/plans/momentum_todo.html`

## 风险与不确定性
- `BotScalpingTwinRange` 当前只是 **repo 工程证据**，不是已验证 alpha；若 source intake 阶段就发现口径不诚实，应快速压回。
- 它原生更偏 `30m / 5m / 1m` 角色分层，不是现成 15m 成品；因此本轮只应给 `source intake -> minimal clean replication` 预算，不能直接幻想成 `P2`。
- 自动化环境近期仍有大量无关脏文件，说明 selective commit 风险仍高；但这不影响当前 seat judgment 本身。

## 建议优先级 Top 1~3
1. `Rank 44 / BotScalpingTwinRange / PSAR anchor + EMA confirm`：先做两条轻量诚实守门，决定是否 admitted 进 clean replication
2. 若 admitted：立刻做同一条线的 **1 次最小 clean replication**，回答它到底只是角色分工模板，还是能改善 15m continuation 的 early-failure
3. 若 fresh repo source 硬 fail：再比较 `Rank 27b > Rank 35b > Run 3 / tiny-live plumbing`，不要直接跳回 `P3 continuity`

## Commit
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件；本轮只做了 `TODO` 顶板最小校准、站点镜像同步与 strategy review 记录，不适合安全 selective commit。
