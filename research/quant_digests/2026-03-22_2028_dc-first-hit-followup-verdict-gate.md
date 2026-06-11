# 别把 post-break follow-up 继续写成固定 N 根 bar：`Directional Change first-hit` 更像 breakout-short 的 honest final-verdict
- 时间：2026-03-22 20:28 UTC
- 类型：论文 + GitHub 仓库 + Binance 公共数据最小快检
- 主题标签：breakout-short/v3/final-verdict/follow-up/directional-change/event-driven/overshoot/timeout/failure/confirmation/filter/paper/repo/crypto/5m/15m
- 证据类型：论文证据 + 仓库实现 + 本地最小复核

## 1) 这次看了什么
这轮不是再找一个“新指标神键”，而是补 **V3 breakout-short follow-up / final-verdict** 最缺的一块：
> **post-break 到底该用“几根 15m bar 后涨跌”判延续/失败，还是该用“先撞到哪一侧阈值”来判？**

主来源是：
1. **Wu & Han (2023)** 的 *Improved Directional Change + Regime Change Detection*；
2. 一个可读 Python 实现仓库，帮助把 `Directional Change (DC)` 从概念落回代码；
3. 我又用 `BTC/ETH/SOL` 的 Binance 公共 `5m/15m` 数据做了一个 very small proxy check，看它对 15m breakout follow-up 有没有“人话价值”。

## 2) 核心结论（先说人话）
- **一句话结论：** 对我们 desk，更值得偷的不是论文里那套完整 forex tick strategy，而是 **`DC first-hit` 这套“先触发 continuation 还是先触发 reversal”的事件判决法**；它比固定 `N` 根 15m bar 更适合做 breakout-short 的 follow-up / final-verdict。  
- **一句话证据：** 论文用 event-driven sampling + threshold/adaptive regime 证明“时钟 bar 会丢掉关键信息”；我在 `BTC/ETH/SOL` 的最小快检里也看到：固定时间窗会留下不少 `timeout`，而 `DC first-hit` 往往很快就已经给出方向判决。

### 关键数据点（本地最小快检）
样本口径：`BTCUSDT/ETHUSDT/SOLUSDT`，Binance Spot 公共 `klines`；15m breakout proxy = `20-bar 前高/前低突破 + breakout bar body%/CLV 过滤`；后续路径在 `12 根 5m` 内观察；`DC threshold = 0.6 * ATR14(15m) / entry`。

1. **固定时钟 verdict 还在犹豫时，DC 往往已经判完了**
   - pooled 事件数：`147`
   - fixed `12x5m` verdict：`continue 38.8% / fail 45.6% / timeout 15.6%`
   - `DC first-hit` verdict：`continue 45.6% / fail 54.4% / timeout 0%`

2. **DC 判决很快，不像又拖出一层慢确认**
   - `mean decision time = 1.44 根 5m`
   - `median decision time = 1 根 5m`

3. **它对当前更关心的 short 侧更像样**
   - short 侧：`continue_share = 58.2%`
   - long 侧：`continue_share = 30.9%`

4. **固定时间窗里的 timeout，并不是真的“没信息”**
   - fixed timeout 样本里，`52.2%` 被 DC 重新判成 `continue`
   - 另外 `47.8%` 被判成 `fail`

> 读法：固定 N-bar 更像“时间到了再看片尾”；`DC first-hit` 更像“谁先打到 continuation / invalidation，就立刻判”。这正是 breakout-short follow-up 当前最缺的 honest verdict 口径。

## 3) 为什么这题比继续泛找更值得
它是直接帮三条收口线里最紧的一条——**`V3 final-verdict / breakout-short follow-up`**——补定义：
- **breakout-short**：最直接。把“跌破后继续走 / 假跌破回收”写成 first-hit，而不是固定几根 bar 后再做模糊总结；
- **Fib confirmation / retest_hold**：可把“回踩守住”改写成 `先完成 continuation overshoot` 还是 `先触发 opposite reversal threshold`；
- **EMA / PSAR raw alpha**：不适合拿 DC 当主触发，但适合拿它做 **post-entry continuation vs whipsaw evaluation lens**。

所以这题不是离题的新方向，而是把 **当前 follow-up / failure verdict** 讲得更诚实。

## 4) 最小可复现实验口径（建议下一步真测）
直接在现有 `support_breakout_v0 / breakout-short follow-up` 上做 A/B：

1. **A = 当前 fixed-bar verdict**
   - 例如入场后看 `N=4` 或 `N=6` 根 15m 的净结果 / timeout
2. **B = DC first-hit verdict**
   - 从 entry 开始，用 `5m` 路径观察：
     - `continuation hit`: 顺方向先走到 `k * ATR15m`
     - `failure hit`: 反方向先走到 `k * ATR15m`
   - `k` 先试：`0.4 / 0.6 / 0.8`
3. **只先测一个 family**
   - 首选：`V3 breakout-short follow-up`
   - 再决定是否扩到 Fib / EMA

优先看 4 个指标：
- `decisive_label_share`（少一点 timeout）
- `false-continuation rate`
- `post-cost excess return by verdict bucket`
- `time-to-decision`

如果 `DC first-hit` 能同时做到：
- 明显减少 timeout；
- short 侧更早筛出 fake continuation；
- OOS 不比 fixed-bar 更漂；
那它就值得升成 **follow-up / final-verdict layer**，而不是继续拿“第 N 根 bar 收哪儿”硬判。

## 5) 风险与保留意见
- 论文主实验是 **forex tick**，不是 crypto 15m，不能把收益数字直接搬过来；
- 本轮本地快检只是 **proxy event test**，不是正式策略回测；
- `theta = 0.6 * ATR` 只是 first pass，真正风险在于阈值过小会追噪音、过大又会退化成慢 verdict；
- `DC first-hit` 更适合 **判路径 / 判失败**，不等于它适合当主入场键。

## 6) 来源
1. **Wu, B., & Han, X. (2023). _Intelligent trading strategy based on improved directional change and regime change detection_. arXiv preprint.**
   - Authors / Year: Bing Wu, Xiangzu Han (2023)
   - Title: Intelligent trading strategy based on improved directional change and regime change detection
   - Venue: arXiv / cs.CE
   - DOI: <https://doi.org/10.48550/arXiv.2309.15383>
   - Readable URL: <https://arxiv.org/abs/2309.15383>
   - Repo URL: N/A
   - 论文关键结果：8 个外汇货币对中，ITA 平均累计收益从 `FT=-24.36%` 提升到 `58.76%`，平均最大回撤从 `19.08%` 降到 `3.53%`；但对我们更值钱的是它的 **event-driven first-hit / overshoot 思路**，不是直接照抄整套策略。

2. **ThomasWangWeiHong (2023). _Time-Series-Directional-Change-Analysis_. GitHub Repository.**
   - Authors / Org: ThomasWangWeiHong
   - Year: 2023（README / repo updated 2023-10）
   - Title: Time-Series-Directional-Change-Analysis
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: <https://github.com/ThomasWangWeiHong/Time-Series-Directional-Change-Analysis>
   - Repo URL: <https://github.com/ThomasWangWeiHong/Time-Series-Directional-Change-Analysis>
   - 可复用点：把 `DC event / overshoot / TMV / T` 从书面定义落成了清楚的 Python 代码骨架。

3. **Binance Open Platform (2026). _Spot REST API – Kline/Candlestick Data_.**
   - Authors / Org: Binance
   - Year: 2026
   - Title: Kline/Candlestick data
   - Venue: Binance Developers Docs
   - DOI: N/A
   - Readable URL: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data>
   - Repo URL: N/A

## 7) 产出文件（本轮）
- `reports/artifacts/quant_digests/dc_followup_proxy_20260322/dc_followup_proxy_events.csv`
- `reports/artifacts/quant_digests/dc_followup_proxy_20260322/summary_metrics.json`
- `reports/artifacts/quant_digests/dc_followup_proxy_20260322/side_summary.csv`
- `reports/artifacts/quant_digests/dc_followup_proxy_20260322/side_x_dc_bucket.csv`
- `reports/artifacts/quant_digests/dc_followup_proxy_20260322/side_x_fixed_bucket.csv`
- `reports/artifacts/quant_digests/dc_followup_proxy_20260322/fixed_timeout_dc_resolution.csv`