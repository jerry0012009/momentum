# TRENDLINE_CONFIRMATION_PROTOCOL

## 目标

把当前 `confirmation ladder` 从“主要服务 PyIndicators 的一页报告”，升级成一份 **跨引擎可复用的事件确认协议**。

这份协议不负责定义某个引擎内部怎么画线，而只负责规定：

- 哪些事件层级应该被统一表示；
- 哪些字段必须产出；
- 不同 source 怎样进入同一张 confirmation 对照表；
- 什么情况下可以说“某个 confirmation 值得保留为默认口径”。

一句话：

> **它不是某个引擎的局部实现说明，而是 Mainline 的 confirmation 比较 contract。**

---

## 1. 为什么现在要把它协议化

当前已经有两个现实情况：

1. `PyIndicators confirmation ladder` 已经跑出了第一批真实结论；
2. `PyTrendline` 也已经从 explainability 进入了 `bridge + validation v1`，后面迟早要接进来。

如果不提前把 confirmation 层做成协议，后面很容易出现两个问题：

- 不同引擎各自用自己的事件名，无法横向比较；
- 大家都说自己做了“confirmation”，但实际上比较的不是同一层东西。

因此，这份协议的核心用途是：

- **把 confirmation comparison 从引擎实现层，提升到主线研究层。**

---

## 2. 协议边界：它管什么，不管什么

### 它管什么

- `event_family` 怎么分层（breakout / rebound / retest 等）
- `confirmation_level` 怎么表达
- 哪些字段必须进 unified table
- 哪些比较指标必须产出
- 什么情况下能说“更强确认值得保留”

### 它不管什么

- 引擎内部如何检测 line
- line score / duplicate grouping 的具体算法
- 交易执行规则（仓位、止损、滑点模型）
- 最终策略组合构造

也就是说：

- **这是一份 event-confirmation protocol**
- 不是 strategy protocol

---

## 3. 协议里的统一对象

### 3.1 最上层对象：event family

当前统一到以下 family：

- `breakout`
- `rebound`
- `retest`
- `touch`
- `switch`

第一阶段重点只强制要求：

- `breakout`
- `rebound`

其余 family 可以先保留为扩展字段。

### 3.2 confirmation level（统一枚举）

#### breakout ladder

- `raw_breach`
- `close_confirm_same_bar`
- `confirm1`
- `confirm3`
- `retest_hold`

#### rebound ladder

- `touch_only`
- `inside_0`
- `inside_1`
- `inside_2`
- `inside_3plus`

说明：
- 这些 label 是 **Mainline label**；
- 某个引擎内部可以保留自己的 native 状态名；
- 但进入主线比较时，必须映射到这些统一层。

### 3.3 `Optimal Stopping` 带来的机制解释（为什么要分这些层）

`Optimal Stopping` 这条线最值得吸收的，不是某个直接可交易参数，而是它提供了一个更稳的解释框架：

- **`touch_or_cross`** 不等于状态真的切换；
- **`provisional_break`** 只说明价格短暂离开了原结构边界；
- **`confirmed_switch`** 才更接近“原来的 support / resistance 语义真的改变了”。

因此在主线协议里，推荐把 breakout ladder 读成：

- `raw_breach`
  - 最接近：`touch_or_cross / provisional_break`
  - 说明：只说明发生了穿越，不代表 regime 已切换

- `close_confirm_same_bar`
  - 最接近：当根 bar 内的较强 provisional evidence
  - 说明：比纯 intrabar breach 更强，但仍不足以单独视为 confirmed switch

- `confirm1`
  - 最接近：一根 bar 后仍维持在线外
  - 说明：是第一层可执行的 confirmed-switch 候选

- `confirm3`
  - 最接近：短窗口内更强的持续性确认
  - 说明：它代表“状态切换并非单根噪音”的更强证据

- `retest_hold`
  - 最接近：最符合 `confirmed switch` 直觉的层级
  - 说明：它不是随手加的 filter，而是“旧边界被重新测试后未被夺回”的结构性证据

对应到 rebound ladder，可把它理解成：

- `touch_only`
  - 只看到接触，不足以说明“守住”
- `inside_0 / inside_1 / inside_2 / inside_3plus`
  - 可以理解成“重新回到原结构内部并持续停留”的强弱层级
  - 层级越高，越接近“假突破 / 未切换成功”的 retained evidence

这段映射的意义是：

- `confirmation` 以后不再只是经验主义过滤器；
- 它有了一个更清楚的机制解释：**在区分 provisional move 与 confirmed switch。**

---

## 4. 最小必备字段（source -> protocol table）

每个进入 confirmation 协议的 source，至少要产出以下字段：

- `source_engine`
- `sample_key`
- `symbol`
- `timeframe`
- `event_family`
- `confirmation_level`
- `event_timestamp`
- `line_side`
- `engine_line_id`
- `is_representative`
- `slope_bucket`
- `line_quality_bucket`
- `sample_scope`

建议附加字段：

- `event_subtype`
- `num_points_bucket`
- `score_bucket`
- `bars_since_first_cross`
- `bars_since_touch`
- `is_confirmed`
- `is_provisional`

明确允许保留为 engine-specific 的字段：

- `duplicate_group_id`
- `navigator_state`
- `active_line_start_bar`
- `active_line_reset_reason`
- `pytrendline_score`

这些可以存在，但不能当成跨引擎强制字段。

### 4.1 source-to-protocol 示例行（v1）

为了避免后续每次接 source 都只停留在口头解释，下面给 2 个 **最小示例行**。

说明：
- 这些行是 **字段落表样例**，不是最终唯一实现；
- 如果某个 source 当前没有天然对应字段，`v1` 允许先写成 `null`；
- **不要为了凑齐 schema 去伪造字段**，尤其是 `is_representative / line_quality_bucket / score_bucket` 这类 source 原生没有的列。

#### 示例 A：PyIndicators breakout_hold_1 -> mainline `confirm1`

```yaml
source_engine: pyindicators
sample_key: 60m_365d
symbol: BTC-USD
timeframe: medium
event_family: breakout
confirmation_level: confirm1
event_timestamp: <signal_ts>
line_side: resistance
engine_line_id: <segment_id>
is_representative: null
slope_bucket: down_steep
line_quality_bucket: null
sample_scope: 60m_365d
event_subtype: breakout_long
bars_since_first_cross: <confirm_bars>
is_confirmed: true
is_provisional: false
```

这行样例强调的是：
- `signal_ts + breakout_hold_1` 已经足够落到 `confirm1`；
- 但 `PyIndicators` 当前没有天然的 `is_representative / line_quality_bucket`，所以 `v1` 不应硬补假值。

#### 示例 B：PyTrendline v1 breakout -> mainline `raw_breach`

```yaml
source_engine: pytrendline
sample_key: BTC-USD_10d_5m_window96
symbol: BTC-USD
timeframe: 5m
event_family: breakout
confirmation_level: raw_breach
event_timestamp: <breakout_date>
line_side: resistance
engine_line_id: <id>
is_representative: true
slope_bucket: up_moderate
line_quality_bucket: q4
sample_scope: recent_window_96
event_subtype: breakout_tagged_line
bars_since_first_cross: 0
is_confirmed: false
is_provisional: true
```

这行样例强调的是：
- `PyTrendline v1` 当前已经足够落成一条 `raw_breach` source row；
- 但它还没有 native 的 `confirm1 / confirm3 / retest_hold` 状态层，所以不能假装已经接完整 ladder。

#### v1 的实务规则

- **字段缺失可以保留 `null`，但语义缺失不能靠硬映射掩盖。**
- 若某 source 只有 `raw_breach`，就老老实实只进 `raw_breach`；
- 若某 source 只有 `inside_0/1/2/3`，就老老实实只参加 rebound ladder；
- 先让表能诚实对齐，再谈更完整的 ladder coverage。

### 4.2 字段分层表（required / nullable / engine-specific）

为了让后续 source 接表时不再争论“这个字段到底是必须填、允许空着，还是根本不该进主 schema”，这里给一个 `v1` 分层表：

| 字段 | v1 口径 | 说明 |
| --- | --- | --- |
| `source_engine` | required | 不允许为空；必须能识别来源引擎 |
| `sample_key` | required | 至少要能识别样本窗口/实验口径 |
| `symbol` | required | 单资产样本也不应省略 |
| `timeframe` | required | 可先用 engine horizon label，但不能缺失 |
| `event_family` | required | 至少明确 breakout / rebound |
| `confirmation_level` | required | 必须落到 mainline ladder |
| `event_timestamp` | required | detection 或 confirmation 时间戳至少要有一个 |
| `line_side` | required | support / resistance 不能为空 |
| `engine_line_id` | required | 没有 id 就无法做 source-level audit |
| `sample_scope` | required | 至少要能复原样本范围 |
| `slope_bucket` | nullable | 当前 source 若没有稳定斜率桶，可先保留 `null` |
| `is_representative` | nullable | `PyIndicators` 这类 source 当前可先为 `null` |
| `line_quality_bucket` | nullable | 没有统一质量分桶时不要硬造 |
| `event_subtype` | nullable | 没有就留空，不影响 first-pass protocol compare |
| `bars_since_first_cross` | nullable | 只对部分 breakout source 原生存在 |
| `bars_since_touch` | nullable | 只对部分 rebound source 原生存在 |
| `is_confirmed` | nullable | 可以由 native ladder 推断时再填 |
| `is_provisional` | nullable | 没有原生状态就不要伪造 |
| `num_points_bucket` | engine-specific | 保留在 source audit / mapping 层，不作为 v1 强制列 |
| `score_bucket` | engine-specific | 可存在，但不要求所有 source 都有 |
| `duplicate_group_id` | engine-specific | 仅对带 duplicate grouping 的引擎有意义 |
| `navigator_state` | engine-specific | 属于 `PyIndicators` 运行态上下文 |
| `active_line_start_bar` | engine-specific | source 内部状态字段，不强制跨引擎对齐 |
| `active_line_reset_reason` | engine-specific | source 内部状态字段，不强制跨引擎对齐 |
| `pytrendline_score` | engine-specific | 仅保留为 `PyTrendline` 侧可审计字段 |

这张表的核心意思是：

- `required`：没有就不该进 protocol compare；
- `nullable`：先允许为空，但要诚实承认 coverage 不完整；
- `engine-specific`：可以保留，但不要强行升成跨引擎必填字段。

### 4.3 source onboarding checklist（v1）

当后续要把一个新 source 接进 confirmation protocol 时，默认先按下面这张 checklist 过一遍；**只有通过前 4 项，才值得继续做 compare page**。

#### 第 0 层：身份识别

- [ ] 能明确 `source_engine`
- [ ] 能明确 `sample_key / sample_scope`
- [ ] 能明确这是更像：
  - breakout source
  - rebound source
  - mixed source
  - 还是只是 explainability / geometry reference

#### 第 1 层：最小 required 字段

- [ ] `symbol`
- [ ] `timeframe`
- [ ] `event_family`
- [ ] `confirmation_level`
- [ ] `event_timestamp`
- [ ] `line_side`
- [ ] `engine_line_id`

如果这一层都不齐：
- **不要进 protocol compare**；
- 先停留在 `mapping / audit / bridge brief`。

#### 第 2 层：native -> mainline 映射是否清楚

- [ ] native state 名称已经能落到 mainline ladder
- [ ] 明确哪些层当前有 clean mapping
- [ ] 明确哪些层当前没有 mapping，必须保留空缺
- [ ] 没有把 `stronger native state` 草率误读成 `confirmed switch`

如果这层过不了：
- 说明 source 还不适合进真正的 ladder compare；
- 只能先作为 `raw-breach baseline` 或 `mechanism reference`。

#### 第 3 层：字段缺失是否诚实

- [ ] 所有 `nullable` 字段都已检查是否需要先填 `null`
- [ ] 没有为了凑 schema 伪造：
  - `is_representative`
  - `line_quality_bucket`
  - `score_bucket`
  - `is_confirmed`
- [ ] `engine-specific` 字段没有被硬升成统一必填列

#### 第 4 层：是否足够进入 compare

最小准入条件：

- [ ] 至少能稳定输出一种 `event_family`
- [ ] 至少能稳定输出一种 mainline `confirmation_level`
- [ ] 至少能产出 `overall ladder summary`

如果连这层都过不了：
- 不要急着做 ladder compare report；
- 先把 source 留在：
  - bridge
  - brief
  - mapping
  - explainability reference

#### 第 5 层：进入 compare 后的默认诚实标签

新 source 第一次进入 compare 时，默认要显式标注它属于哪类：

- `source #1 / baseline compare source`
- `raw-breach-only source`
- `partial ladder coverage`
- `rebound-only source`
- `mechanism-backed but not full-event-universe`

这样做的目的，是避免页面读者误以为：
- 只要已经进了 protocol compare，coverage 就一定完整。

### 4.4 compare-page honesty labels（v1）

为了让后续页面在展示 source 时不要各写各的说明，下面把这批默认标签正式定成 `v1`：

- `source #1 / baseline compare source`
  - 适用场景：当前主 compare 主要依赖它
  - 读者应如何理解：它是当前默认对照源，但不等于它就是“主 thesis 正确”

- `raw-breach-only source`
  - 适用场景：只能稳定产出 `raw_breach`
  - 读者应如何理解：只能参加 raw 层比较，不能假装已经接完整 ladder

- `partial ladder coverage`
  - 适用场景：已接入多层，但 coverage 仍不完整
  - 读者应如何理解：可以参与部分 ladder compare，但页面必须承认缺层

- `rebound-only source`
  - 适用场景：只在 rebound / inside ladder 上干净
  - 读者应如何理解：不应用它去支持 breakout 的强结论

- `mechanism-backed but not full-event-universe`
  - 适用场景：有机制解释或理论映射，但没有完整事件宇宙
  - 读者应如何理解：更适合作 protocol / interpretation reference，而不是 full compare source

#### 当前默认示例

- `PyIndicators`
  - 推荐标签：`source #1 / baseline compare source` + `partial ladder coverage`
  - 原因：它已经是当前最先落地的 compare source，但 breakout 侧仍缺 `close_confirm_same_bar / retest_hold` 等层，且仍混有 operational 语义。

- `PyTrendline v1`
  - 推荐标签：`raw-breach-only source`
  - 原因：当前已可进入 protocol table，但只足够支撑 `raw_breach` / touch candidate 层，不应伪装成 full ladder source。

- `Optimal Stopping`
  - 推荐标签：`mechanism-backed but not full-event-universe`
  - 原因：它帮助解释 `provisional_break / confirmed_switch`，但不是直接导出 full event rows 的 compare engine。

这组标签的作用是：

- 让页面读者一眼知道 coverage 边界；
- 避免把“已接入 compare”误读成“已经完整且可直接下主结论”。

---

## 5. 最小比较输出（每个 source 至少给什么表）

每个 source 进入 confirmation 协议后，最少要给 3 张表：

### 表 1：overall ladder summary

按：
- `sample_key`
- `event_family`
- `confirmation_level`

输出：
- `sample_count`
- `up_ratio_after_h` 或 `positive_asset_ratio`
- `mean_forward_return_h` / `mean_total_return`
- `median_forward_return_h`
- `iqr_forward_return_h`
- `trade_retention`（如果存在 parent ladder）

### 表 2：side split summary

按：
- `sample_key`
- `event_family`
- `confirmation_level`
- `line_side`

输出同上。

### 表 3：bucket split summary

按：
- `sample_key`
- `event_family`
- `confirmation_level`
- `slope_bucket`
  或 `line_quality_bucket`

输出同上。

---

## 6. 主线判定规则：什么时候说“更强确认值得保留”

默认不接受“收益均值稍微高一点”就宣称更强确认更优。

至少要同时看 3 件事：

1. **方向质量是否改善**
   - `up_ratio_after_h` / `positive_asset_ratio` 有没有提升

2. **收益质量是否改善**
   - `mean_forward_return_h` / `mean_total_return` 有没有提升

3. **样本有没有塌得太厉害**
   - `trade_retention` / `sample_count retention` 是否还能接受

默认判定逻辑：

- 若只提升收益，但 retention 严重塌缩 → 不足以直接升默认口径
- 若只提升胜率，但收益均值不改善 → 更像 filter 候选，不直接升默认口径
- 若三者一起改善 → 可以进入 `default candidate`

---

## 7. PyIndicators v1 当前怎么接入这份协议

当前 `PyIndicators` 已经是这份协议的第一个真实 source，也就是当前默认的 **source #1**。

### 7.1 native -> mainline 的最小映射例子

#### breakout 侧

当前可先按下面这个近似口径进入主线：

- `candidate_ts`
  - 更接近：`raw_breach` 的 detection timestamp

- `signal_ts + ladder_label=breakout_hold_1`
  - 更接近：`confirm1`

- `signal_ts + ladder_label=breakout_hold_2/3`
  - 更接近：`confirm3-like stronger confirmation`
  - 说明：当前 `PyIndicators` 原生层级并不等于主线枚举名字，但已经足够归并到“更强持续确认”这一层

- `breakout_hold_4`
  - 当前可先视为：`confirm3-plus / stronger-than-confirm3`
  - 说明：在主线 v1 里可先并入 `confirm3` 扩展层，暂不单独升成新默认枚举

- 当前仍没有 clean 映射到：
  - `close_confirm_same_bar`
  - `retest_hold`

也就是说，`PyIndicators breakout ladder` 当前最像：

- `raw_breach`
- `confirm1`
- `confirm3(+ )`

但还不是一套完整的 `same-bar close confirm + retest-hold` 事件宇宙。

#### rebound 侧

当前可先按下面这个口径进入主线：

- `rebound_inside_0` -> `inside_0`
- `rebound_inside_1` -> `inside_1`
- `rebound_inside_2` -> `inside_2`
- `rebound_inside_3` 及以上 -> `inside_3plus`

这部分映射当前是最干净的，因为 native label 与 mainline label 已经基本同构。

### 7.2 当前已知结论

- breakout：更强确认没有真正把整体质量救起来
- rebound retained subsets：较宽松的 `inside=0/1` 仍是当前更值得继续看的默认口径候选
- 因此 `PyIndicators` 的现实角色是：
  - 当前最先落地的 `confirmation protocol source #1`
  - 但仍不是 full event-universe truth table

---

## 8. PyTrendline v1/v2 该怎么接入这份协议

### 8.1 v1（当前）

当前 `PyTrendline` 只有：
- `event source bridge v1`
- `event validation v1`

它当前主要覆盖：
- `breakout`
- 少量 `touch candidate`

所以它现在：
- **已经可以接协议表头**
- **但还不能完整接 confirmation ladder**

当前最接近的 native -> mainline 读法是：

- `is_breakout=True + breakout_date`
  - 更接近：`raw_breach`

- `is_breakout=False + ends_at_date`
  - 更接近：`touch_only / touch candidate`
  - 说明：它当前更像“还没破、只是碰线/接近线”的对象，而不是已确认 rebound

- 当前仍没有 clean 映射到：
  - `close_confirm_same_bar`
  - `confirm1`
  - `confirm3`
  - `retest_hold`
  - `inside_0/1/2/3plus`

所以 `PyTrendline v1` 的现实定位是：

- 已足够做 source-level compare / raw-breach baseline
- 还不足够直接参加完整 confirmation ladder 对照

### 8.2 v2（下一阶段目标）

要真正进入 confirmation 协议，`PyTrendline` 至少还要补：

- `representative_only` vs `all_valid`
- `rebound / retest` 相关语义
- 更明确的 `close_confirm / confirm1 / confirm3 / retest_hold` 映射

推荐的 v2 目标口径是：

- `line touched / crossed intrabar` -> `raw_breach`
- `same bar close outside line` -> `close_confirm_same_bar`
- `next bar still outside` -> `confirm1`
- `3-bar persistence` -> `confirm3`
- `post-break retest and hold` -> `retest_hold`

也就是说，`PyTrendline v2` 真正该补的不是更多“解释图”，而是：

- 让 native state transition 能稳定落到这 5 层 mainline ladder。

---

## 9. 推荐的执行顺序

后续任何新 source，要接入 confirmation 协议时，默认按这个顺序：

1. **先接 source table**
   - 确认最小字段齐了没有

2. **再接 overall ladder summary**
   - 不要一上来就做复杂 split

3. **再接 side / bucket split**
   - support vs resistance
   - slope / quality buckets

4. **最后才写 mainline judgement**
   - breakout 是继续、park，还是只保留 feature / filter 价值

---

## 10. 当前最直接的下一步

1. 把 `PyIndicators confirmation ladder` 显式标记成这份协议的 `source #1`
2. 把 `PyTrendline v2` 的目标改写成：
   - 不是“做更多页面”
   - 而是“补齐进入 confirmation protocol 所缺字段与层级”
3. 把 `Optimal Stopping` 提供的这套 `touch_or_cross -> provisional_break -> confirmed_switch` 解释，继续落实成页面里可直接引用的 protocol 注释与 state examples
4. 后续所有 breakout/rebound 新实验，默认都引用这份 protocol，而不是各写一套确认层名字

---

## 11. 一句话总结

**从现在开始，confirmation ladder 不应再被理解成 “PyIndicators 那一页报告”，而应被理解成 `Structure-Event Mainline` 的跨引擎确认协议。**
