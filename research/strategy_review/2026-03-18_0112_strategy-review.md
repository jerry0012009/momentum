# 2026-03-18 01:12 UTC — bot2 strategy review

## 本轮先检查了什么
- `git status --short`
  - 结论：repo 里有大量与本轮无关的脏文件 / 未跟踪文件；本轮只做最小必要的 `docs/TODO.md` 调整，不做混合提交。
- 最近 optimization logs
  - `2026-03-18_0002_ema-crypto-refresh-append.md`：`EMA` 已在 `00:02 UTC` 完成 crypto due-now refresh，并回到 `waiting_not_due`
  - `2026-03-18_0013_no-progress.md`：确认 `Run 3 / Rank 2` 继续卡在 **execution surface 缺席**
  - `2026-03-18_0045_bot7-fallback-tsmom-baseline.md`：说明上一轮是在 `Run 1 waiting + Run 2 exhausted + Run 3 blocked` 下借用了一次 `bot7` fallback，不是 desk 主线真的变了
  - `2026-03-18_0101_no-progress.md`：本轮前最近一次 bot3 仍未拿到新的 seat-changing 进展
- 最近 strategy reviews
  - `2026-03-17_1223_strategy-review.md`
  - `2026-03-17_1303_strategy-review.md`
  - `2026-03-17_1343_strategy-review.md`
  - 共同主线：`Paper Seat = EMA`、`Live Seat = 暂空`、`Scout` 要收紧成 fast lane，不奖励近义 wiring
- 当前 cron 列表
  - `bot2-strategy-review-40m`：运行中
  - `bot3-momentum-auto-opt-13m`：健康
  - `momentum-narrow-paper-lanes-20m`：健康
  - `bot7-quant-digest-30m`：健康
  - `bot6-park-reframe-2h`：健康
  - 结论：`Rank 2 / 17 / 29` 的 `P3` continuity 已有专属 cron 托管，不该再抢默认 bot3 主资源

## Desk verdict（本轮 authoritative）

### 1. 谁坐 `Paper Seat`？
- **仍然是 `EMA / PSAR raw alpha`。**
- 当前状态：**`running paper / waiting_not_due`**。
- 证据：`00:02 UTC` 的 crypto due-now refresh 已完成；最新 due 顺序已推到：
  - A 股三条 lane `-> 2026-03-18 07:00 UTC`
  - 美股 `-> 2026-03-18 20:00 UTC`
  - Crypto `-> 2026-03-19 00:00 UTC`
- 这说明 `Paper Seat` 不是坏了，只是被 market clock 暂时挡住；因此 bot3 不能在这里空转。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 理由：
  1. 这轮没有任何新候选已经走到 `clean replication + Light Stability Pack` 之后的升格条件；
  2. `Rank 2 / Rank 17 / Rank 29` 虽然都在 `P3`，但它们现在的正确读法是 **专属 narrow-paper continuity lane**，不是“谁都能顺手升成 live challenger”；
  3. `Rank 2` 真正剩下的状态改变动作仍是那 1 次 `SOLUSDT whitelist-bound test/no-fill replay`，但它继续卡在 **没有 execution surface**，所以这不是“离 live 很近”，而是“外部执行面没到位”；
  4. 已 bench 的 breakout 线不该因为桌上想“有个 live 候选”就被强行抬回来。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **本轮正式认领的 active Scout 只有 1 条：`Rank 32b / slope-floor continuation gate`。**
  - 来源：`PARK_REFRAME_QUEUE` 中的窄派生提案，source=`Rank 32 EMA structure vs MA slope direction gate`
  - 性质：repo-based 派生，不是凭空新造大框架
  - 唯一修改轴：**去掉 `spread-mid reclaim`，只保留 `EMA cross + aligned slope floor`**
- **`Rank 35b` 只保留为备选，不同时打开。**
  - 理由：规则虽然也清楚，但当前边际价值低于 `Rank 32b`
- 为什么 `Rank 32b` 胜过 `Rank 35b`：
  - `Rank 32` 原证据里，`slope_floor` pocket 更强：`6bps/side≈+50.76%`、`positive_asset_ratio=3/3`、`mean_trades≈75.7`
  - `Rank 35b` 的 RSI-only pocket 明显更弱：`6bps/side≈+2.71%`、`mean_trades≈12`
  - 因此当前更值得先花那 **1 次便宜诚实检查** 的，是 `Rank 32b`，不是同时打开两条 soft-park 派生线

### 4. 这些候选分别处在 `P0 / P1 / P2 / P3 / P4` 的哪一档？
- **`Rank 32b` → `P1`（`source intake / clean replication next`）**
  - 还没走到 `clean replication`，所以本轮绝不允许它抢 `Live Seat`
  - 它当前只配拿 **1 次便宜且诚实的最小检查**
- **`Rank 35b` → 仍在 queue-only / not admitted**
  - 这轮没有正式写成 active Scout，不算当前默认主资源位
- **`Rank 17` → `P3`（`narrow paper pilot approved / ETH+SOL only`）**
- **`Rank 29` → `P3`（`narrow paper pilot approved / monitoring-only continuity`）**
- **`Rank 2` → `P3`（`narrow paper pilot approved / tiny-live review blocked by execution surface`）**
- **`P2` 当前为空。**
- **`P4` 当前也为空。**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 — 先过 `EMA` due-check，但若仍是 `waiting_not_due` 立即跳过**
   - 只确认有无新的 `due-now / overdue` paper refresh；没有就不要停在 `EMA` 窗口里空转。
2. **Run 2 — `Rank 32b` 的 `source intake -> clean replication`**
   - 先冻结 `trade on / trade off`
   - 先过 `lookahead / repaint / leakage` 轻量诚实门
   - 然后做最小 clean replication
3. **Run 3 — 继续只围绕 `Rank 32b` 做 1 次最小 verdict-changing check**
   - 若 `Run 2` 通过：优先给 **1 项** `Light Stability Pack`（默认 `时间稳定性` 或 `成本 / 交易数稳定性`）
   - 若 `Run 2` 直接硬 fail：立刻 `park`，本轮不再同时打开 `Rank 35b`
   - 只有在 `Rank 32b` 当轮也被真实外部 blocker 卡住时，才诚实回退到 `Run 3 / tiny-live plumbing fallback`

## 为什么这轮要改 TODO 顶部作战板
因为上一版 desk 读法已经滑成：
- `EMA waiting_not_due`
- `Scout exhaustion`
- 然后直接默认掉到 `Run 3 / tiny-live plumbing`

这在 `PARK_REFRAME_QUEUE` 已经出现两个足够窄、且 repo-based 的 `derived_hypothesis_drafted` 条目后，不再是当前最诚实的默认顺序。

按规则，这一轮应该：
1. 先重读 `RECENT_PAPER_SEEDS / quant_digests / validated shortlist`
2. 若仍拿不到更合格的新 source
3. 再从 `PARK_REFRAME_QUEUE` 里择优认领 **最多 1 条**
4. 只有这一层也没有合格对象时，才回退到 `Run 3`

本轮结论就是：**这层现在已经有合格对象，而且 `Rank 32b` 明显优于 `Rank 35b`。**

## 本轮最小必要更新
- 已更新 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  - 把 `Rank 32b` 写成 active Scout 候选
  - 把 `Next 3 bot3 runs` 的 authoritative override 改成：`EMA waiting_not_due -> Rank 32b -> Rank 32b follow-up -> only then tiny-live fallback`
- 未改 cron prompt
  - 因为当前 cron 结构本身没坏，真正落后的只是顶板排班顺序

## 风险 / 边界
- 本轮没有执行任何交易外部动作。
- 没有把 `Rank 35b` 同时塞进 active Scout，避免 Scout fast lane 再次滑成“多开候选”。
- 没有把 `P3 continuity` 托管误写成新的 active seat。

## 下一轮判据
- 若 `Rank 32b` clean replication 不干净：直接 `park`
- 若 `Rank 32b` clean replication 干净：优先升到 `P2`，不要继续卡在模糊研究态
- 若后续 1~2 轮最小诚实检查也没爆雷：默认继续推向 `P3 / narrow paper pilot`
- 在出现真实 execution surface 之前，`Rank 2` 仍只配视为 `tiny-live plumbing blocked`

## Commit
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件；本轮只做了最小 TODO writeback 与 review 记录，不适合安全 selective commit。
