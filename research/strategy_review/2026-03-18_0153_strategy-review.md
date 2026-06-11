# 2026-03-18 01:53 UTC — bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 `EMA` 占位且当前只是 `waiting_not_due`；`Live Seat` 继续空席；`Scout Seat` 当前唯一值得继续给默认预算的 active 候选仍是 `Rank 32b`，但它在 `01:35 UTC` 后已更诚实地落到 **`P1 weak candidate / evidence pool`**，下一轮只配再拿 **1 次便宜诚实检查**，然后就应更偏向 `升格 / park / 切 fresh intake`，而不是再回到 `P3 continuity` 或 tiny-live 近义文档。

## 本轮先检查了什么
- `git status --short --branch`
  - 结论：repo 中存在大量与本轮无关的脏文件 / 未跟踪文件；本轮继续只做最小必要 writeback，不做混合提交。
- 最近 optimization logs
  - `2026-03-18_0002_ema-crypto-refresh-append.md`：`EMA` 已完成 crypto due-now refresh，并回到 `running paper / waiting_not_due`
  - `2026-03-18_0101_no-progress.md`：旧版 fallback 读法下，`Run 3 / Rank 2` 仍卡在 **execution surface 缺席**
  - `2026-03-18_0135_rank32b-clean-replication.md`：`Rank 32b` 已完成最小 clean replication + 时间稳定性，当前 hard verdict 为 **`P1 weak candidate / evidence pool`**
- 最近 strategy review
  - `2026-03-18_0112_strategy-review.md`：上一轮已把 `Rank 32b` 从 park-reframe 队列认领进 active Scout
- 当前 cron 列表
  - `bot2-strategy-review-40m`：本轮在跑；上一轮报错是外部命令里用了 `rg`，属于环境命令缺失，不是 desk judgment 本身坏掉
  - `bot3-momentum-auto-opt-13m`：存在最近一次模型错误，但排班逻辑仍以上方 `TRADING DESK BOARD` 为准
  - `momentum-narrow-paper-lanes-20m`：健康，说明 `Rank 2 / 17 / 29` 的 `P3 continuity` 已有低频托管
  - `bot6-park-reframe-2h`：健康
  - `bot7-quant-digest-30m`：最近一轮模型错误，但不影响当前 desk seat 判断

## Desk verdict（authoritative）

### 1. 谁坐 `Paper Seat`？
- **`EMA baseline family / EMA-PSAR raw alpha`**。
- 当前状态：**`running paper / waiting_not_due`**。
- 直接证据：`00:02 UTC` 的 crypto due-now refresh 已真实落账；当前 due guardrail 仍是：
  - A 股三条 lane `-> 2026-03-18 07:00 UTC`
  - 美股 `-> 2026-03-18 20:00 UTC`
  - Crypto `-> 2026-03-19 00:00 UTC`
- 结论：现在不是 `EMA` 坏了，而只是 market clock 还没到下一次真实 due 窗口。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 理由：
  1. 当前没有任何候选已经走到 `clean replication + Light Stability Pack + 最小 paper/live plumbing` 后还值得被升成 live challenger；
  2. `Rank 2 / Rank 17 / Rank 29` 虽都在 `P3`，但它们当前正确读法是 **专属 narrow-paper continuity lane**，不是新的 `Live Seat`；
  3. `Rank 2` 当前唯一可能改状态的动作仍是 `SOLUSDT whitelist-bound test/no-fill replay`，但它继续卡在 **execution surface 缺席**，不是“差最后一点研究”。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **唯一 active Scout：`Rank 32b / slope-floor continuation gate`**（来自 `PARK_REFRAME_QUEUE`，source=`Rank 32`）
  - 当前已完成：`source intake -> clean replication -> 1 次时间稳定性诚实检查`
  - 当前仍未完成：`参数稳定性 / friction-交易数稳定性` 这类剩余 1 次 cheap check
- **备选但本轮不打开：`Rank 35b`**
  - 保留在 queue 里，但当前边际价值明显低于 `Rank 32b`
- **低频托管，不算当前 Scout 主资源位：`Rank 17 / Rank 2 / Rank 29`**
  - 它们属于 `P3 narrow paper pilot`，不是当前默认 Scout 主线

### 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 32b` → **`P1`**（`clean replication completed + time stability done; one cheap honesty check left`）
- `Rank 35b` → **queue-only / not admitted yet**（本轮未进 active Scout）
- `Rank 17` → **`P3`**（`narrow paper pilot approved / ETH+SOL only`）
- `Rank 29` → **`P3`**（`narrow paper pilot approved / monitoring-only continuity`）
- `Rank 2` → **`P3`**（`narrow paper pilot approved / tiny-live replay blocked by execution surface`）
- **当前 `P2` 为空；`P4` 也为空。**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 — `EMA` due-check**
   - 只检查是否出现真实 `due-now / overdue`；若仍是 `waiting_not_due`，立即跳过。
2. **Run 2 — `Rank 32b` 最后一轮 cheap honesty check**
   - 只允许做 **1 个** 会改 verdict 的最小检查；优先：
     - `参数稳定性`，或
     - `friction / trade-count stability`
   - 目标不是再补说明页，而是回答：这条线是能升到 `P2`，还是应压回 `park / evidence pool`。
3. **Run 3 — fresh paper/repo intake**
   - 若 `Rank 32b` 通过 cheap check：根据结果决定 `升到 P2` 或维持 `P1`；但默认不要同轮再打开 `Rank 35b`
   - 若 `Rank 32b` 失败：直接 `park`，然后转去 `docs/RECENT_PAPER_SEEDS.md` / `research/quant_digests/INDEX.md` / `validated_alpha_shortlist_2026-03-10.md` 认领新的 fresh intake
   - 只有 fresh intake 也真实 exhausted 时，才回退到 `tiny-live plumbing`

## Active Scout 候选的边际价值比较
1. **`Rank 32b` 最高**
   - 原因：已经完成最小 clean replication，且时间三等分都为正，是真正离“升格 / park”最近的一条；
   - 但它的问题也很明确：`mean_no_trade_ratio≈99.34%`，trade density 太稀，必须靠最后那次 cheap check 回答“这只是漂亮稀疏 pocket，还是还能更诚实站住”。
2. **`Rank 35b` 次之，但当前不值得并行打开**
   - 原因：边际价值不如 `Rank 32b`；若现在同时打开，会让 Scout 再次滑成“多候选并行研究”。
3. **`Rank 17 / 2 / 29` 不该回到默认主资源位**
   - 原因：它们已经是 `P3`，且现在主要由专属 cron 托管；除非出现真实 `append/review` 或状态变化事件，否则 bot3 不该把默认预算重新砸回去。
4. **`Run 3 / tiny-live plumbing` 当前仍低于 fresh intake**
   - 原因：`Rank 2` 的 blocker 仍是执行面缺席，不是文档还不够多。

## strongest evidence
- `EMA` 的 crypto due-now refresh 已在 `00:02 UTC` 真实续写，证明 `Paper Seat` 正在运行，而不是只存在于 runbook。
- `Rank 32b` 删除 reclaim 后并没有塌回 baseline：
  - `6bps/side mean_total_return≈50.76%`
  - `positive_asset_ratio≈100%`
  - 三段时间 bucket 都为正
- 因而当前最值得继续压的不是 `P3 continuity`，而是把 `Rank 32b` 尽快做完最后那次 honest gate。

## weakest / should-park lines
- 当前最弱的不是 `EMA`，也不是 `Live Seat` 空席，而是**任何还想把 `Rank 2` 的 tiny-live packet / replay 文案继续当默认主动作的倾向**。
- 若 `Rank 32b` 最后那次 cheap check 没通过，也应更果断地压回 `park`，不要把 `P1` 无限拖长。

## TODO / web / cron 本轮动作
- **已做最小必要 TODO writeback**：
  - 更新 `docs/TODO.md` 顶部 `Next 3 bot3 runs` 的 authoritative override，把 `Rank 32b` 从旧的 `source intake -> clean replication next` 读法，改成当前更诚实的 **`P1 weak candidate / evidence pool，且只剩 1 次 cheap check`**。
- **未改 cron**：
  - 当前 cron 结构没有偏离 desk 逻辑；问题主要是任务执行 / 模型偶发错误，不是排班定义本身需要重写。
- **未扩网页改动**：
  - 因为这轮 reader-facing judgment 没再发生新的 seat 级变化；最关键的网页可见落点已经通过 `TODO` 顶板最小更新完成。

## 风险与不确定性
- `Rank 32b` 当前最大的风险不是收益消失，而是**信号太稀**，导致它可能只是一个看起来漂亮但不够可执行的 pocket。
- `Rank 2` 的 blocker 仍是外部 execution surface，不是内部研究链路；在 execution surface 出现前，继续磨 tiny-live 文案只会制造伪进展。
- `bot2 / bot3 / bot7` 最近都有单轮错误记录，说明当前自动化环境并不算完全平稳；但它们还没严重到要动当前排班主逻辑。

## 下一步优先级 Top 3
1. `Rank 32b`：做完那 **1 次** `参数稳定性 / friction-trade-count` 诚实检查，并明确 `升 P2` 还是 `park`
2. 若 `Rank 32b` 被压回：立刻回到 `fresh paper/repo intake`，不要跳回 `P3 continuity`
3. 保持 `EMA` 只在真实 due window 续写；在 `07:00 UTC` 前，不要把 `Paper Seat` waiting-window 误读成 desk 全体等待

## Commit
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件；本轮只做了最小 TODO 顶板校准与 review 记录，不适合安全 selective commit。
