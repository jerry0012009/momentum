# Rank pending / ER-90 impulse exhaustion fade first verdict -> background/P0

- 时间：2026-04-24 22:58 UTC
- 对象：`research/quant_digests/2026-04-24_2043_er90-impulse-exhaustion-fade-alpha.md`
- 轮次类型：bot3 fresh intake first verdict
- 结论：`background/P0`

## 为什么这轮直接收口
本轮按 `cycle_plan` 只检查一个最小 decisive blocker：这个 repo 里的所谓 `短时 ATR impulse exhaustion × RSI5 extreme × failure-to-extend fade`，是否真的已经作为可执行 alpha 留下独立的 after-cost exhaustion-fade pocket，而不只是 README 叙事上的完整版故事。

结论是否定的，因此这条 fresh intake 不保留到 `P1`。

## 这轮实际核验到的最小证据
直接复核 `Harvest` 上游源码后，最关键事实不是 README 的高胜率叙事，而是 `strategies/er90.py` 的真实入场条件：

- 文档字符串声称入场需要同时满足：
  - `<2h` 内 `1.5~2.0 x ATR` impulse
  - `RSI(5)` 极值
  - volume spike then decline
  - failure to extend high/low
- 但实际 `check_entry()` 最终硬性写进判定的，只剩：
  - `rsi_signal > er90_rsi_upper` 且 `rsi_1h > 50` -> `SHORT`
  - `rsi_signal < er90_rsi_lower` 且 `rsi_1h < 50` -> `LONG`
- `impulse`、`volume_spiked / volume_declining`、`failed_to_extend_high / low` 虽然被计算了，但当前版本并没有并入最终入场 gating。
- `core/models.py` 还把 admission 阈值进一步放松为：
  - `er90_impulse_atr_min = 1.0`
  - `er90_rsi_upper = 65`
  - `er90_rsi_lower = 35`

因此，这个仓当前真正可执行的 alpha，不是 digest 标题里的 `impulse exhaustion fade`，而是一个更宽松的 `短周期 RSI 极值 + 1h RSI 背景` 反转壳，再外挂固定 bracket 风控。

## 为什么不足以 keep_P1
`cycle_plan` 给出的 keep 条件是：只有当 `impulse / failure-to-extend` 语义不是 README 幻觉、且至少一个 `5m/15m` exhaustion-fade pocket 在统一成本口径下明显成立，才保留到 `P1`。

这轮最便宜、也最能改变结论的 honesty 检查已经直接否掉前半句：

1. `impulse / failure-to-extend / volume decay` 在当前 repo 里不是硬执行条件，属于叙事层而不是真实 admission。
2. 仓内也没有随手可用的 trade ledger / asset-by-asset after-cost pocket 证据，能证明 `5m/15m` exhaustion-fade 这条更强语义本身成立。
3. 既然 alpha 本体没有被真正实现，repo 结果即便为正，也无法归因到我们想 intake 的 `impulse-end exhaustion fade`，而更可能只是宽松 RSI reversal + higher-timeframe bias 的表现。

在这种情况下继续把它留在 `P1`，只会把一个“叙事比实现更强”的 repo 壳带进前排，不符合 first-verdict 的诚实收口标准。

## 本轮改变的系统认知
这条 intake 不是一个已经留下可执行 after-cost pocket 的 `exhaustion-fade` 候选；它更像一份可供未来重写/补全 admission 的研究骨架。当前应直接记入 `background/P0`，不占用 survivor 预算。

## 对 runtime 的回写口径
- fresh intake 当前对象：`background/P0`
- 不分配 Rank（因未达到 `keep_P1`）
- `cycle_plan` 第 1 项收口为 `done`

## 一句话 verdict
`ER-90` 当前源码并没有把 impulse / failure-to-extend exhaustion 语义真正接进入场判定，缺少能证明该 alpha 本体在统一成本口径下成立的 pocket 证据，因此本轮 first verdict 直接收口为 `background/P0`。

## 尾部执行状态（异步回执）
- `publish_homepage_index.sh`：本轮尝试后收到异步结束回执 `signal SIGKILL`，按 policy 记为非阻断尾部失败，不影响本轮 verdict/state/log 生效。
- 邮件摘要：发送成功（`send_text_email.py` 退出码 0）。
