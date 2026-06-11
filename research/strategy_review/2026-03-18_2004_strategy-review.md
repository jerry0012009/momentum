# 2026-03-18 20:04 UTC — desk review：EMA 继续坐 Paper，Live 继续空，Scout 冻结为 Rank 65 / 66 / 67

## 本轮一句话判断
当前 desk 判断**不翻盘**：**`Paper Seat = EMA`**、**`Live Seat = 暂空`**、**`Scout Seat` 当前主资源位 = `Rank 65 / perp-stress resetComplete / re-arm gate`**。本轮唯一需要做的最小校准，不是改大方向，而是把 queue-facing 里还没编号的两条 fresh-source 后备正式冻结为 **`Rank 66 / exec-TF switch alignment gate`** 与 **`Rank 67 / regime-matrix shared-state gate`**，避免顶部作战板继续用未编号候选。

## 0）本轮检查清单
- 已读：`docs/BOT2_STRATEGY_REVIEW_BRIEF.md`
- 已读：`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 已检查 repo 状态 / 最近 logs / 当前 cron
- 最近 optimization logs（最新）
  - `2026-03-18_2002_ema-us-due-refresh.md`
  - `2026-03-18_1940_rank65-source-intake-guard-passed.md`
  - `2026-03-18_1938_rank64-clean-replication-park.md`
  - `2026-03-18_1919_rank64-source-intake.md`
- 最近 strategy review
  - `2026-03-18_1909_strategy-review.md`
  - `2026-03-18_1824_strategy-review.md`
- 当前关键 cron
  - `bot2-strategy-review-40m`：本轮运行中
  - `bot3-momentum-auto-opt-13m`：正常运行
  - `momentum-narrow-paper-lanes-20m`：正常运行
  - `bot7-quant-digest-30m`：正常运行
  - `bot6-park-reframe-2h`：正常运行

## 1）本轮必须回答的 5 个问题

### 1. 谁坐 `Paper Seat`？
- **`EMA / EMA-PSAR raw alpha focus` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / no due-now`**。
- 证据：`2026-03-18 20:02 UTC` 已真实执行 `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`，并把美股 due window 消化完；最新 `ema_paper_trading_due_guardrail_snapshot.csv` 显示最早只剩 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC（due_soon）`。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 65` 目前只到 **`P1 / guard-passed / admit_to_clean_replication_queue`**，还没做最小 clean replication；
  2. `Rank 66 / Rank 67` 还只是 **`P0 fresh-source queue / not admitted`**；
  3. `Rank 2 / 17 / 29 / 32b` 只是 `P3 narrow paper continuity` 托管位，不应误写成 live challenger；
  4. 已被 bench/park 的 `Rank 62 / 63 / 64` 不应再回桌抢占 live 叙事。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位**：`Rank 65 / perp-stress resetComplete / re-arm gate`
  - 来源：`damianpitt/capital41-indicators`
  - 当前阶段：**`guard-passed / admit_to_clean_replication_queue`**
- **当前第一后备**：`Rank 66 / exec-TF switch alignment gate`
  - 来源：`Frosty098/smc-bos-strategy`
  - 当前阶段：**`P0 fresh-source queue / not admitted`**
- **当前第二后备**：`Rank 67 / regime-matrix shared-state gate`
  - 来源：`damianpitt/capital41-indicators`
  - 当前阶段：**`P0 fresh-source queue / not admitted`**
- **当前不应再写成 active Scout 主线的对象**
  - `Rank 64 / pullback-quality score gate`：已 `park / evidence pool`
  - `Rank 63 / 62 / 61 / 60 / 59 / 58 / 57 / 55`：已 `park / evidence pool`
  - `Rank 56`：`P1 weak candidate / evidence pool`
  - `Rank 2 / 17 / 29 / 32b`：`P3 narrow paper continuity`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 65 / perp-stress resetComplete / re-arm gate`** → **`P1 weak candidate`**（`guard-passed / admit_to_clean_replication_queue`）
- **`Rank 66 / exec-TF switch alignment gate`** → **`P0 fresh-source queue / not admitted`**
- **`Rank 67 / regime-matrix shared-state gate`** → **`P0 fresh-source queue / not admitted`**
- **`Rank 56 / liquidation-map path overlay`** → **`P1 weak candidate / evidence pool`**
- **`Rank 2 / Rank 17 / Rank 29 / Rank 32b`** → **`P3 narrow paper continuity`**
- 当前 **`P2` 为空，`P4` 为空**。

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = `EMA due-check only`**（优先盯 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`）
2. **Run 2 = 若 `EMA` 仍无新的 `due-now / overdue`，立刻给 `Rank 65` 做 1 次最小 clean replication**
3. **Run 3 = 若 `Rank 65` minimal clean replication 后仍不能给出更高层 verdict，则回到 fresh source 比较 `Rank 66 > Rank 67`；只有这一层也 exhausted 时，才回退到 `Rank 35b > Rank 16b > tiny-live plumbing`**

## 当前 strongest evidence
- `EMA` 的 `20:00 UTC` due window 已在 `20:02 UTC` 被真实消化，不是纸面 waiting。
- 最新 due guardrail 明确显示：`Crypto -> 2026-03-19 00:00 UTC（due_soon）`、A 股三条 lane `-> 2026-03-19 07:00 UTC`、美股 `-> 2026-03-19 20:00 UTC`。
- `manual_narrow_paper_last_run_summary.json @ 2026-03-18T20:00:14Z` 仍是 `new_closed_trades_appended=0`，说明 `P3 continuity` 当前没有 status-changing event。
- `Rank 65` 已完成 source intake + 两条轻量诚实守门，并已明确写成 `guard-passed / admit_to_clean_replication_queue`；它比直接切到新的 fresh source 更接近下一次 hard verdict。

## 当前 weakest / should-not-overweight lines
- 最不该做的是把 `Rank 65` 过早写成可升格的 `Live Seat` 候选；它还没过 clean replication。
- 也不该继续让 queue-facing 顶板里出现未编号的 fresh-source 候选；这会让 board 的 seat 判断失去统一口径。
- 同样不该回头重炒 `Rank 63 / 64`：它们已经在允许预算内给出更诚实的 `park` verdict。
- `Rank 2 / 17 / 29 / 32b` 仍只是 `P3` 托管 continuity；在 `new_closed_trades_appended=0` 时不应抢主资源。

## 建议优先级 Top 1~3
1. **先把 `Rank 65` 的唯一那手最小 clean replication 做掉，并直接给出 `P2 / park` 倾向。**
2. **若 `Rank 65` 不成立，再切到 `Rank 66 / exec-TF switch alignment gate`，不要跳过编号直接写泛泛 fresh pool。**
3. **保持 `Live Seat = 暂空`，直到出现至少一个完成 clean replication 且没有硬爆雷的候选。**

## TODO / roadmap / web / cron 的改动或建议
- **本轮对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做了最小必要刷新。**
- 已同步：
  - 新增 `2026-03-18 20:04 UTC` desk-review 补充；
  - 正式冻结 **`Rank 66 / exec-TF switch alignment gate`**；
  - 正式冻结 **`Rank 67 / regime-matrix shared-state gate`**；
  - 把当前 active Scout 顺序与 `Run 3` 写回成 **`Rank 65 > Rank 66 > Rank 67`** 的编号口径。
- 本轮**未改 cron**。
- 本轮应同步刷新 `plans/momentum_todo.html` 与首页 index。

## 风险与不确定性
- `Rank 65` 当前仍只是 public proxy 级的 perp-stress 定义；若 clean replication 主要靠砍样本而不是减少 after-stress 误判，应快速 `park`。
- `Rank 66 / Rank 67` 仍未进入 source-intake；当前只是 queue-facing 备选，不是已验证候选。
- 工作区仍有大量无关脏文件 / 未跟踪文件，本轮不安全 selective commit。

## 执行备注
- 本轮席位判断**无变化**，但 `Scout Seat` 的 queue-facing 口径更规范了：从“未编号 fresh-source 描述”收紧成 **`Rank 65 / 66 / 67`**。
- 因此本轮已同步更新 `TODO` 顶部作战板；接下来刷新 `plans/momentum_todo.html`、首页 index，并发送邮件摘要。
- 未提交 git。
