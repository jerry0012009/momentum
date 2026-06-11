# 给 pytrendline 正式补一张 active bridge brief

## 为什么这次选这个

这轮继续沿刚刚定下来的 `replication shortlist v1` 往前推进，但我没有再开新论文，也没有直接去补第二个候选，而是先把一个最明显的缺口补上：

- shortlist v1 里已经把 `pytrendline` 正式列成了 `event-source bridge` 候选；
- 但 `Trendline Replication Briefs` 页面仍停留在旧状态，核心只围着 `Chan 2022 / Svogun 2022` 打转；
- 这会导致页面口径和 shortlist 口径不一致，也会让人误以为 `pytrendline` 还没有被正式纳入 clean-room brief 体系。

这轮最值得复用/借鉴的点是：**当候选池里既有“论文 replication”对象，又有“engine bridge”对象时，不应该强行把所有 brief 都写成论文复现模板；更好的做法是明确把 engine 类对象写成 `active bridge brief`，回答“先复现到哪一层、先接到哪一层、什么算成功”。**

## 核心结论（中文摘要）

核心结论：**`pytrendline` 现在已经正式拥有一张 `active bridge brief`；它的正确定位不是“先复刻某个论文收益率”，而是 clean-room 复现 `结构检测 → source bridge → event validation` 这条可审计路径。**

证据如何支持这个结论：**本轮已更新 `scripts/build_trendline_replication_briefs_report.py`，重建后的 `reports/site/reading/trendline_replication_briefs/report.html` 已新增 `Brief A · pytrendline (Eduardo Nunez)`，并明确写出输入数据、最小 clean-room 定义、bridge 层输出、成功标准与风险；同时 `docs/TODO.md` 已补充“pytrendline 的 active bridge brief 已落地”，并将“外部材料进入正式实现前，默认先做 clean-room replication brief”标记为完成。**

## 本轮做了什么改动

本轮只做一个主点：**把 `pytrendline` 正式纳入 replication brief 体系，并让 brief 页和 shortlist v1 对齐。**

具体改动：

1. 更新 `scripts/build_trendline_replication_briefs_report.py`
   - 重写页面开头的定位，明确这页现在同时容纳：
     - paper replication
     - engine bridge
     - mechanism mapping
   - 将原先过时的“为什么不是先直接复刻 pytrendline？”改成 `Brief 页怎么读`

2. 在同页新增：
   - `Brief A · pytrendline (Eduardo Nunez)`
   - 明确它的目标不是 faithful 论文 replication，而是：
     - detection layer
     - bridge layer
     - validation layer
   - 明确最小 clean-room 定义：
     - 输入标准化 candles
     - 输出 pivots / trendlines / breakout-tagged lines / representative grouped lines
     - 再翻译成 unified event schema 可消费字段
   - 明确成功标准：
     - 不是收益率像素级对齐
     - 而是证明它能稳定成为一个 `可审计 / 可桥接 / 可进入 event validation` 的 structure engine

3. 同页更新 `Replication / Bridge priority`
   - 使其与 shortlist v1 对齐：
     - `Svogun 2022`
     - `pytrendline`
     - `trendln`
     - `Optimal Stopping`
   - 并保留 `Chan 2022 = parked`

4. 同页更新“当前已落地页面”与“我建议的落地顺序”
   - 把 `PyTrendline Event Source Bridge v1`
   - `PyTrendline Event Validation v1`
   都挂进 replication briefs 页的导航里

5. 更新 `docs/TODO.md`
   - 在 `为每个 replication candidate 产出一张 replication brief` 下补记：
     - `Trendline Replication Briefs` 已新增 `pytrendline` 的 active bridge brief
   - 明确当前仍待补：
     - `trendln`
     - `Optimal Stopping`
   - 将：
     - `规定：外部材料进入正式实现前，默认先做 clean-room replication brief，不直接搬代码。`
     - 标记为 `[x]`

6. 重建页面
   - `reports/site/reading/trendline_replication_briefs/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

本轮是文档 / brief / 页面细化，因此采用最小必要验证：

1. 语法检查
   - `./.venv/bin/python -m py_compile scripts/build_trendline_replication_briefs_report.py scripts/build_plans_site.py`

2. 页面重建
   - `./.venv/bin/python scripts/build_trendline_replication_briefs_report.py`
   - `./.venv/bin/python scripts/build_plans_site.py`

3. 本地 grep 验证
   - `reports/site/reading/trendline_replication_briefs/report.html`
     - 已出现：`Brief A · pytrendline (Eduardo Nunez)`
     - 已出现：`Event-source bridge / explainability engine`
     - 已出现：`Optimal Stopping S/R paper`
     - 已出现：`active bridge candidate`
   - `reports/site/plans/momentum_todo.html`
     - 已出现：`[x] 规定：外部材料进入正式实现前，默认先做 clean-room replication brief`
     - `为每个 replication candidate 产出一张 replication brief` 仍保持未完成，但已记录 `pytrendline` brief 已落地

## 风险 / 边界

- 这轮没有新增新的实验结果，也没有给 `trendln / Optimal Stopping` 新补 brief；
- 它解决的是 **brief 体系与 shortlist v1 的口径一致性**，不是直接新增 alpha 证据；
- `pytrendline` 这张 brief 的定位是 `active bridge brief`，不是论文 replication brief，后面若读者没看清这个区别，仍可能误把它理解成“又在为弱 breakout 背书”。

## 下一步建议

1. 按当前顺序继续补下一张 brief
   - 二选一：
     - `trendln`（几何 / channel baseline）
     - `Optimal Stopping`（confirmation / retest 机制）

2. 保持这条纪律
   - paper 类对象 → replication brief
   - engine 类对象 → bridge brief
   - mechanism 类对象 → protocol / mapping brief

3. 后续所有 E shortlist 页面都尽量沿这个三分法写，避免混层。

## Commit hash

- 已提交：`docs(momentum): add pytrendline bridge brief`
- 具体 hash 以本轮提交后的当前 `HEAD` 为准。

## 如果未提交，说明原因

本轮已做安全 selective commit。

我只提交了本轮涉及的 brief 页面 / TODO / 运行记录文件，没有混入当前 repo 里与本轮无关的其它脏文件。