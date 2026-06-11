# 别把这条 re-break 结构只读成 price action 形态：对 short-cycle crypto desk，更该先拆的是「回踩后再次跌破 impulse low」这条可直接落地的 short-continuation raw alpha
- 时间：2026-04-19 20:49 UTC
- 类型：内部 validated artifact audit（`rank378` fresh-intake + execution-realism + P2 admission + live paper runner）
- 主题类型：raw alpha
- 基础 alpha：**下破后回踩未修复、并在限定窗口内再次跌破回踩前 impulse low 的短周期延续**；更直白点说，先跌穿、再回踩、再破低，不是“确认过滤器”，本身就是一条 short continuation 入场信号
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/trend/continuation/retest/re-break/short-only/15m/next-open/fixed-hold/capacity/cost/risk/internal-artifacts
- 证据类型：对象级 execution realism + admission exit + frozen paper-runner spec

## 1. 这次看了什么
先回答 base alpha：**这条东西的 base alpha 很清楚，就是 raw alpha，不是 filter / regime / overlay。**

这次不是新翻一篇论文或 GitHub 仓，而是回到已经被 runtime 验证过的一条独立对象：`Rank 378 / retest-window impulse re-break confirmation`。它的值不在“形态描述”，而在它已经被压成了一个很具体的可交易定义：
- 频率：`15m`
- 方向：`short continuation`
- 标的：`BTC / ETH / SOL`
- 事件骨架：先出现 downside breakout，再发生回踩；
- 核心确认：回踩后记录 `pre_retest_impulse_extreme`，要求在 `N=6 bars` 内 **close 再次跌破该 low**；
- 执行：`next-bar open`
- 退出：固定持有 `8 bars`（约 `2h`）
- execution realism：`6 bps/side` 基础摩擦 + 容量 impact proxy；名义规模看 `10k / 50k / 100k USD`

所以它不是那种“看起来像 alpha，但真正落地时没有 entry/exit/cost”的概念卡片，而是已经接近完整策略壳的 raw alpha。

## 2. 核心结论
- **一句话结论：** 这条线最该保留的，不是“回踩确认”四个字，而是 **retest 后窗口内 re-break low 的 short continuation** 这条 base alpha，本身就能独立成策略。
- **一句话证据：** 在 `BTC/ETH/SOL 120d 15m`、`next-open` 入场、`8-bar` 固定持有、`50k USD` 容量口径下，它仍有 **`+0.3469%/trade`** 的净收益，且三资产都为正。

最关键的数据点：
1. **`50k USD` 组合口径**：`27` 笔交易，`avg_net = +0.3469%/trade`，`total_net = +9.64%`，`win_rate = 48.15%`。
2. **扩容稳定性**：`10k / 50k / 100k USD` 下 `avg_net` 分别为 `+0.3605% / +0.3469% / +0.3368%`，扩容后只是温和衰减，没有被容量直接打穿。
3. **跨资产不是单一币幻觉**：
   - `BTC = +0.2485%/trade`
   - `ETH = +0.3902%/trade`
   - `SOL = +0.4346%/trade`
4. **最小 honesty 检查过关**：所有交易 `entry_ts - confirm_ts = 15 分钟`，没有 same-bar 偷看；delayed-confirm 子集 `12` 笔，`avg_net = +0.6616%`。
5. **时间稳定性不是完美，但没塌**：`2025-12` 与 `2026-01` 小幅负，`2026-02` 与 `2026-03` 又转回正，说明它更像 pocket alpha，不是全年无脑开机策略。

## 3. 为什么这轮值得写成新 digest
当前 desk 最近补了不少：
- panic-bounce / oversold-bounce
- loser→winner fade
- carry / funding / pairs / relative-value

但 **“结构性延续”** 这条线，尤其是 **回踩后再破低** 这种可以压成严格因果定义的 short alpha，积累还不够厚。它值得保留有三个原因：
1. **base alpha 直接可讲人话**：跌破、回踩失败、再破低，赌的是延续，不是解释市场。
2. **策略组件已经完整**：entry、exit、cost、capacity、honesty 都不是空白。
3. **和已有 breakout 主题不完全重叠**：不是裸 breakout，也不是 opening range；真正值钱的是“回踩后再破”的确认结构。

## 3.5 策略拆解（必填）
- 方向属性：单资产、short-only、trend/continuation
- 基础 alpha：**回踩失败后的再破低延续**
- regime：更适合已经出现下行动量、且回踩没能把价格拉回 breakout 结构之上的环境
- filter / veto：
  - 不做“回踩后直接修复”的假破位；
  - 不做 `N=6 bars` 内始终没 re-break 的拖沓结构；
  - 若市场进入极端 news squeeze，short continuation 容易被反抽打脸
- risk / sizing / execution overlay：
  - 基础执行是 `next-bar open`
  - 首版 sizing 可先等权 / 定额；
  - 固定持有 `8 bars` 比主观 trailing 更诚实；
  - 容量口径先按 `10k/50k/100k USD` 检查 impact，不要一上来假设无限吃单

## 4. 本地最小快检（完全内部公开 artifact，可复算）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源：项目内公开 artifact（对本 workspace 可直接读取）
- 更新频率：`15m` 策略事件与 paper runner 刷新
- 最小实验口径：
  - 标的：`BTC-USD / ETH-USD / SOL-USD`
  - 时间框架：`15m`
  - 入场：confirm 后下一根 bar open
  - 持有：`8 bars`
  - 核心参数：`N=6` re-break window
  - 成本：`6 bps/side` 基础摩擦 + `18 * sqrt(participation) bps/side` impact proxy
  - 名义规模：`10k / 50k / 100k USD`

### 4.2 这组快检怎么读
- **这不是高胜率信号，靠的是盈亏比与结构筛选。** `win_rate` 只有 `48.15%`，但平均单笔仍明显为正，所以它更像“少做，但做对结构”的 continuation pocket。
- **capacity realism 比想象中稳。** 很多 price-action 题材一压容量就没了，这条线到 `100k USD` 还保留 `+0.3368%/trade`。
- **honesty 是这条线真正值钱的地方。** 既然所有 entry 都晚于 confirm `15m`，那它至少不是靠 lookahead 幻觉挣钱。

## 5. 为什么它是 raw alpha，不只是 filter
因为这里回答的是“具体做什么”：
> **当 downside breakout 之后的回踩没有修复结构，并且在 `6` 根 bar 内再次跌破回踩前 impulse low，就在下一根 open 做空，持有 `8` 根 bar。**

这已经是标准 raw alpha 叙事：
- 信号是什么；
- 入场何时发生；
- 持有多久；
- 成本怎么压；
- 哪些资产能做。

它当然可以再往上叠 regime gate，但那是后续增强，不影响它本身已经是一条独立 raw alpha。

## 6. 下一步怎么测
1. **先做 exit ladder**：比较 `6 / 8 / 10 / 12 bars`，看 `8 bars` 是否真的是最稳 pocket，而不是偶然默认值。
2. **补 stop / take-profit honesty**：对比 `fixed hold` 与 `ATR stop + time stop`，确认是不是可以在不破坏因果的前提下减少坏尾部。
3. **把 BTC / ETH / SOL 扩到 liquid majors**：优先加 `BNB / DOGE / XRP`，看 edge 是结构通用还是只适用于高 beta 三件套。
4. **加 regime veto**：用 funding、OI unwind、或大盘 realized vol 区分“正常延续”与“news squeeze 反杀”。
5. **做 side-by-side 对照**：把“裸 breakout short”与“retest+re-break short”放同一面板，确认 edge 主要来自哪一步。
6. **paper runner live follow-up**：把 `rank378` 的 live snapshot 连续记账，重点看最近 2~4 周是否出现明显衰减。

## 7. 风险与保留意见
- 这条线目前 **样本数不大**，只有 `27` 笔，统计显著性还没到可以自满的程度。
- 它更像 **event pocket**，不是全天候高频供给机；若强行扩 universe 或加频次，可能稀释 edge。
- 本轮证据来自内部 artifact 链，而不是新论文 / 新仓库；好处是更贴近当前 runtime，坏处是学术外部性较弱。

## 8. 来源
1. `research/optimization_loop/2026-04-10_1958_rank378_rank60b_freshintake_first_verdict_keep_p1.md`
2. `research/optimization_loop/2026-04-10_2219_rank378_survivor_followup_execution_realism_promote_p2.md`
3. `research/optimization_loop/2026-04-10_2256_rank378_p2_exit_admission_promote_p3.md`
4. `reports/artifacts/rank378_execution_realism/rank378_execution_summary.json`
5. `reports/artifacts/rank378_execution_realism/rank378_capacity_friction_summary.csv`
6. `reports/artifacts/rank378_execution_realism/rank378_p2_admission_exit_summary.json`
7. `reports/artifacts/paper_rank378_retest_rebreak/rank378_frozen_launch_spec.json`
8. `reports/artifacts/paper_rank378_retest_rebreak/rank378_last_run_summary.json`

## 9. 本地产物
- 执行汇总：`reports/artifacts/rank378_execution_realism/rank378_execution_summary.json`
- 容量/摩擦：`reports/artifacts/rank378_execution_realism/rank378_capacity_friction_summary.csv`
- admission 出口：`reports/artifacts/rank378_execution_realism/rank378_p2_admission_exit_summary.json`
- frozen spec：`reports/artifacts/paper_rank378_retest_rebreak/rank378_frozen_launch_spec.json`
- latest runner summary：`reports/artifacts/paper_rank378_retest_rebreak/rank378_last_run_summary.json`
