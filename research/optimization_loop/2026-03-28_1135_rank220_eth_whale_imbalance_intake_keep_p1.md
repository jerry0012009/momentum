# Rank 220 / ETH whale balance imbalance alpha — fresh intake 首轮判分：keep_P1

- 时间：2026-03-28 11:35 UTC
- 对象：`research/quant_digests/2026-03-28_1033_eth-whale-balance-imbalance-alpha.md`
- 结论：`keep_P1`
- 新分配 Rank：`220`
- 本轮角色：fresh intake 首判

## 一句话结论
`ETH 大钱包净增持 − 小钱包净减持` 留下的是一条值得保留到前排做唯一一次 follow-up 的 **ETH 事件型外部数据 raw alpha 结构**；但当前公开证据仍主要停留在 **日频论文 + vendor/cohort 口径依赖**，还不足以直接升 `P2`。

## 为什么不是直接 drop
1. **base alpha 明确**：不是泛泛“whales 有用”，而是 `large accumulation - small distribution` 的 holder-imbalance spread。
2. **交易对象单一**：直接落到 ETH 现货 / perp，不需要复杂多腿拼装。
3. **方向性证据够硬**：论文回归给出明确 lead-lag，且 large / small cohort 符号相反，说明不是单边噪音流入故事。
4. **可 desk 化**：可以自然改写成稀疏事件触发，而不是硬装成 every-bar 因子。

## 为什么还不能直接升 P2
1. **现成证据核心仍是日频**：还没证明分钟化后在 `1m/3m/5m/15m` 上保留可交易漂移。
2. **数据工程风险高于交易逻辑风险**：地址标签、交易所/桥地址剔除、cohort 重建与延迟口径都会直接决定信号真假。
3. **vendor 便利口径不可默认获得**：论文依赖 Coin Metrics 分层数据；若没有可复现实验代理，admission 会停在叙事层。
4. **执行 realism 尚未验证**：尚无 after-cost intraday 结果，不能把论文 lead-lag 直接当 deploy-ready alpha。

## 本轮正式 verdict
- `Rank 220 / ETH whale balance imbalance alpha`：**keep_P1**
- 保留原因：它留下了值得做一次 cheap-but-decisive follow-up 的对象，不只是方法论注记。
- 不升 `P2` 原因：当前还缺唯一关键 admission bridge——**分钟化 cohort proxy + after-cost 事件漂移是否仍成立**。

## 唯一 survivor follow-up 应该回答什么
只做一次最小诚实检查：

> 用可公开重建的 `large-vs-small cohort proxy`，验证 `imbalance = z(Δlarge) - z(Δsmall)` 在 ETH 上是否能在现实成本口径下留下 `15m/30m/60m/240m` 的事件型漂移；若不能，就按 `keep_P1 后转 background` 收口。

## 对 runtime 的影响
- fresh intake 已正式判分并获得 `Rank 220`
- survivor 槽位应切换到 `Rank 220`
- `followup_budget_remaining = 1`
