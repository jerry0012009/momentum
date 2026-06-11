# Rank 340 / top20 depth imbalance × tight-spread continuation — survivor decisive follow-up

- Time: 2026-04-05 18:18 UTC
- Object: `Rank 340 / top20 depth imbalance × tight-spread continuation`
- Previous layer: `P1 / surviving candidate`
- New layer: `background / P0`
- Verdict: `drop_to_background`

## Why this changes system belief

`Rank 340` 的 distinct microstructure shell 仍然成立，但 survivor 这唯一一次 decisive follow-up 已经足够回答更关键的问题：**它目前并没有留下可 admission 的独立 alpha 壳**。现有 source 证据仍局限在 `BTCUSDT 单日`，而且给出的 wall-clock / event-time 毛 edge 只有 `~0.12–0.19 bps (1s/2s)` 与 `~0.53–0.84 bps (50/200 events)`；这意味着一旦把问题从“方向关系是否存在”切换到 bot3 当前必须回答的“跨日 / 跨资产 / post-cost 后是否还能独立存活”，答案更接近 **不能**：它更像 execution confirmer / quote-leaning primitive，而不是值得继续占前排资源的独立 raw alpha 候选。

## Evidence used in this follow-up

### 1) clean-room 可复刻关系只有 BTC 单日，不满足 survivor 后续要的 transfer test
本轮重新核对了 source notebook 与 repo 元数据：
- repo：`Starkl7/Crypto-OrderBook-Imbalance`
- 创建时间：`2026-04-05 00:48 UTC`
- 主要材料：`order_book_extensive_analysis.ipynb`
- 数据文件：`2026-01-01_BTCUSDT_ob200.data`
- notebook 输出样本：`BTCUSDT` 单一标的、单日、约 `424,195` 条 `orderbook.200` 消息

这足以支撑 first verdict 的 `keep_P1`：说明 `top20 depth imbalance` 在 tight spread 下确实和同向超短 drift 有关系。

但对 survivor follow-up 来说，关键不再是“有无 microstructure 关系”，而是：
- 是否跨日稳定；
- 是否能迁移到 `ETH/SOL` 等 liquid majors；
- 是否在 post-cost 语义下还保留独立策略壳。

source 目前没有多日、没有跨资产、没有真实成交模型，因此它不能通过 `独立 alpha admission` 所需的最低迁移门槛。

### 2) after-cost 语义直接把它压回 execution primitive
source 内最有价值的数，本轮按 desk 语义重新解释后，结论很明确：
- `1s` extreme-decile spread 约 `0.1172 bps`
- `2s` extreme-decile spread 约 `0.1938 bps`
- `50-event` spread 约 `0.5285 bps`
- `200-event` spread 约 `0.8407 bps`

这些数字对于“方向关系存在”是够的，但对于“独立可交易 alpha”不够：
- 对普通 taker 成本档位，几乎必然被完全吃掉；
- 对 blended 成本语义，也只留下非常脆弱的薄 edge；
- 只有在 maker-first / quote-leaning / execution timing 的语义下，它才有现实价值。

换句话说，**这条线更像 execution layer input，而不是独立 P2 候选**。

### 3) 当前没有额外证据支持把它升到 P2
policy 要求 survivor 的唯一 follow-up 必须诚实收口，而不是继续拖着“也许以后补一下跨日/跨资产”。
本轮没有发现任何能扭转层级判断的新证据：
- 没有多日 out-of-sample；
- 没有 ETH / SOL 迁移结果；
- 没有能覆盖实际 fee / queue / miss risk 的 execution proof；
- 也没有表明它在 post-cost 后仍是独立 alpha，而不只是 shared gate / maker skew。

因此继续把它留在前排，只会把一个已经基本回答完的问题拖成长尾研究。

## Final verdict

`Rank 340` 不升 `P2`。survivor 唯一 follow-up 的结论是：**top20 depth imbalance × tight-spread continuation 目前只足以作为 microstructure execution primitive / shared confirmer 被记档，不足以作为跨日、跨资产、post-cost 下可 admission 的独立 alpha 候选继续占用前排槽位。** 依 policy，本轮直接 `drop_to_background / P0`。

## Runtime consequences

- `Surviving candidate slot` 清空
- `Rank 340` 移入 `Background pool`
- `Fresh intake slot` 仍保持 `research/quant_digests/2026-04-05_1606_twotier-funding-rate-crossvenue-arb-alpha.md` 为当前前位
- 本轮 `cycle_plan` 第 1 小点收口为完成，不再保留开放式 follow-up

## One-line result

`Rank 340` 的 survivor 唯一 follow-up 已诚实收口：source 只证明了 `BTC 单日` 下的超短盘口 continuation 关系，而 post-cost 可迁移独立 alpha 壳并未成立，因此对象从 `P1` 直接 `drop_to_background / P0`，更合适的定位是 execution primitive 而非前排候选。
