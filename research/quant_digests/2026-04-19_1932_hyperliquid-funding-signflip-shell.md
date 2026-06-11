# 别把这份 Hyperliquid funding-arb repo 只读成“又一个收租机器人”：对 short-cycle desk，更该先拆的是「bidirectional funding sign-flip × 15m child execution」这条 raw alpha 壳
- 时间：2026-04-19 19:32 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `strategy.py` + `funding_monitor.py` + `position_manager.py` + `risk_manager.py` + `backtester.py` + `BACKTEST_README.md`）+ Hyperliquid public funding-history `90d` portability probe（`BTC/ETH/SOL/HYPE`）
- 主题类型：raw alpha
- 基础 alpha：**当 8h funding 显著为正时做 `long spot / short perp` 收 funding；当 8h funding 显著为负时反过来做 `short spot / long perp`；持有到 funding 回落到阈值内或方向翻转**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/relative-value/stat-arb/delta-neutral/hyperliquid/sign-flip/threshold-streak/child-execution/15m/5m/repo/public-data/cost/risk
- 证据类型：仓库源码规则 + 公共 funding-history 最小探针

## 1. 这次看了什么
先回答 base alpha：**这条线的 base alpha 很清楚，就是 delta-neutral funding carry，本体是 raw alpha，不是 filter。**

主材料是仓库 **`stephenpeters/delta_neutral_strategies`**。repo 名字像 generic funding bot，但源码里其实给了一个相当完整、而且很适合我们 desk 拆解的全策略骨架：
- `funding_monitor.py`：以 **绝对 funding 阈值** 生成双向信号；
- `strategy.py`：先看账户健康，再管理老仓、再找新机会；
- `position_manager.py`：有 **delta-neutral rebalance**（默认偏离 `5%` 触发）；
- `risk_manager.py`：有 **liquidation buffer**（默认 `30%`）、**max slippage**（默认 `0.1%`）和按账户规模收缩仓位；
- `backtester.py` / `BACKTEST_README.md`：把这条线明确写成 **8h funding-driven hold / exit** 的 carry 策略，而不是硬装成逐根 K 线方向预测。

对我们更值钱的，不是“再记一遍 funding carry 常识”，而是：
> **这份 repo 把 carry alpha 的 entry / exit / sizing / rebalance / liquidation guard 都拆开了，很适合直接翻译成 `15m signal monitor + 5m child execution` 的实盘骨架。**

## 2. 核心结论
- **一句话结论：** 这次最值得 intake 的，不是 repo 自带的“收益宣传”，而是它给出的 **双向 funding sign-flip 完整策略壳**；但对 short-cycle desk，`15m/5m` 的角色更像 **8h carry 事件窗执行层**，不是逐 bar 主信号。
- **一句话证据：** 我用 Hyperliquid 公共 `fundingHistory` 对 `BTC/ETH/SOL/HYPE` 做了近 `90d` probe，发现 repo 默认 `1 bp` 入场阈值在 majors 上几乎不触发，说明这条线若想服务短周期，必须把重点放在 **threshold design + event-window execution**，而不是幻想它天然是高频母信号。

最关键的数据点：
1. **repo 默认阈值是 `1 bp`（`funding_rate_threshold = 0.0001`）**；但在近 `90d`、每币约 `500` 个 `8h` funding 点里，`BTC/ETH/HYPE` 的 **`|funding| > 1 bp` 触发次数都是 `0`**，只有 `SOL` 还有 **`11` 次（占 `2.2%`）**。  
2. 若把阈值降到 **`0.5 bp`**，触发占比变成：`BTC 0.4%`、`ETH 0.8%`、`SOL 11.2%`、`HYPE 1.0%`。这说明 **默认参数对 majors 过稀疏**，但对某些高 beta 币（这里是 `SOL`）已经开始像“可交易 pocket”。  
3. 若再降到 **`0.25 bp`**，`SOL` 的触发占比升到 **`36.6%`**，平均 streak 长度约 **`7.0` 个 funding periods`（约 `56h`）**；`HYPE` 约 **`6.2%`**、但 streak 更短（平均约 `1.94` 个 `8h`），更像短促 carry burst。  
4. 方向上也不对称：本轮样本里，`BTC/ETH/SOL` 超阈值样本**几乎全是负 funding**，而 `HYPE` 超阈值样本则**几乎全是正 funding**。这意味着这条线不只是“有无信号”，还天然带有 **coin-specific direction bias**。  

## 3. 为什么和当前 desk 直接相关
这轮值得保留，不是因为“funding carry 很老”，而是因为它把 **短周期 desk 迟早都要补的一整层实盘组件** 用很透明的方式摆在了台面上：
- **entry**：绝对 funding 阈值；
- **direction**：正 funding 做 `long spot / short perp`，负 funding 做反向；
- **exit**：funding 跌回阈值内，或直接 sign flip；
- **sizing**：按账户与最大仓位限制；
- **rebalance**：净 delta 偏离过大就调仓；
- **risk**：liquidation buffer、slippage cap、margin utilization；
- **timing**：天生围绕 `8h` funding 时钟，不是假装每根 `5m` bar 都有独立 edge。

换句话说，它更像一个 **carry alpha 的 production shell**。对 `1m/3m/5m/15m` 而言，真正该测的是：
**如何在 funding 事件窗附近降低实现成本，而不是把 funding 本体误写成连续方向因子。**

## 3.5 策略拆解（必填）
- 方向属性：relative-value / carry / market-neutral / delta-neutral
- 基础 alpha：当 perp 的 funding 偏离足够大时，站到“收 funding 的那一边”，并在 funding 回落或翻转时退出
- regime：更适合 funding 偏离能持续若干结算周期、且底层流动性足够厚的时候
- filter / veto：
  - 价差过宽不做（repo 里有 `max_slippage` 思路）；
  - 太靠近 liquidation 不做或减仓；
  - 只有单次 funding spike、没有 streak 延续时，可能只够解释、未必够覆盖成本
- risk / sizing / execution overlay：
  - 默认单仓上限 `max_position_size_usd = 10000`（live config）/ 回测默认 `5000`；
  - 账户使用率以 `80%` 为保守上限；
  - `rebalance_threshold = 5%`；
  - `liquidation_buffer = 30%`；
  - `max_slippage = 0.1%`；
  - 回测默认交易费 `0.02%` / side（双腿开平都会算）。

## 4. 本地最小快检（公开可得数据）
### 4.1 数据源、公开性、更新频率、实验口径
- 数据源 A（主策略来源）：GitHub 公开仓 `stephenpeters/delta_neutral_strategies`
- 数据源 B（代理验证数据）：Hyperliquid 公共 `fundingHistory` API，无需 key
- 更新频率：funding 以 `8h` 为主时钟；本轮 probe 拉取近 `90d`
- 最小实验口径：
  - 标的：`BTC / ETH / SOL / HYPE`
  - 样本：每币约 `500` 个 funding observations
  - 统计：分别看 `|funding| > 0.25 / 0.5 / 1.0 bps` 的触发频率、方向偏置、streak 长度
  - 目的：不是回测收益，而是先回答 **repo 默认阈值在 Hyperliquid 现况下到底够不够用**

### 4.2 这组快检怎么读
- **`1 bp` 默认阈值太高。** 这不是“策略无效”，而是说明它在当前 majors 上更像稀疏事件策略，而不是稳定日内主线。  
- **更值得测的是 `0.25~0.5 bp`。** 特别是 `SOL`，已经出现持续数个 funding periods 的 streak，比较像可以往下翻译成 `15m/5m` 执行规则。  
- **币种之间不能共用同一认知。** `SOL` 明显更像负 funding pocket，`HYPE` 更像正 funding pocket；如果一锅端用单参数，很容易把 edge 稀释掉。  

## 5. 为什么这次不把它降级成 filter / overlay
因为这里回答的是：
> **“到底做什么仓位来赚钱？”**

答案已经很明确：
- 不是用 funding 去 veto 别的 alpha；
- 不是只用 funding 判断市场情绪；
- 而是**直接建立能收 funding 的 delta-neutral 仓位**。

这就是标准 raw alpha，只是它的主时钟是 `8h funding boundary`，不是 `5m` 价格 bar。`5m/15m` 在这里服务的是 **execution、re-entry、de-risk**，而不是 alpha 本体。  

## 6. 风险与保留意见
1. **repo 的 backtester 不能直接当收益证据。** 源码里 `capital` / `positions` 的会计处理比较粗，`_create_result()` 甚至没有把 closed positions 正常累计到结果对象里；所以它更像骨架，不是 audited research result。  
2. **position manager 里“spot 腿”目前其实是 perp 代理。** 代码注释写得很直白：*for now, we'll use perps for both sides since Hyperliquid spot requires more setup*。所以 live 版要么补真实 spot 接入，要么承认自己其实在做 perp-only proxy。  
3. **funding 赚的是慢变量，短周期亏的是实现成本。** 如果没有更细的入场、分批和 spread-cap 设计，`1m/3m/5m` 很容易只是在帮你多付手续费。  

## 7. 下一步怎么测
1. **先把阈值从单一 `1 bp` 下修成 coin-specific grid**：例如 `0.25 / 0.5 / 0.75 / 1.0 bps`，分别对 `BTC/ETH/SOL/HYPE` 做触发频率、持续时长、净 carry 覆盖成本能力评估。  
2. **把 `8h funding state` 前向映射到 `15m` bars**：做 `15m signal monitor`，只在 funding sign-streak 还活着时允许 child execution。  
3. **加 `5m` 执行 admission**：只在 `spread / depth / premium` 没有恶化时开双腿，避免把慢变量 alpha 做成滑点机器。  
4. **分开测正 funding pocket 与负 funding pocket**：不要默认它们镜像对称；本轮 `SOL` 和 `HYPE` 已经提示这件事。  
5. **补真实 spot/perp 或 perp/perp proxy 对照**：先决定这是“真正单 venue cash-and-carry”，还是“资金费率驱动的 perp 代理策略”，别把执行层定义混掉。  

## 8. 来源
1. **Stephen Peters. (2025). _delta_neutral_strategies_. GitHub repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: https://github.com/stephenpeters/delta_neutral_strategies  
   - Repo URL: https://github.com/stephenpeters/delta_neutral_strategies  
   - GitHub metadata：创建于 `2025-10-06`，最近更新 `2026-04-19`
2. **Source audit files**  
   - README: https://github.com/stephenpeters/delta_neutral_strategies/blob/master/README.md  
   - Backtest guide: https://github.com/stephenpeters/delta_neutral_strategies/blob/master/BACKTEST_README.md  
   - Strategy: https://github.com/stephenpeters/delta_neutral_strategies/blob/master/strategy.py  
   - Funding monitor: https://github.com/stephenpeters/delta_neutral_strategies/blob/master/funding_monitor.py  
   - Position manager: https://github.com/stephenpeters/delta_neutral_strategies/blob/master/position_manager.py  
   - Risk manager: https://github.com/stephenpeters/delta_neutral_strategies/blob/master/risk_manager.py  
   - Backtester: https://github.com/stephenpeters/delta_neutral_strategies/blob/master/backtester.py
3. **Hyperliquid public API docs / context**  
   - Readable URL: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/info-endpoint  
   - 本轮实际使用：公开 `fundingHistory` endpoint payload

## 9. 本地产物
- Probe 脚本：`reports/artifacts/quant_digests/2026-04-19_hyperliquid_funding_signflip_probe.py`
- Threshold summary：`reports/artifacts/quant_digests/2026-04-19_hyperliquid_funding_signflip_summary.json`
- Threshold table：`reports/artifacts/quant_digests/2026-04-19_hyperliquid_funding_signflip_thresholds.csv`
