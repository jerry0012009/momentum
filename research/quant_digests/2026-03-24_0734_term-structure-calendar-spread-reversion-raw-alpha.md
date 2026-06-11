# 别把 perp 期限结构只当看板：这份 2026 新仓库更该先测的是「front-vs-back 年化基差回归」完整 raw alpha
- 时间：2026-03-24 07:34 UTC
- 类型：2026 GitHub 新仓库 + 近 5 年定价论文 + Binance 公共数据最小快检
- 主题类型：raw alpha
- 基础 alpha：BTC 近月与次季合约的年化基差差值（term spread）在极端偏离后向中枢回归，可用 calendar spread 收敛交易捕捉
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/relative-value/stat-arb/carry/basis/term-structure/calendar-spread/perpetual/futures/crypto/1m/3m/5m/15m/repo/paper
- 证据类型：仓库工程证据 + 论文定价地基 + 公共数据快检

## 1. 这次看了什么
先回答 base alpha：**这篇的 base alpha 不是 filter，而是“期限结构极端偏离后的收敛交易”本体**。

这次主看 2026 新仓库 `abailey81/Crypto-Statistical-Arbitrage` 的 Phase 3（BTC futures curve），重点不是“它宣称的高收益”，而是它给出的可执行骨架：
- 用 `front/back annualized basis` 定义 term spread；
- 用 regime + 阈值触发 `long/short calendar spread`；
- 用 `max_hold / min_dte / 成本` 完成闭环。

并补了两篇定价地基文献（He et al.; Ackerer et al.）说明：perp/futures 的 fair-value 与 funding 机制可以转成可交易的相对价值偏离，而不只是解释变量。

## 2. 核心结论
- **一句话核心结论：** 这条线值得 intake 的不是“futures curve 概念”，而是可独立复现的 `term_spread reversion` raw alpha（可直接做完整策略）。
- **一句话它怎么证明：** 仓库给了明确参数化策略与风险模块；我再用 Binance 公共数据做 30 天 15m 快检，验证“极端 term spread 偏离后有较强短时回归倾向”（事件级，不等于已过成本的实盘收益）。

关键数据点（本轮）：
1. 仓库 README 的 Phase 3（作者口径）给出：`Sharpe 5.81`、`Total Return 203.70%`、`Trades 44,652`（walk-forward OOS，需独立复核）。
2. 仓库默认策略参数（代码常量）是完整的：
   - calendar 入场阈值：`long_entry_basis_pct=15%`、`short_entry_basis_pct=-10%`
   - 出场阈值：`long_exit=5%`、`short_exit=-5%`
   - 约束：`min_days_to_expiry=7`、`max_holding_days=90`
   - cross-venue 口径：`entry z>2.0`、`exit z<0.5`
3. Binance 公开数据快检（2026-02-24~2026-03-24，15m）：
   - 非重叠极端事件（`|z(term_spread)|>=2`）共 `116` 次；
   - 其中 `94.0%` 在 2 小时内回到 `|z|<=0.5`；
   - 截至快照时，BTC 近月年化基差约 `9.15%`、次季约 `2.30%`，term spread 约 `-6.85pp`（明显非平坦曲线）。

## 3. 为什么和当前 desk 直接相关
- 这是 `relative-value / stat-arb / carry` 家族的 **raw alpha**，直接补充当前素材池，不是再做一个“解释层 overlay”。
- 它天然可拆完整组件：
  - entry：term spread 极值（阈值或 zscore）
  - exit：回归到中枢 / 时间止盈止损
  - sizing：vol-target + fractional Kelly
  - risk：DTE、危机窗口、曲线断裂
  - cost：手续费、滑点、资金费率显式计入
- 对 `1m/3m/5m/15m` 的关系：
  - alpha 本体建议在 `15m` 形成（抗噪）
  - `1m/3m/5m` 负责执行分批、滑点治理与 fail-fast。

## 3.5 策略拆解（必填）
- 方向属性：relative value / calendar spread mean reversion（双边）
- 基础 alpha：`term_spread_t = ann_basis_back_t - ann_basis_front_t` 的极值回归
- regime：contango/backwardation 变化与危机窗口（Luna/FTX 类）会改变阈值与持仓上限
- filter / veto：
  - `near DTE < 7` 不开新仓
  - 结算前后流动性塌陷窗口降仓或禁开
  - 跨 venue 成本不覆盖时 veto
- risk / sizing / execution overlay：
  - `max_holding_days` + `|z|` 超阈值止损
  - size 按信号强度与流动性缩放（可半 Kelly）
  - 用 1m/3m 切片下单控制冲击成本。

## 4. 最小可复现实验（公开数据）
### 4.1 数据源、公开性、更新频率
- Binance USDⓈ-M Futures（公开 REST）
  - `continuousKlines`（PERPETUAL / CURRENT_QUARTER / NEXT_QUARTER）
  - `premiumIndex`（mark/index/funding）
- 公开性：无需私钥可读
- 频率：支持 `1m/3m/5m/15m`

### 4.2 最小实验口径（先 15m，再压到 5m）
- 标的：`BTCUSDT`（perp + current quarter + next quarter）
- 信号：
  - `ann_basis = ((F/S)-1) * 365 / DTE`
  - `term_spread = ann_basis_next - ann_basis_current`
  - `z = zscore(term_spread, rolling=2d)`
- 交易规则（示例）：
  - entry：`|z|>=2`
  - direction：`-sign(z)`（做回归）
  - exit：`|z|<=0.5` 或 `max_hold=8 bars(15m)`
- 成本：`6/10/14 bps` round-trip 分层 + 滑点压力（高波动窗口翻倍）
- 先看指标：`post-cost expectancy`、`事件回归成功率`、`持仓时长分布`、`容量约束后净边`。

## 5. 下一步怎么测（必须）
1. **先做 non-overlap 事件回放 + 成本净值化**：把“回归成功率”转换为可交易 PnL。  
2. **做合约滚动稳健性**：跨季度交割切换时，检验信号是否因合约切换失真。  
3. **15m→5m 执行下钻**：同一信号下比较 TWAP 切片 vs 一次性吃单的成本差。  
4. **危机窗口单独评估**：在高波动/高清算日单独统计，决定是否启用 crisis 参数。  
5. **实盘准入门槛**：要求 OOS `post-cost Sharpe > 0.8`、`MDD < 12%`、`容量约束后仍为正`。

## 6. 风险与保留意见
- 仓库很新（2026-03 创建），README 收益指标偏乐观，必须独立复核，不能直接当可实盘结论。  
- 事件回归率不等于可赚到钱；真正约束是执行成本、资金占用与滚动时点。  
- DTE 变短时年化基差会放大，若不做 DTE 约束容易产生“假极值”信号。  
- 单品种单市场先验容易过拟合，后续需扩展 ETH/SOL 与 cross-venue 验证。

## 7. 来源
1. **A. Bailey (GitHub handle: abailey81) (2026). _Crypto-Statistical-Arbitrage_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/abailey81/Crypto-Statistical-Arbitrage  
   - Repo URL: https://github.com/abailey81/Crypto-Statistical-Arbitrage
2. **He, S., Manela, A., Ross, O., & von Wachter, V. (2024, v6). _Fundamentals of Perpetual Futures_. arXiv / Working Paper.**  
   - Venue: arXiv (q-fin.PR)  
   - DOI: https://doi.org/10.48550/arXiv.2212.06888  
   - Readable URL: https://arxiv.org/abs/2212.06888  
   - Repo URL: N/A
3. **Ackerer, D., Hugonnier, J., & Jermann, U. (2025). _Perpetual Futures Pricing_. Mathematical Finance.**  
   - Venue: Mathematical Finance  
   - DOI: https://doi.org/10.1111/mafi.70018  
   - Readable URL: https://onlinelibrary.wiley.com/doi/10.1111/mafi.70018  
   - Repo URL: N/A
4. **Binance Developers (2026). _USDⓈ-M Futures Market Data API_.**  
   - Venue: Official API Docs  
   - DOI: N/A  
   - Readable URL: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Continuous-Contract-Kline-Candlestick-Data  
   - Repo URL: N/A

## 8. 本地复现产物
- `reports/artifacts/quant_digests/term_structure_calendar_20260324_0730/metrics.json`
- `reports/artifacts/quant_digests/term_structure_calendar_20260324_0730/term_spread_15m_30d.csv`
