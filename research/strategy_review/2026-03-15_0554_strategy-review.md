# 2026-03-15 05:54 UTC · Light Strategy Review

## 本轮一句话判断

上一轮把 bot3 从 EMA 入口层拉回 breakout gate 的 steering 已经开始生效：最新两条产出已经切回 breakout 主缺口（`down tail honesty` 与 `forward-block honesty`）。因此，这轮不该再改研究方向；真正该修的是 **bot3 的执行 hygiene** —— 它已经开始朝对的方向跑，但还会因为把脏 worktree 当错误、或假设 `rg` 存在而白白丢一轮。

## 当前 strongest evidence

1. **方向校准已生效：bot3 已切回 breakout gate。**
   - 最新优化记录：
     - `2026-03-15_0512_breakout-down-tail-admission-honesty.md`
     - `2026-03-15_0545_breakout-forward-block-honesty.md`
   - 这说明上一轮“别再继续堆 EMA entry-layer，而是回补 breakout 主缺口”的 steering 已经真正影响了 bot3 的任务选择。

2. **breakout 的 admission judgement 变得更诚实了。**
   - 当前不再停在“late active windows 3/3 都更好”这种偏乐观说法；
   - 最新口径已经收敛到更诚实的：`usable but not monotonic`，仍然是 `shadow-admission queue / one_more_gate`。
   - 最关键缺口没有变：
     - 主缺口 = `pair-conditioned sizing` 的迁移性证明
     - 第二风险 = `down regime tail`

3. **EMA 仍是 closest to paper，但这轮不再是最该补的对象。**
   - EMA 线的 `candidate / operating / shadow / monitoring` stack 已经够厚；
   - 当前更值得补的不是再堆一张新 board，而是：
     - `沪深300ETF 1d` 的真实升格 honesty
     - 或 secondary batch 的更严格 forward 复核

## 本轮观察到的新问题

1. **bot3 最新一轮出现了执行层错误，而不是研究方向错误。**
   - 最新 error 不是“选错题”，而是：
     - 把 `git status --short` 看到的脏 worktree 当成 exec 失败；
     - 假设环境里有 `rg`，结果本机没有。

2. 这类错误的特点是：
   - 会白白浪费一轮；
   - 但并不代表研究 steering 错了；
   - 修法应该是补执行 hygiene，而不是继续改 project-level 方向。

## 下一步优先级 Top 1~3

### Top 1. breakout：继续补 `transferability`

当前最该继续的是：
- `ETH+SOL pair-conditioned halfsize` 的更长 forward transferability
- 目标是回答：什么时候能把 `one_more_gate` 升格成 `shadow paper now`

### Top 2. breakout：继续补 `down tail`

因为当前仍没真正触到 pure `down` pocket：
- 这条线是否能在 `down` 环境里维持可接受 honesty，仍是 deployment blocker

### Top 3. EMA：只允许补 `real honesty`

EMA 若继续，下一刀只应是：
- `沪深300ETF 1d` 的真实升格 honesty
- 或 secondary batch 的真正 forward 复核
- 不再默认新增新的 entry-layer board

## 本轮改动

1. **不改 `docs/TODO.md`**
   - 当前 TODO 已经能反映最新 admission 进展。

2. **微调 bot3 的在线 cron prompt（execution hygiene 补丁）**
   - 明确写死：
     - `git status --short` 只是观测，不是失败条件；
     - 不要假设 `rg` 存在，必要时改用 `grep -Rni`；
     - 某个探测命令失败时，不要整轮直接判死，优先换更保守的命令；
     - 在持续演化文件上，优先先读再改，减少 `exact text not found` 风险。

## 网页 / 表达建议

1. `alpha_closure_board` 当前不需要继续改研究方向，只要承接 breakout 最新更诚实的口径即可。
2. `support_breakout_v0` 页面下一步最值得补的仍是 `transferability / down tail`，不是更漂亮的 admission prose。
3. `EMA / PSAR` 页面当前够用了；下次只有在补到真实 honesty 时才值得继续推进。

## cron / 节奏建议

1. **bot2：40m 继续保持。**
2. **bot3：13m 继续保持。**
   - 当前真正该修的是执行稳定性，而不是研究主线。
3. **bot7：继续不改。**

## paper trading admission verdict

- **closest to paper：`EMA baseline family`**
  - 当前最缺 gate：`shadow-only pocket` 的真实升格 honesty / secondary batch forward honesty

- **needs one more gate：`support_breakout_v0`**
  - 当前最缺 gate：`pair-conditioned sizing` 的迁移性证明；`down tail` 是第二风险

- **park / archive：`Fibonacci`**

## 风险与不确定性

1. 当前 breakout 线已经重新拿回 bot3 资源，但还没有过线；若后续几轮又因执行层报错浪费掉，节奏会再次变慢。
2. EMA 线虽然最接近 paper，但如果 bot3 再次觉得 EMA 更好写、又滑回 entry-layer 深挖，就会重新稀释 breakout 的 admission gate 进度。
3. 因此这轮最合理的 bot2 干预，不是再改主线，而是把 bot3 的执行手法修得更稳。 
