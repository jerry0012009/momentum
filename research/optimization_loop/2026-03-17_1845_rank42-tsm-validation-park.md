# 2026-03-17 18:45 UTC — Rank 42 `Time Series Momentum: Is It There?` source intake hard verdict

## 本轮为什么选这个
- 当前 `Paper Seat / EMA` 仍是 `waiting_not_due`，所以这轮按 authoritative board 落在 `Run 2 / Scout Fast Lane`。
- 过去几轮已经把 `Rank 38 / 39 / 40 / 41` 连续做成 `mechanism note only / source-template only / park / research-seed only`，本地 fast-lane shortlist 基本见底。
- 按 desk 规则，在诚实回退到 `Run 3 / tiny-live plumbing` 之前，仍应先从 `docs/RECENT_PAPER_SEEDS.md`、`research/quant_digests/INDEX.md`、`validated_alpha_shortlist_2026-03-10.md` 里再认领 1 条旧 seed，确认它是不是还能进入当前 fast lane。

## 本轮认领
- 主点：`Run 2 / fresh local paper-seed intake`
- 对象：`Rank 42 / Huang et al. (2020) / Time Series Momentum: Is It There?`
- 紧邻子点：把 hard verdict 写回 `docs/TODO.md` 顶部作战板，并补一个 reader-facing digest 落点。

## 做了什么
1. 重读 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs`，确认当前仍应先做 `Scout Seat`。
2. 复核本地 seed 列表后，选了 `Huang et al. (2020)` 这条还没正式写回 authoritative board 的旧 validation seed。
3. 按当前 desk 的 intake 诚实门做判断：
   - 它能否自然冻结成 `trade on / trade off / exit / hold / no-overlap` 的 15m crypto 执行模板？
   - 它更像新 candidate，还是更像 `TSM vs drift / signal-vs-system` 的验证边界论文？
4. 新增 reader-facing digest：
   - `research/quant_digests/2026-03-17_1845_tsm-is-there-not-fastlane.md`
5. 更新索引与作战板：
   - `research/quant_digests/INDEX.md`
   - `docs/TODO.md` 顶部 `TRADING DESK BOARD`（新增 `Rank 42`，并在 `Next 3 bot3 runs` 补写最新判断）

## 核心判断 / hard verdict
### 1) 这不是当前 fast lane 需要的“执行模板”
这篇论文真正有价值的地方，是提醒别把 `策略收益` 误认成 `最朴素 TSM 信号 alpha`。它最自然的下一步是：
- 拆 `TSM_N`
- 拆 `TSH_like`
- 拆等权 / vol-scaled
- 再做 baseline honesty A/B

这是一条 **validation / honesty-gate** 线，不是当前 `clean replication -> Light Stability Pack -> paper candidate` 所需的现成模板线。

### 2) 这不是坏 source，但用途是“研究校验器”
- 没有显眼的低级 `lookahead / repaint / leakage` 问题；
- 但如果硬塞进 fast lane，会把当前轮次自然拖向新的 baseline-harness 研究框架，而不是当前 desk 想要的 `paper / repo based 5m / 15m crypto` 快筛闭环。

### 3) 最诚实结论
**`Rank 42 -> park / validation-context only`**

更直白地说：
- 它能继续当 `别自欺` 的学术背书；
- 不能当作新的 fast-lane scout candidate 抢默认预算。

## 验证 / 证据
- 证据来源：
  - 旧 digest：`research/quant_digests/2026-03-11_1328_time-series-momentum-is-it-there.md`
  - 本轮 intake digest：`research/quant_digests/2026-03-17_1845_tsm-is-there-not-fastlane.md`
- authoritative writeback：
  - `docs/TODO.md` 已新增 `Rank 42` 条目；
  - `Next 3 bot3 runs` 已补写：本地剩余 seeds 更明确地只剩机制/验证/母论文语境，后续若 `EMA` 仍 `waiting_not_due` 且没有新的 promoted source，可诚实回退到 `Run 3 / tiny-live plumbing fallback`。

## 风险 / 边界
- 这轮**没有**把 `Huang et al. (2020)` 偷渡成新的回测工程线；
- **没有**回头再磨 `Rank 39 / 40 / 41`；
- **没有**动 `Rank 17 / Rank 2 / Rank 29` 的 P3 continuity 配额；
- 这轮新增的是 **hard verdict + authoritative board writeback**，不是新的 clean replication 结果。

## 对下一轮的意义
当前 desk 读法更干净了：
- 本地 fast-lane seeds 基本已经被如实消化；
- 留在列表里的旧论文更多是 `validation / mechanism / mother-paper context`；
- 因此只要 `EMA` 继续 `waiting_not_due` 且 bot2 没有点名新的 promoted source，后续轮次就可以更诚实地落到 `Run 3 / tiny-live plumbing`，而不是继续在本地 seed 池里假装还有未认领的执行模板。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件，按作战板要求不做混提；本轮只保留局部文件改动、日志、首页刷新与邮件摘要。
