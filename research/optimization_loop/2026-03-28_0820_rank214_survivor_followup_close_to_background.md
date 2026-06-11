# Rank 214 / XS relative-strength full-stack baseline survivor follow-up → keep P1 后转 background

- Time: 2026-03-28 08:20 UTC
- Target: `Rank 214 / XS relative-strength full-stack baseline`
- Action: 做唯一一次 survivor follow-up；不再泛泛比较所有增量层，而是直接回答这套 `baseline shell` 接上当前 desk 最有信息量的增量件后，是否还能以**独立前排对象**身份升到 `P2`
- Verdict: `keep_P1 后转 background`

## 本轮回答的问题
`Rank 214` 留下来的价值到底是：
1. 一条值得自己升到 `P2` 的前排主线对象；还是
2. 一个已经完成任务的 `baseline shell`，其最有信息量的增量件其实已经在别的前排对象里被更诚实地承接？

## 这轮用的最小证据
我没有再造一版重复回测，而是直接对照当前 runtime 里已经最有信息量、且和 `Rank 214` 目标最贴近的三类增量件状态：

1. **`jump-veto` 已经被更诚实地接到了同类 XS baseline 上，而且已经形成独立前排对象 `Rank 213`**
   - `2026-03-28_0729_rank213_survivor_followup_promote_p2.md` 已经回答：
     - 在 `30` 币 liquid alt-perp universe 上，plain XS momentum 的核心 failure mode 确实是 **short-leg single-name jump concentration**；
     - `short-leg jump veto` 相比 `short cap` / `inverse-vol` 给出最明显的成本后改善；
     - 因此这条线已经从 `P1` 升到 `Active P2`。
   - `2026-03-28_0811_rank213_p2_admission_parameter_time_honesty_keep_p2.md` 又进一步确认：
     - 同一对象在 `24` 组 parameter/time 网格里有 `23/24` 组成本后为正、`19/24` 组相对 plain 改善；
     - 说明 `jump-veto` 不是单点 lucky hit，而是已经够格成为独立 admission 主线。

2. **`rel-volume` 当前还没有证明自己是能把 baseline 升成 P2 的那层 decisive increment**
   - `2026-03-28_0608_return-relvol-xs-momentum-alpha.md` 已明确写出更长的 Binance Spot `15m` transfer check：
     - 最优 pocket 大致 `k=24, maL=48, rebalance=16 bars`；
     - gross 只剩 `+0.09 bps/bar`；
     - 扣 `4 bps` 后转为 `-0.09 bps/bar`；
     - 当前更像 **feature candidate / quality gate**，而不是可直接升格的 standalone alpha。
   - 这意味着把 `rel-volume` 接到 `Rank 214` 上，本轮并没有比 `jump-veto` 更强、也没有更独立的新 front-slot 身份。

3. **`sentiment` 仍主要是慢变量 gate，不是会把这条 baseline 单独推到 P2 的主增量件**
   - `2026-03-28_0521_xs-momentum-inversevol-lowsentiment-alpha.md` 与 `Rank 212` follow-up 已经收口：
     - `sentiment` 更像 regime / gate，而不是 XS momentum 的主 alpha 本体；
     - `inverse-vol + low-sentiment` 这条线在更诚实 transfer 下没有升到 `P2`，已经退回 background。

## 本轮真正改变的系统认知
`Rank 214` 的 survivor follow-up 最诚实的答案不是“再把 baseline 壳本身也推成一个新的 `P2`”，而是：

> **这套 full-stack baseline shell 的研究任务已经完成。它成功提供了一个可复用底座；但当前最有信息量、最配得上前排资源的增量件是 `jump-veto`，而这部分已经被 `Rank 213` 作为独立对象吃掉。**

换句话说：
- `Rank 214` **有价值**，因为它把 `ranking / rebalance / sizing / cost` 的 baseline 骨架钉死了；
- 但它 **不再有必要继续占用前排 survivor / P2 名额**，因为：
  - `jump-veto` 主线已由 `Rank 213` 继承并进入 `Active P2`；
  - `rel-volume` 目前更像 feature，不够单独升格；
  - `sentiment` 目前更像 gate，不够单独升格。

## 为什么不是 promote_P2
- 若把 `Rank 214` 升到 `P2`，它和 `Rank 213` 的前排身份会高度重叠：都是“XS momentum baseline + 当前最有信息量的增量件”。
- 但 `jump-veto` 这条更强的实现路径已经有正式 rank、正式 artifact、正式 `Active P2` 槽位。
- 让 `Rank 214` 再升一次，本质是在把**baseline 壳**和**已独立成型的最优增量件对象**重复计入前排，属于低杠杆重复，而不是新增系统认知。

## 为什么不是 drop_to_background
- 它不是无价值对象；相反，它对 desk 留下了一个稳定结论：
  - `XS momentum raw alpha` 需要一个诚实的 full-stack baseline；
  - 后续增量件应该接在这个壳上比较，而不是空中加 filter。
- 因此最诚实的位置不是“彻底丢弃”，而是：
  - 保留 `keep_P1` 的知识价值；
  - 退出前排运行槽位，回到 background 作为基线素材。

## Runtime implication
- `Rank 214` 的唯一 survivor follow-up 已用完，不能再继续保留在 `Surviving candidate slot`。
- 当前最有信息量的前排 XS baseline 增量主线仍是 `Rank 213 / large-cap XS momentum × short-leg jump veto`。
- `Rank 214` 应记为：**baseline shell 已验证其研究价值，但其 front-slot 任务已被 `Rank 213` 接续，因此本轮 `keep_P1 后转 background`。**

## Result sentence
`Rank 214 / XS relative-strength full-stack baseline` 的唯一 survivor follow-up 已诚实收口：这套 full-stack shell 证明了它适合作为 XS momentum 的统一 baseline，但当前最有信息量、足以占用前排资源的增量件只有 `jump-veto`，且该主线已由 `Rank 213` 独立承接并进入 `Active P2`；`rel-volume` 仍更像 feature、`sentiment` 仍更像 gate，因此 `Rank 214` 本轮应记为 `keep_P1 后转 background`，不再单独升 `P2`。
