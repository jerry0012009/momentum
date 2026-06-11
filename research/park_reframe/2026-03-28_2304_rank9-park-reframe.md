# 2026-03-28 23:04 UTC — Rank 9 park reframe

- source rank: `Rank 9 / regime-switch indicator stack / no-buy-downtrend gate`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## 1) 原 Rank 为什么会 park
原 Rank 9 被 park，不是因为“regime 主题完全没信息”，而是因为它被写成了 **standalone regime-switch indicator-stack entry** 以后，收益和稳定性都不够诚实。

`2026-03-16 23:00 UTC` 的 clean replication 已经把这点审得很清楚：
- 最不差的 `regime_gate_only` 在 `6bps/side` 下也只有 `mean_total_return≈-10.28%`、`positive_asset_ratio=1/3`、`mean_trades≈142`；
- 对照 `ema_baseline≈-10.83%`，改善很有限，不够把它抬成可交易候选；
- 更重的 `regime_plus_psar_rsi` 直接退化成 `0 trade`，说明 full stack 写法会把规则压到几乎不可交易；
- `Light Stability Pack` 四项一起 fail：时间、参数、跨标的、成本/交易数全部不过线。

所以原 Rank 9 park 的核心原因是：**它作为独立 entry alpha 不成立，且 stacked 版越加越窄、越不诚实。**

## 2) 它更像 hard park 还是 soft park
本轮我仍判它是 **soft park，但比 2026-03-19 更偏硬**。

原因：
- 主题里确实还留过一点“先判势、再决定放不放行”的 residual 信息；
- 这部分 residual 也已经在既有 `Rank 9b` 里被收敛成更窄的角色改写：`EMA(RSI)` asymmetric shared regime veto；
- 但最近新增证据并没有把它重新抬回“值得再派生一条 queue-facing hypothesis”的程度，反而更说明它剩下的价值只适合做更上位、与 Rank 9 本体解耦的 shared confidence / vol-state layer。

## 3) 现有证据里有没有“可救信号”
有，但仍然只剩 **既有 Rank 9b 那一条很窄的可救信号**，没有出现足够新的第二刀。

本轮参考的新增旁证主要有两类：

1. `2026-03-27_2322_btc-si-lagged-tech-continuation-alpha.md`
   - 它支持的是：**高阈值 abstain / 高置信度 continuation trigger** 这条线；
   - 这更像“分钟级方向分数 + abstain”的新 raw-alpha / trigger family，或更一般的 confidence gate；
   - 它并没有把 `regime-switch stack` 自己救活，也没有新增属于 Rank 9 的独特 regime 轴。

2. `2026-03-28_1433_iv-quantile-confirmation-gate.md`
   - 它支持的是：**IV quantile × IV change** 这种 shared confirmation / veto layer；
   - 这是一条新的波动状态 gate family，而不是 Rank 9 的自然延长线；
   - 它说明“状态层”这个大方向没死，但活下来的未必还是 Rank 9 那个 regime-switch stack 语义。

所以，可救信号并不是“Rank 9 还有第二条派生值得 draft”，而是：**原 Rank 9 唯一自然 residual 仍只收敛到既有 Rank 9b；新增证据主要把状态层价值外溢到别的 family，而不是把 Rank 9 本体救回来。**

## 4) 最值得改的唯一一刀是什么
如果必须回答唯一一刀，答案仍然是既有那一刀，不变：

**把 Rank 9 从 standalone regime-switch entry stack，降级成现有 setups 的 `EMA(RSI)` asymmetric shared regime veto。**

也就是：
- 不再让 Rank 9 自己触发开仓；
- 只把 `ema_rsi7` 一类 regime state 用在 long-side allow/deny、short-side asymmetric veto 上；
- 不偷带新 exit / 新 sizing / 第二层 regime matrix。

这条一刀已经由既有 `Rank 9b` 覆盖，本轮没有比它更诚实的新主修改轴。

## 5) 是否值得形成新的 derived hypothesis
**不值得。**

原因：
- 既有 `Rank 9b` 已经把原 Rank 9 最自然、最诚实的残余信息收敛出来了；
- 本轮看到的新旁证，更多是在支持“shared confidence gate”或“IV-state gate”这些更上位的新 family；
- 如果现在硬写 `Rank 9c`，大概率会变成把外部新主题借壳塞回 Rank 9，而不是对原 rank 做诚实的单轴 reframe。

换句话说：
- **原 `park` 仍应保留；**
- **soft / 可救 residual 仍只剩既有 `Rank 9b`；**
- **不诚实新增 `Rank 9c`。**

## 6) trade on / trade off（仅对既有 residual 的复核）
本轮不新增 derived hypothesis，但为了便于后续人工接手，仍把既有 residual 复核一句：

- trade on：把 `EMA(RSI)` 留在 shared allow/deny 层，优先回答“哪些 setup 不该在明显逆势环境里硬上”；
- trade off：放弃“regime-switch stack 本身就是完整 entry alpha”的原读法，接受它只能做更窄的 veto 角色，且改善仍可能只是靠砍单美化。

## 7) 本轮结论
- 原 Rank 为什么 park：因为 standalone regime-switch entry stack 在收益、交易密度与稳定性上一起失败；
- 它更像：`soft park，但比 2026-03-19 更偏硬`；
- 可救信号：有，但仍只剩既有 `Rank 9b` 这条 residual；
- 最值得改的唯一一刀：仍是 `standalone stack -> EMA(RSI) asymmetric shared veto`；
- 是否值得形成新的 derived hypothesis：**否**；
- 本轮最终结论：`keep_park`。

## 8) 文件与提交流程说明
- 本轮只更新本日志、`research/park_reframe/INDEX.md` 与 `docs/PARK_REFRAME_QUEUE.md`；
- 默认不改 `docs/TODO.md` 顶部排班；
- 本轮未做 git commit：按 brief 先保持最小必要文件改动，且若工作区存在无关脏文件，不混提。