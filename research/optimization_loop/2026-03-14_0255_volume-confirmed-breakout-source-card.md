# 给 volume-confirmed breakout / higher-low 补正式来源卡：先当 confirmation/filter 参考，不升主 replication candidate

## 为什么这次选这个

这轮继续保持轻量 E-track，但我不想重复上一轮的 regime-switch 处理，也不想又回到 `pytrendline_event_validation_v3` 的小样本排序上打转。

更值钱的一小步，是把已经有 digest 的 **Yumna et al. (2024)** 往前推成正式来源卡与最小 intake judgment：
- 不做新回测；
- 不写泛泛摘要；
- 直接回答它在当前 15m 研发里到底是什么角色。

这轮最值得复用/借鉴的点是：**有些外部材料不是拿来直接当 alpha 论文的，而是拿来把“假突破过滤链”写得更客观。**

## 核心结论（中文摘要）

核心结论：**`Yumna et al. (2024)` 当前更适合被正式归类为 `confirmation / filter reference`，而不是主 `replication candidate`；它最值得迁移的是 `volume confirmation + support flip + higher-low persistence` 这套假突破过滤链。**

证据如何支持这个结论：**这篇材料全文可得，但本质是单资产 BTC 周频的定性案例研究，没有系统化大样本回测、缺成本/OOS，也未见公开代码；因此不适合把周频案例直接当成已验证 alpha，但很适合把“放量突破、旧阻力转新支撑、后续 higher low”重写成 15m 可检验的客观规则。**

## 本轮做了什么改动

本轮只做一个主点：**把 `Yumna et al. (2024)` 从 digest 提升成正式来源卡 + 最小 audit judgement。**

具体动作：

1. 更新 `docs/LITERATURE_TRENDLINE_SIGNAL_MAP.md`
   - 新增正式来源卡：
     - `Technical Analysis for Buy or Sell Decisions in Cryptocurrency (Bitcoin)`
   - 写明：
     - `source_type = paper`
     - `fulltext_access = full_text`
     - `evidence_status = digest_done`
     - `fit_for_us = filter_candidate`
   - 明确其最小 clean-room 入口：
     - `裸 breakout`
     - `放量 breakout`
     - `support-flip`
     - `higher-low confirm`
     - `组合版`

2. 更新 `docs/TODO.md`
   - 在 `E2-A / E2-B` 下补进度说明：
     - 这张卡已进入候选池；
     - 当前更适合定位为 `confirmation / filter reference`；
     - 最小 clean-room 入口是先测：放量 breakout + 3 根内 support-flip / higher-low 是否能压低 15m 假突破。

3. 更新 scout 网页生成脚本
   - 修改 `scripts/build_trendline_alpha_scout_report.py`：
     - 在“首批种子材料”里加入 `Volume-confirmed breakout + higher low`；
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

因为它当前更像“把确认层讲清楚”的材料，而不是“已经用严谨方法证明可复制 alpha”的论文：
- 资产：只有 BTC
- 频率：周频
- 方法：定性案例研究
- 成本：未见扎实讨论
- OOS / rolling：没有
- 代码：未见公开实现

换成人话就是：
**它告诉你“突破后到底还该等什么”，但没有充分证明“你可以直接照这个挣钱”。**

### 2) 为什么它仍然值得保留

因为它和当前 15m 主线贴得很近：
- `volume confirmation`
- `former resistance becomes support`
- `higher low / higher high`

这三件事本质上都在回答：
**怎么把“碰线就追”升级成“突破后站稳再追”。**

### 3) 当前最合理的本地吸收方式

不是复刻周频形态案例，而是先把它规则化：
- 结构边界：`Donchian20` 或 pivot-based resistance
- breakout：`close > resistance + τ`
- volume filter：`volume > rolling vol median × k`
- support-flip：突破后 1~3 根内回踩旧阻力但未跌回区间
- higher-low confirm：突破后回撤，但 swing low 仍抬高

然后只问一个简单问题：
- **这套过滤链能不能先把 15m 假突破率、失败速度、回撤压下来？**

如果做不到，就没必要继续堆更多确认花样。

## 风险 / 边界

- 这轮没有做本地回测，因此没有新增 alpha 结论；
- 它完成的是 intake discipline：把新 digest 从“读过了”推进到“知道该怎么用 / 不该怎么用”；
- 当前也没有把它加入 replication shortlist，只是把它稳定落到 `reading` / scout 侧。

## 下一步建议

如果后续再给这条线分配一轮，最小而真实的动作应是：

1. 先不做复杂形态识别；
2. 只对已有 breakout baseline 增加一层：
   - `volume filter`
   - `3 根内 support-flip`
   - `higher-low confirm`
3. 优先比较：
   - 裸 breakout
   - 放量 breakout
   - 放量 + support-flip / higher-low
4. 重点看：
   - `false_break_ratio`
   - `time_to_failure`
   - `retest_hold_rate`
   - `post_cost_return`

## Commit hash

- 本轮未提交。

## 如果未提交，说明原因

当前 worktree 里仍有大量与本轮无关的脏文件、历史产物和其它线程修改。此时做 selective commit 仍容易混入无关内容，所以这轮只完成来源卡、TODO、scout board 与日志/邮件同步，不做提交。