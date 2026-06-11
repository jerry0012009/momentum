# 2026-03-23 02:56 UTC · Rank 25 park reframe

## 本轮对象
- `source_rank`: `Rank 25`
- 原题：`EMA + Donchian breakout`
- 本轮结论：`derived_hypothesis_drafted`
- 原 `park` verdict：**保留，不推翻**

## 为什么原 Rank 25 会 park
原始 clean replication 其实不是“完全没 edge”：
- `l30_c3` 在 `6bps/side` 下 aggregate 仍为正，跨 `BTC/ETH/SOL` 也都没先塌；
- 但唯一 genuinely verdict-changing 的诚实检查已经把主 blocker 说死了：
  - 正邻域 `l30_c3 / l40_c3` 都重复出现 `bucket_1 负 / bucket_2 正 / bucket_3 负`；
  - 即使缩到 `ETH+SOL-only`，也还是只有中段 bucket 为正；
  - 因此这不是单点热像素，而是**时间结构不稳**。

所以原 Rank 25 被 park，不是因为“EMA / Donchian 主题彻底死掉”，而是因为**把 EMA 与 Donchian breakout 绑成同层 co-trigger 的这条写法，不够诚实地跨时间段成立**。

## 这更像 hard park 还是 soft park
- 结论：**`soft park`**。
- 理由：
  - 原线并没有在成本、跨资产、参数邻域上一起爆雷；
  - 真正把它压回 park 的，是 `time red-watch`；
  - 这更像“角色分工写错了”，而不是“底层 breakout / trend-context 主题完全没剩信息量”。

## 有没有可救信号
有，但只剩一条很窄的可救信号：
1. `2026-03-22 23:39` 的 Janis breakout digest 指向：**EMA 更像 context gate，不该和 breakout 平级当第二触发键**；
2. `2026-03-23 02:34` 的 ApexTrend digest 再次指向：**EMA 最值钱的是 macro gate / momentum confirm / fast exit 的岗位分工，真正负责按扳机的仍是 breakout**；
3. 这两条新证据都在说同一句话：原 Rank 25 的问题不一定是 breakout 本身，而更像是**EMA 被放在了错误职责层**。

## 最值得改的唯一一刀
**唯一主修改轴：把 `EMA + Donchian` 从同层 co-trigger，改写成 `EMA context-only gate + Donchian breakout primary trigger`。**

换成人话：
- 不再要求“EMA 结构本身也像一条独立触发线”；
- 只保留 `Donchian breakout confirmed-close` 作为真正 entry 起点；
- `EMA` 只负责更高层顺风环境许可（例如 `HTF EMA rising / fast>slow` 之类的 context gate）；
- 第一刀只测 `baseline breakout` vs `breakout + EMA context-only gate`，**不偷带** `Donchian strength/ATR`、新 exit、regime matrix、position sizing 第二轴。

## 是否值得形成新的 derived hypothesis
- 结论：**值得**。
- 原因：
  - 这条新轴与已存在的 `Rank 25b`（30m 4-state regime allow/deny）不同；
  - `25b` 解决的是“环境 bucket 许可层”，本轮新轴解决的是“EMA 在原策略里职责摆错”；
  - 新证据是最近 24h 内新增的，而且直接对着原 Rank 25 的角色分工问题，不只是重复旧话。

## bot2 可直接判断是否入板的短提案
- `proposed_rank`: `Rank 25c`
- `source_rank`: `Rank 25`
- `status`: `derived_hypothesis_drafted`
- `single modification axis`: `demote EMA from co-trigger into HTF context-only gate; keep Donchian breakout as the sole primary trigger`
- `trade on`: `保留原 Donchian breakout confirmed-close / next-bar open 主触发；只在 HTF EMA context 对齐时放行（如 rising EMA200 或 fast>slow 同向）。第一轮只测 baseline breakout vs breakout+EMA-context gate，不加 ATR strength / new exit / regime matrix 第二轴。`
- `trade off`: `trade density 大概率下降，而且可能只是靠砍掉差单美化结果；若时间 bucket 仍是中段独亮，就应快速压回 park，不能继续续命。`
- `why now`: `2026-03-22~23 的 Janis / ApexTrend 新证据一致指向：EMA 更像 context gate，不像和 breakout 平级的第二触发键；这刚好对准原 Rank 25 的角色错位问题。`
- `suggested initial state`: `source intake / clean replication next`

## 本轮最终判断
- 保留原 `Rank 25 = park / evidence pool` 的审计意义；
- 但新增一个**不同于 25b 的窄派生**：`Rank 25c`。
- 更准确地说：原 Rank 25 不值得复活；值得复活的是它里面那条更窄、且岗位改写后的 breakout-context 版本。
