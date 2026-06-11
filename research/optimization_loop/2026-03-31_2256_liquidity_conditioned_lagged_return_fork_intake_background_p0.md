# Rank intake verdict — liquidity-conditioned lagged-return fork

- Time: 2026-03-31 22:56 UTC
- Target: `liquidity-conditioned lagged-return fork`
- Source digest: `research/quant_digests/2026-03-31_2018_liquidity-conditioned-lagged-return-fork-alpha.md`
- Verdict: `background/P0`（不进入前排，不分配 Rank）

## What was checked
只做本轮 policy 允许的最小 fresh-intake 首判：判断这条线是否已经具备可审计的 raw-alpha skeleton，并且当前可交易宇宙里是否存在足够诚实的 transfer path，值得至少给 `keep_P1`。

本轮直接核对了：
1. digest 中给出的策略骨架是否完整；
2. digest 所引用的本地 artifacts 是否支持它声称的 transfer 方向；
3. 当前证据是否足以支持进入前排继续做唯一 survivor follow-up。

## Findings
### 1) 论文读法本身有价值，但更像 research heuristic，不是已站稳的 desk candidate
这条线最有价值的部分是：
- 同一个 `lagged return` 信号，可能需要按 `liquidity bucket` 分叉解释；
- 高流动性桶更可能做 continuation，低流动性桶才谈 reversal。

这个 framing 对后续 desk 研究有用，但“有研究启发”不等于“已形成值得占用前排预算的 candidate”。

### 2) digest 的关键 transfer claim 与本地 daily artifact 不自洽
digest 明写：
- 全样本 `loser-minus-winner = -6.5 bps/day`
- 高流动性桶（top 10% ADV20）`winner-minus-loser = +6.1 bps/day`
- Top-20 最活跃样本 `winner-minus-loser = +26.8 bps/day`

但直接读取其引用的本地 daily artifact：
- `reports/artifacts/quant_digests/liquidity_regime_daily_reversal_momentum_20260331.csv`

按 `mom_highliq` 全样本均值重算，得到的是约 **-5.0 bps/day**，而不是 digest 文案里的 `+6.1 bps/day`。这说明当前 intake 包里至少存在以下一种问题：
- digest 文案引用了另一套未落库口径；
- artifact 列名/方向与文案不一致；
- 或 transfer summary 本身还没做完诚实对账。

在这种口径未对齐状态下，不能把“高流动性 continuation 已看到日频迁移”当成可靠前提。

### 3) 15m intraday proxy 只有“可继续研究”的薄迹象，还不够支持前排 survivor 预算
另一份 intraday artifact：
- `reports/artifacts/quant_digests/liquidity_conditioned_intraday_momentum_15m_20260331.csv`

按文件均值重算：
- `mom1h` ≈ `+1.03 bps`
- `mom4h` ≈ `+11.60 bps`
- 样本切片数 `n = 888`

这能支持一句比较弱但诚实的话：
- 在 top-liquidity spot proxy 上，`24h lagged return` 做 intraday continuation **不是完全空想**。

但它还不支持更强的话：
- after-cost 在当前 shortable perp universe 已足够稳；
- 可直接升成 `keep_P1` 并占用唯一 survivor follow-up；
- 低流动性 reversal 分叉已经有诚实 transfer path。

原因很直接：
- 当前只是 spot proxy，不是统一的 perp shortable universe；
- 还没有把 funding / basis / short-side implementation realism 纳入口径；
- 1h edge 很薄，4h proxy 虽有正值，但还没有 cross-asset / parameter / cost ladder 的最小 admission；
- 低流动性 reversal 仍主要停留在论文样本叙事，没有当前可交易宇宙下的诚实迁移证据。

## Decision
本轮首判直接收口为：

> `liquidity-conditioned lagged-return fork` 目前更像一条有用的 research framing，而不是已具备诚实 transfer check 的前排 raw-alpha candidate；且 digest 的 daily 高流动性 continuation claim 与所附 artifact 口径未对齐，因此本轮不进入前排，不给 `keep_P1`，直接记为 `background/P0`。

## Why no Rank
按 policy，只有 fresh intake 达到 `keep_P1` 或更高 verdict 时才必须分配正式 Rank。
本轮 verdict 是直接 `background/P0`，因此不分配 Rank。

## Runtime impact
- 不占用 `Surviving candidate slot`
- 不占用 `Active P2 slot`
- `cycle_plan` 当前第 2 项可标记为 `done`
- 下一轮可继续看后续 pending intake
