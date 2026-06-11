# Rank 170 / portable microstructure reversion basket — fresh intake 首判（keep_P1）

- 时间：2026-03-25 22:36 UTC
- 对象：`research/quant_digests/2026-03-25_2227_portable-microstructure-reversion-basket.md`
- 轮次角色：bot3 executor
- 执行动作：fresh intake 最小首判，只回答 `park` 还是 `keep_P1`
- 结论：**keep_P1，分配正式 Rank 170**

## 为什么不是直接 park
这条线当前还不能被诚实地打成“只有论文 headline 好看、desk 上完全不可用”的对象。真正该被否掉的，是把论文原文继续误读成**可以直接搬到我们这里做的 `3 秒 taker continuation`**。digest 已经把更有价值、也更贴近当前 desk 的 deployable 核心收窄得很明确：

> 可保留的不是超高频 continuation 叙事，而是**跨资产可移植的 `taker-imbalance × VWAP-pressure` `1m/3m` market-neutral reversion basket**；它目前仍只是 raw alpha 候选，不是已经过成本审计的 always-on 策略。

## 首判依据
1. **有可复现的跨资产分钟级毛边，不是空叙事。**
   - 同一组 pressure proxy 在五币横截面 market-neutral 版本上，`1m hold 1 bar` 约 **`+1.171 bps`**、`1m hold 3 bars` 约 **`+1.209 bps`**；
   - `3m hold 1 bar` 仍有约 **`+0.667 bps`**；
   - 说明这条线至少保留了“分钟级短窗反转篮子”这类可继续诚实检查的 skeleton，而不是首判就归零。
2. **需要保留的 deployable 核心已经足够明确。**
   - digest 已把信号定义收束到 `taker imbalance + VWAP pressure -> reversion_score`；
   - 更重要的是，它明确指向 **`1m/3m` cross-sectional market-neutral reversion**，而不是含糊的“microstructure 很重要”泛结论。
3. **论文支持它更像 shared feature family，而不只是单币巧合。**
   - 原论文在 `BTC/LTC/ETC/ENJ/ROSE` 上给出跨资产稳定的主导特征形状；
   - 这至少支持把对象保留为“可扩展的 shared microstructure feature family”候选，而不是单一小币偶然信号。
4. **但它还远没到 P2。**
   - 当前证据几乎全是 gross / proxy 口径；
   - digest 自己也明确承认 edge 可能依赖尾部币、短窗、高换手和更有利执行方式；
   - 所以下一步只能做一次 survivor 唯一 follow-up，直接回答成本与执行诚实约束下是否还留得住可复制净边。

## 改变系统认知的一句话
**Rank 170 / portable microstructure reversion basket 保持 P1：当前诚实可保留的不是论文 headline 的 `3 秒 taker continuation`，而是跨资产可移植的 `taker-imbalance × VWAP-pressure` `1m/3m` market-neutral reversion basket。**

## 下一步（留给后续唯一 follow-up）
只回答一个问题：`Rank 170` 在最小成本与最小执行诚实约束下，是否仍保留值得进入 `P2` 的可复制净边；若毛边主要停留在 gross、尾部币贡献或不诚实成交假设上，就应直接结束前排并回到 `Background pool`。
