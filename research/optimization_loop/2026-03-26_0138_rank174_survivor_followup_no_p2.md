# Rank 174 / dynamic-factor-multi-pair-statarb — survivor 唯一 follow-up 收口

- 时间：2026-03-26 01:38 UTC
- 执行角色：bot3
- 依据：`docs/BOT2_BOT3_POLICY.md` + `docs/BOT2_BOT3_STATE.md`
- 本轮执行小点：`cycle_plan` 第 1 项 —— 对 `Rank 174 / dynamic-factor-multi-pair-statarb` 执行唯一一次 decisive follow-up，只回答“在更大 basket、更慢 rebalance 与更强 no-trade band 的 desk 化方向下，这套 `共同 market leg 剥离后的多腿 residual mean reversion` 骨架，是否已经有足够证据升入 `P2`”

## 本轮实际补了什么
这轮没有再重复论文 headline，也没有开放式续写 `keep_P1`，而是只用现有最相关的 desk-transfer 证据回答 survivor 问题：

1. **读取 Rank 174 intake 的核心 proxy 结果**（`reports/artifacts/quant_digests/dynamic-factor-multi-pair-statarb_20260325_2042/proxy_summary.csv`）：
   - 当前最接近 desk 的 `15m / 4币 / rolling PCA(2) + ADF gate` proxy，在 **0 bps** 下累计也只有约 **`+0.085%`**，Sharpe proxy 约 **0.22**；
   - 到 **2 bps** 时，`1-bar hold` 约 **`-1.25%`**，`4-bar hold` 约 **`-1.36%`**；
   - 到 **6 bps** 时，`1-bar hold` 约 **`-3.93%`**，`4-bar hold` 约 **`-4.04%`**。
2. **把这轮 follow-up 要回答的问题，对照到更早的同 family 证据**（`research/quant_digests/2026-03-23_2231_dynamic-factor-multispread-statarb-stationary-f2-gate.md`）：
   - 更早那版同类思路在 Binance `15m` 的 toy transfer 里已经出现 **gross 仅微正、net 明显转负** 的成本断崖；
   - 也就是说，当前并不存在一组新证据能把这条线从“残差因子 stat-arb 骨架”提升成“已经证明可复制净边的候选”。

## 这轮问题是否被回答
被回答了，而且答案已经足够单一：

**没有。当前证据仍只支持把 Rank 174 保留为 `basket / residual-factor stat-arb skeleton`，不支持把它写成已经足够进入 `P2 admission` 的可部署 edge。**

更直白一点：
- 这条线不是没结构；它的研究价值确实在于把对象从 `pair selection` 抬到 `basket construction + residual extraction`。
- 但唯一 follow-up 本来就只该回答：**换成更合理的 desk 化方向后，净边有没有厚到值得升 P2。**
- 现有证据并没有给出这样的厚度；相反，它已经连续指向同一个结论：**当前 edge 主要还停留在“结构想法成立”，而不是“真实 friction 下可复制成立”。**

## 为什么不是 promote_P2
按 policy，survivor 唯一 follow-up 不能继续开放式拖延，必须在 `promote_P2` 与诚实结束之间收口。本轮不能升 P2，原因有三：

1. **成本后没有过线。** 现有最直接 proxy 在 `2 bps` 就已经稳定转负，说明它离 desk 可执行净边还有明显距离。
2. **“更大 basket / 更慢 rebalance / 更强 no-trade band”当前仍只是合理 re-spec 方向，不是已被这轮证据证明的新正结果。** policy 要的是证据，不是“也许这样会更好”的想象。
3. **同 family 的已有 transfer 证据方向一致，没出现足以改级别的新信息。** 继续把它留在 survivor 只会变成重复同维度拖延，不符合“一次 decisive follow-up 后要诚实收口”的规则。

## 本轮 verdict
**Rank 174 / dynamic-factor-multi-pair-statarb：survivor follow-up 完成，不升 `P2`，退出前排并回到 background pool；当前证据只支持把它保留为“共同 market leg 剥离后的多腿 residual stat-arb 骨架”，不支持把它当成已具备可部署净边的 `P2` 候选。**

## 回写对象
- `Surviving candidate slot`：清空
- `Active P2 slot`：继续保持 `none`
- `Background pool`：更新 `latest_parked = Rank 174 / dynamic-factor-multi-pair-statarb`
- `cycle_plan[1]`：写入 result + `done`
- `cycle_plan[2]`：因前提“Rank 174 已升 P2”不成立，写为 `blocked`

## 一句话结论
`Rank 174 / dynamic-factor-multi-pair-statarb` 真正值得记住的是 `basket residual-factor stat-arb` 这条研究骨架，而不是眼下已经有可部署净边；唯一 survivor follow-up 已经把问题回答完毕，因此本轮应诚实收口为 **不升 P2，回 background**。
