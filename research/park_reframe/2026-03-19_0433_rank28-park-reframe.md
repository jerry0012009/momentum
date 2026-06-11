# 2026-03-19 04:33 UTC · Rank 28 park reframe review

## Scope
- Source rank: `Rank 28 cross-market intraday leader-laggard TSMOM`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 28 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-19_0214_rank8-park-reframe.md`
  - `research/park_reframe/2026-03-18_2357_rank7-park-reframe.md`
  - `research/park_reframe/2026-03-18_2145_rank4-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0827_rank28-crossmarket-intraday-intake.md`
  - `research/optimization_loop/2026-03-17_0841_rank28-crossmarket-clean-replication.md`
  - `research/quant_digests/2026-03-19_0237_alt-btc-rs-breadth-shared-gate.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- It is a good `bot6` candidate because the original line did not fail from total irrelevance of cross-market information; it failed because the direct `leader -> laggard follow-through` trade was too blunt and stayed negative even when kept cheap and crypto-only.
- A fresh digest now offers a narrower reinterpretation: **stop asking cross-market relative strength to trigger a lag trade directly; let it act as shared breadth/regime context for existing continuation vs retest lanes.**

## 1) 原 rank 为什么 park？
Rank 28 被 park，不是因为“跨市场 / 跨币相对强弱”完全没信息，而是因为它在当时被写成了一个 **同 session 里 leader 先动、laggard 尾段跟随** 的直接交易模型，而这版最小 clean replication 没有形成可过门槛的 pocket。

原 clean replication 的关键证据：
- primary `funding_8h_q60 @ 6bps/side`：`mean_total_return≈-16.58%`、`positive_asset_ratio=0/3`、`mean_false_follow_ratio≈66.42%`、`mean_trades≈124`
- 相对最不差的 `utc_day_q70 @ 6bps/side` 也仍约 `-5.28%`、`0/3` 资产为正
- `Light Stability Pack` 四项全 fail：时间 `0/3`、参数邻域 `0/3`、跨标的 `0/3`、成本梯度 `0/4`

更直白地说：
- 原 Rank 28 不是“完全没样本”；
- 它是 **有样本，但直接去赌 laggard 尾段跟随这件事不赚钱**；
- 因此原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- 作为一个直接 `leader-laggard follow-through` 入场策略，它已经该停；
- 但它留下的 blocker 更像是 **角色放错了**，不是“跨币相对强弱 / 领先落后关系”这类信息一定没用。

更诚实的读法是：
- `hard park` 的部分：原 direct follow-through 交易版本已经被最小 clean replication 审计消费；
- `soft park` 的部分：cross-market relative strength 也许仍适合作为更上层的 `breadth / regime` gate，而不是同 session 尾段追 laggard。

## 3) 有没有“可救信号”？
**有。**

可救信号不在“继续微调 lead threshold / session 切法”，而在把 cross-market 信息从 **直接跟随入场** 降级成 **shared breadth context**。

主要有三点：
1. Rank 28 失败的核心不是 lookahead、样本为零或数据依赖不可得，而是 `leader -> laggard` 这个直接交易形状太粗；
2. 它保留的真正剩余价值，是“市场里别的币相对 BTC / 相对彼此的强弱分布，可能能告诉你当前更像 continuation 还是更像别乱追”；
3. 最新 `alt-vs-BTC RS breadth` digest 正好给出一个只改角色、不改 cross-market 主题的窄改写：把单币 RS / 领先-落后关系改写成 **breadth gate / sizing overlay**。

翻成人话：
- 原 Rank 28 失败，不等于“相对强弱没价值”；
- 更像是“别拿它直接赌尾段补涨，先拿它判断大多数币现在是不是在顺着 BTC 风险偏好一起走”。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀：把 Rank 28 的 cross-market relative-strength 信息，从 `leader-laggard direct follow-through entry` 改成 `alt-vs-BTC RS breadth shared regime gate`。**

也就是：
- 不再让“某个 leader 先动、某个 laggard 后跟”直接触发一笔新交易；
- 改成先统计可交易 alt 池里有多少币相对 BTC 更强 / 更弱，再把它接到现有 lane：
  - `breadth_pos` 高时，更偏向放行 `Fib retest_hold / EMA continuation long`
  - `breadth_neg` 高时，更偏向放行 `breakout-short`
  - 中性区则 `half-size / veto`
- 第一轮只允许比较 `baseline vs breadth_gate vs breadth_sizing`；不能顺手偷带新的 entry、exit、第二层 regime stack 或新的外部宏观数据。

为什么这是一刀而不是多轴大改：
- 核心主题没变，仍是 **cross-market relative strength**；
- 数据仍是公开 crypto 价格序列；
- 只改了它的 **角色层级**：从直接 lag trade alpha，降级成 shared regime / breadth gate。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`。**

理由：
- 原 `park` 结论完整保留，尤其“direct leader-laggard tail follow-through 不够诚实”这点不推翻；
- Rank 28 的最小 clean replication 已把“继续修 direct lag trade”这条旧救法基本消费掉；
- 最新 digest 提供了一个与原 rank 高度同主题、且只改一层角色定义的窄 reframe：**cross-market RS 不直接开仓，只做 breadth gate。**

## 6) trade on / trade off 结论
### Proposed derived hypothesis
- `proposed_rank`: `Rank 28b`
- `source_rank`: `Rank 28`
- `single modification axis`: `demote cross-market intraday leader-laggard signal from direct lag-trade entry to an alt-vs-BTC RS breadth shared regime gate`
- `trade on`: `不再根据 leader 先动、laggard 后跟直接开仓；而是先在固定 alt 池里计算 alt-vs-BTC RS breadth（如 breadth_pos=share(rs_i>0), breadth_neg=share(rs_i<0)），再只把它用作 shared allow/deny/sizing gate：breadth_pos 高时优先放行 Fib retest_hold / EMA continuation long，breadth_neg 高时优先放行 breakout-short，中性区 half-size 或 veto。第一轮只测 baseline vs breadth_gate vs breadth_sizing。`
- `trade off`: `放弃“cross-market lead-lag 本身就是同 session 直接 alpha”的原 Rank 28 读法，换取更诚实的 market breadth / crowd alignment 角色；代价是它不再是独立策略，而且若 breadth 阈值太激进，可能只是靠砍单美化结果，因此第一轮必须只测 breadth 层本身，不偷带新 trigger / exit / universe 漂移。`
- `why now`: `原 Rank 28 clean replication 已很清楚地证明 direct leader-laggard follow-through 在 crypto-only 最小版本里成本后持续为负，但这更像是交易形状太粗，不是 cross-market relative-strength 主题彻底失效；最新 alt-vs-BTC RS breadth digest 又正好提供了一个只改角色、不改主题的窄 reframe。`
- `suggested_initial_state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 28 itself.
It keeps the original `park` intact. The only new move is a narrower role downgrade: **`Rank 28b = stop treating cross-market leader-laggard as a direct lag trade, and test it only as an alt-vs-BTC RS breadth shared regime gate for existing lanes.`**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
