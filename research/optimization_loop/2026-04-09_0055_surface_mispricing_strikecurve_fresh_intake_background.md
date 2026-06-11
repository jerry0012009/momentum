# bot3 optimization loop log — surface mispricing strikecurve fresh intake -> background

- time: 2026-04-09 00:55 UTC
- target: `research/quant_digests/2026-04-08_2336_surface-mispricing-strikecurve-alpha.md`
- action: 判断 `same-event strike surface mispricing × fair-value recross / time-stop` 是否足够构成独立 prediction-market relative-value raw alpha，而不是被当前库里既有 prediction-market mispricing / term-structure / strike-gap family 吸收
- status: done
- verdict: `background / P0`
- result: `same-event strike surface mispricing × fair-value recross / time-stop` 目前仍更像 prediction-market strike-mispricing / fair-value family 的容器内实现细化；在 sibling 梯子完整度、paired fill realism、以及 post-cost realized pocket 仍未被独立坐实前，它不足以作为新的前排 fresh intake 保留。

## 本轮依据
1. 原 digest 已证明 repo 里确有一条可回测 skeleton：
   - 用同 expiry / 同事件 sibling strikes 拟合单调 survival curve；
   - 交易 `fair_mid - market_mid`；
   - 壳层包含 `edge>=2c`、`stake=100`、`max_positions=1`、`max_hold=6h`。
2. 但把它放回项目现有库里看，新增主语仍不够独立：
   - 项目内已经有 `prediction-market` 的 `term-structure mean reversion`、`same-hour strike mismatch`、`hard-expiry pair discount`、`complementary-outcome mispricing`、`strike-gap binary mispricing` 等家族材料；
   - 这条对象真正新增的主要是 **同事件多 strike 上用 isotonic/PAVA 拟合 fair curve** 的实现方式，而不是一个已经被证明不可被现有 `prediction-market relative-value / mispricing` 家族吸收的新 market pocket。
3. 诚实 / execution 侧仍缺少决定性成立证据：
   - digest 里明确承认 `梯子不全` 会让 fair curve 不稳；
   - prediction market 的核心问题仍是 `盘口很薄 / 队列优先 / 临近结算跳价`；
   - 当前没有给出 `paired long-short` 的真实可执行率、单腿暴露损失、或 post-fee realized edge 的独立证据。
4. 因此它更适合保留成 `prediction-market surface-fitting reference`，而不是进入 survivor 前排继续消耗预算。

## 收口说明
- 本轮没有给 `keep_P1`，因此不分配新 Rank。
- 本轮没有触发 survivor / P2 / P3 迁移。
- 合法动作已收口到 `background / P0`，下一轮应由 state 中的下一条 pending 小点继续。 
