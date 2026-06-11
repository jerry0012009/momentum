# 给 EMA / PSAR 收口页补角色判断：PSAR 先定为 fast reaction / loss-protection candidate，不升同等级主 alpha

## 为什么这次选这个

这轮严格按新的三条收口线优先级推进，没有回到 `pytrendline_event_validation_v3` 延伸任务，也没有继续扩外部文献池。

在这三个当前高优先级方向里，`EMA / PSAR raw alpha focus` 这条线有一个很适合这轮解决的小缺口：**PSAR 的角色虽然之前在文字里隐约说过，但还没有在默认报告页里用足够硬的、适合后续决策的口径写死。**

这轮最值得复用/借鉴的点是：**收口线不该一直停留在“看起来谁更好”的研究表述里，而要尽快落成“谁是主 baseline、谁是辅助层、当前不支持什么结论”的页面口径。**

## 核心结论（中文摘要）

核心结论：**当前 `EMA / PSAR Raw Alpha Focus Report` 应明确收口为：`EMA = raw alpha baseline candidate`，`PSAR = fast reaction / loss-protection candidate`；当前不支持把 PSAR 直接升成与 EMA 同等级的主 alpha。**

证据如何支持这个结论：**在现有 cross-market × multi-frequency first-pass 结果里，EMA 与 PSAR 的正收益覆盖率都很高（都约 `92.59%`），但 EMA 在 asset×freq 组合里拿第一的次数更多（`14` vs `8`），同时交易频率明显更低（median trades 约 `53` vs `113`），说明 EMA 更适合作为主 baseline；PSAR 的价值更像“更快反应”，而不是“更稳主干”。**

## 本轮做了什么改动

本轮只做一个主点：**把 `EMA / PSAR Raw Alpha Focus Report` 补成更像策略决策页的收口口径，并顺手完成 TODO 里的 PSAR 角色判断任务。**

具体动作：

1. 更新 `scripts/build_ema_psar_raw_alpha_report.py`
   - 在“先给结论”和 Q1 之间新增一张：
     - `收口定位：这条线现在该怎么读？`
   - 新卡片明确写了 5 件事：
     - 当前核心结论
     - 当前最强证据
     - 当前不支持什么结论
     - EMA / PSAR 更像什么角色
     - 下一步最值得做什么

2. 更新 `docs/TODO.md`
   - 将这条任务勾掉：
     - `优先补 PSAR 的角色判断：它更像主 alpha、保护性退出、还是更快反应层。`
   - 并补一句结果说明：
     - 当前正式口径是 `EMA = raw alpha baseline candidate`；
     - `PSAR = fast reaction / loss-protection candidate`；
     - 当前不支持把 PSAR 升成同等级主 alpha；
     - 后续更合理的是补 PSAR 的成本 / 交易频率敏感性，以及 `EMA + PSAR` 最小组合研究。

3. 最小重建与发布
   - 重建：
     - `reports/site/factors/ema_psar_raw_alpha/report.html`
     - `reports/site/plans/momentum_todo.html`
   - 同步发布到站点镜像。

## 验证 / 证据

### 1) 页面已落地的关键口径
重建后，`EMA / PSAR Raw Alpha Focus Report` 已能直接检索到：
- `收口定位：这条线现在该怎么读？`
- `PSAR = fast reaction / loss-protection candidate`
- `当前不支持把 PSAR 直接升成与 EMA 同等级的主 alpha`

### 2) 为什么这一步现在比继续跑新切片更值钱

因为当前提醒已经明确：
- 短期优先是三条收口线；
- 这轮应优先做结论页、解释补强、角色判断、主入口呈现；
- 而不是继续把时间投到新的泛泛阅读或旧研究线的外延扩张。

在这种阶段，**让默认报告页直接回答“EMA 和 PSAR 各自现在是什么角色”，比继续多跑一刀新图更直接帮助 Jerry 判断后续资源怎么配。**

### 3) 页面口径现在更像什么

现在这页已经更像一个小型策略决策页，而不只是阶段性研究页：
- 它不仅说“谁更强”；
- 还明确说了：
  - 谁是主 baseline；
  - 谁是 secondary / protective layer；
  - 当前不支持什么结论；
  - 下一步该先补什么完整性验证。

## 风险 / 边界

- 这轮没有新增回测结果；
- 它完成的是**决策表达层补强**，不是新的数值发现；
- 但它确实解决了一个重要的收口缺口：
  - 避免后续把 PSAR 误当成与 EMA 同等级的主干 alpha 来推进。

## 下一步建议

如果下一轮继续沿三条收口线推进，更合理的候选是：

1. `EMA / PSAR raw alpha focus`
   - 补 EMA 的成本 / rolling / OOS honesty
   - 或做 `EMA + PSAR` 的最小组合研究

2. `support_breakout_v0 / breakout-short follow-up`
   - 把 `avoid_fluctuating` 真带入 v0 原型做一刀更接近实现层的 A/B

3. `Fibonacci confirmation / retest_hold`
   - 补 archived/filter 结论页表达，而不是回到主 alpha 推进

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成页面口径、TODO、日志与邮件同步，不做提交。