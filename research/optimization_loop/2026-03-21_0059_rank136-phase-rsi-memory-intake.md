# 2026-03-21 00:59 UTC — Rank 136 / phase-wide RSI memory retest gate intake

## 本轮先做的桌面检查（按 TRADING DESK BOARD）
- `git status --short`：repo 仍有大量与本轮无关脏文件，继续 **不混提**。
- 先执行 `Run 1 / EMA due-check first`：
  - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 结果：当前仍无 `due-now / overdue` lane；最靠前仍是 `Crypto 1d+1wk（BTC/ETH/SOL）`，约 `23.0h` 后到点。
  - 结论：`Paper Seat = waiting_not_due`，本轮必须切 `Scout Seat`，不得空转。

## 3.5 Active Scout 边际价值比较（本轮只取 1 条）
比较对象只限当前允许来源里的最新、未认领、且仍适合 `paper / repo based 5m/15m crypto` 的候选：
- `phase-wide RSI memory retest gate`（quant digest 2026-03-21 00:41）
  - 优点：直接服务 breakout-short / Fib / EMA-PSAR 三条主线；已有 pooled quickcheck；是标准 Scout filter，不是 plumbing。
- `fixed partial -> R/ATR partial`（quant digest 2026-03-20 22:42）
  - 优点：有工程价值；但角色更像 `tiny-live / path-management fallback`，不该抢当前 Scout 主位。
- `adaptive exhaustion` 等已入队条目
  - 已有 `Rank 132`，且 clean replication 已 park；本轮不能伪装成 fresh intake 重复占位。

**结论：** 本轮 fresh intake 的最高边际价值对象是 **`phase-wide RSI memory retest gate`**，因此分配下一个顺序 `Rank 136`。

## 本轮主点：认领 `Rank 136 / phase-wide RSI memory retest gate`
来源：
- `research/quant_digests/INDEX.md`
- 对应 digest：`2026-03-21_0041_phase-wide-rsi-memory-retest-gate.md`

## 为什么挑它
这条线值钱，不是因为“RSI 很常见”，而是因为它补的是当前 desk 真缺的一句诚实话：
- 不是只看 entry 当根 RSI，
- 而是问 **整段回踩 / 反抽阶段的动量结构有没有坏掉**。

它正好对齐三条主线：
- `breakout-short`：拦截“反抽还没走完就追空”；
- `Fib retest_hold`：把“碰到位”升级成“回踩整段动量结构没坏”；
- `EMA / PSAR`：给 raw trigger 一个便宜、可复核的后置过滤层。

## 两条轻量诚实守门
### 1) trade on / trade off
- **trade on：** 冻结既有 `breakout_short / fib_retest_hold / ema_psar continuation` entry，只把 RSI 判定改成 phase-wide memory gate：
  - `long`：整段回踩期 `min RSI >= 55`
  - `short`：整段反抽期 `max RSI <= 44`
- **trade off：** 它不是新主策略，也不是 RSI 神谕；若 clean replication 只剩 setup-specific / single-pocket uplift，直接 `park` 或仅保留为单线 overlay。

### 2) no lookahead / repaint / data leakage
- phase gate 只允许使用实际入场判定前已经完成的回踩期 completed bars；
- 执行口径统一 `next-bar open + no-overlap`；
- 禁止用 verdict 之后的 path、future extrema、或后验最优 phase 长度/阈值去倒算 gate。

**本轮 hard verdict：`guard-passed / admit_to_clean_replication_queue`。**

## 新增产物
1. `reports/artifacts/literature/scout_rank136_phase_wide_rsi_memory_source_intake_card.csv`
2. `reports/site/reading/repo_scout/rank136_phase_wide_rsi_memory_source_intake.html`

## 对 desk board 的最小 write-back
- `Scout Seat 当前主点`：切到 **`Rank 136 / phase-wide RSI memory retest gate`**。
- `Active Scout 排序`：将 `Rank 136` 置顶为 `P1 / source intake done / guard-passed`。
- `Next 3 runs`：
  - `Run 2` 改为：若 EMA 仍 `waiting_not_due`，执行 `Rank 136` 的 1 次最小 clean replication；
  - `Run 3` 改为：若 replication 通过，只补 1 个真正会改变 verdict 的最小检查；若 replication 不通过，则回下一条 fresh intake。
- `最近关键 evidence`：补入本轮 `EMA waiting_not_due` 守门与 `Rank 136 fresh intake` 结论。

## 下一轮最小动作建议
- 若 `EMA` 仍非 due-now：给 `Rank 136` **仅 1 次最小 clean replication**（BTC/ETH/SOL、15m、next-bar open、no-overlap、6/10/15bps），比较 `baseline` vs `phase-wide RSI memory gate`，直接输出 `keep_P1 / promote_P2 / park`。

## 验证
- `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`

## commit
- 未提交（当前工作区存在大量与本轮无关脏文件，按规则不混提）。
