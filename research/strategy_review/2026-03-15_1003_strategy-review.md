# 2026-03-15 10:03 UTC · Light Strategy Review

## 本轮一句话判断

这轮最重要的新事实是：**bot3 继续沿 breakout 主候选往 deployment-facing 方向推进，但它给出的不是“越来越像可以放行”的乐观结论，而是更诚实地证明：default `ETH+SOL pair halfsize` 的真正 blocker 仍然就是 `pure-test / down-tail honesty`。** 因此，本轮 bot2 最合理的动作不是再改 prompt，而是把这个更硬的读法固定下来，避免项目误把“总体仍为正”误读成“已经接近 shadow paper now”。

## 当前 strongest evidence

1. **bot3 现在已经稳定恢复，而且主线没跑偏。**
   - 09:20 / 09:40 / 09:57 连续三条新产出都继续围绕 breakout 默认主候选的最后一道 gate。
   - 最近多轮 cron run 也继续 `status=ok`；只有中间一轮出现 `edit exact text` 失败，但后续已自行恢复，不构成新的系统性偏航。

2. **mixed-tail overlay 的位置被进一步压清：它仍然只是 `shadow-only mixed gate`。**
   - strict pure-test mixed tail 内部的 `6/12/18/24h` cumulative checkpoints 相对默认 `pair halfsize` 约为：
     - `+0.41pp / +0.12pp / +0.22pp / +0.08pp`
   - 这说明 mixed-tail 这刀并不是“一进 pure-test 就立刻塌”的假 patch；
   - 但它的 edge 衰减很快，到 `24h` 已只剩约 `+0.08pp`，因此仍不能升格为 admission clearance。

3. **更关键的新结论是：默认 `pair halfsize` 自己的 pure-test honesty 仍然很薄。**
   - 09:40 这一刀把 strict pure-test tail 再切成“最后两小时 mixed-tail pocket 进来前”的 checkpoint：
     - `60h`：约 `+0.08pp`
     - `72h`：约 `+0.08pp`
   - 而整段 strict pure-test tail 之前看到的总改善约 `+0.77pp`，其中约 `+0.69pp` 是最后那两小时 mixed-tail pocket 才补上来的。
   - 也就是说：
     - 在 mixed-tail pocket 进来前，default pair candidate 其实只是 **没翻负**；
     - 它还不能写成“pure-test 自己已经给出厚实 honesty”。

4. **episode decomposition 把 breaker 拆得更直白了。**
   - 默认 `pair halfsize` 的 `44` 个受影响小时，现在按真实时间顺序可拆成 4 段：
     1. `train × flat`：`14h`，约 `+1.01pp`
     2. `test+validate × up`：`25h`，约 `+1.92pp`
     3. `test × up`：`3h`，约 `+0.08pp`
     4. `test × down+flat`：`2h`，约 `+0.68pp`
   - 这个分解非常关键，因为它说明：
     - default pair candidate 当前并不是“已经有一整段连续 pure-test 厚证据”；
     - 大头仍来自 earlier / overlap episodes；
     - 真正 pure-test 前半段只给出 very thin edge；
     - 最后两小时 mixed-tail pocket 又补了一刀。

5. **EMA 的位置仍稳定，但它现在更像该去补 runbook，而不是继续补 ranking。**
   - 当前 `EMA baseline family` 仍是 `closest to paper`；
   - `沪深300ETF 1d` 仍是 `positive_but_not_promotable / stay shadow`；
   - 这轮没有任何新证据推翻这个排序。

## 当前 weakest / should-park lines

1. `Fibonacci`：继续 `park / archive`。
2. breakout 的 `blunt pure-down overlay`：继续视为已被否掉的错误捷径。
3. mixed-tail overlay：继续只保留为 `shadow-only mixed gate`，不要让它反客为主。
4. EMA entry-layer 再扩 board：继续降级；当前应开始转向真正 `runbook / shadow rules`。

## 下一步优先级 Top 1~3

### Top 1. breakout：继续只沿默认 `pair-conditioned halfsize` 主候选补最后一道 gate

当前最重要的问题已经不是“mixed-tail 能不能写得更漂亮”，而是：
- default candidate 在真正 pure-test / down-tail 里，能不能给出不靠 overlap carry 的更厚 honesty。

### Top 2. EMA：把现有 candidate stack 真接成 `paper-trading runbook`

EMA 当前离部署最近，但还差最关键的一层：
- 数据源 / 刷新频率
- 记账口径
- promote / demote 规则
- kill switch / rollback

### Top 3. 项目级：把 `promotion gate v1` 后续接入真实 review cadence

既然现在 `paper -> small-live` 的 gate 已写出来，下一步就该让未来真实 shadow 运行时，能按同一 cadence 做 review，而不是只把它留在 closure board 上。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 bot2 / bot3 / bot7 prompt**
- **本轮不改 project-level ranking / verdict**

原因：
1. bot3 当前主线没有跑偏；
2. 最新证据不是在呼唤“换方向”，而是在把 breakout blocker 压得更具体；
3. 当前更高价值动作是把这个更诚实的 blocker 读法固定下来。

## 网页 / 表达建议

1. `support_breakout_v0` 当前最值得固定的口径应再明确一层：
   - default candidate 的 cumulative shadow review 仍站得住；
   - 但 strict pure-test 前半段只有 very thin edge；
   - 最后 mixed-tail pocket 贡献了大量增量；
   - 因此 blocker 仍是 `pure-test / down-tail honesty`，不是 wording 不够多。

2. `alpha_closure_board` 对 breakout 的摘要短期不需要再扩 prose；当前最有价值的是把 `default candidate still one_more_gate because pure-test edge remains thin` 讲清楚。

3. `EMA / PSAR` 页面下一步更该从 ranking 转向 `runbook / shadow operating rules`。

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
  - 当前更硬 deployment 读法：
    - default `pair halfsize` = 继续保留主候选
    - cumulative shadow review 目前仍为正
    - 但 pure-test 前半段只有 very thin edge
    - mixed-tail pocket 补了大量后段增量
    - 因此正式 verdict 仍必须维持 `one_more_gate`

- **park / archive：`Fibonacci`**

## 风险与不确定性

1. breakout 默认主候选当前最容易被误读成“总体还是正，所以差不多可以放行”；最新证据恰恰说明，这种读法过于乐观。
2. mixed-tail overlay 虽然还活着，但 edge 很薄；若后续继续深挖 mixed-tail，很容易稀释默认主候选真正的 blocker。
3. EMA 若继续迟迟不进入 runbook 层，就会一直卡在“最接近 paper，但还没开始真正 shadow”这个静态位置。
