# 别把这份 order-book imbalance 仓库只读成“高频转低频”概念：对 short-cycle desk，更该先测的是「5m 下跌 + 买压失衡 → 1h 反弹」这条完整 raw alpha

- 时间：2026-04-04 17:48 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `006_Orderbook Imbalance Pattern based Cryptocurrencies Screening Trading Strategy.py`）+ repo 内附参考研报 + Binance Spot 公共 `5m` 最小快检
- 主题类型：raw alpha
- 基础 alpha：**短周期下跌 bar 出现“买压失衡（absorption）”后，后续 `30~60m` 出现均值回归反弹。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/mean-reversion/microstructure/order-book-imbalance/pressure-ratio/absorption/downbar-reversal/single-asset/cross-asset/binance-spot/5m/15m/1m/3m/repo/public-data/cost/risk
- 证据类型：repo 规则证据 + 公共 API proxy 快检

## 1) 先回答一句：base alpha 是什么？

**base alpha = 下跌过程中若订单簿买压（或其可观测 proxy）异常偏强，卖压可能被吸收，价格在后续 `6~12` 根 `5m` 出现反弹。**

这不是 filter/overlay；这是可直接交易的 **mean-reversion raw alpha**。

---

## 2) 为什么这轮选它（且不算重复）

最近 digest 池里虽然已有很多 OBI/flow 主题，但多数是：
- directional continuation（顺势）
- maker alpha
- 或信号 admission（高置信阈值）

这次选题是另一条独立线：**“下跌 + 买压失衡”的反转型 alpha**，并且可以写成完整策略（entry/exit/sizing/risk/cost），可直接补 raw alpha 素材池。

---

## 3) 这份 repo 真正可迁移的部分

来源仓库：
- `davelamtrader/Strategy-Backtest-Orderbook-Imbalance-Pattern-based-Cryptocurrencies-Screening-Trading-Strategy`（2025）

代码核心思路（可读到的骨架）：
1. 从高频订单簿/成交聚合出买卖压力；
2. 计算 `pressure_ratio = log(P_buy) - log(P_sell)`；
3. 当 `pressure_ratio` 超过滚动阈值（如 `mean + 1.96*std`）且价格下跌时触发；
4. 用固定持有期（原脚本示例 `exit_after=10`）管理退出；
5. 显式加入交易费、止损。

> 对我们 desk 的关键迁移：
> - 不是照搬其日频实现，而是把同一逻辑压缩到 `5m/15m`；
> - 用公开可得的 taker-flow proxy 先做最小实验，再决定是否上 L2 深度历史做正式版。

---

## 4) 最小可复现实验（public data）

### 4.1 数据源与公开性
- 数据源：Binance Spot Kline API（公开、免 key）
  - `https://api.binance.com/api/v3/klines`
- 字段：`quote_volume`, `taker_buy_quote_volume`（可做买压 proxy）
- 更新频率：按 bar 更新（本实验使用 `5m`）

### 4.2 实验口径（本地已跑）
- 标的：`BTC, ETH, SOL, BNB, XRP, DOGE, ADA, LINK`
- 样本：每币约 `6000` 根 `5m` bar（约 21 天）
- 入场条件（proxy 版）：
  - 当前 `5m` 收益 `ret1 <= -0.2%`
  - `buy_share_z >= 1.0`
    - 其中 `buy_share = taker_buy_quote / quote_volume`
    - `buy_share_z` 基于滚动 `48` 根（约 4 小时）
- 出场：固定 `h=3/6/12` 根 `5m`（即 `15m/30m/60m`）

### 4.3 关键结果（pooled）
来自：
`reports/artifacts/quant_digests/orderbook_pressure_buyshare_proxy_20260404/pooled_horizon_summary.csv`

- `h=12`（60m）：`n=101`, 平均收益 `+16.82 bps`, 胜率 `52.48%`
- `h=6`（30m）：`n=101`, 平均收益 `+7.65 bps`, 胜率 `53.47%`
- 与仅看“下跌不加买压”相比（`h=12`）：
  - down-only 平均收益 `+1.74 bps`
  - 加上 buy-pressure 条件后 `+16.82 bps`

成本敏感性（round-trip）：
- 若按 `8 bps`，`h=12` 仍约 `+8.82 bps`（proxy 层面可过线）
- `h=6` 接近盈亏平衡（`-0.35 bps`）
- `h=3` 仍不够（`-6.01 bps`）

> 解释：这条线更像 **“慢半拍吸收反弹”**，不适合极短持有；更偏 `30~60m` 的反转兑现。

---

## 5) 如何落成完整策略（entry/exit/sizing/risk/cost）

### Entry
在 `5m` 触发：
1. 价格冲击：`ret1 <= -x`（建议从 `0.2%~0.4%` 网格）
2. 买压失衡：`buy_share_z >= z*`（建议 `0.8~1.5` 网格）
3. 流动性门槛：`quote_volume` 不低于滚动分位（避免冷门噪声）

### Exit
- 主方案：固定时间退出（`6` 或 `12` 根 `5m`）
- 辅助方案：若反向压力出现（`buy_share_z` 回落 + 价格冲高回落）可提前减仓

### Sizing
- 基础仓位 `w0`
- 按信号强度放大：`w = w0 * clip((buy_share_z - z*)/k, 0, w_max)`
- 单币和总组合双上限

### Risk
- 连续亏损 `N` 次触发 cooldown
- 极端波动（单根异常长上下影）禁入
- 新闻/事件窗口（大数据发布或交易所异常）禁入

### Cost
- 明确 maker/taker 两套成本壳（不要只看单一低费假设）
- 至少做 `4/8/12 bps` 三档净值敏感性

---

## 6) 与 `1m/3m/5m/15m` 的关系

- **`5m`**：主信号层（当前最稳妥）
- **`15m`**：可做执行与风控聚合层（减少噪声）
- **`1m/3m`**：适合做“触发确认层”（例如入场后 `1m` 微结构不再恶化才开单）

这条线本体不依赖低频外部宏观变量，天然贴近 short-cycle desk。

---

## 7) 下一步怎么测（直接可排）

1. **L2 正式版替换 proxy**：
   - 用真实 depth snapshot 重算 pressure ratio（替代 `buy_share_z`）
   - 对比 proxy 与真实 L2 的信号一致性

2. **参数稳定性**：
   - 网格：`ret_th × z_th × hold_bars`
   - 用 walk-forward 看参数漂移，而不是单窗最优

3. **执行版本对照**：
   - taker-only vs maker-entry/taker-exit
   - 检查净收益是否仍成立

4. **横截面分组**：
   - 按流动性分层（BTC/ETH vs 次主流）
   - 验证是否存在“只在 mid-liquidity 有效”的资产池

---

## 8) 本轮结论（短版）

这份 repo 最值得 desk 拿走的，不是“高频转低频”的叙事，而是一条可复现的短周期 raw alpha：

**`5m` 下跌冲击后，若买压 proxy 明显抬升，`30~60m` 反弹概率/幅度同步改善。**

在本地 public-data 最小实验里，`h=12` 已出现成本后可讨论的正期望信号，值得进入下一轮 L2 正式复现。

---

## 9) 来源（论文/仓库/文档）

1. **davelamtrader (2025). _Strategy-Backtest-Orderbook-Imbalance-Pattern-based-Cryptocurrencies-Screening-Trading-Strategy_. GitHub Repository.**
   - Venue: GitHub
   - DOI: N/A
   - Readable URL: `https://github.com/davelamtrader/Strategy-Backtest-Orderbook-Imbalance-Pattern-based-Cryptocurrencies-Screening-Trading-Strategy`
   - Repo URL: `https://github.com/davelamtrader/Strategy-Backtest-Orderbook-Imbalance-Pattern-based-Cryptocurrencies-Screening-Trading-Strategy`

2. **Repo source file used in this digest**
   - `006_Orderbook Imbalance Pattern based Cryptocurrencies Screening Trading Strategy.py`  
   - Raw URL: `https://raw.githubusercontent.com/davelamtrader/Strategy-Backtest-Orderbook-Imbalance-Pattern-based-Cryptocurrencies-Screening-Trading-Strategy/main/006_Orderbook%20Imbalance%20Pattern%20based%20Cryptocurrencies%20Screening%20Trading%20Strategy.py`

3. **Tardis.dev API / channels (for order book & trades replay, as referenced by repo)**
   - Venue: Official docs
   - DOI: N/A
   - Readable URL: `https://docs.tardis.dev/`

4. **Binance Spot API Docs (public kline data used in minimum experiment)**
   - Venue: Official API docs
   - DOI: N/A
   - Readable URL: `https://developers.binance.com/docs/binance-spot-api-docs/rest-api/market-data-endpoints#klinecandlestick-data`

5. **参考研报（repo 内附 PDF）**
   - 天风证券（2017）《利用高频数据拓展盘口数据：买卖压力失衡》
   - Venue: 券商研究报告
   - DOI: N/A
   - Readable URL（repo file）: `https://github.com/davelamtrader/Strategy-Backtest-Orderbook-Imbalance-Pattern-based-Cryptocurrencies-Screening-Trading-Strategy/blob/main/20170801-%E5%A4%A9%E9%A3%8E%E8%AF%81%E5%88%B8-%E5%88%A9%E7%94%A8%E9%AB%98%E9%A2%91%E6%95%B0%E6%8D%AE%E6%8B%93%E5%B1%95%E7%9B%98%E5%8F%A3%E6%95%B0%E6%8D%AE%EF%BC%9A%E4%B9%B0%E5%8D%96%E5%8E%8B%E5%8A%9B%E5%A4%B1%E8%A1%A1.pdf`

---

### 附：本轮实验产物
- `reports/artifacts/quant_digests/orderbook_pressure_buyshare_proxy_20260404/per_symbol_summary.csv`
- `reports/artifacts/quant_digests/orderbook_pressure_buyshare_proxy_20260404/pooled_horizon_summary.csv`
- `reports/artifacts/quant_digests/orderbook_pressure_buyshare_proxy_20260404/avg_ret12_pivot.csv`
- `reports/artifacts/quant_digests/orderbook_pressure_buyshare_proxy_20260404/meta.json`
