# 2026-03-14 06:31 UTC · Strategy Review

## 本轮一句话判断

当前最该继续推进的，不是再开新外部分支，而是把三条收口线进一步压成更诚实的角色判断：**EMA/PSAR 先往 raw alpha / role audit 走；V3 只保留 breakout-short follow-up；Fibonacci 继续停在 confirmation/filter 候选，不升 alpha。**

## 当前 strongest evidence

1. **EMA / PSAR raw alpha focus**
   - 当前是三条收口线里最像“能继续往策略层走”的一条。
   - `EMA / PSAR Raw Alpha Focus Report` 已经把结论讲清：
     - `EMA` 更像 `raw alpha baseline`
     - `PSAR` 更像 `fast reaction / loss-protection candidate`
   - 关键原因：跨市场 × 多频率 first-pass 里，EMA/PSAR 在四个原始策略里明显最值得保留，且 EMA 的覆盖度与解释性最好。

2. **V3 final verdict**
   - `pytrendline_event_validation_v3` 已经可以收工，不应再继续无限追加切片。
   - 当前还能保留的不是“趋势线反弹多头 alpha”，而是：
     - `support_breakout_raw @ h24`
     - `support_breakout_confirm_1 @ h24`
   - 它们更像 `continuation short candidate`，但还不够格写成 production alpha 已确认。

3. **Fibonacci confirmation / retest_hold**
   - 这条线当前有价值，但角色已经比较清楚：
     - 不是独立 alpha
     - 更像 `confirmation / filter candidate`
   - 现有本地切片说明它能改善部分失败率与 trade-off，但在成本后仍没有给出足够正面证据去升入 `factors/`。

## 当前 weakest / should-park lines

1. **继续扩 `pytrendline_event_validation_v3` 的衍生切片**
   - 这条线的边际信息增量已经明显下降。
   - 现在最需要的是收口后的 follow-up 验证，而不是继续围着同一批样本打转。

2. **把完整 `MIHS / MIHCS regime stack` 当成新主 alpha thesis**
   - 当前证据更支持把它理解成 `regime/filter reference`。
   - 值得保留的是其中的 `EMA / PSAR raw strategies`，而不是整套 indicator-switching 方案直接升格为当前主线。

3. **bot7 继续泛化扩外部 digest 池**
   - 在当前阶段，这会冲淡三条收口线。
   - 外部材料仍有价值，但默认应先服务当前 closure-first。

## 建议优先级 Top 1~3

### Top 1. EMA baseline 进入“更诚实的策略层验证”

优先做：
- 成本敏感性（gross / low-cost / high-cost）
- rolling / OOS honesty
- 明确它作为后续结构研究默认 baseline 的位置

为什么排第一：
- 这是当前三条线里最像 `main alpha / baseline` 的对象；
- 继续推进最有可能得到“可以真正拿来比较别的东西”的稳定底座。

### Top 2. 把 V3 收窄成 breakout-short follow-up，而不是 reopen 整条 v3

优先做：
- `support_breakout_raw / confirm_1` 与 `avoid_fluctuating` 的组合验证
- post-cost / sample retention / excess_ret / failure path 对照
- 明确它最终更像：`conditional alpha` 还是 `watchlist candidate`

为什么排第二：
- 这条线已有收工结论，但还差最后一层“角色定性”；
- 不需要再开新分支，只需要把保留下来的 breakout-short 候选验证得更诚实。

### Top 3. Fibonacci retest_hold 做“保留还是进一步降级”的最后表达

优先做：
- 把当前结果讲成一页更清楚的 decision / intake note
- 明确：它是 `optional filter`、`archived idea`，还是还值得做一个更长样本复核

为什么排第三：
- 当前证据已经大致足够说明它不是 alpha；
- 现在更重要的是把它讲清楚，避免未来又误升优先级。

## TODO / roadmap / web / cron 的改动或建议

### 本轮已改

1. **微调 `docs/ROADMAP.md`**
   - 在顶部补了一个说明：当前 active roadmap 应以 `docs/TODO.md` 的 closure-first 和 structure-event 主线为准；
   - 避免读者把旧的 `M1~M5` 工程路线误读成当前主优先级。

2. **微调 `bot7-quant-digest-4h` prompt**
   - 保留 4h 节奏不变；
   - 但默认选题从“继续泛化找基础 alpha”改成：优先服务三条收口线；
   - 只有在三条收口线没有更合适外部材料时，才回退到更泛化的 digest。

### 本轮不改

1. **TODO.md**
   - 这轮不再改 TODO：最近已经完成了 EMA / PSAR raw alpha focus 的提升与 closure-first 微调；
   - 当前问题不是 TODO 不清楚，而是后续执行要更集中。

2. **bot3 频率 / prompt**
   - 当前 bot3 已经明显对齐 closure-first；
   - 这轮先不再追加修改，避免过度来回拉扯。

## 网页/表达建议

1. **首页方向已经明显更清楚**
   - 现在首页已经按 closure-first 组织，读者更容易先看到：
     - V3 final verdict
     - EMA / PSAR raw alpha
     - 主线入口
   - 这是正向变化。

2. **接下来最值得补的不是更多页面，而是“what changed recently”**
   - 当前页面已经很多；
   - 对回访读者来说，更缺的是：最近 24~48 小时到底哪条线升级/降级了。

3. **Fibonacci 需要一个更明确的定位句**
   - 当前它在日志与 TODO 里已经比较清楚，但站点读者仍可能误以为它还在积极冲 alpha；
   - 建议后续补一句更硬的定位：`not promoted to factors; keep as optional confirmation/filter reference`。

## cron / 节奏建议

1. **bot3：保持当前 40m，不改频率**
   - 方向已经正确：围绕三条收口线做小步推进；
   - 接下来重点不是更快，而是避免重新散掉。

2. **bot7：保留 4h，但默认更服务 closure-first**
   - 本轮已做 prompt 微调；
   - 目标是不让 digest 继续抢走主线注意力。

3. **bot4：继续保持 disabled**
   - 这是正确状态；
   - `v3` 已收工，不应再单独维持一个 V3 专用推进器。

## 风险与不确定性

1. **EMA 虽然当前最强，但还没有经过完整成本 / rolling / OOS honesty 审核**
   - 现在更像 `baseline candidate`，不是 production-ready alpha。

2. **V3 breakout-short 候选仍可能在更诚实的成本 / retention / OOS 比较后继续降级**
   - 不应因为它是当前 v3 幸存者，就自动视为最终可交易策略。

3. **Fibonacci 当前看起来“有点帮助”，但帮助主要体现在 filter / trade-off，不是收益翻正**
   - 这条线最容易被误读成“差一点就成 alpha”，应继续谨慎表达。
