# 2026-03-18 07:20 UTC — bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 `EMA baseline family` 占位且已重新回到 `running paper / waiting_not_due`；`Live Seat` 继续空席；`Scout Seat` 当前最诚实的读法不是“还有 active replication 在跑”，而是 **`Rank 48 / 49` 都已 park，fast-lane 应重置为 fresh intake**，下一手应给 **`Rank 50 / chanlun-pro structural reclaim gate`** 做 `source intake -> guard check`，而不是回头挤 `P3 continuity` 或过早掉到 `Rank 35b`。

## 本轮先检查了什么
- repo 状态：`git status --short --branch`
  - 工作区仍有大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做最小 board writeback、review 记录、todo 页面刷新，不混提。
- 最近 optimization logs（重点）
  - `2026-03-18_0645_rank48-clean-replication-park.md`
    - `Rank 48 / session-range active-hours gate` 已完成唯一那手最小 clean replication，并如实压回 `park / evidence pool`。
  - `2026-03-18_0658_rank49-funding-basis-intake.md`
    - `Rank 49 / funding-basis crowded-long unwind gate` 已完成 fresh intake 与两条轻量诚实守门，进入 `guard-passed / admit_to_clean_replication_queue`。
  - `2026-03-18_0701_ema-ashare-due-followup.md`
    - `EMA` 的 A 股 `07:00 UTC` due-now refresh 已被真实消化；`ema_paper_trading_refresh_history.csv` 累计到 `15` 条，due guardrail 回到无 `due-now / overdue` lane。
  - `2026-03-18_0712_rank49-clean-replication-park.md`
    - `Rank 49` 的唯一那手最小 clean replication 已完成，并如实压回 `park / evidence pool`。
- 最近 strategy review
  - `2026-03-18_0632_strategy-review.md`
    - 当时把 `Rank 48` 视作 active fresh Scout 主资源位；到当前窗口，这个判断已过期，因为 `Rank 48 / 49` 都已按允许预算完成并 park。
- 当前 cron 列表（重点）
  - `bot3-momentum-auto-opt-13m`：健康，最近真实执行了 `Rank 48 park -> Rank 49 intake -> EMA due follow-up -> Rank 49 park`。
  - `momentum-narrow-paper-lanes-20m`：健康，`manual_narrow_paper_last_run_summary.json @ 06:59:32Z` 显示 `new_closed_trades_appended=0`，当前无新的 `P3 status-changing event`。
  - `bot7-quant-digest-30m`：健康，最近新增了 `2026-03-18 06:54 UTC` 的 `chanlun second-buy structural reclaim gate` digest，可作为 fresh repo source。
  - `bot6-park-reframe-2h`：健康，仍只做低频 derived queue，不改变当前主席位。

## Desk verdict（必须回答的 5 个问题）

### 1. 谁坐 `Paper Seat`？
- **`EMA baseline family / EMA-PSAR raw alpha`**。
- 当前状态：**`running paper / waiting_not_due`**。
- 直接证据：`2026-03-18 07:01 UTC` 已真实执行 A 股 due-now refresh；最新 `ema_paper_trading_due_guardrail_snapshot.csv` 显示：
  - 美股 `-> 2026-03-18 20:00 UTC`
  - Crypto `-> 2026-03-19 00:00 UTC`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC`
- 结论：当前不应再重复 A 股 refresh，而应恢复 `EMA due-check only + Scout Seat` 的正常排班。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 理由：
  1. 当前没有任何候选走到 `P4 tiny-live review candidate`；
  2. `Rank 2 / Rank 17 / Rank 29 / Rank 32b` 都只是 `P3 narrow paper pilot` 托管位，不是 live challenger；
  3. `Rank 48 / 49` 都已在最小 replication 后被压回 `P0`；
  4. 新的 `Rank 50` 也还只是待 intake 的 `P1`，离 `Live Seat` 还早。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **严格说，当前没有存活中的 active replication 候选。**
- 更诚实的状态是：
  - `Rank 48 / session-range active-hours gate` → 已完成最小 clean replication，`park`
  - `Rank 49 / funding-basis crowded-long unwind gate` → 已完成最小 clean replication，`park`
  - 因此 `Scout Seat` 当前已重置到 **fresh paper / repo based intake queue**
- 当前下一手最值得认领的 fresh repo 候选：
  - **`Rank 50 / chanlun-pro structural reclaim gate`**（来源：`2026-03-18_0654_chanlun-second-buy-structural-reclaim-gate.md`）

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 50 / chanlun-pro structural reclaim gate` → **`P1`**（`fresh source intake / 两条轻量诚实守门 next`）
- `Rank 48 / session-range active-hours gate` → **`P0`**（`minimal clean replication done -> park / evidence pool`）
- `Rank 49 / funding-basis crowded-long unwind gate` → **`P0`**（`minimal clean replication done -> park / evidence pool`）
- `Rank 35b` → **queue-only / not admitted**（fallback，不是默认主资源位）
- `Rank 2 / Rank 17 / Rank 29 / Rank 32b` → **`P3`**（`narrow paper pilot / 托管 continuity`）
- **当前 `P2` 为空，`P4` 也为空。**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 — `EMA due-check only`**
   - 只确认当前是否新出现 `due-now / overdue` bar；若仍 `waiting_not_due`，立刻切走，不空转。
2. **Run 2 — `Rank 50 / chanlun-pro structural reclaim gate` source intake + 两条轻量诚实守门**
   - 只回答两件事：
     - 规则能否冻结成 `trade on / trade off`
     - 是否存在明显 `lookahead / repaint / leakage`
   - 不允许同轮提前跳去宽松 feature engineering。
3. **Run 3 — `Rank 50` minimal clean replication（仅当 Run 2 guard-passed 且 EMA 仍 waiting_not_due）**
   - 固定 `BTC/ETH/SOL 15m`、`next-bar open + no-overlap`；
   - 只比较 `raw_fib_or_retest`、`+structural_reclaim`、`+structural_reclaim+HTF direction`（short 侧如要测，单独镜像统计）；
   - 若 Run 2 硬 fail，则 Run 3 回到下一条 fresh source intake；只有 fresh source 仍 exhausted 时，才回退 `Rank 35b / tiny-live plumbing`。

## strongest evidence
- `EMA` 的 `07:01 UTC` A 股 due-now refresh 已真实写账，说明 `Paper Seat` 当前是实盘节奏上的 `waiting_not_due`，不是漏跑。
- `Rank 48 / 49` 都已经在允许预算内完成最小 replication 并 park，因此当前 desk 不该再假装存在 surviving active `P1 / P2`。
- `06:54 UTC` 的 `chanlun-pro structural reclaim gate` digest 比 `Rank 35b` 更符合当前规则：fresh、repo-based、15m crypto、直接服务现有三条线的共用确认层。

## weakest / should-park lines
- 最不该继续高估的是把 `Rank 48 / 49` 当作“还差一轮就可能升格”的 active Scout；它们已经给出 hard verdict。
- 同样不该误用的是 `P3 continuity`：当前 `manual_narrow_paper_last_run_summary.json` 明确 `new_closed_trades_appended=0`，没有新的状态变化需要抢占 bot3 主资源。

## active Scout 边际价值比较
1. **`Rank 50 / chanlun-pro structural reclaim gate` 最高**
   - fresh repo source；
   - 不是开第四条主线，而是给 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 补一层共用结构确认；
   - 比继续磨 `Rank 35b` 更贴当前 desk。
2. **`Rank 35b` 仍只值 fallback**
   - 只在 fresh intake 本轮也拿不到合格 source 时才值得回退。
3. **`P3 continuity` 继续低频托管**
   - 没有新的 append/review event 时，不该重回 bot3 默认主资源位。

## TODO / web / cron 的改动或建议
- **已改 TODO 顶板**：
  - 在 `Scout Seat verdict` 区增加 `07:20 UTC` authoritative 补充，明确 `Rank 48 / 49` 都已 park、当前应重置为 fresh intake、下一条新方向为 `Rank 50`。
  - 在 `Next 3 bot3 runs` 区增加 `07:20 UTC` authoritative 补充，把排班收紧成：`EMA due-check -> Rank 50 intake -> Rank 50 minimal clean replication / 回退`。
- **已更新网页可见落点**：
  - 重新生成 `reports/site/plans/momentum_todo.html`。
- **cron**：本轮不改；当前只是 board 排班更新，不是节奏设计变更。

## 风险与不确定性
- `Rank 50` 目前还只是候选方向名，不是已 guard-passed 的 replication 任务；若规则写不清或存在结构回填/事后确认风险，应直接止步于 intake。
- `chanlun-pro` 本身偏 A 股 / 结构对象口径复杂；必须先压成朴素的 `higher-low / lower-high + reclaim` 因果版定义，不能把整套对象直接搬进 15m crypto。
- 当前 workspace 脏文件较多，本轮依旧不适合安全 selective commit。

## Commit
- 未提交。
- 原因：git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件，本轮不安全混提。
