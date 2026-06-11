# RESEARCH_TRENDLINE_EVENT

## 目标

为 `jerry/momentum` 建立一条新的中间研究主线：

## **trendline event foundation**

它的任务不是立刻给出最终交易策略，而是先回答：

- 趋势线 / 支撑阻力相关事件，是否真的有增量价值？
- 它们更适合被当成：
  - 直接规则型 alpha；
  - confirmation / filter；
  - 还是 feature engineering 输入？
- 在当前项目里，哪些层应该分开：
  - line detection
  - line lifecycle / state
  - event detection
  - confirmation
  - execution

---

## 为什么现在先做这个，而不是继续先押注 parallel channel

当前项目最近几天已经得到几个很关键的内部结论：

1. **raw breakout 不够强**
   - 之前 `pyindicator` breakout 回测只在 crypto 上略有表现，整体偏弱；
   - 说明“见线就追”不足以成为当前主 alpha thesis。

2. **rebound-long 虽然出现过阶段性优势，但还没完成条件审计**
   - 当前 interval sweep 的中间结论是：long 侧赢家主要来自 `rebound-long`；
   - 但这还不足以支持继续盲目优化，因为斜率、资产、周期、确认方式都可能显著影响结果。

3. **`pytrendline` explainability 已经足够成熟，可以当 research baseline**
   - 当前 `pytrendline_research` 已经把 pivot / candidate line / duplicate grouping / breakout / lifecycle / hindsight 边界讲得很清楚；
   - 但它仍然没有回答：“这些结构事件到底有没有 alpha / feature 价值”。

4. **外部材料更支持“先做 event foundation，再做策略层”**
   - `pytrendline` 更适合做 candidate line 与 breakout event generator；
   - Support/Resistance 论文更支持把线位信息当作 feature / confirmation 输入；
   - optimal stopping 论文也更支持把 touch / first break / confirmed switch 分层，而不是把“碰线、穿线、入场”混成一步。

因此，当前更合理的上位主线不是：
- `parallel_channel_alpha`

而是：
- `structure-event alpha`
  - 其中 trendline event 是最近、最容易落地、也最值得先验证的一个子方向。

---

## 当前项目里已经有哪些可复用输入

### 1. `pytrendline_research`

定位：
- explainability / candidate-line inspection baseline

它当前提供：
- support / resistance pivots
- candidate trendlines
- duplicate grouping
- breakout-tagged lines
- `score / num_points / pointset_indeces / breakout_index` 等结构字段

它最适合：
- 回答“最近这段结构里有哪些值得研究的线与事件”

它当前不适合直接承担：
- bar-by-bar 交易信号引擎
- 超长历史 / 高频实时穷举扫描

### 2. `trendline_breakout_navigator`

定位：
- bar-by-bar state machine / active line tracker

它当前提供：
- active support / resistance line
- provisional vs non-provisional line state
- wick interaction
- breakout event
- multi-timeframe trend / composite trend
- segment state extraction

它最适合：
- 回答“当前 bar 相对 active line 发生了什么”

### 3. `trendline_segment_backtest` 及 interval sweep

定位：
- 规则层回测与策略口径试探

当前阶段性信息：
- `rebound-long` 曾表现出更强的 long 侧优势；
- `30m` 是默认主候选，`60m` 在 DOGE / XRP 上保留观察价值。

它最适合：
- 提供“值得继续审计哪些事件口径”的决策信号

它当前不适合：
- 在定义未稳定前继续做大规模扩参与大范围优化

---

## 研究问题（当前版本）

这条研究线第一阶段只回答 4 个问题：

1. **breakout vs rebound**：哪一类结构事件更有继续建模的价值？
2. **slope matters?**：线的斜率方向 / 斜率强弱，是否显著改变事件结果分布？
3. **confirmation matters?**：raw breach 是否太弱，是否必须通过 close / hold / retest 之类确认层才能提升质量？
4. **line quality matters?**：`num_points / score / best-from-group` 这些“结构质量字段”是否真有增量价值？

第一阶段**不回答**：
- 最终完整策略收益最大化；
- 全市场最优参数；
- 是否一定要升级到 parallel channel。

---

## P1 判断流程（压缩版）

如果把 P1 压成最短的一条判断链，可以这样读：

1. **先用真实历史数据抽 event 样本**
   - 不直接先做完整策略净值；
   - 先看 breakout / rebound / confirmation 事件本身。

2. **先看 event-level edge，而不是先看策略收益**
   - 重点先看：
     - `sample_count`
     - `forward returns`
     - `win rate`
     - `MFE / MAE`
     - `false_break_ratio`
     - `event density`

3. **再看分层是否真的有解释力**
   - 重点分层：
     - slope buckets
     - quality buckets
     - support vs resistance
     - representative only vs all valid
     - raw vs confirmed

4. **最后才判断它更像 alpha、feature，还是该 park**
   - `alpha`：事件本身在多个 bucket / 资产 / 周期里都呈现稳定正向优势，值得继续做 MVP 策略层验证；
   - `feature`：单独做信号不够强，但明显能帮助区分情形、提升 confirmation / filter 质量；
   - `park`：样本太少、结果不稳、分层后也没有解释力，暂时不值得继续投入。

5. **只有通过这一步，才进入下一层**
   - 如果是 `alpha`：进入更完整的 signal / backtest MVP；
   - 如果是 `feature`：保留进后续结构模型；
   - 如果是 `park`：停止重投入，避免继续在弱结构上耗时间。

### 一句话版

**P1 的核心不是先证明“这个策略赚不赚钱”，而是先回答：某类 trendline event 发生后，未来价格分布有没有稳定偏移；如果有，再判断它更像 standalone alpha，还是更像 confirmation / feature。**

---

## 系统分层：这 5 层必须分开

为了避免研究口径混乱，当前先强制把系统拆成以下 5 层：

### 1. line detection
- 这一步只回答：有哪些线？
- 例子：`pytrendline` 的 support / resistance candidate lines；`navigator` 的 active line。

### 2. line lifecycle / line state
- 这一步只回答：这条线当前处于什么状态？
- 例子：candidate / valid / breakout-tagged / provisional / grouped-away / representative。

### 3. event detection
- 这一步只回答：相对这条线，价格发生了什么事件？
- 例子：touch、wick interaction、first cross、raw breach、rebound。

### 4. confirmation
- 这一步只回答：这个事件是否获得了足够证据，可以认为“状态真的切换了”？
- 例子：confirm1、confirm3、retest_hold。

### 5. execution / trading rule
- 这一步才回答：要不要入场、怎么持有、怎么退出。

当前阶段只推进前 4 层，不直接写最终执行策略。

---

## Event taxonomy（事件分层）

第一轮 event foundation 统一采用如下事件分层：

### A. touch
- 价格接触到线附近，但没有形成明确穿越或 rejection。
- 这是最弱的一层，更多是结构上下文。

### B. wick interaction
- 影线触线 / 穿线，但收盘没有完成明确状态切换。
- 可再分：
  - wick rejection bull
  - wick rejection bear

### C. first cross / raw breach
- 价格第一次明确跨越线位。
- 当前它更像“几何事件”，不直接等价于可交易信号。

### D. provisional break
- 已经跨线，但证据还很弱，只能暂时视为越界；
- 常见于：
  - 刚刚 close 在线外；
  - 但下一根是否继续仍未知。

### E. confirmed break
- 越界后又拿到了后续证据；
- 例如：
  - `confirm1`
  - `confirm3`
  - `retest_hold`

### F. rebound
- 价格触线后没有有效切换到线外，而是重新沿原结构方向离开。
- 这一步要和 wick interaction 分开：
  - wick interaction 更偏 bar-level interaction
  - rebound 更偏事件级“守线后回弹/压回”

---

## line lifecycle 与 event 的关系

line lifecycle 和 event detection 不是一回事。

### 一个更清楚的关系图是：

1. 先有一条被识别出来的线
2. 这条线进入某个 lifecycle state
   - candidate
   - valid
   - representative
   - grouped-away
   - breakout-tagged
   - provisional（navigator 语义）
3. 然后价格才会相对这条线发生事件
   - touch
   - wick interaction
   - raw breach
   - rebound
4. 然后才进入 confirmation layer
   - confirm1
   - confirm3
   - retest_hold
5. 最后才进入 execution layer

### 这意味着：
- breakout-tagged line ≠ 已确认可交易 breakout
- grouped-away line ≠ 无意义线
- provisional line ≠ 无效线
- raw breach ≠ confirmed regime switch

这是当前 foundation report 必须反复强调的边界。

---

## slope buckets（第一轮建议）

为了回答“斜率是否重要”，第一轮统一设计 slope buckets。

### 1. slope sign
- `up`
- `flat`
- `down`

### 2. slope magnitude
在同一 side / timeframe / asset 下，再按绝对斜率做分桶：
- `low`
- `mid`
- `high`

### 第一轮 operational protocol（建议定稿）

#### A. 统一先把 slope 转成“相对斜率 / relative slope per bar”
- 对每条线先取：
  - `start_price`
  - `end_price`
  - `span_bars = end_idx - start_idx`
- 再定义：
  - `relative_slope_per_bar = (end_price - start_price) / max(abs(start_price), eps) / max(span_bars, 1)`

这样做的理由：
- 比直接用原始 `m` 更适合跨资产、跨周期比较；
- 也更容易解释“这条线每 bar 大致以多快的相对速度在抬升 / 下压”。

#### B. sign bucket 口径
- 在同一 `asset × timeframe × line_side` 宇宙内，先看 `abs(relative_slope_per_bar)` 的分布；
- 用该分布的 **20% 分位数** 作为 `flat_threshold`；
- 然后定义：
  - `up`：`relative_slope_per_bar > +flat_threshold`
  - `down`：`relative_slope_per_bar < -flat_threshold`
  - `flat`：其余

这意味着：
- `flat` 不是“绝对等于 0”，而是“在当前资产 / 周期 / side 下，相对足够平”；
- 它更适合研究，而不是先拍脑袋定一个固定常数阈值。

#### C. magnitude bucket 口径
- 只对 **non-flat** 线继续做 magnitude 分桶；
- 在同一 `asset × timeframe × line_side` 宇宙内，对 `abs(relative_slope_per_bar)` 做 **tertiles**：
  - `low`
  - `mid`
  - `high`
- `flat` 线在 magnitude 维度记为：
  - `flat/na`

#### D. 第一轮推荐汇总视角
第一轮 report 中优先看两种切法：
- `sign only`：`up / flat / down`
- `sign × magnitude`：
  - `up-low / up-mid / up-high`
  - `down-low / down-mid / down-high`
  - `flat/na`

### 为什么先这样做
因为当前最需要先回答的是：
- 上升支撑上的 rebound-long，是否显著优于下降支撑上的 rebound-long？
- 突破下降阻力，是否显著不同于突破上升阻力？

在这一步之前，不值得继续泛化优化 breakout / rebound 策略。

---

## quality buckets（第一轮建议）

第一轮统一先从以下结构质量字段做分层：

- `num_points`
- `score` 分位数
- `is_best_from_duplicate_group`
- `line side`（support / resistance）

### 第一轮 operational protocol（建议定稿）

#### A. `num_points` bucket
第一轮直接用离散桶：
- `3`
- `4`
- `5+`

理由：
- 当前默认 `min_points_required=3`；
- `3 / 4 / 5+` 既贴合当前 explainability 口径，也容易直接让人理解“结构支撑程度”的层级。

#### B. `score` bucket
- 在同一 `asset × timeframe × line_side` 宇宙内，按 `score` 做 tertiles：
  - `score_low`
  - `score_mid`
  - `score_high`

第一轮先不用固定绝对分数阈值，避免不同资产 / 周期之间尺度不一致。

#### C. representative bucket
- `representative`：`is_best_from_duplicate_group == True`
- `non_representative`：其余有效线

第一轮推荐：
- **主表默认只看 representative**
- 再做一个 sensitivity 对照：
  - `representative only`
  - `all valid lines`

理由：
- 否则 duplicate groups 内大量近似线会放大样本、稀释解释；
- 但完全忽略非代表线，也可能错过“grouping 压缩是否改变结论”的信息。

#### D. `line_side` bucket
- `support`
- `resistance`

第一轮不要把 support / resistance 混成一个大盘结论；
应至少分别报告：
- support-side events
- resistance-side events

### 当前假设
这些字段未必直接等于“更赚钱”，但它们可能有助于回答：
- 哪些线更像真正的结构上下文；
- 哪些线更适合进入 confirmation layer；
- 哪些线只适合作为 feature，而不适合直接当触发器。

---

## 第一轮 scope（建议定稿）

### 资产 universe
- BTC
- ETH
- SOL
- DOGE
- XRP

### 时间周期
- `30m`
- `60m`

### 历史样本长度
- 默认：`180d`
- 若事件样本不足：扩到 `365d`

### 默认线集合
- 第一轮主分析：`representative only`
- sensitivity：`all valid lines`

### 默认事件集合
- breakout：先从 `raw_breach / close_confirm_same_bar / confirm1 / retest_hold` 开始
- rebound：先从 `wick_rejection_only / touch_close_back_inside / touch_next_bar_continuation` 开始

### 样本充分性要求（第一轮）
- 单个 bucket 若 `sample_count < 25`：
  - 只展示，不下方向性结论
- 若 `sample_count >= 25 and < 50`：
  - 可做弱结论，但必须标记 low-confidence
- 若 `sample_count >= 50`：
  - 才允许进入第一轮 go / no-go 讨论

### 第一轮默认输出顺序
1. `asset × timeframe × side` 基础覆盖表
2. `sign bucket` 汇总
3. `sign × magnitude` 汇总
4. `quality buckets` 汇总
5. `representative vs all-valid` sensitivity

---

## confirmation ladder（确认阶梯）

当前第一轮统一建议采用以下 breakout / rebound confirmation ladder，并把它们写成尽量可执行的 protocol。

### breakout ladder
1. `raw_breach`
   - 第一次明确跨线
2. `close_confirm_same_bar`
   - 同 bar 收盘也在线外
3. `confirm1`
   - 下一根仍收在线外
4. `confirm3`
   - 3 根内至少 2 根收在线外
5. `retest_hold`
   - 越线后回踩原线位不失守，再次沿突破方向离开

### rebound ladder
1. `wick_rejection_only`
2. `touch_close_back_inside`
3. `touch_next_bar_continuation`
4. `touch_htf_aligned_continuation`

### 第一轮 operational protocol（建议定稿）

#### A. 先定义“事件参考线”
- 每个事件都必须绑定到一条 **已识别 line object**；
- 第一轮默认优先看：
  - `representative only`
  - 且 line 在事件发生时已经进入可用 state（不是纯 candidate 草稿）。

也就是说，confirmation ladder 的对象不是“任意一条画出来的线”，而是：
- 已进入研究可用状态的结构线对象。

#### B. 先定义 `raw_breach` 与 `touch` 的基础几何条件
- 对 support line：
  - `touch`：bar 的 low 触达线附近，但 close 未明显收在线下；
  - `raw_breach`：bar 的 low / close 已明确越到线下。
- 对 resistance line：
  - `touch`：bar 的 high 触达线附近，但 close 未明显收在线上；
  - `raw_breach`：bar 的 high / close 已明确越到线上。

第一轮原则：
- `raw_breach` 先允许 high/low 几何越线；
- 但后续所有更强确认都用 close / 持续性 / retest 来提升质量。

#### C. `close_confirm_same_bar`
- 事件 bar 既发生越线，又在同一 bar 的 close 保持在线外；
- 它比 `raw_breach` 更强，因为排除了“只有影线刺穿一下”的很多情况；
- 但它仍然可能是单根噪声，不等于 confirmed switch。

#### D. `confirm1`
- 在 `close_confirm_same_bar` 之后，下一根 bar 的 close 仍然在线外；
- 这是第一轮最推荐的“低复杂度确认口径”；
- 原因：
  - 比 raw breach 更稳；
  - 比 confirm3 / retest_hold 更容易保留样本量。

#### E. `confirm3`
- 事件发生后的 3 根 bar 内，至少 2 根 close 维持在线外；
- 它更像一个“短窗口稳定性确认”；
- 第一轮应把它视为：
  - 比 `confirm1` 更强
  - 但样本量通常更少、入场更晚

#### F. `retest_hold`
- 越线后，价格回到原线位附近，但没有重新失守回原结构内；
- 随后再次沿突破方向离开。

第一轮建议把它视为：
- breakout ladder 里最强、也最晚的一层确认；
- 它更接近“regime switch 已经被二次验证”，而不是只看首次越线。

#### G. rebound ladder 的对应口径

##### `wick_rejection_only`
- 只有影线触线 / 穿线，但 close 没有完成越线；
- 它最弱，更多像 bar-level reaction。

##### `touch_close_back_inside`
- bar 一度触线，但收盘重新回到原结构内；
- 比 `wick_rejection_only` 更强，因为收盘重新站回了结构侧。

##### `touch_next_bar_continuation`
- 触线 / 守线后，下一根 bar 沿原结构方向继续运行；
- 这是第一轮最推荐的 rebound 确认口径。

##### `touch_htf_aligned_continuation`
- 在 `touch_next_bar_continuation` 基础上，再要求高周期方向一致；
- 第一轮把它列入文档，但默认不作为最先实现的核心口径，避免过早引入多周期复杂度。

### `provisional break` vs `confirmed switch`（第一轮建议）

为了避免把“刚越线一下”和“结构真的切换了”混在一起，第一轮统一做如下区分：

#### provisional break
满足任一：
- 只有 `raw_breach`
- 或只有 `close_confirm_same_bar`
- 但还没有拿到后续持续性证据

它的语义是：
- **状态可能在切换**
- 但证据仍不足，不能直接把它当成已确认 regime switch

#### confirmed switch
满足任一：
- `confirm1`
- `confirm3`
- `retest_hold`

它的语义是：
- **状态切换已经拿到至少一层后续确认**
- 这时才更适合进入 go / no-go 级别比较

### 第一轮推荐的实现顺序

#### breakout
1. `raw_breach`
2. `close_confirm_same_bar`
3. `confirm1`
4. `confirm3`
5. `retest_hold`

#### rebound
1. `wick_rejection_only`
2. `touch_close_back_inside`
3. `touch_next_bar_continuation`
4. `touch_htf_aligned_continuation`（先保留，后实现）

### 第一轮推荐的默认比较顺序

1. `raw_breach` vs `close_confirm_same_bar`
2. `close_confirm_same_bar` vs `confirm1`
3. `confirm1` vs `confirm3`
4. `confirm1` vs `retest_hold`
5. `wick_rejection_only` vs `touch_close_back_inside` vs `touch_next_bar_continuation`

### 核心思想
不是“越多确认越好”，而是：
- 看哪种确认在成本后更可能改善质量；
- 同时警惕样本数塌缩；
- 并始终把 `provisional break` 与 `confirmed switch` 区分开。

---

## 第一轮实验范围（先故意收窄）

### 资产
- BTC
- ETH
- SOL
- DOGE
- XRP

### 周期
- 30m
- 60m

### 样本期
- 先从 180d 开始；
- 若事件样本不足，再扩到 365d。

### 为什么这样设
- 这是当前项目已有中间结论最密集的范围；
- 能承接 `rebound-long` 的已有观察；
- 也能避免在定义未稳定前就做全市场扩展。

---

## 次级但值得保留的扩展方向（当前不设为第一优先级）

下面这些想法值得保留，但当前应明确放在 **foundation 之后**，而不是挤进第一轮主范围：

### 1. 多周期 trendline / event confirmation
- 例如：
  - `30m` 事件是否与 `60m` / `4h` 的结构方向一致；
  - 低周期 raw breach 是否只有在高周期同侧结构/趋势支持下才更可靠；
  - 不同周期的 line state 是否能形成更强的 confirmation ladder。
- 这类方向有潜力提升胜率，但前提是我们先回答：**单周期的 trendline event 本身是否已经有值得保留的信号质量。**

### 2. channel-internal state / liquidity-touch 语义
- 例如：
  - 通道内部更偏向上行漂移 / 下行漂移 / 中性回摆；
  - 价格是否接触到关键边界、mid-line、或更像“流动性关键点”的位置；
  - 某些 bounce / rejection 是否更像通道内再平衡，而不是单线事件。
- 这类方向有研究价值，也和你当前对 `parallel channel` 的兴趣一致；但它本质上属于 **更高阶结构语义**，不应先于 trendline event foundation 本身。

### 当前判断
- **值得记录**：因为它们很可能是后续提高胜率、减少假突破的重要来源；
- **不应抢主线**：因为如果单周期 / 单线事件都还没验证清楚，过早引入多周期确认与通道状态，只会让问题空间变大、结论更难归因。

---

## event-level validation：第一轮看什么

第一轮不做完整策略净值优先，而先看事件研究指标。

### 最小指标集
- `sample_count`
- `event_density`
- `forward_return_windows`
- `win_rate`
- `MFE / MAE`
- `false_break_ratio`

### 第一轮 operational protocol（建议定稿）

#### A. `sample_count`
- 定义：某个 `asset × timeframe × side × event bucket × condition bucket` 下的事件样本数；
- 它是所有结论的第一过滤器；
- 第一轮沿用前文 scope 约束：
  - `<25`：只展示，不下方向性结论
  - `25~49`：可写弱结论，但必须标记 `low-confidence`
  - `>=50`：才允许进入第一轮 go / no-go 讨论

#### B. `event_density`
- 定义：单位时间内该类事件出现的频率；
- 第一轮建议至少同时展示：
  - `events per 1k bars`
  - `avg bars between events`
- 理由：
  - 某个 event 即使 forward return 好看，如果过于稀疏，也未必适合继续做策略层；
  - 反过来，如果太高频，也可能只是噪声事件。

#### C. `forward_return_windows`
- 第一轮先统一用事件后固定窗口 forward return；
- 建议默认窗口：
  - `+1 bar`
  - `+3 bars`
  - `+6 bars`
  - `+12 bars`
- 若后续发现 30m / 60m 的节奏差异太大，再考虑按 timeframe 自适应窗口。

#### D. `win_rate`
- 定义：各 forward window 下，正向收益事件所占比例；
- 不单独决定 go/no-go，但用来辅助判断：
  - 结果是“少数大赢”驱动；
  - 还是更均匀的分布偏移。

#### E. `MFE / MAE`
- 第一轮建议都以事件后固定窗口计算：
  - `MFE`：窗口内最大有利 excursion
  - `MAE`：窗口内最大不利 excursion
- 理由：
  - 它比单纯终点收益更适合回答：
    - 这个事件是不是经常先大幅逆行；
    - 某些确认层是否明显减少了 early adverse move。

#### F. `false_break_ratio`
- 只对 breakout / confirmed switch 相关事件计算；
- 第一轮建议定义为：
  - 事件发生后，在短窗口内重新回到原结构侧、且未维持外侧状态的比例。
- 它的主要用途不是直接看收益，而是看：
  - 某类确认是否真的减少“假突破”。

### 第一轮核心比较（建议定稿）

第一轮优先按下面顺序比较，而不是一次把所有东西摊平：

1. **breakout vs rebound**
   - 先看两大事件族哪个更有继续建模的必要；
2. **raw vs confirmed**
   - 特别看：`raw_breach → close_confirm_same_bar → confirm1 → confirm3 / retest_hold`
3. **slope bucket differences**
   - 看 sign / sign×magnitude 是否真的改变 forward return 分布；
4. **line quality bucket differences**
   - 看 `num_points / score / representative` 是否提供增量解释力；
5. **support vs resistance 分开看**
   - 第一轮默认不把两侧合并成总平均；
6. **representative only vs all valid**
   - 作为 sensitivity check，而不是第一主表。

### 第一轮默认汇总顺序

foundation report 的默认阅读顺序建议是：
1. sample coverage
2. event density
3. raw vs confirmed
4. slope buckets
5. quality buckets
6. go / feature / park judgement

### 第一轮输出目标
foundation report 的结论应该更像：
- **go**：值得继续建模
- **feature**：更适合做 confirmation / filter / feature
- **no-go / park**：当前不值得继续投入

而不是：
- “这个策略已经证明赚钱”

### 第一轮 go / feature / park rubric（建议定稿）

#### `go`
至少大体满足以下几点：
- 样本量足够（核心 bucket 多数达到 `>=50`）；
- 在多个资产 / 周期 / 相邻 bucket 中方向大体一致；
- `confirmed` 明显优于 `raw`，不是随机噪声；
- slope 或 quality 分层能带来稳定解释，而不是到处翻转；
- `false_break_ratio` / `MAE` 没有显示出明显不可控的结构缺陷。

#### `feature`
常见情形：
- 单独拿来做事件信号不够强；
- 但它明显帮助区分情形，例如：
  - `confirm1` 远优于 `raw_breach`
  - 某个 slope bucket 明显更稳
  - representative lines 明显更干净
- 这时它更适合作为：
  - confirmation layer
  - filter
  - feature engineering 输入

#### `park`
常见情形：
- 样本太薄；
- 不同资产 / 周期方向经常互相打架；
- `confirmed` 相比 `raw` 没明显改善；
- slope / quality 分层也没有稳定解释力；
- 表面看起来是图形模式，但统计上没有稳定偏移。

### 当前判断边界
- 第一轮 event study 只回答“这类事件值得不值得继续”；
- 不回答“最终策略收益是否已经成立”；
- 如果进入 `go`，下一层才是 signal / backtest MVP。

---

## foundation report 最小 artifacts（建议）

第一版 `trendline_event_foundation_report` 建议只做下面这些：

1. `event_taxonomy_card`
2. `slope_bucket_summary`
3. `breakout_confirmation_comparison`
4. `rebound_confirmation_comparison`
5. `false_break_statistics`
6. `sample_coverage_table`
7. `2~4 case charts`

### 第一轮 blueprint（建议定稿）

为了避免后续实现时每个人脑补不同页面结构，第一版 foundation report 建议直接按下面顺序出页：

#### 1. `event_taxonomy_card`
**回答的问题：**
- 这页到底在比较哪些 event bucket？
- `raw` / `confirmed` / `rebound` / `provisional break` 分别是什么意思？

**建议字段：**
- `event_family`
- `event_bucket`
- `plain_language_definition`
- `belongs_to`（breakout / rebound / state-switch）
- `notes`

#### 2. `sample_coverage_table`
**回答的问题：**
- 哪些 `asset × timeframe × side × event bucket` 样本够不够？
- 哪些 bucket 只能展示，不能下结论？

**建议字段：**
- `asset`
- `timeframe`
- `line_side`
- `event_bucket`
- `sample_count`
- `confidence_flag`（`display-only / low-confidence / ok`）

#### 3. `event_density_summary`
**回答的问题：**
- 这类事件是稀有事件、可用事件，还是噪声级高频事件？

**建议字段：**
- `asset`
- `timeframe`
- `event_bucket`
- `events_per_1k_bars`
- `avg_bars_between_events`

#### 4. `breakout_confirmation_comparison`
**回答的问题：**
- `raw_breach → close_confirm_same_bar → confirm1 → confirm3 / retest_hold` 这条 ladder 里，哪一层真的改善质量？

**建议字段：**
- `event_bucket`
- `sample_count`
- `fwd_ret_1`
- `fwd_ret_3`
- `fwd_ret_6`
- `fwd_ret_12`
- `win_rate_3`
- `MFE_6`
- `MAE_6`
- `false_break_ratio`

**默认排序：**
- 先按 `event_bucket` 的 ladder 顺序
- 再按 `sample_count` 过滤置信度

#### 5. `rebound_confirmation_comparison`
**回答的问题：**
- `wick_rejection_only → touch_close_back_inside → touch_next_bar_continuation` 是否真在一层层提高质量？

**建议字段：**
- `event_bucket`
- `sample_count`
- `fwd_ret_1`
- `fwd_ret_3`
- `fwd_ret_6`
- `fwd_ret_12`
- `win_rate_3`
- `MFE_6`
- `MAE_6`

#### 6. `slope_bucket_summary`
**回答的问题：**
- sign / sign×magnitude 是否真的改变事件结果？

**建议字段：**
- `event_bucket`
- `slope_sign`
- `slope_mag_bucket`
- `sample_count`
- `fwd_ret_3`
- `fwd_ret_12`
- `win_rate_3`
- `MAE_6`
- `judgement_note`

**默认读法：**
- 先看 `sign only`
- 再看 `sign × magnitude`

#### 7. `quality_bucket_summary`
**回答的问题：**
- `num_points / score / representative` 是否提供增量解释力？

**建议字段：**
- `event_bucket`
- `quality_dimension`
- `quality_bucket`
- `sample_count`
- `fwd_ret_3`
- `fwd_ret_12`
- `win_rate_3`
- `judgement_note`

#### 8. `false_break_statistics`
**回答的问题：**
- 某类 breakout / confirmed-switch 到底是不是“看着像突破，但很快回去”的高假突破结构？

**建议字段：**
- `event_bucket`
- `sample_count`
- `false_break_ratio`
- `median_time_to_fail`
- `note`

#### 9. `representative_vs_all_valid_sensitivity`
**回答的问题：**
- duplicate grouping 压缩是否改变了结论方向？

**建议字段：**
- `event_bucket`
- `line_universe`（`representative_only / all_valid`）
- `sample_count`
- `fwd_ret_3`
- `fwd_ret_12`
- `win_rate_3`

#### 10. `2~4 case charts`
**回答的问题：**
- 抽象统计落到真实线与真实事件上，到底长什么样？

### case charts 应该优先展示
- raw breach 失败样例
- confirm1 成功 / 失败样例
- retest hold 成功样例
- rebound 在不同 slope 下的差异样例

### foundation report 的最小读法（建议定稿）

为了避免一上来盯收益均值，第一轮默认按下面顺序读：

1. **先看 `sample_coverage_table`**
   - 没样本就先别下结论；
2. **再看 `event_density_summary`**
   - 确认这类 event 不是过稀或过密；
3. **再看 `breakout_confirmation_comparison / rebound_confirmation_comparison`**
   - 先回答 raw vs confirmed 到底有没有改善；
4. **再看 `slope_bucket_summary`**
   - 观察 sign / magnitude 是否提供稳定解释；
5. **再看 `quality_bucket_summary`**
   - 观察 `num_points / score / representative` 是否提供增量信息；
6. **最后再看 `go / feature / park` judgement**
   - 这是读完前面证据后的结论，不应跳读到最前面。

### 第一轮默认不要求的东西
- 不要求一开始就有净值曲线；
- 不要求一开始就有完整交易规则；
- 不要求全市场 / 全周期覆盖；
- 不要求所有 bucket 都出 case charts。

---

## 当前暂不做什么

为了避免研究主线被打散，当前明确暂不优先做：

- 直接写最终完整策略结论页
- 在 slope / confirmation 未审计前继续泛化优化 raw breakout
- 在 foundation report 之前直接把 `parallel channel` 升成唯一主线
- 大规模全市场全周期参数扫描
- 过早引入复杂 ML 通道识别

---

## 和 parallel channel 的关系

`parallel channel` 当前仍然保留，但它的合理位置应当是：

- trendline event foundation 之后的候选升级方向

### 只有当下面至少两条成立时，才值得升到更高优先级：
1. trendline event foundation 给出明确正面证据
2. 外部资料能提供足够清晰、可迁移的 channel 定义
3. channel 能提供 trendline 单线结构没有的增量信息

换句话说：
- `parallel channel` 不是被放弃；
- 它只是暂时从“信仰”降级成“候选分支”。

---

## 当前最自然的下一步

1. 完成 `pytrendline_research` 的收尾项：
   - `candidate lines before filtering`
   - `duplicate grouping before/after`
   - 页面四段式结构收束
2. 按本文件定义，开始第一版 `trendline_event_foundation_report` 的最小 artifacts 设计
3. 再决定先做：
   - slope-conditioned rebound audit
   - 还是 breakout confirmation ladder 的最小事件研究
