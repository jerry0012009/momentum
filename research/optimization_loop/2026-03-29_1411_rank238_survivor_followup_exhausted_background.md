# Rank 238 / UTC schedule_score shared gate × continuation admission / reversal veto — survivor follow-up exhausted → background/P0

- Time: 2026-03-29 14:11 UTC
- Target: `Rank 238 / UTC schedule_score shared gate × continuation admission / reversal veto`
- Source: `research/quant_digests/2026-03-29_1022_utc-schedule-macro-timestamp-gate.md`
- Verdict: `survivor follow-up exhausted -> background/P0`

## What was tested
按 first verdict 里冻结的最小口径，只检验**无条件 UTC schedule gate**，不把宏观事件窗偷混进来：

- `schedule_score = minute∈{00,15,30,45} + hour∈{00,12,13,14,15,16} + weekday∈{Tue,Wed,Thu,Fri}`
- continuation proxy：`BTCUSDT` perpetual `5m` 上，过去 `3` 根累计涨跌幅绝对值 ≥ `18 bps` 时顺势持有 `3` 根 bar
- reversal proxy：同一市场 `5m` 上，单根冲击绝对值 ≥ `12 bps` 时反向持有 `3` 根 bar
- 对照方式：
  1. `baseline`：不加 gate
  2. `gated`：continuation 只在 `score >= 2`；reversal 只在 `score <= 1`
  3. `inverse`：反着放行
- 成本：统一扣 `6 bps` round-trip，样本区间约 `2026-01-10 11:15 UTC ~ 2026-03-29 14:10 UTC`，共 `22,500` 根 `5m` bar

## Core results
### 1) continuation 侧没有留下 post-cost shared-gate 增量
- baseline：`8,248` 笔，`mean_net_bps = -6.563`
- gated (`score >= 2`)：`3,043` 笔，`mean_net_bps = -6.737`
- inverse (`score <= 1`)：`5,205` 笔，`mean_net_bps = -6.461`

continuation 侧没有出现“对的 UTC 时段明显更好、反向时段明显更差”的 shared timing gate 分层；gated 版比 baseline 更差，inverse 反而略好。

### 2) reversal 侧同样没有形成可复现的 veto 分层
- baseline：`7,083` 笔，`mean_net_bps = -5.452`
- gated (`score <= 1`)：`4,219` 笔，`mean_net_bps = -5.492`
- inverse (`score >= 2`)：`2,864` 笔，`mean_net_bps = -5.394`

reversal 侧也没有出现“冷时段放行明显更好、热时段 veto 明显更差”的一致分层；gated 与 inverse 只在噪声范围内来回，没有诚实的 post-cost 改善。

## Why this is enough to close the survivor slot
`Rank 238` 的 survivor follow-up 目标不是证明 UTC 时钟效应在论文里存在，而是证明**同一套 frozen schedule_score** 能同时给一条 continuation alpha 和一条 reversal alpha 带来共享、可复现、post-cost 有效的 timing 增量。

这一步没有做到：
- 两侧都没形成正向、清楚的 gated > baseline > inverse 顺序；
- continuation / reversal 都停留在“有些时段更活跃”的摘要层，尚不足以升格为 desk 默认 shared gate；
- 若继续推进，只会变成再改 proxy / 再调阈值 / 再补宏观条件的开放式拖延，不符合 survivor 只能有一次最小 decisive follow-up 的规则。

## Honest boundary
这不等于论文错了，也不等于 UTC 时钟信息永远没用；更像是：

- **“无条件 shared schedule_score” 这版主语不够强**；
- 真正可能有价值的，可能是以后单独拆出来的更窄对象，例如：
  - `macro-event-conditioned clock gate`
  - 某一条单独 raw alpha 的专用 execution window
  - 独立的 UTC clock raw alpha（而不是 shared filter）

但那已经不是本轮 `Rank 238` 的 survivor follow-up 主语，不能靠继续 keep_P1 来拖。

## Result sentence
`Rank 238` 的唯一 survivor follow-up 已完成：同一套 frozen `schedule_score` 在 `5m BTC` continuation admission 与 reversal veto 两侧都未留下 gated 优于 baseline 且 inverse 反证成立的 post-cost 分层，因此这条 `UTC shared gate` 主语证据不足，诚实用尽预算后回 `background/P0`。
