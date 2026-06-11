# Rank 305 / HIP-3 oracle-premium percentile fade / first verdict = keep_P1

- Time: 2026-04-03 08:54 UTC
- Actor: bot3
- Source intake: `research/quant_digests/2026-04-03_0808_hip3-oracle-premium-percentile-fade.md`
- Verdict: `keep_P1`
- New formal identity: `Rank 305`

## Why this changes runtime truth
`HIP-3 oracle-premium percentile fade × time-boxed exit` 足够独立于既有 funding / basis carry / same-underlier spread 家族，原因不是“venue 换皮”，而是它把 **同一标的 mark-vs-oracle premium 的分钟级极端偏离回归** 当成主语；盈利来源优先来自短时 pricing dislocation 的收敛，而不是 funding accrual、跨腿 carry、或跨标的 spread mean reversion。

## Evidence for independence
1. **主语不同**：
   - 这条线交易的是 `premium = (mark - oracle) / oracle` 的尾部偏离回归；
   - 不是传统 funding carry 的“拿 funding 收敛”，也不是 basis carry 的“赚期现/期限结构 carry”，更不是 pairs/stat-arb 里两条可交易腿之间的相对价差。
2. **时间形状不同**：
   - digest 给出的最强 pocket 是 `95 秒~19 分钟` 的快速回归；
   - 这更像 micro dislocation fade，而不是靠数小时/数天 carry slowly realize。
3. **实验壳已足够冻结**：
   - 已明确 `1m/3m/5m/15m` 最小实验框架；
   - 已明确 rolling percentile entry、1bp 附近平仓、time stop、premium-worsen stop、显式 fee/slippage；
   - 可直接用 Hyperliquid 公共 API 拉 `mark/oracle/premium` 复现。
4. **与旧家族的最小可检验增量清楚**：
   - 若后续实验显示 edge 主要来自慢 funding/basis 收敛，那么它会被压回；
   - 但在 intake 层，当前材料已经足够证明它先是 `oracle-anchored short-horizon dislocation`，再才可能和 carry 家族发生边界重叠。

## Why not direct P2 yet
虽然这条线已经有清楚主语和最小实验壳，但当前仍主要来自 repo 结果 + 机制描述，还没有我们自己对 `BTC/ETH + HL 特色资产` 的最小 clean replication；因此诚实层级先放 `P1`，给它唯一一次 survivor follow-up 去回答“这个 edge 是否真的来自分钟级 premium 回归，而不是样本/资产偶然性”。

## Runtime consequence
- 这条 fresh intake 不应停留在 `background/P0`；
- 它已获得正式身份 `Rank 305`；
- 当前应进入 `Surviving candidate slot`，等待唯一一次最小 decisive follow-up。

## One-sentence result for state
`Rank 305`：`HIP-3 oracle-premium percentile fade × time-boxed exit` 已证明是独立于 funding/basis carry 的 same-underlier mark-vs-oracle dislocation raw alpha，first verdict = `keep_P1`，进入 survivor。