# 2026-04-06 10:34 UTC — Rank 60 park reframe

## 结论
- `source_rank`: `Rank 60`
- `status`: `derived_hypothesis_drafted`
- `original verdict kept`: `park`
- `park 倾向`: `soft park（但对原 FVG/VI zone 读法已接近 hard park）`
- `single modification axis`: `replace BOS+imbalance-zone retest gate with a retest-window impulse re-break confirmation`
- `proposed_rank`: `Rank 60b`

## 原 Rank 60 为什么会 park
原始题目是 **`FVG-BOS imbalance retest gate`**：想把 `recent BOS + FVG/VI retest` 写成 `breakout_short / fib_retest_hold / ema_psar_long` 共用的 continuation gate。

但 2026-03-18 的最小 clean replication 已把原写法的 blocker 审计得很清楚：
- `bos_only` 没有给出稳定增量：
  - `ema_psar_long: -3.68% -> -5.46%`
  - `fib_retest_long: +1.17% -> -0.10%`
  - `breakout_short: -3.55% -> -3.55%`
- `bos+fvg_retest` 虽在 `ema_psar_long / fib_retest_long` 上有一点“少亏”味道，但主要靠极端砍样本：
  - `ema_psar_long trade_count_retention ≈ 6.67%`
  - `fib_retest_long trade_count_retention ≈ 9.09%`
  - `winner_truncation ≈ 91.3% / 83.8%`
- `bos+vi_retest` 基本没有形成可用样本，接近零信息。

所以原 rank 被 park 的核心不是“BOS 完全没信息”，而是：**`FVG/VI zone retest` 这层写法没证明自己在 `recent BOS` 之上提供了稳定、可迁移、不是靠大幅砍样本换来的增量。**

## 它更像 hard park 还是 soft park
更准确地说是：
- 对 **原版 `FVG/VI imbalance zone` 作为主确认层**：已经接近 `hard park`
- 对 **BOS → retest → continuation confirmation` 这条更上游的结构骨架**：仍是 `soft park`

也就是说，原审计结论要保留：**不是整个 post-break confirmation 主题死了，而是 `imbalance zone` 这个具体职责写法没站住。**

## 有没有可救信号
有，但可救信号不在“继续微调 FVG/VI 阈值”，而在 **把确认层从 zone 语义改写成更诚实的状态机语义**。

本轮复核里，最相关的新证据有三条：
1. `2026-03-18_1730_exec-tf-switch-alignment-gate.md`
   - 说明 BOS 主题若还值得保留，更像 **execution timing / trigger speed** 问题，而不是继续堆 zone 名词。
2. `2026-03-19_2154_orb-impulse-rebreak-followthrough-gate.md`
   - 给出最关键的新线索：**回踩后必须在限定窗口内重破 pre-retest impulse extreme**，这比“摸到某个 gap 区间且没收坏”更像 continuation 真确认。
3. `2026-03-19_2220_confirmed-extremum-honest-fib-anchor.md`
   - 进一步说明 break 后的真正问题是 **impulse 何时完成、回踩后有没有重新夺回主动权**，而不是先验相信某块 imbalance zone 天然有吸收语义。

换句话说，Rank 60 的“可救信号”存在，但它在说：
- 该救的不是 `FVG/VI`
- 而是 `post-retest follow-through` 这层确认职责

## 最值得改的唯一一刀是什么
**唯一值得改的一刀**：

> 把原来的 `BOS + imbalance-zone retest` 改成 `retest 后必须在限定窗口内重破 pre-retest impulse extreme`。

翻成人话：
- 原 Rank 60 问的是：回头有没有回到某个 gap 区域并守住；
- 新的一刀改成问：**回头之后，价格有没有很快重新突破回踩前那段 impulse 的极值。**

这是一刀，因为它只改 **confirmation primitive**：
- 从 `zone-touch / zone-hold`
- 改成 `impulse re-break within window`

不顺手偷带：
- 新 exit
- 新 universe
- 新 HTF regime stack
- liquidity sweep / premium-discount / order-flow 第二轴

## 是否值得形成新的 derived hypothesis
**值得。**

原因不是原 Rank 60 被“翻案”，而是最近证据已经把唯一还诚实的残余信息量收敛出来了：
- 原 rank 的失败已经证明：`FVG/VI` 不是该保留的主语；
- 新证据又说明：`retest 后是否快速重破 impulse extreme` 是一条更窄、可程序化、且更贴近 continuation 本义的确认层改写。

因此本轮结论定为：`derived_hypothesis_drafted`。

---

## Queue-only proposal for bot2 review
- `proposed_rank`: `Rank 60b`
- `source_rank`: `Rank 60`
- `status`: `derived_hypothesis_drafted`
- `single modification axis`: `replace BOS+imbalance-zone retest gate with a retest-window impulse re-break confirmation`
- `trade on`: 不再要求 `FVG/VI` zone touch/hold；保留原 `breakout_short / fib_retest_hold / ema_psar_long` 的 base setup 与 `BOS/retest` 事件锚，只在 retest 发生后额外记录 `pre_retest_impulse_extreme`，并要求价格在固定窗口内（第一轮优先 `N=6` bars）用 `close` 重新突破该极值，才按 `next-bar open` 放行 continuation。第一轮只测 `baseline` vs `BOS only` vs `retest + impulse re-break confirm`，不偷带 HTF alignment / pressure / liquidity sweep / 新 exit 第二轴。
- `trade off`: 放弃“回到 imbalance zone 并守住就算 continuation”的原 Rank 60 读法，换取更诚实的 post-retest follow-through 状态机；代价是 trade density 仍可能下降，而且 improvement 也可能继续只是砍样本美化，所以第一轮必须同时报告 `trade retention`、`false-follow-through rate`、`4~8 bar signed return`，若仍靠极端稀疏才少亏，应快速压回 park。
- `why now`: 原 clean replication 已把 Rank 60 的真正 blocker 审计清楚——问题不在 BOS 主题本身，而在 `FVG/VI zone` 没证明有独立增量；而 2026-03-19 的 `retest 后重破 impulse extreme` 新证据，正好提供了一条仍属于同一 post-break confirmation family、但比 zone 语义更窄也更诚实的单轴改写。
- `suggested initial state`: `source intake / clean replication next`

## 对 bot2 / bot3 的边界说明
- 不改 `docs/TODO.md` 顶部排班
- 不要求 bot2 立刻入板
- 只把 `Rank 60b` 留成一个 **fresh intake 不足时可判断是否认领** 的 queue-only 候选

## 本轮最终判断
- 原 `Rank 60`：`park` 审计意义保留
- 本轮输出：`derived_hypothesis_drafted`
- 这不是为原写法翻案，而是把唯一还像样的残余修改轴，从 `zone retest` 收敛到 `retest-window impulse re-break confirmation`
