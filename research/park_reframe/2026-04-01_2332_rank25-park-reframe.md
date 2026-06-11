# 2026-04-01 23:32 UTC · Rank 25 park reframe review (revisit)

## Scope
- Source rank: `Rank 25 / EMA + Donchian breakout confirmation`
- Original authoritative verdict stays: `park / evidence pool`
- This round only asks: **在不推翻原 park 的前提下，最近新增的 `MA / breakout raw alpha × bubble-state gate × cost ladder` 证据，是否足以让 Rank 25 再派生出新的窄 reframe hypothesis**

## Why revisit Rank 25 now
- `Rank 25` 上次 park-reframe 复盘是 `2026-03-23 02:56 UTC`，已超过 `7` 天，符合低频复查规则。
- 当前号段轮转里，`50+` 与 `80~110` 近期已连续覆盖；本轮回到 `25~49`，挑 1 条已 parked rank 做低频复核。
- 最近新增的直接相关旁证是：
  - `research/quant_digests/2026-04-01_1811_ma-breakout-bubble-gated-trend-alpha.md`
- 这条新证据会自然追问：**原 Rank 25 这种 `EMA + Donchian breakout` 旧 park，是否值得再长出一个新的 `Rank 25d`，还是只会继续强化“旧 residual 已被 25b / 25c 吸收”的判断。**

## Read set
- required:
  - `docs/TODO.md`
  - `docs/PARK_REFRAME_QUEUE.md`
  - `docs/RECENT_PAPER_SEEDS.md`
  - `research/quant_digests/INDEX.md`
  - `research/park_reframe/INDEX.md`
- prior reframe logs:
  - `research/park_reframe/2026-03-18_1725_rank25-park-reframe.md`
  - `research/park_reframe/2026-03-22_1352_rank25-park-reframe.md`
  - `research/park_reframe/2026-03-23_0256_rank25-park-reframe.md`
- needed evidence:
  - `research/quant_digests/2026-04-01_1811_ma-breakout-bubble-gated-trend-alpha.md`

---

## 1) 原 rank 为什么 park？
这条原始审计结论没有变：

- 原 `Rank 25` 不是完全没 edge；
- 但真正把它压回 `park` 的，是 **time-bucket honesty**，不是单点参数差一点。

此前已固定下来的关键口径是：
- `EMA + Donchian breakout` 在某些 pocket 下确实能留下正 after-cost 样子；
- 但最核心的诚实检查反复出现：`bucket_1 负 / bucket_2 正 / bucket_3 负`；
- 即使缩到更窄资产子集，这个时间结构不稳的问题也没有消失。

翻成人话：
**原 Rank 25 被 park，不是因为 breakout 主题彻底死掉，而是因为“把 EMA 与 Donchian breakout 绑成同层 co-trigger 的这版写法，不够诚实地跨时间段成立”。**

所以原 `park` verdict 仍必须保留，不能因为最近又出现一篇 `MA / breakout + regime gate` 文献，就把历史审计结论抹平。

## 2) 它更像 hard park 还是 soft park？
**仍然更像 `soft park`，但不是那种很容易再切出新旁支的软。**

原因：
- `MA / breakout` 这个大主题当然没死，甚至最近新 digest 还再次证明它值得作为 raw-alpha family 继续 intake；
- 但对 `Rank 25` 这条旧线来说，真正剩下的 residual 已经被前几轮收得很窄：
  - `25b`：上层 regime allow/deny gate
  - `25c`：EMA 从 co-trigger 降级为 HTF context-only gate
- 也就是说，它不是 hard park，因为底层主题没死；
- 但它也不再像“再补一个近义 filter 就值得起 `25d`”的状态。

## 3) 现有证据里是否存在“可救信号”？
**有，但这次的可救信号更像在支持“新 raw-alpha family”，而不是支持 `Rank 25` 再长新号。**

本轮新 digest 的核心信息是：
- `MA / breakout` 应被当成 **价格型 trend raw alpha family**；
- `bubble-state gate` 只是决定什么环境更该做、加仓还是禁做；
- 更诚实的策略卡写法是：`raw alpha + regime gate + cost ladder`。

这对 `Rank 25` 的意义不是“原 rank 又能救一刀”，而是：
1. 它再次确认 **breakout 本体没死**；
2. 但新增 regime 信息是更慢、更上层的 `bubble / acceleration state`；
3. 这类慢变量 gate 更像一条**新的完整策略骨架**或更上位的新 intake 语言，不像 `Rank 25` 这个旧 `EMA + Donchian` 壳子下还能诚实再切出的单一修改轴。

换句话说：
- 这条新证据没有推翻原 Rank 25 的 blocker；
- 它只是把“breakout 家族若要活，应该从第一天就把 regime + cost 写进壳里”说得更清楚；
- 而这句话，已经足以被现有 `25b / 25c` 吸收，没必要再伪装成新的 `25d`。

## 4) 最值得改的唯一一刀是什么？
如果硬要保留唯一一刀，本轮最诚实的答案依然不是新增新轴，而是：

**继续承认 Rank 25 的残余价值只落在既有两条窄派生上：**
- `25b`：上层 regime allow/deny
- `25c`：EMA context-only，Donchian breakout 继续做唯一主触发

也就是说，本轮最值得保留的“唯一主修改轴”其实没有变化。

为什么不把 `bubble-state gate` 单独起成 `25d`：
- 因为那会把一个更慢、更上位、且可服务整个 `MA / breakout` raw-alpha family 的 regime 变量，硬塞回 `Rank 25` 旧壳；
- 这不再是对原 parked rank 的窄 reframe，反而更像一条新的 family-level 策略卡；
- 审计上不诚实。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。结论：`keep_park`。**

理由：
1. 原 `park` blocker（时间结构不稳）没有被新证据化解；
2. 新 evidence 支持的是更上位的 `MA / breakout raw alpha × regime gate × cost ladder` family，而不是原 Rank 25 再长一条近义派生；
3. 对 `Rank 25` 来说，最自然、最诚实的 residual 已经由 `25b / 25c` 两条单轴提案覆盖；
4. 若此时再写 `25d`，更像把“新 family intake”误包装成“旧 rank 窄救”。

---

## Final verdict for this round
- `verdict`: `keep_park`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park，但已更偏“残余已被既有 25b / 25c 吸收”`

## Minimal audit note
本轮不重开 `Rank 25`，也不推翻原 park。

本轮只确认一件事：**2026-04-01 新增的 `MA / breakout × bubble-state gate × cost ladder` 证据，再次证明 breakout 家族仍值得作为 raw-alpha family 研究；但它更像新的 family-level intake 语言，而不是原 `Rank 25` 可以再诚实派生出的 `Rank 25d`。**

## Git
- 本轮只做最小必要文档改动；不做 commit。
- 原因：共享工作区长期存在与本轮无关的脏文件，当前不安全混提。
