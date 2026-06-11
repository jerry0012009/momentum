# Rank 281 — 三连同色 1m K 后反手 fade × TP-only exit（keep_P1）

- 时间：2026-04-01 12:32 UTC
- 对象：`research/quant_digests/2026-04-01_0528_three-candle-contrarian-tponly-alpha.md`
- 动作：fresh intake first verdict
- 结论：`keep_P1`
- 正式 Rank：`281`

## 这一步回答的问题
这条 `三连同色 1m K 后反手 fade × TP-only exit` 到底只是过度依赖 friction 的超短 scalp 幻觉，还是已经形成值得保留的可审计 raw alpha skeleton？

## 本轮判定
本轮给出 **`keep_P1`**，但明确只把它当作 **`1m-native、maker-ish、cost-fragile scalp sleeve`**，不诚实直升 `P2`。

一句话收口：

> `Rank 281` 已经形成可审计的 `1m` 单币 contrarian micro-mean-reversion raw alpha skeleton；但 close-to-close gross 只有约 `3~5 bps`、`4 bps` roundtrip 已基本吃光边，因此当前只能保留在 `P1`，后续若要升级，必须先证明在更诚实的 maker / queue / spread / markout 口径下仍留有 after-cost pocket。

## 支撑理由
1. **alpha skeleton 已清楚**
   - 触发：连续 `3` 根同色 `1m` K；
   - 方向：第三根后反手 fade；
   - 收益来源：随后几分钟的 micro mean reversion；
   - 退出：`TP + time-stop`，而不是依赖长持有。

2. **最小 transfer path 已存在**
   - 公开数据即可先测：Binance BTCUSDT perpetual `1m` klines；
   - 本地已做非重叠事件 quick check，说明这不是纯论文 headline。

3. **但成本/执行现实性是主矛盾**
   - 非重叠样本下，`1m/3m/5m` gross 平均仅约 `+4.76 / +3.86 / +3.26 bps`；
   - `4 bps` roundtrip 已几乎把 close-to-close edge 吃光；
   - 这意味着它不能被包装成 taker-heavy 通用短周期主信号，只能先按 maker-ish scalp pocket 理解。

4. **alpha 的时间分辨率边界很清楚**
   - `1m` 是原生信号层；
   - `3m/5m` 最多可当执行近似；
   - `15m` 已翻负，不应假装是同一条 alpha 的 HTF 版本。

## 为什么不是 P0
虽然 edge 很薄，但它并不是纯叙事：
- trigger / direction / exit / cost sensitivity 都已明确；
- public-data transfer 已给出同方向最小证据；
- 它更像一条 **可被诚实证伪的 maker-only scalp sleeve**，而不是无法落地的空洞形态学故事。

## 为什么不是 P2
因为当前最关键的 honesty / execution 维度还没过：
- 还没有 maker entry / maker exit 的 fill realism；
- 还没有 spread / queue miss / markout 的保守建模；
- 还没有跨 venue（Binance / Bybit / OKX）验证来排除单所微结构偶然；
- 还没有证明 admission（例如累计实体阈值、spread veto、cluster veto）能把薄 edge 变成更厚的 after-cost pocket。

所以此时升 `P2` 会把一个“可审计但显著 cost-fragile 的 1m pocket”误写成“已经接近 paper 的候选”，不诚实。

## 对 runtime 的影响
- 新对象获得正式 durable identity：`Rank 281`。
- 首判：`keep_P1`。
- 但由于当前唯一合法 survivor 仍是 `Rank 280`，本轮只记录这条新 intake 的正式 verdict 与 rank，不改写 survivor / P2 / P3 槽位。

## 若未来 reopen，这条线唯一值得花的下一步预算
只做一类 decisive follow-up：

> 在 `Binance/Bybit/OKX` 公共逐笔/L2 可得口径上，比较 `raw close fade` 与 `maker-leaning quote placement` 两种实现，保守计入 spread、queue miss、未成交与 markout 后，确认这条 `1m` 反手 pocket 是否仍能留下稳定 after-cost edge；若不能，就应回 `P0/background`。

## 最终一句
`Rank 281` 值得留档，因为它已经是清楚的 `1m` contrarian raw alpha skeleton；但它本质上是 **maker-only 倾向、对 friction 极敏感的 scalp pocket**，现阶段只配 `keep_P1`，不配更高。 
