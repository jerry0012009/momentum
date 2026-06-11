# Rank 389 fresh intake first-verdict — cross-venue net-carry ranking alpha（keep_P1）

- 时间：2026-04-12 11:04 UTC
- 对象：`research/quant_digests/2026-04-12_0830_crossvenue-netcarry-ranking-alpha.md`
- 执行动作：fresh intake first-verdict（含 1 条最小 honesty 子检查）

## 结论
- 分配新正式编号：`Rank 389`（next unused integer）。
- first verdict：`keep_P1`。
- 会改变系统认知的一句话：该 cross-venue net-carry ranking 具备可复现的 raw alpha 骨架（funding+basis-成本后做 venue pair 排名），但当前数据接线需要先补“同窗可得性约束”才能进入 survivor follow-up。

## 最小 honesty / execution realism 子检查（本轮仅 1 条）
目标：检查跨 venue 报价/费率时间戳是否同窗可得，避免事后拼接。

### 快检结果（BTC）
- Binance `premiumIndex`：返回 `time=1775992026000`（毫秒时间戳可直接用于同窗对齐）。
- Hyperliquid `metaAndAssetCtxs`：接口响应正常；可记录本地接收时间窗（本次 `recv window≈49ms`）作为对齐锚。
- dYdX `perpetualMarkets`：`BTC-USD` 当前字段里 `nextFundingRate` 可得，但 `updatedAt/nextFundingAt` 为 `null`，缺少稳定 server-side 时间锚。

### 解释
- 该问题是 **可执行性护栏**，不是本轮 fatal flaw：
  - 可用 ingestion 规范补救（统一按 `collector_receive_ts` + 容忍窗对齐，超窗样本直接丢弃）；
  - 但在补齐前，不应把 cross-venue 瞬时排名直接当成可成交 edge。

## 本轮决定
- 不触发 `background/P0`；保留为 `P1`，进入下一步 survivor 唯一 follow-up（围绕“同窗可得 + 成本后净边际”做一次最小收口）。
- 本轮未进入 `P2/P3`，无 handoff/wiring 动作。
