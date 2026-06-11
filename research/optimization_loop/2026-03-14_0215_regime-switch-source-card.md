# 给 regime-switch indicator stack 补正式来源卡：先当 regime gate 参考，不升主 replication candidate

## 为什么这次选这个

这轮我刻意没有继续在 `pytrendline_event_validation_v3` 的 breakout 三档排序上打转。

原因很简单：前几轮已经把 `support_breakout_raw / confirm_1 / confirm_2` 的 `h24` OOS honesty、split-specific excess、以及排序置信度都补到一个比较诚实的阶段了；如果继续对同一份 `validate+test` 小样本反复拧毛巾，信息增量会越来越低。

而当前自动优化节奏又是 **轻微偏向 E-track**，所以更合适的一小步，是把刚新增的 `Naganjaneyulu et al. (2023)` digest 往前推半步：
- 不做重型回测；
- 不再写一篇泛泛摘要；
- 直接判断它对当前 15m 研发到底是什么角色。

这轮最值得复用/借鉴的点是：**有些论文最值钱的不是它回测数字，而是它提供的“什么时候该交易 / 什么时候根本不该交易”的结构化约束。**

## 核心结论（中文摘要）

核心结论：**`Naganjaneyulu et al. (2023)` 当前更适合被正式归类为 `regime / filter reference`，而不是主 `replication candidate`；它最值得迁移的是“先分 Uptrend / Downtrend / Fluctuating，再决定是否允许 breakout / pullback 交易”的设计原则。**

证据如何支持这个结论：**这篇论文全文可得、规则分层清楚（regime → indicator switching / buy restriction），但证据边界也很明显——只有 BTC 日频、未见强 OOS / rolling / 成本敏感性分析，也没公开官方代码；因此它更适合支持本地 15m 的 `regime gate` clean-room 设计，而不适合直接照搬 `EMA(RSI)>60/<40` 与 `MIHCS7` 参数去当 replication 主线。**

## 本轮做了什么改动

本轮只做一个主点：**把 regime-switch 这条线从 digest 提升成正式来源卡 + 最小 intake judgement。**

具体动作：

1. 更新 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
   - 新增正式来源卡：
     - `Multi Indicator based Hierarchical Strategies for Technical Analysis of Crypto market Paradigm`
   - 写明：
     - `source_type = paper`
     - `fulltext_access = full_text`
     - `evidence_status = digest_done`
     - `fit_for_us = filter_candidate`
   - 明确其 clean-room 入口不是“照抄指标参数”，而是：
     - 先做最小 regime classifier；
     - 再比较 `不分 regime 的裸 breakout` vs `仅在 Uptrend 允许 breakout long` vs `Fluctuating 需更严确认`。

2. 更新 `docs/TODO.md`
   - 在 `E2-A / E2-B` 下补进度说明：
     - 这张卡已入候选池；
     - 当前更适合定位为 `regime / filter reference`；
     - 最小 clean-room 入口是先测 regime gate 是否能压低 15m 假突破与回撤。

3. 更新 scout 网页生成脚本
   - 修改 `scripts/build_trendline_alpha_scout_report.py`：
     - 在“首批种子材料”里加入 `Regime switch indicator stack`；
     - 在“第一轮侦察结论”里明确写死：
       - 这条线不进主 replication shortlist；
       - 它服务的是 `regime / filter` 设计原则。

4. 最小重建与发布
   - 重建：
     - `reports/site/reading/trendline_alpha_scout/report.html`
     - `reports/site/plans/momentum_todo.html`
   - 同步发布到站点镜像。

## 验证 / 证据

### 1) 为什么不把它升成主 replication candidate

因为它虽然“讲得通”，但还不够“可直接信任”：
- 资产：只有 BTC
- 频率：日频
- 样本：2018–2022
- 成本：未见扎实建模
- OOS / rolling：未见强设计
- 代码：未见公开官方实现

换成人话就是：
**这篇更像告诉你“策略应该先有状态判断”，但没有充分证明“你可以直接照它的参数挣钱”。**

### 2) 为什么它仍然值得保留

因为它对当前 15m breakout / pullback 研发有一个很强的工程启发：
- 不要默认所有市场状态都用同一套确认逻辑；
- 不该交易的时候，直接禁做某一类交易，本身就是规则的一部分；
- 这和我们最近在 v3 OOS 里看到的现象是相容的：
  - 某些 breakout 候选不是任何时候都同样有效；
  - holding frame / 状态过滤 / continuation 语境，很可能决定它到底更像 alpha 还是噪声。

### 3) 当前最合理的本地吸收方式

不是复刻：
- `EMA(RSI) > 60 / < 40`
- `MIHCS7`

而是先做最小版本：
- `Uptrend`：`EMA50 > EMA200` 且 slope > 0
- `Downtrend`：`EMA50 < EMA200` 且 slope < 0
- `Fluctuating`：其余

然后只问一个简单问题：
- **加这一层 regime gate，能不能先把 breakout long 的假突破率和回撤压下来？**

如果这一步都做不到，就没必要继续抄它的 indicator stack 细节。

## 风险 / 边界

- 这轮没有做本地回测，因此没有新增 alpha 结论；
- 它完成的是 intake discipline：把新 digest 从“读过了”推进到“知道该怎么用 / 不该怎么用”；
- 当前也没有把它加入 replication shortlist，只是把它稳定落到 `reading` / scout 侧。

## 下一步建议

如果后续再给这条线分配一轮，最小而真实的动作应是：

1. 先不碰复杂 indicator stack；
2. 只做一个极简 `regime gate`；
3. 对已有 15m breakout baseline 做对照：
   - 裸 breakout
   - 仅 Uptrend 允许 breakout long
   - Fluctuating 需更严确认
4. 重点看：
   - `false_break_ratio`
   - `post_cost_return`
   - `max_drawdown`
   - `trade_count`

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成来源卡、TODO、scout board 与日志/邮件同步，不做提交。