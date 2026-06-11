# 为 Svogun 2022 落地独立 replication report

## 为什么这次选这个

这轮我刻意没有继续往主线内部加页面，而是响应前面已经明确的原则：**E 模块也要被认真使用，而且最好直接服务当前主线。**

最近几轮我们已经连续完成了：
1. `PyTrendline event source bridge v1`
2. `PyTrendline event validation v1`
3. `Cross-Engine Source Comparison v1`

这意味着主线内部已经暂时有了一条可读的闭环。此时更高杠杆的一步，不是继续补一层内部细节，而是把外部证据轨里最贴近当前痛点的对象真正落成单页入口。

我选的是：**Svogun & Bazán-Palomino (2022)**。

原因很直接：我们当前内部最明显的问题就是——不管是 `PyIndicators breakout` 还是 `PyTrendline breakout v1`，都没有给出很强的正面 breakout 结论。于是下一步最需要的，不是再盲目试更多 breakout 变种，而是把“成本与 regime 约束”正式拉进视野。Svogun 2022 正好就是这个角色。

这轮最值得复用/借鉴的点是：**当内部主线已经连续做了几轮 observation 后，E 模块最应该补的不是泛泛新文献，而是能直接约束当前主线误判风险的 replication report。**

## 核心结论（中文摘要）

核心结论：**Svogun 2022 现在已经从 scout / brief 中的一段文字，升级成了独立的 clean-room replication report；它最重要的价值不是给出某个神奇 breakout 参数，而是把“成本后生存性 + regime 改写效应”正式变成我们当前主线必须面对的现实约束。**

证据如何支持这个结论：**我们最近的内部结果已经显示 breakout 线整体偏弱；而 Svogun 2022 的核心 claim 正是“crypto 技术规则在 gross 与 net 下会被重新排序，bubble/regime 会改写结果”。因此把它独立落页后，后续自动任务就能直接以它为 replication 入口，而不是继续把 breakout 研究停留在不含成本/状态约束的纸面层。**

## 本轮做了什么

本轮只做一个主点：**把 Svogun 2022 做成独立 replication report，并挂回 E 模块导航。**

具体改动：

1. 新增脚本：
   - `scripts/build_svogun2022_cost_regime_replication_report.py`

2. 新增独立页面：
   - `reports/site/reading/svogun2022_cost_regime_replication/report.html`

3. 更新 `Trendline Replication Briefs` 导航页：
   - 现在不仅有 `Chan 2022 · S/R Feature Replication Report`
   - 也有 `Svogun 2022 · Cost/Regime Replication Report`

4. 更新 `Trendline Alpha Scout`：
   - `Svogun 2022` 不再只是 shortlist 中的候选
   - 现在已经拥有独立的 clean-room replication 入口页

5. 更新文档：
   - `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
     - 给 Svogun 2022 补上：`deep dive done + replication brief done`
     - 并记录入口页
   - `docs/TODO.md`
     - 在 replication brief 待办下写明当前已落地：
       - `Chan 2022`
       - `Svogun 2022`

## 这页 replication report 具体解决了什么

这页不是在宣称“我们已经把论文复现成功”，而是在把它变成一个真正可执行的 clean-room 入口。

它明确了：

1. **为什么这篇论文现在重要**
   - 因为当前 breakout 线整体偏弱，后续所有 breakout / trend 研究都不能再只看 gross 纸面表现

2. **我们到底准备复现哪一层**
   - 不是完整复刻 69 条规则族
   - 而是先复刻：
     - breakout / trend 规则在 `gross / net_low / net_high` 下的生存性差异
     - 这些差异是否会被 regime / bubble proxy 改写

3. **第一版最小 clean-room 设计**
   - crypto
   - 60m
   - BTC / ETH / XRP / LTC
   - 365d + 730d
   - MA crossover baseline + breakout baseline
   - gross / net_low / net_high
   - trend_strength / volatility_state / bubble_proxy 分层

## 验证 / 证据

最小必要验证：

- `./.venv/bin/python -m py_compile scripts/build_svogun2022_cost_regime_replication_report.py scripts/build_trendline_replication_briefs_report.py scripts/build_trendline_alpha_scout_report.py scripts/build_plans_site.py`
- `./.venv/bin/python scripts/build_svogun2022_cost_regime_replication_report.py`
- `./.venv/bin/python scripts/build_trendline_replication_briefs_report.py`
- `./.venv/bin/python scripts/build_trendline_alpha_scout_report.py`
- `./.venv/bin/python scripts/build_plans_site.py`

在线验证：

- `https://jp.jerrypsy.top/momentum/reading/svogun2022_cost_regime_replication/report.html` 返回 200
- `https://jp.jerrypsy.top/momentum/reading/trendline_alpha_scout/report.html` 返回 200
- `https://jp.jerrypsy.top/momentum/reading/trendline_replication_briefs/report.html` 返回 200

## 风险 / 边界

- 这轮没有新增本地回测结果，只是把外部证据轨的一个关键对象落成独立 replication report。
- 它仍然不是论文的像素级复刻，而是 clean-room 计划页。
- 但它已经足够把后续自动任务从“继续泛泛找文献”推进到“直接实现 gross vs net + regime 的最小实验脚手架”。

## 下一步建议

1. 如果下一轮继续走 E 模块，最合理的是：
   - 直接给 `Svogun 2022` 起一个最小规则存活性实验脚手架
   - 输出 gross / net_low / net_high + regime slice summary

2. 如果下一轮切回主线，最合理的是：
   - 把这个 cost / regime replication 约束回挂到 breakout / confirmation 主线里
   - 明确哪些内部实验以后必须默认报告 net 与 regime split

## Commit hash

- `33e49c2` — `docs(momentum): add svogun replication report`

## 如果未提交，说明原因

本轮核心改动已安全 selective commit。

我刻意没有一起提交与本轮无关的其它 reading / factors / site 页面脏文件，因为它们不属于这次 `Svogun 2022 replication report` 的最小闭环。
