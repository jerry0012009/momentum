# Rank 291 / KVSI Korean venue share gate — fresh intake first verdict (`keep_P1`)

- Time: 2026-04-02 09:15 UTC
- Source intake: `research/quant_digests/2026-04-02_0522_kvsi-korean-venue-share-regime-gate.md`
- Executor: bot3 auto loop
- Verdict: `keep_P1`
- Rank assigned: `Rank 291`

## Why this intake survives first pass
这条对象**不是独立 raw alpha**，但它作为 `shared regime / venue-segmentation gate` 已经具备进入 `P1` 的最小条件：

1. **主语清楚**
   - 不是泛泛而谈的 Kimchi premium 叙事。
   - 明确主语是：`ΔKVSI × Korea-led continuation / offshore fade`。
   - 角色定位也清楚：给现有 `momentum / lead-lag / shock-reversal` 线做 `gate / veto / sizing`，而不是硬包装成 standalone direction signal。

2. **proxy 与最小接线路径清楚**
   - 已给出可公开复现的最小 proxy：
     - Upbit `KRW-BTC` 分钟成交额
     - Binance spot `BTCUSDT` quote volume
     - Binance perp `BTCUSDT` 作为交易/预测腿
   - 已明确 `KVSI_proxy` 与 `ΔKVSI z-score` 的 desk-side 定义，且更新频率可落到 `5m -> 15m`。

3. **distinctness 够明确**
   - 它补的是当前前排里较缺的 **venue state variable / 谁在主导价格发现**，不是又一条普通 pairs / breakout / funding / OFI 改名变体。
   - 对 short-cycle desk 的价值在于为多条 raw alpha 提供共享 regime gating，而不是重复造一条微弱 standalone alpha。

4. **诚实边界写清楚了**
   - 文档已明确说明：当前证据不支持把它讲成“韩盘变强=下一根必涨/必跌”。
   - 当前只能支持 `keep_P1`，不能直接升 `P2`：
     - 样本仅约 4 天；
     - 目前只是 `Upbit vs Binance` 的粗 proxy；
     - 论文迁移价值主要来自状态变量，不是 RL 本体；
     - 还没完成对具体 base alpha 的 clean A/B gate test。

## Why it does NOT jump to P2 yet
缺的不是故事，而是**最小 decisive follow-up**：
- 需要把 `ΔKVSI` 真正挂到一条明确 base alpha（如 `5m/15m BTC continuation` 或 `BTC impulse -> ETH/SOL follower lead-lag`）上；
- 需要回答它究竟更适合 `trend continuation gate`，还是主要作为 `fade veto`；
- 需要检查效果是否只存在于 `BTC / 单 venue proxy / 短亚洲时段`，还是能形成更稳的 shared gate 证据。

所以本轮最诚实结论是：**保留为 `P1 surviving candidate`，允许一次最小 follow-up，但还不足以直接进 `P2`。**

## Runtime effect
- 正式分配新 rank：`Rank 291`
- 对象从 `Fresh intake` 进入 `Surviving candidate`
- 本轮系统认知更新为：
  - `Rank 291` 代表一条**可分钟级更新、可服务现有短周期策略的 venue-segmentation gate 候选**；
  - 但当前证据仍停留在 `proxy portability + clean framing`，尚未完成 base-alpha A/B admission。

## One-line result
`Rank 291 / ΔKVSI × Korea-led continuation / offshore fade` 已通过 first verdict：它不是 standalone raw alpha，但作为可分钟级更新、可接到现有 momentum/lead-lag/shock-fade 线路上的 venue-segmentation gate 具备明确主语、proxy 定义与最小接线路径，因此进入 `P1 surviving candidate`，暂不升 `P2`。
