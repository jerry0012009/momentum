# 别把这份 2026 OFI 仓只读成“高频回测作业”：对 short-cycle crypto desk，更该先拆的是「1s order-flow imbalance 极值 × 3~5s microburst continuation」这条 raw alpha

- 时间：2026-04-25 15:15 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `Order_Flow_Imbalance.ipynb`）+ Binance USDⓈ-M public-data sanity probe（`BTCUSDT` aggTrades，最近约 `19m`）
- 主题类型：raw alpha
- 基础 alpha：**当极短时间内主动买/卖盘明显失衡（OFI 极值）时，下一小段 `1~5s` 价格更容易朝同方向继续挪一小步；交易上对应 `OFI z-score` 极值触发的 very-short-horizon continuation。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（repo 给了完整骨架；但更偏 `1s` HFT，不应直接硬搬成 `5m/15m` 主信号）
- 主题标签：raw-alpha/microstructure/order-flow-imbalance/ofi/j-threshold/forward-return/microburst/continuation/btc/1s/3s/5s/1m/repo/public-data/cost/risk
- 证据类型：repo source audit + public aggTrades sanity probe

## 1) 先回答：这篇东西的 base alpha 是什么？
这轮不是在讲“延迟 / 滑点 / 风控很重要”这种常识，也不是把 OFI 当纯执行细节。

**base alpha 就一句话：**
> 如果最近 1 秒里主动买盘或卖盘突然明显压过对手盘，价格在随后几秒里往往还会沿同方向再漂一点；因此可以做一个极短持有的顺势 microburst。

所以它是 **raw alpha**，而不是单纯 overlay。

---

## 2) 这次看了什么
主来源是 GitHub 仓 `grantreed1/Crypto-Order-Flow-Imbalance`：
- README 把策略骨架写得很直白：
  1. 先把多交易所原始成交量统一单位；
  2. 对 OFI 做 winsorize（1%/99% 截尾）+ rolling z-score；
  3. 用 chronological split（`40% train / 60% test`）做线性回归，学一个 `OFI -> forward return` 的 beta；
  4. 只在预测值超过动态 `J-threshold`（作者口径：约保留 top `5%` 机会）时出手。  
- notebook 还能确认一些更细口径：
  - 样本覆盖 **6 个交易所**：`OKX / GATE_IO / COINBASE / DERIBIT / BITSTAMP / BINANCE`；
  - 原始时间戳是亚秒级成交；
  - 作者用的是 **2025-05** 的 BTC 交易数据，且 notebook 明写只先载入 **1/6 subsample** 做实验。  

这份仓最值钱的不是“OFI 有预测力”这句话本身，而是它把 **极短 alpha + admission 阈值 + 风险现实约束** 连成了完整壳。

---

## 3) 一句话结论 + 一句话它怎么证明
- **一句话核心结论：** OFI 极值的确更像一条可复现的 microstructure raw alpha，但真正决定能不能赚钱的不是方向准不准，而是你能否把持有窗、阈值、仓位和延迟/滑点一起控制住。  
- **一句话证明方式：** repo 用 train/test 分割后的线性回归和动态 `J-threshold` 验证“高 OFI 极值对应更高 forward return”，同时又在 README 里直接给出高回撤、容量上限和 adverse selection 的反证。  

---

## 4) 关键源码里最值得 desk 学的地方
1. **不要直接拿原始 signed flow 当信号。**  
   作者先做单位归一化、再做极值截尾、再做 rolling z-score。翻成人话：先把不同 venue 的“成交量语言”统一，再把离谱大单噪音削平，再看“这一秒到底有多异常”。

2. **不要每次都出手，要只打最肥的尾部。**  
   `J-threshold` 的意思不是“预测为正就买”，而是“只有强到进了最靠前那批机会才动手”。这对 short-cycle desk 很重要，因为弱 OFI 常常全被手续费和排队吃掉。

3. **方向正确不等于策略成立。**  
   repo README 明写：OKX 最优参数一度给出 `Net P&L $575,712`，但同时 `Max Drawdown -$1.2M`；更糟的是，没有正式 stop / inventory discipline 时，甚至会出现约 `-$62.3M` 的灾难级回撤。  
   这正说明：**raw alpha 有，不代表直接可上线。**

---

## 5) 我的最小 public sanity probe（不是完整复现，只看信号有没有“活”）
### 5.1 数据源与口径
- 数据源：Binance USDⓈ-M `fapi/v1/aggTrades`（公开接口，无需私钥）
- 标的：`BTCUSDT`
- 窗口：最近约 `5000` 笔 aggTrades，覆盖 `2026-04-25 14:53:08 ~ 15:11:52 UTC`
- 做法：
  - 以 1 秒聚合主动买/卖量，构造 signed flow；
  - 对 1 秒 OFI 做 `1%/99%` 截尾 + `60s rolling z-score`；
  - 看 `OFI z-score` 最强 `5%` 与最弱 `5%` 样本，之后 `1s / 3s / 5s` 的方向延续。  

### 5.2 结果（关键数据点）
- 总计约 `992` 个秒级 bar，可用样本 `927` 个。  
- **正向极值（top 5%）**：`47` 次；后续 `3s` 平均约 **`+0.167 bps`**，命中率约 **`51.1%`**。  
- **反向极值（bottom 5%`，按做空方向记）**：`47` 次；后续 `3s` 平均约 **`+0.145 bps`**。  
- `1s` 窗里仍有信号，但更噪；`3s` 比 `1s` 更像 repo 这类 OFI 信号该落脚的持有窗。  

### 5.3 这组快检说明什么
它还远远不够证明“可交易”，但至少说明两件事：
1. **信号本体没死。** 极值 OFI 后，下一小段的方向漂移仍能测到。  
2. **边极薄。** 几个 `0.1 bps` 级别的 markout，几乎注定不能用 taker 思路硬吃；它更像 maker skew / quote bias / veto admission 的原材料。  

### 5.4 产物文件
- `reports/artifacts/quant_digests/20260425_1512_binance_btc_ofi_quickprobe_summary.json`
- `reports/artifacts/quant_digests/20260425_1512_binance_btc_ofi_quickprobe_horizons.json`
- `reports/artifacts/quant_digests/20260425_1512_binance_btc_ofi_quickprobe_series.csv`

---

## 6) 为什么和当前 desk 有关
这条线和我们默认 `5m/15m` 不在同一层级，但仍然值得进研究池，因为它能服务两类东西：

### A. 作为独立 raw alpha（更偏 `1s / 3s / 1m`）
如果后面能拿到更稳定的盘口/成交数据，它本身就是一条极短 continuation alpha。

### B. 作为短周期执行 admission / veto
即使不单独做 HFT，它也很适合给已有 `1m/3m/5m` 信号加一层：
- breakout 时，若 OFI 不支持，就降级或不追；
- mean reversion 时，若 OFI 仍强顺势，就延后接刀；
- maker quote 时，按 OFI 偏向一侧 skew 报价。  

也就是说，这条线不是和主线竞争，而是可能成为 **shared microstructure spine**。

---

## 7) 策略拆解（必填）
- 方向属性：**顺势 / microstructure continuation**
- 基础 alpha：**秒级主动买卖失衡会在随后几秒继续推着价格往同方向漂移。**
- regime：**高流动、低延迟、盘口没被大单瞬间抽空的时段更适合。**
- filter / veto：**只做 `OFI z-score` 尾部事件；弱信号不做；最好叠加 spread / top-of-book depth / queue-risk 过滤。**
- risk / sizing / execution overlay：**严格 time-box（例如 `3s/5s`）、容量上限、inventory 上限、maker-first 或至少 maker-leaning；否则 edge 会被 slippage 和 adverse selection 吃光。**

---

## 8) 下一步怎么测（必须）
1. **先把 1 秒信号映射到 1 分钟，不要急着升 5 分钟。**  
   做 `1m` bar 内的 `max |OFI_z|`、`sum signed flow`、`尾部事件计数`，测它们对下一 `1m/3m` 收益的解释力。

2. **把它接到现有 raw alpha 上做 veto / admission，而不是先裸跑。**  
   最值得先测的组合是：
   - `1m breakout` + OFI 同向确认；
   - `1m/3m mean reversion` + OFI 反向衰减确认。  

3. **一定要做 friction ladder。**  
   这类信号至少要给 `0 / 0.5 / 1 / 2 bps` 四档 execution friction；若 `1 bps` 就全灭，就别把它误判成主 alpha。

4. **补多 venue，而不是只看 Binance 单点。**  
   repo 真正的亮点是碎片化流动性下的统一 OFI；下一轮如果要认真做，应优先比 `单 venue OFI` vs `跨 venue 聚合 OFI` 哪个更稳。

---

## 9) 风险与保留意见
- 这轮 public probe 只是一段很短的 recent snapshot，绝不是正式回测；
- aggTrades 近似的是成交方向，不是完整 L2 OFI，和真正 order-book imbalance 仍有差距；
- repo 的亮点之一是跨 6 venue 聚合，而我这轮快检只拿了 Binance 单 venue；
- 这条 edge 天生很薄，任何 taker 费率、排队失败或网络延迟都可能直接把它打成负。  

---

## 10) 来源
1. **Grant Reed. (2026). _Crypto-Order-Flow-Imbalance_. GitHub repository.**  
   Venue: GitHub; DOI: N/A  
   Readable URL: <https://github.com/grantreed1/Crypto-Order-Flow-Imbalance>  
   Repo URL: <https://github.com/grantreed1/Crypto-Order-Flow-Imbalance>
2. **Grant Reed. (2026). _README.md_ / _Order_Flow_Imbalance.ipynb_.**  
   Raw README: <https://raw.githubusercontent.com/grantreed1/Crypto-Order-Flow-Imbalance/main/README.md>  
   Raw notebook: <https://raw.githubusercontent.com/grantreed1/Crypto-Order-Flow-Imbalance/main/Order_Flow_Imbalance.ipynb>
3. **Binance Developers. (2026). _USDⓈ-M Futures API – Compressed/Aggregate Trades List_.**  
   URL: <https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Compressed-Aggregate-Trades-List>
