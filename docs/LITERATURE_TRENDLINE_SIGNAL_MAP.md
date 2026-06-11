# LITERATURE_TRENDLINE_SIGNAL_MAP.md

> 目的：
> - 沉淀 `trendline / support-resistance / breakout / rebound / retest / confirmation / channel` 相关外部材料；
> - 为 `TODO.md` 中的 **E. External Alpha / Literature Scout** 提供统一 intake 模板；
> - 帮助 Agent 判断：哪些材料只是参考，哪些值得做 digest / deep dive / replication brief。

## 使用规则

1. **近 5 年优先**
   - 默认优先收集近 5 年的论文、工作论文、复现文章、开源仓库。
   - 更老的材料只有在属于 canonical baseline 时才保留，并标注 `canonical / older baseline`。

2. **优先可复现材料**
   - 优先顺序：
     1. 有回测 + 有代码 / GitHub
     2. 有回测 + 有清晰伪代码 / 逻辑定义
     3. 只有理论，没有可操作定义

3. **先做 clean-room replication brief，不直接搬代码**
   - 外部仓库默认只学习逻辑、接口、假设与验证方式；
   - 正式实现进入 `src/` 前，先写 replication brief。

4. **网页边界要清楚**
   - `reading/`：外部证据、论文卡、deep dive、replication candidate
   - `factors/`：我们自己已经本地验证过的研究结果

---

## Scout protocol v1（正式侦察协议）

### 1. 搜索范围

每轮 E 模块默认优先覆盖以下 6 类关键词簇，避免只搜单一 `trendline breakout`：

1. `trendline breakout / confirmation`
2. `failed breakout / rebound / rejection`
3. `support-resistance predictive features`
4. `retest / confirmation / filter`
5. `channel / regression channel`
6. `pivot / swing structure`

### 2. 纳入门槛

一个来源要进入高优先级候选池，默认优先满足以下 4 项：

- 近 5 年优先；
- 来源靠谱（正规期刊 / SSRN / arXiv / working paper / 作者主页 / 可信机构）；
- 有代码 / GitHub / 明确可复刻实现；
- 能拿到全文（PDF / 全文页 / working paper 正文），而不只是摘要。

默认排序规则：

- **四项同时满足** → `top priority`
- **缺 1 项** → 可保留，但降级为 `secondary`
- **只能拿到摘要 / 结论** → 标记为 `abstract_only / weak_evidence`，不进入优先 digest / deep dive / replication shortlist

### 3. 第一轮质量审计口径

每个候选至少审 7 件事：

1. 结构定义是否清楚
2. event / confirmation / execution 是否分层
3. 是否有回测或可读证据
4. 是否讨论交易成本 / 滑点
5. 是否有 OOS / rolling / cross-asset
6. 是否疑似 future info / repaint
7. 是否能 clean-room 重写

### 4. 推荐动作分层

完成最小审计后，默认只允许落到以下动作之一：

- `digest`
- `deep dive`
- `replication brief`
- `park`

如果只是“搜到链接但还没过质量门槛”，不算完成一个 E 任务。

### 5. 与主线的回挂关系

每个候选都必须至少标一类 `fit_for_us`，说明它更像服务：

- `mainline_event_source`
- `feature_candidate`
- `filter_candidate`
- `explainability_reference`
- `low_fit`

也就是说，E 模块不是泛泛读论文，而是默认要回挂到：

- event source design
- validation metric / protocol
- confirmation / retest / filter
- clean-room replication candidate

---

## 推荐标签

### source_type
- paper
- working_paper
- github_repo
- blog_post
- reproduction_article

### structure_family
- trendline_breakout
- trendline_rebound
- support_resistance_feature
- confirmation_filter
- retest_logic
- channel_breakout
- regression_channel
- pivot_structure

### evidence_status
- read
- digest_done
- deep_dive_done
- replication_candidate
- local_validation_started
- local_validation_done
- parked

### fit_for_us
- mainline_event_source
- feature_candidate
- filter_candidate
- explainability_reference
- low_fit

### risk_flags
- repaint_risk
- future_info_risk
- unclear_execution
- no_cost_model
- sample_too_thin
- no_code
- unclear_license

---

## 单条来源卡模板

复制下面这个模板，为每个候选来源填写一张卡。

### 最小字段 checklist（v1）

每张来源卡至少要能回答下面这些字段；否则默认不能进 replication shortlist：

- `title / authors / year`
- `link / doi_or_ssrn / github`
- `source_type`
- `license / source boundary`
- `fulltext_access`（full_text / abstract_only / repo_only）
- `market / frequency / sample`
- `alpha_claim`
- `structure_family`
- `event layering clear?`
- `has_backtest?`
- `has_cost_discussion?`
- `has_oos_or_cross_asset?`
- `repaint_or_future_info_risk`
- `clean_room_repro_difficulty`
- `fit_for_us`
- `recommended_action`
- `evidence_status`

### 卡片模板

```markdown
## <Title>

- source_type:
- year:
- authors:
- link:
- doi_or_ssrn:
- github:
- license:
- fulltext_access: full_text / abstract_only / repo_only
- evidence_status: read / digest_done / deep_dive_done / replication_candidate / parked

### 1) 它在研究什么？
- 一句话 alpha claim：
- 结构定义关键词：
- 市场 / 频率 / 样本：

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：
- 有没有明确事件层次（breakout / rebound / retest / confirm）：
- detection / confirmation / execution 是否分开：

### 3) 它给出了什么证据？
- 是否有回测：
- 关键结论：
- 是否讨论交易成本 / 滑点：
- 是否有 OOS / rolling / cross-asset：

### 4) 可复现性与风险
- 是否有代码 / 伪代码：
- clean-room 复现难度：low / medium / high
- 风险标记：
- 是否疑似未来函数 / 重绘：

### 5) 对我们的价值
- fit_for_us:
- 推荐动作：digest / deep dive / replication brief / park
- 为什么：
```

---

## 第一轮优先搜集方向

1. `trendline breakout + confirmation`
2. `failed breakout / rebound / rejection`
3. `support-resistance features with predictive power`
4. `channel breakout / trend channel / regression channel`
5. `pivot-based structure rules with backtested alpha claims`

---

## 第一轮交付标准（给 Agent）

当 Agent 认领 E 模块任务时，至少应产出以下之一：

- `research/quant_digests/*.md` 一篇新短卡
- `research/deep_dives/*.md` 一篇新深挖
- 本文件新增 / 更新若干来源卡
- `reading/trendline_alpha_scout/report.html` 更新候选池 / shortlist / 状态看板
- 某个候选的 clean-room replication brief

如果只是“搜到了几个链接”，不算完成。

---

## 第一批种子来源卡（2026-03-12 初始化）

## pytrendline (GitHub repo)

- source_type: github_repo
- year: 2021
- authors: Eduardo Nunez
- link: https://github.com/ednunezg/pytrendline
- doi_or_ssrn:
- github: https://github.com/ednunezg/pytrendline
- license: MIT
- fulltext_access: repo_only
- evidence_status: deep_dive_done

### 1) 它在研究什么？
- 一句话 alpha claim：没有正式论文式 alpha claim；核心是把 support / resistance trendlines 做成可枚举、可评分、可筛选的对象。
- 结构定义关键词：trendline / support-resistance / pivot / breakout / duplicate_grouping
- 市场 / 频率 / 样本：仓库级实现，不绑定单一市场；README 明确更适合小窗口日内研究或离线分析。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：先找 pivot，再对点对做穷举扫描；检查触点、误差、是否穿过 candle body、是否满足 pivot 约束；对线打分并分组去重。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：有 breakout line 概念，但没有完整 confirmation ladder。
- detection / confirmation / execution 是否分开：是。更像 detection engine，而不是完整交易系统。

### 3) 它给出了什么证据？
- 是否有回测：没有正式论文/回测报告。
- 关键结论：README 与代码都支持“可枚举的线检测层”，不直接支持“这就是已验证 alpha”。
- 是否讨论交易成本 / 滑点：否。
- 是否有 OOS / rolling / cross-asset：否。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：有代码。
- clean-room 复现难度：medium
- 风险标记：no_cost_model
- 是否疑似未来函数 / 重绘：作为 recent-window 离线检测工具，需要额外审 causal boundary。

### 5) 对我们的价值
- fit_for_us: explainability_reference
- 最新 clean-room 入口补充（2026-03-17 10:07 UTC）：已把它压成 `Rank 30 trendln paired-channel breach / corridor breakout gate` 的 fresh intake；当前只允许下一轮做 1 次最小 `15m crypto corridor breach` clean replication，不把 geometry baseline 直接当已验证 alpha。
- 推荐动作：deep dive / replication brief
- 为什么：非常适合做趋势线 detection 层与结构 explainability，也适合作为 clean-room event-source bridge 候选，但不应直接当成“已验证 alpha”。

## trendln (GitHub repo)

- source_type: github_repo
- year: 2019（repo/article 公开期）
- authors: Gregory Morse
- link: https://github.com/GregoryMorse/trendln
- doi_or_ssrn:
- github: https://github.com/GregoryMorse/trendln
- license:
- fulltext_access: repo_only
- evidence_status: deep_dive_done

### 1) 它在研究什么？
- 一句话 alpha claim：没有正式论文式 alpha claim；核心是程序化计算 support / resistance trend lines，并把它们作为后续结构分析输入。
- 结构定义关键词：support-resistance / trendline / extrema / line-search / channel-candidate
- 市场 / 频率 / 样本：仓库级实现，不绑定单一市场；更像结构线识别工具，而不是完整交易系统。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：先抽 extrema，再做 line search 与 quality 过滤；可扩展为成对 support / resistance line 的 channel 候选。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：没有完整事件树，更偏 detection / geometry layer。
- detection / confirmation / execution 是否分开：是。它主要覆盖 detection，不直接覆盖 confirmation / execution。

### 3) 它给出了什么证据？
- 是否有回测：没有正式回测论文。
- 关键结论：适合作为结构线识别教材/工具库，但不应直接把输出当成已验证 alpha。
- 是否讨论交易成本 / 滑点：否。
- 是否有 OOS / rolling / cross-asset：否。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：有代码。
- clean-room 复现难度：medium
- 风险标记：no_cost_model
- 是否疑似未来函数 / 重绘：需要额外审 extrema 抽取与窗口选择的 causal 边界。

### 5) 对我们的价值
- fit_for_us: explainability_reference
- 推荐动作：deep dive / replication brief
- 为什么：它很适合帮助我们把 channel / support-resistance 问题拆成 extrema、line search、line quality 三层，但与 `pytrendline` 相比更像几何 baseline，而不是当前第一优先 bridge。

## Building a reliable and testable day trading bot on python

- source_type: blog_post
- year: 2021
- authors: Eduardo Nunez
- link: http://ednunez.me/tech/2021/03/18/Algotrading.html
- doi_or_ssrn:
- github:
- license:
- fulltext_access: full_text
- evidence_status: read

### 1) 它在研究什么？
- 一句话 alpha claim：作者自己的低频日内 bot 以 trendline detection 为核心指标，并通过大量参数回测选择当日策略配置。
- 结构定义关键词：trendline_detection / day_trading / OCO / backtesting_permutations
- 市场 / 频率 / 样本：股票日内；文章提到低频日内 bot，但未系统披露样本区间。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：核心依赖 pytrendline 做 trendline detection；同时叠加 news sentiment、SMA/EMA、inflection points。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：没有完整形式化。
- detection / confirmation / execution 是否分开：部分分开，但更偏工程经验分享。

### 3) 它给出了什么证据？
- 是否有回测：有“成千上万参数回测”的表述，但没有论文级结果表与统计检验。
- 关键结论：说明 pytrendline 确实源自作者自己的交易/回测实践，而不只是玩具仓库。
- 是否讨论交易成本 / 滑点：未见系统讨论。
- 是否有 OOS / rolling / cross-asset：未见。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：有仓库，但此文主要是工程说明。
- clean-room 复现难度：medium
- 风险标记：unclear_execution, no_cost_model
- 是否疑似未来函数 / 重绘：文章未充分说明。

### 5) 对我们的价值
- fit_for_us: explainability_reference
- 推荐动作：digest / park
- 为什么：它证明仓库背后有真实交易背景，但证据质量还不足以直接当 alpha 论文使用。

## Support Resistance Levels towards Profitability in Intelligent Algorithmic Trading Models

- source_type: paper
- year: 2022
- authors: Chan, Phoong, Cheng, Chen
- link: https://www.mdpi.com/2227-7390/10/20/3888
- doi_or_ssrn: https://doi.org/10.3390/math10203888
- github:
- license:
- fulltext_access: full_text
- evidence_status: parked

### 1) 它在研究什么？
- 一句话 alpha claim：把自动化 support/resistance 特征加入智能交易模型后，聚合盈利表现提升 65%。
- 结构定义关键词：support_resistance_feature / breakout / feature_engineering
- 市场 / 频率 / 样本：8 个货币对；论文主场景是智能交易模型。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：重点是自动化识别 meaningful support/resistance，并把它们编码成模型输入。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：偏特征工程，不是纯事件研究。
- detection / confirmation / execution 是否分开：基本分开。

### 3) 它给出了什么证据？
- 是否有回测：有。
- 关键结论：加入 S/R input features 后，模型聚合盈利改善且盈利分布差异显著。
- 是否讨论交易成本 / 滑点：摘要层面未充分展开。
- 是否有 OOS / rolling / cross-asset：至少有多货币对证据。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：当前未找到现成官方 GitHub。
- clean-room 复现难度：medium
- 风险标记：no_code
- 是否疑似未来函数 / 重绘：需在复现时重点审线位构造的 causal 边界。

### 5) 对我们的价值
- fit_for_us: feature_candidate
- 推荐动作：reference only / park faithful replication
- 为什么：方向有启发，但当前缺完整方法细节与官方代码；已完成规范提取与一版 clean-room 试跑，现阶段先收口为 literature / feature reference。

## Technical analysis in cryptocurrency markets: Do transaction costs and bubbles matter?

- source_type: paper
- year: 2022
- authors: Svogun, Bazán-Palomino
- link: https://www.sciencedirect.com/science/article/pii/S1042443122000816
- doi_or_ssrn: https://doi.org/10.1016/j.intfin.2022.101601
- github:
- license:
- fulltext_access: full_text
- evidence_status: replication_candidate

### 1) 它在研究什么？
- 一句话 alpha claim：crypto 里的技术分析规则并非全部失效，但一旦扣交易成本，能活下来的规则会显著减少，而且 bubble regime 会改写结果。
- 结构定义关键词：breakout / trend / crypto / transaction_cost / regime
- 市场 / 频率 / 样本：BTC、ETH、XRP、LTC、BCH；1-min 与 1-day。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：更偏规则族比较（含 breakout 类），不是单一 trendline 论文。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：有限。
- detection / confirmation / execution 是否分开：以规则回测为主。

### 3) 它给出了什么证据？
- 是否有回测：有。
- 关键结论：扣成本后仍有少数规则存活，但超短频最容易被摩擦成本吃掉；bubble regimes matter。
- 是否讨论交易成本 / 滑点：有，这是它的核心价值。
- 是否有 OOS / rolling / cross-asset：有多资产和多频率比较。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：论文有规则族描述，但未见官方开源仓库。
- clean-room 复现难度：medium
- 风险标记：no_code
- 是否疑似未来函数 / 重绘：需在具体 breakout 定义层自行审查。

### 5) 对我们的价值
- fit_for_us: filter_candidate
- 推荐动作：digest / replication brief
- 为什么：它非常适合做“alpha 生存性约束”，防止把纸面 breakout 当成可交易 alpha。
- 当前状态：`deep dive done` + `replication brief done` + `experiment v1 done`
- clean-room 入口：
  - `reading/svogun2022_cost_regime_replication/report.html`
  - `reading/svogun2022_cost_regime_experiment/report.html`

## (Re-)Imag(in)ing Price Trends

- source_type: paper
- year: 2023
- authors: Jiang, Kelly, Xiu
- link: https://doi.org/10.1111/jofi.13268
- doi_or_ssrn: https://doi.org/10.1111/jofi.13268
- github:
- license:
- fulltext_access: abstract_only
- evidence_status: deep_dive_done

### 1) 它在研究什么？
- 一句话 alpha claim：价格路径形状本身可能携带独立于朴素动量的可预测信息。
- 结构定义关键词：price_structure / trend / path_shape / breakout_context
- 市场 / 频率 / 样本：论文主场景不是专门 trendline，但与结构事件研究高度相关。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：更上游的路径形状学习，不是单个 trendline 工具。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：没有直接给交易层事件树。
- detection / confirmation / execution 是否分开：主要提供结构有信息的理论/实证框架。

### 3) 它给出了什么证据？
- 是否有回测：有实证 alpha 论证。
- 关键结论：路径结构是独立信息源，支持我们把 breakout / confirmation 看成结构特征工程问题。
- 是否讨论交易成本 / 滑点：不是这篇主重点。
- 是否有 OOS / rolling / cross-asset：论文层面较强，但不直接等同于可复制交易规则。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：未见简洁的开源规则仓库。
- clean-room 复现难度：high
- 风险标记：no_code
- 是否疑似未来函数 / 重绘：主要风险是“结构抽取复杂、与我们当前引擎不一一对应”。

### 5) 对我们的价值
- fit_for_us: mainline_event_source
- 推荐动作：deep dive / park for direct replication
- 为什么：它更适合作为理论母体与 feature 设计指导，不适合作为第一批直接复刻的规则仓库。

## The Support and Resistance Line Method: An Analysis via Optimal Stopping

- source_type: working_paper
- year: 2021 / 2025 v2
- authors: Henderson, Jacka, Liu, Maeda
- link: https://arxiv.org/abs/2103.02331
- doi_or_ssrn: https://doi.org/10.48550/arXiv.2103.02331
- github:
- license:
- fulltext_access: full_text
- evidence_status: digest_done

### 1) 它在研究什么？
- 一句话 alpha claim：support / resistance 更像 path-dependent regime switching 下的最优停时问题，而不是简单的“见线就追”。
- 结构定义关键词：support_resistance / breakout / regime / confirmation / optimal_stopping
- 市场 / 频率 / 样本：数学建模 working paper，不是特定市场的分钟级实证回测。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：把隐藏价位与 regime 切换联系起来，区分 line touch、line break 与 confirmed regime switch。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：有机制上的分层，但不是工程化事件树实现。
- detection / confirmation / execution 是否分开：是。更偏机制层与 optimal stopping 框架。

### 3) 它给出了什么证据？
- 是否有回测：不是经验回测型论文。
- 关键结论：反抽确认 / 回踩确认可以被理解为“是否真的发生 regime switch”的证据，而不只是经验主义过滤器。
- 是否讨论交易成本 / 滑点：不是主重点。
- 是否有 OOS / rolling / cross-asset：否，更偏理论机制。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：无现成交易规则代码。
- clean-room 复现难度：medium
- 风险标记：no_code
- 是否疑似未来函数 / 重绘：不属于这篇主风险；主要风险是理论框架到实盘定义的映射误差。

### 5) 对我们的价值
- fit_for_us: filter_candidate
- 推荐动作：digest / deep dive
- 为什么：它非常适合做 confirmation / retest 的机制解释与系统分层参考，但不适合作为第一批直接规则复刻对象。

## Betting on bitcoin: a profitable trading between directional and shielding strategies

- source_type: paper
- year: 2021
- authors: De Angelis, De Marchis, Marino, Martire, Oliva
- link: https://link.springer.com/article/10.1007/s10203-021-00324-z
- doi_or_ssrn: https://doi.org/10.1007/s10203-021-00324-z
- github:
- license:
- fulltext_access: full_text
- evidence_status: digest_done

### 1) 它在研究什么？
- 一句话 alpha claim：在短周期 BTC 中，把方向预测与交易边界分开，并允许 `no-trade band / threshold`，可能比“碰边界就交易”更能控制损失。
- 结构定义关键词：breakout_threshold / no_trade_band / shielding / confirmation_filter / intraday_crypto
- 市场 / 频率 / 样本：BTC 1 分钟数据；预测窗口 60/90/120 分钟；是短周期 crypto 上的边界交易研究，不是传统 trendline 论文。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：不是画 trendline，而是先给出方向/路径预测，再用独立 boundary 决定做多 / 做空 / no-trade；本质上属于“边界触发 + 阈值带 + wait-and-see”。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：有。虽然不用同一套术语，但它明确区分“触边”“越界到足够距离”“边界附近不交易/等待”。
- detection / confirmation / execution 是否分开：相对较清楚。方向层与交易触发边界是分开的，执行层也与单纯预测层分离。

### 3) 它给出了什么证据？
- 是否有回测：有。
- 关键结论：作者声称 boundary-based 方案相较 MA/MACD/Stochastic 在部分窗口上更能压低损失与回撤；对当前项目最重要的启发是“先定义 no-trade band / threshold，再决定何时把边界触碰升级成真实 breakout”。
- 是否讨论交易成本 / 滑点：未见系统纳入交易成本；更偏纸面策略比较。
- 是否有 OOS / rolling / cross-asset：未见强 OOS / rolling / cross-asset 设计；主要是单资产 BTC 场景。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：未找到公开官方代码；全文页可访问，但目前未发现明确 GitHub 入口。
- clean-room 复现难度：medium
- 风险标记：no_code
- 是否疑似未来函数 / 重绘：主风险不在 repaint，而在于路径预测 + boundary 设定若处理不当，容易把预测层与交易层混在一起；做 clean-room 时应先保留最小 causal 版本（先不用 LSTM，只保留 threshold/no-trade 思想）。

### 5) 对我们的价值
- fit_for_us: filter_candidate
- 推荐动作：digest / replication brief
- 为什么：它不是 trendline 主母体，但对当前 breakout-confirmation 体系非常有价值，因为它直接回答“为什么碰线后不应该立刻交易”，很适合转写成 15m crypto 的 `τ-band / no-trade zone / wait-and-see` clean-room 对照实验。
- 当前状态：`digest_done`
- clean-room 入口：
  - 先固定最简单方向层（如 EMA bias）
  - 再对 Donchian / session range / rolling box 加 `τ-band`
  - 做 `裸 breakout vs τ-band vs 2-of-3 closes outside vs retest_hold` 的最小对照

## Energy crypto currencies and leading U.S. energy stock prices: are Fibonacci retracements profitable?

- source_type: paper
- year: 2022
- authors: Ikhlaas Gurrib, Mohammad Nourani, Rajesh Kumar Bhaskaran
- link: https://jfin-swufe.springeropen.com/articles/10.1186/s40854-021-00311-8
- doi_or_ssrn: https://doi.org/10.1186/s40854-021-00311-8
- github:
- license:
- fulltext_access: full_text
- evidence_status: digest_done

### 1) 它在研究什么？
- 一句话 alpha claim：Fibonacci 回撤位本身可以生成交易收益，但更像 pullback / breakout 的结构确认层；单独拿来做 alpha 主体时，风险收益比并不稳定。
- 结构定义关键词：fibonacci_retracement / pullback / support_resistance / confirmation / breakout
- 市场 / 频率 / 样本：10 只美国能源股 + 4 个能源相关 crypto；日频；2017-11 到 2020-01。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：先用 swing high / low 定义 Fibonacci 回撤位（23.6 / 38.2 / 50 / 61.8 / 78.6），再用“触及 / 上穿 / 下破关键回撤位”触发交易；另有 `Fibonacci + 50-day MA crossover` 的对照。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：有部分分层。它没有完整 trendline event tree，但明确区分“触位”“跨位”“短窗口连续突破”以及“额外均线确认”。
- detection / confirmation / execution 是否分开：部分分开。结构层（回撤位）与额外确认层（MA crossover）分开，但 execution / cost 层较弱。

### 3) 它给出了什么证据？
- 是否有回测：有。
- 关键结论：Fibonacci-only 在部分标的上能给出较高总收益，但 Sharpe / Sharpe per trade 普遍偏弱；叠加 50-day MA crossover 后交易次数显著下降，整体没有稳定改善。更可迁移的发现是：连续回撤位突破主要集中在 1 天内，说明确认窗口应偏短。
- 是否讨论交易成本 / 滑点：未见完整交易成本建模。
- 是否有 OOS / rolling / cross-asset：没有严格 OOS / rolling；有跨资产（能源股 + 能源 crypto）对照，但样本规模不大。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：未见官方代码；规则定义可读，能 clean-room 重写。
- clean-room 复现难度：medium
- 风险标记：no_code, no_cost_model, sample_too_thin
- 是否疑似未来函数 / 重绘：主风险不在 repaint，而在 swing high/low 与回撤位更新若实现不当，容易把 hindsight 结构直接前置到交易决策；做本地复现时应先固定 causal swing 定义。

### 5) 对我们的价值
- fit_for_us: filter_candidate
- 推荐动作：digest / secondary replication brief
- 为什么：它最值得复用的不是参数，而是“把回撤位当确认层、并把确认窗口压短”的思路；很适合转写成 15m crypto 的 pullback / breakout confirmation 对照实验，但当前证据还不够支持直接升为第一批 active replication 主候选。
- 当前状态：`digest_done`
- clean-room 入口：
  - 固定方向层（如 `EMA50 vs EMA200` 或既有 breakout bias）
  - 用 recent-window swing high/low 计算 `23.6 / 38.2 / 50 / 61.8` 回撤位
  - 做 `裸 pullback entry vs confirm-1bar vs confirm-2of3 vs retest-hold` 的最小对照
  - 重点看 `false_break_ratio / max_drawdown / post_cost_return`

## Multi Indicator based Hierarchical Strategies for Technical Analysis of Crypto market Paradigm

- source_type: paper
- year: 2023
- authors: V. S. S. K. R. Naganjaneyulu, Prashanth G., Revanth M., A. V. Narasimhadhan
- link: https://ijeces.ferit.hr/index.php/ijeces/article/download/2517/322
- doi_or_ssrn: https://doi.org/10.32985/ijeces.14.7.4
- github:
- license:
- fulltext_access: full_text
- evidence_status: digest_done

### 1) 它在研究什么？
- 一句话 alpha claim：单一指标不该吃所有行情；更稳妥的做法是先识别 `Uptrend / Downtrend / Fluctuating`，再切换不同 indicator stack，并在 Downtrend 里限制 BUY。
- 结构定义关键词：regime_switch / trend_filter / confirmation_filter / loss_protection / indicator_stack
- 市场 / 频率 / 样本：BTC；日频；2018–2022。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：它不是 trendline 论文，核心结构不是线，而是 `EMA(RSI)` 驱动的 regime 分类：`>60` 视为 Uptrend、`<40` 视为 Downtrend、其余视为 Fluctuating；再按 regime 选择 EMA / RSI / PSAR 的动作逻辑。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：有部分分层。它没有完整 breakout event tree，但把“方向判断（regime）”“允许交易的状态”“执行/保护动作”拆开了。
- detection / confirmation / execution 是否分开：相对清楚。regime 判断先于交易动作；MIHCS 进一步把“某些 regime 下不允许 BUY”显式写成约束层。

### 3) 它给出了什么证据？
- 是否有回测：有。
- 关键结论：作者声称 `MIHCS7`（EMA7 on RSI + regime-constrained actions）在 BTC 日频 2018–2022 的 consolidated profit percentage 约为 `701.8%`，高于单独 EMA 的 `394.1%`。对我们最重要的启发不是收益数值，而是：**先分 regime，再决定 breakout / pullback / protection 规则**，比让同一套规则吃所有行情更合理。
- 是否讨论交易成本 / 滑点：未见扎实成本敏感性分析。
- 是否有 OOS / rolling / cross-asset：没有强 OOS / rolling；基本是单资产 BTC。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：未见公开官方代码；规则口径可读，能做 clean-room 重写。
- clean-room 复现难度：medium
- 风险标记：no_code, no_cost_model, sample_too_thin
- 是否疑似未来函数 / 重绘：主风险不在 repaint，而在 regime classifier 与 indicator switch 的参数敏感性；若直接照抄日频阈值到 15m，较容易过拟合或误迁移。

### 5) 对我们的价值
- fit_for_us: filter_candidate
- 推荐动作：digest / source card / park
- 为什么：它最值得复用的不是 `MIHCS7` 的具体参数，而是 **regime gate** 这个设计原则——在 15m crypto 里，更适合把它转写成 `先分 Uptrend / Downtrend / Fluctuating，再决定是否允许 breakout continuation / pullback long / strict confirmation` 的约束层，而不是把论文本体升成主 replication candidate。
- 当前状态：`digest_done`
- clean-room 入口：
  - 先用最小 regime classifier（如 `EMA50 > EMA200` 且 slope>0 / `<` 且 slope<0 / 其余为震荡）
  - 再比较 `不分 regime 的裸 breakout` vs `仅在 Uptrend 允许 breakout long` vs `Fluctuating 需更严确认`
  - 重点看 `false_break_ratio / post_cost_return / drawdown` 是否先被 regime gate 压下来

## Technical Analysis for Buy or Sell Decisions in Cryptocurrency (Bitcoin)

- source_type: paper
- year: 2024
- authors: Hartsa Fayi Yumna, M. Taufiq, Anisa Fitria Utami
- link: https://ejournal.media-edutama.org/index.php/jebisma/article/download/68/77
- doi_or_ssrn:
- github:
- license:
- fulltext_access: full_text
- evidence_status: digest_done

### 1) 它在研究什么？
- 一句话 alpha claim：breakout 不能只看“穿过去了没”，还要看 `volume confirmation`、`resistance becomes support`、以及后续是否形成 `higher low / higher high`；这些确认层比单纯追突破本身更接近可执行规则。
- 结构定义关键词：breakout_confirmation / volume_filter / support_flip / higher_low / confirmation_filter
- 市场 / 频率 / 样本：BTC；周频；2022-06 到 2023-10。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：以水平 support / resistance、常见 bullish chart patterns、MA200 与成交量配合判断买卖；关键不是形态名称本身，而是 breakout 之后是否放量、是否站稳旧阻力、以及是否形成 higher low。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：有。它虽然不是严格事件研究，但实际上把 `breakout`、`volume confirmation`、`support flip / retest`、`higher low persistence` 依次排成了一条确认链。
- detection / confirmation / execution 是否分开：部分分开。结构触发、确认层、方向背景（MA200）可以区分，但执行与成本层很弱。

### 3) 它给出了什么证据？
- 是否有回测：没有系统化大样本回测，更像定性案例研究。
- 关键结论：文中反复强调 **显著放量的 breakout 才更可信**，以及 **突破后旧阻力转新支撑、再形成 higher low** 才更像延续而非假突破。对我们最重要的启发不是“某个形态赚钱”，而是把 `volume + support flip + higher low` 当成客观 confirmation layer。
- 是否讨论交易成本 / 滑点：未见扎实讨论。
- 是否有 OOS / rolling / cross-asset：没有；基本是单资产 BTC 的周频案例。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：未见公开官方代码；规则逻辑可读，能做 clean-room 重写。
- clean-room 复现难度：low_to_medium
- 风险标记：no_code, no_cost_model, sample_too_thin, unclear_execution
- 是否疑似未来函数 / 重绘：主风险不在 repaint，而在定性形态描述若不转成客观事件定义，容易产生后见解释；本地吸收时应优先把 `放量阈值 / support-flip / higher-low` 写成明确规则。

### 5) 对我们的价值
- fit_for_us: filter_candidate
- 推荐动作：digest / source card / park
- 为什么：它不是高证据强度的 alpha 论文，但和当前 15m 主线非常贴：最值得迁移的是 `volume filter + support flip / higher-low persistence` 这一整套假突破过滤层。更适合当 `confirmation / filter reference`，而不是主 replication candidate。
- 当前状态：`digest_done`
- clean-room 入口：
  - 先用最简单的横向边界（`Donchian20` 或 pivot-based resistance）定义 breakout
  - 再比较 `裸 breakout` vs `放量 breakout` vs `support-flip` vs `higher-low confirm` vs `组合版`
  - 重点看 `false_break_ratio / time_to_failure / retest_hold_rate / post_cost_return`

## Technical Analysis as a Tool for Determining Cryptocurrency Trends in Times of Chaos

- source_type: paper
- year: 2024
- authors: Bartłomiej Wiśniewski
- link: https://czasopisma.uni.lodz.pl/em/article/view/23156
- doi_or_ssrn: https://doi.org/10.18778/2082-4440.46.01
- github:
- license:
- fulltext_access: full_text
- evidence_status: digest_done

### 1) 它在研究什么？
- 一句话 alpha claim：趋势线不是“连两点就能交易”的信号；更合理的做法是先等第三次结构确认，再要求 EMA / MACD 共识，避免把第一次弱突破直接当成可执行 entry。
- 结构定义关键词：trendline_breakout / third_touch / confirmation_filter / ema_filter / macd_filter
- 市场 / 频率 / 样本：BTC、ETH；周频；2018–2023。

### 2) 它怎么定义结构？
- line / support-resistance / channel / pivot / confirmation 的定义：核心是手工 trendline / support-resistance 判读，作者反复依赖 `third peak / third vertex / three lows` 来确认趋势线与结构是否成立；EMA30 与 MACD(12,26,9) 作为方向与动量共识层。
- 有没有明确事件层次（breakout / rebound / retest / confirm）：有部分分层。它没有规范化 event tree，但实际上把 `candidate line`、`third-touch confirmation`、`breakout`、`EMA/MACD alignment` 逐层拆开了。
- detection / confirmation / execution 是否分开：部分分开。结构层和方向共识层能分开，但执行、成本与持仓层并不扎实。

### 3) 它给出了什么证据？
- 是否有回测：没有系统化大样本规则回测，更像案例研究 + 图表判读。
- 关键结论：作者强调单看 breakout 或单看 EMA/MACD 往往只给出弱信号，甚至互相冲突；更可靠的是 **trendline 结构确认后，再看 EMA/MACD 是否同向**。对我们最重要的启发不是收益数字，而是：**第三次确认 + 共识过滤** 比“第一次穿线就追”更值得工程化。
- 是否讨论交易成本 / 滑点：未见扎实讨论。
- 是否有 OOS / rolling / cross-asset：没有强 OOS / rolling；虽有 BTC / ETH 两资产，但本质仍是低频案例分析。

### 4) 可复现性与风险
- 是否有代码 / 伪代码：未见公开官方代码；逻辑可以 clean-room 重写，但原文主观成分较高。
- clean-room 复现难度：medium
- 风险标记：no_code, no_cost_model, sample_too_thin, unclear_execution
- 是否疑似未来函数 / 重绘：主风险不在 repaint，而在主观趋势线与“第三个点”若不写成客观 pivot / close-outside 规则，容易后见解释。

### 5) 对我们的价值
- fit_for_us: filter_candidate
- 推荐动作：digest / source card / park
- 为什么：它不是高证据强度 alpha 论文，但非常适合支持当前 15m 的 `third-touch / confirm_1~2 / retest_hold + EMA/MACD` clean-room 设计。更适合当 `confirmation / filter reference`，而不是 replication shortlist 主候选。
- 当前状态：`digest_done`
- clean-room 入口：
  - 用客观 pivots 先定义 candidate trendline
  - 仅在 `third-touch confirmed` 后才允许 breakout 事件进入候选池
  - 比较 `裸 breakout` vs `confirm_2of3` vs `EMA slope 同向` vs `EMA+MACD 共识`
  - 重点看 `false_break_ratio / outside_bar_persistence / time_to_failure / post_cost_return`

## 第一版 replication shortlist（2026-03-13）

> 这份 shortlist 是在当前 intake queue 规模还不大、且已知 `Chan 2022` 已 park、`Jiang/Kelly/Xiu 2023` 暂不适合直接 faithful replication 的前提下，先选出的 **第一批 4 个 clean-room replication / bridge candidates**。

### 1. Svogun & Bazán-Palomino (2022)
- shortlist_role: filter / constraint replication
- 为什么入选：全文可得，问题直接约束当前 breakout / trend 研究，且已完成 brief + experiment v1，最适合继续往成本 / regime 约束上深化。
- 近期动作：继续作为 `active` 候选保留。

### 2. pytrendline (GitHub repo)
- shortlist_role: mainline event-source bridge
- 为什么入选：有代码、结构定义清楚、和当前 unified event schema / source bridge 主线直接相连，最适合做 clean-room bridge 与 explainability 对照。
- 近期动作：优先补 bridge / source audit，而不是把 repo 直接当交易系统。

### 3. trendln (GitHub repo)
- shortlist_role: geometry / channel baseline
- 为什么入选：有代码、extrema → line search → line quality 的拆法清楚，适合作为 support-resistance / channel 的几何 baseline。
- 近期动作：作为 `secondary` 候选保留；优先级低于 pytrendline，因为与当前主线贴合度稍弱。

### 4. The Support and Resistance Line Method: An Analysis via Optimal Stopping
- shortlist_role: confirmation / retest mechanism candidate
- 为什么入选：全文可得，最适合支持 confirmation / retest / regime-switch 机制设计，能直接反哺当前 mainline 的 protocol layer。
- 近期动作：优先补 deep dive / protocol mapping，而不是做 faithful paper replication。

### 当前明确不进 shortlist 的对象
- `Chan 2022`：已 park，保留为 feature reference。
- `Jiang/Kelly/Xiu 2023`：理论价值高，但当前 `abstract_only + high difficulty`，更适合作为上游理论母体，不进入第一批直接 replication shortlist。
- `Ed Nunez blog`：更像工程背景材料，不单列为 replication 主候选。
