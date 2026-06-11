# 别让裸 EMA 继续单扛 15m：5 EMA stack + ADX + volume + range filter，才像值得先测的 raw-alpha skeleton
- 时间：2026-03-18 03:34 UTC
- 类型：GitHub
- 主题标签：ema/psar/raw-alpha/adx/volume/range-filter/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
看的是 GitHub 仓库 `hasnocool/tradingview-pine-scripts` 里、Babehdyo 的开源 Pine 脚本 **EMA-ADX-VOL-CRYPTO KILLER [15M]**。它不算“已验证策略”，但很适合拿来回答当前 `EMA / PSAR raw alpha focus` 还没讲透的问题：**15m 上，裸 EMA 到底该补哪几层，才不只是把噪音包装成趋势。**

## 2. 核心结论
- **一句话核心结论**：对 15m desk 来说，值得先测的不是 `裸 EMA cross`，而是 **趋势对齐 + 强度确认 + 参与度确认 + 噪音过滤** 这 4 层 skeleton。
- **一句话证明方式**：这份脚本把规则直接写死在代码里——只有当 `close` 同侧站上/跌破 `EMA 8/13/21/34/55`、`DI+/DI-` 与方向一致且 `ADX > 20`、成交量超过 `SMA20×3.2` 或 `SMA22×1.9`、再叠加 `period=15 / mult=2.6` 的 range filter 后，才允许 `longCondition / shortCondition` 触发。
- 最值得复用的不是它的 TP/SL 参数，而是这套**分层 veto**：EMA 先回答“方向有没有排齐”，ADX 回答“这段走势有没有力”，volume 回答“是不是有人真在推”，range filter 回答“是不是还困在噪音带里”。
- 这比继续争论“EMA 8/21 还是 13/34 更神”更有 desk 价值，因为当前主问题不是均线参数，而是 **裸 EMA 为何一上成本就脆**。
- 这轮优先认领它也合理：`breakout-short` 和 `Fibonacci retest_hold` 刚拿到 fresh repo intake，而 `EMA / PSAR raw alpha focus` 还缺一个足够具体、能直接下手做最小实验的 entry skeleton。

## 3. 为什么和当前项目有关
它直接服务 `EMA / PSAR raw alpha focus`，但也能反哺另外两条收口线：
- 对 `EMA / PSAR`：它提醒我们，EMA 更像**底层方向骨架**，真正决定能不能下单的，是 ADX / volume / range 这些 veto 层；
- 对 `breakout-short follow-up`：breakdown 后若 `ADX` 不过门、volume 不扩、价格仍困在 range filter 里，就别硬追 continuation；
- 对 `Fibonacci confirmation / retest_hold`：Fib 回踩成功也不该只看“碰没碰到线”，而应叠加 **方向是否仍排齐、回踩后有没有重新脱离噪音带**。

## 4. 可复刻的最小实验
- **研究假设**：在 `15m` crypto 上，把 EMA 从单层信号升级成 `EMA stack + ADX + volume + range filter`，会比裸 EMA 更诚实，主要体现为**成本后收益更稳、假启动更少**。
- **四臂定义**：
  1. `EMA_stack_only`：`close` 同侧站上/跌破 `EMA 8/13/21/34/55`；
  2. `+ ADX_DI`：再要求 `ADX > 20` 且 `DI` 同向；
  3. `+ volume_gate`：再要求 `volume > SMA20×1.9` 或更严格的 `SMA20×3.2`；
  4. `+ range_filter`：再要求价格脱离 `period=15, mult=2.6` 的噪音带。
- **最小回测切口**：`BTC / ETH / SOL` perpetual，最近 `180~365` 天，`15m`，`next-bar open` 入场，`no-overlap`，先看 `hold 4 / 8 / 12 bars` 与 `opposite-signal exit` 两档；成本至少看 `6 / 10 / 15 bps per side`。
- **最先看的 4 个指标**：`post-cost return`、`trade_count`、`positive_asset_ratio`、`false-start rate`（可先定义成入场后 `4` 根内反向超过 `0.5 ATR` 或提前翻空/翻多）。
- **下一步怎么测**：先回答一个很窄的问题——`ADX / volume / range` 三层里，哪一层单独加上去最值钱？如果三层一起才能勉强变好，那说明 edge 很可能只是“强过滤换少交易”；如果其中某一层能单独改善 `false-start rate`，它才配进入 `breakout-short` 或 `Fib retest_hold` 的 overlay 候选池。

## 5. 风险与保留意见
- 这是 **repo 工程证据**，不是论文证据；不能把脚本名字里带 `15M` 就当成已验证适配 15m crypto。
- 原脚本 `default_qty_value=100`、`slippage=0`、`commission=0.03%`、`TP 0.9% / SL 4.2%`，风险收益比和交易摩擦设定都偏粗，不能照搬。
- `volume > SMA×3.2` 这类门槛在主流币上可能太稀，在山寨上又可能太吵；很容易把 trade count 压到失真。
- `close` 相对多条 EMA 的位置，不等于真正的 slope / trend quality；如果后续发现 edge 主要来自极少数放量冲刺 bar，而不是 EMA 结构本身，就要把它降级为事件过滤器，而不是原始 alpha。

## 6. 来源
- Babehdyo / mirror by hasnocool. (2023). *EMA-ADX-VOL-CRYPTO KILLER [15M]*.
  - Venue / DOI：无
  - Repo URL: <https://github.com/hasnocool/tradingview-pine-scripts>
  - Readable URL: <https://github.com/hasnocool/tradingview-pine-scripts/blob/main/EMA-ADX-VOL-CRYPTO%20KILLER%20%5B15M%5D.pine>
  - Raw URL: <https://raw.githubusercontent.com/hasnocool/tradingview-pine-scripts/main/EMA-ADX-VOL-CRYPTO%20KILLER%20%5B15M%5D.pine>
