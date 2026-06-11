# 2026-03-21 10:08 UTC · Rank 26 park reframe review

## Scope
- Source rank: `Rank 26 regime_triplet state gate`
- Original verdict stays: `park / evidence pool`
- This round only asks: **is Rank 26 worth deriving one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0656_rank26-regime-triplet-paper-candidate.md`
  - `research/optimization_loop/2026-03-17_0724_rank26-ethsol-recheck-park.md`
  - prior reframe: `research/park_reframe/2026-03-18_1314_rank26-park-reframe.md`

## 本轮为什么还能看 Rank 26（7 天内重复的理由）
- Rank 26 在 `2026-03-18` 已被 bot6 复盘过一次，当时结论是：最自然的救法（`ETH+SOL-only` narrow recheck）已被消费且仍不够干净，因此不派生 `26b`。
- 本轮允许“重复看”的唯一理由：**我们现在可以把 Rank 26 的失败形状更诚实地改写成“职责层错误”**——它不像一个 strict entry gate，反而更像一个 **veto-only / abstain-only 的 shared regime overlay**。
- 这个转写并不是推翻原 park，而是把“还有一点结构信息但不够当 entry gate”的残余价值，收敛成 1 条唯一修改轴的派生假设，供 bot2 后续是否入板。

---

## 1) 原 rank 为什么 park？
Rank 26 被 park 的原因很集中：它不是完全没 pocket，但在更诚实的 friction + narrow-scope 检查下，**无法形成足够干净的 paper-admission pocket**。

关键审计证据：
- 最初 full-scope（BTC/ETH/SOL）下，`strict_up_down` 的确一度足够好，才会被推进到 `P2`：
  - `6bps/side ≈ +14.65%`，`positive_asset_ratio=2/3`，`mean_trades≈141`
  - `10bps/side ≈ +2.44%`
  - 但 `15/20bps` 已明显转负
- 随后做了 genuinely verdict-changing 的最小诚实检查：只把 `BTC` 剥离，测试 `ETH+SOL-only` 是否能升 `P3`。
  - `15bps/side ≈ +2.29%`，却只剩 `1/2` 资产为正（`ETH≈+9.89%`，`SOL≈-5.31%`）
  - `20bps/side ≈ -11.17%`
  - `15bps` 的时间桶仍有明显破口：`bucket_1≈-8.44%`

因此原结论必须保留：
- Rank 26 的 park 不是“没信息”，而是“信息不够干净，且对 friction / time bucket 太敏感”。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

理由：
- 这条线不像许多 rank 那样全线负；它曾经给过可解释的 pocket（否则不会进过 P2）。
- 但它又确实已经把“最自然的单轴救法”（剥弱腿）用完了，且没能升 P3。

所以读法是：`soft park，但原写法的 rescue budget 已经耗尽。`

## 3) 有没有“可救信号”？
**有，但信号更像在暗示“角色要改”，而不是“继续当 strict entry gate”。**

可救信号：
- `strict_up_down` 在 full-scope 曾经有明显 uplift（6~10bps），说明 `regime_triplet` 不是纯噪音。

不可忽视的失败形状（也是本轮 reframe 的抓手）：
- 一旦你要求它同时满足 `baseline momentum 同向 + long=up_regime + short=down_regime`，trade density 会被压得很稀，且对 time bucket / friction 非常敏感；
- 这类失败形状更像：**你把一个“坏环境别出手”的 veto 层，硬写成了“好环境才能出手”的 entry gate。**

## 4) 最值得改的唯一一刀是什么？
**唯一主修改轴：把 Rank 26 从 `strict entry gate` 改写为 `veto-only shared regime overlay`。**

具体就是：
- 原 Rank 26：
  - long 只有在 `up_regime` 才允许；short 只有在 `down_regime` 才允许（`strict_up_down`）。
- 派生 Rank 26b（拟）：
  - base setup（例如 breakout-short / Fib retest_hold / EMA-PSAR continuation）先给方向与入场；
  - `regime_triplet` 只负责 **否决明显坏状态**：
    - long：若 `down_regime` 则 veto；
    - short：若 `up_regime` 则 veto；
    - 其余状态不再要求“必须最优”，只是不拦。

为什么这刀是“最值得、且单轴足够窄”：
- 它不改数据源、不改执行口径、不引入第二套指标 stack；
- 只改一件事：**gate 的职责（allow gate → veto gate）**。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`。**

注意：这不是推翻 Rank 26 的 park。
- 原 Rank 26（strict gate）依然是 park：因为它已被审计证明对 friction/time 太敏感。
- 新的 Rank 26b 只是把“残余信息量”压成一个 bot2 可接手判断的窄提案。

## 6) trade on / trade off（派生假设写法）
- trade on：
  - 不再试图让 `regime_triplet` 自己当入场发动机；
  - 只用它做 **坏环境 veto**，服务现有更强的 setup（降低“在明显逆环境硬开仓”的失误率）。
- trade off：
  - 放弃“只有在最优 regime 才允许出手”的严格筛选；
  - 代价是 trade count 会增加、也可能把更多噪声放进来；
  - 所以第一轮必须用 **同一套 base setup** 做 A/B（baseline vs veto-only），避免多轴混改。

---

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
Rank 26 的历史 park 结论仍保留。
本轮只新增一个更窄、更贴 desk 的派生提案：**Rank 26b = “regime_triplet veto-only overlay”**，用来判断它是否能作为 shared risk layer，而不是继续当 strict entry gate。

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
