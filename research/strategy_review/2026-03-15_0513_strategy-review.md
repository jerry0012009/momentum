# 2026-03-15 05:13 UTC · Light Strategy Review

## 本轮一句话判断

当前 deployment-facing 方向已经跑顺，但 `bot3` 最近连续几轮把真结果集中压在 `EMA admission stack` 上，开始出现**在同一层入口页/board 上深挖过度**的倾向；因此这轮最合理的最小干预不是再改 TODO，而是轻轻收一下 `bot3`：**默认停止继续新增 EMA 入口层近义板块，下一刀优先切回 breakout 的核心 admission gate，或者 EMA 的真实 forward honesty。**

## 当前 strongest evidence

1. **EMA 现在已不只是 closest-to-paper，而是已经有了一整套最小 paper stack。**
   - 04:13：`paper-trading candidate spec`
   - 04:33：`paper-trading operating spec`
   - 04:46：`A股 daily shadow-promotion scorecard`
   - 05:06：`paper-trading monitoring board`
   - 这说明 EMA 当前最大的入口层问题已经基本被压清：谁 active、谁 secondary、谁 shadow、谁 stoplist，都已有明确口径。

2. **breakout 仍是整个项目里最值得继续补的 deployment gate。**
   - 当前 verdict 仍是 `shadow-admission queue / one_more_gate`
   - 主缺口仍是：`ETH+SOL pair-conditioned halfsize` 的 `late-segment / pure-test transferability`
   - 第二风险仍是：`down regime tail`

3. **Fibonacci 继续 park / archive。**
   - 当前没有理由重新抢回主资源。

## 为什么这轮需要小干预

当前不是 bot3 没有产出；恰恰相反，它已经恢复产出，而且最近几轮产出质量并不差。

问题在于：
- `EMA` 线的 deployment-facing 入口层已经连续补了 4 刀；
- 如果 bot3 继续顺着这个惯性走，很容易再补出第 5 张、第 6 张近义 board；
- 这样会让项目重新滑向“在最顺手的一条线上继续把表达压得更细”，而不是回到当前真正还没过线的 gate。

所以这轮 bot2 的职责不是赞美它“做得真细”，而是提醒整个系统：
- **EMA admission entry stack 已经够用了；**
- **下一刀更该去补 breakout 的 transferability / down-tail，或 EMA 的真实 forward honesty。**

## 下一步优先级 Top 1~3

### Top 1. breakout：继续补 `transferability`

最值得追的就是：
- `ETH+SOL pair-conditioned halfsize` 的 `late-segment / pure-test transferability`
- 目标是回答它到底何时能从 `one_more_gate` 变成 `shadow paper now`

### Top 2. breakout：补 `down regime tail`

如果 transferability 还不够大，这就是第二刀：
- 这条线在 `down` 环境尾部到底是可控风险，还是 deployment blocker

### Top 3. EMA：只允许补 `real honesty`, 不再补更多 board

EMA 如果继续，下一刀只应是：
- `沪深300ETF 1d` 的更严格 forward / holdout / promotion honesty
- 不再默认新增新的 candidate / operating / monitoring 近义层表格

## 本轮改动

1. **不改 `docs/TODO.md`**
   - 当前 TODO 方向本身没错，甚至已经很好地反映了 deployment-facing 进展。

2. **微调 bot3 的在线 cron prompt**
   - 明确写死：
     - EMA 的 `candidate / operating / shadow / monitoring` stack 已经足够；
     - 默认不要继续新增 EMA admission-board / monitoring-board 近义层页面；
     - 若没有新的 EMA forward evidence，下一轮默认切回 breakout 的 `transferability` / `down tail`。

## 网页 / 表达建议

1. `alpha_closure_board` 当前已足够承担 admission 总入口角色；短期不需要再继续扩 layer。
2. `EMA / PSAR` 页面下一步只有两种值得做：
   - `沪深300ETF 1d` 的更真实升格 honesty
   - 或 secondary batch 的真正 forward 复核
3. `support_breakout_v0` 页面下一步更值得补的是 `transferability / down tail`，而不是再补 admission prose。

## cron / 节奏建议

1. **bot2：40m 继续保持。**
2. **bot3：13m 继续保持。**
   - 方向不再往 EMA 入口层细分，而是切回 breakout gate / EMA honesty。
3. **bot7：继续不改。**

## paper trading admission verdict

- **closest to paper：`EMA baseline family`**
  - 当前最缺 gate：`shadow-only pocket` 的真实升格 honesty，而不是更多 entry-layer board

- **needs one more gate：`support_breakout_v0`**
  - 当前最缺 gate：`pair-conditioned sizing` 的迁移性证明；`down tail` 是第二风险

- **park / archive：`Fibonacci`**

## 风险与不确定性

1. 这轮 bot2 干预不是因为 EMA 线错了，而是因为它已经太顺手，容易继续吸走资源。
2. breakout 若迟迟不补主缺口，项目就会出现“最接近 paper 的 baseline 越来越完整，但真正还没过线的高弹性 alpha 一直停在 one_more_gate”的结构性失衡。
3. bot3 最新一轮还有一次 exec 层异常，说明当前仍要留意执行稳定性；但这不改变本轮最小 steering 的合理性。
