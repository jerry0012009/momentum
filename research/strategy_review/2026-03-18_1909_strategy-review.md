# 2026-03-18 19:09 UTC — desk review：EMA 继续坐 Paper，Live 继续空，Scout 切到 Rank 64 / CQI

## 本轮一句话判断
当前 desk 的大席位判断**没有翻盘**：**`Paper Seat = EMA`**、**`Live Seat = 暂空`** 继续成立；但在 `Rank 63 / Fib 0.618 hold / 0.5 fail gate` 已于本窗口给出 **`park / evidence pool`** 后，`Scout Seat` 不能停在“generic fresh pool”这种模糊写法里，因此本轮做了最小必要校准：把 **`pullback-quality / CQI`** 正式冻结为 **`Rank 64 / pullback-quality score gate`**，并把下一手默认顺序收紧成 **`Rank 64 source intake -> Rank 64 minimal clean replication -> 失败后再切 perp-stress / exec-TF switch / regime-matrix`**。

## 0）本轮检查清单
- 已读：`docs/BOT2_STRATEGY_REVIEW_BRIEF.md`
- 已读：`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：`git status --short --branch` 仍有大量与本轮无关的既有脏文件 / 未跟踪产物；本轮不混提。
- 最近 optimization logs（目录里最新）
  - `2026-03-18_1854_rank63-source-intake-guard-passed.md`
  - `2026-03-18_1830_rank62-clean-replication-park.md`
  - `2026-03-18_1813_rank62-source-intake.md`
  - `2026-03-18_1800_rank61-clean-replication-park.md`
- 最近 strategy review
  - `2026-03-18_1824_strategy-review.md`
  - `2026-03-18_1744_strategy-review.md`
  - `2026-03-18_1651_strategy-review.md`
- 最近 quant digest（fresh pool 对比所需）
  - `2026-03-18_1845_perp-stress-reset-complete-rearm-gate.md`
  - `2026-03-18_1730_exec-tf-switch-alignment-gate.md`
  - `2026-03-18_1707_regime-matrix-shared-state-gate.md`
  - `2026-03-18_1151_pullback-quality-score-gate.md`
- 当前关键 cron
  - `bot2-strategy-review-40m`：本轮运行中
  - `bot3-momentum-auto-opt-13m`：正常运行
  - `momentum-narrow-paper-lanes-20m`：正常运行
  - `bot7-quant-digest-30m`：正常运行
  - `bot6-park-reframe-2h`：正常运行
- `EMA due guardrail` 当前仍全为 `waiting_not_due`
  - 美股 `1d+1wk -> 2026-03-18 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-19 00:00 UTC`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json @ 2026-03-18T18:50:50Z`
  - `new_closed_trades_appended=0`
  - 当前没有新的 `P3 status-changing event` 值得让 bot3 抢回 continuity
- `Rank 63` 额外核对
  - 虽然 `research/optimization_loop/` 目录里尚未看到单独的 `19:09` 日志文件，但 `reports/artifacts/scout_rank63_fib0618_hold05_fail_15m/overall_summary.csv` 与对应 reader-facing 页面已落地，`docs/TODO.md` 也已写回 `park / evidence pool`，证据已足够把 `Rank 63` 视为退出 active Scout fast-lane

## 1）本轮必须回答的 5 个问题

### 1. 谁坐 `Paper Seat`？
- **`EMA / EMA-PSAR raw alpha focus` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 当前 blocker 仍只是 market clock，不是执行漂移：最新 `due guardrail` 里没有新的 `due-now / overdue` lane。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 63` 已在最小 clean replication 后压回 `park / evidence pool`；
  2. 新的主资源位 `Rank 64 / pullback-quality score gate` 现在还只配拿 `source intake + 两条轻量诚实守门`，远没到 `clean replication` 或 `Light Stability Pack` 之后的升格窗口；
  3. `Rank 2 / 17 / 29 / 32b` 仍是 `P3 narrow paper continuity` 托管位，不应误写成新的 live challenger；
  4. 当前规则明确允许 `Live Seat` 为空，不能为了“桌上必须有 live challenger”而抬升未过 gate 的线。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位**：`Rank 64 / pullback-quality score gate`
  - 来源：`nirujan123/Pullback-Quality-Strategy`
  - 定位：把 `Fib retest_hold / breakout-short follow-up / EMA-PSAR continuation` 统一收敛到一个 `trend / zone / volume / trigger` 的 shared score skeleton
  - 当前阶段：**`source intake / 两条轻量诚实守门 next`**
- **当前第一后备**：`perp-stress resetComplete / re-arm gate`
  - 来源：`damianpitt/capital41-indicators`
  - 定位：shared post-squeeze reset / re-arm gate
  - 当前阶段：fresh-source queue / 未 admitted
- **当前第二后备**：`exec-TF switch alignment gate`
  - 来源：`Frosty098/smc-bos-strategy`
  - 定位：`4H/1H` 同向时 `5m` 提前点火、否则退回 `15m` 的 shared execution gate
  - 当前阶段：fresh-source queue / 未 admitted
- **当前第三后备**：`regime-matrix shared-state gate`
  - 来源：`damianpitt/capital41-indicators`
  - 定位：给三条主线做 shared allow/deny state gate
  - 当前阶段：fresh-source queue / 未 admitted
- **明确不该再写成 active Scout 主线的对象**
  - `Rank 63`：已 park
  - `Rank 62 / 61 / 60 / 59 / 58 / 57 / 55`：已 park
  - `Rank 56`：`P1 weak candidate / evidence pool`
  - `Rank 2 / 17 / 29 / 32b`：P3 托管 continuity，不是当前 Scout 主资源位

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 64 / pullback-quality score gate`** → **`P1 weak candidate`**（`source intake / 两条轻量诚实守门 next`）
- **`perp-stress resetComplete / re-arm gate`** → **`P0 fresh-source queue / not admitted`**（外部数据摩擦更高）
- **`exec-TF switch alignment gate`** → **`P0 fresh-source queue / not admitted`**
- **`regime-matrix shared-state gate`** → **`P0 fresh-source queue / not admitted`**
- **`Rank 56 / liquidation-map path overlay`** → **`P1 weak candidate / evidence pool`**
- **`Rank 57 / 58 / 59 / 60 / 61 / 62 / 63`** → **`P0 park / evidence pool`**
- **`Rank 2 / Rank 17 / Rank 29 / Rank 32b`** → **`P3 narrow paper continuity`**
- 当前 **`P2` 为空，`P4` 为空**。

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = `EMA due-check only`**
2. **Run 2 = 若 `EMA` 仍 `waiting_not_due`，立刻给 `Rank 64 / pullback-quality score gate` 做 `source intake + 两条轻量诚实守门`**
3. **Run 3 = 若 `Rank 64` 已 `guard-passed`，立刻给它 1 次最小 clean replication；若 `Rank 64` 这轮直接 hard fail / exhausted，则切去比较 `perp-stress resetComplete / re-arm gate > exec-TF switch alignment gate > regime-matrix shared-state gate`；只有这层也 exhausted 时，才回退到 `Rank 35b > Rank 16b > tiny-live plumbing`**

## 2）当前 active Scout 边际价值比较
1. **`Rank 64 / pullback-quality score gate` 当前最高**
   - 它最直接回答当前 desk 的真实缺口：`retest_hold` 不能继续写成碰到位就算守住，`EMA / PSAR` 也不该继续单扛 entry；
   - 它仍是 paper / repo based 且只依赖公开 OHLCV，迁移摩擦低于 perp/OI 路线；
   - 虽然更像 shared score skeleton，但当前问题是“怎么更诚实地给回踩/延续定义”，这比再加一个单轴 veto 更贴眼下缺口。
2. **`perp-stress resetComplete / re-arm gate` 次高**
   - 题目对三条主线都相关，但它需要 `spot + perp + OI + liquidation-wick proxy`，首轮数据摩擦明显高于 `Rank 64`；
   - 更适合作为 `Rank 64` 若 hard fail 后的下一手，而不是直接抢当前主资源位。
3. **`exec-TF switch alignment gate` 第三**
   - 规则清楚、数据便宜，是不错的 next-source；
   - 但它更偏 execution layer，而不是当前最急需的 `hold / fail / quality` 诚实定义。
4. **`regime-matrix shared-state gate` 第四**
   - 价值在 shared allow/deny layer；
   - 但它和今天较早的 squeeze / regime 语言有信息重叠，当前没必要优先于更直接的 `Rank 64` / `perp-stress` / `exec-TF switch`。
5. **`P3 continuity` 继续只保留低频托管位**
   - 当前没有 closed-trade append、weekly review row 或明显异常，不该抢走 Scout 主资源。

## 3）当前 strongest evidence
- `EMA due guardrail` 仍全为 `waiting_not_due`，说明 `Paper Seat` 当前只是被 market clock 卡住，不是执行掉线。
- `manual_narrow_paper_last_run_summary.json @ 18:50:50Z` 仍是 `new_closed_trades_appended=0`，说明 narrow-paper 托管位此刻没有状态变化，不值得抢占主资源。
- `Rank 63` 的 clean-replication artifact 与页面已经落地，而且主臂在 `6bps/side` 下仍是 `0/3` 资产为正，因此把它压回 `park / evidence pool` 是当前更诚实的 desk 读法。
- 当前 fresh pool 里，`CQI` 比其它备选更直接解决“回踩/延续如何写成更诚实的 through/fail / quality skeleton”这个真实缺口。

## 4）当前 weakest / should-not-overweight lines
- 最不该做的是继续把 `Rank 63` 写成还值得续命的 active Scout：它已经给出 hard fail。
- 也不该因为 `perp-stress` / `exec-TF switch` / `regime-matrix` 都各自有道理，就同时开多条 source intake；这会把 Scout 再次放大成泛研究入口。
- 同样不该把 `Rank 2 / 17 / 29 / 32b` 这些 `P3` 托管位重新写成新 seat；它们只是 continuity 托管层。
- 更不该因为 `EMA` 还没到下一根 bar，就把 bot3 导回 `NO_PROGRESS` 或低杠杆维护。

## 5）本轮最值得的 Top 3 动作
1. **把 `Rank 64 / pullback-quality score gate` 的 source intake + 两条轻量诚实守门做完，并直接给出 `guard-passed / park`。**
2. **若 `Rank 64` hard fail，立即切到 `perp-stress resetComplete / re-arm gate`，不要在 generic fresh-pool wording 上继续打转。**
3. **继续保持 `Live Seat = 暂空`，直到出现至少一个完成 clean replication 且没有硬爆雷的候选。**

## 6）TODO / 网页 / cron 的改动或建议
- **本轮对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做了最小必要刷新。**
- 已同步：
  - 把 `pullback-quality / CQI` 正式冻结为 **`Rank 64 / pullback-quality score gate`**；
  - 把 active Scout 顺序写成 **`Rank 64 > perp-stress resetComplete / re-arm gate > exec-TF switch alignment gate > regime-matrix shared-state gate`**；
  - 把 `Run 2 / Run 3` 从 generic fresh-pool 回退改成具体的 `Rank 64 source intake -> Rank 64 minimal clean replication -> 失败后切下一个 fresh source`。
- 本轮**未改 cron**。

## 7）风险与不确定性
- `CQI` 本身偏 `4H/Daily long-only`，而且是小 repo；它现在只是更高边际价值的 source intake skeleton，不是已验证候选。
- `perp-stress` 的 shared re-arm 读法虽然直观，但首轮会引入 `OI / basis / wick proxy` 的口径摩擦，因此现在不应抢跑 `Rank 64`。
- `Rank 63` 虽已 park，但当前 `research/optimization_loop/` 目录里没看到独立 `19:09` 日志；这意味着 audit trail 略显不齐。好在 artifact/page/TODO 三处证据已能支撑 desk-level judgment。
- 当前工作区脏文件很多；本轮仍不安全 selective commit。

## 8）执行备注
- 本轮 **席位判断无变化**，但 **Scout 主资源位与下一手排班更具体了**：从 generic `fresh paper/repo intake（优先 CQI）` 收紧到 `Rank 64 / CQI` 的 queue-facing 口径。
- 因此本轮已同步更新 `TODO` 顶部作战板；接下来刷新首页 index 并发送邮件摘要。
- 未提交 git。
