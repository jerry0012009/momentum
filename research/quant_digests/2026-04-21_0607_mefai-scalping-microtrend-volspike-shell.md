# 别把 mefai 的 scalping 模块只读成“高频拼盘”：对 short-cycle crypto desk，更该先回答的是「EMA micro-trend × volume-spike / imbalance confirmation × 15m hard-timeout」这条 raw alpha 壳到底有没有净边
- 时间：2026-04-21 06:07 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `config.yaml` + `src/strategies/scalping.py`）+ Binance USDⓈ-M public-data portability probe（8 个 liquid majors，`1m/3m/5m/15m`）
- 主题类型：raw alpha
- 基础 alpha：当超短 EMA（`3/8/21`）形成同向 micro-trend，且同时出现 **成交量突增** 或 **盘口失衡同向确认** 时，追随短时延续，使用 `0.2%` 止盈、`0.15%` 止损、`15m` 最大持有时间做 time-boxed scalp
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / single-asset / trend / momentum / scalping / ema-alignment / volume-spike / order-book-imbalance / time-stop / Binance USDⓈ-M / 1m / 3m / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo 工程壳 + public-data quick probe

## 1. 这次看了什么
这次看的是 2026 GitHub repo **mefai-dev / mefai-autotrade** 里的 `scalping.py`。它不是一句“做短线 scalp”，而是把完整壳写得很清楚：`3/8/21 EMA` 判 micro-trend，`volume_spike_mult=3.0` 找放量确认，盘口侧用 top-book `imbalance_threshold=0.3` 做方向偏置，`target_pct=0.2`、`stop_pct=0.15`、`max_hold_minutes=15`、`max_trades_per_hour=10`，而且还内置 `expected profit >= 2 × round-trip commission` 的 admission check。对我们这种 short-cycle crypto desk 来说，这不是“指标拼盘”，而是一条 **可以明确写成 entry / exit / sizing / risk / cost 的完整 raw alpha 壳**。

## 2. 先回答：这篇东西的 base alpha 是什么
一句话：**超短均线同向排列代表 micro-trend 正在形成；如果这个方向同时被成交量突增或盘口失衡确认，接下来几根 bar 仍有短时延续概率。**

所以它是 `raw alpha`，不是单纯 filter：
- alpha 本体：micro-trend continuation
- confirmation：volume spike / order-book imbalance
- execution 壳：tight spread、佣金过滤、限时持有、rate limit

## 3. repo 里真正值得拆的，不是“会 scalp”，而是这一整套 admission 壳
从 `scalping.py` 和 `config.yaml` 能拆出一条很完整的策略骨架：
- **入场**：
  - `EMA(3) > EMA(8) > EMA(21)` 做多，反之做空；
  - 再要求 `order book imbalance` 同向，或 `当前量 >= 20-bar 均量 × 3`；
  - 若 spread 太宽（默认 `>0.05%`）则 veto；
  - 若预期毛利不足以覆盖 `2×` round-trip 佣金则 veto。
- **出场**：
  - 固定 TP `0.2%`；
  - 固定 SL `0.15%`；
  - 最长持有 `15m`；
  - 若持仓已盈利且盘口失衡反向，可提早止盈；
  - 目标被穿越后还尝试做一层 trailing-profit 逻辑。
- **仓位**：默认 `position_size_pct=5%`。
- **节流**：默认每小时不超过 `10` 笔。

这也是它比一般“1 分钟追涨脚本”更有研究价值的原因：**它把 raw alpha 与 execution / risk 绑在了一起。**

## 4. 我做了什么最小实验
为了先判断这条东西是不是值得继续深挖，我先做了一个 **不依赖私有撮合、不依赖私有 order-book 历史** 的 public-data probe：
1. 数据：Binance USDⓈ-M 公共 K 线；
2. 标的：`BTC/ETH/SOL/BNB/XRP/DOGE/LINK/AVAX` 8 个 liquid majors；
3. 周期：`1m/3m/5m/15m`；
4. 信号代理：保留 repo 的 `EMA(3/8/21) + volume spike` 主壳；因为这轮没拉逐秒 order-book 历史，所以先不把 `imbalance` 加进去；
5. 参数：把 repo 的 `volume_spike_mult=3.0` 轻微放宽到 `2.5`，避免样本过稀；TP/SL 仍保持 `+20bps/-15bps`；
6. time-stop 映射：
   - `1m`：`15` bars；
   - `3m`：`5` bars（约 `15m`）；
   - `5m`：`6` bars（约 `30m`，作为 5m 子壳可交易上限）；
   - `15m`：`2` bars（约 `30m`，只当 desk portability sanity check，不当 repo 原生主战场）。

## 5. quick probe 结果：这条壳“能发信号”，但当前纯 candle 版没有稳定净边
### 5.1 汇总读法
把 8 个 liquid majors 合并后：
- `1m`：`433` 笔，平均 **`-0.42 bps/trade` gross**，中位数 **`-7.03 bps`**；若粗扣 `4 bps` round-trip，变成 **`-4.42 bps` net proxy**。
- `3m`：`516` 笔，平均 **`-0.88 bps` gross**；扣 `4 bps` 后约 **`-4.88 bps`**。
- `5m`：`483` 笔，平均 **`-1.88 bps` gross**；扣 `4 bps` 后约 **`-5.88 bps`**。
- `15m`：`546` 笔，平均 **`-4.08 bps` gross**；扣 `4 bps` 后约 **`-8.08 bps`**。

更关键的是止损/止盈结构：
- `1m`：`TP 138` vs `SL 203` vs `timeout 92`
- `3m`：`TP 171` vs `SL 262` vs `timeout 83`
- `5m`：`TP 172` vs `SL 291` vs `timeout 20`
- `15m`：`TP 162` vs `SL 365` vs `timeout 19`

也就是说，**这条壳并不是“完全不触发”**，而是 **触发很多，但默认 `0.2% / 0.15%` RR 在纯 candle 代理下并没有穿过交易成本**。

### 5.2 哪些标的还算没那么差
按单币看，只有少数 pocket 没那么糟：
- `1m BTC`：`56` 笔，**`+0.35 bps gross`**，扣费后仍负；
- `1m BNB`：`43` 笔，**`+0.97 bps gross`**，扣费后仍负；
- `1m AVAX`：`61` 笔，**`+1.73 bps gross`**，扣费后仍约 **`-2.27 bps`**；
- `3m BTC`：`64` 笔，**`+1.20 bps gross`**；
- `3m DOGE`：`62` 笔，**`+0.52 bps gross`**；
- `5m ETH`：`73` 笔，**`+1.42 bps gross`**；
- `5m BNB`：`52` 笔，**`+2.24 bps gross`**。

但这些 pocket **都还没穿过保守的 `4 bps` 成本门槛**。所以这轮不能把它包装成“已验证可上”的 alpha，而应老老实实记成：**repo 给了一个完整 raw alpha 壳，但它的“candle-only 退化版”当前没过线。**

## 6. 对 desk 最有价值的判断
### 判断 1：它仍然是 raw alpha，不该被误判成纯 filter
因为它的 base alpha 很明确：
- EMA micro-trend = 方向；
- volume / imbalance = 确认；
- TP / SL / timeout = payoff 壳；
- spread / commission gate = admission 壳。

这已经是一条完整策略，不只是“风控层”。

### 判断 2：真正可能有价值的是 **order-book confirmation**，不是 candle-only 版本
这轮 public probe 故意先做最容易复现的最小实验，所以只保留了 `EMA + volume spike`。但 repo 真正区别于一堆零售 scalp 脚本的地方，是它把 **盘口失衡** 放进 admission：
- 如果 order-book imbalance 和 micro-trend 同向，信号可信度才上升；
- 还有 tight-spread veto；
- 持仓盈利后出现反向盘口也能提前出场。

而我这轮没把逐秒盘口历史加进去，因此当前结论更准确的说法是：
**纯 candle 代理下，这条壳不够好；要不要留下来，关键取决于 top-book imbalance / spread filter 能不能把坏信号删掉。**

### 判断 3：它更像 `1m/3m` 主战场，`5m/15m` 只能当 portability check
repo 自己在 README 和 config 里已经写得很明显：
- 原生时间框架是 `1m`；
- `5m` 可以作为更慢一档的 micro-trend 监控；
- 再往 `15m` 挪，已经不是同一类 scalp 了。

这轮数据也支持这个读法：随着周期拉长，止损占比明显恶化，`15m` 基本失去“超短延续 scalp”的原义。

## 7. 为什么它值得写，而不是继续找别的材料
因为现在 desk 不是只缺“又一条 headline alpha”，也缺 **完整失败样本**：
- 这条东西是标准的 **可直接落地完整策略壳**；
- base alpha 清楚；
- 公开数据可快速复现；
- quick probe 很快告诉我们：如果没有盘口确认，只靠 K 线追 micro-trend，大概率不够；
- 这正好帮我们把研究资源集中到 **order-book admission 是否真有增量价值** 这个问题上。

换句话说，这篇值得保留，不是因为它已经赢，而是因为它把一个常见但模糊的说法——“超短趋势 + 放量确认”——拆成了可验证的具体结构，并且当前 first probe 已经指出 **增量价值大概率不在 EMA 本身，而在盘口 admission。**

## 8. 下一步怎么测
1. **补 order-book 历史**：
   - 拉 Binance `bookTicker` / top-N depth snapshot；
   - 真正复刻 `imbalance_threshold` 与 `max_spread_pct`；
   - 对照 `EMA+volume` vs `EMA+imbalance` vs `EMA+volume+imbalance` 三版。
2. **做 admission ablation**：
   - 只要一个问题：盘口过滤能不能显著降低 `SL rate`；
   - 若不能，就说明这条壳不值得再加细节。
3. **把成本写实**：
   - maker/taker 混合费率不该只粗扣 `4 bps`；
   - 需要单独测 `maker exit / taker emergency exit / timeout forced close` 三种成本分布。
4. **做 symbol routing**：
   - 目前看全市场一起跑不行；
   - 可以只保留 `BTC/BNB/AVAX` 这类相对没那么差的 pocket，再测是否存在稳定 top-N router。
5. **重写 payoff**：
   - 现在 `+20/-15 bps` 太紧；
   - 应测试 `18/12`、`25/15`、`30/20` 与更短 timeout 的组合，看看是不是 payoff 结构先天不匹配 perp 噪声。

## 9. 结论
这篇 repo 的 **base alpha 很清楚**：**micro-trend continuation，在 volume / order-book confirmation 下做 time-boxed scalp。**

所以它合格地属于 `raw alpha`，而且是 **可独立复现、可直接落地完整策略** 的那类材料。

但这轮 first probe 也很清楚：**如果只保留 candle 侧的 EMA + volume-spike 退化版，这条壳在 `1m/3m/5m/15m` liquid majors 上都还没有穿过成本。**

因此当前最合理的 desk 结论不是“这条 alpha 成立”，而是：
**先别再优化 EMA 细节；优先验证 order-book imbalance / tight-spread admission 能否把这条 raw alpha 壳从负边拉回可交易。**

## 10. 来源
- Mefai Dev (2026), **Mefai Autotrade**. GitHub repo: <https://github.com/mefai-dev/mefai-autotrade>
- GitHub metadata API: <https://api.github.com/repos/mefai-dev/mefai-autotrade>
- Source audit files:
  - `README.md`
  - `config.yaml`
  - `src/strategies/scalping.py`
- 本地 artifacts：
  - `reports/artifacts/quant_digests/probe_scalping_1m5m_2026-04-21.py`
  - `reports/artifacts/quant_digests/scalping_microtrend_volspike_probe_summary_2026-04-21.csv`
  - `reports/artifacts/quant_digests/scalping_microtrend_volspike_probe_trades_2026-04-21.csv`
  - `reports/artifacts/quant_digests/probe_scalping_3415_2026-04-21.py`
  - `reports/artifacts/quant_digests/scalping_microtrend_volspike_probe_summary_3m15m_2026-04-21.csv`
  - `reports/artifacts/quant_digests/scalping_microtrend_volspike_probe_trades_3m15m_2026-04-21.csv`
