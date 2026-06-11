# 别把 cross-venue funding carry 继续做成 always-on 收租：这份 2025/2026 GitHub 新仓库更该先测的是「APR gate × spread veto × forced refresh」完整 raw alpha
- 时间：2026-03-28 03:34 UTC
- 类型：2025 GitHub 新仓库 + README/source/脚本审阅 + 近 2 年 funding 定价论文地基
- 主题类型：raw alpha
- 基础 alpha：同一币种跨 venue 做 `long 低 funding venue + short 高 funding venue` 的 delta-neutral carry，并只在 `净 APR 足够高 + 腿间价格没明显错位` 时开仓
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/cross-venue/relative-value/stat-arb/delta-neutral/rotation-scheduler/apr-gate/spread-veto/forced-refresh/execution-risk/crypto/1m/3m/5m/15m/repo/paper
- 证据类型：工程实现证据 + 论文地基

## 1. 这次看了什么
主材料是 **djienne (repo created 2025-10, updated 2026-03)** 的 GitHub 仓库 **`CROSS_EXCHANGE_DELTA_NEUTRAL_LIGHTER_EDGEX`**。我重点看了 `README.md`、`lighter_edgex_hedge.py`、`test_funding_comparison.py`、`check_all_spreads.py`、`check_volume.py`。这次最值得 intake 的，不是“funding carry 这件事存在”，而是它把一条 raw alpha 写成了可运行的 **轮动调度器**：先比两边 funding APR，再过流动性和 price spread 门槛，开完双腿后强制持有一个 funding collecting 窗口，再统一平掉重扫。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正值钱的不是“跨 venue 收 funding”这个老话题，而是把它明确做成了一个 **有开机门槛、有强平/回滚、有刷新节奏** 的完整策略骨架。
- **一句话它怎么证明：** 不是靠摘要结论，而是靠源码把 `entry / exit / sizing / risk / execution` 全部写出来了。
- repo 里最重要的三道开仓门：`min_net_apr_threshold = 5%`、`min_volume_usd = 250,000,000`、`max_spread_pct = 0.15%`。这比“看见 funding spread 就上”诚实得多。
- 代码默认把仓位当成 **状态机** 来管理：`IDLE → ANALYZING → OPENING → HOLDING → CLOSING → WAITING → ERROR`。这说明 alpha 本体不是静态 snapshot，而是一个需要持续治理的 carry cycle。
- 这份实现显式处理了 **partial fill rollback**：若一条腿成交、另一条腿失败，就立即平掉成功那条腿，避免 orphaned exposure。对实盘来说，这比多讲一页 funding 理论更有价值。
- 资金费节奏本身也被工程化了：repo 的 comparison 脚本明确写到 **EdgeX 每 4 小时 funding 一次（6x/day），Lighter 每小时一次（24x/day）**；主 bot 默认 `hold_duration_hours = 8`，README 示例则给了 `12h` 版本，说明它本来就是按 funding clock 做 refresh，而不是 always-on 死拿。
- 执行层同样没含糊：开仓用 **相对 mid price 的 `±3%` aggressive limit**，再叠加 **5% capital buffer**、按两边较小容量定 size、以及按杠杆自动算 stop-loss。也就是说，这不是“只会选方向”的半成品，而是完整交易骨架。

## 3. 为什么和当前项目有关
这条线和当前 desk 直接相关，因为它补的是 **carry / relative-value / stat-arb** 素材池里更接近 production 的一段：
- 它不是解释 funding 的 overlay，而是可以单独跑的 **raw alpha**；
- 它适合 `1m/3m/5m/15m` 的方式不是逐根猜方向，而是：**短周期监控 APR、价差、成交量和腿间风险；funding clock 负责兑现 alpha**；
- 对当前项目更有价值的点，是它把“开不开机、何时刷新、哪一腿失败时怎么回滚”全都写清楚了，方便后面直接做最小复现。

## 3.5 策略拆解（必填）
- 方向属性：carry / relative-value / cross-venue delta-neutral
- 基础 alpha：`funding_high_venue - funding_low_venue - trading_cost - hedge_slippage - spread_drift`
- regime：优先在 funding 分化足够大、腿间价格仍紧、两边成交量够厚时启动；主流币优先，先做 `BTC / ETH / SOL`
- filter / veto：`net APR >= 5%`、`combined 24h volume >= 250M USD`、`cross-venue mid spread <= 0.15%`；若 funding 翻号、quote 失真、单腿失败、容量不够则直接 veto
- risk / sizing / execution overlay：仓位按两边较小可用容量定 size；使用 capital buffer；单腿失败立即 rollback；达到 hold window 或 stop-loss 就平仓；下一轮重新选 symbol，不做无脑续抱

## 4. 可复刻的最小实验
### 4.1 研究假设
比起 always-on 持有，**`APR gate + spread veto + forced refresh`** 的 cross-venue funding carry，在短周期监控下更像一条可活的完整策略，而不是一张静态收益表。

### 4.2 数据源、公开性、更新频率
- `test_funding_comparison.py`：比较 EdgeX / Lighter funding 并换算 APR
- `check_all_spreads.py`：抓两边 best bid/ask 与 mid spread
- `check_volume.py`：抓 24h volume 过滤
- 公开性：**信号侧市场数据可先按 repo 的比较脚本/交易所公开行情接口复现；真正下单才需要私有凭证**
- 更新频率：funding 以交易所 funding clock 更新；quote / best bid-ask 可按秒级或更快采样，再聚合到 `1m / 3m / 5m / 15m`

### 4.3 最小实验口径
1. 先只做 `BTC / ETH / SOL` 三个币，逐分钟记录：`net_apr_t`、`mid_spread_t`、`volume_filter_t`。
2. 生成两套组合：
   - A：always-on（只要 funding spread 为正就持有）
   - B：gate+refresh（`APR>=5%`、`spread<=0.15%`、`vol>=250M` 才开，最多持有 `8h`）
3. exit 规则先用最朴素版本：
   - 到下一 funding 收取窗或 `8h` 上限就平；
   - 若 `net_apr` 翻负或 `mid_spread` 超过 `0.15%` 则提前平。
4. 输出四个 first-verdict 指标：`post-cost APR`、`spread blowout frequency`、`partial-fill proxy ratio`、`capital utilization`。

## 5. 先记住的交易结论
如果这条线要进 desk，不该再被写成“看 funding 榨票息”，而该被写成：**一条由 funding clock 驱动、由 quote spread 和流动性决定是否开机、并且必须内建 rollback/refresh 的完整 carry 策略。**

## 6. 下一步怎么测
1. **先做 signal-only 回放**：不连私钥，只记录两边 funding / quote / volume，验证三道 gate 之后 trade count 还剩多少。
2. **把 hold window 做成网格**：`1h / 4h / 8h / 12h` 四档，检查真正赚的是 funding 还是只是在吃腿间 mark-to-market 漂移。
3. **补最小成本阶梯**：maker-maker、maker-taker、taker-taker 三档，把“3% aggressive fill”对应的实际滑点诚实加进去。
4. **单独统计 rollback 风险**：哪怕 paper side 很美，只要单腿失败率高，这条线就该降权，不要靠想象补收益。

## 7. 来源
1. **djienne. (2025/2026). _CROSS_EXCHANGE_DELTA_NEUTRAL_LIGHTER_EDGEX_. GitHub repository.**
   - Authors: djienne
   - Year: repository created 2025, updated 2026
   - Title: *CROSS_EXCHANGE_DELTA_NEUTRAL_LIGHTER_EDGEX*
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: https://github.com/djienne/CROSS_EXCHANGE_DELTA_NEUTRAL_LIGHTER_EDGEX
   - Repo URL: https://github.com/djienne/CROSS_EXCHANGE_DELTA_NEUTRAL_LIGHTER_EDGEX

2. **Park, H., Choi, M., & Lim, A. E. B. (2025). _Designing funding rates for perpetual futures in cryptocurrency markets_. arXiv.**
   - Venue: arXiv
   - DOI: https://doi.org/10.48550/arXiv.2506.08573
   - Readable URL: https://arxiv.org/abs/2506.08573
   - Repo URL: N/A

3. **He, S., Manela, A., Ross, O., & von Wachter, V. (2024). _Fundamentals of Perpetual Futures_. arXiv.**
   - Venue: arXiv
   - DOI: https://doi.org/10.48550/arXiv.2212.06888
   - Readable URL: https://arxiv.org/abs/2212.06888
   - Repo URL: N/A
