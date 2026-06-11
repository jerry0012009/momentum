# 2026-03-15 02:27 UTC · Light Strategy Review

## 本轮一句话判断

这轮不再继续改 prompt / TODO / cron；上一轮刚把 bot2 steering 从“轻量统揽”推向了 `paper trading admission` 视角，现在更合理的动作是**先观察新 steering 是否开始把 bot2 / bot3 的注意力压到 deployment-facing gates 上**，而不是连续两轮再加码改动。

## 当前 strongest evidence

1. **EMA 仍是三条线里最接近 `paper trading baseline` 的对象。**
   - 新近证据仍指向同一个结论：`EMA baseline family final survivor map` 已经把边界压清——`60m crypto` 出局，`A股 weekly frontier` 出局，`创业板ETF 1d` 仍是 daily survivor，`沪深300ETF 1d` 只是 `mixed / watch`。
   - 这说明 EMA 当前已经不缺“family 边界”，而缺一版 deployment-facing 的 `candidate spec / scope page`。

2. **breakout 仍值得继续，但 admission 仍未过线。**
   - `raw + avoid_fluctuating + pair-conditioned sizing` 仍是默认主原型；
   - 更窄的 `context-conditioned / pure-test × up` 已被诚实 park，说明这条线目前更该收敛到“默认候选是否够资格进 shadow paper trading”的问题，而不是再扩新变体。

3. **Fibonacci 当前仍是明确的 archived / optional filter。**
   - 没有新的证据支持它重新进入近期部署候选。

## 当前 weakest / should-park lines

1. `Fibonacci`：继续保持 archived / optional filter，不应再消耗主资源。
2. breakout 的 `context-conditioned` 分支：继续 park，不应再与默认 sizing candidate 并列。
3. EMA 线上的 wording / cleanup 型微步：继续降级，优先让位给 `candidate spec`。

## 下一步优先级 Top 1~3

### Top 1. EMA：产出一版 `paper-trading candidate spec`

最该回答：
- 哪些 pocket 先进入 baseline shadow / paper；
- 哪些 pocket 明确排除；
- `mixed / watch` pocket（如 `沪深300ETF 1d`）是先 shadow observe 还是先不做；
- 最小监控指标是什么。

### Top 2. breakout：给默认主原型一版 admission verdict

最该回答：
- `raw + avoid_fluctuating + pair-conditioned sizing` 是否已经够资格进入 shadow paper trading；
- 若仍不够，最缺的是 `test pocket` 迁移性、`down` 环境尾部，还是组合层资金曲线可信度。

### Top 3. 项目级：把三条线压成统一 admission board

建议固定三档：
- `closest to paper`
- `needs one more gate`
- `park / archive`

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 bot2 / bot3 / bot7 cron**

原因：
1. 上一轮刚做过 paper-trading 导向 steering 微调；
2. 当前更重要的是看新 steering 是否开始生效，而不是连续两轮继续推 prompt；
3. repo worktree 依旧很脏，当前阶段 bot2 再加文档层编辑，边际价值低于继续压实 admission verdict。

## 网页 / 表达建议

1. `alpha_closure_board` 下一步最值得补的是 `paper trading admission verdict`，不是更多背景解释。
2. `EMA / PSAR` 页下一步应从 `family conclusion page` 转向 `candidate spec / deployment scope`。
3. `support_breakout_v0` 页下一步应从 `follow-up research page` 转向 `shadow paper admission page`。

## cron / 节奏建议

1. **bot2：40m 先保持，不改。**
   - 方向已经改过；这轮更该观察是否开始影响真实判断，而不是继续调频或叠 prompt。

2. **bot3：13m 先保持，但默认应被拉向 deployment-facing tasks。**
   - 下一批更高杠杆任务不该再是 closure-copy，而应是 `candidate spec / admission verdict / hard gate`。

3. **bot7：先不改。**
   - 当前仍不是最缺新材料，而是最缺 admission-level 收口。

## paper trading admission verdict

- **closest to paper：`EMA baseline family`**
  - 但它是 `market-specific baseline`，不是全市场通用模板。
  - **当前最缺 gate：`candidate scope / paper spec`**，也就是“到底先做哪些 pocket、怎么监控、哪些 pocket 明确排除”。

- **needs one more gate：`support_breakout_v0`**
  - 当前仍是 `conditional alpha`。
  - **当前最缺 gate：`admission honesty verdict`**，本质上是把 `walk-forward / holdout / portfolio honesty` 压成一句可部署或不可部署的话。

- **park / archive：`Fibonacci`**
  - 当前不应进入近期 paper trading 讨论。

## 风险与不确定性

1. `EMA` 离 paper trading 最近，不等于它已经 ready；目前仍更像 baseline candidate。
2. breakout 线若 `test` 或组合层 honesty 不够硬，仍不应过早上 shadow book。
3. 本轮是“先稳住 steering、观察是否开始生效”，不是新增实验结果轮。
