# 2026-03-19 17:50 UTC — Rank 9 park reframe

- source rank: `Rank 9 / regime-switch indicator stack / no-buy-downtrend gate`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `derived_hypothesis_drafted`
- original park verdict kept: `yes`

## 1) 原 Rank 为什么会 park
原 Rank 9 的问题，不是“regime 这个主题完全没信息”，而是它被写成了 **standalone indicator-stack entry** 后，增量不够诚实：

- `2026-03-16 23:00 UTC` 的 clean replication 里，最不差的 `regime_gate_only` 在 `6bps/side` 下也只有 `mean_total_return≈-10.28%`、`positive_asset_ratio=1/3`、`mean_trades≈142`；
- 对照 `ema_baseline≈-10.83%`，改善非常有限，远谈不上把它救进 `paper candidate`；
- 更重的 `regime_plus_psar_rsi` 直接退化成 `0 trade`，说明把 regime + PSAR + RSI 全叠成一条 entry stack，只会把规则压到几乎不可交易；
- `Light Stability Pack` 四项一起 fail：时间、参数、跨标的、成本/交易数都没过。

所以原 rank 被 park，是因为它作为 **独立交易骨架** 既没带来足够 post-cost edge，也没带来诚实稳定性。

## 2) 它更像 hard park 还是 soft park
我把它判成 **soft park**。

原因：
- hard fail 的是“把 regime-switch stack 当 standalone alpha / entry engine”这件事；
- 但 `downtrend 禁多 / chop 降权` 这种 **角色更窄的 veto 语义**，并没有被原实验单独消费干净；
- 近邻新证据也在往同一个方向收口：更值得测的是 shared veto / allow-deny layer，而不是再造一条新 entry alpha。

## 3) 有没有可救信号
有，但只剩 **弱而窄** 的可救信号：

1. 原 Rank 9 里最有信息量的部分，其实不是 full stack，而是 `regime_gate_only` 这条“先判势、再决定放不放行”的骨架；
2. 新 digest `2026-03-18 19:56_ema-rsi-regime-veto-gate.md` 明确把同一篇论文重新翻译成了更贴 desk 的读法：
   - `EMA(RSI)>60 / <40` 更像 shared regime + veto；
   - Long setups 应先测 `downtrend long-veto`；
   - breakout-short 则更适合在 `regime_down` 里优先；
3. 原 clean replication 里，`ema_baseline` 的亏损有一大块来自 `fluctuating` 段（`total_return≈-0.3103`），说明“把所有状态同权放行”本身就可能是问题。

也就是说，可救信号不是“原 Rank 9 差一点就能成”，而是：**论文主题还可能留在 veto 层有用，只是原来角色写错了。**

## 4) 最值得改的唯一一刀
**唯一修改轴：把 Rank 9 从 standalone regime-switch entry stack，降级成现有 setups 的 `EMA(RSI)` asymmetric regime veto。**

不改数据源，不改主 setup，不同时偷带新 exit / 新 sizing / 新 execution；只回答一件事：
- `EMA(RSI)` 分层能不能作为 shared allow/deny gate，减少明显逆势 long，并给 breakout-short 一个更诚实的 downtrend 优先窗口？

## 5) 是否值得形成新的 derived hypothesis
**值得。**

原因不是原 Rank 9 已经被证明能赚钱，而是现在已经能把新假设写得足够窄：
- 只改角色，不改主题；
- 只改一刀，不搞多轴大修；
- 能清楚写出 trade on / trade off；
- bot2 后续可以直接判断：这条 `Rank 9b` 到底要不要在 fresh intake 不足时入板。

## 6) Derived hypothesis draft（供 bot2 后续判断是否入板）
- proposed_rank: `Rank 9b`
- source_rank: `Rank 9`
- status: `derived_hypothesis_drafted`
- single modification axis: `demote standalone regime-switch indicator stack into an EMA(RSI)-based asymmetric shared regime veto`
- trade on:
  - 不再让 Rank 9 自己直接触发开仓；
  - 只在固定 `EMA(RSI)` regime 下给现有 setup 做 allow/deny：
    - `EMA/PSAR continuation long` 与 `Fib retest_hold long` 仅在 `ema_rsi7 > 60` 或最小宽松版 `>55` 时放行；
    - `breakout-short` 仅在 `ema_rsi7 < 40` 或最小宽松版 `<45` 时优先放行；
    - 中性区默认 `half-size / veto`，第一轮优先先测 `strict veto`，不要偷带第二层 score。
- trade off:
  - 放弃“regime-switch stack 本身就是一条完整 entry alpha”的原 Rank 9 读法，换取更诚实的 shared veto 角色；
  - 代价是它不再是独立策略，而且若阈值过严，可能只是靠砍交易数美化结果；因此第一轮必须只测 `base vs asymmetric veto`，不偷带新 exit / new combo stack / second-layer regime matrix。
- why now:
  - 原 Rank 9 已经把“standalone stack”这条路基本审计完：post-cost 仍负、稳定性全 fail、full stack 甚至零交易；
  - 但同一论文在 `2026-03-18 19:56` 的 digest 又把最可迁移的部分收敛成了更窄的 shared veto 读法；
  - 这说明现在重开的理由不是推翻原 park，而是把剩余信息量从“失败的 entry stack”里拆出来。
- suggested initial state: `source intake / clean replication next`

## 7) 本轮结论
- 原 Rank 9 为什么 park：因为作为 standalone regime-switch entry stack，收益与稳定性都不够诚实；
- 它更像：`soft park`
- 可救信号：有，但只剩 `EMA(RSI)` regime veto 这一条窄角色线索；
- 最值得改的唯一一刀：**降级成 asymmetric shared regime veto**；
- 本轮最终结论：`derived_hypothesis_drafted`

## 8) 文件与提交流程说明
- 本轮只更新 `research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md` 与本日志；
- 默认不改 `docs/TODO.md` 顶部排班；
- 本轮未做 git commit：未先验证工作区是否适合安全 selective commit，按 brief 保持最小必要改动。
