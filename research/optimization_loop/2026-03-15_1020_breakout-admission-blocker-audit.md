# Breakout admission blocker audit

- 时间：2026-03-15 10:20 UTC
- 主线：`support_breakout_v0 / breakout-short follow-up`
- 本轮类型：deployment-facing verdict compression（不再新增近义 wording，而是把现有 admission 证据压成一张 blocker checklist）

## 为什么认领这刀

按当前 steering，breakout 仍是默认最高优先级，但这条线在过去几轮已经连续补了：

- `pure-test tail`
- `pre-mixed 60/72h checkpoints`
- `default pair episode decomposition`
- `mixed-tail overlay episode decomposition`

如果这轮还继续补同类细切片，就容易变成“证据越来越碎、结论却没更 deployment-facing”。

所以这轮改成只做一个更接近 admission / shadow paper 判断的小闭环：

> 把 breakout 当前最关键的 gate evidence 压成一张 blocker checklist，直接回答：
> 1. 哪些问题已经不是主 blocker；
> 2. `one_more_gate` 现在到底卡在哪；
> 3. mixed-tail / blunt pure-down 应该在 deployment 口径里怎么排位。

## 本轮完成

### 1) 新增 breakout admission gate checklist artifact

在 `scripts/build_support_breakout_v0_reports.py` 新增：

- `summarize_breakout_admission_gate_checklist(...)`

并落地新 artifact：

- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_admission_gate_checklist_20bps.csv`

这张表把 breakout 当前 admission 证据压成 7 行 blocker/gate：

1. 组合层 hourly path 是否已不是主 blocker
2. 更长 `5d/10d` forward honesty 是否已从 lucky patch 提高到 usable
3. `pure-test tail` 自身是否已经够厚
4. `down-tail coverage` hard gap 是否已补上
5. `mixed-tail overlay` 能否直接改写 verdict
6. `blunt pure-down patch` 能否当现成补丁
7. 最终 deployment verdict

### 2) 刷新 breakout 主报告

在 `reports/site/factors/support_breakout_v0_h24/report.html` 新增一节：

- `如果只看 deployment blocker：这条 breakout 线的 one_more_gate 到底卡在哪？`

作用不是再堆解释，而是把之前已经做过的 evidence 压成一张更可执行的 blocker checklist，让 Jerry 直接看到：

- 哪些 first-pass 已经过；
- 哪些仍是硬缺口；
- 这条线今天到底为什么还不能写成 `shadow paper now`。

### 3) 同步 TODO / plans

- 在 `docs/TODO.md` 的 breakout open item 下补了一条 `[x]` 最新补充；
- 重新生成 `plans` 页面，保证入口同步当前 blocker 读法。

## 本轮结果

### 新 checklist 给出的 deployment-facing 结论

当前 breakout admission blocker 已经明显收敛成一句话：

> `组合层 hourly path` 与更长 `5d/10d` forward honesty 已经不是主 blocker，
> 但 `pure-test tail` 仍偏薄，而且 `down-tail coverage` 仍是 `0/100`；
> 所以正式 verdict 继续只能是 `one_more_gate`。

### 关键数字

1. **组合层 hourly path：已过 first-pass**
   - default pair 相对 gate-only 累计约 `+4.44pp`
   - max drawdown 约改善 `+0.93pp`
   - 这说明 breakout 已不只是 per-asset 幻觉，可以继续沿 default pair 主候选推进 admission 判断。

2. **更长 forward honesty：usable，但还不是 clearance**
   - `5d` non-overlap blocks：约 `3/4` 为正
   - `10d` non-overlap blocks：约 `2/2` 为正
   - 这说明一般性的 late-segment 焦虑在下降，但还不等于正式放行。

3. **pure-test tail：仍偏薄**
   - strict tail：约 `+0.77pp`，但只打到 `5/30h`
   - 若先不把晚段 mixed-tail pocket 算进去，`72h` checkpoint 其实只有约 `+0.08pp`，且只打到 `3h`
   - 这说明前半段 pure-test 更像“没翻负”，还不是厚实到能单独解除 gate 的 admission honesty。

4. **down-tail coverage：硬缺口未补**
   - 当前仍是 `0/100 = 0.00%`
   - 这是最硬的 blocker，不是 wording 问题。

5. **mixed-tail overlay：继续只配 shadow-only**
   - strict tail 相对 default pair 约 `+0.26pp`
   - `5d` / `10d` forward blocks 都还是 `1/2`
   - 所以它可以作为附加观察项继续留着，但还不能改写 verdict，也不能替代 default pair 主候选。

6. **blunt pure-down patch：继续 reject**
   - 虽然 pure-down coverage 能打到约 `63/100`
   - 但 overall delta 约 `-0.42pp`
   - 这说明 blocker 看起来像 down-tail，但不能靠“一律 pure-down 再砍半”机械解除。

## 本轮 verdict

### breakout 当前正式 verdict

- 继续维持：`shadow-admission queue / one_more_gate`

### 更 deployment-facing 的一句话

> breakout 线还能继续推，但默认只该沿 `default pair halfsize` 主候选继续推；
> mixed-tail 继续只配 `shadow-only`，blunt pure-down 继续视为 reject sanity check。

### 这轮相对前几轮新增的价值

不是又多做了一张 near-synonym 页面，而是把已有 evidence 压成：

- **已过 first-pass 的东西**：组合层 hourly path、一般性更长 forward honesty
- **还没过的硬门槛**：`pure-test tail thickness`、`down-tail coverage`
- **附加观察项 / 已排除项**：`mixed-tail = shadow-only`，`blunt pure-down = reject`

这样 breakout 线下一轮是否继续推进，就不会再回到“到底还差哪道 gate”这种抽象问题，而能直接围绕最硬 blocker 继续推进。

## 变更文件

- `scripts/build_support_breakout_v0_reports.py`
- `docs/TODO.md`
- `reports/artifacts/support_breakout_v0_h24/avoid_fluctuating_admission_gate_checklist_20bps.csv`
- `reports/site/factors/support_breakout_v0_h24/report.html`
- `reports/site/plans/momentum_todo.html`
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`

## 最小验证

已执行：

```bash
python3 -m py_compile scripts/build_support_breakout_v0_reports.py
python3 scripts/build_support_breakout_v0_reports.py
python3 -m py_compile scripts/build_plans_site.py
python3 scripts/build_plans_site.py
```

结果：通过。

## Git / hygiene 备注

- 本轮开始前 `git status --short` 已显示大量与本轮无关的脏改动与未跟踪文件；该状态不是失败条件，但意味着不能把无关内容混进本轮。
- 本轮没有提交：
  - 原因不是本轮工作无效；
  - 而是当前工作区存在大量跨主题既有脏文件（EMA / trendline / reading / workspace 级缓存与未跟踪产物等），不适合在本轮直接做安全的 selective commit。
- 若后续要提交，建议先单独隔离工作区，再只挑本轮 breakout admission checklist 相关文件。

## Post-log ops

按 loop protocol：

1. 记录写完后刷新首页 index；
2. 再把本记录邮件发送到默认收件箱。
