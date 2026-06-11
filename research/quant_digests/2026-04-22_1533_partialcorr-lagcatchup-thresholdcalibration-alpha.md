# 别把 `crypto-correlation-bot` 只读成“相关性报警器”：对 short-cycle crypto desk，更该先拆的是「BTC/ETH 残差化后按强度排名的 pair catch-up」这条 stat-arb raw alpha

- 时间：2026-04-22 15:33 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `config.py` + `correlation_engine.py` + `main.py`）+ Binance USDⓈ-M public-data portability probe（16 币，`15m/5m`，各 `1500` bars）
- 主题类型：raw alpha
- 基础 alpha：在去掉 BTC/ETH 大盘共振后，挑选“残差相关性最高”的 alt-alt 对；当短窗收益差（lead-lag divergence）拉开时，做 lagger 向 leader 方向的 catch-up
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/lead-lag/partial-correlation/btc-eth-residualization/catch-up/binance-perpetual/5m/15m/repo/public-data/cost/risk
- 证据类型：repo 规则骨架 + public-data first probe

## 1) 这次看了什么

这轮主来源是一个 2026 新仓：

- **Authors**：solipsirai
- **Year**：2026（repo 创建时间 2026-03-08）
- **Title**：Crypto Correlation Bot
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL**：<https://github.com/solipsirai/crypto-correlation-bot/blob/main/README.md>
- **Repo URL**：<https://github.com/solipsirai/crypto-correlation-bot>
- **关键源码**：
  - <https://raw.githubusercontent.com/solipsirai/crypto-correlation-bot/main/config.py>
  - <https://raw.githubusercontent.com/solipsirai/crypto-correlation-bot/main/correlation_engine.py>
  - <https://raw.githubusercontent.com/solipsirai/crypto-correlation-bot/main/main.py>

repo 的核心流程是：
1. 先用 BTC/ETH 回归把市场共振剥离（partial correlation）。
2. 对 pair 做相关性筛选，再看短窗收益差（lead-lag spread）。
3. 做一个 lagger catch-up 方向提示。

## 2) 先回答一句：base alpha 是什么？

> **base alpha = 残差化后的相对价值短线均值回复（pairs/stat-arb）**：
> “同一对里 leader 先动、lagger 滞后”时，下注 lagger 的短窗补涨/补跌。

所以这不是纯 filter/overlay，而是可直接交易表达的 **raw alpha**。

## 3) 这轮最关键发现：repo 默认阈值在我们 desk 口径下过严

repo 默认 `CORRELATION_THRESHOLD=0.85`，且对 `3m/5m` 还会再加 `LOW_TIMEFRAME_PENALTY=0.05`（相当于 `0.90`）。

我按 Binance USDⓈ-M 16 币池（去除 BTC/ETH 作为基准）做 first probe，结果：

- `15m`：总 pair `91` 个，`|partial corr| >= 0.85` 的 **0 个**，最大仅 `0.5778`
- `5m`：总 pair `91` 个，`|partial corr| >= 0.90` 的 **0 个**，最大仅 `0.5674`

对应文件：
- `reports/artifacts/quant_digests/solipsirai_partialcorr_20260422/strict_threshold_check.csv`

**结论（人话）**：
repo 的“残差相关性阈值”直接搬到 liquid majors，会把信号池几乎筛空。这个仓真正有用的，不是固定阈值，而是它的 **残差化框架 + lead-lag 交易壳**。

## 4) 可复现实验口径（最小版）

### 数据源（公开）
- Binance USDⓈ-M klines（无需 key）：<https://fapi.binance.com/fapi/v1/klines>
- 频率：`15m` 与 `5m`
- 样本：各 `1500` bars
- Universe：`BTC ETH BNB SOL XRP DOGE ADA AVAX LINK LTC TRX BCH SUI AAVE NEAR UNI`

### 策略表达（first probe）
1. 对所有币收益率做 BTC/ETH 残差化，计算 pair partial correlation。
2. 不再用固定 `0.85/0.90`，改为 **按 |partial corr| 排名前 12 对**（排除 BTC/ETH 相关 pair）。
3. 每个 bar 计算最近 3 根收益差 `|ra-rb|`；若超过阈值 `d`（0.75/1.0/1.5/2.0%），触发事件。
4. `ra > rb` 时做 `b`（lagger）跟随 `a` 的方向，反之同理。
5. hold `1/3/6` 根后平仓，统计每事件 bps（此轮先看 **gross**，未扣手续费）。

对应文件：
- `reports/artifacts/quant_digests/solipsirai_partialcorr_20260422/top12_pairs.csv`
- `reports/artifacts/quant_digests/solipsirai_partialcorr_20260422/event_probe_summary.csv`

## 5) first probe 结果（挑最有信息量的 3 组）

1. **稳样本基线（15m）**：`d=0.75`, hold=3
   - 事件数 `529`
   - 平均 `+4.88 bps`（gross）
   - 胜率 `51.4%`

2. **更快口袋（5m）**：`d=1.0`, hold=3
   - 事件数 `10`
   - 平均 `+31.20 bps`（gross）
   - 胜率 `90%`
   - 但样本极小，不能当稳态结论

3. **阈值过高导致信号归零**（最关键工程结论）
   - `15m` 下 `|partial corr|>=0.85`：`0/91`
   - `5m` 下 `|partial corr|>=0.90`：`0/91`

补充：top pair 基本集中在 `ADA/SUI`, `DOGE/ADA`, `ADA/AVAX`, `AVAX/SUI` 这类中高 beta alt 组合，符合“同风格链上币残差共振”直觉。

## 6) 这条线如何落成完整策略（entry/exit/sizing/risk/cost）

- **Entry**：
  - 每 `15m`（或 `5m`）滚动更新 top-N `|partial corr|` pair（N 可先 8~15）
  - divergence 触发：`|ra-rb| > d`
  - 方向：做 lagger 跟随 leader
- **Exit**：
  - 固定 hold（先 1/3/6 bars 网格）
  - 或“spread 回落到阈值内”提前平
- **Sizing**：
  - pair notional 先 dollar-neutral
  - 再按残差波动做 inverse-vol 缩放
- **Risk**：
  - 单 pair 最大并发限制
  - 同币多 pair 曝险上限
  - shock veto（BTC 大波动窗口减仓/禁入）
- **Cost**：
  - 当前 first probe 未扣费，后续必须带 `maker/taker` 分层成本；
  - 若用纯 taker，`15m` 基线 edge 很可能被吞噬，需 maker-first child execution。

## 7) 下一步怎么测（明确动作）

1. **先修 admission**：把 `fixed threshold` 改成 `rank-based + min floor`（例如 top12 且 `|corr|>0.35`）。
2. **补成本后再筛参数**：对 `d × hold × fee` 做网格，至少跑 `3/6/10 bps` 三档。
3. **加“同币曝险约束”回测**：避免一个 lagger 在同一时刻被多个 pair 重复下注。
4. **做滚动稳定性**：按周滚动重估 top-N pair，检验 pair 漂移和收益衰减。
5. **落地 15m parent + 5m child**：15m 负责 admission，5m 做挂单执行和滑点控制。

## 8) 结论一句话

**这份仓对 desk 真正有价值的，不是 `0.85/0.90` 这种硬阈值，而是“BTC/ETH 残差化 + pair catch-up”这套可交易 raw alpha 壳；先把 admission 由 fixed-threshold 改为 rank-based，才有机会在 `5m/15m` 真正跑出可持续样本。**
