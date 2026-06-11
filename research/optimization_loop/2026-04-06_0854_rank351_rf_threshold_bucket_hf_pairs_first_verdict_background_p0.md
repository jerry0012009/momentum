# Rank 351 / RF threshold-bucket × HF pairs alpha — fresh intake first verdict: background / P0

- 时间：2026-04-06 08:54 UTC
- 对象：`research/quant_digests/2026-04-06_0754_rf-threshold-bucket-hf-pairs-alpha.md`
- 层级动作：`fresh intake -> background / P0`
- Rank：`351`
- 结论：这篇材料补的是 `HF pairs` 已有均值回归壳上的 `threshold selection / execution tuning`，还不足以单独成立为新的 raw alpha 主语；本轮不给 `keep_P1`，直接回到 `background / P0`。

## 为什么这轮不保留到 P1

这篇 paper 确实有价值，但它最硬的部分是：
- 不同 pair 不该共享同一个固定 trigger；
- `pair-state -> threshold bucket` 可以作为参数分层/执行层来学；
- 在作者的 `BTC-quoted spot threshold-rebalance` 设定里，RF 对阈值桶分类有一定样本内外表现。

问题在于，这些信息还没有把对象压成一条**独立的 raw alpha**，原因有三点：

1. **alpha 主语没有脱离旧 `pairs mean reversion` 本体。**
   论文的收益来源仍然是高相关 pair 的相对价格回归，RF 只是在问“这条旧 alpha 该配多宽的 trigger”。这更像 execution / admission layer，而不是一条新的独立 alpha。

2. **threshold-bucket 的 transfer 目前仍被锁在作者特定壳体里。**
   作者用的是 `2022–2024 Binance BTC-quoted spot` + `threshold rebalance`。若切到我们更关心的 `USDT perp / long-short residual shell / explicit funding + slippage`，目前 digest 只说明“值得测”，还没有把迁移后的最小诚实骨架压清。

3. **它更像“给旧 pairs 策略加一层 ML 参数分层”，不是新对象。**
   真正值得后续吸收的，是 `corr / moments / VaR -> threshold regime` 这条工程启发；但这条启发更适合被并入未来某个具体 pairs/P2 admission 的 parameter layer，而不是单独占一个前排 raw-alpha 名额。

## 本轮改变系统认知的一句话

`Rank 351`：`RF threshold-bucket × HF pairs` 并未形成独立于旧 `pairs mean reversion` 的 raw alpha 主语；当前证据更像可吸收进既有 pairs admission/execution 的参数分层层，而不是值得单独保留的 fresh intake，因此 first verdict 直接定为 `background / P0`。

## 后续处理

- 不进入 `Surviving candidate slot`
- 不升级 `P2`
- 可在未来某个具体 pairs 对象进入 admission 时，回收这里的唯一高价值启发：
  - `pair-state -> threshold bucket`
  - `固定阈值 vs corr-bucket vs learned bucket` 三组对照
  - 明确 post-cost / overlap / funding realism

## 运行备注

- 中文邮件摘要已发送。
- 首页刷新已尝试执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，但当前 cron runtime 无可用提权能力，而脚本内部依赖 `sudo mkdir/install/chown` 发布到 `/var/www/momentum-report`，因此本轮停在发布权限门槛，研究结论与 runtime state 已正常写回。
