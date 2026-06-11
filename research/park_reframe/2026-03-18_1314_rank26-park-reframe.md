# 2026-03-18 13:14 UTC · Rank 26 park reframe review

## Scope
- Source rank: `Rank 26 regime triplet state gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 26 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-18_1036_rank18-park-reframe.md`
  - `research/park_reframe/2026-03-18_0836_rank31-park-reframe.md`
  - `research/park_reframe/2026-03-18_0629_rank16-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0656_rank26-regime-triplet-paper-candidate.md`
  - `research/optimization_loop/2026-03-17_0724_rank26-ethsol-recheck-park.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- It is one of the more tempting parked ranks because the original clean replication was **not** a total failure: `strict_up_down` once looked good enough for temporary `P2`.
- But that also means the obvious salvage path was already clear and already spent: **keep the same rule, honestly remove the weakest leg, and see whether a narrow-scope pilot survives**. That exact rescue was already tried and still failed to produce a clean `P3` read.

## 1) 原 rank 为什么 park？
Rank 26 被 park，不是因为“regime gate 毫无信息量”，而是因为它在更诚实的 friction 与窄范围复核下，**没有形成足够干净的 paper-admission pocket**。

原始 `P2` 证据的确不差：
- `strict_up_down @ 6bps/side`：`mean_total_return≈+14.65%`
- `positive_asset_ratio=2/3`
- `mean_trades≈141`
- `10bps/side≈+2.44%`
- time stability 也一度有 `2/3` positive buckets

但把它推进到真正会改 verdict 的最小诚实检查后，问题暴露得很直接：
- 只看 `ETH+SOL-only`，`15bps/side≈+2.29%`，却只剩 `1/2` 资产为正
- 其中 `ETH≈+9.89%`，`SOL≈-5.31%`
- `20bps/side≈-11.17%`
- `15bps` 时间桶仍有明显破口：`bucket_1≈-8.44% / bucket_2≈+1.56% / bucket_3≈+2.45%`

更直白地说：
- 它不是没有一点 edge 味道；
- 但当前最诚实的 narrow-scope 检查已经说明，这个 edge 还不够干净；
- 所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- 它不像很多 rank 那样一上来就全线负、完全无 pocket；
- 原始 `strict_up_down` 的确给过一个“也许能 narrow”的理由；
- 即使压回 park，结论也更像“当前预算内不够干净”，而不是“方向彻底错了”。

但它之所以没有进入 `derived_hypothesis_drafted`，是因为：
- 最自然的那条救法已经不是想象中的未来动作，
- 而是**已经被执行过**：把 `BTC` 弱腿剥离，只留 `ETH+SOL`。
- 结果仍然不够干净，所以现在更像 `soft park but no honest next cut yet`。

## 3) 有没有“可救信号”？
**有弱可救信号，但还不足以支撑新的派生假设。**

可救信号主要有三点：
1. 原始 full-scope 结果不是纯负噪音，说明 `regime state gate` 至少碰到了一点真实结构；
2. 去掉 `BTC` 之后，低 friction 下 aggregate 结果确实进一步变好；
3. 它的故事也足够清楚：`baseline momentum` 负责方向，`regime triplet` 负责只在更像趋势态时放行。

但为什么仍不够：
- 最关键那次窄范围诚实检查已经做过；
- 做完之后，`15bps` 仍只剩 `1/2` 资产为正，时间前段仍破；
- 这意味着“先剥弱腿再看”这条最自然救法已经被消费，且没有把它送进 `P3`。

所以当前更像：
- `regime gate` 有点东西；
- 但 `Rank 26` 这条具体写法在当前 desk 预算内，已经没有足够诚实的新证据支持继续派生。

## 4) 最值得改的唯一一刀是什么？
**表面上最值得改的一刀，是把“对称的 strict up/down entry gate”改成“非对称 veto-only regime overlay”。**

也就是：
- 不再要求 long 一定进 `up_regime`、short 一定进 `down_regime` 才能开仓；
- 而是让 base setup 先给方向，只在明显 `bad regime` 时 veto。

这确实是当前还剩下的最自然单轴：
- 从“它决定能不能开仓”
- 改成“它只负责别在坏状态里硬开仓”。

但本轮**不把这刀写成正式 `Rank 26b`**，原因也很明确：
1. 这已经开始改变它在系统里的角色，不再只是原 rank 的窄修正，而是在改“gate 的职责”；
2. 当前没有新的局部证据证明 `veto-only` 比 `strict gate` 更诚实，只是理论上听起来更温和；
3. 这条线很容易滑向“再试一个版本看看”，而不是当前 brief 要求的 **足够窄、足够有证据支撑的单轴派生**。

所以这刀目前只能算“最像下一刀”，还不能算“值得立刻起草的新 hypothesis”。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
- 原 rank 的 `park` 仍有明确审计意义；
- 它最自然、也最诚实的救法（剥掉弱腿，做 `ETH+SOL-only` narrow-scope recheck）已经被执行并失败；
- 剩下最像的一刀（改成 veto-only overlay）目前证据还不够，写成 `Rank 26b` 更像继续给它续命，而不是提出一个真正扎实的新窄假设。

## 6) trade on / trade off 结论
本轮**不形成**新的 `Rank 26b`。

更诚实的保留口径是：
- `trade on` 故事并不荒谬，甚至曾经一度接近可升格；
- 但原 rank 当前已经把最自然的 salvage budget 用掉了；
- 若后面真要重开，应该等到出现新的、能支撑“entry gate -> veto-only overlay”这条单轴的额外证据，而不是现在硬写一个名字先进队列。

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 26 itself.
It records that the most obvious honest salvage path — **keep the rule, remove the weak BTC leg, and check whether ETH+SOL-only can survive as a narrow pilot** — has already been spent and still failed to produce a clean `P3` read. So the honest action this round is to **keep Rank 26 parked**, not draft `Rank 26b`.

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
