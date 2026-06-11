# 2026-03-23 16:03 UTC · Rank 151 / P2 discussion write-up

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行 = empty`
- 本轮未见 `Interrupt` 级异常
- 顶板 `Next 3 bot3 runs / Run 1 = 把 Rank 151 整理成明确的 P2 discussion write-up`
- 因此本轮不再补第三条 family，不做新的回测扩张；只回答一个最值钱问题：

> `Rank 151` 现在是否已经值得从 `P2 / pre-paper candidate` 继续冲 `P3 / Paper launch queue`？如果还不行，最小 admission bar 是什么？

## 1. 当前证据包（只用已完成事实）

### 主点：shared-gate 证据已经形成
`Rank 151 / EWMAC breakout band-pass gate` 目前已完成的四段证据链：
1. `breakout-short` 首条 family honest gate 通过
   - primary `6bps/side`：`band_pass = +5.55 bps/trade`
   - 对照：`baseline = -3.47`，`hard_positive = -3.62`
   - 三资产方向一致改善
2. `breakout-short` 时间稳定性初检通过
   - uplift 在 `7` 个月里 `5/7` 为正
3. `fib retest` 第二 family 复核通过
   - primary `6bps/side`：`band_pass = +36.36 bps/trade`
   - 对照：`baseline = +11.89`，`hard_positive = -15.52`
   - `10 / 15bps` 成本层仍优于 baseline
4. rolling / split 稳定性通过
   - `breakout-short` uplift：`front_half +9.82` / `back_half +7.94 bps`
   - `fib_retest_long` uplift：`front_half +10.68` / `back_half +32.28 bps`
   - `families_passing_split_check = 2/2`

### 紧邻子点：它解决的不是“强趋势要不要追”，而是“极端对齐分数要不要避开”
两条 family 目前给的是同一个方向：
- `hard_positive` 都不稳，甚至显著差；
- `band_pass` 都优于 baseline；
- 这更像一个 **shared admission filter**，而不是某条 family 的偶然参数 pocket。

换成人话：
- 不是“越强越好”；
- 更像“太极端的对齐分数别追，中段放行反而更诚实”。

## 2. 为什么这已经够进入 P2 discussion
P2 不是要证明“已经可以上 paper”，而是要证明：
1. 候选不再只是单 family 幻觉；
2. 证据已经足够支撑一次是否进 `P3` 的正式讨论；
3. 后续工作应该从“继续找它是不是假的”切换到“它离 launch queue 还差哪一刀”。

`Rank 151` 现在满足前两条：
- 有 **两条 family replication**，不是单点 luck；
- 有 **月度 + split** 两层时间稳定性，不是只靠单月或单半段；
- primary family `breakout-short` 的样本量也不小（`band_pass 1033 trades`，baseline `1727 trades`）；
- 方向上不是“更强趋势筛选更好”，而是两条 family 同时支持同一条 shared-gate 解释。

所以它已经不是 `keep_P1` 语境，而是标准的 **`P2 / pre-paper candidate`**。

## 3. 为什么现在还不能直接升 P3
我这轮的判断：**还不到直接 `promote_P3`。**

原因不是证据弱，而是离 `Paper / 待开启自动运行` 还差最后一块“可部署性”证明：

### blocker A：第二 family 样本偏薄
- `fib retest` 总 trades 只有 `34`，`band_pass` 只有 `20`
- split 后前半只有 `5` 笔、后半 `15` 笔
- 它可以当 replication support，但还不够当 launch 的主承重墙

### blocker B：当前证据仍偏“研究 verdict”，不是“paper operating spec”
要进 `P3`，不只要说明它在研究里成立，还要回答：
- 它应该挂到哪一条现有 family / runner 语境里？
- 最终执行口径是单 family 加 gate，还是 shared overlay 先 shadow？
- 如果给 paper queue，runner 的最小输入/输出和状态页该怎么定义？

### blocker C：缺一个 admission-bar 风险检查
现在已有：
- family honest gate
- 时间稳定性
- split 稳定性

但还缺一个足够便宜、又能直接服务 `P3` 决策的检查，例如：
- 仅在目标 family 上做更严格的 out-of-sample / recent-slice admission bar；或
- 对将来最可能接 paper 的 family，做一次“加入 gate 后 trade density / refresh cadence / runner feasibility”检查。

## 4. authoritative judgment

### 当前层级
- **`Rank 151 = P2 / pre-paper candidate`**

### 本轮不建议的动作
- 不建议继续补第三条 family replication
- 不建议现在就包装成 `P3 / launch queue`
- 不建议把它写成“新 alpha”

### 本轮建议的动作
- 把它当成 **shared gate 预审通过**
- 下一刀只做 **1 个 admission-bar check**，目标不是再证明它“很有意思”，而是决定：
  - `promote_P3`，还是
  - `stay_P2 with explicit blocker`

## 5. 最小 P3 admission bar（建议口径）
我建议把下一轮 admission bar 写得非常窄，避免再次掉回无限研究：

### 方案 A（优先）
只针对最有 deploy 价值的承载 family（当前优先 `breakout-short`）做一次：
- 更近实盘语境的 recent-slice / holdout admission check
- 看 `band_pass` 是否仍在主要成本层保持：
  - 正 uplift
  - 足够 trade density
  - 不把 runner 变成过稀疏的纸面故事

如果这一步通过，`Rank 151` 就有理由升到 `P3 / Paper launch queue`。

### 方案 B（若 A 不适合）
直接写一个很小的 `paper candidate framing`：
- 明确它先挂在哪条 family 上 shadow
- 先做 sidecar / overlay paper，而不是新 seat
- 明确 runner 最小产物（status json / ledger row / refresh clock）

如果 framing 本身都说不清，那就不该进 P3。

## 6. 简短 scorecard
- `shared_gate_evidence = 3/3`
- `time_stability = 3/3`
- `cross_family_consistency = 3/3`
- `deploy_readiness = 2/3`
- `paper_launch_readiness = 2/3`
- `recommended_action = stay_P2_and_do_one_admission_bar_check`
- `why_now = 顶板 Run 1 要的不是再补 replication，而是把已有证据整理成是否继续冲 P3 的明确讨论入口。`
- `main_weakness = fib retest 样本偏薄，且还缺最后一块面向 paper launch 的 admission-bar / operating-spec 证明。`

## 7. 对 desk 的直接影响
1. `Rank 151` 继续保留 `Scout` 主点，而且仍是默认 primary。
2. 它已经配得上 `P2 discussion`，但 **还不是自动进入 P3**。
3. 下一轮如果继续沿 `Rank 151` 主线推进，必须是：
   - `one decisive admission-bar check`，而不是再做同类 replication。
4. 如果 desk 不想继续给 `Rank 151` 追加预算，那么合理状态不是降回 `P1`，而是：
   - `P2 / evidence good but P3 blocker explicit`。

## 8. 一句话结论
`Rank 151` 现在已经足够从“研究上像 shared gate”推进到“值得认真讨论是否进 paper launch queue”的层级，所以 **P2 是成立的**；但它还差最后一块面向 launch 的 admission-bar 证明，因此这轮最诚实的结论不是直接 `promote_P3`，而是：**`stay_P2, do one narrow admission-bar check, then make the P3 call.`**
