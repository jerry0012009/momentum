# 别把 15m volume confirmation 继续写成 rolling SMA：`same-clock intraday RVOL` 更像 breakout-short / Fib / EMA 的 honest volume gate
- 时间：2026-03-20 08:51 UTC
- 类型：GitHub 仓库 + Binance 公共数据快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/volume/intraday-seasonality/same-clock/rvol/confirmation/filter/repo/crypto/5m/15m
- 证据类型：仓库代码 + 工程快检（公开 OHLCV）

## 1. 这次看了什么
这次主看一个很新的 GitHub 仓库 **ycchew/CQ_breakout_strategy**（2026-03 创建）。真正值得偷的，不是 repo 里那些日线股票 breakout 参数，而是它在 `indicators/volume.py` 里单独写出来、但很多 desk 会忽略的一层：**`calculate_intraday_rvol` 会把当前 bar 的成交量，拿去和“历史同一时刻的 bar”比较，而不是拿最近 20 根滚动均量硬比。**

## 2. 核心结论
- **一句话核心结论：** 对 24/7 crypto 的 5m/15m，很多所谓“放量确认 / 缩量回踩”先该过的不是更神的阈值，而是**同钟点归一化**；不然你测到的经常只是 UTC 时段差，不是真 setup 质量。
- **一句话证明方式：** repo 直接给了 `same-time-of-day` 的 RVOL 计算骨架；我又用 **Binance Futures BTCUSDT 15m 公共 K 线**做了一个最小快检，看 naive RVOL 和 same-clock RVOL 到底有多常打架。
- 快检样本：**6000 根 BTCUSDT 15m perp bar**，时间覆盖 **2026-01-16 21:00 UTC ~ 2026-03-20 08:45 UTC**。
- 关键数据点 1：不同 15m 时段的平均成交额差异很大。样本里最活跃 slot 是 **14:30 UTC**，平均 quote volume 约 **4.51e8**；最弱 slot 是 **21:45 UTC**，约 **7.71e7**；**同是 15m bar，强弱时段均值差约 5.85 倍**。
- 关键数据点 2：在最近 **20 天 / 1440 根 bar** 上，若把 `naive_rvol > 1.5` 当“放量”，会有 **3.96%** 的 bar 属于“naive 看着像 spike，但 same-clock 其实只是正常”；反过来有 **2.57%** 的 bar 是“same-clock 真 spike，但 naive 看不出来”。
- 关键数据点 3：对 `dry-down` 更敏感：若把 `rvol < 0.7` 当“缩量”，则有 **10.83%** 的 bar 是“naive 说缩量、same-clock 不认”，另有 **20.07%** 的 bar 是“same-clock 认缩量、naive 没认”。这对 `Fib retest_hold` 很关键，因为我们最近不少确认层正依赖“回踩时量能降下来”。
- 补一条：两种 RVOL 当然不是完全无关，但相关系数也只有 **0.765**，说明它们不是简单换皮。

## 3. 为什么这轮值得先做
这轮不是偏题，反而是在给三条收口线补一个共同的“地基洞”：**你现在很多 confirmation layer 都在用 volume，但 volume 本身若没先做时段归一化，后面的 gate 很容易是伪精细。**

- **V3 final-verdict / breakout-short follow-up**
  - 很多 follow-up / failure 判决都要看 break 后有没有“跟量”。
  - 如果 14:30 UTC 天生就比 21:45 UTC 活跃很多，`rolling mean` 会把“正常活跃时段”误判成 spike，也会把冷时段里的真正异常量漏掉。
  - 对 short 侧尤其危险：你可能以为自己在拦“假延续”，其实只是在惩罚冷门时段。

- **Fibonacci confirmation / retest_hold**
  - 这条线近期多次依赖“回踩缩量、反弹再放量”。
  - 但缩量如果不用 same-clock 口径，很容易把“亚洲慢时段的正常低量”误当成优质 hold，把“美盘高量时段里的真实 dry-down”漏掉。

- **EMA / PSAR raw alpha focus**
  - raw alpha 现在最怕的是：本来 edge 就薄，还叠上一个不诚实的 volume filter。
  - same-clock RVOL 的价值不在于让 raw alpha 突然变神，而在于**先把 volume 这层从时段偏差里洗干净**，再判断 EMA / PSAR 到底有没有被 volume 确认真正改善。

## 4. repo 里最值得偷的，不是“volume spike > 2x”，而是这个实现口径
repo 的 `calculate_intraday_rvol` 大意是：
1. 先把每根 bar 映射到 `HH:MM` 时刻；
2. 对每个时刻单独维护历史均量；
3. 当前 bar 用 `当前量 / 历史同 slot 均量` 得到 `intraday_rvol`。

把它翻回我们 desk 语言，就是：
- `14:30` 只和历史 `14:30` 比；
- `21:45` 只和历史 `21:45` 比；
- 不再把整个日内流量曲线压扁成一条统一均线。

这很适合当前阶段，因为它不是又加一个复杂外部数据源，也不是重做主信号；**它只是把已有 volume gate 的计量口径修正得更诚实。**

## 5. 可复刻的最小实验（下一步怎么测）
### 研究假设
把当前所有 `volume confirmation / dry-down` 从 `naive rolling RVOL` 改成 `same-clock RVOL` 后，能减少 false confirm，并保留更多真正有信息的慢时段 setup。

### 数据源（公开可得）
- 价格与成交量：**Binance Futures /fapi/v1/klines**（公开 API，15m 近实时更新）
- 公开性：公开可得
- 更新频率：每根 5m/15m bar 更新
- 最小可复现实验口径：BTC/ETH/SOL perp，先看 15m，再补 5m

### 首版冻结定义
1. 对每个 symbol、每个 `HH:MM` 维护过去 `N=20` 次同 slot 的均量：
   - `slot_avg_vol_t = mean(volume at same HH:MM over past N occurrences)`
2. 定义：
   - `slot_rvol = volume / slot_avg_vol_t`
   - `slot_dry = slot_rvol < 0.7`
   - `slot_spike = slot_rvol > 1.5`
3. 对照组：继续用现有 `rolling 20-bar RVOL`

### 接到三条线怎么测
- **breakout-short**：把 post-break follow-up 的 `volume confirm` 从 naive RVOL 改成 `slot_spike`；比较 `4~8 bars` 内回抽失败率。
- **Fib retest_hold**：回踩阶段用 `slot_dry`，重破阶段用 `slot_spike`；看 `hold confirmed` 后的 `N-bar continuation` 是否更干净。
- **EMA / PSAR raw alpha**：只把 volume gate 换口径，不改 EMA / PSAR 本体；看是否能在不大砍 trade count 的前提下抬 `post-cost expectancy`。

### 先看哪 2 个指标
- `post-cost expectancy`
- `false-follow / false-hold rate`（入场后 `4~8` 根内回到 opposite edge 或失守确认线）

## 6. 风险与保留意见
- 这轮证据主要来自 **repo 实现 + 公共数据快检**，不是已经证明 15m alpha 提升；真正结论必须来自 A/B 回测。
- repo 原始场景是股票 breakout，不是 crypto perp；我们偷的是 **计量口径**，不是整套策略。
- same-clock RVOL 也不是万能：若市场正处在宏观事件或突发行情里，同 slot 历史均量本身会滞后，因此后续最好再叠一个 `event / jump blackout`。

## 7. 来源
1. **ycchew. (2026). _Christian Qullamaggie Strategy_. GitHub repository.**
   - Repo URL: `https://github.com/ycchew/CQ_breakout_strategy`
   - Readable URL: `https://github.com/ycchew/CQ_breakout_strategy/blob/master/README.md`
   - Volume implementation: `https://github.com/ycchew/CQ_breakout_strategy/blob/master/indicators/volume.py`
   - Breakout strategy: `https://github.com/ycchew/CQ_breakout_strategy/blob/master/strategies/breakout.py`
   - DOI: `N/A`
   - Authors: GitHub user `ycchew`
2. **Binance. _USDⓈ-M Futures Market Data REST API: Kline/Candlestick Data_.**
   - Docs URL: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
   - Data URL example: `https://fapi.binance.com/fapi/v1/klines?symbol=BTCUSDT&interval=15m&limit=1500`
   - 公开性：公开 API
   - 更新频率：每根 K 线更新
   - DOI: `N/A`

---
快检文件：
- `reports/artifacts/literature/same_clock_intraday_rvol_quickcheck_2026-03-20.json`
- `reports/artifacts/literature/same_clock_intraday_rvol_slot_stats_2026-03-20.csv`
- `reports/artifacts/literature/same_clock_intraday_rvol_examples_2026-03-20.csv`
