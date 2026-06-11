# 2026-03-19 08:48 UTC · Rank 6 park reframe

## 本轮范围与约束
- 只复盘 `Rank 1~37` 中已 `park` 的 1 条旧 rank。
- 保留原 `park` verdict 的审计意义，不改 `docs/TODO.md` 顶部排班。
- 本轮只判断 `Rank 6` 是否值得派生出一个新的窄 reframe hypothesis。

## 这轮为什么选 Rank 6
- `Rank 6 / BTC -> COIN / MSTR proxy` 仍在 `Rank 1~37` 范围内，且最近 `7` 天没有被 `bot6` 复盘过。
- 原始证据不像“彻底没任何信息”，更像“把外部代理变量硬当 direct lag-trade entry 后，成本和 time-pocket 不够干净”。
- 2026-03-19 新增 digest `2026-03-19_0501_etf-price-discovery-shared-regime-gate.md` 提供了一个**只改角色、不改主题**的新旁证：把美股侧 price-discovery / 资金主导信息降级成 shared regime gate，而不是继续要求它单独产出可交易 lag alpha。

## 原 rank 为什么 park
原 `Rank 6` 的问题，不是完全没有同步/领先味道，而是把这层信息直接写成 `BTC 先动 -> COIN/MSTR 下一根跟随` 的交易规则后，证据不够诚实：

- 最不差的 `btc_large_move_follow_proxy` 在 `6bps/side` 下只有：
  - `mean_total_return≈+2.39%`
  - `positive_asset_ratio=100%`
  - `mean_trades≈110`
- 但一旦成本从 `6bps/side` 抬到 `10bps/side`，三档规则全部转负。
- `mean_sign_hit_rate` 只在 `50~52%` 左右，边薄得像“有一点味道，但不够当主策略”。
- 时间分桶也不干净：
  - `COIN` 只有中间桶显著为正；
  - `MSTR` 则是中间桶转负。

所以原审计结论成立：**把 equity proxy 当成 direct lag-trade alpha，不够抗成本，也不够稳定。**

## hard park 还是 soft park
我把 `Rank 6` 归为 **`soft park`**。

原因：
- 原版 direct-entry 读法已经被审计消费，不能翻案；
- 但它并非像某些硬 fail rank 那样“连最小 pocket 都没有”。
- 它更像是**信号角色放错层级**：外部 price-discovery / proxy-pressure 也许能当上层 allow/deny/sizing gate，却不适合继续硬写成逐笔可吃成本的 standalone lag trade。

## 有没有可救信号
有，但只限于“降级角色后也许还能留住一点价值”，不是“原 rank 其实没 park”。

最关键的可救信号有两类：

1. **原 Rank 6 至少留过薄 pocket**
   - `btc_large_move_follow_proxy` 在最低成本档并非全灭，说明“外部代理市场先动”这件事不是纯噪音。
   - 真正失败的，是把它强行包装成可直接下单的主 alpha。

2. **新证据把“外部领先”更自然地指向 shared regime gate，而不是 lag-trade entry**
   - 2026-03-19 的 ETF digest 给出的最小快检方向很一致：
     - `corr(ETF_t, BTC_{t+1}) = 0.213`
     - `corr(BTC_t, ETF_{t+1}) = 0.028`
     - 1h 滚动窗里 ETF 领先占比约 `80.7%`
   - 这类证据更像在回答：**当前是不是处在“美股代理/ETF 主导的风险偏好窗口”**，而不是回答“下一根我能不能直接去做 COIN/MSTR 跟单”。

## 最值得改的唯一一刀
**唯一主修改轴：把 `Rank 6` 从 direct lag-trade entry，降级成 `ETF / US proxy lead-strength` shared regime gate。**

也就是：
- 不再交易 `BTC -> COIN/MSTR` 的直接跟随；
- 保留“外部价格发现 / 代理资金主导”这个主题；
- 但只把它用作现有 `breakout-short / Fib retest_hold / EMA-PSAR` 的上层 `allow / veto / sizing`。

## 是否值得形成新的 derived hypothesis
**值得。**

本轮结论：`derived_hypothesis_drafted`

原因：
- 原 rank 的失败点很集中：**交易形状过于直接、成本过敏、time-pocket 不稳**；
- 新 digest 给出的旁证也很集中：**外部领先更适合作为 regime / price-discovery gate**；
- 这能形成一条足够窄、且 bot2 后续可直接判断是否入板的派生提案。

## 派生假设草案（供 bot2 后续判断是否入板）
- `proposed_rank`: `Rank 6b`
- `source_rank`: `Rank 6`
- `status`: `derived_hypothesis_drafted`
- `single modification axis`: `demote BTC->COIN/MSTR direct lag-trade entry to an ETF / US proxy lead-strength shared regime gate`
- `trade on`: 不再根据 `BTC 先动 -> COIN/MSTR 下一根跟` 直接开仓；而是在固定外部代理篮子（第一轮优先 `IBIT/FBTC/GBTC`，必要时保留 `COIN/MSTR` 作为次级对照）上计算 `lead_edge + impulse_z` 之类的 lead-strength 状态，只把它用作 shared allow/deny/sizing gate：外部代理同向领先且脉冲显著时，放行或加权 `EMA/PSAR continuation` 与 `Fib retest_hold`；若外部代理与 crypto setup 方向冲突，则 half-size 或 veto。第一轮只测 `base vs gate vs sizing`，不偷带新 trigger / exit / universe 扩张。
- `trade off`: 放弃“equity / ETF proxy 本身就是可直接交易的 lag alpha”这条原始读法，换取更诚实的 `price-discovery / risk-appetite overlay` 角色；代价是它不再是独立策略，而且若 gate 阈值太激进，可能只是靠砍单美化结果，因此第一轮必须只测 overlay 本身，不偷带额外 entry 逻辑。
- `why now`: 原 `Rank 6` clean replication 已经很清楚地证明 direct lag-trade 读法只在最低成本档留下一点薄 pocket，随后立刻被成本与 time-pocket honesty 否掉；但 2026-03-19 的 ETF lead digest 又刚好给出一个更贴近“外部市场先发现价格”主题、且只改角色不改主题的窄 reframe。
- `suggested initial state`: `source intake / clean replication next`

## 本轮结论
- 原 `park` verdict：**保留**
- 当前判断：**`soft park`**
- 是否有可救信号：**有，但只支持角色降级，不支持翻案**
- 最值得改的一刀：**把 external lead-lag 从 direct entry 改成 shared regime gate**
- 最终输出：**`derived_hypothesis_drafted`**

## 备注
- 本轮只更新 `research/park_reframe/` 与 `docs/PARK_REFRAME_QUEUE.md`，不改 `docs/TODO.md` 顶部排班。
- 未做 commit：工作区长期存在大量与本轮无关的既有脏文件；为避免混提，本轮只做最小必要文件改动与邮件摘要。