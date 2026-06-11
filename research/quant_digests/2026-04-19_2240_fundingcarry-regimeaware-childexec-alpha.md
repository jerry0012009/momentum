# 别把这份 funding-rate-arb 仓只读成“又一个慢速收租回测”：对 short-cycle crypto desk，更该先拆的是「8h positive funding carry × 15m child execution」这条 raw alpha 壳
- 时间：2026-04-19 22:40 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/backtest.py` + `src/basis_trade.py` + `results/backtest_default_metrics.csv` + `results/basis_vs_funding_summary.csv`）+ Binance USDⓈ-M recent funding-history portability probe（`BTC/ETH`）
- 主题类型：raw alpha
- 基础 alpha：**当 perp funding 显著为正时做 `long spot / short perp` 收 carry，直到 funding 回落到退出阈值；`15m/5m` 只负责更省成本地执行双腿，不负责发明 alpha 本体**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/relative-value/stat-arb/delta-neutral/binance/8h/15m/5m/child-execution/repo/public-data/cost/risk/regime
- 证据类型：仓库源码规则 + 仓库结果表 + Binance 公共 funding 最小探针

## 1. 这次看了什么
先回答 base alpha：**这条线的 base alpha 很清楚，就是 delta-neutral funding carry，本体是 raw alpha，不是 filter。**

主材料是 GitHub 仓库 **`zwmjj/funding-rate-arb`**。它不是“预测涨跌”的方向策略，而是一个很干净的 carry 壳：
- `src/backtest.py`：规则写得非常直白——**funding > entry_bps` 入场，`funding < exit_bps` 出场**；
- PnL 拆成三块：**funding income + basis drift + 双腿交易成本**；
- `src/basis_trade.py`：还顺手把 **dated futures basis** 拿来做对照，避免把 perp funding 当成唯一 carry 载体。

对我们最有用的，不是“又看到 long spot / short perp”这句话，而是它把问题说得很明确：
> **这条 alpha 的关键不是猜价格，而是先确认 funding 本身够不够厚、够不够持久，能不能覆盖双腿实现成本。**

## 2. 核心结论
- **一句话结论：** 这份 repo 最值得 intake 的，是它把 funding carry 明确写成一条 **可独立复现的完整 raw alpha 策略**；但对 short-cycle desk，`15m/5m` 更应该扮演 **child execution / admission**，而不是把 funding 硬伪装成逐根价格信号。
- **一句话证据：** repo 自带结果表显示 `2020-2026` 的 BTC/ETH carry 在低回撤下仍有年化正收益，但我补的 recent Binance probe 说明 **最近一段时间正 funding 已明显变薄甚至转负**，所以这条线当前更像 **regime-aware raw alpha**，不是无脑常开策略。

最关键的数据点：
1. repo 默认参数 `entry = 1 bp / 8h`、`exit = 0.5 bp / 8h`、`taker = 4 bps / side / leg`；在这套口径下，结果表给出：**BTC 年化约 `9.02%`、ETH 年化约 `11.24%`，最大回撤约 `-0.34% / -1.80%`，胜率约 `87.5% / 91.7%`**。
2. repo 还给了 carry 分布：**BTC 平均 funding 约 `1.13 bps / 8h`，ETH 约 `1.34 bps / 8h`**；对应 funding-implied annual carry 约 **`12.3% / 14.7%`**，明显高于它算出来的 **BTC dated-futures mean annual basis `4.26%`**。这说明在它的样本里，**perp funding carry 比 dated basis 更厚**。
3. 但我用 Binance 公共 recent funding-history 做了轻量快检后，最近约 `87` 个 funding observations 里：**BTC 平均 funding 约 `-0.095 bps / 8h`，ETH 约 `-0.166 bps / 8h`**，而且 **`> 1 bp` 的正 funding 事件一个都没有**。这意味着 repo 的默认入场阈值在当前 recent regime 下几乎不触发。
4. 即便把阈值降到 `0.25 bp`，recent 样本里 BTC/ETH 也更像“正负 funding 混杂、且最近偏负”的状态，而不是旧样本里那种稳定 contango carry。换句话说：**raw alpha 还在，但 admission gate 必须先看 regime。**

## 3. 为什么和当前 desk 直接相关
这条线当前值得保留，不是因为它“慢”，而是因为它回答了一个很实际的问题：

> **如果 alpha 本体不是价格趋势，而是 funding carry，那 `1m/3m/5m/15m` 应该干什么？**

答案是：
- 不负责重新定义 alpha；
- 负责 **在 funding 事件窗内更低成本地建双腿 / 平双腿**；
- 负责做 **spread-cap admission、分批、再平衡、边界撤退**；
- 负责避免把一个 8h 慢变量，做成高频手续费机器。

所以这条线和当前 short-cycle desk 的关系很直接：
**它不是 `15m` 主信号，但非常适合成为 `15m signal monitor + 5m child execution` 的完整 carry sleeve。**

## 3.5 策略拆解（必填）
- 方向属性：relative-value / carry / delta-neutral / market-neutral
- 基础 alpha：当 perp funding 显著为正时，做 `long spot / short perp` 收 funding；当 funding 回落到退出阈值以下时离场
- regime：更适合持续 contango、正 funding 占优、且 funding 不只是单次 spike 的阶段
- filter / veto：
  - funding 没有持续性时不做；
  - 双腿价差 / 冲击成本过高不做；
  - 若 recent funding 均值已接近零或转负，应把该币种降级到观察名单
- risk / sizing / execution overlay：
  - repo 口径下以双腿 taker 成本显式计费；
  - 可加 `max hold periods`，避免长期占用资金；
  - short-cycle 版本应补 `15m spread cap`、`5m child slicing`、再平衡阈值和 inventory 管理

## 4. 本地最小快检（公开可得数据）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源 A：GitHub 公开仓 `zwmjj/funding-rate-arb`
- 数据源 B：Binance USDⓈ-M 公开 `fundingRate` 与 `8h klines`
- 更新频率：funding 以 `8h` 为主时钟；child execution 可映射到 `15m / 5m`
- 本轮最小实验口径：
  - 标的：`BTCUSDT`、`ETHUSDT`
  - recent 样本：近 `87` 个 funding observations
  - 先看：平均 funding、正负 funding 占比、`>0.25 / 0.5 / 1.0 bp` 事件是否还存在、以及对应 next `8h` 价格是否天然反转

### 4.2 这组快检怎么读
- **当前不是 repo 样本里的强 contango 环境。** recent 样本下 BTC/ETH 平均 funding 都已略为负值。
- **默认 `1 bp` 入场阈值当前过高。** recent 样本里 BTC/ETH 的正 funding `>1 bp` 事件都是 `0`。
- **所以现在更该测的是 regime-aware admission，而不是直接照抄默认参数。** 例如：先按 recent `30d/60d` 平均 funding 是否为正开关策略，再决定是否启用 `0.25~0.5 bp` 的 lower threshold。  

## 5. 为什么这次仍算 raw alpha，而不是 overlay
因为这里回答的是：
> **到底建立什么仓位来直接赚钱？**

答案非常明确：
- 不是用 funding 去解释别的策略；
- 不是拿 funding 做一个抽象情绪指标；
- 而是**直接建 `long spot / short perp` 的 carry 仓位去收 funding**。

这就是标准 raw alpha。只是它的主时钟是 `8h funding boundary`，而不是 `5m` 价格条。`15m/5m` 在这里服务的是 **执行与成本控制**，不是 alpha 本体。  

## 6. 风险与保留意见
1. **这条线极度依赖 regime。** repo 自己就写了 `2021` 很强、`2025+` 明显转弱；我补的 recent probe 进一步说明，当前不能默认正 funding 永远够厚。  
2. **repo 的价格腿处理偏简化。** `backtest.py` 假设双腿价格基本对冲，重点放在 funding 与交易费；真实交易里还要补 spot/perp 借贷、库存、再平衡与冲击成本。  
3. **短周期最容易犯的错，是过度交易。** funding 本身是慢变量；如果每个 `5m` 小波动都去重建双腿，edge 很容易被手续费和滑点吃掉。  

## 7. 下一步怎么测
1. **先做 regime gate：** 用 recent `30d / 60d` 平均 funding、正 funding 占比、以及 `>0.25bp` 事件密度决定该币种是否允许开 carry sleeve。  
2. **把 `8h funding state` 前向映射到 `15m` bars：** 只在 carry state 为 `ON` 时允许 child execution，测试 `immediate taker` vs `15m TWAP / 5m slicing` 的实现差。  
3. **补双腿成本 ladder：** maker/taker、spot/perp、单次建仓 vs 分批建仓，先回答“edge 到底够不够覆盖真实 frictions”。  
4. **加 persistence 条件：** 不只看单次 funding print，而是看 `2~3` 个 funding periods 的连续性；如果只有一次 spike，宁可放弃。  
5. **做币种分层：** BTC/ETH 作为低 beta carry 基线，后续再看 SOL 等高 beta 币是否存在更厚、但更不稳定的 pocket。  

## 8. 来源
1. **zwmjj. (2026). _funding-rate-arb_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/zwmjj/funding-rate-arb  
   - Repo URL: https://github.com/zwmjj/funding-rate-arb  
2. **Source audit files**  
   - README: https://github.com/zwmjj/funding-rate-arb/blob/main/README.md  
   - Backtest: https://github.com/zwmjj/funding-rate-arb/blob/main/src/backtest.py  
   - Basis comparison: https://github.com/zwmjj/funding-rate-arb/blob/main/src/basis_trade.py  
   - Default metrics: https://github.com/zwmjj/funding-rate-arb/blob/main/results/backtest_default_metrics.csv  
   - Funding vs basis summary: https://github.com/zwmjj/funding-rate-arb/blob/main/results/basis_vs_funding_summary.csv  
3. **Binance USDⓈ-M public endpoints**  
   - Funding rate history: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Get-Funding-Rate-History  
   - Klines: https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data  

## 9. 本地产物
- Probe summary：`reports/artifacts/quant_digests/2026-04-19_funding_carry_no_reversal_summary.csv`
- Probe events：`reports/artifacts/quant_digests/2026-04-19_funding_carry_no_reversal_events.csv`
