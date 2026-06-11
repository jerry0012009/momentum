# Rank intake log — toxic-flow jump × short-horizon continuation

- Time: 2026-04-08 19:38 UTC
- Slot: Fresh intake
- Target: `research/quant_digests/2026-04-08_1828_toxicflow-jump-continuation-alpha.md`
- Action: first verdict
- Verdict: `background / P0`

## Why this step changed system truth
这条对象证明了一个**有用 admission 提示**：不是所有 jump 都一样，`high-tox jump` 比 `all jump` 更可能在后续 1 bar 延续，尤其 `15m` 负向高毒 jump 的 next-bar 同向漂移在当前 probe 里最强。

但它**还没压成新的独立 queue-facing raw alpha**，原因有三条：

1. **主语不独立。**
   现在真正起作用的叙事仍是“microstructure continuation / jump-event continuation”，而 `toxicity` 更像事件筛选或 admission gate。它没有把对象从既有 `OFI / imbalance / signed-flow / jump continuation` 家族里分离出来。

2. **faithful toxicity 证据还不够。**
   digest 自己已经承认当前只是 `bar-based toxicity proxy`，不是论文里的高频 VPIN / volume-synchronized flow toxicity。既然独立增量正好建立在“toxicity 比普通 flow/jump 更有信息”这一点上，那用 `24-bar abs(signed taker quote imbalance) / volume` 的代理只能证明“值得记住”，还不能证明“足够单开前排对象”。

3. **执行真实性仍未过 admission。**
   当前 strongest probe 集中在极端事件、样本稀薄、且最亮眼的是 `15m` 单资产 `BTC` 的 next-bar continuation；这更像给既有单资产 / microstructure continuation family 增加一个 `high-tox jump veto/admission layer`，而不是已经形成可独立排队的新 raw alpha。本轮 success criterion 明确要求：若仍主要停在 proxy-toxicity 与事件筛选、尚未证明 faithful VPIN / friction realism 下的独立增量，则应收口为 `background / P0`。

## Minimal honesty check used
做了最小交叉检索，确认仓内已存在多条相邻家族：
- `2026-03-25_0318_single-asset-microstructure-taker-alpha.md`
- `2026-03-30_0944_ofi-fillaware-maker-taker-alpha.md`
- `2026-04-01_0138_l1-imbalance-vwap-spread-direction-alpha.md`
- `2026-04-07_0640_persistent-imbalance-signedflow-continuation-alpha.md`

这进一步支持本轮判断：`toxicity` 当前更像这些家族上的 **event admission / regime split / veto layer**，而不是新的独立主语。

## Result sentence for runtime
`toxic-flow jump × short-horizon continuation` 证明了高毒 jump 可作为既有 microstructure/jump continuation 家族的 admission gate，但在 faithful VPIN 与 friction realism 尚未建立前，它不足以成为新的独立 queue-facing raw alpha，因此本轮 fresh intake 收口为 `background / P0`。
