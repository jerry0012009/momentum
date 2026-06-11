# TODO Archive（moved from TODO.md on 2026-03-24）

> 这个文件保存 `TODO.md` 中已从主面板移出的历史主线、旧模块规划、旧阶段结论和历史里程碑。
> 当前 bot2 / bot3 运行不依赖本文件；它主要用于人类回看历史上下文。

## 当前总纲（2026-03-12）

### 已收工研究线（2026-03-14）— PyTrendline v3

> `pytrendline_event_validation_v3` 这条研究线已经正式收工，不再作为当前 bot3 20m auto loop / TODO agent 的默认认领对象。后续若没有用户明确 reopen，自动化应把它视为 **已归档结论**，只在需要引用历史证据时回看。

#### V3 Close-out Summary
- [x] 已完成代码与事件归属审计。
  - 关键审计页：`reports/site/factors/pytrendline_event_validation_v3_breakout_side_audit/report.html`
  - 关键修复页：`reports/site/factors/pytrendline_event_validation_v3_sampler_fix_rerun_a4c/report.html`
- [x] 已完成用户可读版主报告梳理。
  - 主报告：`reports/site/factors/pytrendline_event_validation_v3/report.html`
- [x] 已完成 `180d core4` 扩样本页。
  - 长样本页：`reports/site/factors/pytrendline_event_validation_v3_crypto_180d/report.html`
- [x] 已完成 `OOS honesty + 小参数稳健性 + final verdict`。
  - Final verdict 页：`reports/site/factors/pytrendline_event_validation_v3_final_verdict/report.html`

#### V3 Final Call（固定口径）
- [x] `keep as alpha candidate`：`support_breakout_raw @ h24`
- [x] `keep as co-primary alpha candidate`：`support_breakout_confirm_1 @ h24`
- [x] `park as primary variant`：`support_breakout_confirm_2`
- [x] `keep as feature/watch, not alpha`：`support_rebound_confirm_1`
- [x] `V3 overall`：可以收工。收工方式不是“确认了成熟 production alpha”，而是——**保留 breakout-short 候选，关闭 v3 研究线，把后续动作移到更窄的实现验证或 alpha-candidate follow-up。**

#### 对自动化 / 定时任务的明确约束
- [x] bot3 / TODO agent 默认**不再继续认领** `V3X-*` 的扩样本、跨市场、大全参数搜索等后续工作。
- [x] 若后续需要继续，只允许在用户明确 reopen 时，作为一条新的、更窄的后继线单独立项（例如成本层 / 执行层 / 非重叠持仓 / 实盘约束验证）。
- [x] 当前应把 v3 当作 **已完成的历史证据包**，而不是当前主线 backlog。
- [x] bot3 的核心职责应始终理解为：**从 TODO / 当前 closure 线里认领一个具体小任务，完成一个真实可见的小步，并留下产物。**
- [x] bot3 的默认成功标准不是“本轮没报错”，而是“本轮有具体任务、有真实推进、有可审计痕迹”。
- [x] bot3 的成果默认不应只停留在邮件或日志里；只要本轮确实有推进，默认应尽量把成果落实到相关网页 / 报告 / plans / closure 页面，让 Jerry 能在站点上直接看到产出。

#### 推荐读者入口（替代旧 v3 深挖顺序）
- `reports/site/factors/pytrendline_event_validation_v3_final_verdict/report.html` ← 默认入口
- `reports/site/factors/pytrendline_event_validation_v3_crypto_180d/report.html` ← 长样本补充证据
- `reports/site/factors/support_breakout_v0_h24/report.html` ← 保留下来的 breakout-short 原型页


### 主判断

当前项目真正的上位主线不是“继续深化某一个画线库”，而是：

## **Structure-Event Alpha Research**

也就是：
- 先研究 **结构事件本身**（trendline / support-resistance / breakout / rebound / confirmation）是否有稳定增量价值；
- 再决定它们更适合：
  - 直接做规则型 alpha；
  - 作为 confirmation / filter；
  - 或者只作为 feature；
- `parallel channel`、`pytrendline`、`pyindicators` 都先看作 **定义方式 / 事件来源候选**，而不是默认主结论。

### 为什么要这样重排

1. **PyIndicators 这条线已经给了我们重要反证**
   - 之前大量回测表明：raw breakout 整体偏弱；
   - 只有少数市场 / 少数 subset 有一点点效果；
   - 所以它更像一个 **baseline event source**，不再是默认要继续重仓深化的主 thesis。

2. **PyTrendline 更像 explainability baseline，而不是直接给 alpha 结论**
   - 它很适合把“线是怎么来的”讲清楚；
   - 但它还没有直接回答“这些结构事件值不值得继续研究”。

3. **真正值得推进的是跨定义方式的统一事件研究**
   - 同一个 `breakout / rebound / confirmation` 问题，可以由不同引擎给出样本；
   - 真正该沉淀的，是统一的 event schema、validation protocol、decision rubric。

### 当前执行路线（2026-03-12，供 Agent 直接执行）

> 这一段是接下来 1~2 周的默认主线，优先级高于零散优化。原则：**先把 `PyTrendline` 变成干净可验证的 event source，再决定是否进入 signal / strategy 层。**

1. **冻结 / 降级 PyIndicators**
   - 不再继续做 raw breakout 的泛化优化；
   - 仅保留其作为 baseline event source / 对照组的定位。
2. **推进 PyTrendline → unified event schema**
   - 先明确哪些对象可映射成 mainline event；
   - 产出最小 event sample，作为后续 validation 输入。
3. **补趋势线文献与外部实现地图（与主线并行推进）**
   - 聚焦 trendline breakout / rebound / retest / confirmation；
   - 为后续 event 定义与 validation 提供外部参考；
   - 默认要求：E 模块的每轮产出都尽量直接服务当前主线问题，而不是做泛泛资料堆积。
4. **先做 event-level validation，不先做完整策略**
   - 先比较 breakout vs rebound、raw vs confirmed、quality / slope / representative buckets；
   - 先回答“事件有没有信息量”，再回答“值不值得交易”。
5. **只有在 evidence 足够时，才进入 MVP signal / strategy validation**
   - 默认只做 1~2 个最小规则型信号，不做大参数优化。
6. **默认执行节奏：短期进入“三条收口线优先”**
   - 当前短期优先对象改为：
     1. `V3 final-verdict / breakout-short follow-up`（围绕已收工的 v3 结论，继续把保留下来的 breakout-short 候选讲清楚、挂清楚、接到更接近策略的验证层）
     2. `Fibonacci confirmation / retest_hold`（把这条线正式收口并讲清楚它为什么不是当前主 alpha）
     3. `EMA / PSAR raw alpha focus`（补更完整回测、成本、OOS、角色判断）
   - 默认优先目标不再是继续扩张候选池，而是：**把已经接近收口的 3 条研究线做成更清楚、更诚实、可直接支持下一步研发决策的网页与结论**。
   - 短期建议顺序：
     1. 先把每条线的当前结论、边界、适用环境、别过度解读什么写清楚；
     2. 再补最小但关键的完整性工作：成本、OOS、rolling、稳定性、组合/角色判断；
     3. 再做一页更上位的比较页，回答“这 3 条线谁更像主 alpha、谁更像 filter / candidate、谁该 park”。
   - 若这 3 条线中的任一条在更完整验证后明显转弱、收口为 `park` 或边际价值显著下降，再把释放出来的时间回拨给 `E. External Alpha / Literature Scout` 去继续找新 alpha。

### 当前补充判断（2026-03-14）

- 基于 `Naganjaneyulu et al. (2023)` 的 clean-room replication 与后续 `EMA / PSAR Raw Alpha Focus Report`，当前新增一个**小重点结论**：
  - **EMA** 应升格为当前项目的 `raw alpha baseline` 候选；
  - **PSAR** 应保留为第二原始 alpha 候选，但当前更像 `fast reaction / loss-protection` 风格，不应在解释上和 EMA 混成同一种角色；
  - 这条结论是“后续值得继续研究的两个原始策略”，**不是**说论文里的完整 `MIHS / MIHCS regime gate` 已经升级为当前主 alpha 主线。
- 因此短期默认策略应理解为：
  - 暂时不再把 `E-first` 作为第一优先级；
  - 先把 `V3 / Fibonacci / EMA-PSAR` 这 3 条已接近收口的线真正收完整、讲清楚、挂到网页主入口；
  - 其中：
    - `V3 final-verdict / breakout-short follow-up` 负责回答：v3 收工之后，当前真正值得留下来的结构事件候选到底是什么、该如何更接近策略层地继续验证；
    - `Fibonacci` 负责回答它更像有用 filter 还是伪希望，并把这条线诚实收口；
    - `EMA / PSAR` 负责回答当前最朴素 raw alpha baseline 究竟值不值得继续往更完整回测 / 稳定性 / 半实盘准备推进；
  - 只有当这 3 条线完成一轮更完整 closure 后，才把默认重心重新拨回 `E` 模块继续找新 alpha。

### 当前更高目标（历史归档说明）

> 下方这一大段原本属于 **deployment-first / tiny-live bridge** 时期的旧口径。
> 从 `2026-03-24` 起，默认不再作为 bot2 / bot3 的排班依据。
>
> 当前统一改读为：
> 1. 先 **fresh intake** 新策略 / 新论文 / 新 repo / 新 alpha；
> 2. 再做最小但诚实的验证，快速给出 `park / keep_P1 / promote_P2 / promote_P3`；
> 3. 能进 `Paper / 待开启自动运行` 的对象尽快 handoff；
> 4. `tiny-live / live-shadow / paper->tiny-live bridge / deployment-first blocker` 一类旧目标，当前全部视为**冻结归档话题**。
>
> 因此：
> - 任何 `time-to-tiny-live`、`shadow admission`、`paper -> tiny-live bridge`、`deployment-first` 的旧措辞，默认只保留历史参考价值；
> - 当前 bot2 / bot3 不再围绕这些目标分配主资源；
> - 若未来需要重启，再单独开新规则，不复用这里的旧排班口径。

### 当前接力棒（2026-03-15 02:20）

> 这一小段是给 bot3 / 人工都能直接认领的**结果导向 Top 3**。目标不是继续补漂亮结论，而是把最接近部署的问题压成明确 verdict。

1. [x] **EMA：把 final survivor map 继续压成 `paper-trading candidate spec`**
   - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q23`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_candidate_spec.csv`。
   - 当前口径：`创业板ETF 1d` = `paper_now_primary`；`美股/crypto 1d+1wk` 与 `贵州茅台 1d+1wk` = `paper_now_secondary`；`沪深300ETF 1d` = `shadow_only`；`60m crypto` + `A股 weekly frontier` = `exclude`。

2. [x] **breakout：把 `raw + avoid_fluctuating + pair-conditioned sizing` 压成更硬的 admission verdict**
   - 已完成：`reports/site/factors/support_breakout_v0_h24/report.html` 已新增显式 `admission verdict` 段，并同步刷新 `reports/site/factors/alpha_closure_board/report.html`。
   - 当前口径：这条线已进入 `shadow-admission queue`，但正式 verdict 仍是 `one_more_gate`，不是 `shadow paper now`。
   - 最关键缺口已明确：主缺口不是组合层资金曲线可信度，而是默认 `ETH+SOL pair-conditioned halfsize` 的 `late-segment / pure-test transferability`；`down` 环境尾部是第二风险。
   - 最新补充（2026-03-15）：默认 pair-conditioned sizing 当前受影响约 `44` 个小时，其中 `up / flat / down+flat` 约为 `28 / 14 / 2`，pure `down` 仍是 `0`。这说明它现在主要修到的是后段 `up/flat` pocket，还没真正碰到 `down` tail，所以 breakout 线仍应停在 `shadow-admission queue / one_more_gate`，下一刀优先继续补 `down` tail honesty 或更长 forward transferability。
  - 最新补充（2026-03-15 05:45 UTC）：已把 late-segment honesty 再压成从首个触发时点开始的 non-overlap `5-day` forward blocks。当前结果不再是“active windows 里 3/3 都更好”这么乐观，而是更诚实的 `3/4` blocks 改善、`1/4` block 约回吐 `-0.56pp`；因此 breakout 默认 sizing candidate 现在可以写成 `usable but not monotonic`，仍需再补 `down tail / longer forward` 才能尝试升格。
  - 最新补充（2026-03-15 05:59 UTC）：若把同一段 active period 再压成 non-overlap `10-day` forward blocks，当前有动作的 `2/2` 个 block 仍都优于 gate-only（约 `+0.53pp`、`+3.22pp`）。这说明一般性的 late-segment transferability 焦虑在下降；当前更像还卡在 `pure-test / down-tail honesty`，所以 breakout 线虽然更接近 shadow admission，但仍应停在 `one_more_gate`。
  - 最新补充（2026-03-15 06:05 UTC）：若把默认 `ETH+SOL pair-conditioned halfsize` 再收紧成 strict pure-test tail——只看从首个 pure `test` 触发（`2026-03-06 00:00 UTC`）到样本末尾——当前 gate-only 累计约 `-1.02%`，halfsize 约 `-0.25%`，delta 约 `+0.77pp`。这说明 pure-test 方向暂时没翻负，但这也只是一段约 `30` 小时的小尾巴；再结合 `pure down = 0`，breakout 线仍应继续停在 `one_more_gate`。
  - 最新补充（2026-03-15 06:18 UTC）：已把默认 sizing 的 `down-tail coverage gap` 单独压成审计口径：在同一套 gate-only `20bps hourly path` 下，`down` 段约有 `100` 个活跃小时、累计约 `-1.52%`，但默认 `ETH+SOL pair-conditioned halfsize` 对 pure `down` 的覆盖仍是 `0/100`（`0%`）。这说明当前 blocker 已可写成 deployment hard gap，而不是泛泛“担心 down-tail”；因此 verdict 仍是 `one_more_gate`。
  - 最新补充（2026-03-15 06:30 UTC）：已在不改动默认 `pair-conditioned` 主候选的前提下，补了一刀最小 `down+flat mixed-tail` protective gate（只对 active hours 中 `regime_mix = down + flat` 再做 `0.5x`）：overall hourly path 约从 `19.90%` 抬到 `20.88%`，max drawdown 约从 `-9.04%` 收窄到 `-8.53%`；strict pure-test mixed tail（约 `25` 小时）累计约从 `-0.50%` 收窄到 `-0.25%`（约 `+0.26pp`）。这说明“下一道 gate”可以先做 very-small protective honesty，而不必立刻回到泛化新变体；但该证据仍集中在单段 mixed tail，尚不足以解除 `one_more_gate`。
  - 最新补充（2026-03-15 06:59 UTC）：也已反向做了一个 blunt `pure down -> 0.5x` sanity check：若在默认 `ETH+SOL pair-conditioned halfsize` 上，对所有 pure `down` active hours 机械再砍半，max drawdown 虽会从约 `-9.04%` 收窄到约 `-7.96%`，但 overall hourly path 反而会从约 `19.90%` 回落到约 `19.48%`；而且这刀虽然打到约 `63` 个 pure `down` 小时，却仍没有碰到当前 strict pure-test tail（那段 tail 的 pure `down` 仍是 `0`）。这说明当前 hard gap 不能被误读成“pure down 一律半仓”的现成补丁；下一道 gate 更像 `down+flat mixed-tail / shadow honesty`，不是 blunt pure-down overlay。
  - [x] 最新补充（2026-03-15 08:02 UTC）：已把这刀 `down+flat mixed-tail protective gate` 再压成相对默认 `ETH+SOL pair halfsize` 的 non-overlap forward honesty。当前 active `5-day` blocks 约 `1/2` 改善、`1/2` 回吐（约 `+0.55pp / -0.39pp`），`10-day` blocks 也约 `1/2` 改善、`1/2` 回吐（约 `+0.57pp / -0.40pp`）。这说明 mixed-tail 这刀虽然 overall first-pass 仍正，但一进更前瞻口径就已经是 `split verdict`；更诚实的位置应收紧成 `shadow-only / promising but mixed gate candidate`，仍不足以解除 `one_more_gate`。
  - [x] 最新补充（2026-03-15 08:08 UTC）：已把 `gate-only baseline / default pair halfsize / down+flat mixed-tail overlay / blunt pure-down overlay` 压成一张 `conditional policy admission queue`，并同步落到 breakout 主报告与 closure board。当前更明确的 deployment-facing 排位是：`default pair halfsize = keep / default candidate`；`mixed-tail overlay = shadow-only mixed gate`；`blunt pure-down overlay = reject blunt patch`。这让 breakout 线下一轮是否继续推进的答案更直接：可以继续，但默认只沿 `pair halfsize` 主候选推进，mixed-tail 只保留为附加 gate 观察项。
  - [x] 最新补充（2026-03-15 08:17 UTC）：已继续沿 `down+flat mixed-tail` 补一层更前瞻的 rolling shadow honesty：相对默认 `ETH+SOL pair halfsize`，按 `10-day window / 5-day step` 的 walk-forward 口径，当前真正触发 overlay 的 active windows 约 `3/3` 都仍优于基线（累计约 `+0.03pp ~ +0.57pp`，其中 `2/3` 还伴随更浅回撤）。这说明 mixed-tail 这刀已经不只是单格 lucky pocket；但更克制的 non-overlap `5d/10d` forward blocks 仍是 `1/2` 正、`1/2` 负，所以它更像 `shadow honesty improved, but still shadow-only mixed gate`，还不足以解除 breakout 的 `one_more_gate`。
  - [x] 最新补充（2026-03-15 08:31 UTC）：已把 mixed-tail overlay 的 non-overlap forward blocks 再拆成 `target-pocket conditional honesty`。结果显示：这不只是“整体 path 被非目标小时稀释”的假象——active `5-day` blocks 里，target mixed-tail pocket 自己也是 `1/2` 改善、`1/2` 转弱；最弱那格（约 `2026-03-04 -> 2026-03-09`）条件累计约从 `+0.77%` 回落到 `+0.39%`（约 `-0.38pp`）。这说明 mixed-tail 目前还不能诚实地写成“target pocket 已稳定受益”的 conditional policy，因此仍只能停在 `shadow-only mixed gate`，breakout 正式 verdict 继续维持 `one_more_gate`。
  - [x] 最新补充（2026-03-15 08:53 UTC）：已把默认 `ETH+SOL pair halfsize` 再翻成更接近 shadow review 的累计 checkpoint 口径：从首个触发日起算，`5/10/15/20` 天 review 当前是 `4/4` 都仍优于 gate-only（约 `+1.04pp / +0.53pp / +3.24pp / +3.95pp`，回撤改善约 `+0.50pp / +0.50pp / +3.12pp / +3.12pp`）。这说明默认主候选虽然在 non-overlap `5-day` blocks 里并不单调，但 cumulative shadow review 目前还没有翻回 gate-only 下方；因此一般性 transferability 焦虑继续下降。不过 `down-tail coverage` 仍是 `0/100`，所以 breakout 正式 verdict 仍只能维持 `one_more_gate`。
  - [x] 最新补充（2026-03-15 09:06 UTC）：已把 `down+flat mixed-tail overlay` 也翻成从首个触发日起算的 cumulative shadow review checkpoints。当前相对默认 `ETH+SOL pair halfsize` 的 `5/10/15/20` 天 checkpoint 约 `4/4` 仍为正（约 `+0.55pp / +0.57pp / +0.59pp / +0.19pp`，回撤改善约 `+0.51pp / +0.51pp / +0.51pp / +0.49pp`）。这说明 mixed-tail 这刀不是“前瞻一看就塌”的假 gate，但到 `20-day` checkpoint 的 edge 已收窄到 very thin；再结合前面 `5d/10d` non-overlap blocks 与 target-pocket conditional honesty 仍是 split verdict，它更诚实的位置仍是 `shadow-only mixed gate`，还不能替代默认 pair candidate。
  - [x] 最新补充（2026-03-15 09:20 UTC）：已把 mixed-tail overlay 再压成 strict pure-test mixed tail 内部的 `6/12/18/24h` cumulative checkpoints（相对默认 `ETH+SOL pair halfsize`）。当前 `4/4` checkpoints 仍为正，但 delta 已从约 `+0.41pp`（`6h`）快速收窄到约 `+0.08pp`（`24h`），说明这刀不是靠单个终点 luck 才勉强为正，但它在 pure-test tail 里的 protective edge 也没有稳定扩张，更像“方向没塌、但很薄”的 `shadow-only mixed gate`，仍不足以升格成 admission clearance。

3. [x] **项目级：在 closure / TODO 入口给出一版统一 `paper trading admission verdict`**
   - 已完成：`reports/site/factors/alpha_closure_board/report.html` 已改成显式 `paper admission` 口径，并在总览表中把三条线分成：`EMA = closest to paper`、`breakout = needs one more gate`、`Fibonacci = park / archive`。
   - 这样当前入口页已经能直接回答“下一轮最该继续推进谁、谁只该 shadow、谁该 park”。

4. [x] **项目级：在 closure / plans 入口补一张从现在到 `paper trading / 小资金实盘` 的 deployment 路线图**
   - 已完成：`alpha_closure_board` 已新增显式 deployment ladder 区块，明确 `Step 1~5`（收口 -> admission gate -> operating spec -> paper/shadow -> small-cap live），并写清当前三条线分别处在什么位置。
   - 已同步：`docs/TODO.md` 也新增固定 deployment 路线图与“当前距离判断”，避免网页入口和任务清单之间口径漂移。

5. [x] **EMA：把 `candidate spec` 再压成 `paper-trading operating spec / guardrails`**
   - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q24`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_operating_spec.csv`。
   - 当前口径：`创业板ETF 1d` 必须单独记账做 `primary pilot`；`美股/crypto/贵州茅台` 的 `1d+1wk` 只能作为分 market × freq 的 `secondary backstop batch`；`沪深300ETF 1d` 只保留 `shadow watch`；`60m crypto + A股 weekly frontier` 维持 `hard exclude`，除非后续出现新的 overturn evidence。

6. [x] **EMA：把 `沪深300ETF 1d` 的 mixed/watch 状态压成 `shadow-promotion scorecard`**
   - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q25`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_shadow_promotion_scorecard.csv`。
   - 当前口径：`创业板ETF 1d` 在这套 A股 daily promotion gate 上约 `5/5` 命中，继续作为 `primary pilot`；`沪深300ETF 1d` 约 `3/5`，虽然 recent holdout 转强，但仍只应保留 `shadow watch`，不宜现在升格进正式 paper batch。

7. [x] **EMA：把 `candidate spec / operating spec / shadow scorecard` 再压成 `paper-trading monitoring board`**
   - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q26`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_monitoring_board.csv`。
   - 当前口径：`创业板ETF 1d` = `active_primary`，`美股/crypto/贵州茅台 1d+1wk` = `active_secondary_backstop`，`沪深300ETF 1d` = `shadow_watch`，`A股 weekly + crypto 60m` = `exclude_stoplist`；这样 EMA 线现在已不只知道“谁能进 paper”，也知道“平时该盯哪几列、何时升降级”。

8. [x] **EMA：把 `沪深300ETF 1d` 的 shadow 状态再压成 `recent-forward honesty audit`**
   - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q27`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_ashare_daily_recent_forward_audit.csv`。
   - 当前口径：若只看最近 `2` 段真实 forward holdout（`2024-03-12 -> 2026-03-12`），`沪深300ETF 1d` 的 EMA 累计 net20 已转正（约 `+14.26%`），但同期 PSAR 约 `+18.71%`，EMA 只在 `1/2` 段跑赢 PSAR，且最弱那段仅约 `+0.26%`；因此它现在可以写成 `recent-forward positive`，但还不能写成 `promotion honesty passed`，更诚实的位置仍是 `positive_but_not_promotable / stay shadow`。

### Deployment-facing 剩余硬门槛（2026-03-15）

- [x] **EMA：把 `candidate spec / operating spec / monitoring board` 真正接成 `paper-trading runbook`**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q28`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_runbook.csv`。
  - 当前口径：runbook 已明确 primary / secondary / shadow / stoplist 各自的数据源、刷新频率、记账口径、promote-demote / kill-switch / rollback 规则；其中 `active_secondary_backstop` 现在也被写死为：只要任一单 pocket 连续转红或被更严格 honesty 打回 `mixed/watch`，就降回 `shadow`，不允许继续拿同批别的 pocket 稀释。
- [x] **EMA：把 `runbook` 再压成 `day-0 kickoff checklist / ledger template`**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q29`，并落地 artifacts `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_kickoff_checklist.csv`、`reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_ledger_template.csv`。
  - 当前口径：现在不只知道“该按什么规则跑”，也知道 paper/shadow 第一天该先冻结哪些 scope、如何按 `market × freq` 分账、哪些字段（`monitor_status / review_action / data_health`）必须落表，避免 runbook 继续停留在口头层。
- [x] **EMA：把 `ledger template` 再压成 `day-0 launch seed rows`**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q30`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_day0_seed_rows.csv`。
  - 当前口径：day-0 不是抽象“开始记账”，而是先固定建好 `11` 条 seed rows：`primary = 1`、`secondary = 6`、`shadow = 1`、`stoplist = 3`；其中 `secondary` 必须按 `market × freq` 拆开，不允许混成一条“secondary 总曲线”。
- [x] **EMA：把 `day-0 launch seed rows` 再压成 `first weekly review scorecard / red-yellow-green protocol`**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q31`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_week_review_scorecard.csv`。
  - 当前口径：首个 weekly review 不再只是“看一眼曲线”，而是按 scope 预先写死 `green / yellow / red -> keep / demote / stop / rollback`。其中 `创业板ETF 1d` 若首周转 red 就直接降回 `shadow`；secondary 任一 pocket 若转 red 只降该 pocket，不再靠整批结果遮盖；`沪深300ETF 1d` 即便首周顺利也默认仍 `stay shadow`；stoplist 若误混回账本则立即回滚。
- [x] **EMA：把 `active_secondary_backstop` 压成可执行 `recheck queue`（避免整批口头维持）**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q32`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_secondary_backstop_recheck_queue.csv`。
  - 当前口径：secondary 不再按“美股/crypto/茅台三组都还行”整批叙事，而是按 pocket 排队复核：先看最薄 buffer 的 front queue；任一 pocket 被更严格 honesty 打回 `mixed/watch`，就按 runbook 直接从 `active_secondary_backstop` 降回 `shadow`，不允许继续靠同批别的 pocket 稀释。
- [x] **EMA：按 `day-0 launch seed rows` 真正启动首个 `0` 真资金 shadow / paper ledger snapshot（不要再继续新增近义 spec 页）**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q33`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_day0_snapshot.csv`。
  - 当前口径：固定的 `11` 条 day-0 rows 已按同一时刻写进首份 snapshot，并分别带上 `paper_status / monitor_status / review_action / data_health`；其中 `创业板ETF 1d` 已明确记成 `start_primary_paper`，front-queue secondary 会在 day-0 就落成 `kickoff_yellow_front_queue` 等待优先复核，`沪深300ETF 1d` 继续只记 `stay_shadow_until_promotion_gate`，stoplist 继续 `keep_excluded`。
- [x] **EMA：把 `day-0 snapshot` 再压成 `first-refresh queue`，明确首刷顺序与 demote / rollback 动作**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q34`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_refresh_queue.csv`。
  - 当前口径：`day-0 snapshot` 之后不再只写“下一步做真实 refresh / week-1 review”，而是把同一张账本的首刷顺序写死：默认先做 `创业板ETF 1d / A股-1d` 的 primary 首刷，再轮到 front-queue secondary（当前前两格是 `美股 1d+1wk（SPY/QQQ/AAPL） / 美股-1d` 与 `沪深300ETF 1d / A股-1d` 的 shadow refresh-only lane），stoplist 则统一保持 `audit-only`；任一 secondary pocket 若首刷后转弱，直接按 queue 写明的 `if_fail_then_action` 降回 `shadow`，不再靠整批叙事遮盖。
- [x] **EMA：沿 `first-refresh queue` 落下首个真实 refresh / week-1 delta 记录（不要再继续做近义 verdict sync）**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q35`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_first_refresh_delta.csv`。
  - 当前口径：已沿同一张账本把 top-3 lanes（`创业板ETF 1d / A股-1d`、`美股 1d+1wk / 美股-1d`、`沪深300ETF 1d / A股-1d`）落成首份真实 refresh delta。day-0 的 `flat_waiting_first_signal` 现已被真实状态替换：`创业板ETF 1d` 当前 `EMA BUY` 且已有 open long；front-queue 美股日频当前为 `SELL/flat` 并继续保留 `stricter front recheck`；`沪深300ETF 1d` 当前仍 `SELL/flat`，继续 `stay_shadow_until_promotion_gate`。
  - 执行价值：这一步把 EMA 从“queue 已排好”推进到“账本已出现首笔真实状态变化”，Jerry 可直接据此判断下一轮应继续跑 market-close refresh / week-1 review，而不是再补近义 verdict sync。
- [x] **EMA：把 top-3 首刷扩到全部 active `1d` lanes 的 daily refresh snapshot（看真实数据源与账位状态）**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q35b`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_daily_refresh_snapshot.csv`。
  - 当前口径：这轮不再补近义 board，而是把 `创业板ETF / 美股日频 / crypto 日频 / 茅台日频 / 沪深300ETF 日频` 同一天写进一张 refresh snapshot，直接记录 `live vs cache fallback`、`long_open vs flat` 与 `monitor/review` 动作；这样 Jerry 可以直接看清“今天这条线是否真的在按 runbook 续跑”，而不是只看 top-3 局部状态。
- [x] **EMA：先修复 active `1d` lanes 的 refresh 数据连续性（优先 `Crypto-1d` 与 `贵州茅台-1d`），不要在 `data unavailable` 还没清零前继续补近义 refresh 页面**。
  - 已完成：`scripts/build_ema_psar_raw_alpha_report.py` 已把 `Crypto-1d` refresh 源切到 `Binance spot klines`、把 `贵州茅台-1d` refresh 源切到 `stooq 600519.cn`，并同步刷新 `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_daily_refresh_snapshot.csv`。
  - 当前口径：active `1d` lanes 的 `refresh_data_unavailable` 红灯已清零；当前约为 `live = 3`、`cache fallback = 2`、`data unavailable = 0`。这说明 EMA 从“closest to paper”往连续 shadow/paper 续跑的最显性运营阻塞已先解除；下一步若继续推进，更该盯真实 refresh 续写与 fallback 依赖，而不是再补近义 refresh 页面。
- [x] **EMA：把 active `1d` lanes 的 `live / fallback` 依赖压成 `refresh dependency audit`（明确下一刀先修哪里）**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q35c`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_refresh_dependency_audit.csv`。
  - 当前口径：active `1d` lanes 当前虽已 `data unavailable = 0`，但仍有约 `2/5` 条依赖 cache fallback，而且其中就包括唯一 primary pilot `创业板ETF 1d`；因此 EMA 当前更诚实的 deployment-facing 读法不是“已经完全 paper-ready”，而是 `can-run / can-ledger, but still primary source-risk`。下一刀若继续 EMA，默认更该先压 A股日频 fallback 依赖，而不是继续补近义 runbook / refresh 页面。
- [x] **EMA：把 `创业板ETF 1d / 沪深300ETF 1d` 的 A股日频 refresh 源从 frontier cache fallback 升成可重复 `Eastmoney live`**。
  - 已完成：`scripts/build_ema_psar_raw_alpha_report.py` 已新增 `Eastmoney daily loader`，并把 primary / shadow A股日频 lane 的 refresh source 切到 `159915.SZ -> 0.159915`、`510300.SS -> 1.510300`。
  - 当前口径：`ema_paper_trading_daily_refresh_snapshot.csv` 与 `ema_paper_trading_refresh_dependency_audit.csv` 现在已把两条 A股日频 lane 刷成 `eastmoney_live`；active `1d` lanes 当前约为 `live = 5`、`cache fallback = 0`、`data unavailable = 0`。这说明 EMA 当前默认不再卡在 primary source-risk，下一刀更该回到真实 `market-close refresh / week-1 review / front-queue honesty`，而不是继续修同类 source 说明。
- [x] **EMA：把 `创业板ETF 1d` 的 `PSAR overlay` 候选压成 narrow `shadow protective protocol`（只做 sidecar，不改默认持有）**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q35g`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_chinext_daily_psar_shadow_protocol.csv`。
  - 当前口径：`创业板ETF 1d` 虽有约 `75%` strict holdout 改善、median net20 delta 约 `+2.00pp`，但 `A股 daily overall` 仍只有约 `50%` 改善、median delta 约 `-0.38pp`；因此更诚实的运行方式是 `EMA-only primary + PSAR sidecar shadow`。新 protocol 已把 `scope freeze / market-close sidecar refresh / weekly relative review / promotion-or-rollback gate` 写死：只允许沿同一次 A股收盘 refresh 记录 overlay comparator，不允许在没有新 completed bar 时补伪 forward，也不允许把这格 pocket 的局部改善偷渡成 family-wide default overlay。
- [x] **EMA：把 `on-clock waiting` 压成 next-close action queue（到点可执行，不靠口头记忆）**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q35h`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_next_close_action_queue.csv`。
  - 当前口径：这张队列把 `active_primary / active_secondary_backstop / shadow_watch` 按下一次预计收盘时点排成同一张执行顺序表，并为每条 lane 明确 `action_when_due / if_not_due / if_blocked`。它不伪造新 forward 结果，但能减少下一次真实 close 到来时的执行漂移，直接服务于未完成主线（line-299：连续落下 market-close refresh / week-1 review）。
- [x] **EMA：把 next-close queue 再压成 `due-now / overdue` 守门快照（close 过后别继续误写成 waiting）**。
  - 已完成：`reports/site/factors/ema_psar_raw_alpha/report.html` 新增 `Q35i`，并落地 artifact `reports/artifacts/ema_psar_raw_alpha/ema_paper_trading_due_guardrail_snapshot.csv`。
  - 当前口径：这张快照不重复回答“到点后先做什么”，而是专门把 `waiting_not_due / due_soon / due_now_refresh_window / overdue_refresh_check` 分开。当前最靠前的 lane 已可被明确标成距下一次 close 还有多久；一旦 future run 落入 `due_now` 或 `overdue`，默认就该先写 ledger / 查 blocked，而不是继续补近义 queue / refresh wording。
- [ ] **EMA：沿同一张 live ledger 连续落下下一轮 `market-close refresh / week-1 review` 结果（不要在 source-risk 已清零后继续补近义 source 文案）**。
  - 目标：在现有 `day-0 snapshot -> first-refresh delta -> all active 1d daily snapshot` 基础上，继续给出至少一轮新的真实续写，重点回答：`创业板ETF 1d` primary 是否继续守住、front-queue secondary 是否需要 `keep / stricter recheck / demote`、以及 week-1 review 是否出现首个 `yellow/red` verdict。
  - 当前理由：EMA 当前 active `1d` lanes 已约 `live = 5`、`cache fallback = 0`、`data unavailable = 0`，最显性的运行 blocker 已先解除；因此下一步最有杠杆的动作，不再是继续修 source 或补 refresh 说明页，而是把这张账本继续写成真正的前瞻 review 记录。
  - 最新补充（2026-03-15 17:07 UTC）：已新增 `ema_paper_trading_refresh_clock_audit.csv` 并同步挂到 EMA 主报告。当前 active `1d` lanes 不是 stale：它们约 `5/5` 都还处在 `on-clock waiting next close`，首个 `week-1 review` 最早约在 `2026-03-22 17:00 UTC`。这说明 source-risk 清零后，当前更诚实的状态不是“还缺一页 source 文案”，而是**正在按计划等下一次真实 completed bar**；因此本任务仍未完成，但下一刀该等真 `market-close refresh / week-1 review`，不该伪造不存在的新 forward 结果。
  - 最新补充（2026-03-15 18:55 UTC）：`closure sync / overlay deployment matrix / 创业板ETF sidecar protocol / next-close action queue` 现已齐备；在下一根真实 completed daily bar 到来前，默认**不要**继续新增近义 `overlay / source / queue / closure-copy` 页面。这个等待窗口里的有效动作只剩两类：
    1. 到点后按 `ema_paper_trading_next_close_action_queue.csv` 真落下一轮 refresh / review；
    2. 若执行时再次出现脚本/编辑层故障（例如 exact-text mismatch），只修执行阻塞本身，不再扩写新的部署说明页。
  - 最新补充（2026-03-15 20:00 UTC）：已新增 `scripts/run_ema_paper_trading_guarded_refresh.py` 作为**守门执行入口**。它默认先重跑 `build_ema_psar_raw_alpha_report.py`，再只输出 `due_now / overdue / due_soon` lanes，并可用 `--require-due` 在 close 前直接拒绝伪 refresh。这样下一次真实 close 到来时，默认先跑这一个入口做守门与动作提示，而不是再手动翻 queue / report 或继续新增近义页面。
  - 最新补充（2026-03-15 20:10 UTC）：已用 `--require-due` 真跑一遍守门入口并完成 smoke test。结果显示当前仍**没有** `due_now / overdue` lane，最靠前的是 `Crypto 1d+1wk`，距下一次 UTC 日线 close 约 `3.8` 小时；`创业板ETF 1d / 贵州茅台 1d+1wk / 沪深300ETF 1d` 约 `10.8` 小时后到点，美股日频约 `23.8` 小时后到点。也就是说，EMA 这条线当前最诚实的动作仍是按 guardrail 等待真实 completed bar，而不是把“还没到点”误写成新的 refresh 结果；但等到 `Crypto 1d` close 到来后，下一轮就应优先沿同一张 ledger 真续写。
  - [x] 最新补充（2026-03-15 21:01 UTC）：已把覆盖式 `ema_paper_trading_daily_refresh_snapshot.csv` 接成 append-only `ema_paper_trading_refresh_history.csv`。`scripts/run_ema_paper_trading_guarded_refresh.py` 现在会按 `deployment_scope × market_freq_book × latest_completed_bar_utc` 去重追加真实 completed-bar rows；当前已先把现有 `5` 条 active `1d` lane 种子写入 history。这样下一次真实 close 到来后，EMA 线不再只有“最新快照覆盖”，而能沿同一份 history ledger 连续累计 refresh / review 轨迹。这仍不等于 line-305 已完成，但已补上运行连续性的最小 execution blocker。
  - [x] 最新补充（2026-03-15 21:29 UTC）：已把 `scripts/run_ema_paper_trading_guarded_refresh.py` 再压成 `fast-precheck` 守门入口：当 `--require-due` 打开、且现有 `due_guardrail_snapshot` 显示所有 `next_expected_close_utc` 仍在未来时，脚本现在会直接跳过本轮 full rebuild，并动态回显最靠前 lane 距离到点还有多久。这样高频巡检就不会在还没到真实 close 前反复重建整份 EMA 主报告；真正到点后才回到完整 rebuild + ledger append 路径。这一步没有伪造新的 refresh 结果，但补掉了 waiting window 里的一个真实 execution friction。
  - 最新补充（2026-03-15 21:37 UTC）：`refresh_history / homepage deployment watch / guarded fast-precheck` 这三块 execution 垫片现已全部落地。在下一根真实 completed bar 到来前，默认不要再对 `scripts/run_ema_paper_trading_guarded_refresh.py`、`scripts/build_site_index.py` 或对应首页/计划镜像重复做同一类 patch；若当前状态没有新的 `due_now / overdue` lane，且也没有新的执行阻塞（脚本异常 / data loader 故障），本线默认应返回 `NO_PROGRESS`，而不是再次尝试“内容已相同”的重复 edit。
  - 最新补充（2026-03-15 22:46 UTC）：已把已有的 `ema_paper_trading_refresh_history.csv` 正式挂回 `EMA / PSAR Raw Alpha Focus Report`，并新增 `ema_paper_trading_refresh_history_audit.csv`。当前这一步没有伪造新的 refresh 结果，而是把“覆盖式 latest snapshot”与“append-only ledger 是否真的在连续续写”拆开：现在可以直接看到各 lane 仍大多只有 `seed_only_history` 的 1 条记录，所以 line-305 仍未完成；但下一次真实 close 到来后，应优先检查 `rows_recorded` 是否从 `1` 增到 `2+`，而不是只盯新的覆盖式 snapshot。
  - [x] 最新补充（2026-03-16 00:01 UTC）：已在 close 到点后真跑 `python3 scripts/run_ema_paper_trading_guarded_refresh.py`，`ema_paper_trading_refresh_history.csv` 追加 `1` 条新 completed-bar row（累计 `6` 条），新增键为 `Crypto 1d+1wk（BTC/ETH/SOL） | Crypto-1d | 2026-03-15 00:00 UTC`。这说明 line-305 已从“全是 seed-only”进入首个真实连续续写；但 `创业板ETF / 贵州茅台 / 沪深300ETF` 当前仍是 `waiting_not_due`（约 `7h` 后到点），week-1 review 也仍未到期，所以该主线暂不勾完成，下一刀默认在 A股 next close 后继续沿同一 ledger 追加。
- [x] **breakout：已把 `raw + avoid_fluctuating + ETH+SOL pair halfsize` 主候选的当前样本最后一道 gate 压成 freeze verdict**。
  - 已完成：`docs/TODO.md`、`support_breakout_v0_h24` 主报告与 `alpha_closure_board` 现已统一写成 `same-sample admission freeze`；当前样本里的 retrospective admission slicing 已基本榨干。
  - `mixed-tail overlay` 只保留 `shadow-only` 观察项，不再与默认主候选并列消耗主资源。
  - [x] 最新补充（2026-03-15 09:40 UTC）：已把默认 `ETH+SOL pair halfsize` 的 strict pure-test tail 再切成“晚段 mixed-tail pocket 进来前”的 `60/72h` checkpoints。结果显示：在最后两小时 `down+flat mixed tail` 进来前，default sizing 相对 gate-only 的累计改善其实都只有约 `+0.08pp`、回撤改善近乎 `0pp`；整段 strict tail 的约 `+0.77pp` 改善里，约 `+0.69pp` 是最后那两个 mixed-tail 小时才补上来的。这说明 default pair candidate 在更早的 pure-test tail 里还只是“没翻负”，并没有给出厚实的 pure-test honesty，因此 breakout 正式 verdict 继续维持 `one_more_gate`，且 blocker 仍是 `pure-test / down-tail honesty`。
  - [x] 最新补充（2026-03-15 09:57 UTC）：已把默认 `ETH+SOL pair halfsize` 的 `44` 个受影响小时按真实时间顺序压成 episode decomposition。结果显示它当前并不是一整段连续的 pure-test honesty，而是 `train × flat (14h, 约 +1.01pp)`、`test+validate × up (25h, 约 +1.92pp)`、`test × up (3h, 约 +0.08pp)`、`test × down+flat (2h, 约 +0.68pp)` 这四段拼出来的。更诚实的 deployment-facing 读法因此更清楚了：default pair candidate 的大头仍来自 overlap / earlier episodes；真正 pure-test 前半段还只有 very thin edge，最后两小时 mixed-tail 才补上更多增量。所以 breakout 正式 verdict 继续维持 `one_more_gate`，blocker 仍是 `pure-test / down-tail honesty`，不是 wording 问题。
  - [x] 最新补充（2026-03-15 10:02 UTC）：已把 `pair + down+flat mixed-tail overlay` 的 `37` 个受影响小时按真实时间顺序压成 episode decomposition，并落到 breakout 主报告。结果显示这刀目前只会塌成 `3` 段：前两段仍是 `train × down+flat`，合计条件改善约 `+0.55pp`（约占总 conditional delta 的 `68%`）；真正 pure `test × down+flat` 只有最后一段 `25h`、条件改善约 `+0.26pp`。这让 mixed-tail 的 deployment-facing 读法更清楚：它不是完全没 forward 方向，但目前仍主要靠训练段 carry + 单段 test pocket 支撑，因此继续只配 `shadow-only mixed gate`，还不足以补成 admission clearance。
  - [x] 最新补充（2026-03-15 10:20 UTC）：已把 breakout 当前 admission 证据压成一张 `avoid_fluctuating_admission_gate_checklist_20bps.csv`，并落到 breakout 主报告。当前 deployment-facing blocker 已经收敛成一句话：`组合层 hourly path` 与更长 `5d/10d` forward honesty 已不再是主 blocker，但 `pure-test tail` 仍偏薄（strict tail 约 `+0.77pp`，而晚段 mixed-tail 进来前的 `72h` 其实只有约 `+0.08pp`），且 `down-tail coverage` 仍是 `0/100`。因此 breakout 正式 verdict 继续维持 `one_more_gate`；mixed-tail 只配 `shadow-only`，blunt pure-down patch 可继续视为 reject sanity check。
  - [x] 最新补充（2026-03-15 10:31 UTC）：已把 `pair + down+flat mixed-tail overlay` 在 strict pure-test tail 里进一步压成更前瞻的 non-overlap `6h` blocks（artifact：`avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_pure_test_tail_forward_blocks_6h_20bps.csv`）。结果约为 `2/4` 正、`2/4` 负：最强 block 约 `+0.41pp`，但最弱 block 约 `-0.29pp`，且另有一格约 `-0.14pp`。这说明 mixed-tail 不是纯 lucky patch，但也还不是“每段都稳定更优”的 conditional policy；因此它继续只配 `shadow-only mixed gate`，不能改写 breakout 的 `one_more_gate`。
  - [x] 最新补充（2026-03-15 10:43 UTC）：已把 breakout 当前 `one_more_gate` 进一步压成执行型 `gate clearance protocol`（artifact：`avoid_fluctuating_gate_clearance_protocol_20bps.csv`），并同步落到 `support_breakout_v0_h24` 主报告。当前 deployment-facing 读法更明确了：`default pair halfsize` 只有在后续更前瞻的 shadow / holdout 里**真正命中 pure down 小时**、且同一段 `pure-test / down-tail` 仍不翻负时，才有资格从 `one_more_gate` 往 `shadow paper now` 再走一步；否则只要 `pure down coverage` 继续停在 `0/100`、strict tail 仍只像当前约 `+0.77pp on 5/30h` 这种 very-thin edge，正式 verdict 就继续维持 `one_more_gate`。同时 `mixed-tail overlay` 也被正式写死为：只有在 `5d/10d` non-overlap forward blocks 与 strict-tail `6h` blocks 不再给出 split verdict 时，才配继续升级；在那之前继续只配 `shadow-only mixed gate`。
  - [x] 最新补充（2026-03-15 10:50 UTC）：已把默认 `ETH+SOL pair halfsize` 的 strict pure-test tail 也压成 non-overlap `6h` active-block 审计（artifact：`avoid_fluctuating_eth_sol_pair_halfsize_pure_test_tail_forward_blocks_6h_20bps.csv`），并同步落到 breakout 主报告。结果显示当前真正满足最小 active-block 门槛的只有 `1/5` 段，而且就是最后那格 `test × down+flat` mixed-tail pocket，delta 约 `+0.68pp`；前面那 `3` 个 `test × up` 小时甚至连一个可独立成形的 active block 都凑不出来。更诚实的 deployment-facing 读法因此进一步收紧成：default pair candidate 还没有给出“多段独立可复用”的 pure-test honesty，blocker 仍是 `pure-test / down-tail honesty`，breakout 正式 verdict 继续维持 `one_more_gate`。
  - [x] 最新补充（2026-03-15 11:03 UTC）：已新增 `pre-down bridge audit`（artifact：`avoid_fluctuating_eth_sol_pair_halfsize_predown_bridge_audit_20bps.csv`），专门检查默认 `ETH+SOL pair halfsize` 能不能被解释成“虽然没打到 pure down，但至少会在 pure down 前几小时提前减仓”。结果显示答案仍是否：未来 `6/12/24h` 内会滑进 pure `down` 的 bridge 小时，命中数仍是 `0/5`、`0/11`、`0/23`；其中最关键的 `12h` bridge 其实是一整段 `validate × flat` 前置滑落，自身累计约 `-3.92%`，但默认 pair 仍完全没命中。也就是说，当前缺口不只是 `down-tail coverage = 0/100`，连最接近 pure-down 的 anticipatory bridge 也没有 coverage，因此 breakout 正式 verdict 继续维持 `one_more_gate`，且不能把 default pair candidate 解释成“提前减仓式”的 down-tail protection。
  - [x] 最新补充（2026-03-15 11:31 UTC）：已新增 `future pure-down lead audit`（artifacts：`avoid_fluctuating_eth_sol_pair_halfsize_future_pure_down_lead_audit_20bps.csv`、`avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_future_pure_down_lead_audit_20bps.csv`），反过来只看 default pair / mixed-tail 自己打到的小时，检查它们离“下一段 pure down”到底还有多远。结果显示两条 policy 在未来 `24/48h` 内都仍是 `0/x` 命中：default pair 约 `0/44`、`0/44`，mixed-tail 约 `0/37`、`0/37`；即便放宽到 `72/96h`，default pair 也只到约 `13/44`、`14/44`，mixed-tail 只到约 `5/37`、`12/37`，而且这些少量 future-down-adjacent 小时依然全部来自 `train`（default = `train × flat`，mixed = `train × down+flat`），没有新的 pure-test 证据。这个结果把 breakout 当前 blocker 再收紧了一步：问题不只是 `down-risk zone` 没 coverage，而是 current policy active hours 结构上就离 pure-down 太远，所以 mixed-tail 仍不能被诚实地写成 near-down conditional gate，正式 verdict 继续维持 `one_more_gate`。
  - [x] 最新补充（2026-03-15 11:47 UTC）：已把 `down-risk zone audit` 继续沿同一条 breakout admission 主线放宽到未来 `48/72/96h`（artifacts：`avoid_fluctuating_eth_sol_pair_halfsize_downrisk_zone_audit_20bps.csv`、`avoid_fluctuating_eth_sol_pair_halfsize_downflat_overlay_downrisk_zone_audit_20bps.csv`、`avoid_fluctuating_downrisk_zone_audit_compare_20bps.csv`）。结果显示：default pair 与 mixed-tail 在 `12/24/48h` 风险区里都仍是 `0` coverage；直到 `72/96h` 才分别开始擦到少量 bridge（default 约 `13/164`、`14/177`；mixed 约 `5/164`、`12/177`），但 pure `down` coverage 仍是 `0/63`。这说明 mixed-tail 目前最多只能算“把窗口放宽到 3~4 天才会擦到一点 bridge”的远距离 shadow gate，仍不能诚实地写成 near-down protective policy；因此 breakout 正式 verdict 继续维持 `one_more_gate`，而 hard blocker 仍是 `pure-test / down-tail honesty`。
  - [x] 最新补充（2026-03-15 12:00 UTC）：已把 breakout 当前这段历史样本是否还值得继续做 retrospective admission slicing 压成 `current-sample freeze verdict`（artifact：`avoid_fluctuating_current_sample_freeze_verdict_20bps.csv`），并同步落到 breakout 主报告。结果显示：default pair 在最相关的近距离 blocker 口径里仍是 `48h down-risk zone = 0/109`、`future pure-down 48h = 0/44`，strict pure-test tail 再压成 `6h` blocks 也只剩 `1/5` 真正有动作且为正；mixed-tail 也仍是 `48h down-risk zone = 0/109`、`future pure-down 48h = 0/37`，而 strict-tail `6h` blocks 继续停在 `2/4` 正、`2/4` 负。更诚实的 deployment-facing 读法因此进一步收口成：当前样本里的 retrospective micro-slicing 已基本榨干，下一次 breakout admission 的有效推进必须来自新的 shadow / holdout 真正命中 `pure-test / down-tail`，而不是继续在同一段历史样本里补近义 board / wording；正式 verdict 继续维持 `one_more_gate`。
  - [x] 最新补充（2026-03-15 12:35 UTC）：已把 breakout 当前 `scope verdict` 压成一张更 deployment-facing 的 `up-flat biased conditional alpha` 压缩页（artifact：`avoid_fluctuating_scope_verdict_20bps.csv`），并同步补到 `support_breakout_v0_h24` 主报告与 `alpha_closure_board`。当前更硬的项目级写法已固定为：这条线仍可继续保留成 narrow `shadow-admission candidate`，但不能再被写成 near-down protective policy 或泛化 breakout-short；因为 default pair 仍是 `pure down = 0/100`、`48h down-risk zone = 0/109`、`future pure-down 48h = 0/44`，所以 same-sample micro-slicing 不会再改写 verdict，下一次有效推进必须来自新的 forward / shadow `pure-test/down-tail` honesty。
  - [x] 最新补充（2026-03-15 23:25 UTC）：已用 `.venv/bin/python scripts/build_pytrendline_event_validation_v3_report.py --refresh-data` + `.venv/bin/python scripts/build_support_breakout_v0_reports.py` 真跑一轮 fresh-refresh recheck，并把结果压成 artifact `avoid_fluctuating_refresh_recheck_20260315_20bps.csv`。当前 fresh rerun 之后，breakout 主样本尾部仍没有往后推进：`event_sample_purged.csv` 的最新 `action_timestamp` 仍停在 `2026-03-10 11:00 UTC`，default pair 的硬 blocker 也完全没动（`pure down = 0/100`、`12h pre-down bridge = 0/11`、`48h down-risk zone = 0/109`、`future pure-down 48h = 0/44`、strict pure-test `6h` active-positive blocks 仍只 `1/5`）。这说明当前不是“旧结论没刷新”，而是**用现有 data loader 真重跑后，仍没有 fresh overturn evidence**；因此 breakout 线默认继续停在 `same-sample admission freeze / one_more_gate`，下一轮不该再对这条线做同类 rerun，除非底层数据窗口或新的 post-tail 事件真的往后走。
  - [x] 最新补充（2026-03-16 00:31 UTC）：已新增轻量 `breakout rerun guard` artifact：`reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_revisit_guard_20bps.csv`，专门把“什么时候才值得再跑 heavy refresh recheck”压成执行门槛。当前 guard 读法是：上次 heavy recheck 检查到的 cache bar 为 `2026-03-13 13:00 UTC`，而本轮 guard 已观测到本地 cache 最新 bar 到 `2026-03-16 00:00 UTC`（约 `+59.0h`），因此 verdict 标成 `cache_advanced_rerun_worth_checking`，默认动作是“允许再跑一次 heavy rerun”；若后续 cache 没继续前推，则 guard 会把动作收回到 `same_sample_hold_no_rerun`，避免在同样本窗口里反复重跑。
  - [x] 最新补充（2026-03-16 02:48 UTC）：已把 breakout 守门继续压成**动态 homepage watch**：本轮先重跑 `python3 scripts/build_breakout_revisit_guard.py`，确认本地 cache 仍领先上次 heavy recheck 所见尾部，但最近一次 heavy rerun 距今仅约 `3.4h`，因此当前更诚实 verdict 已收紧为 `cache_advanced_but_recent_recheck_cooldown_hold`；随后 `scripts/build_site_index.py` 也改成按当前时间动态重算 cooldown，而不再机械照抄旧 guard 行。这样首页现在会直接显示“还在短冷却、剩余多久、默认别再重跑 breakout”，避免 Jerry 在 waiting window 里被误导成 `rerun worth checking`；在 cooldown 走完前，默认把执行重心切回 EMA 的下一次真实 market-close refresh。
- [x] **项目级：旧 `paper -> tiny-live` promotion gate 已归档**。
  - 保留原因：这些 artifact 仍可作为将来若重启 deployment 话题时的历史参考。
  - 当前统一口径：
    - `tiny-live / live-shadow / routing dry-run / parity / reopen gate / operator reconciliation` **都不是 bot2 / bot3 的当前默认目标**；
    - 它们不再构成 `Run 3 fallback`，也不再参与当前排班；
    - 现阶段只保留 `paper launch handoff`，不继续推进后续 live 相关链路。
  - 因此下方若仍看到旧 artifact 名称，应按**归档材料**理解，而不是当前待办。

#### 当前不优先（避免 bot3 再掉回低杠杆微步）
- [ ] 不再优先新增 `EMA` 线上的 `protocol / gate / cleanup / closure-copy` 小步；优先把它压成 `candidate spec / deployment scope`。
- [ ] 不再优先回头纠结 `confirm_1` 会不会抢 breakout 主线位；这件事在更正式口径下已经基本看清。
- [ ] 不再优先扩新的 breakout 变体；先把 `raw` 主原型在环境 gate 与更正式组合层上的边界压清楚。
- [ ] 不再优先给 `Fibonacci` 增加新的 hopeful follow-up；当前默认只保留 archived / optional filter 口径。

---

## 目录与项目组织原则

以后统一按下面四层组织，而不是把单个引擎当主线：

### A. Structure-Event Mainline（默认主入口）
回答：
- 我们到底在研究什么结构事件？
- 它们值不值得继续？
- 当前证据支持 `go / feature / park` 中哪个结论？

### B. Engine Labs（定义引擎实验室）
回答：
- 不同引擎是怎么定义线、突破、反弹、确认的？
- 它们能否作为 mainline 的事件来源？
- 目前各自的优点、局限、边界是什么？

当前先拆成：
- `PyTrendline`：explainability baseline
- `PyIndicators`：active-line / segment-state baseline

### C. Downstream Exploitation（只对胜出者继续）
只有在 mainline 给出正面证据时，才进入：
- feature builder
- MVP signal
- 策略回测
- 进一步 robustness / OOS / rolling

### D. Candidate Engines / Future Branches
例如：
- parallel channel
- regression channel
- 其他 support/resistance / channel / pattern 定义器

---

## A. Structure-Event Mainline（默认主入口）

目标：
- 不绑定某一个画线库；
- 先把结构事件研究本身做扎实；
- 再决定哪些引擎、哪些事件、哪些 subset 值得进入下一层。

### A0. 主线文档与决策框架

- [x] 明确项目主线应表述为 **Structure-Event Alpha Research**，而不再是“先押注 parallel channel alpha”。
- [x] 明确当前主判断：
  - 先验证结构事件是否有稳定价值；
  - 再决定它们更适合做 alpha / feature / confirmation；
  - 不再默认把某一个定义引擎当作最终主线。
- [x] 在主线文档或主页中补一个 **decision board**。
  - 已在 `Structure-Event Mainline` 页面补上最小版 decision board：
    - `breakout` → 偏 `park / weak`
    - `rebound retained subsets` → 偏 `continue / feature candidate`
    - `pytrendline source` → `unknown / need bridge`
  - `go`
  - `feature`
  - `park`
  - `unknown / need more evidence`

### A1. Unified Event Foundation（统一事件地基）

建议目标文件 / 产物：
- `docs/RESEARCH_TRENDLINE_EVENT.md`
- `scripts/build_trendline_event_foundation_report.py`
- `reports/site/factors/trendline_event_foundation/report.html`

#### A1-A. event taxonomy / schema

- [x] 在设计草案中明确 **event taxonomy（事件分层）**。
  - 已定义：touch、wick interaction、first cross / raw breach、provisional break、confirmed break、retest hold、rebound。

- [x] 在设计草案中明确 **事件与 line lifecycle 的关系**。
  - 已明确区分：line detection / line lifecycle / event detection / confirmation / execution。

- [x] 新增一个 **cross-engine unified event schema** 草案。
  - 已新增 `docs/CROSS_ENGINE_MAPPING.md`，先给出一版 schema v0：区分通用字段（`source_engine` / `event_family` / `event_subtype` / `line_side` / `event_timestamp` 等）与 engine-specific 字段（如 `duplicate_group_id` / `navigator_state`），并明确哪些概念不能硬对齐。

- [x] 新增一页或一节 **Cross-Engine Mapping**。
  - 已新增并站点镜像化 `Cross-Engine Mapping` 页面，明确说明：
    - PyIndicators 更像 first event-study source；
    - PyTrendline 更像 explainability baseline；
    - 两者应先映射到 unified event schema，再进入同一条 Mainline 比较。

#### A1-B. 条件分层（buckets）

- [x] 为 mainline 设计 **slope buckets**。
- [x] 为 mainline 设计 **quality buckets**。
- [x] 明确第一轮先收窄到 **crypto + 少量周期**，不做全市场扩展。
- [x] 在 foundation 页面中增加一个更明确的 **bucket glossary**，让读者不用翻设计文档也能直接看懂。
  - 已新增 `Bucket glossary / how to read the labels`，明确解释：
    - 当前已接入的 event buckets（confirmed_breakout / confirmed_rebound）
    - future ladder buckets（raw_breach / close_confirm / confirm1 / confirm3 / retest_hold）
    - `support / resistance`
    - `slope bucket`
    - `quality bucket`
    - `representative_only vs all_valid`
    - 以及 `gross / net / bubble_proxy` 这种外部约束切片

#### A1-C. confirmation ladder

- [x] 为 breakout 事件定义 **confirmation ladder**：
  - `raw_breach`
  - `close_confirm_same_bar`
  - `confirm1`
  - `confirm3`
  - `retest_hold`

- [x] 为 rebound 事件定义 **rebound confirmation ladder**。
- [x] 明确 `provisional break` 与 `confirmed switch` 的区分口径。
  - 当前已进一步挂回 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md`：不再只停留在 brief / notes，而是成为主线可引用的解释口径。
- [x] 把 ladder 比较真正升级成 **跨引擎可复用协议**，而不是只绑定当前单一 source。
  - 已新增 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 与站点镜像 `plans/trendline_confirmation_protocol.html`：
    - 统一 breakout / rebound 的 confirmation level 枚举
    - 规定最小必备字段
    - 规定最小比较输出表
    - 明确什么情况下才算“更强确认值得保留为默认口径”
    - 明确 `PyIndicators` 是 source #1，`PyTrendline v2` 的目标则是补齐进入该协议所缺层级
  - foundation 页现也已把它作为独立 `protocol layer` 接入 provenance / glossary，避免 confirmation 再被误读成单页实现细节

- [x] 把 `Optimal Stopping` 的 `touch_or_cross / provisional_break / confirmed_switch` 解释显式挂回 confirmation protocol。
  - 已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 新增机制解释段：明确 `raw_breach -> provisional_break`、`confirm1/confirm3 -> stronger confirmed-switch candidates`、`retest_hold -> 最接近结构性 confirmed switch`，并把 rebound ladder 也解释为“回到原结构内部并持续停留”的 retained evidence 层级。

- [x] 在 confirmation protocol 中补 `PyIndicators / PyTrendline` 的 native -> mainline 最小映射例子。
  - 已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 明确：
    - `PyIndicators breakout_hold_1 -> confirm1`，`breakout_hold_2/3/4 -> confirm3-like stronger confirmation`，`rebound_inside_0/1/2/3 -> inside_0/1/2/3plus`；
    - `PyTrendline v1 is_breakout -> raw_breach`，而 `close_confirm_same_bar / confirm1 / confirm3 / retest_hold` 仍是 v2 需要补齐的原生状态层。

- [x] 在 confirmation protocol 中补 source-to-protocol 示例行（含允许 `null` 的 v1 口径）。
  - 已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 新增 `PyIndicators confirm1` 与 `PyTrendline raw_breach` 的示例行，明确哪些字段当前可诚实落表、哪些字段应保持 `null` 而不是伪造值。

- [x] 在 confirmation protocol 中补字段分层表：`required / nullable / engine-specific`。
  - 已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 新增 `4.2 字段分层表`，明确哪些字段没有就不该进 protocol compare，哪些字段允许先保留 `null`，以及哪些字段应继续只留在 source audit / mapping 层。

- [x] 在 confirmation protocol 中补 `source onboarding checklist`。
  - 已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 新增 `4.3 source onboarding checklist (v1)`：明确新 source 进入 compare 前，应依次检查身份识别、required 字段、native->mainline 映射、nullable/engine-specific 边界，以及最小 compare 准入条件。

- [x] 在 confirmation protocol 中固定 compare-page honesty labels（v1）。
  - 已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 新增 `4.4 compare-page honesty labels (v1)`：统一 `source #1 / baseline compare source`、`raw-breach-only source`、`partial ladder coverage`、`rebound-only source`、`mechanism-backed but not full-event-universe` 这几类标签，并补了 `PyIndicators / PyTrendline v1 / Optimal Stopping` 的默认示例。

#### A1-D. event-level validation

- [x] 先定义 **event study 指标集**，而不是直接跳到完整策略净值。
- [x] 明确第一轮核心比较问题：
  - breakout vs rebound
  - raw vs confirmed
  - slope bucket differences
  - quality bucket differences
  - support vs resistance
  - representative only vs all valid
- [x] 明确第一轮目标是 **go / feature / park decision**，不是收益最大化。
- [x] 明确 event-level validation 的默认观察口径（默认模板 v1）。
  - 默认 horizon：`+1 / +3 / +6 / +12` bars
  - 若需要更直观的人类读法，可同步换算成近似时间：
    - `5m` bar：`5m / 15m / 30m / 60m`
    - `30m` bar：`30m / 90m / 180m / 360m`
    - `60m` bar：`1h / 3h / 6h / 12h`
  - 默认最小指标模板：
    - `up_ratio_after_h`
    - `mean_forward_return_h`
    - `median_forward_return_h`
    - `iqr_forward_return_h`
    - `positive_asset_ratio_h`（跨资产时）
    - `sample_count`
  - 默认要求至少同时报告：
    - 总体统计
    - `support vs resistance`
    - `slope bucket`
    - `quality bucket`

#### A1-E. foundation report artifacts

- [x] 已定义最小 artifacts 清单。
- [x] 已定义 foundation report 的最小读法。
- [x] 已有 skeleton / contract。
- [x] 已填入第一批真实统计（partial stats）。
- [x] 已列出升级到完整 ladder / full event universe 所缺的数据接口。
- [x] 把 foundation 页再补一个 **“当前证据来自哪些 source，哪些 source 还没接入”** 区块。
  - 已在 `Trendline Event Foundation Report` 增加 `Current source provenance / what is already connected`：明确列出
    - 已接入的 `PyIndicators slope audit / confirmation ladder`
    - 已接入但仍处于 bridge-v1 的 `PyTrendline validation`
    - 只提供成熟度审计的 `cross-engine source comparison`
    - 作为外部约束的 `Svogun 2022 cost/regime experiment`
    - 以及仍缺失的 `full event-universe / ladder-native source`

### A2. 当前主线证据与下一步验证

#### A2-A. subset evidence

- [x] 已完成第一轮 **slope-conditioned audit**。
- [x] 当前中间结论：
  - `breakout-long` 整体仍偏弱；
  - `rebound-long` 只在少数 subset 更像值得继续的候选；
  - 不能再把整个 PyIndicators breakout 当默认主线继续救。

- [x] 把 slope audit 的结论正式沉淀成 **mainline decision card**。
  - 已在 `Structure-Event Mainline` 页面补成最小 decision board：
    - 哪些 bucket 暂时 `continue`
    - 哪些 bucket 暂时 `park`
    - 哪些 bucket 仍然 `unknown`

#### A2-B. confirmation ladder evidence

- [x] 完成 `Trendline Confirmation Ladder Report` 的最终生成与站点接入。
  - 已生成并接入 `reports/site/factors/trendline_confirmation_ladder/report.html`；`Structure-Event Mainline` 现已把它作为第 4 页主线阅读项挂出。

- [x] 在 mainline 中明确回答：
  - 更强 confirmation 是否真的改善质量；
  - 还是只是让样本数塌缩。
  - 当前最值得复用的结论是：`breakout` 侧更强确认并没有把整体质量真正救起来；而 `rebound` 的 retained 子集（尤其 `flat + down_high`）里，最宽松的 `inside = 0/1` 反而保留了更好的 trade retention 与总体表现。

#### A2-C. next mainline task（推荐顺序）

- [x] 先补 `Cross-Engine Mapping` 页面。
- [x] 做第一版 **PyTrendline -> unified event schema** 的试映射。
  - 已完成最小交付：
    - `docs/CROSS_ENGINE_MAPPING.md` 已追加 `PyTrendline mapping v1`；
    - 已生成 `outputs/research/pytrendline_event_sample.csv`；
    - 已生成最小网页入口 `reports/site/factors/pytrendline_event_source/report.html`。
- [x] 基于 `PyTrendline event sample` 做第一轮 **PyTrendline event-level validation**。
  - 已生成：`reports/site/factors/pytrendline_event_validation/report.html`
  - 当前第一轮只覆盖 bridge v1 可见范围：
    - breakout vs non-breakout candidate
    - support vs resistance
    - slope / quality buckets
    - event 后固定 horizon 的方向 / 收益分布
  - 默认按模板 v1 执行：
    - horizon = `+1 / +3 / +6 / +12 bars`
    - 指标 = `up_ratio / mean_forward_return / median_forward_return / iqr_forward_return / sample_count`
  - 说明：`representative only vs all valid` 与更完整 `rebound / retest` 仍待 v2 bridge 扩展。
- [x] 基于同一事件问题，做 **PyIndicators source vs PyTrendline source** 的第一轮并行比较。
  - 已生成：`reports/site/factors/cross_engine_source_comparison/report.html`
  - 当前 v1 是 **source-level / evidence-level 对照**，先只回答：
    - 两边目前谁更成熟、谁覆盖更广
    - breakout vs rebound / touch coverage
    - 当前证据各自更强 / 更弱在哪
  - 当前结论：
    - `PyIndicators` 仍是覆盖更广、证据更多的 baseline source，但 breakout 线整体偏弱；
    - `PyTrendline` 定义更干净，也已进入 observation 层，但当前 coverage 窄、breakout validation v1 仍偏弱。
- [ ] 在 bridge v2 / 更可比 sample 上，再做第二轮更严格的 **apples-to-apples numeric comparison**。
  - 目标再补：
    - representative only vs all valid
    - rebound / retest coverage
    - 尽量同样窗口 / 同样 bucket 的对照
- [x] 在 Mainline 中补一张 **decision card**。
  - 当前默认口径已落到页面：
    - `breakout` → 偏 `park / weak`
    - `rebound retained subsets` → 偏 `continue / feature candidate`
    - `pytrendline source` → `unknown / need bridge`

---

## B. Engine Labs（定义引擎实验室）

目标：
- 这里不是主结论页；
- 这里只负责讲清定义方式、边界、输入输出、可否成为 mainline 的事件来源。

### B1. Engine Lab · PyTrendline

目标：
- 把 `pytrendline` 冻结成 explainability baseline；
- 为未来接入 unified event schema 做准备。

#### B1-A. explainability baseline v1

- [x] 完成 `pytrendline_research` explainability 主体建设：
  - reading guide
  - 参数解释
  - pivot / candidate / duplicate grouping / breakout 语义
  - filter waterfall
  - accepted vs rejected examples
  - line lifecycle + state diagram
  - selected line deep-dive
  - time semantics / hindsight 边界
  - 分步骤图与 overlay 语义修正

- [x] 已增加：
  - `candidate_lines_before_filter`
  - `duplicate_grouping_before_after`
  - 四段式结构
  - baseline v1 status note
  - next step 建议

#### B1-B. PyTrendline 接入 mainline 的下一步

- [x] 明确：`pytrendline` 当前哪些对象可以映射成 unified event schema。
  - 已在 `docs/CROSS_ENGINE_MAPPING.md` 与 `PyTrendline Event Source Bridge v1` 中明确：representative line、breakout-tagged line、line side、score、num_points、duplicate group、breakout timestamp 等对象的最小映射。
- [x] 产出一个最小的 **PyTrendline event-source sample**。
  - 已生成：`outputs/research/pytrendline_event_sample.csv`
  - 当前最小样本基于 `BTC-USD / 10d / 5m / window96`，包含 `source_engine / event_family / event_subtype / line_side / event_timestamp / slope_bucket / quality_bucket` 等字段。
- [x] 单独标注哪些字段是 `pytrendline` 独有、不可与 PyIndicators 硬对齐。
  - 已明确记录：`duplicate_group_id`、`best_from_duplicate_group`、`num_points`、`score` 等仍属 engine-specific。
- [ ] 补一份 **PyTrendline literature / repo map**。
  - 最小交付：`docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
  - 每条材料至少记录：来源、事件定义、是否强调 confirmation / retest、可借鉴点、风险点。
- [x] 基于 event sample 做第一轮 **PyTrendline event-level validation**。
  - 已完成第一版 observation 页：`reports/site/factors/pytrendline_event_validation/report.html`
  - 当前先覆盖：breakout vs touch candidate、support vs resistance、slope bucket、quality bucket。
  - 默认执行模板：
    - horizon = `+1 / +3 / +6 / +12 bars`
    - 统计 = `up_ratio / mean / median / IQR / sample_count`
  - 待后续 bridge v2 再补：`rebound / retest / representative only vs all valid`。

### B2. Engine Lab · PyIndicators

目标：
- 不再把它当最终 thesis；
- 把它保留为一个已经跑过很多实验、能提供反证与样本的 baseline engine。

#### B2-A. 已有 engine evidence

- [x] 已完成 `trendline_breakout_navigator` 语义对齐与可视化。
- [x] 已完成 `trendline_segment_backtest` baseline 回测页。
- [x] 已完成 interval sweep / cross-market / rebound scan。
- [x] 已完成 slope-conditioned audit，并得到“整体偏弱、只能保留少数 subset”的中间结论。

#### B2-B. 对 PyIndicators 的当前定位

- [x] 明确：它当前更适合作为 **baseline event source / 对照组**。
- [x] 在文档或页面中明确标注：
  - 暂不再优先做“raw PyIndicators breakout 的泛化优化”；
  - 除非 confirmation / subset audit 再次给出清晰正面证据。
  - 研究动作上默认“收起来”，只保留已有 evidence、subset 结论与对照作用。

#### B2-C. PyIndicators 接入 mainline 的下一步

- [x] 明确哪些现有事件字段已经满足 unified event schema。
  - 已在 `docs/CROSS_ENGINE_MAPPING.md` 新增 `PyIndicators mapping v1`，明确 `segment_strategy_events / navigator_segments / confirmation_ladder trade_detail` 中哪些字段已可直接映射到 `source_engine / sample_key / event_family / line_side / event_timestamp / confirmation_level / engine_line_id / slope_bucket`，以及哪些仍缺。
- [ ] 把现有回测口径里与 execution 绑定过深的部分拆出来，避免混淆 detection / confirmation / execution。

---

## C. Downstream Exploitation（只对胜出者继续）

前提：
- 只有当 mainline 在某些事件 / subset / source 上给出较明确正面证据时，才进入这一层。

### C0. Raw alpha focus（当前新增小重点）

> 这一层不是要替代 structure-event mainline，而是承接一条已经通过第一轮外部来源 clean-room 验证、值得继续深挖的原始策略支线：`EMA / PSAR`。

- [x] 把 `EMA` 正式作为当前项目的 `raw alpha baseline` 候选挂入主线比较口径。
  - 最小要求：后续所有新结构/过滤器/confirmation 层，都应尽量回答“是否稳定优于 EMA baseline”。
  - 最新补充（2026-03-14）：当前这条口径已经在 `EMA / PSAR Raw Alpha Focus Report` 与 `alpha_closure_board` 写死：`EMA = raw alpha baseline candidate`，且下一步默认先做 `EMA 60m gross vs 20bps` 的 rolling / walk-forward falsification slice，后续结构层若要继续推进，默认都应回答“是否稳定优于 EMA baseline”。
- [x] 把 `PSAR` 正式作为第二原始 alpha 候选挂入研究队列，但当前默认角色标记为 `fast reaction / loss-protection candidate`，而不是直接与 EMA 视作同类主干 alpha。
  - 最新补充（2026-03-14）：当前这条口径也已在 `EMA / PSAR Raw Alpha Focus Report` 与 `alpha_closure_board` 固定下来：`PSAR` 保留为第二原始策略候选，但默认角色已明确收为 `fast reaction / loss-protection candidate`，后续优先走 `EMA + PSAR` 最小组合验证，而不是单独扩成与 EMA 同级的主 alpha。
- [ ] 维护 `EMA / PSAR Raw Alpha Focus Report`，确保它持续回答这三个问题：
  - 谁更像主 alpha baseline？
  - 谁更像 exit/filter/protective layer？
  - 它们在不同市场 / 频率 / 成本假设下是否仍成立？

#### C0-A. EMA 后续任务

- [x] 为 `EMA raw alpha baseline` 增补成本敏感性页（gross / low-cost / high-cost）。
  - 最新补充（2026-03-14）：已把 first-pass `cost budget` 审计正式挂进 `EMA / PSAR Raw Alpha Focus Report`，用 `gross / 10bps / 20bps / 50bps` 的线性近似摘要回答“EMA 扣完成本后还站不站得住”。当前正式读法：`EMA` 在 `1d / 1wk` 的成本空间仍明显充足，但到 `60m` 明显收紧——`60m` 正 gross 组合的 median breakeven round-trip cost 约 `27.5bps`，扣 `20bps` 后仍约有 `4/9` 组合存活；因此它仍可保留为 `raw alpha baseline candidate`，但后续必须补更正式的 net / rolling / OOS 页面。
- [x] 为 `EMA raw alpha baseline` 增补 rolling / OOS honesty 检查，避免只是在长牛市样本里显得好看。
  - 已完成（2026-03-15）：`EMA / PSAR Raw Alpha Focus Report` 已补齐 `Crypto 60m rolling falsification + A股 frontier rolling + A股 daily/weekly strict holdout`，并把 family 边界压成 `final survivor map`。当前更诚实的固定口径已收敛为：`Crypto 60m = fail`、`A股 weekly = remove / PSAR-lean`、`沪深300ETF 1d = mixed / watch`、`创业板ETF 1d = daily survivor`，其余 `美股/crypto/茅台 1d+1wk` 只保留为次级 backstop；这条任务的完成并不代表 EMA“全市场都稳”，而是说明 rolling / OOS honesty 已经足够把 baseline family 的 keep/watch/remove 边界说清。
- [x] 把 `EMA` 作为后续 breakout / retest / confirmation 研究的默认 baseline，对比“结构层有没有带来增量价值”。
  - 已完成（2026-03-15）：`alpha_closure_board` 已新增显式 `structure vs EMA baseline` 对照表，并落地 artifact `reports/artifacts/alpha_closure_board/structure_vs_ema_baseline_v1.csv`。
  - 当前固定口径：`EMA baseline family` 继续占据默认 baseline / deployment reference lane；`support_breakout_v0` 目前仍只算 `conditional alpha / one_more_gate`，还没有在 admission rank 上反超 EMA；`Fibonacci` 则继续停在 `archive / optional filter`。后续结构层若要继续消耗主资源，默认应先回答：它能否比 EMA 更诚实地拿到 paper admission，或至少给出明确可并列保留的增量价值。

#### C0-B. PSAR 后续任务

- [x] 对 `PSAR` 做角色审计：它更适合作为 `standalone alpha`、`protective exit`，还是 `fast filter`？
  - 最新补充（2026-03-14）：当前角色审计已经在 `EMA / PSAR Raw Alpha Focus Report` 中形成固定口径：`PSAR` 更像 `fast reaction / loss-protection candidate`，比起独立 `standalone alpha`，现阶段更值得优先拿去回答“当快退出 / protective layer 时，是否比单跑 EMA 更诚实”。
- [x] 为 `PSAR` 增补成本与交易频率敏感性页，重点检查“更高交易次数是否显著吃掉其表面收益”。
  - 最新补充（2026-03-14）：已把这部分正式挂进 `EMA / PSAR Raw Alpha Focus Report` 的成本段。当前正式读法：`PSAR` 的交易频率更高（overall median trades 约 `113`，高于 EMA 的约 `53`），而且 `60m` 成本空间更薄——正 gross 组合的 median breakeven round-trip cost 约 `15.4bps`，扣 `20bps` 后只剩约 `2/9` 组合仍为正，`50bps` 下已 `0/9` 存活；因此这项任务可收口，且结论进一步支持它当前更像 `fast reaction / loss-protection candidate`，不宜直接当与 EMA 同级的主 alpha。
- [x] 做一版 `EMA + PSAR` 的最小组合研究：
  - `EMA` 决定主方向
  - `PSAR` 决定更快退出 / 保护性反应
  - 先回答“组合后是否比单跑 EMA 更诚实”。
  - 最新补充（2026-03-15 18:25 UTC）：已把现有 `Crypto 60m overlay slice + A股 daily overlay audit` 压成统一的 `EMA + PSAR overlay deployment matrix`，并挂回 `EMA / PSAR Raw Alpha Focus Report`。当前 first-pass 结论已足够固定：`Crypto 60m` 约仅 `4/30` 窗口改善、median net20 delta 约 `-6.26pp`、median trade delta 约 `+46`，因此只能继续视为 `reject rescue overlay`；`创业板ETF 1d` 约 `75%` strict holdout 改善、median delta 约 `+2.00pp`，只保留为 `primary lane` 的 `shadow protective` 候选；`沪深300ETF 1d` 约 `25%` 改善、median delta 约 `-1.51pp`，不能当 promotion patch；A股 daily overall 约 `50%` 改善、median delta 约 `-0.38pp`，因此项目级默认规则仍是 `EMA` 负责方向与默认持有，`PSAR` 不升格成 family-wide default overlay。

### C0-C. 三条收口线（短期最高优先级）

- [x] 为 `V3 / Fibonacci / EMA-PSAR` 各自补一版 **closure-style report framing**。
  - 每页最少都要清楚回答：
    - 当前核心结论是什么；
    - 当前最强证据是什么；
    - 不支持什么结论；
    - 更像 `main alpha / conditional alpha / filter / baseline / park` 中哪一类；
    - 下一步最值得做的完整性验证是什么。
  - 最新补充（2026-03-14）：这三条线现在都已有对应的 closure-style 读法页/段落：`support_breakout_v0_h24` 已把 v0 breakout 收成 `conditional alpha / strategy-facing prototype`；`support_breakout_v0_fib_ab` 已把 Fibonacci 收成 `optional filter candidate with archived status`；`EMA / PSAR Raw Alpha Focus Report` 则已把 `EMA = raw alpha baseline candidate`、`PSAR = fast reaction / loss-protection candidate` 写成固定口径，并在页内回答最小 falsification slice 应先从哪里下刀。
- [x] 为这 3 条线补一个更上位的 **comparison / decision board**。
  - 目标不是拼谁图更多，而是回答：
    - 谁最值得继续做更完整回测；
    - 谁更像辅助层；
    - 谁该收口归档；
    - 若都不够强，下一轮该回到哪类新 alpha 搜索。
  - 最新补充（2026-03-14）：`alpha_closure_board` 现已把这四个问题都写成网页可见结论：资源顺序已明确为 `EMA / PSAR = #1`、`breakout-short follow-up = #2`、`Fibonacci = archived`；同时新增“若三条线都没过 gate，应回到哪类外部 alpha 搜索”的 fallback 段，明确下一轮应优先回到 `structure-event confirmation / retest / filter / raw baseline` 相关的 E-track，而不是泛泛扩候选池。
  - 最新补充（2026-03-14）：`alpha_closure_board` 现也已把 breakout v0 的 first-pass realism 一并补回总览口径——`20bps` 下 per-asset independent 累计约 `75.03%`，但 `equal-weight concurrent(entry)` 约 `19.40%`、`1-slot global` 约 `13.83%`；当前更诚实的读法因此变成：这条线仍值得继续，但应作为需要组合级资金曲线 / sizing honesty 的 `conditional alpha` 继续推进，而不是再按独立记账累计收益去想象执行空间。
  - 最新补充（2026-03-14）：`alpha_closure_board` 现也已把 `raw vs confirm_1` 的同框架结果补回总览口径：在同样的 `20bps / equal-weight / 1-slot` first-pass 下，`confirm_1` 约为 `59.38% / 12.04% / 5.06%`，仍低于 raw 的约 `75.03% / 19.40% / 13.83%`；因此当前固定资源顺序不变——`raw` 继续作为 breakout-short 主原型，`confirm_1` 仅作为紧邻确认变体跟进，而不是反过来抢主线位。
  - 最新补充（2026-03-14）：`alpha_closure_board` 现也已把 breakout v0 的 `hourly portfolio path` 结果补回总览口径：在 `20bps` 下，raw 从 `equal-weight concurrent(entry)` 的约 `19.40%` 进一步压到更正式 `equal-weight hourly path` 的约 `14.04%`，已几乎贴近 `1-slot global` 的约 `13.83%`。因此当前总决策页的 breakout 读法也更收紧了：这条线仍值得继续，但必须按统一资金曲线来理解执行空间；下一步若继续，更该把 `confirm_1` 放进同一套 hourly portfolio path / sizing honesty 里复核，而不是再扩 breakout 变体。
  - 最新补充（2026-03-14）：`alpha_closure_board` 现也已同步 `confirm_1 hourly portfolio path` 的最新结果：在更正式的 `20bps hourly mark-to-market` 口径下，`confirm_1` 约为 `11.54% / -13.60%`（累计 / max drawdown），仍弱于 raw 的约 `14.04% / -12.03%`。因此总决策页的 breakout 线 next step 已进一步收窄为：不再继续纠结 `confirm_1` 会不会抢主线位，而是默认继续把 raw 当主原型，并优先把 `avoid_fluctuating` 这类更像样的环境 gate 放进同一套 hourly portfolio path / sizing honesty 里复核。
  - 最新补充（2026-03-14）：`alpha_closure_board` 现也已把 EMA 线的两刀真实结果补回总览口径：`EMA 60m` 在 `BTC/ETH/SOL` 的 `45d + 15d` rolling slice 中，gross 正窗口仅 `4/30`、`20bps` 后仅 `2/30`，且 `0/3` 资产达到“多数窗口 net 为正”；进一步叠加 `PSAR exit overlay` 后，正窗口降为 `0/30`，整体 median window net20 delta 约 `-6.26pp`。因此当前总决策页的正式读法已收窄为：`EMA / PSAR` 线仍可继续，但应把 `EMA 60m crypto` 明确视为失败口袋；若还继续这条线，更该问“日/周频 baseline family 还剩什么”或“overlay 为什么只增加交易次数却没带来净改善”，而不是继续把 60m 当 hopeful 证据。
- [x] 在网页主入口或主线页中把这 3 条线挂成“当前收口中的候选”，避免最新最关键结论淹没在一堆子页面里。
  - 最新补充（2026-03-14）：站点首页 `reports/site/index.html` 与 `plans/index.html` 现在都已按 `closure-first` 挂出固定入口，并把 `Current Alpha Closure Board` 提到最前；Jerry 现在可以先从三条收口线总入口进入，再分流到 `breakout v0 / Fib A/B / EMA-PSAR`，不用再在一堆中间页里自己找当前主结论。
  - 最新补充（2026-03-15 21:19 UTC）：首页已新增直接读 artifacts 的 `Deployment Watch / 当前守门快照`，不再只停在静态 priority 文案。当前会把 `ema_paper_trading_due_guardrail_snapshot.csv`、`ema_paper_trading_refresh_history.csv`、`avoid_fluctuating_scope_verdict_20bps.csv` 压成首页可见的最短执行判断：`EMA` 现在是否已进入 `due_now / overdue`、最靠前 lane 距下一次真实 close 还有多久、append-only ledger 目前累计了几条 completed-bar rows，以及 breakout 当前仍不能被误读成什么。这样 Jerry 只看首页也能更快判断：现在该继续等 EMA 真 close，还是 breakout 终于拿到了足以 overturn `one_more_gate` 的新证据。
  - 最新补充（2026-03-15 22:20 UTC）：首页的 `Deployment Watch` 现已不再死读 artifact 里写死的 `relative_due_gap / due_bucket`，而会按 `next_expected_close_utc` 在发布时动态重算倒计时与 `due_now / overdue` 状态。这样即使 EMA 主报告还没重建，首页也不会把已经到点的 lane 继续误写成旧的 `due_soon / waiting_not_due`；它现在更像一个 honest ops clock，而不只是静态摘要卡。
  - 最新补充（2026-03-15 23:09 UTC）：首页的 `Recent Activity` 现也会把重复出现的 `NO_PROGRESS` 自动合并显示，只保留最新一条原因与合并计数，避免 waiting-window 里的重复守门记录把真正的新推进淹没。这样 Jerry 只看首页，也能更快分清“当前是在诚实等待下一根 completed bar”还是“项目又真的有了新的 deployment-facing 产物”。
  - 最新补充（2026-03-15 23:35 UTC）：首页的 `Deployment Watch` 现也会自动吸收最新一轮 breakout `fresh refresh recheck` artifact，不只显示抽象 scope verdict，还会直接写出：样本尾部目前仍停在哪个 `action_timestamp`、上游 cache 只刷新到哪根 bar、以及 `pure down / 12h pre-down bridge` 这两个最硬 blocker 仍是多少。这样 Jerry 只看首页，也能更快判断：breakout 这条线当前是真没拿到新的 overturn 证据，而不是只是“还没人把最新 rerun 读出来”。

#### C0-C1. V3 后继收口任务

- [x] 把 `v3 final verdict` 与 `support_breakout_v0_h24` 串成更清楚的“研究结论 -> 候选策略原型”路径。
  - 最新补充：已在 `support_breakout_v0_h24` 页与 `alpha_closure_board` 明确写死这条继承关系：`v3 final verdict` 负责回答“留下了什么”，`support_breakout_v0_h24` 负责回答“把留下来的 breakout-short 候选压成最小策略原型后长什么样”；并同步补入当前更可执行的 follow-up 口径：优先试 `avoid_fluctuating`，而不是把它机械地限死在 `only_downtrend`。
- [x] 用 plain-language 补清：`support_breakout_raw / confirm_1 @ h24` 到底更像可交易原型、条件性 alpha，还是只适合作 feature/watchlist。
  - 最新补充（2026-03-14）：已把这段解释正式补进 `support_breakout_v0_h24` 页。当前固定口径是：`support_breakout_raw @ h24 = 可交易 v0 原型 / 条件性 alpha`，`support_breakout_confirm_1 @ h24 = co-primary confirmation variant`，两者都不该降成 `feature/watchlist`；真正更像 `feature/watch` 的仍是 `support_rebound_confirm_1` 这类对象。
- [x] 若继续验证，只允许做更窄的 follow-up：成本、执行、环境约束、非重叠持仓、或更接近策略层的 honesty 检查；不要重新把 v3 扩回大全参数 / 跨市场大工程。
  - 最新补充（2026-03-14）：已把这条边界正式写进 `support_breakout_v0_h24` 页：允许继续做的只剩 `cost / rolling OOS / non-overlap-capital-allocation / avoid_fluctuating` 这类更接近策略层的 honesty / execution follow-up；同时明确不再回到 `v3` 式大全参数搜索、跨市场大工程、或 breakout 变体重新排位。
  - 最新进度（2026-03-14）：已对 `support_breakout_raw @ h24 v0` 补做 first-pass 成本敏感性。当前读法是：扣 `20bps` 后 overall 平均单笔仍约 `1.24%`、累计仍约 `75.03%`，说明这条线不是被轻微成本直接抹平；但 `test split` 累计约 `-3.08%`、`up` 环境累计约 `-2.98%`，因此下一步更该优先补 `split / regime honesty`，而不是继续扩新 breakout 变体。
  - 最新补充（2026-03-14）：`support_breakout_v0_h24` 页现已把 `split / regime honesty protocol v1` 正式写死。当前固定口径是：保持 `support_breakout_raw @ h24` 与 `24bar hold` 不变，至少同时看 `gross + 20bps`，优先回答 `test` 是否持续低于零、以及这条线是否主要只在 `flat` 环境成立；若答案是“主要靠 train + flat 抬起来”，就应继续把它当 `conditional alpha / v0 原型`，而不是升格成通用 short。
  - 最新补充（2026-03-14）：页面也已把 `为什么优先先试 avoid_fluctuating，而不是 only_downtrend` 的 event-level OOS gate 证据包正式挂回原型页：当前关键读法是 `avoid_fluctuating` 仍保留约 `16/19` 个 OOS 事件（约 `84.21%` retention），明显高于 `only_downtrend` 的约 `7/19`（约 `36.84%`）；因此下一步若只做一个最小环境 gate，对 `breakout v0` 更应先试前者，而不是过早把样本砍窄。
  - 最新补充（2026-03-14）：已把 `avoid_fluctuating` 真正推进到和 raw 完全同一套 `20bps hourly mark-to-market` 口径。当前它保留约 `40/48` 笔交易（约 `83.33%`），overall hourly path 累计约 `15.46%`、max drawdown 约 `-9.97%`，相比 raw 的约 `14.04% / -12.03%` 有小幅改善；更关键的是 `up` 弱口袋从约 `-1.99%` 提到约 `+0.95%`，而 `test` 仍约 `-2.67%`。因此这轮之后更诚实的读法是：`avoid_fluctuating` 确实比“换成 confirm_1”更像样，但它仍只是有帮助的最小环境 gate，不是把 breakout 线直接洗成通用 short 的开关。
  - 最新补充（2026-03-14）：已把 `avoid_fluctuating` 的 `hourly path` 再拆到 `split / regime`。当前更细的读法是：`train / validate` 仍约 `+8.16% / +5.52%`，但 `test` 仍约 `-2.67%`；`up` 已转到约 `+0.95%`，可 `down` 仍约 `-1.52%`，真正最像样的仍是 `flat`（约 `+16.79%`）。这说明 gate 的作用更像“先把最刺眼的 up 弱口袋磨平”，下一步若继续补组合层 honesty，更该盯 `test/down` 的尾部风险，而不是再回头纠结 `confirm_1` 排位。
  - 最新补充（2026-03-14）：也已把 `2` 仓弱小时继续拆到 `pair × split/regime`。当前读法是：最大的 broad drag 并不主要长在 `test`，而是像 `BNB+ETH @ train×flat`（约 `20` 小时、mean hourly return 约 `-0.25%`）和 `BTC+SOL @ train×up/flat`；真正更像后段尾部的是更窄的 `ETH+SOL` test pocket（其中 `test × down+flat` 约 `2` 小时、mean hourly return 约 `-0.69%`）。`avoid_fluctuating` 更像先把 `BTC+SOL` 这类 broad drag 压掉了，但 residual weakness 仍集中在 `ETH+SOL @ test+validate × up`（约 `25` 小时、mean hourly return 约 `-0.15%`）；因此下一步最值得做的已从“继续诊断”收窄成“基于这些 residual pair/context 交一版最小条件化 sizing 切片”。
  - 最新结果（2026-03-14）：这刀最小条件化 sizing 现已交付：在 `avoid_fluctuating` 后仍出现的 `ETH-USD + SOL-USD` 两仓小时上只做 `0.5x` 半仓，约影响 `44/398` 个活跃小时（约 `11.06%`）。当前同框架结果是：`20bps` hourly path 约从 gate-only 的 `15.46%` 提升到 `19.90%`，max drawdown 约从 `-9.97%` 收窄到 `-9.04%`，而该 residual pair pocket 的条件累计也从约 `-7.17%` 收窄到约 `-3.61%`。这说明 breakout 线如果继续，更值得做的是把这类 pair-conditioned sizing 放进更严格的 holdout / walk-forward honesty 里复核，而不是继续泛化地换 breakout 分支。
  - 最新结果（2026-03-15）：在 pair-conditioned halfsize 之外，也已补出更窄的 `context-conditioned sizing` 对照：只对 `ETH-USD + SOL-USD @ validate/test × up` 这块 residual context 做 `0.5x` 半仓，约影响 `28/398` 个活跃小时（约 `7.04%`）。当前同框架结果是：`20bps` hourly path 约从 gate-only 的 `15.46%` 提升到 `17.86%`，而该 residual context 的条件累计也从约 `-3.79%` 收窄到约 `-1.95%`。但继续收窄到真正的 `pure test × up` 后，只剩约 `3/398` 个活跃小时受影响，overall 也只轻微抬到约 `15.56%`、pure `test` 条件累计改善仍仅约 `+0.08pp`。因此这条更窄 context-conditioned branch 当前更适合先 park 成诊断型分支，而不是继续与默认 sizing 候选并列消耗主资源。
  - 最新补充（2026-03-15 06:05 UTC）：也已把默认 `ETH+SOL pair-conditioned halfsize` 再压成一刀更严格的 `strict pure-test tail honesty`——从首个 pure `test` 触发（`2026-03-06 00:00 UTC`）一直看到样本末尾。当前这一小段 tail 只有约 `30` 个活跃小时、其中约 `5` 个小时真的触发 halfsize；gate-only 累计约 `-1.02%`，halfsize 约 `-0.25%`，delta 约 `+0.77pp`。这说明 default sizing candidate 在 strict pure-test 眼光下暂时没翻负，但证据仍很薄；再结合 `pure down = 0`，它还不够单独清掉 breakout 的 `one_more_gate`。
  - 最新补充（2026-03-15 06:18 UTC）：也已把 `down-tail` 的 admission gap 改成可量化审计：在 gate-only `20bps hourly path` 里，`down` 段约 `100` 个活跃小时、累计约 `-1.52%`，但默认 `ETH+SOL pair-conditioned halfsize` 在 pure `down` 上覆盖仍是 `0/100`。因此当前更准确的 blocker 不是“还想再看一点 down-tail”，而是“down-tail coverage 仍是硬缺口”，breakout 继续维持 `one_more_gate`。
  - 最新补充（2026-03-15 06:59 UTC）：也已补做一个更诚实的 `down-tail` 反向 sanity check：若把 hard gap 粗暴改成 pure `down` active hours 一律 `0.5x`，overall hourly path 会约从 `19.90%` 回落到 `19.48%`，虽然 max drawdown 可收窄到约 `-7.96%`。这说明当前 blocker 虽然长得像 `down-tail`，却不能靠 blunt pure-down overlay 机械解除；下一刀更像 `down+flat mixed-tail` 或更贴近 shadow 的 honesty 观察。
  - 最新补充（2026-03-15 11:16 UTC）：也已把当前 blocker 压成统一的 `down-risk zone` 审计（`pure down` + 未来会滑进 `pure down` 的 bridge），并把默认 `pair halfsize` 与 `down+flat mixed-tail overlay` 摆到同一张 deployment-facing 表里。当前更硬的读法是：默认 `pair halfsize` 在 `12h/24h down-risk zone` 上仍是 `0` coverage；更关键的是，`mixed-tail overlay` 在同一口径下也仍是 `0` coverage，既没碰到 pure `down`，也没碰到这些 near-down bridge。于是 breakout 当前正式 verdict 继续是 `shadow-admission queue / one_more_gate`，而 mixed-tail 的诚实位置也更明确了：它可以继续当 strict pure-test mixed pocket 的 shadow 观察项，但还不能被写成真正命中 near-down blocker 的 protective gate。
  - 最新补充（2026-03-14）：已对 `support_breakout_raw @ h24` 补做 cross-asset overlap first-pass。当前读法是：约 `50%` 的入场发生时已有至少 `1` 笔别的仓位开着，约 `25%` 的入场发生时已有至少 `2` 笔，且活跃持仓时间里约 `34.80%` 处在 `4` 笔并发；这说明下一步若继续往策略层推进，`non-overlap / capital allocation` 已不能再只停留在口头提醒，而应优先补最小组合约束对照。
  - 最新补充（2026-03-14）：已补做 `1-slot global` 的 capital-allocation first-pass。当前读法是：若全局任何时刻只允许 `1` 笔仓位，`20bps` 下只保留约 `14/48` 笔交易（约 `29.17%`），平均单笔仍约 `0.97%`、累计仍约 `13.83%`；说明这条线并不是“一加组合约束就归零”，但当前页面里约 `75.03%` 的 `20bps` 累计收益，确实明显依赖跨资产并发摊开后的读法。下一步更值得补的是 `1-slot global vs equal-weight concurrent` 的更正式组合级对照。
  - 最新补充（2026-03-14）：已补做 `equal-weight concurrent(entry)` first-pass。当前读法是：若允许并发、但按入场时并发仓位均分资金，`20bps` 下 `48` 笔交易都保留，但平均有效仓位权重只约 `42.36%`，累计约 `19.40%`——高于 `1-slot global` 的约 `13.83%`，但明显低于 `per-asset independent` 的约 `75.03%`；因此这条线仍可保留为 `conditional alpha / v0 prototype`，但后续更该补正式组合级资金曲线，而不是继续按独立记账累计收益理解可执行空间。
  - 最新补充（2026-03-14）：也已把 `support_breakout_confirm_1 @ h24` 放进同一套 `cost / capital-allocation` first-pass 框架对照。当前读法是：`confirm_1` 仍值得保留为 `co-primary confirmation variant`，但还没有表现出比 `raw` 更强的执行层诚实度——在 `20bps` 下其 per-asset 累计约 `59.38%`（低于 raw 的约 `75.03%`），`equal-weight concurrent(entry)` 约 `12.04%`（低于 raw 的约 `19.40%`），`1-slot global` 约 `5.06%`（低于 raw 的约 `13.83%`）；因此当前更合理的顺序仍是 `raw` 继续作为主原型，`confirm_1` 作为紧邻确认变体跟进，而不是反过来升格。
  - 最新结果（2026-03-14）：已把 `equal-weight concurrent` 从 entry-only 近似进一步推进到 `hourly mark-to-market` 的统一资金曲线 first-pass。当前在 `20bps` 下，breakout v0 的更正式 hourly equal-weight path 累计约 `14.04%`、max drawdown 约 `-12.03%`，低于 entry-only 近似的约 `19.40%`，但仍略高于 `1-slot global` 的约 `13.83%`；这说明这条线没被组合约束直接抹掉，但 entry-only 口径仍偏乐观，后续若继续推进，更该补正式 portfolio path / sizing honesty，而不是继续按独立记账或 entry-only 结果想象执行空间。
  - 最新结果（2026-03-14）：也已把 `confirm_1` 放进同样的 `hourly mark-to-market` 统一资金曲线口径。当前 `20bps` 下，`confirm_1` 的 hourly equal-weight path 累计约 `11.54%`、max drawdown 约 `-13.60%`，仍低于 raw 的约 `14.04% / -12.03%`；这说明一旦把两者都推进到更正式一点的 portfolio path，`confirm_1` 也没有在执行层反超 raw，因此当前资源顺序仍应保持 `raw` 主原型、`confirm_1` 紧邻跟进。

#### C0-C2. Fibonacci 收口任务

- [x] 把 Fibonacci 线正式收成一页“结论页 / archived idea page”。
  - 最新补充（2026-03-14）：已在 `support_breakout_v0_fib_ab` 页把这条线正式收口成 archived idea page，并明确写清：它原本想解决的是“breakout 后等反抽确认再做空”；它确实改善了机制表达与过滤层直觉，但没有改善主线收益结果——A 组 v0 平均单笔约 `1.44%`、累计约 `92.45%`，fib 版仅约 `0.71%`、累计约 `20.00%`，且平均入场延迟约 `12.5` 根 bar；因此当前不再把它当主 alpha 继续推。
- [x] 若仍保留价值，明确它在当前项目里到底是 `optional filter`、`teaching example`，还是 `future revisit candidate`。
  - 最新补充（2026-03-14）：当前正式标签已写死为 `optional filter candidate with archived status`。它比纯 `teaching example` 更强一点，因为确实说明了“确认层可以改善机制诚实度，但不一定能救活 alpha”；也比泛泛 `future revisit candidate` 更近一点，因为若未来只研究更明确的 `downtrend` breakout-short filter，仍可作为窄验证参考。

#### C0-C3. EMA / PSAR 收口任务

- [x] 把 `EMA / PSAR Raw Alpha Focus Report` 升级成更接近策略决策页，而不只是阶段性研究页。
  - 最新补充（2026-03-14）：页内现已不只回答“谁更强”，也会明确回答“今天该怎么排研发优先级”——当前固定口径是：先把 `EMA` 当主 `raw alpha baseline` 候选补 rolling / OOS honesty；`PSAR` 不单独扩成第二条主 alpha，而是优先放进最小 `EMA + PSAR` 组合验证，看它是否更像快退出 / protective layer。换句话说，这页现在已经更像策略决策页，而不只是阶段性研究摘要。
- [x] 优先补 `EMA` 的成本 / rolling / OOS / 跨市场稳定性，让它真正有资格当 `raw alpha baseline`。
  - 最新进度（2026-03-14）：已在 `EMA / PSAR Raw Alpha Focus Report` 明确写入 `rolling / OOS honesty protocol v1`。当前固定口径是：固定 `EMA9/EMA20` 不再二次调参、按 `asset × freq` 做 rolling / walk-forward 检查、至少同时报告 `gross + 20bps` 近似，并优先看“正收益窗口占比 / 坏窗口是否扎堆 / 是否仍比 PSAR 更像稳定主干”；另外若只先做一个最小 falsification slice，当前默认优先从 `EMA 60m gross vs 20bps` 开始，因为它的成本空间最薄（positive-only median breakeven cost 约 `27.5bps`，扣 `20bps` 后只剩约 `4/9` 组合存活），最适合先检验 baseline 幻觉是否会被打掉。
  - 最新补充（2026-03-14）：页内也已把这个 first falsification slice 的 **go / yellow / fail gate** 写死：如果 `EMA 60m` 在 rolling 下多数窗口仍为正、且 `gross -> 20bps` 后没有出现整排窗口塌陷，就继续保留 `baseline candidate`；如果 gross 还能看、但 `20bps` 后只剩少数窗口/少数资产在撑，就暂缓主 baseline 地位；若 rolling 后大部分窗口在 `20bps` 下都转负，或主要只靠少数大牛段 / 单一资产撑住，就应把 EMA 从 `baseline candidate` 降回 `research branch`。这条任务的判定规则已落地，后续不再需要重复补 protocol wording。
  - 最新结果（2026-03-14）：已用现成 `pytrendline_event_validation_v3_crypto_180d/cache` 对 `BTC / ETH / SOL` 做出第一版 `EMA 60m gross vs 20bps` rolling falsification slice（`45d window + 15d step`）。当前 `30` 个窗口里，gross 只有 `4/30`（约 `13.33%`）为正，扣 `20bps` 后只剩 `2/30`（约 `6.67%`）为正，且 `0/3` 个资产达到“多数窗口 net 为正”；`BTC / ETH / SOL` 的 median window net20 分别约 `-16.24% / -11.45% / -19.71%`。这说明 `EMA 60m` 在 recent crypto slice 上已明显落入 `fail` 档；若还继续 EMA 线，更合理的是把这块当成最弱口袋，优先看 `EMA + PSAR exit overlay` 能不能改善，而不是再把 `EMA 60m` 单独当 baseline 证据继续包装。
  - 最新完成态（2026-03-15）：后续又补齐了 `A股 frontier rolling + A股 daily strict holdout + A股 weekly strict holdout + final survivor map`。当前项目级结论已能写死为：`EMA baseline family` 不是“跨市场都稳”，而是已经收成明确边界——`创业板ETF 1d` 仍是 primary survivor，`沪深300ETF 1d` 只配 `mixed/watch`，`A股 weekly` 与 `Crypto 60m` 均应排除，其余 `美股/crypto/茅台 1d+1wk` 只保留为 secondary backstop。也就是说，这条任务现在完成的意义不是证明 EMA 无敌，而是已经足够诚实地回答“哪部分还能拿去 paper、哪部分必须排除”。
- [x] 优先补 `PSAR` 的角色判断：它更像主 alpha、保护性退出、还是更快反应层。
  - 最新补充：已在 `EMA / PSAR Raw Alpha Focus Report` 里补上更明确的收口定位：当前正式口径是 `EMA = raw alpha baseline candidate`，`PSAR = fast reaction / loss-protection candidate`；当前不支持把 PSAR 直接升成与 EMA 同等级的主 alpha，后续更合理的是先做 PSAR 的成本/交易频率敏感性与 `EMA + PSAR` 最小组合研究。
- [x] 做一版 `EMA + PSAR` 最小组合研究，并明确它是否比“单跑 EMA”更诚实、更可用。
  - 最新进度（2026-03-14）：组合验证的最小协议已先写回 `EMA / PSAR Raw Alpha Focus Report`。当前固定口径是：`EMA` 负责主方向 / 默认持有，`PSAR` 只负责更快退出 / protective overlay；比较时必须与 `单跑 EMA` 用同一资产、同一频率、同一资金与成本口径，且至少同时看 `gross + 20bps`。若只先做一个最小 falsification/combination slice，当前默认优先 `EMA 60m + PSAR exit overlay`，因为这正好对应 `EMA` 最薄、`PSAR` 也最需要证明“快反应价值能否盖过成本”的那一块。
  - 最新结果（2026-03-14）：已用同一批 `BTC / ETH / SOL` 60m cache（`45d window + 15d step`）做出第一版 `EMA 60m + PSAR exit overlay` 对比 `单跑 EMA 60m` 的真实切片。当前 overlay 只在 `4/30` 个窗口（约 `13.33%`）里把 net20 做得更好，`EMA` 自己在 `20bps` 下至少还有 `2/30` 个正窗口，但 overlay 后变成 `0/30`；整体 median window net20 delta 约 `-6.26pp`，median trade delta 约 `+46` 笔，且 `0/3` 个资产出现“median delta 为正”。这说明在当前最脆的 crypto 60m 口袋里，`PSAR exit overlay` 还没有救到 EMA，反而更像通过显著抬高交易频率把 cost-adjusted 结果进一步压坏。
  - 最新补充（2026-03-14）：已继续把 overlay 失败拆到 `trade_delta` 诊断层。当前 `trade_delta` 与 `net20_delta` 的相关系数约 `-0.68`：当 overlay 额外多出至少 `50` 笔交易时，这类窗口约占 `5/30`，但 `0%` 窗口出现 net20 改善，中位 delta 约 `-9.71pp`；即便额外交易控制在 `<45` 笔，这类窗口约也只有 `4/13` 出现改善，中位 delta 仍约 `-1.13pp`。因此当前更像是：`PSAR` 把区间切得更碎、显著抬高了换手，但没有稳定换来足够多的坏窗口修复。
  - 最新补充（2026-03-14）：已把 `EMA / PSAR` 的 `baseline family survivors` 切到 `1d + 1wk vs 60m` 的同页结果里。当前 `EMA non60m` 共 `18/18` 组合 gross 为正、`20bps` 下也仍 `18/18` 存活，positive-only median breakeven cost 约 `2066.8bps`；`PSAR non60m` 也仍 `18/18` 存活，但对应 breakeven 约 `585.0bps`。这说明当前更有价值的问题已经不是“60m 能不能被救回来”，而是：若继续保留这条线，应把 `EMA 1d / 1wk` 当作 baseline family 主体，而把 `PSAR` 继续放在次级对照 / protective layer 位置上看。
  - 最新结果（2026-03-14）：也已把 `EMA non60m` 再压成一版 `survivor frontier` 队列。当前最薄的几个口袋依次是 `沪深300ETF 1d`（breakeven 约 `39.7bps`，`50bps` 近似下已约 `-5.79%`）、`沪深300ETF 1wk`（约 `184.0bps`）、`创业板ETF 1wk`（约 `276.5bps`）、`SPY 1d`（约 `339.0bps`）、`QQQ 1d`（约 `383.2bps`）。
  - 最新补充（2026-03-14）：已把这批 frontier 前 6 名和同口径 `PSAR` 做 head-to-head。当前更诚实的读法是：`创业板ETF 1d`、`SPY 1d`、`QQQ 1d` 仍明显支持 `EMA` 作为 baseline，但 `沪深300ETF 1wk` 与 `创业板ETF 1wk` 这两格里 `PSAR` 反而略占优，`沪深300ETF 1d` 更像双方都偏薄、但 EMA 因交易更少而稍厚一点的 mixed pocket。因此若下一轮只做一刀 `EMA non60m` 的 rolling / OOS honesty，更诚实的顺序不应先看最厚的 crypto 周频，而应优先从这批 A股 frontier 开始；如果连它们都守不住，`EMA baseline family` 就该继续收窄。
  - 最新结果（2026-03-14）：已把 `沪深300ETF / 创业板ETF` 这批 A股 frontier 真正推进到第一刀 `rolling / OOS honesty`（`730d window + 180d step`, `EMA9/EMA20`, `20bps`）并与同口径 `PSAR` 对照。当前 `EMA` 在 A股 frontier 上是 `mixed`：`2/4` 个 pocket 达到“多数窗口 net20 为正”，与 `PSAR` 持平；其中 `沪深300ETF 1d / 1wk` 仍可守住（median net20 约 `+0.13% / +9.21%`），`创业板ETF 1d` 仍明显好于 `PSAR`（约 `-0.75%` vs `-16.19%`），但 `创业板ETF 1wk` 仍明显偏弱（`EMA` 约 `-11.64%` vs `PSAR` 约 `+13.10%`）。这说明 `EMA baseline family` 还没有被 A股 frontier 一刀否掉，但下一步应继续收窄到 `A股 weekly frontier`，而不是再平均撒在整个 non60m family 上。
  - 最新结果（2026-03-15）：现已把 `A股 weekly frontier` 进一步推进到更严格的 `strict holdout honesty`：固定 `EMA9/EMA20` 与 `PSAR`，用 `730d lookback + 365d forward holdout`、按年滚动，只评估下一年。当前两格 weekly pocket 一共 `14` 个 holdout，`EMA` 正 holdout 占比仅约 `42.86%`，而 `PSAR` 约 `85.71%`；其中 `创业板ETF 1wk` 的 `EMA` median net20 约 `0.00%`，低于 `PSAR` 的约 `4.03%`，`沪深300ETF 1wk` 的 `EMA` 约 `-5.17%`，也低于 `PSAR` 的约 `1.01%`。因此这条线当前最诚实的项目级读法应继续收窄成：`A股 daily` 仍可保留观察，但 `A股 weekly` 已不该再算作 `EMA baseline family` 的支持 pocket，更像 `PSAR/mixed branch`。
  - 最新结果（2026-03-15）：现也已把 `A股 daily` 推进到同样更严格的 `strict holdout honesty`：当前两格 daily pocket 共 `16` 个 holdout，`EMA` 正 holdout 占比约 `62.50%`，高于 `PSAR` 的约 `43.75%`；其中 `创业板ETF 1d` 的 `EMA` median net20 约 `12.05%`，明显高于 `PSAR` 的约 `5.13%`，`沪深300ETF 1d` 则更像 mixed，但 `EMA` median net20 约 `-2.60%`，仍略好于 `PSAR` 的约 `-4.49%`。因此这条线当前更诚实的 family 边界已能收成一句话：`A股 weekly` 出局，但 `A股 daily` 仍可暂时保留，尤其 `创业板ETF 1d` 仍是能替 EMA 守门的 daily pocket。
  - 最新结果（2026-03-15）：现已把前面分散的结果进一步压成 `EMA baseline family final survivor map`。当前固定边界已可写死为：`60m crypto` = fail pocket；`A股 weekly frontier` = remove / `PSAR-lean`；`沪深300ETF 1d` = mixed / watch；`创业板ETF 1d` = daily survivor；`贵州茅台 1d+1wk`、`美股 1d+1wk`、`Crypto 1d+1wk` = 仍可暂时保留的 nonfrontier backstops。也就是说，EMA family 现在既不是“只剩 A股 daily”，也不是“non60m 整体都一样强”，而是已经收成了前线 keep/watch/remove 更清楚的分层边界。
  - 最新结果（2026-03-15，runbook overlay audit）：已进一步把 `A股 daily strict holdout` 下的 `EMA + PSAR exit overlay` 直接压到 deployment 口径。当前 `创业板ETF 1d` 这格 primary pilot 上，overlay 约 `75%` 的 holdout 能改善 net20，median delta 约 `+2.00pp`、median trade delta 约 `+13`；但 `沪深300ETF 1d` 这格 shadow 上，overlay 仅约 `25%` 改善、median delta 约 `-1.51pp`、median trade delta 约 `+15`。两格合并后 overall 改善占比约 `50%`、median delta 约 `-0.38pp`，因此项目级更诚实读法是：`PSAR` 目前只配作为 `primary shadow protective` 候选与 benchmark 观察位，不应焊进 A股 daily 默认 runbook，更不能拿来替代 shadow promotion gate。

### C1. Event feature builder

- [ ] 实现一个 **trendline / structure event feature builder**。
  - 至少输出：
    - event type
    - line side
    - slope bucket
    - quality bucket
    - confirmation state
    - bars since event
    - source engine
  - 当前优先只接：`PyTrendline event sample` + `PyIndicators baseline sample`。

### C2. MVP signals

- [ ] 实现一个 **最小规则型 structure-event signal**。
  - 原则：
    - 先只做 1~2 种事件；
    - 不做过多参数混战；
    - 明确区分 detection / confirmation / execution。
  - 当前推荐的最小候选：
    - `pytrendline rebound + light confirmation`
    - `pytrendline breakout + retest_hold`（仅在 event-level validation 支持时再做）

### C3. Strategy validation（只对胜出者）

- [ ] 对通过 mainline 的事件做 MVP 回测。
- [ ] 做最小必要的：
  - OOS
  - rolling
  - cross-asset
  - sample adequacy 检查
- [ ] 在未完成 event-level validation 之前，不提前做大规模参数优化。

---

## D. Candidate Engines / Future Branches

### D1. Parallel Channel（保留但降级）

目标：
- 继续保留你的 channel 兴趣；
- 但不在 structure-event foundation 之前，直接把它重新升成主 alpha thesis。

#### D1-A. 外部研究与来源清单

- [ ] 收集 5~10 个与 `parallel channel / channel breakout / channel rebound / trend channel / regression channel` 有关的外部仓库或研究材料。
  - 结果要求：
    - 来源
    - 许可证
    - 核心方法
    - 可借鉴点
    - 风险点

- [ ] 整理这些外部实现如何定义平行通道。
- [ ] 整理这些实现如何定义趋势方向 / breakout / rebound / confirmation。

#### D1-B. 升级条件

- [ ] 明确：**什么条件下，parallel channel 才值得从候选分支升级成主线**。
- [ ] 在升级条件未满足前，不直接进入 `parallel_channel_*` 的大规模实现与回测。

### D2. 其他未来候选引擎

- [ ] 为未来的 channel / regression / support-resistance 引擎预留统一接入口。
- [ ] 原则上先接到 unified event schema，再谈策略页。

---

## E. External Alpha / Literature Scout（外部 alpha / 文献侦察）

目标：
- 系统性寻找 **近 5 年** 与 trendline / support-resistance / breakout / rebound / retest / confirmation 相关的论文、开源仓库、复现文章；
- 优先选择 **来源靠谱 + 有回测 / alpha claim + 有逻辑说明 + 有公开 GitHub/代码 + 能拿到全文** 的材料；
- 把“别人声称有效的结构 alpha”与“我们自己已经本地验证过的东西”严格区分开；
- 为后续 mainline / engine labs 提供可审计、可复现、可进入本地验证队列的候选池；
- 明确把 E 模块视为 **当前最快的 alpha 发现通道**：默认优先去找高标准文献、公开仓库、可复现逻辑，而不是停留在泛泛综述；
- 明确把 E 模块视为 **主线的外部证据轨**，默认服务当前最核心的问题：事件定义、验证指标、confirmation/retest 设计、以及 replication candidates。

边界：
- 这里不是直接下最终策略结论的地方；
- 这里先回答：**别人做了什么、证据质量如何、值不值得复现、该先复现哪几个。**
- 但 E 模块也不再满足于“只读不做”：默认应尽量把高质量来源推进到 **replication brief -> 最小本地验证 -> factor intake decision** 这条链路；
- 默认要求每轮 E 产出尽量能落回主线四类用途之一：
  - `event source design reference`
  - `validation metric / protocol reference`
  - `confirmation / retest / filter reference`
  - `clean-room replication candidate`

### E0. 当前默认策略（2026-03-13 起）

- [ ] 短期把 E 模块视为默认最高优先级工作流，优先于新增 explainability 美化类任务。
- [ ] 默认不再把“只新增一篇泛泛 digest”视为高价值完成；优先完成以下任一更接近 alpha 的动作：
  - 新增一个高质量来源卡并完成 reproducibility audit
  - 把一个候选推进到 replication brief
  - 对一个候选完成最小 clean-room 复现
  - 对一个候选完成最小 event study / MVP backtest
- [ ] 若某个外部来源在本地最小验证里显示出明确正面 alpha 证据，则应立刻创建对应的 `factor intake` / `candidate signal` 任务，而不是只停留在 reading 层。

建议目标文件 / 产物：
- `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
- `scripts/build_trendline_alpha_scout_report.py`
- `reports/site/reading/trendline_alpha_scout/report.html`
- `research/quant_digests/*.md`（短卡）
- `research/deep_dives/*.md`（长文拆解）

### E1. Scout protocol（侦察协议）

#### E1-A. 搜索范围与筛选标准

- [x] 明确 `trendline alpha scout` 的搜索协议。
  - 已在 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md` 新增 `Scout protocol v1`：覆盖 6 类关键词簇、4 项高优先级纳入门槛、第一轮质量审计 7 项、以及 `digest / deep dive / replication brief / park` 的动作分层。
  - 其中也明确：只能拿到摘要 / 结论、拿不到正文的来源，默认标记为 `abstract_only / weak_evidence`，不进入优先 digest / deep dive / replication。

- [x] 明确允许保留的例外材料。
  - 已明确：超过 5 年但属于 `canonical / older baseline` 的理论根节点可保留，但必须单独标注，不能和近年高优先级 replication candidates 混排。
  - 例如：虽然超过 5 年，但属于 canonical baseline（如 Lo 2000）时，可作为“理论根节点”保留，但必须单独标注为 `canonical / older baseline`。

#### E1-B. 来源卡片模板

- [x] 定义统一的来源卡片字段，写入 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`。
  - 已新增 `最小字段 checklist (v1)` 与更新后的卡片模板；除原有标题 / 作者 / 链接 / 市场 / alpha claim / 结构定义 / 是否有代码 / 风险 / 推荐动作外，现还要求明确 `fulltext_access`、`evidence_status`、`license/source boundary` 与 `clean-room` 复现难度。 
### E2. Intake queue（候选收集队列）

#### E2-A. 第一轮候选池

- [ ] 收集第一轮 `8~12` 个**高质量**候选来源（不再以凑数量为先）。
  - 结果要求：优先 trendline / support-resistance / channel / confirmation 相关材料；
  - 至少 `70%` 来自近 5 年；
  - 至少 `5` 个带公开仓库 / 明确代码 / 可 faithful-clean-room 复现路径；
  - 第一批默认优先级：`全文可得 + 有公开代码/仓库 + 有回测 alpha claim` > `全文可得 + 无代码但定义清楚` > `只有摘要/结论`；
  - 若来源只有摘要、没有正文、没有可操作定义，默认不算优先 intake。

- [ ] 把第一轮候选统一整理到 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`。
  - 当前进度：已新增 `De Angelis et al. (2021)` 这张高相关来源卡，定位为 `filter_candidate`；它提供了可直接转写成 15m crypto breakout 对照实验的 `threshold / no-trade band / wait-and-see` clean-room 入口。
  - 最新补充：已新增 `Gurrib et al. (2022)` 来源卡，定位为 `filter_candidate`；当前最可复用的点不是把 Fibonacci 回撤位当独立 alpha，而是把它当 `pullback / breakout confirmation layer`，并优先测试短确认窗口。
  - 最新补充：已新增 `Naganjaneyulu et al. (2023)` 来源卡，当前定位同样不是主 alpha 论文，而是 `regime / filter reference`：最值得迁移的是“先分 Uptrend / Downtrend / Fluctuating，再决定是否允许 breakout / pullback 交易”的设计原则，而不是直接照抄 `MIHCS7` 参数。
  - 最新补充：已新增 `Yumna et al. (2024)` 来源卡，当前定位为 `confirmation / filter reference`：最值得迁移的不是周频 BTC 形态结论本身，而是把 `volume confirmation + support flip + higher low persistence` 写成 15m breakout 假突破过滤层。
  - 最新补充：已新增 `Wiśniewski (2024)` 来源卡，当前定位同样是 `confirmation / filter reference`：最值得迁移的不是周频趋势线案例本身，而是把 `third-touch confirmation + EMA/MACD confluence` 写成更客观的 15m breakout / retest 过滤层。
- [x] 在网页侧生成一个 **Trendline Alpha Scout** 总览页。
  - 已落地：`reports/site/reading/trendline_alpha_scout/report.html`
  - 当前页已能按候选池 / shortlist / 状态标签展示，并区分 `deep_dive_done / digest_done / replication_candidate / parked / read` 等状态。 
#### E2-B. 质量审计

- [ ] 为每个候选补一个最小 **quality / reproducibility audit**。
  - 当前进度：已为 `De Angelis et al. (2021)` 补了最小 audit——全文页可访问、未发现公开官方代码、主价值在 `threshold / no-trade band` 的 confirmation/filter 启发，建议走 `digest -> replication brief` 而不是直接升为高优先级 faithful replication。
  - 最新补充：已为 `Gurrib et al. (2022)` 补最小 audit——全文可得、规则定义可读但未见官方代码，交易成本与 OOS 讨论偏弱、样本也不厚；因此当前更适合当 `confirmation / retest / filter reference`，先做短窗口 pullback confirmation 的 clean-room 对照，而不是直接升为主 replication candidate。
  - 最新补充：已为 `Naganjaneyulu et al. (2023)` 补最小 audit——全文可得、规则分层清楚（regime → indicator switch / buy restriction），但只有 BTC 日频、缺强 OOS / cost 讨论、未见官方代码；因此完整 `MIHS / MIHCS` 当前仍更适合当 `regime gate` 设计参考，而不是高优先级 faithful replication。最小 clean-room 入口应是“先测 regime gating 能否压低 15m 假突破与回撤”，而不是照搬论文的 `EMA(RSI)>60/<40` 与 `MIHCS7` 配方。
  - 当前新增分流判断：虽然完整分层策略仍不升主 replication shortlist，但该论文里的两个原始策略 `EMA / PSAR` 已经通过本地 cross-market 第一轮验证，现应转入项目内部的 `raw alpha focus` 小重点；其中 `EMA` 当前定位为 `raw alpha baseline candidate`，`PSAR` 当前定位为 `fast reaction / loss-protection candidate`。
  - 最新补充：已为 `Yumna et al. (2024)` 补最小 audit——全文可得，但本质是单资产 BTC 周频的定性案例研究，没有系统化回测、缺成本/OOS，也未见公开代码；因此当前更适合当 `volume confirmation / support-flip / higher-low` 的规则化参考，而不是 replication shortlist。最小 clean-room 入口应是“先测放量 breakout + 3 根内 support-flip / higher-low 是否明显压低 15m 假突破”。
  - 最新补充：已为 `Wiśniewski (2024)` 补最小 audit——全文可得、结构启发很贴当前主线，但本质仍是 BTC/ETH 周频案例研究，没有系统化大样本回测、缺成本/OOS，也未见公开代码；因此当前更适合当 `third-touch confirmation + EMA/MACD confluence` 的规则化参考，而不是 replication shortlist。最小 clean-room 入口应是“先测第三次确认后的 breakout，是否比 first-cross + 无共识过滤更少假突破”。
  - 至少判断：
    - 结构定义是否清楚
    - 回测口径是否足够可读
    - 是否存在未来函数 / 重绘嫌疑
    - 样本是否过薄
    - 是否有交易成本讨论
    - 是否能 clean-room 重写
    - 是否能拿到全文（若不能，默认降为弱证据）
    - 是否存在明确的本地复现入口（数据字段、事件定义、回测步骤）
  - 若不能明确写出最小复现入口，默认不进入高优先级 shortlist。
  - 若材料与当前主线直接相关，额外标记它更接近服务哪一类：
    - `event source design reference`
    - `validation metric / protocol reference`
    - `confirmation / retest / filter reference`
    - `clean-room replication candidate`

- [x] 给每个候选打一个最小状态标签：
  - 已为当前种子来源卡补齐 `evidence_status` 与 `fulltext_access`；当前已覆盖 `read / digest_done / deep_dive_done / replication_candidate / parked` 等最小状态，便于后续 shortlist 直接按状态筛选。

### E3. Replication shortlist（复现 shortlist）

#### E3-A. shortlist 机制

- [x] 从 intake queue 中选出第一批 `3~5` 个 **replication candidates**。
  - 已在 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md` 新增 `第一版 replication shortlist（2026-03-13）`，当前先收口为 4 个对象：`Svogun 2022`（成本/regime 约束）、`pytrendline`（event-source bridge）、`trendln`（geometry/channel baseline）、`Optimal Stopping`（confirmation/retest 机制候选）。
  - 当前明确不进 shortlist：`Chan 2022`（已 park）、`Jiang/Kelly/Xiu 2023`（理论价值高但当前不适合直接 faithful replication）、`Ed Nunez blog`（工程背景材料）。
- [x] 为每个 replication candidate 产出一张 **replication brief**。
  - 当前已落地：
    - `Chan 2022 · S/R Feature Replication Report`（已收口为 reference，不再继续 active replication）
    - `Svogun 2022 · Cost/Regime Replication Report`
    - `Svogun 2022 · Cost/Regime Experiment v1`
    - `Trendline Replication Briefs` 已新增 `pytrendline` 的 active bridge brief
    - `Trendline Replication Briefs` 已新增 `Optimal Stopping` 的 mechanism brief
    - `Trendline Replication Briefs` 已新增 `trendln` 的 geometry baseline brief
  - shortlist v1 当前已实现 brief 全覆盖。
  - 最新补充：已把 `Gurrib et al. (2022)` 追加成 `secondary mini brief`，方便后续直接做 15m `裸 pullback vs confirm-1bar vs confirm-2of3 vs retest-hold` 的最小 clean-room 对照；当前仍不升为 shortlist 主候选。
  - 最新补充：该 mini brief 现已固定 `causal swing protocol v1`——pivot 需 `2-bar right confirmation` 才正式可见，回撤位只能由最近一对已确认 opposite swings 生成，且已形成的交易候选不允许被后来才确认的新 swing retroactively 重写。
  - 最新补充：已对 `Gurrib et al. (2022)` 做第一刀本地验证切片（BTC/ETH/SOL，15m，60d，24-bar hold，10bps round-trip cost，`baseline / confirm_1bar / confirm_2of3`）。当前结果：`confirm_1bar / confirm_2of3` 都能把 `12-bar invalidation ratio` 从约 `51.3%` 压到约 `32.3% / 31.0%`，但整体净收益仍未转正；其中 `confirm_2of3` 是三者里最不差的一档（mean net return 约 `-0.031%`），说明它更像“能改善假信号但还没救活 alpha”的 confirmation/filter 候选，而不是已成立的独立 alpha。
  - 最新补充：已继续补跑 `retest_hold`（同样 BTC/ETH/SOL，15m，60d）。当前四档对照里，`retest_hold` 的聚合表现最不差：mean net return 约 `-0.024%`、win ratio 约 `45.6%`、`12-bar invalidation ratio` 约 `37.1%`；它不像 `confirm_2of3` 那样把 invalidation 压到最低，但在“少被打脸”和“少亏一点”之间给出了更均衡的 trade-off。当前最诚实判断仍然是：Fibonacci 更像 `confirmation / filter candidate`，还不是可独立成立的 alpha；但若后续要继续这条线，`retest_hold` 比 `confirm_1bar` 更值得优先保留。
  - 最新收口（2026-03-14）：已完成 `support_breakout_raw @ h24` vs `breakout + Fibonacci retest_hold` 的小闭环 A/B。结果显示：v0 breakout 口径约 `48` 笔、平均单笔 `+1.44%`、累计 `+92.45%`；叠加 Fibonacci 过滤后约 `29` 笔、平均单笔 `+0.71%`、累计 `+20.00%`，且平均入场延迟拉长到约 `12.5` 根 bar。当前正式结论是：`support_breakout_raw @ h24` 可先保留为 **条件性 alpha / v0 原型**（尤其更适合 `flat` 与次之的 `down` 环境），而 Fibonacci `retest_hold` 降级为 **optional filter candidate / archived idea**，这条研究线到此收口，不再继续作为主 alpha 方向。
  - 当前新增的最小实验结论：
    - `Chan 2022`：方向有启发，但缺方法细节与官方代码，当前先收口，不再继续 faithful replication；
    - cost 的确会把 breakout / trend baseline 的均值与胜率进一步压低；
    - regime（bubble proxy）也会显著重排表现，因此后续 breakout 主线默认应报告 gross / net / regime split。
  - 最小字段：
    - 核心假设
    - 原始事件定义
    - 我们准备怎样 clean-room 复现
    - 需要哪些数据 / 字段 / 适配层
    - 成功标准是什么
    - 风险是什么

#### E3-B. clean-room 复现入口

- [x] 规定：外部材料进入正式实现前，默认先做 **clean-room replication brief**，不直接搬代码。
  - 已在 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md` 的使用规则与 `reports/site/reading/trendline_replication_briefs/report.html` 中明确固化该口径；当前 `pytrendline` 也已按 bridge brief 而非直接实现交易系统的方式接入。
- [x] 明确哪些候选更适合：
  - mainline event source
  - feature candidate
  - filter / confirmation
  - 纯 explainability reference
  - 已在 `reports/site/reading/trendline_replication_briefs/report.html` 新增 `候选角色对照（对应 E3-B）`：当前明确 `pytrendline -> mainline event source`，`Chan 2022 -> feature candidate`，`Svogun 2022 / Optimal Stopping -> filter / confirmation`，`trendln / Ed Nunez blog -> pure explainability reference / geometry baseline`。

#### E3-C. factor intake gate（复现成功后的入库口）

- [x] 定义一个最小 `factor intake gate`，用于判断外部 replication candidate 何时可以进入本地因子库候选。
  - 当前已固定 `factor intake gate v1`，要求候选至少明确回答 5 件事：
    1. 核心事件 / 因子定义是否已 clean-room 明确；
    2. 是否已有最小本地验证结果（event study 或 MVP backtest）；
    3. 是否已报告样本量与最小统计口径；
    4. 是否已报告至少一个现实约束切片（交易成本/滑点、OOS、rolling、跨资产 中至少一项）；
    5. 当前更适合 `alpha candidate / feature candidate / filter candidate` 中哪一类。
  - `gate v1` 的默认决策纪律：
    - 5 项里若第 1 / 2 任一缺失：仍留在 `reading/`，不能进 `factors/`；
    - 若 1~4 全齐，且角色判断清楚：可以升为“本地候选因子 / candidate factor”；
    - 若本地验证仍只是机制启发或过滤作用，不强行挂成 `alpha candidate`，可诚实标为 `filter candidate` 或 `feature candidate`。
- [ ] 对 shortlist 中最有希望的 `1~2` 个对象，优先推进到 `最小复现 + 最小验证 + factor intake decision`，而不是长期停留在 reading 状态。
  - 最新进度：已先对 `Svogun 2022` 做第一张 `factor intake decision`——当前可进入本地候选库，但角色应诚实标为 `filter candidate`，不是 `alpha candidate`。
  - 最新进度：已基于 `Gurrib et al. (2022)` 的两刀本地验证切片（`confirm_1bar / confirm_2of3 / retest_hold`）做出临时 intake 判断：当前**不**把它升入 `factors/`，仍保留在 `reading/` 侧作为 `confirmation / filter candidate`。原因是它确实能降低快速失效比例，`retest_hold` 也给出四档里最不差的 trade-off，但在 BTC/ETH/SOL 的 15m / 60d / 10bps 成本下，聚合 net return 仍未转正，证据还不够支撑把它升级成“本地候选因子”。
- [ ] 若某个 replication candidate 的本地验证明显为正，则在 `factors/` 下创建对应研究入口，并把它从 `reading/` 的外部候选升级为“本地候选因子”。

### E4. Web deliverables（网页交付）

- [x] 为 `Trendline Alpha Scout` 维护一个固定网页入口：
  - `reading/trendline_alpha_scout/report.html`
  - 当前页已可展示：
    - 当前候选池
    - 正式 shortlist v1
    - 状态标签
    - 下一步推荐复现对象

- [ ] 规定每轮 E 模块产出至少落到网页上的一种形式：
  - scout board 更新
  - replication brief
  - deep dive
  - 带最小复现/验证结论的 research note
  - `quant digest` 仍可保留，但默认只在它能明确推进 shortlist / replication / factor intake 时才算高优先级完成

- [ ] 在网页结构上明确区分：
  - `reading/` = 外部证据与复现候选
  - `factors/` = 我们已做本地验证的研究结果
  - 避免把“别人声称有效”和“我们已经验证有效”混在一起。

---

## SUPPORTING（辅助研究）

- [ ] 审计 Henderson / Jacka / Liu / Maeda 这篇 optimal stopping 论文的可迁移性。
- [ ] 整理一个 **structure-event alpha 的常见坑** 清单。
  - 至少包括：
    - 未来函数
    - 重绘
    - 假突破过多
    - 把 detection / confirmation / execution 混在一起
    - 样本太少却过早下结论
- [ ] 若外部仓库很好，但许可证/来源边界不干净，要单独记录，不直接搬进正式实现。

---

## PARKED（先不做）

- [ ] 把 `parallel channel` 继续当唯一主 alpha thesis 去推进
- [ ] 把 `PyIndicators` 当默认唯一主线继续深化
- [ ] 继续为 `raw PyIndicators breakout` 做泛化优化 / 扩参数 / 扩市场挽救
- [ ] 在未完成 unified event foundation 前，直接写最终策略结论页
- [ ] 一开始就做大规模参数寻优
- [ ] 一开始就做全市场全周期回测
- [ ] 一开始就把多个引擎的事件定义强行混成一套而不注明差异

---

## DONE（重要里程碑，保留精简摘要）

- [x] 已建立 `AUTO_OPTIMIZATION_LOOP.md` 与对应 cron 流程。
- [x] 已把自动优化循环改成可从 `docs/TODO.md` 挑选任务，并要求完成后回写 `[x]`。
- [x] 已明确：项目上位主线应改为 **Structure-Event Alpha Research**。
- [x] 已明确：`parallel channel` 当前先降级为候选研究分支，而不是唯一主线。
- [x] 已完成 `pytrendline_research` explainability baseline v1 主要建设。
- [x] 已完成 `PyIndicators` baseline engine 的一系列回测与审计，并得到“整体偏弱、只在少数 subset 可继续”的关键中间结论。
- [x] 已修复站点发布流程，`reports/artifacts/...` 可随站点正确发布。
inability baseline v1 主要建设。
- [x] 已完成 `PyIndicators` baseline engine 的一系列回测与审计，并得到“整体偏弱、只在少数 subset 可继续”的关键中间结论。
- [x] 已修复站点发布流程，`reports/artifacts/...` 可随站点正确发布。
�系列回测与审计，并得到“整体偏弱、只在少数 subset 可继续”的关键中间结论。
- [x] 已修复站点发布流程，`reports/artifacts/...` 可随站点正确发布。
ts/artifacts/...` 可随站点正确发布。
�中间结论。
- [x] 已修复站点发布流程，`reports/artifacts/...` 可随站点正确发布。
ts/artifacts/...` 可随站点正确发布。
��，`reports/artifacts/...` 可随站点正确发布。
ts/artifacts/...` 可随站点正确发布。
�中间结论。
- [x] 已修复站点发布流程，`reports/artifacts/...` 可随站点正确发布。
ts/artifacts/...` 可随站点正确发布。
�布。
ts/artifacts/...` 可随站点正确发布。
��，`reports/artifacts/...` 可随站点正确发布。
ts/artifacts/...` 可随站点正确发布。
�中间结论。
- [x] 已修复站点发布流程，`reports/artifacts/...` 可随站点正确发布。
ts/artifacts/...` 可随站点正确发布。
