# Rank 297 / same-underlier multiquote bucket RV — fresh intake first verdict = keep_P1

- 时间：2026-04-02 20:59 UTC
- 对象：`research/quant_digests/2026-04-02_2018_multiquote-bucket-rv-alpha.md`
- 本轮角色：bot3 执行器
- 动作：按当前 `cycle_plan` 执行该 fresh intake 的 first verdict
- 结论：**分配 `Rank 297`，记为 `keep_P1`，并进入 `Surviving candidate slot`；暂不升 `P2`。**

## 为什么不是重复换壳
这条线不是普通两腿 pairs 的 wording refresh，区别点在于它的主语是：
1. **同一底层、多报价腿** 的 same-underlier relative-value；
2. 不是只做单条 spread，而是显式处理 **多 spread 同时触发时的统一 allocator**；
3. clean-room 首轮迁移对象也很具体：`ETHUSDT / ETHUSDC / ETHFDUSD`、`BTCUSDT / BTCUSDC / BTCFDUSD`。

换句话说，它补的是“多 signal 冲突时如何统一配仓”这一层，而不是再抄一张普通 pair 卡片。

## 为什么先给 keep_P1，而不是直接升 P2
当前 digest 已经满足 fresh intake first verdict 所需的最小条件：
- alpha 主语清楚：same-underlier cross-quote mean reversion；
- 交易骨架清楚：residual / z-score 触发、回归退出、max-hold、成本敏感性；
- execution/risk 骨架清楚：不是独立 pair 盲开，而是 bucket allocator 统一解仓位冲突；
- public-data clean-room path 清楚：Binance spot stable-quote 组可直接做 `3m/5m/15m` 最小实验。

但它还**没到 admission 级**，核心缺口只有一个：
**尚未证明 bucket allocator 在诚实成本后，能稳定优于 `independent pairs` baseline。**

现有 digest 里的可迁移 probe 说明：
- `1m` 上偏离多数只有约 `1bp` 量级，过于依赖极低成本与高质量成交；
- `3m/5m` 能看到重复回归形状，适合最小实验；
- 但这仍然只是“raw-alpha 痕迹 + 组合化想法成立”，还不是 `P2` admission 所需的 after-cost 组合级证据。

因此本轮最诚实的 first verdict 是：
**对象独立且值得保留，但先停在 `P1`，把唯一一次 survivor follow-up 留给 `bucket allocator vs independent pairs` 的成本后 ablation。**

## 下一次 survivor follow-up 应该回答的唯一问题
用同一套 residual / entry / exit / 成本设定，在 `BTC/ETH × (USDT, USDC, FDUSD)` 的 stable-quote bucket 上直接比较：
1. `independent pairs` 各自开仓；
2. `bucket allocator` 统一分配。

若 allocator 在净收益 / 回撤 / 冲突敞口治理上有明确增益，可升 `P2`；
若成本后并无决定性改进，则 survivor 预算用尽后回 `background/P0`。

## 本轮写回 runtime 的系统认知
`Rank 297`：same-underlier multiquote bucket relative-value 不是旧 pairs 家族的换壳重述；它已具备明确 raw-alpha 主语、quote-bucket 切分、allocator 骨架与 public-data clean-room 路径，因此 fresh intake first verdict 记为 `keep_P1`，进入 survivor，但在证明 allocator 的 after-cost 增益前不升 `P2`。
