# Rank 334 — GA 优化 triple-barrier pair-label veto：first verdict = keep_P1

- 时间：2026-04-04 21:06 UTC
- 对象：`research/quant_digests/2026-04-04_2028_ga-triplebarrier-pair-label-veto-alpha.md`
- 本轮角色：fresh intake first verdict
- 结论：`keep_P1`，并正式分配 `Rank 334`

## 为什么不是直接丢回 background
这条对象虽然仍然依赖 pair shell，但不只是给现有 cointegration/pairs 壳随便糊一层泛化 ML filter。

当前 digest 已经把 4 个关键点讲清：
1. **pair-shell dependency 是明确且诚实的**：底层 alpha 主语就是 `cointegrated spread mean reversion`，不是把模型误写成 alpha 本体；
2. **label definition 是交易口径而不是泛 future return**：`triple barrier` 明确围绕 `tp / sl / max_hold` 的交易事件来定义“这次偏离值不值得做”；
3. **veto edge 有最小实证支撑**：本地 `15m` portability probe 虽未证明成本后已正净边，但已经证明 `take/skip` admission layer 能显著缩窄亏损与 MDD proxy，说明它确实在回答“哪些 dislocation 更值得做”；
4. **selected-subset post-cost pocket 的下一步实验面清楚**：digest 已明确留下 `EG/Johansen + residual ADF + rolling beta stability` 的 pair admission、`15m -> 5m` 迁移、`profit-first / drawdown-first` 双标签、以及 `take-rate / skipped-loss saved / selected-trade expectancy / selected-subset MDD` 这些最小 desk 版实验路径。

## 为什么还只是 keep_P1，不直接升 P2
现在证据更像“admission-layer research object 已成立”，还不是“已证明 selected subset 成本后能稳定转正”。

缺的不是主题定义，而是唯一一次 survivor follow-up 去回答：
- 在更诚实的 pair admission 与 barrier grid 下，`selected subset` 能否从“少亏一点”推进到可辩护的 post-cost pocket；
- 以及 `HRHP / LRLP` 双档标签是否真能形成可区分的 deployment 档位，而不只是同一 veto 的不同阈值表述。

所以本轮最诚实的 first verdict 是：
- **对象 distinct，值得保留到 P1；**
- **但还没到 P2 admission。**

## 对 runtime 的影响
- fresh intake 正式写为：`Rank 334 / GA-optimized triple-barrier pair-label veto`
- 由于 first verdict = `keep_P1`，它成为新的 `Surviving candidate slot`，并占用那唯一一次 follow-up 预算
- 推荐的 survivor 唯一 follow-up 方向：
  - 固定同一 pair admission / 成本口径，直接比较 `baseline all-take` vs `GA/triple-barrier label veto selected subset` 是否出现至少一个可辩护的 post-cost positive pocket；
  - 若仍只是普遍“少亏一点”，则应直接收口到 `background/P0`

## 一句话结果
`Rank 334` 不是泛化 AI filter 的换壳；它已经构成一条 distinct 的 `pairs admission-layer raw alpha` 研究对象，因此 first verdict 记为 `keep_P1`，进入 survivor 唯一 follow-up。