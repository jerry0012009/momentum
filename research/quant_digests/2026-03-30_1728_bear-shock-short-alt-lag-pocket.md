# 别把 dual-regime lead-lag 当成对称策略：这份 2026 新仓库更该先测的是「bear-shock short alt basket」raw alpha，bull dip-buy 先降级
- 时间：2026-03-30 17:28 UTC
- 类型：2026 GitHub 新仓库 + `config.py` / `trader.py` / `simulate_6months.py` / `engineering_v2.py` source audit + Binance Spot 公共 `5m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：`BTC 先在 5m 内急跌，而 alt basket 在熊市 regime 下往往会在随后 15m 继续补跌；因此做的是“BTC shock → short lagging alts”的事件型 lead-lag alpha`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/event-driven/lead-lag/btc-shock/alt-basket/bear-short/regime-switch/5m/15m/1m/3m/repo/public-data/cost
- 证据类型：仓库工程证据 + 公共数据快检

> 先回答 base alpha：**这次不是在讲 regime/filter 本身。真正的 base alpha 是“BTC 先跌、alts 在熊市里延迟补跌”的可交易 pocket。** repo 虽然写成 dual-regime（bear short + bull dip-buy），但对我们 desk 更值得 intake 的，其实是其中更硬的一支：`bear-shock short alt basket`。

## 1. 这次看了什么
主看 **mamipour/lead-lag-trader (2026)**。这份 repo 不是在做抽象网络图，而是把 cross-asset lead-lag 直接写成完整交易骨架：`BTC 5m 跌幅阈值 → 7d/3d regime 分类 → bad-hour veto → 15m/30m 固定持有 → 1~2x leverage`。对当前项目最有价值的读法，不是照抄它的“多空对称叙事”，而是先拆清楚：**哪一支是 raw alpha，哪一支只是看起来顺手的对称延伸。**

## 2. 核心结论
- **一句话核心结论：** 这份 2026 repo 最值得先落地的，不是完整保留 dual-regime，而是先把它收缩成 **bear regime 下的 BTC shock → short alt basket** 事件型 raw alpha。  
- **一句话它怎么证明：** repo 给出了明确参数和回测骨架；我再用 Binance Spot 公共 `5m` 数据做 120 天 proxy 快检，结果显示 bear 支路有 pocket，bull dip-buy 反而偏弱。  
- repo 默认规则非常清楚：`BTC 5m drop >= 1%` 触发 bear short，`BTC 7d return <= -5%` 才允许；`BTC 5m drop >= 0.5%` 触发 bull dip-buy，但要满足 `BTC 7d >= 0%` 且 `BTC 3d >= 0%`；UTC `7~11` 点禁做；bear 分支还会跳过 `>2%` 的大跌以避免 crash bounce。  
- 本地快检（Binance Spot 公共 `5m`，最近 `120` 天，`19` 个 alt，按 repo 的 `6 bps` round-trip maker+slippage 假设）显示：  
  1. **bear 分支**共 `13` 个事件，event mean `+40.6 bps`，median `+3.6 bps`，event hit rate `53.8%`；均值最好的一组是 `TIA/SOL/NEAR/APT/OP`，单腿平均约 `+73~84 bps`。  
  2. **bull 分支**共 `30` 个事件，但 event mean 只有 `-4.0 bps`，median `-14.2 bps`，event hit rate `46.7%`；说明“BTC 跌一下就去抄 alt 反弹”至少在这段样本里不够硬。  
  3. bear 事件的平均 BTC 跌幅约 `1.18% / 5m`；也就是说，这不是超极端 crash 才出现的尾部特例，而是中等强度 shock 的可重复 pocket。  

## 3. 为什么和当前项目有关
- 它直接补的是 **raw alpha 素材池**，而不是再给 breakout/retest 加一层解释。  
- 这条线属于 **event-driven cross-asset lead-lag**：BTC 负责触发，alt basket 负责兑现。  
- 它能自然对接当前 desk 的短周期节奏：  
  - 信号定义在 `5m`；  
  - 持有窗可以先用 `15m`；  
  - 真正执行再下钻到 `1m/3m` 做分批进场、滑点控制和撤单管理。  
- 更重要的是，这条线给了一个很有用的研究姿势：**别把 repo headline 当最终策略，先把里面最硬的那一支拿出来做最小实盘化。**

## 3.5 策略拆解（必填）
- 方向属性：event-driven / lead-lag / cross-asset directional alpha  
- 基础 alpha：`BTC 急跌后，熊市 regime 下 alt basket 在后续 15m 继续补跌`  
- regime：优先 `BTC 7d return <= -5%`；bull 分支当前只保留为次级候选，不当主 intake  
- filter / veto：`BTC 5m drop` 必须进入阈值；跳过 UTC `7~11`；bear 分支跳过 `>2%` 极端跌幅；bull 分支还需 `BTC 3d >= 0%`  
- risk / sizing / execution overlay：bear 分支 leverage 随跌幅从 `1x` 线性提到 `2x`；同一事件只做一篮子；执行层先用 `1m/3m` TWAP/分批，避免在 shock bar 尾部一次性吃单  

## 4. 可复刻的最小实验
### 4.1 数据源、公开性、更新频率
- Binance Spot `5m` klines：`BTCUSDT` + repo 篮子中的 `19` 个 alt，公开可得，无需私钥  
- 更新频率：`5m`；若做执行仿真，再补 `1m` klines 或 trade 级别数据  

### 4.2 最小实验口径
- **研究假设：** 当 `BTC 5m drop` 进入 `1.0%~2.0%` 且 `BTC 7d <= -5%` 时，alt basket 后续 `15m` 的继续下跌，足以覆盖 `6 bps` round-trip 成本。  
- **最小规则：**  
  - entry：`BTC 5m drop >= 1.0%` 且 `<= 2.0%`，`BTC 7d <= -5%`，不在 UTC `7~11`  
  - position：short `TIA/SOL/NEAR/APT/OP` 或先做全 basket proxy  
  - hold：`15m` 固定持有  
  - sizing：按 BTC shock 幅度在 `1x~2x` 之间缩放  
  - cost：至少扣 `6/10/14 bps` 三档  
- **先看指标：** `event_mean_bps`、`event_hit_rate`、`basket dispersion`、`top-pocket stability`。

## 5. 下一步怎么测（必须）
1. **从 Spot proxy 切到可交易 perp 口径。** 先做 Binance USDⓈ-M 或 Hyperliquid，同样规则重跑，并把 taker/slippage/funding 一起扣掉。  
2. **把 full basket 改成 routed basket。** 当前 120 天里最像样的是 `TIA/SOL/NEAR/APT/OP`；下一步做 rolling walk-forward，看这些 pocket 是否稳定，避免把偶然赢家写死。  
3. **把 `5m` 触发下钻到 `1m/3m` 执行。** 比较“触发后立刻打” vs “1~2 分钟 TWAP 切入”的真实侵蚀。  
4. **做 shock 强度 × 持有时长网格。** 先测 `0.8/1.0/1.2/1.5%` × `10/15/20m`，看看 pocket 是来自更快进场还是更短持有。  
5. **bull 分支先做诚实降级。** 不是直接删掉，而是只把它当备选；除非加上更强 gate 后能转正，否则不要把它和 bear 分支并列。  

## 6. 风险与保留意见
- repo 回测是仓库作者口径，当前更值得信的是“规则定义清楚”，不是它的 headline 收益数字。  
- 本地快检用的是 **Binance Spot proxy**，离真正的 perp 执行还有一层 basis/funding/盘口冲击差异。  
- bear 分支本质上还是在吃市场 stress；如果执行太慢，最容易变成“short 在补跌末端”。  
- 当前 `13` 个 bear 事件不算大样本，只够做 first verdict，不够直接上实盘。  

## 7. 来源
1. **Mamipour. (2026). _lead-lag-trader_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/mamipour/lead-lag-trader  
   - Repo URL: https://github.com/mamipour/lead-lag-trader  
2. **Scagliarini, T., Pappalardo, G., Biondo, A. E., Pluchino, A., Rapisarda, A., & Stramaglia, S. (2022). _Pairwise and high-order dependencies in the cryptocurrency trading network_. Scientific Reports.**  
   - Venue: Scientific Reports  
   - DOI: https://doi.org/10.1038/s41598-022-21192-6  
   - Readable URL: https://www.nature.com/articles/s41598-022-21192-6  
   - Repo URL: N/A  
3. **Binance Developers. (2026). _Spot API Docs – Kline/Candlestick Data_.**  
   - Venue: Official API Docs  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data  
   - Repo URL: N/A  

## 8. 本地复现产物
- `reports/artifacts/quant_digests/dual_regime_btc_shock_alt_lag_20260330_1720/summary.json`
- `reports/artifacts/quant_digests/dual_regime_btc_shock_alt_lag_20260330_1720/event_summary.csv`
- `reports/artifacts/quant_digests/dual_regime_btc_shock_alt_lag_20260330_1720/asset_level.csv`
