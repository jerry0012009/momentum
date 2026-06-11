# 别把 dual-regime lead-lag 只读成“bear short 一枝独秀”：对 short-cycle crypto desk，更该先回答的是「bull-regime BTC dip-buy alt basket」这条 raw alpha 分支在真实成本下还剩多少

- 时间：2026-04-25 14:50 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `scripts/simulate_6months.py` + `scripts/paper_trade.py` + `src/features/engineering_v2.py` + `src/paper/config.py` + `src/paper/trader.py`）+ Binance USDⓈ-M public-data portability probe（`5m`，`60d/180d`）
- 主题类型：raw alpha
- 基础 alpha：**在 bull regime（`BTC 7d >= 0` 且 `BTC 3d >= 0`）里，若 BTC 在 `5m` 出现阈值级下跌（dip），alts 会在随后 `15~30m` 出现“延迟补涨/反弹”，可做 long alt basket。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 给了完整骨架；但这轮 public-data 现实检验显示该分支当前未过成本线）
- 主题标签：raw-alpha/event-driven/lead-lag/cross-asset/bull-regime/btc-dip/alt-basket/long-only/5m/15m/30m/repo/public-data/cost/risk
- 证据类型：repo source audit + public futures portability probe

## 1) 先回答：这篇东西的 base alpha 是什么？
这轮不是讲“regime filter 本身”，也不是讲执行细节本身。

**base alpha 就一句话：**
> 在偏多市场里，BTC 的短时下挫更像 risk-on 链条里的“短暂抽水”，部分 alt 会滞后反弹；因此在事件触发后做一个 time-boxed 的 long alt basket。

它是 raw alpha（event-driven lead-lag），不是 overlay。

---

## 2) 这次和 2026-03-30 那篇的区别（避免重复）
我在 2026-03-30 已经做过同 repo 的 **bear 分支**（`bear-shock short alt basket`）并给过 first verdict。

这次刻意只拆 **bull 分支**：
- 不再讨论“bear 口袋是否更强”这个老问题；
- 只回答一件事：**bull dip-buy 这条能不能单独站住，且在成本后还能不能活。**

也就是把同一个 dual-regime 框架里的“另一条腿”单独做现实检验。

---

## 3) 主来源（仓库）
- **Author / Repo owner:** mamipour
- **Year:** 2026（repo created at `2026-03-18`）
- **Title:** *lead-lag-trader*
- **Venue:** GitHub
- **DOI:** N/A
- **Readable URL:** <https://github.com/mamipour/lead-lag-trader>
- **Repo URL:** <https://github.com/mamipour/lead-lag-trader>

关键源码：
- README：<https://raw.githubusercontent.com/mamipour/lead-lag-trader/main/README.md>
- 回测脚本：<https://raw.githubusercontent.com/mamipour/lead-lag-trader/main/scripts/simulate_6months.py>
- 纸面交易：<https://raw.githubusercontent.com/mamipour/lead-lag-trader/main/scripts/paper_trade.py>
- 特征工程：<https://raw.githubusercontent.com/mamipour/lead-lag-trader/main/src/features/engineering_v2.py>
- 策略配置：<https://raw.githubusercontent.com/mamipour/lead-lag-trader/main/src/paper/config.py>

repo 对 bull 分支写得很清楚：
- `BTC 5m dip >= 0.5%`
- 且 `BTC 7d >= 0%`
- 且 `BTC 3d >= 0%`
- 触发后 long alt，默认 hold `30m`
- UTC `7~11` 不做

---

## 4) 一句话结论 + 一句话它怎么证明
- **一句话核心结论：** 这条 bull dip-buy 分支在当前 Binance USDⓈ-M public 口径下，`60d` 和 `180d` 都是**成本后负期望**，暂不该作为 short-cycle 主 alpha 入口。  
- **一句话证明方式：** 我按 repo 的事件定义在 `5m` 数据上做 non-overlap event backtest（扣 `8 bps` roundtrip），`60d` 与 `180d` 两个窗口都显示 event-level mean net bps 为负。

---

## 5) 我的最小 portability probe（public-data）

### 5.1 数据源与可复现实验口径
- 数据源：Binance USDⓈ-M Futures REST `fapi/v1/klines`
- 公开性：公开接口，无需私钥
- 更新频率：`5m`
- 资产池：
  - 60d 版：`ETH/SOL/BNB/XRP/ADA/AVAX/LINK/DOGE/APT/NEAR`
  - 180d 版：`ETH/SOL/BNB/XRP/ADA/DOGE`
- 成本：统一粗扣 `8 bps`（roundtrip）
- 事件去重：
  - bull（hold 30m）用 6 根 `5m` 非重叠事件

### 5.2 结果（关键数据点）
#### `60d`（更近样本，10-asset）
- bull 分支事件数：`30`
- event mean net：`-13.05 bps/事件`
- median net：`-17.84 bps`
- hit-rate：`33.3%`
- 最不差单币：`DOGE`，mean net 仍约 `-2.87 bps`

#### `180d`（更长样本，6-asset）
- bull 分支事件数：`46`
- event mean net：`-14.10 bps/事件`
- median net：`-14.81 bps`
- hit-rate：`41.3%`
- 最不差单币：`DOGE`，mean net 约 `-8.30 bps`

（同口径里 bear 分支也在这 180d 样本下为负，但本轮主问题是 bull 分支，所以不把 bear 作为本篇主结论。）

### 5.3 产物文件
- `reports/artifacts/quant_digests/20260425_144239_leadlag_dualregime_bulldip_probe_summary.json`
- `reports/artifacts/quant_digests/20260425_144239_leadlag_dualregime_bull_events.csv`
- `reports/artifacts/quant_digests/20260425_144407_leadlag_dualregime_bulldip_probe180d_summary.json`
- `reports/artifacts/quant_digests/20260425_144407_leadlag_dualregime_bull_events180d.csv`

---

## 6) 对 desk 的实用判断
这条分支不是“没想法”，而是“**想法清楚但当前不够厚**”。

具体说：
1. **可复现性很高**（规则非常干净）；
2. **策略壳完整**（entry/exit/sizing/risk/cost 都有）；
3. 但 **当前 market + cost 组合下，bull 分支没有穿过生存线**。

因此它现在更适合：
- 放进候选池做低优先级跟踪；
- 不适合直接升成主 digest 的“可上线 lane”。

---

## 7) 下一步怎么测（必须）
1. **先做强事件分层，不要全收。**  
   例如只保留 `BTC 5m drop` 在 `0.8%~1.4%` 且前 `60m` realized vol 处于中位以下的事件，重新测 `15m/30m`。

2. **加入 `15m parent -> 5m child` 的执行层。**  
   这轮是“事件发生即等权入场”的粗口径；下一轮要比较 `next-bar taker` vs `2-bar TWAP` vs `pullback-maker-first`，确认是否被进场冲击吃掉。

3. **做单币路由而非全篮子。**  
   当前两组样本里 `DOGE` 都是“最不差”；下一步可测 `DOGE/ADA` 小篮子 + cooldown，再看是否从“负但接近”翻到可交易。

4. **成本梯度必须给全。**  
   至少跑 `4 / 6 / 8 / 10 bps` 四档，把这条分支的“成本断崖”画清楚。

---

## 8) 风险与保留意见
- 该分支事件数本来就不多（`30~46`），统计波动大；
- 当前只是 public proxy，不包含真实撮合优先级与盘口冲击；
- repo 的回测是 Kraken Futures 语境，直接迁移到 Binance 需要重做参数与执行。

---

## 9) 来源
1. Mamipour. (2026). *lead-lag-trader*. GitHub repository.  
   Venue: GitHub; DOI: N/A  
   URL: <https://github.com/mamipour/lead-lag-trader>
2. Binance Developers. (2026). *USDⓈ-M Futures REST API – Kline/Candlestick Data*.  
   Venue: Official API Docs; DOI: N/A  
   URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data>
