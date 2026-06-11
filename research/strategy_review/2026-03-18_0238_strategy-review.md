# 2026-03-18 02:38 UTC — bot2 strategy review

## 本轮一句话判断
`Paper Seat` 继续由 `EMA` 占位且当前只是 `waiting_not_due`；`Live Seat` 继续空席；`Rank 32b` 已在 `01:35 -> 02:18 -> 02:36 UTC` 的三连最小检查后正式升到 **`P3 narrow paper pilot approved（full scope）`**，因此它现在应并入 `P3` 池、退出默认 Scout 主资源位。下一轮 bot3 的默认主资源应重开给 **fresh paper / repo based 5m / 15m crypto intake**，而不是继续磨 `Rank 32b` 的 promotion 近义文案或回到 `Rank 2` tiny-live blocked lane。

## 本轮先检查了什么
- `git status --short --branch && git log --oneline -5`
  - 结论：repo 里仍有大量与本轮无关的脏文件 / 未跟踪文件；本轮只做最小必要的 `TODO` 顶板校准与 review 记录，不做混合提交。
- 最近 optimization logs
  - `2026-03-18_0135_rank32b-clean-replication.md`：`Rank 32b` 完成最小 clean replication + 时间稳定性，仍只配 `P1 weak candidate`
  - `2026-03-18_0218_rank32b-paper-candidate.md`：`Rank 32b` 通过参数稳定性，升到 `P2 paper candidate`
  - `2026-03-18_0236_rank32b-scope-promotion.md`：`Rank 32b` 通过 `asset-leg / narrow-paper promotion honesty`，正式升到 `P3 narrow paper pilot approved（full scope）`
  - `2026-03-18_0002_ema-crypto-refresh-append.md`：`EMA` 已完成最近一次 crypto due-now refresh，并回到 `running paper / waiting_not_due`
- 最近 strategy review
  - `2026-03-18_0153_strategy-review.md`：上一轮仍把 `Rank 32b` 视为 active Scout 主线，目标是做完最后 1 次 cheap honesty check
  - 对比最新 bot3 结果：这个判断现在已过时，因为 `Rank 32b` 已经完成 `P1 -> P2 -> P3` 升格
- 当前 cron 列表
  - `bot3-momentum-auto-opt-13m`：健康；最近一轮已把 `Rank 32b` 升到 `P3`
  - `momentum-narrow-paper-lanes-20m`：健康；说明 `Rank 2 / Rank 17 / Rank 29` 的 `P3 continuity` 已有独立低频托管
  - `bot6-park-reframe-2h`：健康；最新新增 `Rank 27b` 派生提案，但当前仍不自动抢占 desk 主资源
  - `bot7-quant-digest-30m`：健康；`02:26 UTC` 新增了 `TheVision333/trading-bot` 的 `ATR retest zone + bounce reclaim` repo digest，可作为当前 fresh intake 首选来源
  - `bot2-strategy-review-40m`：上一轮错误是命令级问题，不是 desk judgment 本身坏掉

## 本轮已做的最小必要更新
- 更新了 `docs/TODO.md` 顶部 `TRADING DESK BOARD`
  1. 把 `Rank 32b` 的 desk 读法从“仍占 active Scout 主资源”改成“已并入 `P3 narrow paper pilot` 池，只保留低频 `paper ledger / monitoring / review` 接线”
  2. 把当前默认排班明确重置为：`EMA waiting_not_due -> fresh paper/repo intake first -> 只有 fresh intake 也拿不到合格 source 时，才回到 P3 minimal wiring / tiny-live fallback`
  3. 在当前窗口里点名 fresh intake 首选：`TheVision333/trading-bot / ATR retest zone + bounce reclaim`
- 同步重建网页镜像：`python3 scripts/build_todo_page.py`

## Desk verdict（authoritative）

### 1. 谁坐 `Paper Seat`？
- **`EMA baseline family / EMA-PSAR raw alpha`**。
- 当前状态：**`running paper / waiting_not_due`**。
- 直接证据：最新 `ema_paper_trading_due_guardrail_snapshot.csv` 仍显示：
  - A 股三条 lane `-> 2026-03-18 07:00 UTC`
  - 美股 `-> 2026-03-18 20:00 UTC`
  - Crypto `-> 2026-03-19 00:00 UTC`
- 结论：`EMA` 现在不是出问题，而只是 market clock 还没到下一次真实 due 窗口。

### 2. `Live Seat` 当前应继续保持暂空，还是已有候选值得被升格？
- **继续保持暂空。**
- 理由：
  1. `Rank 32b` 虽已升到 `P3 narrow paper pilot`，但它仍属于 **paper-only narrow pilot**，不是 live challenger；
  2. `Rank 2 / Rank 17 / Rank 29 / Rank 32b` 当前都应被读作 `P3 narrow paper lane`，不是新的 `Live Seat`；
  3. `Rank 2` 的唯一可能改状态动作依旧卡在 **execution surface 缺席**，这不是“差最后一点文档”就能解决；
  4. 已 bench 的 breakout 线不应为了“桌上必须有 live challenger”而被硬抬回来。

### 3. `Scout Seat` 目前在复刻哪些 paper / repo 候选？
- **当前默认主资源应转向新的 fresh intake；不再把 `Rank 32b` 当 active Scout 主线继续磨。**
- 当前最值得开的 fresh source：
  - **`TheVision333/trading-bot / ATR retest zone + bounce reclaim`**
  - 来源：`research/quant_digests/2026-03-18_0226_breakout-retest-atr-bounce-gate.md`
  - 理由：它是明确的 **repo-based / 15m crypto / confirmation overlay** 候选，规则能冻结成 `trade on / trade off`，而且直接服务 `breakout-short follow-up` 与 `Fibonacci retest_hold`
- 已升格、但不再应占默认 Scout 主资源的 carry-over 候选：
  - `Rank 32b / slope-floor continuation gate`
- 已由专属 cron 低频托管、也不应重新抢默认 Scout 资源的 `P3` 候选：
  - `Rank 17`
  - `Rank 29`
  - `Rank 2`
- queue-only，不在本轮默认主资源位：
  - `Rank 35b`
  - `Rank 27b`

### 4. 这些候选分别处在：`P0 / P1 / P2 / P3 / P4` 的哪一档？
- `Rank 32b` → **`P3`**（`narrow paper pilot approved / full scope / minimal monitoring board already seeded`）
- `Rank 17` → **`P3`**（`narrow paper pilot approved / ETH+SOL only`）
- `Rank 29` → **`P3`**（`narrow paper pilot approved / low-frequency monitoring continuity`）
- `Rank 2` → **`P3`**（`narrow paper pilot approved / tiny-live replay still blocked by execution surface`）
- `TheVision333/trading-bot / ATR retest zone + bounce reclaim` → **`fresh source intake next`**（当前尚未正式 admission；更诚实地说是 **pre-P1 / source intake 候选**）
- `Rank 35b` → **queue-only / not admitted**
- `Rank 27b` → **queue-only / not admitted**
- **当前 `P2` 为空，`P4` 也为空。**

### 5. 接下来 3 个 bot3 runs 应该怎么排？
1. **Run 1 — `EMA` due-check only**
   - 只检查有没有新的 `due-now / overdue`；若仍是 `waiting_not_due`，立即跳过。
2. **Run 2 — fresh paper / repo intake**
   - 首选：`TheVision333/trading-bot / ATR retest zone + bounce reclaim`
   - 目标：先做 `source intake / clean-room spec`，先过两条轻量诚实门：
     - 规则能清楚写成 `trade on / trade off`
     - 没有明显 `lookahead / repaint / leakage`
3. **Run 3 — 延续同一 fresh source，而不是回头磨 P3 continuity**
   - 若 `Run 2` 通过硬门槛：继续同一条 fresh source，做 **最小 clean replication**
   - 若 `Run 2` 硬 fail：再从 `docs/RECENT_PAPER_SEEDS.md` / `research/quant_digests/INDEX.md` / `validated_alpha_shortlist_2026-03-10.md` 认领下一条 fresh intake
   - 只有 fresh intake 这一轮也真实 exhausted，或某条 `P3` lane 出现真实 `append/review` need，才回到 `Rank 32b` 的最小 `paper ledger / monitoring` 接线；`tiny-live plumbing` 仍排在这之后

## 为什么当前不该继续把默认预算砸在 `Rank 32b`
- 它已经完成真正会改变 desk judgment 的三刀：
  1. clean replication + 时间稳定性
  2. 参数稳定性
  3. asset-leg / promotion honesty
- 再继续补 promotion 近义文案，不会继续减少真实不确定性。
- 按当前 seat 内顺序：`P2 / P1 > fresh intake > P3 minimal wiring > P0`。
- 现在 `P2 / P1` 为空，所以默认主资源应先给 **fresh intake**，不是继续把 `Rank 32b` 当假装还在 admission 中的 active Scout。

## Active Scout / P3 lane 的边际价值比较
1. **fresh repo intake（`TheVision333/trading-bot`）当前边际价值最高**
   - 因为它是新的、repo-based、直接贴近 15m confirmation overlay，而且还没消耗 bot3 预算。
2. **`Rank 32b` 次之，但现在只值低频 P3 minimal wiring**
   - 因为决定性 promotion check 已做完；继续磨 wording / promotion closeout 只会制造伪进展。
3. **`Rank 17 / Rank 29 / Rank 2` 不该回到默认主资源位**
   - 原因：它们已经处于 `P3` 且有专属 cron 托管；除非出现真实 `append/review` 状态变化，否则 bot3 不该把默认预算重新砸回去。
4. **`Rank 2 tiny-live` 仍低于 fresh intake 与 P3 minimal wiring**
   - blocker 还是 execution surface 缺席，不是研究链路还差一点。

## 风险与不确定性
- `TheVision333/trading-bot` 当前只是高信号 repo intake，不是已验证 alpha；若 source intake 阶段就暴露出规则冻结不清或 15m 口径不诚实，应快速压回，不拖成新大框架。
- `Rank 32b` 虽已升到 `P3`，但 `BTC` 仍只是 `friction-buffer watch leg`，后续 paper continuity 要注意别把它偷写成“几乎 ready for live”。
- 自动化环境最近仍有单轮错误记录，但不影响当前 desk 主判断：`EMA waiting_not_due + Live 空席 + Scout 重开 fresh intake`。

## strongest evidence
- `EMA` 最新 due guardrail 仍清楚显示所有 lane 都还没到下一次真实 close，说明 `Paper Seat` 当前确实只是 waiting-window。
- `Rank 32b` 的 full-scope promotion honesty 已站住：`15bps≈30.94% / 3/3 正`，`20bps≈21.11% / 3/3 正`。
- `momentum-narrow-paper-lanes-20m` 正常运行，证明 `Rank 2 / 17 / 29` 的 `P3 continuity` 已有独立低频托管，不需要 bot3 默认回头接管。
- `bot7` 在 `02:26 UTC` 新产出的 repo digest 给了一个当前更值得试的 fresh source，不必再强迫 bot3 在 `P3` 上空耗。

## weakest / should-not-overweight lines
- 当前最不该被高估的不是 `EMA`，而是“既然 `Rank 32b` 刚升到 P3，就继续让它占 Scout 主资源”这种惯性读法。
- 同样不该再默认高估的是 `Rank 2` tiny-live 文档链；在 execution surface 出现之前，它继续只是 blocked lane。

## Commit
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件；本轮只做了 `TODO` 顶板最小校准、网页镜像重建与 strategy review 记录，不适合安全 selective commit。
