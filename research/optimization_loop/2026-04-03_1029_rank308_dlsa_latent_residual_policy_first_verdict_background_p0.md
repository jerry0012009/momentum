# Rank 308 — DLSA latent-state residual policy fresh intake first verdict = background/P0

- Time: 2026-04-03 10:29 UTC
- Target: `research/quant_digests/2026-04-03_0848_dlsa-latent-residual-policy-alpha.md`
- Slot: `Fresh intake`
- Verdict: `background/P0`
- Rank assigned: `308`

## Why this intake does **not** earn `keep_P1`

这篇 DLSA 的价值我认可，但它当前更像一套 **panel-level stat-arb alpha factory / training container**，而不是已经足够独立 desk 化的一条 raw alpha。

本轮按 fresh intake 的标准，关键不是“框架是否高级”，而是它是否已经给出：
1. 单独可命名的 residual trading 主语；
2. 不依赖再设计一整层 latent-factor / residualization 工程的最小执行壳；
3. 相对现有 stat-arb / regime / residual 家族的最小新增、且可直接检验的独立 edge。

这条 intake 目前没过这三点，原因如下：

### 1) alpha 主语仍然过于上游
DLSA 真正描述的是：
- 先做 conditional latent factor stripping；
- 再从 residual panel 学 continuous allocation policy；
- 再把成本、换手、short hold cost 一起纳入目标。

这是一套 **研究/建模框架**，不是一条已经定型的 `residual signal X -> trade Y` 主语。
它告诉我们“怎么组织一篮子 residual alpha”，但没有把某个独立 residual pocket 明确钉死成当前可单独 desk 化的对象。

### 2) 可迁移，但不等于当前已可独立落地
digest 已经把 crypto 版最小实验壳讲清楚了：`15m`、20~40 个 perp、beta/sector/funding/OI residualization、再跑 baseline/OUFFN/CNNTransformer。

问题在于：这套落地仍然依赖我们**先发明/选择**一整层 crypto residual factor schema。也就是说，真正需要被验证的核心 edge 还停留在：
- 因子怎么剥；
- residual panel 怎样构；
- 哪个资产池有效；
- 是 reversal 还是 momentum；
- 何种成本口径下还能活。

因此它更像“一个可展开的研究程序”，而不是已经具备独立首判资格的具体 raw alpha。

### 3) 和现有家族相比，新增信息主要在容器层，不在 alpha 本体
当前 intake 池里已经有：
- cross-sectional reversal
- stat-arb / pair / basis / premium / residualization
- regime-conditioned execution

DLSA 的新增，主要是把这些东西装进 `latent-factor residual portfolio × cost-aware continuous allocation` 容器里统一训练。
这对中长期 research infra 有价值，但对本轮 fresh intake 的标准来说，它并没有直接给出一条足够独立、可与现有 residual/stat-arb 家族区分开的 raw alpha 本体。

## System-level result

`Rank 308 / latent-factor residual portfolio × cost-aware continuous allocation` 已完成 fresh intake 首判：
- 它值得保留为 **研究框架/方法论参考**；
- 但当前不作为一条独立前排 raw alpha 推进；
- 因此本轮收口为 `background/P0`，不进入 `Surviving candidate slot`。

## One-line result for runtime

`Rank 308`：DLSA 提供的是可迁移的 residual-panel / continuous-allocation 研究容器，而不是已具备独立 residual 主语与最小执行壳的单条 raw alpha，因此 fresh intake first verdict = `background/P0`。
