# 2026-03-21 18:15 UTC · Rank 18 park reframe review

## 邮件摘要（给 bot2 / Jerry 可直接扫读）
- source_rank：`Rank 18 / EMA neighborhood consensus (plateau vote)`（原 verdict 保持 `park / evidence pool`）
- 本轮结论：`derived_hypothesis_drafted`（新增 `Rank 18b` 窄派生提案；不推翻原结论）
- 原 rank 为何 park：standalone entry 在 BTC/ETH/SOL 15m 上 **全资产为负**，且成本/参数邻域都不出现由负转正平台
- soft vs hard：更像 **soft park**（主题可能有信息，但被放在“当主入场引擎”这个职责层里用错了）
- 可救信号：相对 anchor 少亏（-30% → -20%），且天然带来高 `no_trade_ratio`（更像“abstain 过滤层”而非 entry）
- 唯一修改轴（single modification axis）：把 Rank 18 从 **standalone entry** 降级成 **shared abstain / trend-readiness veto gate**（只做 allow/deny/half-size；不改原 setup 的 entry/exit）
- trade on / trade off：用 plateau 共识强弱来“少做低质量段”，代价是 trade density 下降、可能只是在切样本美化；因此第一刀必须是 strict A/B（baseline vs abstain-only gate）

## Scope
- Source rank: `Rank 18 / EMA neighborhood consensus / plateau-stable crossover`
- Original verdict stays: `park / evidence pool`
- This round only asks: **after the new “abstain / no-trade band” evidence, does Rank 18 deserve one narrower derived reframe hypothesis?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0309_rank18-clean-replication-park.md`
  - `research/quant_digests/2026-03-20_0539_alpha-beta-abstain-profit-window-verdict.md`

## Why this rank this round
- 严格说，`Rank 18` 在最近 7 天内已经被 desk 级结论压成 `hard park`（bot6 也在 2026-03-18 复盘过“暂无单轴可切”）。
- 但过去 72h 新增了一条**直接相关的新证据**：`双阈值 abstain / no-trade band` 的框架（见 2026-03-20 digest）强调：
  - 低位移/小波动段应 **不交易**（abstain），而不是硬逼信号当 alpha；
  - 这类层更像三条收口线的 shared filter，而不是 standalone entry。
- Rank 18 的 clean replication 结果本身也提示：它更像“自带 abstain”的结构（`mean_no_trade_ratio≈68%`），但被错误地当成主入场引擎去评估，导致“少亏但仍负”的结论。

---

## 1) 原 rank 为什么 park？
来自 clean replication 的硬失败（standalone entry）：
- `plateau_vote_5of9_spread_guard`：`mean_total_return ≈ -19.89%`
- `positive_asset_ratio = 0/3`
- `mean_trades ≈ 157`（并不算稀到可以用“样本太少”遮羞）
- 成本梯度 `10/15/20bps` 继续恶化（约 `-29.36% / -39.63% / -48.42%`）
- 参数邻域没有出现“由负转正的平台”

翻成人话：
- 这不是“差一点点”，而是 **standalone EMA 平台共识当入场 alpha** 这条路在当前 15m crypto pocket 下站不住。
- 因此原 `park` verdict 仍有完整审计意义，不能被“换个阈值就行”推翻。

## 2) 它更像 hard park 还是 soft park？
这轮我把它读成：**`soft park`（但仍然 park）**。

理由：
- 结果是负的，所以不能 pretend 成“好策略”。
- 但它相对 `anchor_10_40` 少亏（约 `-30.21% → -19.89%`），说明**EMA 邻域共识/平台这件事可能仍有一点信息量**；只是它更像应该被放在 `abstain / trend-readiness` 的职责层，而不是被迫当“直接开仓的 alpha”。

## 3) 有没有“可救信号”？
有，但信号的含义需要换读法：
- **可救信号不是“它快转正了”**（并没有）；
- 而是：
  1) 该 rank 天然带来较高 `no_trade_ratio`，更像一种“减少低质量交易段”的机制；
  2) 新 digest 提供了更合理的评估语义：把这种机制当成 `abstain gate` 来评估，而不是硬按 standalone alpha 打分。

## 4) 最值得改的唯一一刀是什么？
**唯一主修改轴：把 Rank 18 从 standalone entry 降级为 shared abstain / trend-readiness veto gate。**

具体写法（不引入第二轴）：
- 不再使用 Rank 18 作为“开仓触发”；
- 只在其他已冻结 setup 触发时，额外计算 `plateau_consensus_ok`：
  - `plateau_vote_5of9_spread_guard == True`（或更宽松 `row_consensus_2of3` 做对照臂）
- Gate 行为只允许三档之一（第一轮优先只做最小二臂）：
  - baseline：无 gate
  - abstain-only：`consensus_ok==False -> veto new entry`（只 veto，不改 exit）
  - （可选第三臂）half-size：`consensus_ok==False -> 0.5x`（但这会多一层 sizing 细节；非必须）

这刀的本质是“改职责层”，不是“改指标/改出场/改 universe”。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`（新增 `Rank 18b`）。**

因为：
- 这条 rank 的失败点更像“放错层级”（把 abstain/filter 当 entry alpha）；
- 新 digest 给了一个可以直接对齐的语言：`abstain / no-trade band`；
- 这条派生假设只做 1 个改动轴（职责层），且天然可用 strict A/B 验证“是否只是靠砍单美化”。

## 6) trade on / trade off
- **trade on**：
  - 用 `plateau consensus / spread guard` 识别“EMA 族在当前 bar 上没有形成足够一致性”的段落；
  - 在这些段落里宁可 abstain（或降仓），把交易预算留给更像“走出来”的段。
- **trade off**：
  - trade density 必然下降；
  - 也可能只是切样本让指标变好（并不代表真实 edge）。
  - 所以第一刀必须严格限定为：`baseline vs abstain-only gate`，不允许偷带第二层确认（ADX/ER、RSI、VWAP、regime matrix、new exit 等一律不加）。

---

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `derived`: `Rank 18b`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Proposed derived hypothesis (bot2-ready)
- `proposed_rank`: `Rank 18b`
- `source_rank`: `Rank 18`
- `single modification axis`: **demote standalone EMA plateau-consensus entry into a shared abstain / trend-readiness veto gate**
- `trade on`: 在现有 setup 触发时，仅当 `plateau_vote_5of9_spread_guard` 通过才允许新 entry；否则 abstain（或对照臂 half-size）。
- `trade off`: 牺牲 trade density；风险是“砍单美化”而非真实 edge，因此必须 strict A/B。
- `why now`: 2026-03-20 的 `α/β abstain` 证据把“少做低位移段”从经验变成可审计框架；Rank 18 的 high no-trade ratio 让它天然适合改写成 abstain gate，而不需要推翻原 park。
- `suggested initial state`: `source intake / clean replication next`（只做 baseline vs abstain-only gate；不改 entry/exit/universe）

## Git / write scope
- 本轮只做最小必要写入：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`
- 默认不改 `docs/TODO.md`
- 默认不做 git commit：若存在共享脏文件，避免混提
