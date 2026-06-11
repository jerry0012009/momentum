# Rank 174 / dynamic-factor-multi-pair-statarb — fresh intake 首判（keep_P1）

- 时间：2026-03-26 01:10 UTC
- 对象：`research/quant_digests/2026-03-25_2042_dynamic-factor-multi-pair-statarb.md`
- 结论：**keep_P1，不升 P2**
- 正式 Rank：**174**

## 这轮只回答一个问题
这条 2021 动态因子多腿 stat-arb 线，是否值得作为新的前排候选保留？

回答：**值得保留到 P1，但当前证据不支持直接升 P2。**

## 为什么保留
1. **它补的是结构缺口，不是旧 pairs 的同义改写。**
   这条线的 base alpha 不是“继续找更好的一对 z-score”，而是先从整篮子里剥离共同 market leg，再交易会均值回归的 residual factor。对当前研究池来说，它确实补上了 `pair -> basket / residual factor` 这一层迁移卡。
2. **策略骨架是完整的。**
   digest 已明确给出 regime gate、entry/no-trade band、long-short 半篮子构造、持有频率、成本审计和停机条件，不只是一个抽象因子解释。
3. **失败形状本身有信息量。**
   本地最小快检说明：raw alpha 形状是成立的，但 naive short-cycle transfer（4 币、15m、频繁重算）太薄，真实成本下一上就死。这不是“没东西”，而是把后续唯一值得补的方向收窄到了更大 basket、更慢 rebalance、更强 no-trade band。

## 为什么这轮不升 P2
1. **当前 desk transfer 证据还是负面的。**
   在 digest 自带的 15m perp proxy 里，1-bar 毛边只有约 `+0.085%` 累计，一加 `2 bps` 就转负，4-bar 持有也没救回来。现在还没有“足以进入 admission”的净边证据。
2. **现阶段更像中频 residual skeleton，不是已证明可部署 edge。**
   这条线当前更诚实的标签是：`market-neutral residual stat-arb skeleton`，值得做一次 survivor follow-up，但还不能说已经跨过短周期可部署门槛。
3. **唯一便宜 follow-up 很明确。**
   若要继续，只该回答一个 decisive 问题：把篮子扩到更合理的 `8~12` 币、把 rebalance/hold 降速、并让 no-trade band 成为主角后，是否还能留下足以覆盖 `2~4 bps` 的可复制净边；如果不能，就该诚实回 background，而不是继续在 pairs 近邻里打转。

## 本轮改变的系统认知
**Rank 174 / dynamic-factor-multi-pair-statarb 值得以前排 P1 身份保留的，不是 15m 四币 proxy 的薄毛边，而是“共同 market leg 剥离后的多腿 residual mean reversion”这套 basket stat-arb 骨架；当前仍未证明可直接升入 P2。**

## Runtime 落点
- `Fresh intake slot`：本轮首判完成
- `Surviving candidate slot`：切换为 `Rank 174 / dynamic-factor-multi-pair-statarb`
- `followup_budget_remaining`：`1`
- 原 survivor `Rank 173 / repo-statarb-live-stack-transfer-check`：退出前排，回到 background pool（并非被否定，而是给新 fresh intake 让出唯一 survivor 槽位）
