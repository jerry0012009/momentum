# 为 Mainline 落地最小 decision board，并清掉重复待办

## 为什么这次选这个

这轮继续沿最近最接近的主线推进，没有新开题。

前面几轮已经完成：
1. 把站点改成 `Structure-Event Mainline + Engine Labs`；
2. 补了 `Cross-Engine Mapping`；
3. 跑完并接入了 `confirmation ladder` 报告。

因此当前最自然、也最值得复用的一步，不是继续加新页面，而是把已经散落在 TODO、confirmation ladder、slope audit 里的判断，收束成一个**首页级可见的 decision board**，让后续人一进 Mainline 就知道：哪些方向偏继续、哪些方向偏停、哪些方向还缺桥接。

这轮最值得复用/借鉴的点是：**当主线结构刚完成重组时，下一步最该补的不是更多内容，而是“最小决策板”——它能把已有研究结论立刻转成导航和优先级。**

## 核心结论（中文摘要）

核心结论：**当前最小版主线判断已经足够明确，可以公开写成 decision board：`breakout` 偏 `park / weak`，`rebound retained subsets` 偏 `continue / feature candidate`，`pytrendline source` 仍是 `unknown / need bridge`。**

证据如何支持这个结论：**`confirmation ladder` 与此前 `slope audit` 已共同说明 breakout 侧即便加强确认也没有形成可靠改善；而 retained rebound subsets（尤其 `flat + down_high`）在较宽松 `inside=0/1` 下仍保留更好的 positive asset ratio、mean total return 与 trade retention；与此同时 `pytrendline` 虽然 explainability 已很强，但还没有最小 event-source bridge，所以还不能直接进入同口径比较。**

## 做了什么改动

本轮只做一个主点：**把最小 decision board 挂到 Mainline 页面，并把 TODO 里重复的 decision-card 待办统一收口。**

具体改动：

1. 修改 `scripts/build_trendline_tracks_site.py`
   - 给 `Track` 增加：
     - `decision_title`
     - `decision_items`
   - 给页面模板增加 `decision-card` 样式与渲染逻辑。

2. 在 `Structure-Event Mainline` 中填入当前最小 decision board：
   - `breakout` → `park / weak`
   - `rebound retained subsets` → `continue / feature candidate`
   - `pytrendline source` → `unknown / need bridge`

3. 更新 `docs/TODO.md`
   - 将“在主线文档或主页中补一个 decision board”标记为已完成 `[x]`
   - 同时把两个语义重复的 `decision card` 待办统一勾掉，避免后续自动循环重复挑同一题
   - 同步更新 `reports/site/plans/momentum_todo.html`

4. 重新生成并发布：
   - `reports/site/factors/structure_event_mainline/report.html`
   - `reports/site/factors/trendline_pytrendline_track/report.html`
   - `reports/site/factors/trendline_pyindicator_track/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

最小必要验证：

- `./.venv/bin/python -m py_compile scripts/build_trendline_tracks_site.py`
- `./.venv/bin/python scripts/build_trendline_tracks_site.py`
- `./.venv/bin/python scripts/build_plans_site.py`

落地产物检查：

- 本地确认 `reports/site/factors/structure_event_mainline/report.html` 中已出现：
  - `当前 decision board（最小版）`
  - `breakout：偏 park / weak`
  - `rebound retained subsets：偏 continue / feature candidate`
  - `pytrendline source：unknown / need bridge`

- 本地确认 `reports/site/plans/momentum_todo.html` 中已将相关 decision board / decision card 待办标记为完成。

- 在线页面仍可访问：
  - `https://jp.jerrypsy.top/momentum/factors/structure_event_mainline/report.html`
  - `https://jp.jerrypsy.top/momentum/plans/momentum_todo.html`

## 风险 / 边界

- 这个 decision board 是**最小版**，当前作用是帮助阅读和排优先级，不是最终研究终局。
- `pytrendline source` 目前仍然只是 explainability baseline，还没完成 event-source bridge。
- 这轮没有新增统计，只是把已有证据沉淀成更好复用的站点结构与 TODO 状态。

## 下一步建议

1. 做第一版 `PyTrendline -> unified event schema` 试映射；
2. 让 `pytrendline` 产出最小 event-source sample；
3. 然后再做第一轮 `PyIndicators source vs PyTrendline source` 的 mainline 对照。

## Commit hash

- `86028e5` — `feat(momentum): add mainline decision board`
- `b77cc15` — `chore(momentum): log mainline decision board run`
- `dbff399` — `docs(momentum): close duplicate decision-card todos`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有一起提交：
- `reports/site/plans/index.html`
- `reports/site/plans/report.html`
- 以及 repo 内其它与本轮无关的脏文件和生成物

原因是它们主要是本轮重建时顺带产生的时间戳/镜像变动，不属于这次 decision board 的最小闭环。
