# 给 third-touch + EMA/MACD confluence 补正式来源卡：先当 confirmation/filter 参考，不升主 replication candidate

## 为什么这次选这个

这轮继续保持轻量 E-track，但不重复前两轮已经补过的 `regime gate` 和 `volume-confirmed breakout`。

更合适的一小步，是把已经有 digest 的 **Wiśniewski (2024)** 往前推成正式来源卡与最小 intake judgement。原因很明确：
- 它和当前 15m 结构研究主线很贴；
- 但它的证据强度并不够，不能直接被当成“趋势线 alpha 已被证明”；
- 所以最重要的不是再写一篇摘要，而是把它的角色写死，避免后面被误升成 replication 主线。

这轮最值得复用/借鉴的点是：**“第三次确认 + EMA/MACD 共识”更适合被理解成 confirmation/filter 设计原则，而不是一个可以直接照抄的可交易论文配方。**

## 核心结论（中文摘要）

核心结论：**`Wiśniewski (2024)` 当前更适合被正式归类为 `confirmation / filter reference`，而不是主 `replication candidate`；它最值得迁移的是“第三次结构确认后，再要求 EMA/MACD 共识”的设计原则。**

证据如何支持这个结论：**这篇材料全文可得、和当前结构主线贴得很近，但本质仍是 BTC/ETH 周频案例研究，没有系统化大样本回测、缺成本/OOS，也未见公开代码；因此不适合把周频趋势线案例直接当成已验证 alpha，但很适合把 `third-touch confirmation + EMA/MACD confluence` 转成 15m 的客观过滤层。**

## 本轮做了什么改动

本轮只做一个主点：**把 `Wiśniewski (2024)` 从 digest 提升成正式来源卡 + 最小 audit judgement。**

具体动作：

1. 更新 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
   - 新增正式来源卡：
     - `Technical Analysis as a Tool for Determining Cryptocurrency Trends in Times of Chaos`
   - 写明：
     - `source_type = paper`
     - `fulltext_access = full_text`
     - `evidence_status = digest_done`
     - `fit_for_us = filter_candidate`
   - 明确其最小 clean-room 入口：
     - candidate trendline
     - `third-touch confirmed`
     - breakout
     - `EMA slope / MACD` 共识过滤

2. 更新 `docs/TODO.md`
   - 在 `E2-A / E2-B` 下补进度说明：
     - 这张卡已进入候选池；
     - 当前更适合定位为 `confirmation / filter reference`；
     - 最小 clean-room 入口是先测：第三次确认后的 breakout，是否比 `first-cross + 无共识过滤` 更少假突破。

3. 更新 scout 网页生成脚本
   - 修改 `scripts/build_trendline_alpha_scout_report.py`：
     - 在“首批种子材料”里加入 `Third-touch + EMA/MACD confluence`；
     - 在“第一轮侦察结论”里明确写死：
       - 这条线不进主 replication shortlist；
       - 它服务的是 `confirmation / filter` 设计参考。

4. 最小重建与发布
   - 重建：
     - `reports/site/reading/trendline_alpha_scout/report.html`
     - `reports/site/plans/momentum_todo.html`
   - 同步发布到站点镜像。

## 验证 / 证据

### 1) 为什么不把它升成主 replication candidate

因为它更像“把结构确认讲清楚”的材料，而不是“已经用严谨方法证明可复制 alpha”的论文：
- 资产：BTC / ETH
- 频率：周频
- 方法：案例研究 + 图表判读
- 成本：未见扎实讨论
- OOS / rolling：没有
- 代码：未见公开实现

换成人话就是：
**它告诉你“第一次突破不够，最好等第三次确认和共识层”，但没有充分证明“你可以直接照这个挣钱”。**

### 2) 为什么它仍然值得保留

因为它和当前 15m 主线贴得非常近：
- `candidate trendline`
- `third-touch confirmation`
- `breakout persistence`
- `EMA/MACD alignment`

这些恰好就是当前结构研究里最容易被主观化、但又很值得规则化的部分。

### 3) 当前最合理的本地吸收方式

不是复刻周频图表案例，而是先把它写成客观规则：
- 用 pivots 定义 candidate trendline
- 只有第三次有效接触后，才允许结构进入候选池
- breakout 用 `close outside + τ` 定义
- EMA slope 与 MACD histogram 只负责共识过滤，不负责发现边界

然后只问一个简单问题：
- **第三次确认后的 breakout，是否比 first-cross + 无共识过滤更少假突破、失败更慢、回撤更低？**

如果做不到，就没必要继续堆更多“结构确认”的花样。

## 风险 / 边界

- 这轮没有做本地回测，因此没有新增 alpha 结论；
- 它完成的是 intake discipline：把 digest 从“读过了”推进到“知道该怎么用 / 不该怎么用”；
- 当前也没有把它加入 replication shortlist，只是把它稳定落到 `reading` / scout 侧。

## 下一步建议

如果后续再给这条线分配一轮，最小而真实的动作应是：

1. 先不用复杂手工 trendline；
2. 只在已有结构引擎上增加一层：
   - `third-touch confirmed`
   - `confirm_2of3`
   - `EMA slope 同向`
   - `MACD histogram 不反向`
3. 优先比较：
   - first-cross breakout
   - third-touch breakout
   - third-touch + EMA/MACD confluence
4. 重点看：
   - `false_break_ratio`
   - `outside_bar_persistence`
   - `time_to_failure`
   - `post_cost_return`

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成来源卡、TODO、scout board 与日志/邮件同步，不做提交。