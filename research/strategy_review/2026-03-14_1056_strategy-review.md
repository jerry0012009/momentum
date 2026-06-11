# 2026-03-14 10:56 UTC · Light Strategy Review

## 本轮一句话判断

这轮的核心问题不是三条收口线方向漂移，而是 **bot3 的“可见产出纪律”不够强**：过去约 2~3 小时里，cron 状态显示它持续被触发且 `lastRunStatus=ok`，但 `research/optimization_loop/` 下没有对应时段的新记录文件。为避免继续出现“看起来在跑，但看不到它到底干了什么”的情况，本轮对 bot3 做了一个最小必要修正：**每轮必须留下真实产物，或者明确留下 `NO_PROGRESS` 记录。**

## 当前 strongest evidence

1. **bot3 确实在运行，但可见产物不匹配当前频率**
   - 当前 `bot3-momentum-auto-opt-15m` 的 cron 状态显示：
     - 最近一次运行：`2026-03-14 10:48 UTC`
     - `lastRunStatus=ok`
     - 运行时长约 `46.7s`
   - 但 `research/optimization_loop/` 下最近的可见记录仍停在：
     - `2026-03-14_0706_psar-role-framing.md`
   - 这意味着：它至少“被唤醒并成功结束”了，但不能证明它最近几轮都留下了可见推进成果。

2. **bot3 的方向 prompt 仍然是对的**
   - 当前 prompt 仍明确要求：
     - 从 `docs/TODO.md` 中挑任务；
     - 只做三条收口线相关的小步；
     - 不 reopen `v3`；
     - 写 `optimization_loop` 记录；
     - 发简短邮件；
   - 所以问题不在“方向错误”，而在“产物纪律不足”。

3. **closure-first 的项目主判断仍然没变**
   - `EMA / PSAR` 仍是最像继续往策略层走的对象；
   - `breakout-short follow-up` 仍应沿 `support_breakout_v0` + `avoid_fluctuating` 继续；
   - `Fibonacci` 仍应继续按收口说明处理。

## 当前 weakest / should-fix-now

1. **bot3 最近存在“ok 但无可见结果”的风险**
   - 这会让 Jerry 无法判断：
     - bot3 是真的推进了，
     - 还是只做了检查然后结束。
   - 这个问题当前已经比“是否再微调 TODO”更值得修。

2. **当前不该继续只观察而不加 guardrail**
   - 前几轮 bot2 一直在轻量观察；
   - 但现在已经积累出足够证据，说明需要一个最小约束来提升可审计性。

## 建议优先级 Top 1~3

### Top 1. 观察 bot3 新 guardrail 是否真的生效
- 关注下一批 15m 轮次是否出现：
  - 新 `optimization_loop/*.md` 文件；
  - 或明确的 `NO_PROGRESS` 记录；
  - 与之对应的简短邮件。

### Top 2. EMA baseline 的成本 / OOS honesty
- 这仍是最像直接改变研发决策质量的主任务。

### Top 3. breakout-v0 × avoid_fluctuating 的最小 A/B
- 这仍是 breakout-short follow-up 最自然的下一刀验证。

## 本轮改动

### 已改

- **微调 `bot3-momentum-auto-opt-15m` 的实际 cron prompt**：
  - 新增硬约束：
    - 每轮必须留下一个 durable artifact；
    - 要么是真实推进记录；
    - 要么是明确的 `NO_PROGRESS` 记录；
    - 不允许“只检查一下然后安静结束”且不留下任何可见痕迹。

### 本轮未改

- 不改 `docs/TODO.md`
- 不改 `docs/ROADMAP.md`
- 不改 bot2 / bot7

原因：
- 当前最主要的问题已经足够明确，就是 bot3 的可审计性；
- 这轮优先修这个，不再额外引入更多变量。

## 网页/表达建议

1. 这轮不做网页改动；
2. 等 bot3 新 guardrail 跑过一轮后，再看是否需要在 closure 页中补“最近一次 bot3 推进了什么”的轻量提示。

## cron / 节奏建议

1. **bot3-auto-opt-15m：先不降频，先看新 guardrail 是否让它变得可审计**
   - 如果后续仍连续多轮只留下 `NO_PROGRESS`，再考虑把频率从 15m 调回 30m 或 40m。

2. **bot2-strategy-review-40m：继续保持**
   - 当前 bot2 的价值之一，就是像这轮这样识别“不是研究方向错了，而是执行纪律要补”。

3. **bot7-quant-digest-4h：继续保持**
   - 这轮不动它。

## 风险与不确定性

1. bot3 最近没有可见新日志，不等于它完全没做事；但就审计角度看，当前证据不足以证明它每 15m 都有真实推进。
2. 新 guardrail 可能会暴露出另一个事实：15m 频率下确实经常“没有值得动手的小步”；若连续出现这种情况，下一步就该调频，而不是怪 agent 不干活。
3. 当前三条收口线本身的优先级判断没有变；本轮修的是执行层可见性，而不是研究层结论。
