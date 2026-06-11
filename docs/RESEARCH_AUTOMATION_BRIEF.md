# RESEARCH_AUTOMATION_BRIEF

> 用途：给定时研究任务（cron）提供统一执行规范。
> 目标：围绕 **Crypto 短周期量化策略**（默认 `5m / 15m`，也接受 `1m / 3m` 的更快高强度 alpha），持续积累可复刻的论文、GitHub 仓库、因子思路与工程实现线索。

## Authoritative Priority Note（2026-03-23）

本文件当前只应被理解为 **Scout 的研究辅助引擎**。
它默认服务于：**找下一条值得 intake、能快速验证、能尽快进入 `P2 / P3` 的候选**。

也就是说：
- research / digest 默认服务于 **找下一条更快进入 `P3 / Paper launch queue` 的候选**；
- 不应把资源拉去 autonomous paper 监控、interrupt 维护、tiny-live 或 live-shadow；
- 若一个研究选题不能帮助 desk 更快回答“这条 alpha / 策略靠不靠谱”，它就应降低优先级；
- **更重要的是：Scout 当前不是泛研究入口，而是快验证入口**，默认优先那些能快速进入 `first verdict / clean replication / admission check` 的候选。

## 总目标

每次运行只做 **1 个小主题**，产出一篇简短但扎实的研究笔记。

### 论文 / 外部材料的最高优先级规则（新增，强约束）

如果候选论文 / 外部研究同时满足下面 4 个条件，才属于**最高优先级**：

1. **近期**：默认优先最近 5 年；
2. **靠谱**：来源可信（正规期刊 / working paper / SSRN / arXiv / 研究者主页 / 领域内有明确信誉的作者或机构）；
3. **有公开仓库或代码**：至少存在 GitHub / 代码仓 / 清晰伪代码 / 可直接复刻实现；
4. **能拿到全文**：不仅能看到摘要，最好能直接获取全文页面、PDF、working paper 完整正文，便于真正读方法与实验细节。

执行时的默认排序规则：
- **四项同时满足** → 最优先选题；
- 缺 1 项 → 可保留为候选，但优先级下调；
- 若只能看到摘要 / 结论、拿不到正文 → 只可作为**弱线索**，不应作为主线 digest、deep dive 或 replication candidate 的优先对象。

核心原则：**只看摘要和结论，对当前研究主线帮助有限**。后续定时任务应尽量把注意力放到“能真正读懂方法、读懂实验、并能复刻”的材料上。

优先服务于：

- **raw alpha 家族**：trend / momentum / breakout / mean reversion / cross-sectional / relative value / stat-arb / pairs / carry / funding / basis
- **alpha 的确认与增强层**：pullback / retest / volume confirmation / continuation-confirmation
- regime / filter / risk / sizing overlay
- execution / slippage / cost / microstructure
- 适合短周期（默认 `5m / 15m`，也接受 `1m / 3m`）Crypto 的可复刻思路

## 当前阶段优先级（重要）

当前用户的核心诉求是：**先找到基础 alpha，再谈仓位、风控和执行层优化**。

因此在未来一段时间内，选题优先级调整为：

1. **先找 raw alpha**：默认包括 trend / momentum / breakout，也包括 mean reversion、cross-sectional / relative value、stat-arb / pairs、carry / funding / basis
2. **优先完整策略可落地**：同质量下，优先具备 `entry / exit / sizing / risk / cost` 全链条定义、可直接进入复现与实盘候选池的主题
3. **基础 alpha 的工程实现优先**：可直接启发当前 `momentum` 项目的信号定义、确认规则与组合方式
4. **filter / regime / risk / sizing 可以研究，但默认要明确它服务于哪个 raw alpha**
5. **如果一个来源只能产出 filter，却说不清 base alpha 是什么，则优先级下调**
6. **快验证优先于大而全研究**：默认优先那些能在短时间内完成 `first verdict`、快速补最小成本检验、并快速进入 `clean replication / admission check` 的候选
7. **连续两篇非 raw alpha 后，下一篇默认必须回到 raw alpha 或完整策略主题（除非明确写出无合格候选）**

如果在一个主题上拿不准，默认按以下**内部判断规则**排序：
- 更接近“帮助用户找到基础 alpha”的主题，优先级更高
- 更接近“优化一个尚未成立的策略”的主题，优先级更低

注意：这是定时任务的内部排序规则，**不需要向用户发问或请求确认**；定时任务应在无人工干预的情况下独立完成选题、整理与讲解。

## Scout 候选准入与排序（authoritative）

当前若一个候选想占用 `Scout` 主资源，默认优先满足下面 5 条：

1. **数据源稳定可获取**
2. **规则可清楚写成 `trade on / trade off`**
3. **能在短时间内完成 `first verdict`**
4. **能快速做 `friction ladder`**
5. **能快速进入 `clean replication / admission check`**

默认排序规则：
- **第一优先级**：最简单、最可实现、最可复核的短周期候选（默认以 `5m / 15m` 为稳健基线；若 `1m / 3m` 能明显缩短研发周期且成本后仍有生存空间，也可优先）
- **第二优先级**：能快速加成本并验证 `trade count` 的候选
- **第三优先级**：只有在前两类不足时，才考虑更复杂的数据源或模型

明确边界：
- Scout **可以不局限于结构类信号**；
- 但它**不得滑成泛研究入口**；
- 当前目标是尽快获得 `first verdict / clean replication / admission` 证据，而不是追求完美研究报告。

## 按最近学习进展推荐（重要）

定时任务不只是机械找论文，而要**结合用户最近一段时间与 AI 学量化的进展**来推荐下一篇内容。

默认做法：
1. 先判断用户当前学到哪一层：
   - 基础 alpha 本体
   - alpha 增强 / 确认层
   - 环境过滤 / 风控 / 仓位
   - 执行 / 成本 / 微观结构
2. 优先推荐**正好衔接下一步**的论文，而不是跳层推荐。
3. 若最近几次 digest 已经覆盖某一层，下一次优先补相邻缺口，而不是重复同类主题。
4. 若当前项目文档显示用户还处在“找基础 alpha”阶段，则推荐应继续围绕 alpha 本体展开，不要过早转向二层优化。

### 当前额外兴趣焦点（动态）

当前 bot7 不应围绕某个固定形态（如 breakout / retest / trendline）持续内循环。

因此在接下来一段时间里，若存在多个同质量候选主题，默认优先比较：
- 哪个更接近独立 raw alpha
- 哪个更容易拆成 `base alpha / regime / filter / overlay`
- 哪个更容易进入复现、first verdict 与后续实盘素材池

若 `mean reversion / cross-sectional / relative value / stat-arb / pairs` 与结构突破类候选质量接近，应优先保证前者也持续进入 intake，而不是长期只做结构型主题。

## 运行前必读

每次运行前，先读：

1. `docs/MAINLINE1_STRATEGY_FACTOR_MAP.md`
2. `docs/FACTOR_BACKLOG.md`
3. `docs/LEARNING_TRACK.md`
4. `research/quant_digests/INDEX.md`

如果有需要，再查看最近 1~3 篇 digest 源文件，以判断最近已经讲过什么。

目的：
- 避免重复主题
- 根据最近学习进展决定下一篇推荐什么
- 优先补当前主线缺口
- 保持研究朝“最终做出短周期完整策略（`1m / 3m / 5m / 15m`）”这个方向推进

## 选题优先级

优先选择以下 3 类内容之一：

### A. 经典或高质量论文
要求：
- 与 raw alpha、regime、risk、execution 中至少一类直接相关；其中 raw alpha 默认包括动量 / 趋势 / breakout / mean reversion / cross-sectional / relative value / stat-arb / pairs / carry / funding / basis
- 最好有较明确的实证结论
- 尽量不是纯长周期资产配置论文，除非其中的思想可迁移到短周期 Crypto
- **默认优先最近 5 年论文**，尤其是更贴近当前学习阶段的更新研究
- 优先选择 **来源靠谱 + 有公开仓库/代码 + 能拿全文** 的论文
- 经典老论文可以引用，但应作为“概念地基 / 学术母体 / 必要补充”，而不是默认优先项
- 优先使用可直接访问的 DOI / 出版商页面 / arXiv / SSRN / working paper 页面；若能拿 PDF / 全文页，优先级更高
- 如果只能看到摘要 / 简短结论，看不到全文，则默认不进入最高优先级

## 资料获取降级策略（重要）

外部检索不是单点依赖。按下面顺序取材：

1. 先看项目内已有种子资料：
   - `reports/artifacts/literature/validated_alpha_shortlist_2026-03-10.md`
   - `docs/RECENT_PAPER_SEEDS.md`
2. 优先选那些**能直接拿到全文 / PDF / working paper 正文** 的候选
3. 若可用，优先使用免 API key 的 `n2-free-search` 技能（例如 `n2_web_search` / `n2_news_search`）
4. 再使用可直接访问的 DOI / 出版商 / SSRN / arXiv / working paper URL 配合 `web_fetch`
5. `web_search` 只是加速项，不是硬依赖

如果 `web_search` 不可用（例如缺 API key），**不要因此中止任务**；应优先回退到 `n2-free-search` 或项目内种子清单 + 直接 URL 抓取，并继续完成产出。

但注意：
- 如果最后仍然只能拿到摘要 / 标题页，看不到正文，就把该来源标记为 `abstract-only / weak-evidence`；
- `abstract-only` 来源可以进入候选池，但默认不进入：
  - 高优先级 digest
  - deep dive
  - replication shortlist

### B. 有参考价值的 GitHub 仓库
要求：
- 代码可读、结构清晰、不是明显废弃仓库
- 最好包含：因子实现、信号逻辑、回测框架、成本处理、组合逻辑中的至少一项
- 优先找能启发当前 `momentum` 项目结构的实现

### C. 一个“被反复提及、值得验证”的小知识点
例如：
- breakout 为什么容易在低波动压缩后更有效
- ATR 更适合做止损器还是过滤器
- volume spike 在假突破中的角色
- funding / liquidity / spread 对短周期策略的侵蚀路径

注意：**不要把“社区流行说法”写成已被严格验证的事实。**
必须明确标注证据类型：
- `论文证据`
- `工程经验`
- `社区经验/待验证`

## 输出位置

每次运行：
- 新建一篇笔记到 `research/quant_digests/`
- 文件名格式：`YYYY-MM-DD_HHMM_topic-slug.md`
- 然后追加更新 `research/quant_digests/INDEX.md`

## 表达侧重点（重要）

保持现有研究笔记 / 邮件 / 聊天摘要的**大体结构不变**，不要把输出压缩成只剩 3 条。

但在原有结构里，要**更明显地突出**下面 3 件事：

1. **哪些内容值得复用 / 借鉴 / 学习 / 复现**
   - 如果是论文：优先指出可迁移的方法、特征定义、实验设计、评估框架
   - 如果是 GitHub：优先指出可直接参考的模块、算法骨架、参数语义、数据结构、可替代实现
   - 如果是知识点：优先指出哪些部分已经可计算，哪些还只是待验证假设
2. **一句话核心结论**
   - 用尽量朴素的中文，把“这篇东西最想告诉我们的是什么”讲清楚
   - 避免术语堆砌，优先写成用户一眼能懂的话
3. **一句话说明它是怎么证明这个结论的**
   - 说明它依赖的是：实证回测、跨市场样本、统计检验、数学建模、代码实现、案例对照中的哪一种
   - 目标是让用户迅速知道：这个结论的证据强度来自哪里

注意：这 3 点是**强调项**，不是替代项。原本的背景、关联性、最小实验、风险提示、来源信息仍然要保留。

## 网站同步（方案 B）

研究笔记不是只存 markdown，也要自动进入网站：

1. 先写入 `research/quant_digests/*.md`
2. 运行：`python3 scripts/build_quant_digest_site.py`
3. 这会自动生成：
   - `reports/site/reading/quant_digests/report.html`
   - `reports/site/reading/quant_digests/<slug>.html`
   - 并把入口挂到 `reports/site/index.html`
4. 如需对外发布，再执行：`bash scripts/publish_report_site.sh`

注意：后续新增 digest 时，默认应同步更新网页页，而不是只停留在 markdown。

## 单篇笔记模板

每篇笔记尽量控制在 **400~900 字正文**，结构如下：

```md
# 标题
- 时间：
- 类型：论文 / GitHub / 知识点
- 主题类型：raw alpha / filter / regime / overlay
- 基础 alpha：____
- 是否可独立复现：是 / 否
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是 / 否
- 主题标签：trend / momentum / breakout / volume / volatility / regime / execution / cost / microstructure
- 证据类型：论文证据 / 工程经验 / 社区经验/待验证

## 1. 这次看了什么
一句话说明来源和对象。

## 2. 核心结论
用 3~5 条 bullet 写清楚，不要空话。

## 3. 为什么和当前项目有关
明确连到 `momentum` 当前主线，说明它更像：
- 新因子候选
- 过滤器候选
- 风控/执行层改进
- 研究方法启发

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 逆势 / 横截面 / 相对价值
- 基础 alpha：____
- regime：____
- filter / veto：____
- risk / sizing / execution overlay：____

## 4. 可复刻的最小实验
给出一个很小的实验建议，强调可执行。
包括：
- 研究假设
- 一个可计算定义
- 最小回测切口（资产 / 周期 / 样本）
- 最该先看哪 1~2 个指标

## 5. 风险与保留意见
写清楚哪些地方可能失效、过拟合、不可迁移，或者仍缺证据。

## 6. 来源
若是论文，尽量按下面格式写清楚：
- Authors. (Year). Title. Venue / Journal.
- DOI: `...`
- Readable URL: `https://...`

若是 GitHub / 文章，也尽量给：
- 作者/组织名
- 项目/文章标题
- URL
```

## INDEX 追加格式

每次在 `research/quant_digests/INDEX.md` 末尾追加一行：

```md
- YYYY-MM-DD HH:MM | 类型 | 标题 | 标签 | 文件名
```

## 提交与版本留痕

完成笔记、索引与网页同步后，优先做一次**范围受控**的 git 提交：

```bash
git add \
  research/quant_digests/INDEX.md \
  research/quant_digests/<new-file>.md \
  reports/site/reading/quant_digests/<new-file>.html \
  reports/site/reading/quant_digests/report.html \
  reports/site/reading/quant_digests/index.html \
  reports/site/index.html

git commit -m "docs(research): add quant digest <topic-slug>"
```

要求：
- 只提交本次新增/修改的研究笔记、网页页与站点索引
- 不顺手提交其他无关文件
- 如果提交失败（例如仓库状态异常），在对外摘要里明确说明“已写文件但未成功提交”

## 对外汇报格式（发到聊天）

运行完成后，给聊天发一个简短中文摘要，控制在 **6 条以内**：

1. 这次主题
2. 1~2 个最关键结论
3. 为什么和 15m 策略有关
4. 下一步最小实验建议
5. 文件保存位置
6. 主要来源链接（1~3 个，论文需尽量附 DOI 或原文 URL）

额外要求：
- 在不打乱以上结构的前提下，尽量补进两句最值钱的话：
  - **一句话核心结论**：这篇研究最值得记住的判断是什么
  - **一句话证明方式**：作者/仓库主要是靠什么方法把这个判断撑起来的
- 如果空间允许，再补一小句：**最值得复用/复现的点是什么**
- 口吻优先用易懂中文，必要时把专业名词翻译成人话

## 选题约束

- 避免连续两次都讲同一类东西
- 若近期学习主线还明显停留在基础 alpha，则即使连续几次都是论文，也允许继续优先论文
- 如果最近连续讲了论文，且当前学习主线允许拓展，下次优先找 GitHub 或工程实现
- 如果最近连续讲了因子定义，下次优先讲执行/成本/微观结构
- 默认优先最近 5 年研究；经典论文仅在明显值得补地基时插入
- 永远围绕“最终做出能回测、能实盘的短周期完整策略（`1m / 3m / 5m / 15m`）”服务

## 邮件摘要写法（重要）

定时任务完成后发给默认收件人的邮件，仍然保留原先的大体信息量，但应优先让用户在几十秒内抓到重点。

推荐做法：
- 先保留原先已有字段：主题、2 个核心结论、与当前短周期（`1m/3m/5m/15m`）的关系、最小实验、文件路径、页面 URL、来源链接
- 邮件开头固定先给：主题类型、基础 alpha、是否可独立复现、是否可直接落地完整策略
- 再把下面 3 项以**短句**方式自然嵌进去：
  1. **可复用/可复现点**：这篇论文/仓库里最值得我们拿来试的是什么
  2. **一句话核心结论**：最该记住的判断
  3. **一句话证明方式**：它主要靠什么证据得出这个判断

建议邮件正文优先顺序：
1. 主题类型 + 基础 alpha + 可复现/可落地状态
2. 主题
3. 一句话核心结论
4. 一句话证明方式
5. 最值得复用/复现的点
6. 2 个核心结论
7. 与当前短周期（`1m/3m/5m/15m`）的关系
8. 最小实验
9. 文件路径 / 页面 URL / 来源链接

注意：
- 这是**强调顺序**，不是删减原信息
- 不要把邮件写成只剩 3 条的超短摘要
- 目标是“保留完整度，同时让用户更快抓住可执行价值”

## 禁忌

- 不要编造论文结论
- 不要把没有看过正文的内容说得很确定
- 只有摘要 / 结论、拿不到全文的论文，不要当成主线优先成果来讲
- 不要一次塞太多主题
- 不要把 `web_search` 失败当成任务失败；要按降级策略继续完成
- 若 `n2-free-search` 技能可用，优先把它作为无 key 搜索后备，而不是重复撞 Brave/Tavily 等需 key 路径
- 不要输出泛泛而谈的综述，必须给出一个可落地的小实验方向
