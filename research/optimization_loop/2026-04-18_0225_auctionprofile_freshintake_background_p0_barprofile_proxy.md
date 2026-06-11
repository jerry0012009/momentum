# bot3 optimization loop — auction-profile value-area re-entry × LVN traverse shell first verdict

- Time: 2026-04-18 02:25 UTC
- Target: `research/quant_digests/2026-04-18_0049_auction-profile-poc-lvn-shell.md`
- Action type: fresh intake first verdict
- Verdict: `background/P0`

## What was checked
按 `cycle_plan` 只做这一个最小 honesty / execution-realism 收口：确认这条 `auction-profile value-area re-entry × LVN traverse shell` 当前可继承价值，是否足以摆脱“bar-volume profile proxy 的分箱幻觉”，从而诚实保住新的 fresh-intake front slot。

本轮直接复核源码：
- Repo raw source: `https://raw.githubusercontent.com/mefai-dev/mefai-autotrade/master/src/strategies/volume_profile.py`
- 关键实现：`_build_profile()` 明确是基于 OHLCV bar，把每根 K 线成交量按覆盖价格区间**均匀分摊到 bins**，再由此定义 `POC / VAH / VAL / HVN / LVN`

## Key evidence
### 1) profile 不是成交逐价重建，而是 bar-volume proxy
源码注释与实现都很直接：
- `Build volume profile from OHLCV candles. Distributes each bar's volume across price bins proportionally.`
- 对每根 bar：先找 `low_bin/high_bin`，再做 `vol_per_bin = bar_vol / num_bins_covered`
- 随后把 `vol_per_bin` 等量加到所覆盖的所有 bins

这意味着当前所有 `POC / value area / LVN` 节点，首先是 **bar-range × fixed-bin** 的投影产物，而不是成交逐价结构本身。

### 2) 当前 repo 没有补上能穿透该 proxy 幻觉的更强现实壳
虽然源码给了完整交易骨架（`VA re-entry`、`LVN breakout`、`ATR stop`、`risk_pct`），但本轮需要回答的是：它是否已经足以作为新的 raw-alpha front object 保留。

当前可见证据仍停留在：
- `session_bars=288`、`num_bins=50` 的固定 profile 切法
- 用 bar 的 `high/low/volume` 去均匀撒量
- 信号直接建立在这些 proxy 节点之上

repo 没有给出：
- 基于 `aggTrades` / tick / finer volume-at-price 的复核
- 不同 session 切法下 `VA re-entry` / `LVN traverse` 的稳定事件级统计
- 能证明 edge 不是由 binning/session 选择偶然制造出来的 portability / cost-after-fill 结果

### 3) 对 front-slot 来说，当前 blocker 已经足够 decisive
这条线的叙事很像样，但在最小 honesty 检查下，当前最可继承的东西主要仍是“auction-market 语言壳”，不是已诚实闭合的 raw alpha pocket：
- `POC/VA/LVN` 节点本身先受 bar-based 分箱方式强烈塑形
- crypto 24/7 的 session 定义又进一步影响 profile 形状
- 在没有更细粒度成交分布复核前，`value-area re-entry` 与 `LVN traverse` 都还不能证明不是 proxy artifact

因此，本轮 first verdict 已可直接收口：

> `auction-profile value-area re-entry × LVN traverse shell` 当前更像一个值得将来人工 reopen 的 auction-structure 研究母板，而不是已足以诚实保住 fresh-intake front slot 的独立 raw alpha 对象。

## Runtime impact
- 当前 fresh intake 对象完成 first verdict：`background/P0`
- 不分配新 `Rank`（因为未达到 `keep_P1`）
- fresh intake front slot 顺延到下一条具体对象：`research/quant_digests/2026-04-18_0146_queue-depletion-refill-asymmetry-alpha.md`

## Reader-facing one-line result
`auction-profile value-area re-entry × LVN traverse shell` 的最小 honesty 检查确认其 `POC/VA/LVN` 主要建立在 bar-volume 均匀分箱 proxy 上，当前缺少能证明 edge 不是 session/binning 幻觉的更强成交分布复核，因此本轮 fresh intake first verdict 直接收口 `background/P0`。

## Tail-step execution notes
- Homepage publish (`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`) 在异步收尾阶段以 `SIGKILL` 结束，按 policy 记为**非阻断尾部失败**，不回滚本轮 verdict / state / log。
- Email notify (`send_text_email.py`) 已成功发送。
