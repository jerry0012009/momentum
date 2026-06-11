# 别把 Fib 0.618 当 15m 单独开火键：volume > SMA24 + SMA200/EMA 过滤，更像 retest_hold 确认骨架
- 时间：2026-03-18 04:08 UTC
- 类型：GitHub
- 主题标签：fibonacci/retest-hold/confirmation/volume/ema/atr/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
看的是 GitHub 仓库 `11Muhil/FibTrend-Pro-Strategy_Pinescript`（2025）。它不是在证明 “Fib 线位本身就是 alpha”，而是把 **最近 50 根 bar 的 Fib 0.618 / 0.5、成交量门槛、SMA200 趋势过滤、EMA9/26 延续确认、ATR 出场** 写进了一段很短的 Pine 策略里。对当前 desk 来说，这正好能补 `Fibonacci confirmation / retest_hold` 还缺的一块：**回踩到 Fib 附近后，到底还要再过哪些门，才像能做的确认层。**

## 2. 核心结论
- **一句话核心结论**：对 15m 来说，Fib 更像**位置许可层**，不是单独进场键；真正值得先测的是 **Fib 位置 + 参与度确认 + 趋势确认 + 明确失效线** 这套组合。
- **一句话证明方式**：这份 repo 没讲太多故事，而是把条件直接写死在代码里——`lookback=50` 定义 rolling 高低点，`volume > SMA24` 要求有参与度，`close > fib0.618` 只说明价格回到强侧，`close > SMA200` 与 `EMA9 > EMA26` 再确认趋势延续，失效则看 `close < fib0.5`，ATR 版还加了 `1.5 ATR` 止损、`3 ATR` 目标和 `1.5%` trailing。
- 最值得复用的不是它声称的胜率，而是这套**层级分工**：`0.618` 更像 reclaim / hold 门，`0.5` 更像 pullback 已失效的 floor，volume 和 EMA/SMA 负责回答“这次回踩后有没有人继续推”。
- 这轮优先认领它也合理：`breakout-short` 和 `EMA / PSAR` 线刚各自补过 fresh repo，而 `Fib confirmation / retest_hold` 还缺一份足够工程化、能立刻切成最小实验的 skeleton。
- 但它也在提醒我们别自欺：README 明说 **4H / 1D / 1W** 更好，说明作者自己都没有把它包装成天然适配 `15m` 的现成模板；这反而是个好信号——我们应该拿它当确认层骨架，不是照抄策略。

## 3. 为什么和当前项目有关
- 对 `Fibonacci confirmation / retest_hold`：它把 “线位” 和 “确认” 分开了。`Fib 0.618` 不是触碰就进，而是先要回到强侧，再看 volume / trend 有没有一起站队。
- 对 `EMA / PSAR raw alpha focus`：这里的 `EMA9 > EMA26` 更像 continuation 质量过滤器，而不是要 EMA 单独扛原始 alpha；这和最近几轮对 EMA 角色的重估是一致的。
- 对 `V3 breakout-short follow-up`：这份 repo 主要是 long 侧模板，不能直接镜像成 short；但它至少提示我们，short 侧也该先写清楚 **回抽位置、参与度、趋势仍在弱侧、以及失效线**，而不是跌破就追。

## 4. 可复刻的最小实验
- **研究假设**：在 `15m` crypto 上，把 Fib 从“裸回撤线位”升级成 `Fib zone + volume gate + trend gate`，会比单独看线位更能降低假回踩和成本后打脸率。
- **四臂定义**：
  1. `fib_touch_raw`：价格回到 `0.618` 上方（或多头回踩后重新站上）即入场；
  2. `+ volume_gate`：再要求 `volume > SMA(volume, 24)`；
  3. `+ trend_gate`：再要求 `close > SMA200`，以及 `EMA9 > EMA26`；
  4. `+ fail_line`：在第 3 臂基础上，把 `close < fib0.5` 设为 setup 失效，另做 `1.5 ATR stop / 3 ATR target` 与 `hold 4/8/12 bars` 两套退出对照。
- **最小回测切口**：`BTC / ETH / SOL` perpetual，最近 `180~365` 天，`15m`，`next-bar open`，`no-overlap`，成本至少看 `6 / 10 / 15 bps per side`。
- **最先看的 4 个指标**：`post-cost return`、`false-retest rate`（入场后 `4` 根内反向超过 `0.5 ATR` 或跌回 `fib0.5` 下方）、`trade_count`、`positive_asset_ratio`。
- **下一步怎么测**：先别急着比谁收益最高，先回答一个更值钱的问题——**是 volume gate 更能救 Fib，还是 trend gate 更能救 Fib？** 如果只有把两层都叠满、且交易数被压得很低时结果才变好，那说明 Fib 本身边不够硬；如果单独加 `volume` 或 `trend` 其中一层就能明显改善 `false-retest rate`，它才配进入当前 `retest_hold` 收口线。

## 5. 风险与保留意见
- 这是 **小仓库工程证据**，不是论文或成熟实盘证据；仓库只有 `3` stars、`1` fork，社会证明很弱。
- 仓库主逻辑是 rolling `50` bar 高低点，不是我们更偏好的 confirmed swing / structure pivot；下放到 `15m` 后，线位会随窗口滚动而漂移，可能把“结构位”偷换成“短窗统计位”。
- README 明说高周期表现更好，这对我们不是利好，而是警告：它在 `15m` 上很可能更像过滤器而非主信号。
- 策略主要写的是 long 侧；如果要服务 `breakout-short`，必须单独做 short mirror 实验，不能把多头结论直接翻面套用。
- 代码没有完整 friction ladder，也没有 OOS / rolling / cross-market 结果；因此这轮最多算 **可复现骨架**，不算 validated alpha。

## 6. 来源
- 11Muhil. (2025). *FibTrend-Pro-Strategy_Pinescript*.
  - Venue / DOI：无
  - Repo URL: <https://github.com/11Muhil/FibTrend-Pro-Strategy_Pinescript>
  - Readable URL: <https://github.com/11Muhil/FibTrend-Pro-Strategy_Pinescript/blob/main/README.md>
  - Raw strategy URL: <https://raw.githubusercontent.com/11Muhil/FibTrend-Pro-Strategy_Pinescript/main/Scripts/FibTrend_ATR.pine>
  - Alt strategy URL: <https://raw.githubusercontent.com/11Muhil/FibTrend-Pro-Strategy_Pinescript/main/Scripts/FibTrend_1%25_TP.pine>
  - Repo API: <https://api.github.com/repos/11Muhil/FibTrend-Pro-Strategy_Pinescript>