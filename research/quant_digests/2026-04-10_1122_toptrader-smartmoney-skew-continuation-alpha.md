# 公开 top-trader 持仓极值 × 1h continuation
- 时间：2026-04-10 11:22 UTC
- 类型：论文 + 公共数据快检
- 主题类型：raw alpha
- 基础 alpha：**头部交易者（top traders）净多/净空持仓比出现极值时，未来约 1 小时价格更容易沿同方向继续走**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：positioning / futures / smart-money / continuation / external-data / 5m / 15m / BTC / ETH / SOL
- 证据类型：论文证据 + 公共数据快检

## 1. 这次看了什么
主线材料是 **Dirk G. Baur, Lee A. Smales (2022), _Trading behavior in bitcoin futures: Following the “smart money”_, Journal of Futures Markets**。Wiley 正文页当前对抓取不友好，这轮没有假装“全文复刻”，而是老实用 **OpenAlex abstract + DOI metadata** 读核心结论，再把它翻译成我们 desk 真能马上试的版本：**别等 CFTC 周频报告，直接用 Binance 公共 `topLongShortPositionRatio` 做 `5m/15m` 短周期 smart-money proxy**。

## 2. 核心结论
- **一句话核心结论：** 公开 top-trader 持仓极值不是纯情绪噪音，至少在 liquid majors 上，它更像一条可交易的短周期 continuation alpha。
- **一句话证明方式：** 论文摘要口径里，作者发现比特币期货里的“leveraged money”有 market-timing ability；而我用 Binance 公共 `top trader position ratio + perp klines` 做 `5m/15m` portability probe，也看到同方向后续漂移。
- 本轮更值得 desk 拿来试的，不是“聪明钱存在”这句废话，而是 **`top_ratio` 的 rolling z-score 极值本身就能当入场信号**。
- `5m` 明显优于 `15m`：`15m` 还能看到同向性，但 gross edge 更接近成本线；`5m` 更像 first lane。
- 信号有明显 **asset × side 不对称**：`ETH` 两边都能做，`BTC` 更偏 long continuation，`SOL` 更偏 short continuation。
- Binance 公共近窗快检：
  - `ETHUSDT 5m`：`top_log_z > 1.5` 做多后持有 `12` 根（约 `1h`），约 `560` 笔、**+18.63 bps/笔 gross**、胜率约 `58.9%`；`top_log_z < -1.5` 做空约 `524` 笔、**+12.19 bps/笔 gross**、胜率约 `62.4%`。
  - `ETHUSDT 5m` 更极端阈值 `|z|>2.0`：做多约 `218` 笔、**+16.75 bps**；做空约 `155` 笔、**+22.16 bps**、胜率约 `70.3%`。
  - `BTCUSDT 5m`：`z>2.0` 做多约 `292` 笔、**+16.70 bps**；但 `z<-2.0` 做空约 `-2.99 bps`，说明 BTC 更像单边 long-follow。`SOLUSDT 5m` 则相反，`z<-2.0` 做空约 `140` 笔、**+24.16 bps**。

## 3. 为什么和当前项目有关
这不是慢频“情绪指数”。它是 **公开可拿、5 分钟更新、能直接映射到 perp 方向书** 的外部持仓 alpha。对当前 `1m/3m/5m/15m` desk，更像：
- 一条独立 raw alpha（positioning continuation）
- 也可以给已有 trend / breakout / jump-follow 信号做 **confirm / veto**
- 还能顺手产出 **asset admission layer**：不是所有币、所有方向都该开机

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 单资产
- 基础 alpha：top-trader 净多净空比的极值 continuation
- regime：优先 liquid majors；当前快检里 `5m > 15m`
- filter / veto：优先只交易 first verdict 为正的 `asset × side` 组合（如 `BTC-long`、`ETH-long/short`、`SOL-short`）
- risk / sizing / execution overlay：`1h` time-stop；单笔先粗扣 `8 bps` round-trip 做 friction ladder；仓位可按 `|z|` 分层但要封顶

## 4. 可复刻的最小实验
- **研究假设**：若 top traders 的净持仓比突然比过去显著更偏多/偏空，未来 `1h` 价格更容易朝同方向继续漂。
- **可计算定义**：`top_log_z = zscore(log(topLongShortPositionRatio))`，阈值先试 `±1.5 / ±2.0`。
- **最小回测切口**：Binance USDⓈ-M 公共 `BTCUSDT / ETHUSDT / SOLUSDT`，先跑 `5m`；入场后固定持有 `12` 根（`1h`），再看 `15m × 4` 根是否还能活。
- **最该先看**：`gross bps/笔` 与 **扣 `8 bps` 后是否仍为正**；其次看 `asset × side` 是否稳定，而不是强行全币统一开机。

## 5. 风险与保留意见
- 论文原始证据是 **比特币期货 trader-category 行为**，不是 Binance top-trader ratio；这里是有意识做的 **proxy transfer**，不是声称“原文已经证明 5m ETH perp 可交易”。
- 公共 ratio 口径可能有样本选择偏差，且 Binance endpoint 单次窗口有限；本轮快检窗口约为 `15m: 45d`、`5m: 14d`，只能算 first verdict。
- `15m` 上 edge 还在，但比 `5m` 更容易被 taker 成本吃掉；若要上实盘，优先先做 `5m`，再看 maker 化是否能保住边际。
- 这类信号可能在极端 squeeze 期最强，常态期衰减更快，所以别默认全天候常开。

## 6. 来源
1. **Baur, D. G., & Smales, L. A. (2022). _Trading behavior in bitcoin futures: Following the “smart money”_. Journal of Futures Markets.**  
   DOI: `10.1002/fut.22332`  
   Readable URL: `https://doi.org/10.1002/fut.22332`  
   说明：本轮主要使用 OpenAlex abstract + metadata；Wiley 正文抓取受限。
2. **Binance USDⓈ-M Futures public endpoints**  
   - `futures/data/topLongShortPositionRatio`  
   - `futures/data/globalLongShortAccountRatio`  
   - `fapi/v1/klines`
3. **本地 portability artifacts**  
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_toptrader_smartmoney_probe_summary_2026-04-10.csv`  
   - `/root/clawd/jerry/momentum/reports/artifacts/literature/binance_toptrader_smartmoney_probe_detail_2026-04-10.csv`
