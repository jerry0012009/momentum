# 别把这份 delta-basis repo 只读成“中性套利框架”：对 short-cycle crypto desk，更该先拆的是「spot↔perp basis z-score fade」这条完整 raw alpha 壳
- 时间：2026-04-21 23:59 UTC
- 类型：GitHub / repo source audit + Binance public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：当同一标的的 perpetual 相对 spot 出现异常升贴水时，做 **long cheap leg / short rich leg**，赌 basis spread 向自身短窗中枢回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但当前 short-cycle first verdict 偏弱）
- 主题标签：carry / basis / relative-value / stat-arb / delta-neutral / spot-perp / mean-reversion / Binance / 5m / 15m / repo / public-data
- 证据类型：工程经验 + repo rule shell + public-data first probe

## 1. 这次看了什么
这次看的是 2025 GitHub repo **mariamlulu / delta-basis-trading**。它不是只给一个“套利会回归”的口号，而是把完整策略骨架都摆出来了：`basis_spread -> rolling z-score -> entry/exit -> size -> fees/slippage/funding -> report`。对 desk 更有价值的读法是：**这不是单纯 carry 研究，而是一条可直接落到 `5m/15m` 最小实验的 raw alpha 壳。**

## 2. 一句话核心结论
这条 `spot↔perp basis z-score fade` **方向上完全成立，且 gross 几乎每笔都赚钱**；但在 Binance `BTC/ETH` 的 `5m/15m` portability probe 里，**单笔 gross 只有约 `1.8~2.1 bps`，远不够覆盖 repo 自带那档 realistic 四腿摩擦**，所以当前更像一条 **maker-first / event-conditioned / inventory-aware** 的 relative-value 壳，而不是可直接 taker 化上线的主信号。

## 3. 它是怎么证明这点的
不是靠泛讲“套利无风险”，而是直接把 Binance spot 与 Binance USDⓈ-M perp 的同标的 K 线对齐，按 repo 配置近似复刻：`336h` rolling z-score、`|z|>=2` 入场、`|z|<=0.5` / `|z|>=4` / `336h timeout` 出场，再统计每笔 basis-trade 的 gross bps，并粗扣 `28 / 40 bps` round-trip 四腿成本梯度。

## 4. 核心结论展开
- 这篇东西的 **base alpha 很清楚**：不是方向赌币价涨跌，而是赌 **spot-perp 升贴水偏离会回归**。
- repo 的完整策略壳也很完整：
  - signal：`basis = perp / spot - 1`，再做 rolling z-score
  - entry：`|z| >= 2`
  - exit：`|z| <= 0.5`、`|z| >= 4` 或 time-stop
  - sizing：`50% NAV`、spot `1x` + perp `3x`
  - cost：maker / taker / slippage / funding 都有位置放
- 这轮 Binance 公开数据 quick probe（最近约 `60d`，`BTCUSDT/ETHUSDT`）给出的 first verdict：
  - `15m BTC`：`122` 笔，gross `+2.14 bps/笔`，胜率 `99.2%`
  - `15m ETH`：`94` 笔，gross `+1.78 bps/笔`，胜率 `94.7%`
  - `5m BTC`：`332` 笔，gross `+2.06 bps/笔`，胜率 `99.1%`
  - `5m ETH`：`239` 笔，gross `+1.81 bps/笔`，胜率 `95.0%`
- 问题也非常直接：repo 配置本身就假设了不低的摩擦。若按四腿 round-trip 粗扣：
  - `28 bps`（maker+slippage 风格）后，单笔 net 仍约 `-25.9 ~ -26.2 bps`
  - `40 bps`（更保守 taker 风格）后，单笔 net 约 `-37.9 ~ -38.2 bps`
- 所以这条 alpha 的真实结论不是“没回归”，而是：**回归存在，但常态幅度太薄；若 execution 不是特别强，这笔 edge 会全被摩擦吃掉。**

## 5. 为什么和当前项目有关
它补的是我们 raw alpha 素材池里一条很重要、但还没被彻底拆干净的支线：**同一 underlier 的现货-永续 financing dislocation**。这和前面的 perp-calendar / funding-sign-flip 不同，它更接近 desk 能直接落地的“单交易所、双腿、分钟级”最小原型，适合继续拆成：
- maker-first child execution
- funding / premium jump 条件下的 event router
- inventory 对冲层的 deploy / unwind timing

## 6. 策略拆解
- 方向属性：relative-value / stat-arb / carry-adjacent mean reversion
- 基础 alpha：spot-perp basis 偏离后的回归
- signal：`basis_pct = perp_close / spot_close - 1`，再做 `336h` rolling z-score
- entry：`z >= +2` → long spot / short perp；`z <= -2` → short spot / long perp
- exit：`|z| <= 0.5`、`|z| >= 4`、或 `336h` timeout
- sizing：双腿等名义；perp 允许杠杆，但真实 desk 更该按流动性、库存与 borrow/funding 约束来缩放
- 主要风险：funding 突变、perp mark / index 脱钩、现货腿成交与借贷限制、四腿摩擦、极端行情下 basis 继续扩张

## 7. 可复刻的最小实验
### 数据源
- Binance Spot 公开 K 线：`/api/v3/klines`
- Binance USDⓈ-M Perp 公开 K 线：`/fapi/v1/klines`
- 公开性：公开可得，无需私有权限
- 更新频率：分钟级；这轮实验用 `5m / 15m`

### 最小实验口径
1. 拉 `BTCUSDT/ETHUSDT` spot 与 perp 最近 `45~60d` K 线；
2. 对齐时间戳，算 `basis_pct`；
3. 用 repo 的 `336h / 2.0 / 0.5 / 4.0 / 336h timeout` 先跑 baseline；
4. 统计 `gross bps/trade`、`win rate`、`avg hold`；
5. 再加 `28/40 bps` friction ladder；
6. 若常态 net 仍明显为负，再测试 maker-only、funding jump、premium dislocation、结算前后等 event-conditioned 版本。

## 8. 这轮我保留的判断
这条线 **绝对算 raw alpha，而且是完整策略壳**。但当前更像：

> **有稳定 gross 回归、却没有足够厚度覆盖常态摩擦的 spot-perp relative-value shell。**

也就是说，值得留，不该高估。它最适合进入后续 **execution-aware / event-aware / inventory-aware** 复现分支，而不是直接当成 `5m/15m` standalone 主 alpha。

## 9. 下一步怎么测
- 把 `BTC/ETH` 扩到更容易出现资金费率/库存错配的币，别只盯最有效率的 majors。
- 补 `fundingRate / premiumIndex / mark price`，测试 **basis widening + funding shock** 联合 admission，而不是全天候机械做回归。
- 做 **maker-first fill model**：只有当预期回归幅度 `> fee+slippage+inventory_penalty` 才下单。
- 把它和我们已有的 funding / calendar / pairs 素材池串起来，测试它更适合当：
  - standalone alpha
  - carry entry-timing layer
  - delta-neutral inventory unwind router

## 10. 来源
- GitHub user `mariamlulu` (2025), **Delta Basis Trading System**. Repo URL: <https://github.com/mariamlulu/delta-basis-trading>
- Readable README URL: <https://raw.githubusercontent.com/mariamlulu/delta-basis-trading/main/README.md>
- Source audit 文件：`README.md`, `src/config.yaml`, `src/signals/threshold_strategy.py`, `src/backtest/backtest_engine.py`
- 本地 artifacts：
  - `reports/artifacts/quant_digests/delta_basis_spreadfade_summary_2026-04-21.csv`
  - `reports/artifacts/quant_digests/delta_basis_spreadfade_trades_2026-04-21.csv`
