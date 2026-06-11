# 别把 15m 压缩期也硬做趋势：BB inside KC 的 squeeze→release，更像 breakout-short / Fib / EMA 的 shared avoid-chop gate
- 时间：2026-03-18 13:28 UTC
- 类型：GitHub
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/squeeze/compression/expansion/regime/filter/repo/crypto/15m
- 证据类型：工程经验 / 待验证

## 1. 这次看了什么
看的是两个开源实现：`GiustiRo/squeezem-adx-ttm`（把 Squeeze Momentum、ADX、TTM Waves 拼到一张 Pine 面板里）和 `hackingthemarkets/ttm-squeeze`（用 Python 直接把 **Bollinger Band 完全收进 Keltner Channel** 定义成 `squeeze_on`，再检测 `coming out the squeeze`）。对当前 desk 来说，最值得抄的不是整套指标拼盘，而是一个更朴素的 shared gate：**当 15m 还困在压缩里时，别急着把 breakout、Fib 回踩或 EMA 延续都当成已经启动。**

## 2. 核心结论
- **一句话核心结论**：对 `Crypto 5m/15m`，`squeeze_on` 更像 `no-trade / avoid-chop` 提醒，`squeeze_off` 后的前几根扩张 bar 才更像值得让三条收口线出手的窗口。
- **一句话证明方式**：两份 repo 都把规则直接写进代码——核心不是主观画图，而是 `BB(20,2)` 是否被 `KC(20,1.5*ATR)` 完整包住；一旦从 `sqz_on=1` 变成 `0`，就视为压缩结束、波动重新扩张。
- 最值得复用的不是 John Carter / TTM 的整套话术，而是这层**状态切换**：`压缩中`、`刚释放`、`已扩张一段时间`，这比“线碰到了没”更贴 15m 执行。
- 它比继续给三条线各补一个独立过滤器更值得先看，是因为它横向回答的是同一个痛点：**很多假 breakout、假 retest、假 EMA continuation，本质上都发生在低波压缩没结束时。**
- 和今天已经写过的 `OI / liquidation / VWAP / CHoCH` 不同，这条线只依赖现有 OHLCV，接入成本最低，也最适合先做一刀最小实验。

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：如果跌破发生时仍处在 `sqz_on`，更诚实的读法往往不是 continuation，而是 **箱体内假动作 / chop break**；只有 `sqz_off` 后继续扩张，short follow-through 才更值得信。
- 对 `Fibonacci confirmation / retest_hold`：Fib 告诉我们“价格回到哪”，但 squeeze 状态能补一句“这次回踩是在压缩里乱抖，还是已经完成压缩、开始重新放大”。
- 对 `EMA / PSAR raw alpha focus`：这条线最像 shared regime veto——**EMA/PSAR 负责方向，squeeze 负责判断这段行情到底有没有从静音切到可交易。**
- 如果要回答“为什么它比继续各自收口更值钱”，答案也够直接：它不是开新支线，而是在给三条线找一个共同的 `avoid-chop / expansion-confirmation` 层。

## 4. 可复刻的最小实验
- **研究假设**：把 `BB inside KC` 的压缩/释放状态接到现有三条 base archetype 上，能在不明显砍死样本的前提下，减少 `2~4 bar` 假启动与成本后磨损。
- **最小可计算定义**：
  1. `sqz_on_t = [lowerBB(20,2) > lowerKC(20,1.5ATR)] and [upperBB(20,2) < upperKC(20,1.5ATR)]`
  2. `release_t = sqz_on_{t-1}=1 and sqz_on_t=0`
  3. 可选方向确认：沿用 repo 的 `linreg momentum` 正负号；long 要求 `mom_t > 0`，short 镜像。
- **四臂先比**：
  1. `base`
  2. `base + no_sqz_on_veto`（压缩中不做）
  3. `base + release_recent_gate`（只接受 `release_t` 后 `1~4` 根内的信号）
  4. `base + release_recent_gate + momentum_sign`
- **最小回测切口**：`BTC / ETH / SOL` perpetual，最近 `120~180d`，`15m`，把它压到三条 archetype：`breakdown_reclaim_short`、`fib_retest_hold`、`ema_slope_continuation`；统一 `next-bar open + no-overlap`，成本先看 `6 / 10 bps per side`。
- **最先看的 4 个指标**：`whipsaw_2bars / 4bars`、`post-cost expectancy`、`trade_count_retention`、`follow-through@4/8 bars`。
- **下一步怎么测**：先别问“收益最高是哪臂”，先只问一个 yes/no——**`no_sqz_on` 或 `release_recent` 能不能稳定减少假启动，而不是单纯靠大幅砍样本？** 如果能，它就配进 shared gate 候选池；如果 retention 掉太多、收益没改善，就快速压回 evidence pool。

## 5. 风险与保留意见
- 这是 **repo 工程证据**，不是论文 OOS 证据；它证明的是“规则可冻结”，不是“edge 已成立”。
- `BB/KC` 参数非常容易被调参美化；`20/2/1.5` 只能先当默认基线，不该一开始就扫太大参数网格。
- `release` 常常是 **晚确认**：它可能减少假动作，但也可能把最好的一段初始扩张让掉，尤其在 crypto 里经常发生“刚 release 就一根走完”。
- 24/7 市场里，低波压缩也可能只是亚洲午后或周末静音；如果后续发现 edge 主要来自 session effect，就要把它降级成与活跃时段联动的 filter，而不是独立 alpha。
- 它和早上那篇 `EMA + ADX + volume` 有邻近性，所以这轮刻意不把 ADX 当主角；若最终改善主要来自 ADX 而不是 `sqz_on/off` 状态机，就应把功劳还给 ADX，不要混记。

## 6. 来源
- GiustiRo. (2023). *squeezem-adx-ttm*.
  - Venue / DOI：无（GitHub repo）
  - Repo URL: <https://github.com/GiustiRo/squeezem-adx-ttm>
  - Readable URL: <https://github.com/GiustiRo/squeezem-adx-ttm/blob/main/README.md>
  - Raw script URL: <https://raw.githubusercontent.com/GiustiRo/squeezem-adx-ttm/main/script>
- hackingthemarkets. (2020). *ttm-squeeze*.
  - Venue / DOI：无（GitHub repo）
  - Repo URL: <https://github.com/hackingthemarkets/ttm-squeeze>
  - Readable URL: <https://github.com/hackingthemarkets/ttm-squeeze/blob/master/squeeze.py>
  - Raw code URL: <https://raw.githubusercontent.com/hackingthemarkets/ttm-squeeze/master/squeeze.py>
- 概念母体（仅作背景，不作为本轮主证据）：John F. Carter. *Mastering the Trade* / TTM Squeeze 系列讲法。