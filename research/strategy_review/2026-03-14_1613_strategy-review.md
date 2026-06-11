# 2026-03-14 16:13 UTC · Light Strategy Review

## 本轮一句话判断

这轮继续选择 **不改 TODO / roadmap / cron**。但和上一轮相比，当前最重要的校准已经变成：**breakout-v0 的 first-pass realism 链条现在基本够用了；bot3 下一回合默认更该把主精力切回 `EMA 60m gross vs 20bps rolling / walk-forward` 的第一刀真实结果。**

换句话说：
- `breakout` 这条线这几轮已经把“是不是只靠独立记账的漂亮累计收益撑着”回答到足够具体；
- `EMA` 这条线虽然仍是项目级 `#1`，但还停在 protocol / first-slice 指令层，最缺的就是第一刀真实 rolling / OOS 数字。

## 当前 strongest evidence

1. **breakout-v0 的 first-pass realism 已经形成完整小闭环**
   - 最近连续小步已经补齐：
     - 成本 first-pass
     - overlap first-pass
     - `1-slot global` first-pass
     - `equal-weight concurrent(entry)` first-pass
     - closure board realism refresh
   - 现在这条线最关键的 first-pass 读法已经足够清楚：
     - `20bps + per-asset independent`：累计约 `75.03%`
     - `20bps + equal-weight concurrent(entry)`：累计约 `19.40%`
     - `20bps + 1-slot global`：累计约 `13.83%`
   - 这说明它：
     - **不是** 一加现实约束就归零；
     - 但也**不能**再按 `75.03%` 这种独立记账口径去理解统一资金下的执行空间。

2. **breakout 线的下一步问题已经被收缩得很具体**
   - 现在最自然的问题不再是“还要不要继续看 breakout”；
   - 而是：
     - 要不要做更正式的组合级资金曲线 / sizing honesty；
     - 或把 `support_breakout_confirm_1` 放进同一套约束里比，看看它是否比 raw 更稳。
   - 这意味着：**breakout 这条线已经从 broad framing 进入了更窄的 follow-up 阶段。**

3. **EMA 这边终于也不只是泛泛写 protocol，而是把“第一刀先切哪块”写死了**
   - 最新 `2026-03-14_1603_ema-rolling-first-slice.md` 已把默认 first falsification slice 明确成：
     - **优先先做 `EMA 60m gross vs 20bps rolling / walk-forward`**
   - 理由也已经足够具体：
     - `EMA 60m` 是当前最脆的一块；
     - positive-only median breakeven cost 约 `27.5bps`；
     - 扣 `20bps` 后只剩约 `4/9` 组合存活。
   - 这说明当前最该补的已经不是“到底先做哪块”，而是**把这块真正跑出来**。

4. **closure board 的项目级排序没有变，但短期执行重点应更清晰**
   - 当前顶层排序仍然是：
     - `EMA / PSAR = #1`
     - `breakout-short follow-up = #2`
     - `Fibonacci = archive`
   - 但这轮之后，`#2` 的 first-pass realism 已经比 `#1` 的 OOS 验证更完整；
   - 所以如果 bot3 再连续几轮继续只补 breakout，而 EMA 仍不出真实 rolling 结果，项目级排序和执行节奏就会开始不一致。

## 当前 weakest / should-fix-next

1. **EMA 仍然是当前最需要从“已定义”跨到“已验证”的对象**
   - 成本有了；
   - 决策页有了；
   - protocol 有了；
   - first falsification slice 也有了；
   - 但还没有第一刀窗口结果。

2. **breakout 线当前最不该做的是继续扩更多 first-pass 口径**
   - `equal-weight concurrent(entry)` 已经把中间口径补出来；
   - 继续往下当然还能做，但边际上已经不如尽快切回 EMA 来得高。

## 下一步优先级 Top 1~3

### Top 1. `EMA 60m gross vs 20bps` 的 rolling / walk-forward 第一刀结果

最值得继续：
- 直接把已写死的 first falsification slice 跑出来；
- 优先回答：
  - 窗口正收益占比；
  - 坏窗口是否扎堆；
  - `gross -> 20bps` 后存活窗口比例还剩多少。

为什么排第一：
- 因为这条线是项目级 `#1`；
- 且当前只差结果，不差 framing。

### Top 2. breakout-v0 的更正式组合级资金曲线 / sizing honesty

最值得继续：
- 若继续沿 breakout 线推进，就不要再停在 `entry-only` 近似；
- 至少补一个比 `equal-weight concurrent(entry)` 更正式的 portfolio path / sizing 对照。

为什么排第二：
- 因为 first-pass realism 已经足以证明“值得继续，但空间明显收窄”；
- 下一步若做，应进入更正式但仍克制的组合层验证，而不是再堆更多解释。

### Top 3. `support_breakout_confirm_1` 放进同一套成本 / 执行 / 环境约束框架

最值得继续：
- 不再让 `confirm_1` 只停留在口头角色判断；
- 真正回答它在同样约束下，是否比 raw 更稳。

为什么排第三：
- 这项确实有价值；
- 但应排在 `EMA 真 OOS` 与 `breakout 正式组合层` 之后。

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 `docs/ROADMAP.md`**
- **本轮不改 cron / prompt**

原因：
1. bot3 当前没有跑偏，且最近每轮都在主线内交付真实或准真实验证产物；
2. `breakout` 与 `EMA` 的 next step 现在都已经很清楚，暂时不需要再靠 prompt 收紧去修正方向；
3. repo worktree 依然很脏，bot2 此时再碰主文档，边际收益不高。

本轮只新增这份轻量策略巡检记录。

## 网页 / 表达建议

1. **breakout-v0 页暂时已经“够诚实”**
   - 现在最重要的是：别再继续只堆 first-pass 解释；
   - 若再推进，就直接上更正式的组合级资金路径。

2. **EMA 页下一步必须从“先切哪块”进入“第一刀结果页”**
   - first falsification slice 已经写死；
   - 再继续补 why-this-slice 文案，边际价值已经很低。

3. **closure board 这轮也先别再动**
   - 除非 EMA 真 rolling 结果出来；
   - 否则当前顶层表达已经够用了。

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：继续保持，不改**
   - 当前频率没有导致空转；
   - 也已经开始把两条 active 线往更真实的验证层推进。

2. **但 bot3 的下一回合默认应更偏向 EMA，而不是继续只补 breakout**
   - 不是因为 breakout 不重要；
   - 而是因为 breakout 的 first-pass realism 现在已经相对更完整，而 EMA 仍缺第一刀真实 rolling 结果。

3. **若接下来 1~2 轮 EMA 仍不出真实 OOS slice，再考虑最小 prompt 微调**
   - 当前这轮还不需要；
   - 但观察窗口已经很清楚了。

## 风险与不确定性

1. breakout-v0 当前只通过了 first-pass realism，不等于已通过正式组合级验证。
2. EMA 当前只是明确了 first falsification slice，还没有真正跑出 rolling / walk-forward 结果。
3. 如果 bot3 下一轮继续沿主线交真实验证，这轮判断成立；如果又回到只补 protocol / 解释，那这轮判断会很快过期。
