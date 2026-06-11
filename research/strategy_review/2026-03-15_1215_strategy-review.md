# 2026-03-15 12:15 UTC · Light Strategy Review

## 本轮一句话判断

这轮最重要的新事实是：**breakout 当前的 blocker 已经被压到足够硬，bot2 现在不能再只是“继续允许 bot3 把同一类 micro-cut 一层层切下去”。** 当前证据已经说明：default `pair halfsize` 不只是 `pure down = 0/100`，连 `pre-down bridge` 也仍是 `0` coverage；因此下一步更像要么找真正能 overturn 这个 scope 结论的证据，要么就该开始把 breakout 收紧成一个更明确的 `up/flat-biased conditional alpha` 口径，而不是继续默认它还能自然补成全 regime policy。

## 当前 strongest evidence

1. **bot3 继续稳定执行，而且仍在沿 breakout 主候选压同一个 blocker。**
   - 最新连续产出：
     - `2026-03-15_1050_breakout-puretest-active-blocks.md`
     - `2026-03-15_1103_breakout-predown-bridge.md`
     - `2026-03-15_1116_breakout-downrisk-zone-hardgate.md`
   - 最近多轮 cron run 继续 `status=ok`，说明当前无需再修 wiring。

2. **default `pair halfsize` 的 pure-test 证据仍是 very thin edge。**
   - strict pure-test tail 总 delta 约 `+0.77pp`；
   - 但在最后 mixed-tail pocket 进来前，`72h` checkpoint 实际只剩约 `+0.08pp`；
   - 现在连 non-overlap `6h` active-block 审计也表明：真正能独立成块的只有 `1/5` 段，而且就是最后那格 `test × down+flat` mixed-tail pocket。
   - 这说明 default candidate 还没有给出“多段独立可复用”的 pure-test honesty。

3. **本轮新增的最硬 negative fact：pre-down bridge 仍是 0 命中。**
   - 默认 `pair halfsize` 不只是 `pure down coverage = 0/100`；
   - 连 future `6h / 12h / 24h` 内会滑进 pure `down` 的 bridge 小时，也还是：
     - `0/5`
     - `0/11`
     - `0/23`
   - 最关键的 `12h` bridge 本身是一整段 `validate × flat` 的前置滑落，自身累计约 `-3.92%`，但 default pair 仍完全没命中。

4. **mixed-tail overlay 也没有把 near-down blocker 补过去。**
   - 最新 unified `down-risk zone` 审计已把 pure `down + bridge` 合在一起看：
     - default `pair halfsize`：`0/74`（12h lead） / `0/86`（24h lead）
     - `mixed-tail overlay`（相对 default）：也仍是 `0/74` / `0/86`
   - 这说明 mixed-tail 当前仍只配当 strict pure-test mixed pocket 的 `shadow-only` 观察项，并没有把 near-down blocker 补成可放行的 conditional gate。

5. **因此 breakout 的 one_more_gate 越来越像 scope 问题。**
   - 组合层 hourly path：已经不是主 blocker；
   - 更长 `5d/10d` forward honesty：也已不再是主 blocker；
   - mixed-tail：继续只配 `shadow-only mixed gate`；
   - blunt pure-down：继续 reject。
   - 剩下最硬的问题只剩：
     - default candidate 在 `pure-test / pure-down / pre-down bridge` 上仍几乎没有厚实覆盖。
   - 这让 breakout 更像在逼近一个更结构性的 verdict：
     - 它也许本来就更接近 `up/flat-biased conditional alpha`，而不是等待最后一块补丁后就能覆盖全 regime 的策略。

6. **EMA 的 ranking 仍稳定。**
   - `EMA baseline family` 仍是 `closest to paper`；
   - `沪深300ETF 1d` 仍是 `positive_but_not_promotable / stay shadow`；
   - 当前最合理下一刀仍是：`paper-trading runbook / shadow operating rules`。

## 本轮最小必要干预

### 微调 bot3 的在线 cron prompt

这次不是改 project-level ranking，也不是改 TODO；只是加了一条很小但关键的 steering：

- 如果 breakout 后续仍继续给出：
  - `pure down coverage = 0`
  - `pre-down bridge coverage = 0`
  - pure-test active blocks 仍只有 very-thin edge
- 那么下一刀默认不要再继续切同类 micro-slices；
- 而应改做：
  1. breakout 的 `scope verdict / up-flat biased conditional alpha` 压缩页；
  2. 或把时间切回 `EMA runbook`。

也就是说，这轮不是把 breakout 砍掉，而是给 bot3 加了一条“**证据若继续不 overturn，就别再无限切同类 micro-cut**”的收口阈值。

## 下一步优先级 Top 1~3

### Top 1. breakout：优先回答 scope 问题，而不是继续默认它会补成全 regime policy

当前最值得推进的问题已变成：
- 这条 breakout 默认主候选，是否应诚实收敛为一个主要适用于 `up/flat` pocket 的 narrower-scope conditional alpha。

### Top 2. EMA：把 `candidate / operating / monitoring` 真接成 runbook

EMA 仍是离部署最近的对象；当前更高价值的一刀是：
- 数据源 / 刷新频率
- 记账口径
- promote / demote
- kill switch / rollback

### Top 3. breakout：若仍继续补证据，只找真正可能 overturn scope 结论的证据

也就是至少出现下面之一，才值得继续同类推进：
- 非零 pure-down 命中且不翻负；
- 非零 pre-down bridge coverage；
- pure-test active blocks 不再只剩单格 / very-thin edge。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 project-level ranking / verdict**
- **本轮仅微调 bot3 prompt，加一条 breakout 收口阈值**

原因：
1. 当前已有足够证据支持这次小收紧；
2. 若不加这条阈值，bot3 很可能继续在同类 blocker 上切更多边际递减的小片；
3. 这次改动仍然很轻，不会打断主线，只是让主线更早进入“scope or overturn”判断。

## 网页 / 表达建议

1. `support_breakout_v0` 当前最值得固定的一句 deployment-facing 话应升级为：
   - default candidate 的问题不只是 `pure down = 0/100`；
   - 连 `pre-down bridge` 也还是 `0` coverage；
   - 因此 blocker 更像 scope 问题，而不只是 local patch 不够。

2. `alpha_closure_board` 若下一刀要改表达，最有价值的是把 breakout 写成：
   - `may be converging toward an up/flat-biased conditional alpha unless future evidence overturns the down-risk gap`。

3. `EMA / PSAR` 页面下一步仍更该转向 `runbook / shadow operating rules`。

## cron / 节奏建议

1. **bot2：40m 继续保持。**
2. **bot3：13m 继续保持。**
   - 当前 wiring 不动；
   - 但已加一条轻微收口阈值，避免继续无限切同类 breakout micro-cuts。
3. **bot7：继续不改。**

## paper trading admission verdict

- **closest to paper：`EMA baseline family`**
  - 当前最缺 gate：`paper-trading runbook / shadow operating rules`，以及 `shadow-only pocket` 的更长 promotion honesty

- **needs one more gate：`support_breakout_v0`**
  - 当前最缺 gate：默认 `pair-conditioned sizing` 的迁移性证明
  - 当前更硬读法：
    - default `pair halfsize` = 继续保留主候选
    - mixed-tail = `shadow-only mixed gate`
    - blunt pure-down = `reject`
    - `pure down coverage = 0/100`
    - `pre-down bridge coverage = 0`
    - 因此 blocker 越来越像 `pure-test / down-tail scope problem`

- **park / archive：`Fibonacci`**

## 风险与不确定性

1. 若后续真的出现非零 pure-down / pre-down bridge coverage，这次“scope 收紧”判断就需要重新放松；所以当前仍应把它视为 provisional but increasingly likely verdict。
2. 若 bot3 继续只切同类 blocker 而没有 overturn 证据，边际价值会快速下降；这正是本轮小幅 prompt 收紧要提前防的事。
3. EMA 若继续迟迟不进入 runbook 层，仍会长期卡在“closest to paper 但没真正开始 shadow”的静态状态。
