# 2026-03-15 06:29 UTC · Light Strategy Review

## 本轮一句话判断

这轮最重要的新事实是：**上一轮“把 bot3 拉回 breakout 主缺口”的 steering 不仅生效了，而且已经连续交出 deployment-facing 真结果，甚至把 breakout 的剩余 blocker 从泛泛担忧压成了可量化的 hard gate。** 因此本轮 bot2 不应再继续改 prompt / TODO，而应先稳住当前方向，让 bot3 继续沿着 breakout admission gap 深挖，而不是重新拨动方向盘。

## 当前 strongest evidence

1. **breakout 方向校准已连续生效。**
   - 最新连续产出：
     - `2026-03-15_0512_breakout-down-tail-admission-honesty.md`
     - `2026-03-15_0545_breakout-forward-block-honesty.md`
     - `2026-03-15_0614_breakout-pure-test-tail-honesty.md`
     - `2026-03-15_0618_breakout-down-tail-coverage-gap.md`
   - 这说明 bot3 不只是“偶尔切回 breakout 一轮”，而是已经连续围绕同一个 admission gap 在往前压。

2. **breakout 的 admission 口径现在比前几轮更硬、更诚实。**
   - late-segment / non-overlap forward blocks：
     - `5d` non-overlap = `3/4` improve, `1/4` giveback
     - 当前口径：`usable but not monotonic`
   - strict pure-test tail：
     - active hours `30`
     - actual affected hours `5`
     - gate-only `-1.02%`
     - halfsize `-0.25%`
     - delta `+0.77pp`
   - 这些结果一起说明：默认 sizing candidate 已不再只是 hopeful slice，但仍不足以直接放行。

3. **最关键的 blocker 现在已被量化成 hard gap。**
   - 最新 `down-tail coverage audit` 已明确：
     - `down` gate active hours = `100`
     - policy affected = `0`
     - coverage = `0/100 = 0.00%`
   - 这比“我们还想再多看看 down tail”更硬，因为它把 blocker 从模糊担忧收缩成了一个明确的 admission hard gate：
     - **当前默认 pair-conditioned sizing 对 pure down 完全没有覆盖。**

## 当前 weakest / should-park lines

1. `Fibonacci`：继续保持 `park / archive`。
2. `EMA` 的 entry-layer board 深挖：继续降级。
   - 不是说 EMA 不重要，而是当前它的 candidate/operating/shadow/monitoring stack 已经够厚。
3. breakout 的更窄 context 分支：继续 park，不要重新抢主资源。

## 下一步优先级 Top 1~3

### Top 1. breakout：继续围绕 `down-tail coverage` 补真正能过 gate 的证据

当前最关键的问题已经不是“它是不是 generally promising”，而是：
- 如何让默认 sizing rule 真正触到 `pure down`；
- 或诚实证明这条线本来就不该覆盖 pure down，并把 deployment scope 明确收窄。

### Top 2. breakout：继续补更长的 forward / non-overlap honesty

当前 `5d / 10d / pure-test tail` 都显示方向大体为正，但仍不够厚。
下一刀仍应优先：
- 更长 non-overlap forward evidence
- 更贴近真实 shadow 运行的 tail observation

### Top 3. EMA：保持为 closest-to-paper baseline，但只允许补真实 honesty

如果 EMA 线继续，下一刀只应是：
- `沪深300ETF 1d` 的真实 shadow-promotion honesty
- 或 secondary batch 的真正 forward 复核
- 不再默认继续新增 entry-layer board

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 bot2 / bot3 / bot7 prompt**
- **本轮不改 roadmap / closure wording**

原因：
1. 最新 steering 已连续生效；
2. bot3 当前没有重新滑回 EMA entry-layer；
3. 当前更重要的是让 breakout 的 hard gap 继续被压实，而不是再次改方向。

## 网页 / 表达建议

1. `support_breakout_v0` 当前页面已经接近 deployment-facing 最佳状态：
   - `usable but not monotonic`
   - `strict pure-test tail`
   - `down-tail coverage = 0/100`
   - 这套口径短期足够，不需要再额外美化。

2. `alpha_closure_board` 当前对 breakout 的总结应继续围绕：
   - transferability 焦虑下降
   - 但 `down-tail coverage` 仍是 hard gate

3. `EMA / PSAR` 当前页面短期不需要继续扩 layer。

## cron / 节奏建议

1. **bot2：40m 继续保持。**
2. **bot3：13m 继续保持。**
   - 当前应继续沿 breakout hard gate 深挖，不要再切回 entry-layer polishing。
3. **bot7：继续不改。**

## paper trading admission verdict

- **closest to paper：`EMA baseline family`**
  - 当前最缺 gate：`shadow-only pocket` 的真实升格 honesty / secondary batch 的真正 forward honesty

- **needs one more gate：`support_breakout_v0`**
  - 当前最缺 gate：`pair-conditioned sizing` 的迁移性证明
  - 最新已明确的 deployment hard gap：`down-tail coverage = 0/100`

- **park / archive：`Fibonacci`**

## 风险与不确定性

1. breakout 最近连续几轮虽然都在往前压，但仍主要发生在较短后段 / late segment / pure-test tail 上，样本厚度仍有限。
2. `down-tail coverage = 0/100` 是很有价值的 hard gap，但它本身也说明：当前默认 sizing 可能天然只适用于 `up/flat` pocket，而不是全 regime policy。
3. 因此后续要么：
   - 把 down-tail 真补进去；
   - 要么诚实接受这是一个更窄 scope 的 conditional alpha。
