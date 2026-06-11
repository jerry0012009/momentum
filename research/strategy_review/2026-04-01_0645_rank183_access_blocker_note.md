# 2026-04-01 06:45 UTC — Rank 183 access / onboarding blocker note

## 对象
- `Rank 183 / cbeth-eth-rolling-fair-basis-mr`

## 当前决策口径
- **标记为：开户 / 执行接入有难度（access-blocked）**
- **当前动作：先搁置，不作为近期优先推进的 paper / shadow / live 候选**

## 原因
1. 这条策略的可交易版本依赖：
   - `CBETH spot`
   - `ETH perp`
2. 当前研究与执行口径里，`CBETH spot` 主要对应 **Coinbase** 一侧；而可用的对冲腿是 `ETH perp`（如 Binance）。
3. 已确认：
   - `Coinbase Exchange` 公共产品列表里有 `CBETH-USD`
   - 当前已检查到的 `Binance spot / Binance futures` 公开交易对列表里**没有 `CBETH`**
4. 用户当前反馈：`Coinbase` 开户 / KYC 具备现实摩擦（例如所需账单材料当前不方便提供）。
5. 因此当前真正阻止策略推进的，不是 alpha 本身先失效，而是 **可接入性 / 账户准备度 / 标的可得性**。

## 诚实表述
- 这不是在说 `Rank 183` 的研究逻辑被证伪；
- 而是在说：**在用户当前账户与交易通道条件下，它不适合继续作为近端执行候选。**

## 后续处理建议
- 将 `Rank 183` 从“近期优先研究 -> 准执行”队列中移出；
- 保留为 `watchlist / niche relative-value candidate`；
- 若未来出现以下任一条件，再考虑重开：
  1. 用户完成 Coinbase 可用开户/KYC；
  2. 出现其他主流可接入 venue，能稳定获得 `CBETH` 现货流动性；
  3. 找到同类但更容易接入的 `LSD basis` 替代标的。

## 对当前 shortlist 的影响
- 当前不应再把 `Rank 183` 作为“下一条优先落地研究”的主推荐。
- 若继续找 `P3 / 原始 alpha / 非趋势 / 偏均值回归`，应优先转向**接入门槛更低**的对象，而不是继续投入 `Rank 183` 的执行细节。
