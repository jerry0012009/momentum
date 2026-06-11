# 别把这个实时 pairs dashboard 只读成“看板”：对 short-cycle crypto desk，更该先拆的是「Kalman 动态 hedge ratio × rolling z-score spread fade」这条 raw alpha
- 时间：2026-04-20 12:16 UTC
- 类型：GitHub / repo source audit + Binance USDⓈ-M `15m` portability probe
- 主题类型：raw alpha
- 基础 alpha：两个高度相关的币短时偏离动态 hedge ratio 后，spread 往滚动均值回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/kalman/dynamic-hedge-ratio/zscore/spread-fade/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：GitHub 工程证据 + Binance public-data portability probe

## 1. 这次看了什么
这次主材料是 2025-12 新仓 **`KulkarniPushakar/Real-Time-Crypto-Pair-Trading-Analytics-`**。README 和 `app.py` 的核心不是 Streamlit UI，而是一条很标准、可直接拆成交易规则的 pairs/stat-arb sleeve：Binance WebSocket 对齐双币价格，计算 OLS / Huber / Theil-Sen / **Kalman dynamic hedge ratio**，再用 spread、rolling z-score、rolling correlation、ADF p-value 和 `z_entry / z_exit` 阈值生成 `LONG / SHORT / EXIT` alerts。

一句话核心结论：**这条线最值得拿走的是“不要用一根固定 beta 去做 pairs，先让 hedge ratio 随市场慢慢漂，再只 fade 真正偏离 beta 的 spread”。**

一句话证明方式：**repo 把实时数据、动态 hedge、z-score 阈值和 rule-based alert 串成了可执行骨架；我再用 Binance USDⓈ-M `15m` 公共数据做了一个最小 portability probe，看它是否还有成本后 pocket。**

## 2. 核心结论
- **base alpha 是 raw alpha，不是 filter。** 信号本体是：`spread = price_y - beta_t * price_x`；当 `z(spread) > 2`，做空 rich leg / 做多 cheap leg；当 `z < -2` 反向；`|z| < 0.5` 平仓。
- **Kalman / dynamic beta 的价值是减少“关系变了还硬做回归”的假信号。** 对 crypto pairs 来说，`BTC/ETH`、`XRP/DOGE`、`SOL/AVAX` 这类相关关系会随叙事和波动切换漂移，固定 OLS beta 很容易把 beta 漂移误读成 spread alpha。
- **最小 probe 显示：广谱铺开不够，局部 pair pocket 有交易价值。** 我用 `BTC/ETH/BNB/SOL/XRP/DOGE/ADA/LINK/AVAX/LTC`，`2026-01~03`、`15m`，对 45 个 pair 做 Kalman-style beta + `96-bar` z-score + `corr>0.55` admission：
  - 全部离散交易合计约 `6,928` 笔，说明机会很多，但也意味着成本非常敏感。
  - `XRPUSDT/DOGEUSDT` 最突出：`187` 笔，平均 `+11.04 bps gross/trade`，粗扣 `8 bps` 双腿 round-trip 后仍约 `+3.04 bps/trade`，gross win rate 约 `56.1%`。
  - `BTCUSDT/ETHUSDT` 很稳定但太薄：`325` 笔，平均 `+2.11 bps gross`，扣 `8 bps` 后约 `-5.89 bps/trade`；它更适合当 sanity benchmark，不适合直接上 taker 版。
- **所以这不是“pairs 都能赚钱”，而是一个 pair-admission / execution 问题。** 先找同叙事、高相关、spread 回归快、且 gross edge 能覆盖双腿成本的 pair，再谈上策略。

## 3. 为什么和当前项目有关
这篇对当前素材池有用，因为它补的是 **pairs / stat-arb / relative value** 族里的一个清楚 raw alpha 壳，和最近的 trend / funding digest 不同：

- 对 `15m`：可直接做母信号，尤其适合 `XRP/DOGE`、`SOL/AVAX`、`LINK/LTC` 这种同风格 alt pair。
- 对 `5m`：更适合做 child execution——`15m` 发现 spread extreme，`5m` 等回归第一脚或 maker queue placement。
- 对实盘组件：可以拆成 `pair admission`、`dynamic hedge`、`spread z-score entry`、`exit / timeout / stop-z`、`cost ladder` 五个模块，后续可以独立替换。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / pairs / stat-arb / 均值回归
- 基础 alpha：`Kalman dynamic hedge ratio` 调整后的 pair spread 偏离滚动均值后回归
- regime：只在 `rolling_corr > 0.55`、beta 为正且不过度异常时启用；更严格版本应加 ADF / half-life / liquidity admission
- filter / veto：`|z| < 2` 不开；`corr` 降低、beta 跳变、spread stop-z、单腿跳空、资金费率/新闻事件可 veto
- sizing / risk / execution overlay：双腿 gross exposure 归一化为 `1 + |beta|`；`|z| < 0.5` 平仓；`12 bars` timeout；`|z| > 4` 同向扩张止损；研究期先按 `4/8/12 bps` 双腿 round-trip friction ladder
- cost：当前 probe 粗扣 `8 bps` round-trip；真实执行若走 taker 双腿会很吃亏，优先测 maker-first / one-leg-maker-one-leg-taker

## 4. 可复刻的最小实验
- 数据源：Binance USDⓈ-M public monthly klines，公开可得，分钟级可映射到 `1m/3m/5m/15m`
- 最小实验口径：先用 `15m`，`XRP/DOGE`、`BTC/ETH`、`SOL/AVAX`、`LINK/LTC` 四个代表 pair；样本先滚动 `90d`
- 一个可计算定义：
  - `beta_t = Kalman(price_y ~ beta_t * price_x)`
  - `spread_t = price_y - beta_t * price_x`
  - `z_t = (spread_t - rolling_mean_96) / rolling_std_96`
  - `entry: z>2 => short y/long beta*x; z<-2 => long y/short beta*x`
  - `exit: |z|<0.5 or timeout=12 bars or stop_z=4`
- 最该先看：
  1. `net_bps/trade` under `4/8/12 bps` friction
  2. `mean-cross exit ratio` 与 median holding bars
  3. pair-by-pair stability，而不是 pooled average

## 4.5 下一步怎么测
1. **先做 desk 版 pair admission**：`corr>0.7 + ADF p<0.1 + half-life 2~16 bars + quote_volume top bucket`，看 `XRP/DOGE` 的 `+3.04 bps net/trade` 是否还保得住。  
2. **把 `15m` signal 接 `5m` child execution**：入场不直接 next-open taker，改成 `5m` 第一根 spread 回落 / maker mid-placement，目标是把 `8 bps` 成本打到 `4 bps` 以下。  
3. **做 rolling OOS pair selection**：每周只从过去 `30d` 里选 top 3 pairs，下一周交易，避免事后挑 `XRP/DOGE`。  
4. **补 static OLS vs Kalman A/B**：同一批 pair 比较固定 beta、rolling OLS beta、Kalman beta，确认动态 hedge 是否真的减少坏信号。  
5. **加 funding / borrow / shortability 检查**：pairs alpha 不是无成本相对价值，perp 两腿资金费和保证金占用必须进 PnL。

## 5. 风险与保留意见
- 当前结果只说明 **Kalman dynamic spread fade 有局部 pocket**，不是证明所有 pairs 都可交易；多数 pair 扣 `8 bps` 后为负。
- `XRP/DOGE` 的好结果可能包含阶段性 meme / alt beta 结构，不应直接外推；必须做 rolling OOS selection。
- 这份 repo 是实时 analytics / alert platform，不是完整回测框架；我补的 bracket / timeout / cost 是 desk 版最小策略壳，后续需要 clean replication。

## 6. 来源
- **Author / Year / Title / Venue**：KulkarniPushakar (2025), *Real-Time-Crypto-Pair-Trading-Analytics-*, GitHub repository
- **DOI**：N/A
- **Readable URL**：https://github.com/KulkarniPushakar/Real-Time-Crypto-Pair-Trading-Analytics-
- **Repo URL**：https://github.com/KulkarniPushakar/Real-Time-Crypto-Pair-Trading-Analytics-
- **关键源码 / 文档**：`README.md`, `app.py`, `main.py`
- **GitHub metadata**：created `2025-12-17`, pushed `2025-12-17`, language `Python`
- **本地 probe artifacts**：
  - `reports/artifacts/quant_digests/2026-04-20_kalman_pair_spreadfade_probe_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-20_kalman_pair_spreadfade_probe_trades.csv`
  - `reports/artifacts/quant_digests/2026-04-20_kalman_pair_spreadfade_probe_event_horizon.csv`
