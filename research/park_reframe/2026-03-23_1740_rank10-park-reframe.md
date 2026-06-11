# 2026-03-23 17:40 UTC｜bot6 park-reframe｜Rank 10

## 0) 本轮选择
- 选定：`Rank 10 / volatility-managed EMA / ATR sizing overlay`
- 原因：它上次被 bot6 正式复盘是在 `2026-03-19 22:42 UTC`，虽然仍在 7 天内，但今天出现了**足够贴题的新旁证**：
  - `research/quant_digests/2026-03-23_0503_tc-waterfall-participation-tradeability-veto.md`
- 这条新证据不是在讲新入场形状，而是在讲：**很多 15m 策略真正该先问的是“能不能交易”，不是继续调仓位公式。**
- 因此本轮要判断的不是“要不要推翻 Rank 10 的 park”，而是：**这条新旁证够不够把 Rank 10 从既有 `Rank 10b` 再推进成新的更窄派生假设。**

## 1) 原 Rank 为什么 park？
原始证据来自：`research/optimization_loop/2026-03-16_2312_vol-managed-ema-park.md`。

原 Rank 10 被 park 的原因非常直接，不是“样本太薄看不清”，而是**在有足够交易数的前提下，ATR 管理仓位既没把收益救活，也没把回撤救好**。

关键原始读数（`6bps/side`）：
- `baseline_100`：`mean_total_return≈-15.66%`，`mean_max_drawdown≈-31.01%`，`positive_asset_ratio=0/3`
- `atr_clip_050_150`（primary variant）：`mean_total_return≈-26.21%`，`mean_max_drawdown≈-35.03%`，`positive_asset_ratio=0/3`
- 邻近 clipping 也都没翻正：
  - `atr_clip_075_125≈-21.30%`
  - `atr_clip_025_175≈-28.42%`
- 四类稳定性包一起失败：
  - 时间稳定性：`0/3 positive buckets`
  - 参数稳定性：`0/5 positive configs`
  - 跨标的稳定性：`0/3 assets positive`
  - 成本稳定性：`0/4 cost levels positive`

所以原结论必须保留：
**Rank 10 失败的不是“还差一点 clip 参数”，而是 standalone `ATR_ref / ATR14` 这条 volatility-managed sizing 读法本身没有把 15m EMA 方向层救活。**

## 2) 它更像 hard park 还是 soft park？
- **本轮仍读作 `soft park`。**

原因不是说它快翻身了，而是：
- ATR / 波动信息本身未必毫无价值；
- 真正失败的是把它写成了 **standalone alpha / standalone rescue line**；
- 因此它仍保留一个很窄的残余价值：更像 shared `size-down / veto` 风险层，而不像独立可交易线。

也正因为如此，之前已经自然收敛出 `Rank 10b`：
- 把 `volatility-managed EMA / ATR sizing` 降级成 `ATR stopDistancePct` shared size-veto overlay。

## 3) 有没有“可救信号”？
- **有，但今天的新信号只会继续强化既有 `Rank 10b`，不会打开新的主修改轴。**

本轮新旁证 `2026-03-23_0503_tc-waterfall-participation-tradeability-veto.md` 的含义很明确：
- 真正值得补的不是“再调一个 ATR clipping 公式”；
- 而是先把 `commission → spread → impact` 的交易性约束写成 `tradeability veto / sizing gate`；
- 翻成人话：**先决定这笔单能不能做，再决定做多大；不要把仓位管理错当成 alpha 修复器。**

映射回 Rank 10：
- 这条新证据并没有替原 Rank 10 的 standalone ATR sizing 正名；
- 反而进一步说明，原 Rank 10 最大的问题正是**把 ATR 仓位缩放当成主修复器**；
- 可救信号仍然只有一句：
  **ATR 更适合作为 shared risk / tradeability 层的一部分，而不是自己单独扛一条线。**

## 4) 最值得改的唯一一刀是什么？
- **仍然是既有结论：把 ATR 从 standalone sizing alpha，降级成 shared `size-veto / tradeability` overlay。**

也就是：
- 唯一最值得保留的修改轴，依然是 `Rank 10b` 已经写下的那一刀；
- 今天的新成本瀑布旁证，只是在更 execution-facing 的层面再次证明：
  **别再把 ATR clipping 本身写成一条独立救法。**

## 5) 是否值得形成新的 derived hypothesis？
- **不值得。结论：`keep_park`。**

原因：
1. 原 `park` 结论没有被推翻，反而被新的 tradeability 旁证进一步坐实；
2. 新证据支持的仍是同一条旧 reframe：`ATR -> shared size/veto overlay`，这已经被 `Rank 10b` 消费；
3. 若本轮再硬写一个 `Rank 10c`，大概率只是把 `10b` 的角色边界换个说法重写一遍，而不是新增真正独立的一刀。

因此更诚实的判断是：
- 原 `Rank 10` 继续保留 `park / evidence pool`；
- `Rank 10b` 继续足够代表这条主题最自然、最窄的 reframe；
- 本轮不再新增 `Rank 10c`。

## 6) 本轮固定回答（摘要）
- 原 rank 为什么 park？
  - 因为 standalone ATR volatility-managed sizing 在 15m EMA 上收益、回撤、时间、参数、跨标的、成本六个角度一起失败，不是“只差一点参数”。
- 它更像 hard park 还是 soft park？
  - `soft park`，因为 ATR 信息可能还有 residual value，但只应留在 shared risk layer。
- 有没有可救信号？
  - 有；新证据说明真正该补的是 tradeability / participation veto，而不是继续美化 standalone ATR sizing。
- 最值得改的唯一一刀是什么？
  - 仍是 `Rank 10b`：把 ATR 降级成 shared `size-down / veto` overlay。
- 是否值得形成新的 derived hypothesis？
  - 不值得；本轮结论为 `keep_park`。

## 7) 本轮结论
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`
- 补充口径：`2026-03-23 的成本瀑布 / participation 新证据只会进一步强化既有 Rank 10b（ATR 应降级成 shared tradeability / size-veto overlay），不足以再派生 Rank 10c`

## 8) 文件动作
- 新增本轮日志：本文件
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## 9) commit
- 本轮默认不做 commit。
- 原因：当前仓库长期存在与本轮无关的共享脏文件风险；这轮只做最小必要文档改动，避免混提。
