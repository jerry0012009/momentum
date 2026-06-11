# 2026-03-15 11:33 UTC · Light Strategy Review

## 本轮一句话判断

这轮最重要的新事实是：**breakout 默认主候选的 blocker 又被压实了一层——当前不只是 `pure down coverage = 0/100`，连最接近 pure-down 的 `pre-down bridge` 也仍然是 `0` 命中。** 这意味着 breakout 当前卡住的，不再只是“还没覆盖 pure down”这种宽泛担忧，而更像已经逼近一个更结构性的判断：**它到底是不是一条主要只适用于 `up/flat` pocket 的 narrower-scope conditional alpha。**

## 当前 strongest evidence

1. **bot3 继续稳定执行，而且仍在沿 breakout 主候选压同一个 blocker。**
   - 最新连续产出：
     - `2026-03-15_1050_breakout-puretest-active-blocks.md`
     - `2026-03-15_1103_breakout-predown-bridge.md`
     - `2026-03-15_1116_breakout-downrisk-zone-hardgate.md`
   - 最近多轮 cron run 继续 `status=ok`，说明当前不需要再改 wiring / prompt。

2. **默认 `pair halfsize` 的 pure-test 证据仍然过薄。**
   - 先前已经知道：
     - strict pure-test tail 总 delta 约 `+0.77pp`；
     - 但若先不算最后两小时 mixed-tail pocket，`72h` checkpoint 其实只有约 `+0.08pp`；
     - `44` 个 affected hours 的大头仍来自 `train × flat` 与 `test+validate × up`，真正 `test × up` 只有约 `+0.08pp`。
   - 这已经说明 default candidate 还没有给出“多段独立可复用”的 pure-test honesty。

3. **本轮又新增了一个更硬的 negative fact：pre-down bridge 仍是 0 命中。**
   - `pre-down bridge audit` 现在直接回答了一个此前仍可能自我安慰的问题：
     - 即使 default `pair halfsize` 没直接命中 pure `down`，它会不会至少在 pure down 来临前几小时提前减仓？
   - 当前答案仍是否：
     - future `6h` bridge：`0/5`
     - future `12h` bridge：`0/11`
     - future `24h` bridge：`0/23`
   - 最关键的 `12h` bridge 还是一整段 `validate × flat` 的前置滑落，自身条件累计约 `-3.92%`，但 default pair 仍完全没命中。
   - 这让 blocker 的读法明显升级：
     - 当前缺口不只是 `pure down coverage = 0/100`；
     - 连最接近 pure-down 的 anticipatory bridge 也没有 coverage。

4. **因此 breakout 的 one_more_gate 已越来越像结构性 scope 问题，而不只是局部证据不够。**
   - 组合层 hourly path：已经不是主 blocker；
   - 更长 `5d/10d` forward honesty：也已从 lucky slice 降级为“usable but not clearance”；
   - mixed-tail：继续只配 `shadow-only mixed gate`；
   - blunt pure-down：继续 reject。
   - 剩下最硬的问题只剩：
     - default candidate 在 `pure-test / down-tail / pre-down bridge` 上仍然几乎没给出厚实覆盖。

5. **EMA 的位置仍稳定，不受本轮影响。**
   - `EMA baseline family` 仍是 `closest to paper`；
   - `沪深300ETF 1d` 仍是 `positive_but_not_promotable / stay shadow`；
   - 当前最合理下一刀仍是：把现有 candidate / operating / monitoring 接成 `paper-trading runbook`。

## 当前 weakest / should-park lines

1. `Fibonacci`：继续 `park / archive`。
2. breakout 的 `blunt pure-down overlay`：继续视为已被否掉的错误捷径。
3. breakout 的 `mixed-tail overlay`：继续只保留 `shadow-only mixed gate`，不让它反客为主。
4. EMA entry-layer 再扩 board：继续降级；当前该转向 runbook / shadow rules。

## 下一步优先级 Top 1~3

### Top 1. breakout：从“继续补 patch”转成回答 scope 问题

当前最值得推进的问题，已经不只是“还能不能再补一刀 down-tail protection”，而是：
- 这条 breakout 默认主候选是否应诚实收敛为一个**主要适用于 `up/flat` pocket** 的 narrower-scope conditional alpha；
- 如果答案是是，那么后续页面与 admission 口径都应围绕这个更窄 scope 去写，而不是继续默认期待它能补成全 regime policy。

### Top 2. EMA：把 `candidate / operating / monitoring` 真接成 runbook

EMA 仍是离部署最近的对象；当前最该做的不是再补 ranking，而是：
- 数据源 / 刷新频率
- 记账口径
- promote / demote
- kill switch / rollback

### Top 3. breakout：若仍继续补证据，优先只找“真正 overturn scope 结论”的证据

也就是说，只有当后续新证据能做到下面至少一条，才值得继续投入同类 micro-cut：
- 真正命中 pure `down` 小时且不翻负；
- 在 pre-down bridge 上出现非零、可复用 coverage；
- pure-test active blocks 不再只剩单格 / very-thin edge。

否则，再继续补同类小切片的边际价值会快速下降。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 bot2 / bot3 / bot7 prompt**
- **本轮不改 project-level ranking / verdict**

原因：
1. 最新几轮依然有真实新证据，不属于“连续两轮只补 wording / cleanup”；
2. 当前更高价值动作是把 blocker 的新读法讲清，而不是再拨一次方向盘；
3. 真要做下一次 steering，更值得等 scope 问题再多一刀证据后再收一次，而不是现在就过早改写主线。

## 网页 / 表达建议

1. `support_breakout_v0` 当前最值得固定的一句 deployment-facing 话应升级为：
   - default candidate 的问题不只是 `pure down = 0/100`；
   - 连 `pre-down bridge` 也还是 `0` coverage；
   - 因此 blocker 更像 scope 问题，而不只是 local patch 不够。

2. `alpha_closure_board` 当前对 breakout 的摘要短期不需要再扩 prose；但下一刀若要改表达，最有价值的就是把这句写清：
   - `breakout may be converging toward an up/flat-biased conditional alpha unless future evidence overturns the down-tail gap`。

3. `EMA / PSAR` 页面下一步仍更该转向 `runbook / shadow operating rules`。

## cron / 节奏建议

1. **bot2：40m 继续保持。**
2. **bot3：13m 继续保持。**
   - 当前不需要再改 wiring / prompt；
   - 继续沿 breakout 主候选最后一道 gate 与 EMA runbook gap 往前压。
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

1. breakout 当前最容易被误读成“虽然没打到 pure down，但至少会提前减仓”；最新 bridge audit 已经说明，这种安慰式读法目前并不成立。
2. 若后续继续沿同类微切片推进，却始终没有出现非零 pure-down / pre-down coverage，bot2 迟早需要把主线收紧成“接受 narrower scope”的明确 steering。
3. EMA 若继续迟迟不进入 runbook 层，仍会长期卡在“closest to paper 但没真正开始 shadow”的静态状态。
