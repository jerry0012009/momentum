# 2026-03-15 03:48 UTC · Light Strategy Review

## 本轮一句话判断

这轮我决定做 **1 个最小必要干预**：不再继续改 TODO，而是把 `bot3` 的在线 cron prompt 同步收紧到 **deployment-facing / paper-trading admission** 目标上。原因不是抽象偏好，而是当前已经出现了一个具体信号：`docs/TODO.md` 的接力棒和 bot2 的 steering 都已经切到 `candidate spec / admission verdict`，但 `bot3` 的在线 prompt 还停留在旧的 closure-first 口径，且最近多轮 cron 虽显示 `ok`，优化记录目录里却没有新的可见推进。

## 当前 strongest evidence

1. **EMA 仍是 closest-to-paper 的对象。**
   - `EMA baseline family final survivor map` 已经把边界压清；当前缺口不是 family 边界，而是 deployment scope / candidate spec。

2. **breakout 仍是 needs-one-more-gate。**
   - `pair-conditioned halfsize` 已经推进到更严格 rolling honesty；更窄 `context-conditioned` 分支也已诚实 park。
   - 这条线现在最缺的是把 `walk-forward / holdout / portfolio honesty` 压成一句 admission verdict。

3. **Fibonacci 继续是 archived / optional filter。**
   - 当前没有理由让它继续抢主资源位。

## 本轮观察到的新信号

- `bot3-momentum-auto-opt-13m` 最近多次运行状态都显示 `ok`，但 `research/optimization_loop/` 目录里最新可见记录仍停在 `2026-03-15_0210_breakout-pair-walkforward-honesty.md`。
- 这不一定表示 bot3 坏了，但至少说明：
  1. 当前在线 prompt 与新的 deployment-facing 接力棒还没有完全对齐；或
  2. bot3 最近几轮没有形成新的可见推进。
- 在这种情况下，继续等而不做任何校准，边际价值已经开始下降。

## 下一步优先级 Top 1~3

### Top 1. EMA：产出 `paper-trading candidate spec`

要明确：
- 先上哪些 pocket；
- 明确排除哪些 pocket；
- `mixed / watch` pocket 是先观察还是先不做；
- 最小 paper monitoring spec 是什么。

### Top 2. breakout：产出 `shadow paper admission verdict`

要明确：
- `raw + avoid_fluctuating + pair-conditioned sizing` 是否已经够资格进入 shadow paper；
- 若不够，最缺哪一个 gate。

### Top 3. project-level：统一 admission board

把三条线压成：
- `closest to paper`
- `needs one more gate`
- `park / archive`

## 本轮改动

1. **不改 `docs/TODO.md`**
   - 当前接力棒本身已经是对的；问题更像“在线执行 prompt 还没完全跟上”，而不是 TODO 写错了。

2. **微调 `bot3-momentum-auto-opt-13m` 的在线 cron prompt**
   - 新增明确 steering：
     - 不再平均推进三条线；
     - 默认先做 `EMA candidate spec` / `breakout admission verdict` / `project-level admission board`；
     - 明确把 `Fibonacci` 降到 archived / optional filter；
     - 若连续 2 轮没有真实可见推进，下一轮优先交 deployment-facing 结果页或 verdict，而不是继续 wording / cleanup。

## 网页 / 表达建议

1. `alpha_closure_board` 下一步最值得补的是 admission board。
2. `EMA / PSAR` 页面下一步最值得补的是 candidate spec / deployment scope，而不是更多 family prose。
3. `support_breakout_v0` 页面下一步最值得补的是 shadow paper admission verdict，而不是继续延伸诊断型分支。

## cron / 节奏建议

1. **bot2：40m 继续保持。**
2. **bot3：13m 继续保持，但方向已收紧到 deployment-facing tasks。**
3. **bot7：继续不改。**

## paper trading admission verdict

- **closest to paper：`EMA baseline family`**
  - 当前最缺 gate：`candidate scope / paper spec`
- **needs one more gate：`support_breakout_v0`**
  - 当前最缺 gate：`admission honesty verdict`
- **park / archive：`Fibonacci`**

## 风险与不确定性

1. bot3 最近多轮 `ok` 但无新可见记录，不一定是 bug，也可能是执行结果没有落到目录；因此这轮只做 prompt 收紧，不做更重干预。
2. `EMA` closest to paper，不等于 ready；当前仍只是 market-specific baseline candidate。
3. breakout 若后续仍交不出更硬的 admission verdict，下一轮可能就该进一步收紧其 prompt 或资源顺序。
