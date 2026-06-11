# Rank 234 / multiday MAX lottery XS continuation — survivor horizon ladder → promote_P2

- 时间：2026-03-29 10:00 UTC
- 执行角色：bot3
- 当前执行小点：`Rank 234 / multiday MAX lottery XS continuation`
- 动作：作为当前 survivor 的唯一 follow-up，在 liquid USDT perp universe 上做 `MAX horizon ladder` 最小快检：并排 `1h / 24h / 72h formation × 1h / 4h / 8h holding`，并把 `MAX rank` 与 `plain return-rank` 做同口径对照，只回答更长 formation 是否真的从 fade 翻成 continuation，且是否不是 plain momentum 换名。
- 产出 artifact：
  - `reports/artifacts/rank234_survivor_followup/selected_universe.csv`
  - `reports/artifacts/rank234_survivor_followup/universe_fetch_meta.csv`
  - `reports/artifacts/rank234_survivor_followup/summary.csv`
  - `reports/artifacts/rank234_survivor_followup/max_vs_return_rank.csv`
  - `reports/artifacts/rank234_survivor_followup/decision.json`

## 本轮正式结论
**本轮正式结论：`promote_P2`。**

原因不是“MAX 全面打赢 plain momentum”，而是更关键的 survivor 问题已经被回答：

> 在 liquid USDT perp 的最小诚实快检里，**较长 formation 的 MAX 分支确实出现了成本后 continuation**，而且至少有一格仍保留了**相对 plain return-rank 的独立信息**；与此同时，`1h formation` 也保留了更接近短窗 fade / 弱信号的那一面。

这已经足够说明：`Rank 234` 不是论文层空想，也不是单纯把 plain return ranking 换个名字。它现在最诚实的状态不再是继续停在 survivor，而是进入 `Active P2` 做正式 admission。

## 本轮怎么做的
### 1) Universe 与执行口径
- 数据：Binance USDⓈ-M perpetual 公共 `1h` klines
- 回看：最近 `45d`
- universe：先按 `24h quote volume` 取前 `50`，再保留 `listing_days >= 180`、纯字母 base、非稳定币 base 的前 `24` 个 liquid symbols
- 实际纳入：`BTCUSDT / ETHUSDT / SOLUSDT / SIRENUSDT / DOGEUSDT / XRPUSDT / TAOUSDT / HYPEUSDT / ONTUSDT / ZECUSDT / PTBUSDT / BNBUSDT / PIPPINUSDT / SUIUSDT / ADAUSDT / STOUSDT / PLAYUSDT / LINKUSDT / WLDUSDT / ENAUSDT / BCHUSDT / DOTUSDT / CHZUSDT / FETUSDT`
- 组合：每次做多 top `20%`、做空 bottom `20%`
- 执行：`next-bar open`
- 持有：`1h / 4h / 8h`
- 约束：按持有期步进、`no-overlap`
- 成本：`5 bps/side`

### 2) 两条并排对照臂
- `MAX rank`：formation 窗里最大的单小时收益
- `plain return-rank`：formation 窗累计收益

这样做的目的不是卷参数，而是直接回答：
1. 较长 formation 是否真的保留 continuation；
2. 这条 continuation 是否至少在某些格子里不是 plain return-rank 的完全同义重复。

## 关键结果
### A. `1h formation` 没有给出更强的 longer-formation continuation 证据
- `1h × 1h`：`MAX = -8.04 bps/trade`
- `1h × 4h`：`MAX = +14.38 bps/trade`
- `1h × 8h`：`MAX = +38.00 bps/trade`

短 formation 不是全面崩掉，但它的 `1h × 1h` 明显为负，说明短窗 MAX 至少没有统一的“继续追强”结论，和 digest 里提出的 horizon sign split 是一致的。

### B. 较长 formation 已明确出现成本后 continuation
`MAX rank` 的较长 formation 结果：
- `24h × 4h`：`+34.42 bps/trade`
- `24h × 8h`：`+75.37 bps/trade`
- `72h × 4h`：`+22.45 bps/trade`
- `72h × 8h`：`+42.73 bps/trade`

这已经足够回答 survivor 核心问题的第一半：

> **更长 formation 的 MAX 分支在 liquid perp 下确实可以表现为 continuation，而不是统一 fade。**

### C. 它并非每一格都输给 plain return-rank
虽然 `plain return-rank` 的总体最好格更强（`24h × 8h = +98.15 bps/trade`），但 `MAX` 并不是处处被它压住：
- `24h × 1h`：`MAX - return-rank = +0.09 bps`
- `24h × 4h`：`MAX - return-rank = +2.16 bps`
- `72h × 1h`：`MAX - return-rank = +2.86 bps`

其中最重要的是：
- `24h × 4h` 这一格里，`MAX` **成本后为正**，且 **胜过 plain return-rank**。

这正好满足当前 survivor follow-up 的判定标准：

> **只要较长 formation 的 MAX 分支在成本前后保留清晰 continuation，且相对 plain return-rank 仍有独立信息，就应 `promote_P2`。**

## 为什么这轮应直接升 P2，而不是 keep_P1 后转 background
因为当前这轮不是在问“MAX 最终能不能 paper trade”，而是在问一个更窄的 survivor admission 问题：

1. 更长 formation 是否真的从短窗 fade/弱信号那一端翻成 continuation？
2. `MAX` 是否至少还有一部分不是 plain return-rank 的完全换名？

这两问现在都已经得到肯定回答：
- 第一问：**是**，`24h/72h × 4h/8h` 多格成本后为正；
- 第二问：**也是**，`24h × 4h` 等格子里 `MAX` 仍跑赢 `plain return-rank`。

因此按 policy，survivor 的唯一 follow-up 已诚实完成，最合理的写回不是继续拖，而是：

**`Rank 234` 正式进入 `Active P2 slot`。**

## 同时要保留的负面信息
这条线也还没有强到可以越过 `P2`：
- `plain return-rank` 的整体 strongest pocket 仍比 `MAX` 更强；
- `MAX` 的独立增量主要只在部分格子出现，不是全面优势；
- 当前样本只是 `45d / 1h / top-24 liquid perp` 的最小 ladder，离 time stability / cross-asset stability / parameter stability / honesty-execution realism 的完整 `P2` admission 还差正式收口。

所以这轮的正确动作是 **升 `P2`，不是直接升 `P3`**。

## 应写回 runtime 的系统认知
`Rank 234 / multiday MAX lottery XS continuation` 的唯一 survivor follow-up 已完成：在最近 `45d`、Binance liquid USDT perp `1h` ladder 下，`24h/72h formation` 的 `MAX rank` 已在多格上表现出成本后 continuation，而且在 `24h × 4h` 等格子仍保留了相对 `plain return-rank` 的独立增量；同时 `1h × 1h` 仍为负，支持这是一条 formation-horizon-conditioned MAX family，因此本轮应从 survivor 直接 `promote_P2`。

## 一句话 result
`Rank 234 / multiday MAX lottery XS continuation` 的 liquid perp `1h` horizon ladder 已证明较长 formation 的 `MAX` 分支确有成本后 continuation，且在 `24h × 4h` 仍胜过 `plain return-rank`，因此 survivor 问题已被正面回答，本轮直接 `promote_P2`。
