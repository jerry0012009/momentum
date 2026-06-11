# 2026-03-14 11:36 UTC · Light Strategy Review

## 本轮一句话判断

这轮的主判断仍不是研究方向漂移，而是 **bot3 的可审计性还需要再收紧一格**：上轮已经要求它“每轮必须留下真实产物或 `NO_PROGRESS` 记录”，但本轮复核时，cron 状态显示 bot3 仍在 `2026-03-14 11:33 UTC` 正常运行、`lastRunStatus=ok`，而 `research/optimization_loop/` 下仍未看到对应时段的新文件。因此，这轮继续做了一个更明确的最小修正：**若无推进，必须显式落一个 `YYYY-MM-DD_HHMM_no-progress.md` 文件，并在首行写 `NO_PROGRESS: <中文原因>`。**

## 当前 strongest evidence

1. **bot3 确实持续运行**
   - 当前 cron 状态显示：
     - 最近一次运行：`2026-03-14 11:33 UTC`
     - `lastRunStatus=ok`
     - 最近运行时长约 `19.8s`
   - 所以问题不是“bot3 没被触发”。

2. **但可见产物仍然没有跟上运行频率**
   - `research/optimization_loop/` 的最近文件仍停在：
     - `2026-03-14_0706_psar-role-framing.md`
   - 这说明上轮加的“要留痕”要求，还没有变成足够明确、容易审计的行为约束。

3. **closure-first 的主研究判断仍然没有变化**
   - `EMA / PSAR raw alpha focus` 仍是最像继续往策略层走的对象；
   - `breakout-short follow-up` 仍应沿 `support_breakout_v0 + avoid_fluctuating` 继续；
   - `Fibonacci` 仍继续按收口说明处理。

## 当前 weakest / should-fix-now

1. **bot3 仍存在“ok 但看不到产物”的风险**
   - 这已经不是观察问题，而是审计与信任问题：
     - Jerry 看不到它是否真的在推进；
     - bot2 也无法判断是“没任务可做”还是“没按要求留下记录”。

2. **当前最该补的是显式 `NO_PROGRESS` 文件规范，而不是继续观察**
   - 上轮只要求“留下 `NO_PROGRESS` 记录”；
   - 这一轮进一步把它具体化到文件命名与首行格式，减少模糊空间。

## 建议优先级 Top 1~3

### Top 1. 观察 bot3 新的 `*_no-progress.md` 规范是否真的开始落地
- 关注下一批 15m 轮次是否出现：
  - 新推进文件；
  - 或显式的 `*_no-progress.md`。

### Top 2. EMA baseline 的成本 / OOS honesty
- 这仍是最像直接提升决策质量的主研究动作。

### Top 3. breakout-v0 × avoid_fluctuating 的最小 A/B
- 这仍是 breakout-short follow-up 最自然的一刀策略化验证。

## 本轮改动

### 已改

- **继续微调 `bot3-momentum-auto-opt-15m` 的实际 cron prompt**：
  - 若本轮没有推进，文件名必须显式写成：
    - `research/optimization_loop/YYYY-MM-DD_HHMM_no-progress.md`
  - 且文件第一行必须是：
    - `NO_PROGRESS: <中文原因>`
  - 目的：让 Jerry 和 bot2 后续都能一眼判断：这轮是诚实无进展，而不是无声漏产出。

### 本轮未改

- 不改 `docs/TODO.md`
- 不改 `docs/ROADMAP.md`
- 不改 bot2 / bot7

原因：
- 当前最主要的问题已经足够集中，就是 bot3 的产出可见性；
- 这轮继续只修这一点，不引入更多变量。

## 网页/表达建议

1. 本轮仍不动网页；
2. 等 bot3 真开始稳定留下 `no-progress` / progress 文件后，再考虑是否在 closure board 增加一条“最近一次 bot3 做了什么”的轻量可见入口。

## cron / 节奏建议

1. **bot3-auto-opt-15m：先继续观察，不立刻降频**
   - 先看新文件规范能否解决“跑了但看不见”的问题；
   - 若后续仍连续多轮只留下 `no-progress`，再考虑从 15m 调回 30m 或 40m。

2. **bot2-strategy-review-40m：继续保持**
   - bot2 当前在做正确的事情：不是重写研究方向，而是补执行层可审计性。

3. **bot7-quant-digest-4h：继续保持**
   - 这轮不动它。

## 风险与不确定性

1. bot3 最近没有可见新日志，不等于它完全没做事；但从项目治理角度看，“做了但无痕”与“没做”几乎一样不可审计。
2. 若新 `no-progress` 规范生效后仍显示 15m 频率下经常无事可做，那问题就不再是 prompt，而是频率设置本身。
3. 当前三条收口线的研究优先级本身没有变化；本轮修的是执行可见性，不是研究结论。
