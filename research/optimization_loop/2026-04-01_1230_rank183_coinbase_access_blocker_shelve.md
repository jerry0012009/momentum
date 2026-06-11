# Rank 183 / cbeth-eth-rolling-fair-basis-mr — 暂停推进：开户/接入现实受阻（shelve）
- 时间：2026-04-01 12:30 UTC
- 对象：`Rank 183 / cbeth-eth-rolling-fair-basis-mr`
- 状态动作：`mark_access_difficult_and_shelve`

## 这次只回答一个现实问题
不是再讨论 alpha，也不是再重跑 admission；只回答：

> **这条线在当前用户现实约束下，是否应继续沿 paper launch queue 往前推？**

## 结论
**结论：先明确标记为“开户/接入有难度”，并暂时搁置（shelve）。**

更具体地说：
- 这条线的研究对象本身没有被推翻；
- 但它当前的可落地交易路径高度依赖 `CBETH` 的现实可得性；
- 在用户当前约束下，**Coinbase 开户/地址验证材料是现实 blocker**；
- 同时，快速外部核对显示，`CBETH` 在主流非 Coinbase 交易所上的现货可交易性并不宽，至少不是一个“随便换家所就能平替落地”的标的；
- 因此最诚实的动作不是继续排 paper launch，而是先把这条线标记清楚：**access difficult / shelved until venue access changes**。

## 这次为什么要 shelve
### 1) Coinbase 侧的地址/开户材料，当前就是现实门槛
快速外部核对（Coinbase Help 搜索结果）显示，Coinbase 在 identity / proof-of-address 流程中，确实会要求补充如下地址证明材料之一：
- `Bank statement`
- `Credit card statement`
- `Utility bill`

而用户当前明确给出的现实约束是：
- 当前没有可用的 **香港信用卡账单**；
- 因此 Coinbase onboarding / address verification 至少在当前阶段不顺畅，不应假装这是一个“马上就能接线”的对象。

### 2) CBETH 的非 Coinbase 可替代交易入口，看起来并不宽
快速外部核对结果：
- Coinbase Exchange 公共产品接口返回 `CBETH-USD`，状态为 `online`，说明 Coinbase 原生现货路径是存在的；
- 但对几家主流非 Coinbase 交易所的快速 API 核对里：
  - Kraken：`Unknown asset` / `Unknown asset pair`
  - Binance：`Invalid symbol`
  - Bybit：spot `list=[]`
  - Bitget：`Parameter ... does not exist`
  - OKX：`Instrument ID ... doesn't exist`

这不能证明“全世界只有 Coinbase 能买到 CBETH”，但足以支持更保守、也更实用的 desk 结论：

> **对当前这条 rank183 的现实落地来说，CBETH 不是一个在主流替代 venue 上轻松可得、可无缝迁移的标的。**

### 3) 这次 shelve 的原因是“接入现实”，不是“研究被推翻”
必须分清楚：
- 研究结论：`CBETH spot + ETH perp` 的 `15m rolling fair-basis MR` 仍然是一个曾通过 admission / honesty gate 的候选；
- 现实结论：**当前用户缺少关键 onboarding 材料，且标的 venue 可替代性弱**，所以这条线此刻不适合作为优先推进对象。

因此正确标签不是：
- “alpha 失效”
- “研究作废”

而是：
- **`operationally blocked by venue access`**
- **`shelved pending Coinbase access / alternative venue confirmation`**

## 后续执行口径（写死）
从现在起，对 `Rank 183` 采用以下口径：
1. **不再把它当作当前优先 paper launch 候选；**
2. 若后续用户补齐 Coinbase 所需地址/开户材料，或找到可信、流动性足够的非 Coinbase `CBETH` 可交易入口，再解除 shelve；
3. 在解除 shelve 之前，保留研究结论与证据链，但默认不继续投入接线/runner 实现精力。

## 一句话状态标签
`Rank 183 / cbeth-eth-rolling-fair-basis-mr`：**研究有效，但现实接入受阻；标记为开户有难度 / venue access difficult，暂时搁置。**
