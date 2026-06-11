# 别把 15m 冲击延续当“跨时段默认”：`abnormal-return event clock` 更像 breakout-short / Fib / EMA-PSAR 的 follow-up 与 timeout gate
- 时间：2026-03-20 06:08 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/event-clock/abnormal-return/follow-up/failure/regime/filter/timeout/crypto/15m
- 证据类型：论文证据

## 1. 这次看了什么
这次主看 Caporale & Plastun (2020) 对 BTC/ETH/LTC 的“单日异常涨跌后，小时级路径怎么走”的实证，重点不是它的 headline，而是可直接迁移到 15m 的旁支：**同一时段延续更强，跨时段延续明显变脆，且存在方向不对称例外**。

## 2. 核心结论
- **一句话核心结论**：对 5m/15m desk，更该先把“冲击后还能追多久”写成 `event-clock`，而不是默认信号可无脑 carry 到下个时段。
- **一句话证明方式**：作者用 2015-2019 的 BTC/ETH/LTC 小时数据做 abnormal-return 事件分组 + CAR + 交易仿真，比较“事件当日”与“次日”的延续稳定性。
- 数据口径：BTC/ETH/LTC vs USD，2015-01-01~2019-09-01；异常收益用动态阈值（BTC `k=2σ`，ETH/LTC `k=1.5σ`）。
- 关键发现 1（最可复用）：事件当日延续很强；正异常日 Strategy 1 总收益分别约 BTC `143.11%`、LTC `311.39%`、ETH `507.63%`（样本期累计，胜率高）。
- 关键发现 2（对 final-verdict 更关键）：次日延续显著变弱且不稳，部分情形转成反转（如 BTC 正异常、ETH 负异常出现 contrarian），说明“跨时段继续追”需要更严格否决层。

## 3. 为什么和当前项目有关
- `V3 final-verdict / breakout-short follow-up`：可直接加一层 `event-age gate`——冲击后优先做“同 session follow-up”，超过时段窗口默认降级为“需二次确认/不追”。
- `Fibonacci confirmation / retest_hold`：冲击后首次回踩若发生在事件窗口内可高权重；跨窗口回踩默认降权，避免把“晚到的回踩”误判成高质量 retest。
- `EMA / PSAR raw alpha focus`：把 `event-clock` 当 overlay，而非改 EMA/PSAR 本体，可更快验证“原始触发 + 时间衰减门控”是否优于裸信号。

## 4. 可复刻的最小实验（先做这个）
1. 资产与周期：`BTC/ETH/SOL perp, 15m`（执行层可加 5m）；样本先 `180d`。
2. 事件定义：`abs(ret_15m) > μ + k·σ`（rolling 96 bars），先测 `k∈{1.8,2.2}`；记录事件方向与 `event_age`（距事件发生的 bar 数）。
3. 三臂对照：
   - `baseline`：现有 breakout-short / fib / ema-psar 规则；
   - `same-window-only`：仅允许 `event_age<=N`（如 8~12 bars）方向一致 follow-up；
   - `window+timeout`：`event_age>N` 后必须额外满足二次确认（如 close-confirm reclaim / re-break）才可入场。
4. 先看两项：`成本后总收益`、`post-break false-follow rate`（特别是跨窗口交易的失败占比）。

## 5. 风险与保留意见
- 论文样本到 2019，且是现货口径；对当前 perp 微观结构（资金费率、清算链）需做 OOS 再确认。
- 论文交易仿真未完整纳入现实交易摩擦（作者也说明该限制）；迁移到 15m 时必须先过 friction ladder。
- “按 UTC 日切分”的时钟可能与 crypto 真实流动性时钟不完全一致；实作时建议并行测试 `UTC day` 与 `rolling event-age` 两种切法。

## 6. 来源
1. Caporale, G. M., & Plastun, A. (2020). *Momentum effects in the cryptocurrency market after one-day abnormal returns*. Financial Markets and Portfolio Management, 34, 251–266.
   - DOI: https://doi.org/10.1007/s11408-020-00357-1
   - Readable URL: https://link.springer.com/article/10.1007/s11408-020-00357-1
   - PDF URL: https://link.springer.com/content/pdf/10.1007/s11408-020-00357-1.pdf
   - Repo URL: N/A（论文未提供官方代码仓库）
