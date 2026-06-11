# 别把 funding 只做单边 cash-and-carry：这份 2026 新仓库更该先测的是「双向 funding z-score × perp 组合中性」完整 raw alpha 壳

- 时间：2026-04-16 12:04 UTC
- 类型：2026 GitHub repo source audit（README + `strategy.py` + `notebook.ipynb`）
- 主题类型：raw alpha
- 基础 alpha：跨币种做 `funding_rate` 相对历史分位偏离的双向回归（`z>阈值` 做空 perp、`z<阈值` 做多 perp），靠 funding 现金流与偏离回归赚钱
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/relative-value/stat-arb/cross-sectional/perp-only/zscore/oi-gate/macro-gate/1m/3m/5m/15m/repo/public-data/cost/risk
- 证据类型：工程证据（源码 + notebook 回测输出）

## 1. 这次看了什么
这次主看 `PietroC21/Crypto-PerpetualFutures`。它不是常见的「long spot + short perp」单腿 carry，而是一个**双向、跨币、perp 组合化**的 funding 异常交易壳：按每个币自己的 funding 历史算 z-score，极端正 funding 做空、极端负 funding 做多，并配 OI / 宏观门控。

## 2. 核心结论
- **一句话核心结论**：这条线是可独立复现、可完整落地的 raw alpha 壳，但当前公开参数下最大问题不是“信号有没有”，而是**成本后几乎被吃光**。
- **一句话证明方式**：直接用 repo 自带 notebook 的净值分解与敏感性输出看 `gross→net` 断层、break-even fee、分阶段表现与参数压力测试。
- notebook 给出 `Gross CAGR 13.0%`，但 `Net CAGR 0.2%`；`Net Sharpe -5.72`，说明 edge 对交易摩擦极敏感。
- 平均换手约 `0.2755/period`，对应 `break-even taker fee ≈ 3.4 bps`，而默认 taker fee 用的是 `4 bps`，净值被费用压穿。
- 分阶段结果显示：2020-2021 某些阶段可赚钱，但 `Post-FTX Cycle (2023-01~2026-02)` 退化明显（CAGR 为负、回撤抬升），说明该壳需要 regime/执行层再分流，不宜裸跑。
- 参数压力测试里，`z_entry` 从 `1.0 -> 2.5` 提升时回撤下降，但 Sharpe 仍长期为负，提示“只调阈值”不是解法，关键在执行与成本治理。

## 3. 为什么和当前项目有关
这条主题对 desk 有直接价值：
1) 它属于我们当前优先级最高的 raw alpha 家族（carry/relative-value/stat-arb）；
2) 它给了完整可拆策略链路（signal→sizing→risk→cost）；
3) 它天然能映射到 `1m/3m/5m/15m`：alpha 决策在 funding 结算时钟（8h），分钟级负责执行切片、冲击控制与持仓管理。

## 3.5 策略拆解（必填）
- 方向属性：relative-value / carry（组合中性）
- 基础 alpha：`funding_zscore_reversion + funding_cashflow - turnover_cost`
- regime：高拥挤高摩擦阶段 edge 变薄；低摩擦、偏离可回归阶段更可做
- filter / veto：
  - OI gate：`open_interest >= ratio * rolling_mean(OI)`
  - macro gate：`VIX/SPY drawdown` 异常时整体降档或停机
  - 可选 OBI confirm：订单簿失衡不对齐时 veto
- risk / sizing / execution overlay：
  - 等权分配到活跃信号（1/N）
  - 15m/5m/3m/1m 做 TWAP/分片，避免一次性冲击
  - 设置持有上限（1~3 个 funding 周期）+ basis/价差异常扩张止损

## 4. 可复刻的最小实验
### 4.1 数据源、公开性、更新频率
- Binance funding（8h）、perp/spot OHLCV（可到 1m）；Bybit OI（1h）；均为公开接口可拿。
- VIX/SPY 在原仓库里是宏观 gate（低频）；对 short-cycle 可先替换为纯 crypto 可得 gate（如 realized vol / spread / depth）。

### 4.2 最小实验口径（先 15m，再下钻 5m/3m/1m）
- 标的：先 BTC/ETH/SOL 三币 perp，后扩到前 10 流动性币。
- 信号：每 8h 刷新 `funding_z`；`z > 1.5` 做空，`z < -1.5` 做多。
- 持有：1 个 funding 周期起步，做 1/2/3 周期网格。
- 成本：至少做 `4/6/8 bps` 三档 round-trip 压测。
- 首看指标：
  1) `post-cost pnl bps/trade`
  2) `capacity-adjusted turnover`（防“高换手假 edge”）

## 5. 下一步怎么测（必须）
1. **把 8h 信号、15m 执行解耦**：同一信号下比较一次性吃单 vs 15m TWAP 分片。  
2. **做 funding 极端分层**：`|z| 1.5~2.0 / 2.0~2.5 / 2.5+`，看哪档成本后仍存活。  
3. **加“最小持有 + 迟滞”**：减少来回翻仓，先压 turnover 再看净值恢复。  
4. **把宏观 gate 换成纯 crypto gate**：避免 VIX/SPY 数据依赖导致实盘链路变长。  
5. **做跨币容量约束**：限制单币权重与相关暴露，防止“看似中性、实则挤在同一风险因子”。

## 6. 风险与保留意见
- 当前策略对 taker 成本极敏感，若无法降到 break-even 以下，信号优势很容易被吞噬。  
- perp-only 组合并非天然完全 delta-neutral，极端单边行情下仍可能出现净方向暴露。  
- OI 与订单簿确认层若数据质量不稳，会引入伪过滤与错杀。  
- 这条线更像“可复刻策略壳 + 执行工程问题”，不是“开箱即用生产 alpha”。

## 7. 来源
1. **PietroC21. (2026). _Crypto-PerpetualFutures_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: `https://github.com/PietroC21/Crypto-PerpetualFutures`  
   - Repo URL: `https://github.com/PietroC21/Crypto-PerpetualFutures`
2. **仓库关键源码**  
   - `strategy.py`: `https://raw.githubusercontent.com/PietroC21/Crypto-PerpetualFutures/main/strategy.py`  
   - `README.md`: `https://raw.githubusercontent.com/PietroC21/Crypto-PerpetualFutures/main/README.md`  
   - `notebook.ipynb`: `https://raw.githubusercontent.com/PietroC21/Crypto-PerpetualFutures/main/notebook.ipynb`
3. **公开数据接口文档（最小复现）**  
   - Binance Funding: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History`  
   - Binance Klines: `https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
