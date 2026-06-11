# Rank 180 / network-peripheral-pairs-book survivor follow-up -> park_to_background

- 时间：2026-03-26 07:19 UTC
- 对象：`Rank 180 / network-peripheral-pairs-book`
- 执行动作：survivor 唯一一次 cheap but decisive follow-up
- 结论：`park_to_background`

## 本轮只回答一个问题
`pairs raw alpha + peripheral same-community book construction` 在**不改 base pairs alpha score** 的前提下，是否已经能比 classic top-pairs 更诚实地改善 pair-book overlap / contagion / downside 画像，从而值得继续升到 `P2`？

答案：**不能，当前应收口为 `park_to_background`。**

## 为什么这轮必须收口
policy 对 survivor 很清楚：`Rank 180` 只有这一次 follow-up 预算；这次 follow-up 必须回答它能否支撑继续前排，而不是继续把 network 叙事拖成长线研究。

## 本轮看的证据
直接复用 intake 已生成的本地 artifact：
- `reports/artifacts/quant_digests/network_pairs_proxy_20260326_0615/summary.json`
- `reports/artifacts/quant_digests/network_pairs_proxy_20260326_0615/group_summary.csv`
- `reports/artifacts/quant_digests/network_pairs_proxy_20260326_0615/*_pairs_backtest.csv`

并补做一个最小 book-overlap / concentration 读数：统计每本 book 的节点复用度与 leg concentration（HHI）。

## 本轮得到的决定性事实
### 1) peripheral sleeve 没证明自己优于 classic top-pairs
现有 OOS 代理结果里：
- `classic_top_proxy`：`+118.1 bps/trade`，`+1.01 bp/h`
- `peripheral_same_community`：`+71.2 bps/trade`，`+0.73 bp/h`
- `central_same_community`：`+111.7 bps/trade`，`+0.57 bp/h`

翻成人话：peripheral sleeve **只是在单位时间产出上高于 central sleeve**，但并没有把 classic top-pairs 压过去；因此它还不是一个足够强的“继续前排 admission”理由。

### 2) 它想解决的 overlap / contagion 问题，当前 proxy 反而没有被诚实改善
按 pair book 里的 shared-leg 集中度来看：
- `classic_top_proxy`：5 对、6 个独立节点；最高复用节点 `BTCUSDT` 出现 `3` 次；leg HHI = `0.20`
- `peripheral_same_community`：3 对、4 个独立节点；最高复用节点 `BNBUSDT` 出现 `3` 次；leg HHI = `0.3333`
- `central_same_community`：5 对、7 个独立节点；最高复用节点 `ETHUSDT` 出现 `3` 次；leg HHI = `0.18`

也就是说，当前这版 `peripheral same-community` book **没有减少隐藏共振，反而更像把 BNB 当共同中介腿反复使用**。如果它的卖点本来就是“更诚实地处理 pair-book overlap / contagion”，那这个结果已经足够构成反证：

> 这条配书骨架在当前可复用 proxy 下，还没证明自己真的把 book 变得更分散、更抗共振。

### 3) 因而它当前更像“研究提醒”，不是可前排推进的对象
这不等于论文没价值；更准确地说：
- 它提醒我们 **pairs alpha 评估不能只看单对，要看整个 book 的隐藏相关风险**；
- 但当前保留下来的这条具体对象 —— `peripheral same-community pair book construction` —— 还没拿出足够证据，证明它是能继续推进的独立前排骨架。

## 为什么不是 promote_P2
若要升 `P2`，至少要看到这条骨架对它声称解决的问题给出正向、可继续 admission 的信号。当前没有：
1. 收益层面没赢 classic；
2. overlap / concentration 层面没改善，反而更集中；
3. downside / contagion 的 thesis 目前停留在论文叙事，尚未被当前本地 proxy 诚实复现。

所以继续把它留在前排，只会变成“再补一点 network 证据”的开放式拖延，不符合 policy。

## 对系统认知的更新
**Rank 180：唯一 survivor follow-up 已诚实收口为 `park_to_background`；当前 `peripheral same-community` 这条 pairs 配书骨架没有证明自己比 classic top-pairs 更能改善 overlap / contagion 画像，且 proxy book 反而表现出更高的 shared-leg concentration（BNB 3 次复用，leg HHI 0.3333），因此不足以升入 `P2`。**
