# 把 Optimal Stopping 的机制解释正式挂回 confirmation protocol

## 为什么这次选这个

这轮继续完全沿最近几轮的 E / protocol 收口线程推进，没有扩新候选，也没有重跑任何实验，而是直接做一个最近且很实用的动作：

- 前两轮已经把 `Optimal Stopping` 正式补成了 `mechanism brief`；
- 但它最有价值的部分，仍主要停留在 brief 页面里；
- 如果不把它真正挂回 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md`，那它对主线的价值仍然更像“读过的好材料”，而不是“可以被主线稳定引用的解释口径”。

所以这轮最合适的推进，不是再写一篇新 brief，而是把它最关键的机制解释——`touch_or_cross / provisional_break / confirmed_switch / retest_hold`——正式并入 confirmation protocol 本体。

这轮最值得复用/借鉴的点是：**当一篇机制型材料对主线最有价值的是“解释框架”而不是“实验结果”时，最好的落地方式不是重复写 digest，而是直接把它吸收到协议文档里，变成可被后续所有实验统一引用的 contract language。**

## 核心结论（中文摘要）

核心结论：**`Optimal Stopping` 现在已经不再只是 `Trendline Replication Briefs` 里的一张 mechanism brief；它关于 `touch_or_cross -> provisional_break -> confirmed_switch` 的解释，已经正式并入 `TRENDLINE_CONFIRMATION_PROTOCOL`，成为主线可直接引用的 confirmation 口径。**

证据如何支持这个结论：**本轮已在 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md` 新增 `3.3 Optimal Stopping 带来的机制解释（为什么要分这些层）`，明确解释了 `raw_breach / close_confirm_same_bar / confirm1 / confirm3 / retest_hold` 各自更接近什么状态层级；同时 `reports/site/plans/trendline_confirmation_protocol.html` 已同步出现这一新章节，`docs/TODO.md` 与 `plans/momentum_todo.html` 也新增了对应的 `[x]` 记录。**

## 本轮做了什么改动

本轮只做一个主点：**把 `Optimal Stopping` 的机制解释从 brief 页面上升为 protocol 层语言。**

具体改动：

1. 更新 `docs/TRENDLINE_CONFIRMATION_PROTOCOL.md`
   - 在 `3.2 confirmation level` 后新增：
     - `3.3 Optimal Stopping 带来的机制解释（为什么要分这些层）`
   - 这段新内容明确说明：
     - `touch_or_cross` 不等于状态真的切换；
     - `provisional_break` 只说明价格暂时离开原结构边界；
     - `confirmed_switch` 才更接近结构语义真的变化。

2. 在同一新章节中，把 breakout ladder 显式解释为：
   - `raw_breach`
     - 最接近：`touch_or_cross / provisional_break`
   - `close_confirm_same_bar`
     - 最接近：较强的 same-bar provisional evidence
   - `confirm1`
     - 第一层可执行的 confirmed-switch 候选
   - `confirm3`
     - 更强的持续性确认
   - `retest_hold`
     - 最接近结构性 `confirmed switch`

3. 同时把 rebound ladder 的解释补清楚：
   - `touch_only`
     - 只看到接触，不足以说明“守住”
   - `inside_0 / inside_1 / inside_2 / inside_3plus`
     - 可以理解成“回到原结构内部并持续停留”的 retained evidence 强弱层级

4. 更新 `docs/TODO.md`
   - 在 `A1-C. confirmation ladder` 下补充：
     - `明确定义 provisional break 与 confirmed switch` 这条现在已进一步挂回 protocol 本体
   - 新增并标记为 `[x]`：
     - `把 Optimal Stopping 的 touch_or_cross / provisional_break / confirmed_switch 解释显式挂回 confirmation protocol`

5. 重建 plans 镜像
   - `reports/site/plans/trendline_confirmation_protocol.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮是协议 / 页面细化，因此采用最小必要验证：

1. 页面重建
   - `./.venv/bin/python scripts/build_plans_site.py`

2. 本地 grep 验证协议页
   - `reports/site/plans/trendline_confirmation_protocol.html`
     - 已出现：`3.3 Optimal Stopping 带来的机制解释（为什么要分这些层）`
     - 已出现：`touch_or_cross`
     - 已出现：`retest_hold`
     - 已出现：`confirmed switch`

3. 本地 grep 验证 TODO 页
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 把 Optimal Stopping 的 touch_or_cross / provisional_break / confirmed_switch 解释显式挂回 confirmation protocol。`
     - 已出现：`[x] 明确 provisional break 与 confirmed switch 的区分口径。`

## 风险 / 边界

- 这轮没有新增新的回测或事件统计；
- 它解决的是 **protocol 解释口径的统一与可引用性**，不是直接新增 alpha 证据；
- 当前 `Optimal Stopping` 的价值仍主要是 mechanism / protocol 层，不应被误读为已经给出某个可交易的默认参数答案。

## 下一步建议

1. 如果继续沿这条线推进，下一步最合理的是：
   - 把这套 `touch / provisional_break / confirmed_switch / retest_hold` 机制解释，进一步映射到现有 source（尤其是 `PyIndicators` 与后续 `PyTrendline v2`）的原生字段上；
2. 如果转回更实证的工作，则可以开始问：
   - `confirm1 / confirm3 / retest_hold` 三层中，哪一层在 retention 与 forward-return 之间最值得保留为默认口径。

## Commit hash

- 已提交：`docs(momentum): map optimal stopping into protocol`
- 具体 hash 以本轮提交后的当前 `HEAD` 为准。

## 如果未提交，说明原因

本轮已做安全 selective commit。

我只提交了本轮涉及的 protocol / TODO / 运行记录文件，没有混入当前 repo 里与本轮无关的其它脏文件。