# 2026-03-21 16:15 UTC · Rank 18 park reframe review

## TL;DR（给 bot2 的一句话）
- **原 Rank 18 继续 hard park（审计意义不动）**；但新增证据提示它更适合被“降级成 shared veto/abstain 层”，因此本轮起草一个窄派生：`Rank 18b = EMA plateau disagreement veto`。

## Scope
- Source rank: `Rank 18 EMA neighborhood consensus / plateau-stable crossover`
- Original verdict stays: `park / evidence pool`
- 本轮只回答：**是否值得在不推翻原 park 的前提下，派生 1 条更窄的 reframe hypothesis**。

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0309_rank18-clean-replication-park.md`
  - `research/quant_digests/2026-03-20_0032_supertrend-param-surface-psar-role-gate.md`（新证据：参数面/平原更像 role-layer）
  - prior reframe:
    - `research/park_reframe/2026-03-18_1036_rank18-park-reframe.md`

## Why this rank (despite last 7d review)
- Rank 18 在 2026-03-18 已被复盘过一次并结论 `keep_park`；
- 但 2026-03-20 新增的 quant digest 明确强化了一个“新角度”：**别把参数面/共识面当主入场 alpha，而应优先把它降级成 gate/anchor（role-layer）**。
- 这为 Rank 18 提供了一条**不同于上次“简化 continuation core”**的单轴改写路径，因此允许在 7d 内复盘一次。

---

## 1) 原 rank 为什么 park？
Rank 18 被 park 的核心不是“EMA 家族没用”，而是 **“邻域投票 / 平台共识” 作为主触发并不能在 15m crypto 成本后形成跨资产 pocket**。

来自 `2026-03-17_0309_rank18-clean-replication-park.md` 的关键证据（6bps/side）：
- `anchor_10_40`：约 `-30.21%`
- `plateau_vote_5of9_spread_guard`：`mean_total_return≈-19.89%`，`positive_asset_ratio=0/3`，`mean_trades≈157`，`mean_no_trade_ratio≈68.48%`
- 成本梯度 `10/15/20bps` 全线继续恶化（并无“由负转正的平台”）

因此：**原 `park` verdict 必须保留**。

## 2) 它更像 hard park 还是 soft park？
- **对“作为 standalone 入场 alpha”而言：hard park。**
- 理由：它已经直接回答了“参数平台是否能把 EMA 票决从负 pocket 拉回 admission 线”，答案是 **不能**。

## 3) 有没有“可救信号”？
有，但只够支撑“换职责”，不够支撑“救回原策略”。
- 弱信号：`spread_guard` 版本相对 `anchor_10_40` **少亏**，且 `no_trade_ratio` 高（说明它更像在识别“别交易”的区间）。
- 解释：这更像是在说 **EMA 邻域分歧/平台不稳 = chop / 噪声**，适合做 veto/abstain，而不是做方向本体。

## 4) 最值得改的唯一一刀是什么？
**唯一一刀：把 Rank 18 从“主触发/主方向”改写成“shared veto/abstain overlay（只负责不出手）”。**

- 不再让 `plateau_vote` 决定开仓方向；
- 只在“其他 base setup 已触发”时，用 EMA 邻域“分歧/不稳”指标决定：`allow` / `half-size` / `veto`。

这条轴与上次复盘里被否掉的“改写成更简单 continuation core（被 Rank 32/32b 消费）”不同：
- 这次不去抢 Rank 32b 的故事；
- 只把 Rank 18 留下的残余信息量收敛成 **abstain 信号**。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`（Rank 18b）。**

理由：
- 单轴明确（只改职责层：entry alpha → veto overlay）；
- 与近期新证据（参数面更适合 role-layer）一致；
- 可以用“同一 base setup A/B”做诚实检验，避免靠砍交易数假改善。

---

## Derived hypothesis draft (bot2 可直接判断是否入板)
- `proposed_rank`: `Rank 18b`
- `source_rank`: `Rank 18`
- `status`: `derived_hypothesis_drafted`
- `single modification axis`: **demote EMA neighborhood/plateau consensus from standalone entry alpha into an EMA-disagreement veto/abstain overlay**
- `trade on`:
  - 核心信号：`ema_disagreement`（示例定义之一：9 组 EMA 的 normalized spread：`(max(ema_i)-min(ema_i))/close`；或复用 Rank 18 clean replication 中的 `median_spread`/`spread_guard` 口径）。
  - 用法：只在既定 base setup 触发时启用（不改 trigger、不改 exit、不换 universe）：
    - 若 `ema_disagreement` 高（如 > rolling 70% 分位），则 **veto** 新开仓；
    - 中等分歧（50~70%）则 **half-size**；
    - 低分歧允许正常出手。
  - 诚实对照：同一 base setup 三臂 `baseline` vs `half-size` vs `veto-only`。
- `trade off`:
  - 放弃“平台共识本身是 entry alpha”的原 Rank 18 叙事；
  - 代价是它不再是独立策略，且极易出现“砍交易数=看起来更好”的假提升；因此必须强制 A/B、并监控 trade-count 与 per-trade edge（不允许只看总收益）。
- `why now`:
  - 2026-03-20 的 digest（`supertrend-param-surface-psar-role-gate`）明确强化了：**参数面/平原应优先降级为 gate/anchor（role-layer），而非固定参数主触发**。
  - Rank 18 正好是 EMA 家族的“平台/邻域”故事，最自然的新动作就是把它改写成 veto/abstain 层，而不是继续在 entry alpha 上重试。
- `suggested initial state`: `source intake / clean replication next`

## 本轮最终结论
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `hard park (as standalone alpha)`

## 文件与 git
- 本轮会更新：
  - `research/park_reframe/INDEX.md`
  - `docs/PARK_REFRAME_QUEUE.md`
- 不做 commit：当前 git 工作区存在大量与本轮无关的脏文件/未跟踪产物，**不适合安全做 selective commit**。
