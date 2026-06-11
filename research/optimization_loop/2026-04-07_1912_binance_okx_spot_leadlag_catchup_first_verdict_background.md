# Rankless fresh intake first verdict — Binance spot impulse × OKX delayed catch-up → background / P0

- Time: 2026-04-07 19:12 UTC
- Target: `research/quant_digests/2026-04-07_1748_binance-okx-spot-leadlag-catchup-alpha.md`
- Slot: `Fresh intake`
- Verdict: `background / P0`

## Why this step was the current legal action
`BOT2_BOT3_STATE.md` 当前 `cycle_plan` 里排在最前且仍为 `pending` 的小点，就是这条 `2026-04-07_1748_binance-okx-spot-leadlag-catchup-alpha.md` fresh intake first verdict。当前不存在 `Paper launch queue` 或 `Active P2` 的待执行对象，因此本轮只处理这一条。

## What changed system knowledge
`Binance spot impulse × OKX delayed catch-up` 没有提供独立于既有 `same-underlier cross-venue lead-lag / XEMM / gap-close` 家族的新 raw alpha 主语，因此本轮诚实收口为 `background / P0`，不进入 survivor。

## Evidence for the verdict
1. **主语不新，仍落在既有家族里。**
   该 digest 自己把对象定义为 `same-underlier cross-venue lead-lag raw alpha`，并明确说未来更适合作为已有 `XEMM / quote-gap-close / maker-taker hedge` 的 `leadership admission / no-chase veto`。这说明它更像旧家族的 leader filter / execution overlay，而不是一条全新的独立 raw alpha 主语。

2. **证据主要是秒级 lag-correlation EDA，不是独立策略壳。**
   核心结果是 `spot_binance_spot_okx_corr` 在 lag=17 处约 `0.4332`，反向约 `0.3387`，外加 `21` 个观测点大约 `2.61s`。这能说明“Binance 更常领先”，但还停留在相关性扫描与事件解释层，并没有把 `entry / exit / sizing / fill realism` 压成可独立 admission 的策略骨架。

3. **样本窄，且对象只是一对 venue 的 BTC。**
   notebook 样本只覆盖 `2025-06-03` 到 `2025-06-04` 两天，主对象是 `Binance BTCUSDT` 与 `OKX BTC-USDT` spot/perp 对齐。对当前素材池来说，这更像对既有 `same-underlier cross-venue` 口袋的局部补图，而不是能自然扩成一个新 rank 的跨资产/跨时钟 alpha 家族。

4. **当前池里已有更完整的同家族对象。**
   研究池已经有：
   - `2026-04-04_0146_sameunderlier-crossvenue-gap-latency-budget-alpha.md`
   - `2026-04-03_1845_pacifica-hl-maker-taker-xemm-alpha.md`
   - `2026-03-26_0252_futures-lead-spot-lag-spread-alpha.md`
   - `2026-03-26_0922_cex-dex-eth-leadlag-spread-alpha.md`
   这些对象都比这份 notebook 更接近“可交易的 same-underlier/cross-venue relative-value 壳”。本条 intake 没有给出能和它们正交的新 pocket。

## Decision
按当前 policy，这条对象的 first verdict 应直接写成 `background / P0`：
- 不分配 Rank
- 不进入 `Surviving candidate slot`
- 不升级到 `P2`

## Reader-facing implication
无新增前排对象；只是把一个看似新鲜、实际属于旧 `cross-venue lead-lag` 家族的素材诚实停放到 background，避免它靠“秒级 notebook + 新 repo 时间戳”误占 survivor 配额。
