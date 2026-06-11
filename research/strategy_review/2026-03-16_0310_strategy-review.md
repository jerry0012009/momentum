# 2026-03-16 03:10 UTC · Light Strategy Review

## 本轮一句话判断

当前主排序仍不变：**`EMA = closest to paper`，`breakout = one_more_gate`，`Fibonacci = park`**。但和前两轮相比，这轮最该动的一刀已经不是再重复说“继续等真实 close”，而是把 **Paper/Live 同时被时钟或 cooldown 卡住时的 `Run 3` fallback 写得更硬**，避免 bot3 在明明还有 Scout / tiny-live plumbing 可做时，继续连续多轮只交 `NO_PROGRESS`。

## 本轮先检查了什么

1. repo 状态与当前 worktree
   - `git status --short --branch` 显示当前仓库仍有大量历史未跟踪产物，但这轮只碰最小必要文件。
2. 当前 cron 列表
   - `bot3-momentum-auto-opt-13m`：运行中
   - `bot2-strategy-review-40m`：正常
   - `bot7-quant-digest-4h`：当前正常
3. 最近研究推进
   - 最近几条 strategy review 仍持续维持同一判断：EMA 等真实 close、breakout 维持 one_more_gate。
   - 最近 optimization loop 里，`2026-03-16_0002_ema-crypto-close-refresh-append.md` 已给 EMA 落下首条非 seed 的真实 completed-bar history 续写；`2026-03-16_0255_breakout-homepage-cooldown-guard.md` 已把 breakout rerun 收紧到 cooldown hold；`2026-03-16_0302_no-progress.md` 则再次确认：当前 A 股日频还没到点、breakout 也仍在 rerun cooldown。
4. 关键网页入口
   - `alpha_closure_board` 与首页 deployment watch 仍一致写成：EMA closest to paper，breakout one_more_gate，Fibonacci park。
5. 自动化方向一致性
   - `AUTO_OPTIMIZATION_LOOP.md` 明确要求：Paper Seat 被 market clock 卡住时应切到 Live，再切到 Scout/Tiny-live plumbing，而不是在 waiting window 空转。
   - `RESEARCH_AUTOMATION_BRIEF.md` 也已明确：研究/digest 只是 Scout Seat 辅助，不得反客为主压过 Paper/Live。

## 当前 strongest evidence

### 1) EMA 仍是最接近进入 paper trading 的对象

- closure board 与首页都仍一致写成 `closest to paper`；
- EMA 线已经有 `candidate spec / operating spec / monitoring board / runbook / day-0 ledger snapshot / refresh history`；
- 最近一次真实推进已经把 `Crypto 1d+1wk` 追加成首条非 seed 的 completed-bar history；
- 当前最缺的不是新说明页，而是 **沿同一张 ledger 连续落下下一轮真实 market-close refresh / week-1 review**。

所以 `Paper Seat` 继续由 EMA 占着，没有替换理由。

### 2) breakout 仍是最接近 tiny-live review 的 challenger，但 hard gate 还没清

- 最近 fresh rerun 与 cooldown guard 没有改写核心 blocker；
- 当前更诚实的写法仍是 `up-flat biased conditional alpha / one_more_gate`；
- 最硬缺口仍然没变：`pure down coverage = 0`、`pre-down bridge coverage = 0`，也就是 **还没有足够证据证明这条 sizing candidate 能诚实穿过最关键的 crypto stress pocket**。

因此 breakout 还是 Live Seat challenger，但还没到可写 `tiny-live review ready`。

### 3) Fibonacci 继续只是 archive/filter，不应抢主资源

这一轮没有任何新证据能把它从 `archive / optional filter` 拉回 active seat。

## 当前 weakest / should-park lines

- **最该继续收着的是 Fibonacci**：没有 deployment-facing 新价值，不该再回升优先级。
- **breakout 当前最该避免的是同样本重复 rerun**：在 cooldown 里继续重跑 heavy refresh，只会重复旧 blocker，不会新增 overturn evidence。

## 这轮为什么必须小动一下，而不是继续“不改”

前两轮 bot2 的“不改”是合理的，因为需要先确认：
- EMA 的 waiting-window guardrail 健康；
- breakout 的 cooldown guard 已落地；
- 首页与 closure board 没有乱漂。

但到这一轮，新的问题已经浮出来了：
- `AUTO_OPTIMIZATION_LOOP` 说 blocked 时应切 seat；
- `TODO` 顶部也写了 `Run 3 = Tiny-live plumbing 或 Scout Seat`；
- 可实际近几轮仍出现 `NO_PROGRESS`，说明 **Run 3 fallback 还不够具体，不足以稳定驱动 bot3 在双阻塞窗口里做出结果导向的小步**。

所以这轮最有杠杆的小调整，不是再改排序，而是把 `Run 3` 写成更具体的 fallback 约束。

## 本轮最小必要改动

### 已改：`docs/TODO.md`

在顶部 `TRADING DESK BOARD -> Next 3 bot3 runs -> Run 3` 下新增明确约束：

- 若 `EMA` 明确处于 `waiting_not_due`，且 breakout 同时落在 `rerun cooldown / no fresh overturn evidence`；
- **不要连续多轮只交 `NO_PROGRESS`**；
- 默认至少交付下面二选一：
  1. 一张 `Scout Seat shortlist card`（优先 `crypto 5m/15m`、`breakout / confirmation`、且尽量满足 `全文可得 + 有代码/可 clean-room`）
  2. 一张 `tiny-live plumbing` 最小清单（`capital cap / kill-switch / live ledger fields / mismatch guardrail`）

这刀的目标不是新开大分支，而是把 waiting/cooldown 窗口里的 fallback 变成**更可执行的 desk 行为**。

### 这轮不改

- 不改 `Paper Seat / Live Seat / Scout Seat` 排位
- 不改 `alpha_closure_board` 主排序文案
- 不改 cron 频率
- 不改 bot7 方向

原因：当前真正偏差不在席位判断，而在 **双阻塞窗口里的 fallback 任务过于抽象**。

## 下一步优先级 Top 1~3

### Top 1. EMA：继续等真实 next close，到点后先沿 ledger 续写

默认入口仍是：
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

下一次真实推进，仍优先看：
1. `创业板ETF 1d` primary 是否继续守住；
2. front-queue secondary 是否要 `keep / stricter recheck / demote`；
3. week-1 review 是否首次出现 `yellow / red`。

### Top 2. breakout：cooldown 走完后最多再做一次 heavy rerun 检查

前提是：
- cache 仍领先；
- 且 rerun 不再只是重复旧 blocker。

否则继续维持 `one_more_gate / up-flat biased conditional alpha`。

### Top 3. 双阻塞窗口里，优先让 Run 3 真正落地

若 EMA 还没到点、breakout 还在 cooldown，下一轮 bot3 默认应从下面二选一：
1. `Scout Seat shortlist card`
2. `tiny-live plumbing` 最小清单

而不是继续只报 `NO_PROGRESS`。

## 网页 / 表达建议

- `alpha_closure_board` 与首页当前已经足够诚实，不需要再改主排序。
- 这轮真正该更新的是 `plans / TODO` 镜像，让网页也能看到新的 `Run 3 fallback` 约束。
- `bot7` 当前更适合作为 **Scout Seat 辅助引擎** 继续保留，不需要为了这轮去改频率或换主题。

## cron / 节奏建议

- `bot2 40m`：不改
- `bot3 13m`：不改频率，但现在有了更硬的 Run 3 fallback 约束
- `bot7 4h`：不改，继续当 Scout Seat 辅助，不抢 Paper/Live 主资源

## paper trading admission verdict

- **closest to paper：EMA baseline family**
  - 当前最缺的 gate：**连续 `market-close refresh / week-1 review` 的 forward honesty**
- **closest to tiny-live review：support_breakout_v0**
  - 当前最缺的 live gate：**`paper/live mismatch honesty` 仍未过**；因为 default policy 还没有非零 `pure down / pre-down bridge` coverage，不能诚实假设它在 crypto stress pocket 里可直接迁移
- **park：Fibonacci**

## 风险与不确定性

1. 这轮改的是 fallback 调度质量，不是新增 alpha 证据本身。
2. 若后续 bot3 在双阻塞窗口里仍持续只交 `NO_PROGRESS`，说明还需要进一步把 `Scout Seat` 或 `tiny-live plumbing` 拆成更具体的可认领条目。
3. 若 EMA 很快进入连续 due-now refresh，或 breakout 拿到真正新的 down-tail forward 命中，这轮新加的 Run 3 约束就会自动退居次位。

## 本轮一句话结论（给 Jerry）

**主排序不变，但这轮我还是动了一刀：把 TODO 顶部的 `Run 3` fallback 写得更具体，避免 bot3 在 EMA waiting + breakout cooldown 的双阻塞窗口里继续空转；接下来仍然是 EMA 最接近 paper，breakout 最接近 tiny-live review，但它最缺的 live gate 仍是 `paper/live mismatch honesty`。**
