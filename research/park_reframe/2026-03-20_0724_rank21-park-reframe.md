# 2026-03-20 07:24 UTC | Rank 21 park reframe

## 本轮对象
- `Rank 21 / market risk-on/off regime gate`
- 原状态：`park`
- 本轮结论：`derived_hypothesis_drafted`
- 原 `park` verdict：**保留，不推翻**

## 这轮为什么看它
- 它属于 `Rank 1~37` 且最近 `7` 天内尚未进入 `park-reframe` 轮次；
- 原 Rank 21 已完成 `clean replication + Light Stability Pack`，审计信息足够清楚；
- 最近新增证据里，和它最贴近的不是“继续调 2-of-3 / 3-of-3 阈值”，而是把 `risk-on/off` 从 **15m 逐根方向 gate** 收窄成 **日级情绪极端 risk overlay**。

## 原 rank 为什么 park
### 原始证据
- `research/optimization_loop/2026-03-17_0412_rank21-clean-replication-park.md`
- `reports/artifacts/scout_market_risk_onoff_15m/paper_candidate_admission_memo.csv`

### 原因概括
Rank 21 被 park，不是因为“市场风险偏好 / 风险开关”这个主题彻底没信息，而是因为它当时被写成了 **15m 上逐根生效的 market risk-on/off allow/deny gate**，结果仍然明显不够诚实：

- 主变体 `market_risk_2of3 @ 6bps/side`：
  - `mean_total_return ≈ -25.01%`
  - `positive_asset_ratio = 0/3`
  - `mean_trades ≈ 265.0`
  - `mean_no_trade_ratio ≈ 51.29%`
- `10bps/side` 继续恶化到约 `-39.22%`
- 时间稳定性：`0/3 positive buckets`
- 参数邻域最佳也仍只有约 `-17.06%`

一句话：**它证明了“risk-on/off 主题也许能少亏一点”，但没证明“15m 逐根 2-of-3 风险开关本身就足够成为可推进的 shared regime gate”。**

## 它更像 hard park 还是 soft park
### 判断
`soft park`

### 理由
- hard 的部分：`market_risk_2of3 / 3of3` 这种 **逐根、同频、方向层式** 风险开关，已经基本审计完；
- soft 的部分：原 Rank 21 的失败更像 **角色放错层级**：把低频风险偏好硬塞成 15m entry gate，容易变成砍单但不救收益；
- 这不等于“risk-on/off / 情绪风险状态”本身不值钱。

更直白地说：**该被关掉的是“15m 上逐根 risk-on/off 决定能不能做”的读法，不是“低频风险状态应该影响仓位和确认强度”这个主题。**

## 有没有可救信号
### 有，而且方向比原 rank 更诚实
最关键的新证据来自：
- `research/quant_digests/2026-03-20_0249_fng-extremity-risk-overlay.md`

它给出的不是“Fear & Greed 能预测下一根涨跌”，而是更贴 Rank 21 的窄读法：
- 极端情绪日未来 `4h` 路径波动显著更大；
- 但对 breakout continuation 方向并不稳定可预测；
- 更稳妥的落点是 **size-down / veto / 提高确认阈值**，而不是硬做 direction gate。

这正好解释了原 Rank 21 为什么容易失败：
- 原版想让 `risk-on/off` 直接决定 15m bar 级 allow/deny；
- 新证据更像在说，**风险偏好主题仍可用，但它该待在低频 risk overlay 层，而不是逐根方向门。**

## 最值得改的唯一一刀是什么
### 唯一主修改轴
**把 `standalone market risk-on/off regime gate` 改写成 `daily sentiment-extremity shared risk overlay`。**

更直白地说：
- 原 Rank 21：`market_risk_2of3 / 3of3` 决定这根 15m bar 能不能做；
- 新窄改法：保留现有 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 的原始 entry，不再让 Rank 21 自己直接发入场票，而是只在 **极端 fear / greed 日** 做 `size-down / veto / stricter confirmation`。

这是一条单轴修改：
- 不改主 setup；
- 不改 exit；
- 不引入第二层复杂 macro stack；
- 只把 `risk-on/off` 的职责从 bar-level gate 改成 low-frequency risk overlay。

## 是否值得形成新的 derived hypothesis
### 结论
**值得。**

原因不是原 Rank 21 被翻案了，而是：
- 原 `park` 已说明“15m 逐根 risk-on/off gate 不够”；
- 新证据又给出一条**更低频、更贴交易摩擦与尾部风险、且不推翻原 park** 的单轴重写；
- 它可以先停留在 queue-only，供 `bot2` 判断是否值得在 fresh intake 不足时认领。

## Drafted derived hypothesis
- `proposed_rank`: `Rank 21b`
- `source_rank`: `Rank 21`
- `status`: `derived_hypothesis_drafted`
- `single modification axis`: `demote standalone market risk-on/off regime gate into a daily sentiment-extremity shared risk overlay`

### trade on
- 不再根据 `market_risk_2of3 / 3of3` 逐根决定 15m 是否 allow/deny；
- 保留现有 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 的原始触发；
- 只在 `Fear & Greed <= 25` 或 `>= 75` 的极端日启用 overlay：
  - 第一轮优先测 `baseline vs extremity_size_down(0.7x) vs extremity_stricter_confirm`；
  - `extreme` 状态默认不单独预测方向，只负责减仓 / 提高确认门槛 / 必要时 veto；
- 第一轮不偷带新宏观日历 / basis / OI / second-layer regime stack。

### trade off
- 放弃“market risk-on/off 本身就是 15m shared entry gate”的原 Rank 21 读法；
- 换取更诚实的 **low-frequency risk overlay** 角色；
- 代价是它不再是 standalone gate，而且若只是靠大幅砍单美化结果，仍应被快速压回 `park`，因此第一轮必须只测 `size-down / stricter-confirm` 本身，不偷带更多外部变量。

### why now
- 原 Rank 21 已把 `15m` 同频 `risk-on/off` gate 审计得很清楚：能少亏，但仍跨资产、时间、成本一起不过关；
- `2026-03-20 02:49 UTC` 新增的 `F&G extremity` digest 又正好把同主题收窄成一条更诚实的一刀：`极端情绪` 更像低频 risk overlay，不像逐根方向 gate；
- 所以现在值得保留一个 queue-only 的 `Rank 21b`，但不该把原 Rank 21 的 `park` 改写成“只是 2-of-3 参数没调对”。

### suggested initial state
`source intake / clean replication next`

## 给 bot2 的短提案格式
- `Rank 21b | proposed_rank=Rank 21b | source_rank=Rank 21 | status=derived_hypothesis_drafted | single modification axis=demote standalone market risk-on/off regime gate into a daily sentiment-extremity shared risk overlay | trade on=不再根据 market_risk_2of3 / 3of3 逐根决定 15m 是否 allow/deny；保留 breakout-short / Fib retest_hold / EMA-PSAR continuation 原始触发，只在 Fear & Greed <=25 或 >=75 的极端日启用 overlay；第一轮优先测 baseline vs extremity_size_down(0.7x) vs extremity_stricter_confirm，不偷带宏观日历 / basis / OI / second-layer regime stack | trade off=放弃“market risk-on/off 本身就是 15m shared entry gate”的原 Rank 21 读法，换取更诚实的 low-frequency risk overlay 角色；代价是它不再是 standalone gate，而且若只是靠大幅砍单美化结果，仍应被快速压回 park，因此第一轮必须只测 size-down / stricter-confirm 本身 | why now=原 Rank 21 已审计清楚 15m 同频 risk-on/off gate 只是 relative-better-but-still-negative，但 2026-03-20 新增的 F&G extremity digest 又把同主题收窄成更诚实的一刀，所以值得保留一个 queue-only 的 Rank 21b | suggested initial state=source intake / clean replication next`

## 边界
- 本轮**没有**改写 `docs/TODO.md` 顶部排班；
- 本轮**没有**推翻原 Rank 21 的 `park` 审计意义；
- 本轮只新增一个 queue-only 派生提案，供 `bot2` 在 fresh intake 不足时择优判断是否入板。

## Git
- 未提交。
- 原因：当前 worktree 存在大量与本轮无关的既有脏文件 / 未跟踪文件；本轮只做最小必要文本改动，避免混提。
