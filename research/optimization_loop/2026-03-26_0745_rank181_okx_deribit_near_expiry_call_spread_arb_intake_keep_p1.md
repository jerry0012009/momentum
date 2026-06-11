# Rank 181 / okx-deribit-near-expiry-call-spread-arb intake -> keep_P1

- 时间：2026-03-26 07:45 UTC
- 对象：`research/quant_digests/2026-03-26_0658_okx-deribit-near-expiry-call-spread-arb.md`
- 执行动作：fresh intake 最小首判
- 结论：`keep_P1`
- 正式 Rank：`181`

## 本轮只回答一个问题
`short-dated cross-venue same-contract option premium convergence` 这条对象，是否值得作为前排 survivor 保留？

答案：**值得，保留为 `keep_P1`。**

但要保留的不是泛化的“crypto options 有时不有效”，也不是泛 derivatives watchlist；本轮保留的是一条更具体的 raw alpha 骨架：

> **short-dated cross-venue same-contract option premium convergence**

也就是：优先只看 `DTE<=7d`、尤其 `0~3d` 的 BTC call，在 `OKX` 与 `Deribit` 上做 `same expiry / same strike / same option type` 的 premium spread 收敛，默认表达为 `short rich venue / long cheap venue`。

## 为什么不是直接 park
1. 这条对象本体足够具体，不是模糊主题。
   - digest 已经把交易对象、entry/exit、主要成本与风险都写清楚；
   - 它是完整 raw alpha，而不是别的 alpha 的过滤器或说明文。
2. 当前最小快检虽然否定了“常开套利”，但**没有否定 pocket 本体**。
   - `45` 个近 7 天共同 call snapshot 里，`0` 个在 top-of-book 口径下立即过成本；
   - 但这更像说明 edge 只会出现在更窄事件窗，而不是说明 same-contract premium spread 完全不存在。
3. 这条线对当前 desk 有新增信息密度。
   - 它补的是 `crypto options / cross-exchange relative-value`，不是再在现有 breakout / cross-sectional 家族里内循环；
   - 而且最小数据采样门槛低，后续 cheap follow-up 可直接围绕 `settlement window / DTE bucket / liquidity bucket` 收口。

## 为什么现在还不到 P2
1. 当前证据还没证明它具备稳定、可重复、成本后能穿透的 admission 级净边。
   - 现有 snapshot 更清楚地支持“平时大多被 options 自身宽 spread 吃掉”；
   - 也就是说，本轮确认的是 **event-driven pocket 值得留**，不是“生产级跨 venue option arb 已成立”。
2. 时间稳定性、参数稳定性与 execution realism 还没被真正补齐。
   - 当前只是单时点快照，不是 `7~14d` sidecar；
   - settlement window mismatch 是否真能系统性穿过双边 spread，目前仍未被连续样本证明。
3. 它更像 survivor 应做的一次便宜决定性检查，而不是直接送入 admission。

## 下一轮唯一值得做的 follow-up 应该是什么
若继续认领 `Rank 181`，唯一值得做的 survivor follow-up 应收紧为：

- 只做 `7~14d` 的 `30s/1m` sidecar 采样；
- 只回答 **`T-180m ~ T-30m` 结算前窗口里，这条 same-contract premium spread 是否曾稳定穿过 top-of-book 成本**；
- bucket 只看 `DTE`、`moneyness`、`combined spread/liquidity`，不扩成泛 options 平台研究。

## 对系统认知的更新
**Rank 181：`short-dated cross-venue same-contract option premium convergence` 首判成立，保留为唯一一次 survivor follow-up 对象；当前保留的是近到期 OKX-Deribit 同合约 premium 收敛这条 event-driven raw alpha 本体，不是全天候 options 套利，也不是泛 derivatives watchlist。**
