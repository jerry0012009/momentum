# 2026-03-15 08:38 UTC · Light Strategy Review

## 本轮一句话判断

这轮最重要的新事实是：**上一轮修 bot3 wiring 的动作已经生效了——bot3 不但不再 skip，而且已经连续恢复出 4 条新的 optimization loop 产物，并且都继续沿 breakout 的 mixed-tail / admission 主缺口往前压。** 因此，本轮 bot2 最合理的动作不是再改 prompt，而是承认：当前执行链路已恢复，研究主线也没有重新跑偏，接下来应继续稳住 breakout 主线。

## 当前 strongest evidence

1. **bot3 wiring 修复已确认生效。**
   - 上一轮之前：连续 `skipped`，报错 `isolated job requires payload.kind=agentTurn`
   - 这轮观察到：修复后已连续恢复 `ok` 运行，并新增：
     - `2026-03-15_0806_breakout-mixed-tail-forward-honesty.md`
     - `2026-03-15_0811_breakout-policy-admission-queue.md`
     - `2026-03-15_0817_breakout-mixed-tail-walkforward.md`
     - `2026-03-15_0831_breakout-mixed-tail-conditional-honesty.md`
   - 这说明当前最危险的“13 分钟自动优化循环空转”问题已经被修掉了。

2. **breakout 主线继续沿 mixed-tail gate 往更诚实的 deployment verdict 推进。**
   - 之前已经知道：
     - `down-tail coverage = 0/100`
     - `blunt pure-down 0.5x` 不是现成补丁
     - `mixed-tail protective gate` 可能是更像样的下一刀
   - 这轮进一步确认：
     - mixed-tail 这刀虽然在 overall path 上 first-pass 为正；
     - 但一旦压到 non-overlap forward / target-pocket honesty，就已经是 `split verdict` / `1/2 正, 1/2 负`；
     - 更诚实的位置应收紧成：`shadow-only mixed gate`，而不是把它误写成已经通过的 conditional policy。

3. **breakout 的 admission queue 现在已经更清楚了。**
   - 当前 deployment-facing 排位已收敛为：
     - `default pair halfsize = keep / default candidate`
     - `mixed-tail overlay = shadow-only mixed gate`
     - `blunt pure-down overlay = reject blunt patch`
   - 这让下一轮的资源分配更清楚：
     - 默认继续沿 `pair-conditioned halfsize` 主候选推进；
     - mixed-tail 只保留为附加 gate 观察项；
     - 不再回到“是不是要纯 down 一律半仓”这种错误分支。

4. **EMA 的位置仍然稳定，没有被 breakout 这波推进推翻。**
   - 当前 `EMA baseline family` 仍是 `closest to paper`。
   - `沪深300ETF 1d` 最新更诚实口径仍是：`positive_but_not_promotable / stay shadow`。
   - 这说明当前项目级 ranking 不需要重排。

## 当前 weakest / should-park lines

1. `Fibonacci`：继续 `park / archive`。
2. breakout 的 `blunt pure-down overlay`：当前已可视为被否掉的错误捷径。
3. EMA entry-layer 再扩 board：继续降级；当前只允许补真实 honesty / runbook。

## 下一步优先级 Top 1~3

### Top 1. breakout：继续沿默认 `pair-conditioned halfsize` 主候选推进最后一道 gate

当前最值得推进的仍是：
- 默认 `pair-conditioned halfsize` 本身的更长 forward / shadow honesty；
- 不要让 mixed-tail 附加 gate 反客为主。

### Top 2. breakout：把 mixed-tail gate 固定为 `shadow-only mixed gate`

这条线现在最该回答的是：
- mixed-tail 到底只是一个可观察的附加 protection，
- 还是值得进入真正的 conditional policy queue；
- 当前证据更支持前者。

### Top 3. EMA：开始从 candidate stack 转向真正 `paper-trading runbook`

EMA 线当前若继续，下一刀比起再补 honesty，甚至更值得开始问：
- 数据源 / 刷新频率 / 记账口径 / promote-demote 规则 / kill switch
- 也就是：从 `closest to paper` 向真正可执行的 shadow runbook 再迈半步。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 bot2 / bot3 / bot7 prompt**
- **本轮不改 project-level ranking / verdict**

原因：
1. bot3 wiring 已修好并恢复产出；
2. breakout 主线没有跑偏，反而在继续变得更诚实；
3. 当前更高价值动作是“承认修复生效 + 稳住主线”，而不是再次拨方向盘。

## 网页 / 表达建议

1. `support_breakout_v0` 当前页面最该固定的 deployment 口径是：
   - `default pair halfsize = keep / default candidate`
   - `mixed-tail overlay = shadow-only mixed gate`
   - `blunt pure-down overlay = reject blunt patch`
   - `breakout verdict = one_more_gate`

2. `alpha_closure_board` 当前对 breakout 的摘要短期不需要再扩 prose；核心是把 admission queue 讲清，而不是继续堆更多解释文字。

3. `EMA / PSAR` 页面下一步更值得从 `closest to paper` 往 `runbook / shadow operating rules` 迈，而不是继续扩 layer。

## cron / 节奏建议

1. **bot2：40m 继续保持。**
2. **bot3：13m 继续保持。**
   - 当前不需要再改 wiring / prompt；
   - 让它继续沿 breakout admission gap 和 EMA runbook gap 做诚实推进。
3. **bot7：继续不改。**

## paper trading admission verdict

- **closest to paper：`EMA baseline family`**
  - 当前最缺 gate：`paper-trading runbook / shadow operating rules` + `shadow-only pocket` 的更长 promotion honesty

- **needs one more gate：`support_breakout_v0`**
  - 当前最缺 gate：默认 `pair-conditioned sizing` 的迁移性证明
  - 最新 deployment queue 读法：
    - `default pair halfsize = keep`
    - `mixed-tail overlay = shadow-only mixed gate`
    - `blunt pure-down overlay = reject`

- **park / archive：`Fibonacci`**

## 风险与不确定性

1. mixed-tail overlay 当前虽然已不是纯 lucky slice，但 target-pocket honesty 仍是 `1/2` 正、`1/2` 负，离可部署 conditional policy 还有距离。
2. breakout 线现在最容易出现的风险，不是证据完全翻负，而是系统继续在“附加 gate”上挖太深，稀释默认主候选的最后一道 admission gate。
3. EMA 虽然仍是 closest to paper，但如果迟迟不开始写 runbook / shadow rules，它也会一直停在“看起来快能上 paper”的静态状态。
