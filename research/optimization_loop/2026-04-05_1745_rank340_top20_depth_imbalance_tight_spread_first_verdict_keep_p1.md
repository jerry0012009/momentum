# Rank 340 / top20 depth imbalance × tight-spread continuation — fresh intake first verdict

- Time: 2026-04-05 17:45 UTC
- Object: `research/quant_digests/2026-04-05_0059_top20-depth-imbalance-tightspread-continuation-alpha.md`
- Assigned Rank: `340`
- Previous layer: `fresh intake`
- New layer: `P1 / surviving candidate`
- Verdict: `keep_P1`

## Why this changes system belief

`top20 depth imbalance + tight spread continuation` 不是把已有 order-flow / OBI 题材换个参数名，而是把 **前 20 档盘口库存失衡在 tight spread 环境下驱动超短 continuation** 明确成了一个独立的 microstructure raw alpha primitive；更关键的是，它已经给出了可迁移的最小执行壳：`imbalance_top20` 定义、tight/normal/wide spread gate、秒级/事件级 holding horizon、以及 maker/blended/taker 三档成本框架都写得够清楚，因此值得保留到 `P1` 做那唯一一次便宜但决定性的 follow-up。

## First-verdict reasoning

### 1) distinct alpha shell is real
- digest 的核心不是泛泛而谈“order-book imbalance 有信息”，而是把信号压到一个可复刻公式：
  - `imbalance_top20 = (sum_bid_qty_top20 - sum_ask_qty_top20) / (sum_bid_qty_top20 + sum_ask_qty_top20)`
- 方向假说也不是旧的反转/确认版本，而是 **same-direction continuation**：bid-heavy → 后续 mid-price 更容易上漂，ask-heavy → 更容易下滑。
- 这让它和此前更慢、更偏 bar-level 的 OBI / pressure / reversal 叙事有了清晰边界。

### 2) execution shell is sufficiently concrete
- source 使用公开 Bybit `orderbook.200` 流，数据获取路径明确，不是私有数据黑箱。
- digest 已把最小实验壳写清：
  - venue/data: Bybit level-200 public orderbook
  - symbols: BTCUSDT 起步，可扩到 ETHUSDT / SOLUSDT
  - horizon: `1s/2s/5s/10s` 与 `10/50/200 events`
  - gating: tight/normal spread regime
  - mapping path: 原生秒级版 + 聚合到 `1m/3m` 的 persistence 版
- 这已经足够形成 desk 可验证的 clean-room，而不是停留在“值得以后研究”的概念层。

### 3) cost realism is honest enough for intake
- digest 没把极薄毛 edge 包装成可直接 aggressive taker 的成熟策略，反而明确承认：
  - `1s/2s` extreme-decile spread 只有约 `0.12~0.19 bps`
  - `50/200 events` spread 也只有约 `0.53~0.84 bps`
- 并已明确区分三种落地语义：
  1. maker skew / quote leaning
  2. shared entry confirmer / veto
  3. fee-favorable taker path
- 这种诚实的成本叙述意味着它值得留在前排继续判“独立 alpha 还是 execution primitive”，而不是因为没有假装很赚钱就直接丢掉。

## Why not promote P2 yet
- 当前证据仍主要来自 **单日 BTCUSDT notebook 输出**；虽足以支撑 `keep_P1`，但还没覆盖跨日稳定性、跨资产迁移、以及 post-cost 下是否仍保留可交易净收益。
- 因此它还不该直接进 `P2 admission`，更合适的是进入 survivor 唯一 follow-up，优先回答：
  - 这条关系在多日样本里是否稳定；
  - 在 ETH/SOL 是否还能保留；
  - 成本后它是独立 alpha，还是只能作为 execution primitive 存活。

## Runtime consequences
- 分配新正式 Rank：`340`
- 当前对象写成 `keep_P1`
- survivor 槽位由 `Rank 340` 占据
- fresh intake 前位顺延到：`2026-04-05_1606_twotier-funding-rate-crossvenue-arb-alpha.md`

## One-line result

`Rank 340 / top20 depth imbalance × tight-spread continuation` 已完成 fresh intake first verdict：该对象把 `top20 depth imbalance`、tight-spread gate、秒级/事件级持有窗与三档成本语义压成了可复刻的 microstructure continuation raw alpha 壳，足以作为 distinct intake 保留到 `P1`，但尚未完成跨日/跨资产/post-cost admission，因此本轮写成 `keep_P1` 而非直升 `P2`.
