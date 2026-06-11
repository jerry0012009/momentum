# 2026-03-18 11:08 UTC — desk review：EMA 继续坐 Paper，Live 继续空，Scout 由 Rank 54 拿主资源

## 本轮一句话判断
当前 desk 没有席位翻盘：**`Paper Seat = EMA`，`Live Seat = 暂空`，`Scout Seat = Rank 54 / LVN rejection + POC acceptance gate`**。真正需要补的不是再换 seat，而是把 `Run 3` 写清：若 `Rank 54` 的最小 clean replication 没爆雷，下一轮默认应直接给它 **1 个 truly verdict-changing 的 Light Stability Pack**，然后做 **`P2 / park`** 判定，而不是提前写死成纯 fallback。

## 0）本轮先做的状态检查（按 desk 规则）
- 已先读：`docs/BOT2_STRATEGY_REVIEW_BRIEF.md`
- 已先读：`docs/TODO.md` 顶部 `TRADING DESK BOARD`
- repo 状态：`git status --short --branch` 仍显示大量与本轮无关的既有脏文件 / 未跟踪文件；本轮继续只做顶板最小写回，不混提其它内容。
- 最近 optimization logs：
  - `2026-03-18_1104_rank54-source-intake-guard-passed.md`
  - `2026-03-18_1102_rank53-clean-replication-park.md`
  - `2026-03-18_1034_rank53-source-intake-guard-passed.md`
  - `2026-03-18_1011_rank52-clean-replication-park.md`
- 最近 strategy review：
  - `2026-03-18_1021_strategy-review.md`
  - `2026-03-18_0925_strategy-review.md`
- 当前 cron 关键项：
  - `bot2-strategy-review-40m`：正常运行中（本轮即当前 run）
  - `bot3-momentum-auto-opt-13m`：正常运行中
  - `bot7-quant-digest-30m`：正常运行中
  - `momentum-narrow-paper-lanes-20m`：正常运行中
  - `bot6-park-reframe-2h`：正常运行中
- `EMA due guardrail` 当前仍全是 `waiting_not_due`：
  - 美股 `1d+1wk -> 2026-03-18 20:00 UTC`
  - Crypto `1d+1wk -> 2026-03-19 00:00 UTC`
  - A 股三条 lane `-> 2026-03-19 07:00 UTC`
- `manual_narrow_paper_last_run_summary.json @ 11:07:58Z`：`new_closed_trades_appended=0`；当前没有新的 `P3 status-changing event` 值得把 bot3 拉回 continuity。

## 1）本轮必须回答的 5 个问题

### 1. 谁坐 `Paper Seat`？
- **`EMA / EMA-PSAR raw alpha focus` 继续坐 `Paper Seat`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 这意味着 bot3 的 `Run 1` 仍只能是 **`due-check only`**，不能伪造 refresh，更不能把整张 desk 一起拖进等待。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持 `暂空`。**
- 原因：
  1. `Rank 54` 目前只到 **`guard-passed / admit_to_clean_replication_queue`**，还没走完 `clean replication`；
  2. `Rank 53 / 52 / 51 / 50` 都已在允许预算内给出 hard verdict 并压回 `park / evidence pool`；
  3. `Rank 2 / 17 / 29 / 32b` 虽然是 `P3 narrow paper continuity`，但不是当前可直接升为 tiny-live challenger 的新 seat。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前唯一 active Scout 候选是：`Rank 54 / LVN rejection + POC acceptance gate`。**
- 它来自 fresh repo source：`Aksee123/nq1_Scalping_Strategy`。
- 当前不是“多条并行 replication”，而是：
  - `Rank 54` 拿主资源位；
  - `Rank 35b`、`Rank 16b` 仅保留 queue-only fallback；
  - `Rank 2 / 17 / 29 / 32b` 继续只算 `P3 continuity` 托管，不抢当前 Scout seat。

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 54 / LVN rejection + POC acceptance gate`** → **`P1 weak candidate`**（`guard-passed / admit_to_clean_replication_queue`）
- **`Rank 35b`** → **queue-only fallback / 未重新 admitted**（不算 active `P1/P2`）
- **`Rank 16b`** → **queue-only fallback / 未重新 admitted**（不算 active `P1/P2`）
- **`Rank 53 / Rank 52 / Rank 51 / Rank 50`** → **`P0 park / evidence pool`**
- **`Rank 2 / Rank 17 / Rank 29 / Rank 32b`** → **`P3 narrow paper continuity`**（仅保留 `paper ledger / monitoring / refresh / review` 最小托管）
- 当前 **`P2` 为空，`P4` 为空**。

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 = `EMA due-check only`**
2. **Run 2 = `Rank 54 / LVN rejection + POC acceptance gate` 的最小 clean replication**（仅当 `EMA` 仍 `waiting_not_due`）
3. **Run 3 = 条件式继续，不预先写死成纯 fallback**
   - 若 `Rank 54` clean replication **没被判死刑**：只给它 **1 个 truly verdict-changing 的 `Light Stability Pack`**（默认优先 `时间稳定性`，并直接做 `P2 / park` 判断）
   - 若 `Rank 54` clean replication **失败 / exhausted**：再回退到 **`Rank 35b > Rank 16b > tiny-live plumbing`**

## 2）当前 active Scout 边际价值比较
- **`Rank 54` 最高**：fresh repo、shared acceptance gate、已过两条轻量诚实守门，而且比继续磨已 park 的 `Rank 53 / 52 / 51 / 50` 更接近改变 desk judgement。
- **`Rank 35b` 次之**：只是 derived fallback，不该在 fresh repo 主资源位仍活着时抢前排。
- **`Rank 16b` 再次之**：同样是 fallback，而且与近期被证伪的 session/time-window 类轴更相邻。
- **`tiny-live plumbing` 最后**：当前 `Live Seat` 仍空，且没有新 promoted challenger，不该抢在 fresh Scout 前面。

## 3）strongest evidence
- `EMA due guardrail` 仍全为 `waiting_not_due`，证明 `Paper Seat` 当前只是被 market clock 卡住，而不是漏跑。
- `Rank 54` 已通过两条轻量诚实守门：`trade on / trade off` 能冻结，源码层也未见一眼可判死刑的 `lookahead / repaint / leakage`。
- `manual_narrow_paper_last_run_summary.json @ 11:07:58Z` 仍是 `new_closed_trades_appended=0`，说明本轮没有真实 `P3 continuity` 事件值得 bot3 抢回去做。

## 4）weakest / should-park lines
- 最不该再高估的是把 `Rank 53 / 52 / 51 / 50` 假装写成还在 active queue 的候选；它们都已给出 hard verdict。
- 同样不该误写的是把 `Rank 2 / 17 / 29 / 32b` 这些 `P3` 托管位重新当成默认 Scout 主资源。

## 5）这轮做的最小必要改动
- **已改 `docs/TODO.md` 顶部 `TRADING DESK BOARD`**：
  - 追加 `2026-03-18 11:08 UTC` authoritative 补充；
  - 明确当前 seat judgment 不变；
  - 把 `Run 3` 从“预先写死成 fallback”改成“若 `Rank 54` 存活，则先做 1 个 truly verdict-changing 的 `Light Stability Pack`，再做 `P2 / park` 判定”。
- 这轮没有改 cron。

## 6）reader-facing judgment
- 这轮 reader-facing judgment 有小但重要的变化：
  - 不是换 seat，
  - 而是把 **`Rank 54` 过 replication 后的默认去向** 写清，防止 bot3 又掉回“继续 intake / 直接 fallback”的模糊态。
- 因此已同步到网页可见落点：`docs/TODO.md` 顶板（并重建其站点镜像）。

## 7）风险与不确定性
- `Rank 54` 源 repo 原语境偏 NQ futures，不是 crypto；clean replication 时必须坚持 clean-room 迁移，不能继承原作者绩效叙事。
- 若 `Rank 54` 的改善主要来自强砍样本或 profile 窗口敏感性过大，就应快速压回 `park / evidence pool`。
- 当前工作区仍有大量与本轮无关的脏文件 / 未跟踪文件，因此本轮不安全 selective commit。

## 8）执行备注
- 未提交 git。
- 原因：工作区存在大量与本轮无关的脏文件与未跟踪产物，不满足安全 selective commit 条件。
