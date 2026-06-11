# 2026-03-18 22:27 UTC — desk review：EMA 继续坐 Paper，Live 继续空，Scout 切到 Rank 69 / IVU fast lane

## 本轮一句话判断
当前 desk verdict 需要跟上过去 40 分钟内的两次真实写回：**`Rank 68` 已在最小 clean replication 后压回 `park / evidence pool`，`Rank 69 / IVU opening-volume uncertainty gate` 已完成 `source intake + 两条轻量诚实守门` 并进入 `guard-passed / admit_to_clean_replication_queue`**。因此本轮更诚实的排兵布阵是：**`Paper Seat = EMA`**、**`Live Seat = 暂空`**、**`Scout Seat` 主资源位 = `Rank 69`**；若 `EMA` 继续 `waiting_not_due`，bot3 应先把 `Rank 69` 的唯一那手 minimal clean replication 做掉，而不是回头挤占 `P3 continuity`。

## 0）本轮检查清单
- 已读：`docs/BOT2_STRATEGY_REVIEW_BRIEF.md`
- 已读：`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- 已检查 repo 状态：`git status --short --branch` 仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮不混提、不做 selective commit
- 最近 optimization logs（最新）
  - `2026-03-18_2223_rank69-ivu-source-intake.md`
  - `2026-03-18_2207_rank68-clean-replication-park.md`
  - `2026-03-18_2130_rank67-regime-matrix-park.md`
  - `2026-03-18_2050_rank66-clean-replication.md`
- 最近 strategy review
  - `2026-03-18_2140_strategy-review.md`
  - `2026-03-18_2052_strategy-review.md`
  - `2026-03-18_2004_strategy-review.md`
- 当前关键 cron
  - `bot2-strategy-review-40m`：本轮运行中
  - `bot3-momentum-auto-opt-13m`：正常运行
  - `momentum-narrow-paper-lanes-20m`：正常运行
  - `bot7-quant-digest-30m`：正常运行
  - `bot6-park-reframe-2h`：当前启用，但最近一次报错为 `rg: command not found`；与本轮 seat judgment 无直接冲突，先不混改
- 当前 `EMA due guardrail`
  - `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC / waiting_not_due`
  - 美股 `1d+1wk -> 2026-03-19 20:00 UTC / waiting_not_due`
- 当前 `P3 continuity`
  - `reports/artifacts/manual_narrow_paper_lanes/manual_narrow_paper_last_run_summary.json @ 2026-03-18T21:54:20Z`
  - `new_closed_trades_appended = 0`
  - 当前没有新的 `P3 status-changing event` 值得 bot3 回头抢主资源

## 1）本轮必须回答的 5 个问题

### 1. 谁坐 `Paper Seat`？
- **`EMA / EMA-PSAR raw alpha focus` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due（Crypto lane due_soon）`**。
- 证据：最新 `ema_paper_trading_due_guardrail_snapshot.csv` 里仍没有 `due-now / overdue` lane，最早只剩 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 69` 目前只到 **`P1 weak candidate / guard-passed / admit_to_clean_replication_queue`**，还没过 minimal clean replication；
  2. `realized-vol mid-band` 与 `PSAR close-confirmed follow-up` 目前都还只是 fresh source，不是已 admitted 候选；
  3. `Rank 68 / 67 / 66 / 65` 当前都更诚实地属于 `evidence pool`；
  4. `Rank 2 / 17 / 29 / 32b` 仍是 `P3 narrow paper continuity` 托管位，不应误写成 live challenger。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前主资源位**：`Rank 69 / IVU opening-volume uncertainty gate`
  - 来源：`Yang & He (2026)`
  - 定位：给 `breakout-short / Fib retest_hold / EMA-PSAR` 三条主线加一个 shared continuation allow/deny / size haircut gate
  - 当前阶段：**`P1 weak candidate（guard-passed / admit_to_clean_replication_queue）`**
- **当前第一 fresh-source 后备**：`realized-vol mid-band cost-survival gate`
  - 来源：`Svogun & Bazán-Palomino (2022)` + 本地 `Rank 23` pocket evidence
  - 定位：给三条主线做 shared `allow/deny` vol gate
  - 当前阶段：**`P0 fresh-source pool / not admitted`**
- **当前第二 fresh-source 后备**：`PSAR close-confirmed follow-up gate`
  - 来源：`0xeth-drc-888 / PSAR Strategy on close`
  - 定位：把 `PSAR flip` 改写成 `close-confirmed + 第 N 根 trend bar` 的 follow-up gate，服务 `EMA / breakout-short`
  - 当前阶段：**`P0 fresh-source pool / not admitted`**
- **当前不应继续写成 active fast-lane 主线的对象**
  - `Rank 68 / block-mitigation retest score`：已在允许预算内给出 **`park / evidence pool`**
  - `Rank 67 / regime-matrix shared-state gate`：已在允许预算内给出 **`park / evidence pool`**
  - `Rank 66 / exec-TF switch alignment gate`：已完成 minimal clean replication，当前更诚实的身份是 **`P1 weak candidate / evidence pool`**
  - `Rank 65 / perp-stress resetComplete / re-arm gate`：保留 **`evidence pool`**
  - `Rank 35b / Rank 16b`：fallback queue
  - `Rank 2 / 17 / 29 / 32b`：`P3 narrow paper continuity`

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 69 / IVU opening-volume uncertainty gate`** → **`P1 weak candidate`**（`guard-passed / admit_to_clean_replication_queue`）
- **`realized-vol mid-band cost-survival gate`** → **`P0 fresh-source pool / not admitted`**
- **`PSAR close-confirmed follow-up gate`** → **`P0 fresh-source pool / not admitted`**
- **`Rank 68 / 67 / 66 / 65`** → **`evidence pool`**（其中 `Rank 66` 保留 `P1 weak candidate` 痕迹，但当前不再占 fast lane）
- **`Rank 2 / Rank 17 / Rank 29 / Rank 32b`** → **`P3 narrow paper continuity`**
- 当前 **`P2` 仍空、`P4` 仍空**。

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = `EMA due-check only`**（继续盯 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC / due_soon`）
2. **Run 2 = 若 `Rank 69` 已 guard-passed 且 `EMA` 仍 `waiting_not_due`，立刻给 `Rank 69` 1 次最小 clean replication**
3. **Run 3 = 若 `Rank 69` clean replication 后仍不能升到更高层 verdict，则优先回到 fresh source 比较 `realized-vol mid-band > PSAR close-confirmed follow-up`；只有 fresh source 这一层也 exhausted 时，才回退到 `Rank 35b > Rank 16b > tiny-live plumbing`**

## 2）当前 active Scout 边际价值比较（必须显式比较）
1. **`Rank 69 / IVU opening-volume uncertainty gate` 当前最高**
   - 已完成 `source intake + 两条轻量诚实守门`，离下一次硬 verdict 最近；
   - 只依赖现有 `15m OHLCV volume`，实验摩擦低；
   - 直接服务 `breakout-short / Fib retest_hold / EMA-PSAR` 三条主线，而且比继续写泛波动过滤层更不重叠。
2. **`realized-vol mid-band cost-survival gate` 第二**
   - paper 证据更完整，也有本地 pocket anchor；
   - 但和已 park 的 `Rank 23` 波动轴更近，如果最后只是靠砍样本换改善，就很容易再次滑回复读旧问题；
   - 因此现在更适合做 `Rank 69` 之后的下一条 fresh-source，而不是跳过它抢主资源。
3. **`PSAR close-confirmed follow-up gate` 第三**
   - repo 规则很清楚，也很贴 `EMA / breakout-short`；
   - 但证据级别与泛化面暂弱于前两条，更像“角色澄清 / follow-up gate”，不是当前更该优先冻结的 shared paper candidate。
4. **`Rank 35b` 第四、`Rank 16b` 第五**
   - 两条都仍只是 fallback，不该在 fresh paper/repo queue 还有对象时抢主资源。
5. **`tiny-live plumbing` 继续最末位**
   - 当前既没有 promoted live challenger，也没有新的 tiny-live 执行变化值得前置。

## 3）当前 strongest evidence
- `Paper Seat / EMA` 当前仍是 **`running paper / waiting_not_due`**，下一次最早 due 点明确是 `Crypto 1d+1wk -> 2026-03-19 00:00 UTC`。
- `manual_narrow_paper_last_run_summary.json @ 21:54:20Z` 仍是 `new_closed_trades_appended=0`，说明 `P3 continuity` 当前没有 status-changing event。
- `Rank 68` 已在最小 clean replication 后明确压回 **`park / evidence pool`**，不应继续霸占 fast lane。
- `Rank 69` 已在 `22:23 UTC` 完成 `guard-passed`，当前是离下一次硬 verdict 最近的 fresh paper candidate。

## 4）当前 weakest / should-not-overweight lines
- 最不该做的是在 `Rank 69` 已经 admitted 到 clean-replication queue 后，还让 bot3 回头做 `P3 continuity` 或 generic maintenance。
- 也不该因为 `realized-vol` 与 `PSAR close-confirmed` 两条 fresh digest 很顺手，就在 `Rank 69` 还没跑第一手验证前再次改写 fast-lane 头部。
- 同样不该把 `Rank 66` 误写成仍在 active fast lane：它现在更诚实的身份只是 `evidence pool`。
- `Live Seat` 也不该为了“桌上必须有 challenger”而强行补位。

## 5）本轮最值得的 Top 3 动作
1. **先把 `Rank 69 / IVU opening-volume uncertainty gate` 的唯一那手 minimal clean replication 做掉，并直接给出 `P2 / park` 倾向。**
2. **若 `Rank 69` 不成立，优先把 `realized-vol mid-band` 冻结成下一条 queue-facing fresh source，再做 intake。**
3. **若 `realized-vol mid-band` 也不够诚实，再比较是否值得把 `PSAR close-confirmed follow-up` 收进 queue；只有这层也不成立时，才回退到 `Rank 35b / Rank 16b / tiny-live plumbing`。**

## 6）TODO / 网页 / cron 的改动或建议
- **本轮对 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 做了最小必要刷新。**
- 已同步：
  - 新增 `2026-03-18 22:27 UTC，bot2 desk review` 补充；
  - 显式冻结当前席位判断：`Paper Seat = EMA`、`Live Seat = 暂空`；
  - 把 active Scout 顺序收紧为 **`Rank 69 > realized-vol mid-band > PSAR close-confirmed > Rank 35b > Rank 16b > tiny-live plumbing`**；
  - 把 `Next 3` 收紧为 **`Rank 69 minimal clean replication -> fresh source 比较 -> fallback`**。
- 已刷新 reader-facing 页面：`reports/site/plans/momentum_todo.html`
- 本轮**未改 cron**。

## 7）风险与不确定性
- `Rank 69` 原论文样本是中国股票 `30m`，不是 crypto `15m`；若 clean replication 发现改善主要来自“砍单换胜率”，应快速 `park`。
- `realized-vol mid-band` 虽有 paper 背书，但也最容易退化成“把交易数砍掉后看起来更稳”的 shared gate。
- `PSAR close-confirmed follow-up` 很可能能澄清 `EMA / breakout-short` 的角色，但当前证据还不足以让它越过前两条。
- 工作区仍有大量无关脏文件 / 未跟踪文件；本轮不安全 selective commit。

## 8）执行备注
- 本轮属于 **有变化巡检**：相较上一轮 bot2 review，当前 `Scout Seat` 已从 `Rank 68` 切换到 `Rank 69`，并且 `Next 3` 顺序已经发生变化。
- 因此本轮已把变化写回 `TODO` 顶板，并同步刷新 `momentum_todo.html`。
- 接下来继续刷新首页 index，并发送邮件摘要。
- 未提交 git。
