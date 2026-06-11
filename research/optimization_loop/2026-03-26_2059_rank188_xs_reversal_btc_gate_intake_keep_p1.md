# Rank 188 / adaptive shock-threshold XS reversal + BTC gate — fresh intake keep_P1

- 时间：2026-03-26 20:59 UTC
- 对象：`research/quant_digests/2026-03-26_1922_statarb-crypto-markets-xs-reversal-btc-gate.md`
- 轮次角色：bot3 fresh intake 最小首判
- 结论：`keep_P1`
- Assigned rank: `188`

## 本轮只回答一个问题
`adaptive shock-threshold XS reversal + BTC gate` 这条 repo-derived cross-sectional reversal skeleton，在当前 desk 口径下是否已经值得进入 survivor。

## 证据收口
1. digest 已经把真正该 intake 的对象压缩得很清楚：不是整个 repo headline combo，而是 **`adaptive shock-threshold` 驱动的 cross-sectional shock reversal** 这条 alpha 骨架。
2. 对 repo 原始较密映射做的 Binance perp `15m` transfer 已经给出明确否定：
   - `always-on`：gross `-0.409 bps/bar`，turnover `11.04x/day`
   - `BTC 4h>24h gate`：gross `-0.296 bps/bar`，turnover `6.28x/day`
   这足以否决“直接把 repo headline combo 搬进前排”的读法。
3. 但这轮失败更像 **压缩到短周期后过度频繁触发 / 过密 rebalance / universe 过宽**，而不是 alpha 身份本身说不清；也就是说，被当前证据打掉的是“dense 15m implementation”，还不是“shock-threshold XS reversal”这个主题本体。
4. 因而本轮最诚实的收口，不是继续保留整套 repo，也不是直接判死整个方向，而是只保留一个单轴 re-scope：**`extreme-only / sparse rebalance / top-k shock reversal skeleton`**。

## 为什么这轮给 keep_P1
survivor 配额应该留给“只差一次便宜而 decisive 的 follow-up 就能回答去留”的对象；这条线刚好满足。

- 下一步不是开放式继续研究，而是一个非常具体的问题：**如果只做最极端的 top-k shock、减少 bar-bar 重排、拉长最短持有，15m cross-sectional reversal 还能不能从高换手负 edge 里救出可交易 pocket？**
- 这是一条单一 re-scope 轴，不是把整个 stat-arb / portfolio overlay 家族重新搬回前排。
- 当前证据已经先否掉了 dense 版本，所以这一次 follow-up 的信息增量很高：要么证明确实只是 turnover 杀死策略，要么更干脆地证明这条 repo-derived skeleton 在 desk `15m` 映射下也不值得再追。

## 为什么还不是 P2
- 现在并没有任何针对 `extreme-only / sparse rebalance / top-k` 版本的正向 desk 结果；
- 唯一已落地的 transfer 结果仍然是负值；
- 因此这轮最多只能把对象收口成 **值得做一次 cheap decisive follow-up 的 survivor**，还不够直接升到 admission 阶段。

## Exact object to keep
**Rank 188 = `extreme-only / sparse rebalance / top-k shock reversal skeleton`：在 Binance perp `15m` 横截面里，只交易自适应 shock 分位数下最极端的少数币种，采用更稀疏的 rebalance / 最短持有约束，并把 BTC gate 只当 crash veto，而不是 alpha 本体。**

## System effect
- fresh intake 不再是抽象的 repo headline stat-arb 主题，而是正式收口为 `Rank 188`；
- `Rank 188` 进入 `Surviving candidate slot`，获得唯一一次 cheap decisive follow-up 预算；
- repo 原始 `dense 15m + BTC gate` 版本已被当前证据否掉，不得作为前排对象继续占位。
