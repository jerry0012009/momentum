# 别把这份 retail-flow repo 只读成“行为金融大工程”：对 short-cycle crypto desk，更该先测的是「downside momentum extreme × participation spike → panic-bounce fade」这条 raw alpha

- 时间：2026-04-19 15:26 UTC
- 类型：GitHub repo source audit + Binance USDⓈ-M portability probe
- 主题类型：raw alpha
- 基础 alpha：**短窗里先出现“急跌得很猛、成交明显放大”的 downside panic event，然后反手做下一小段 bounce；不是追跌，而是接被挤出来的那一脚。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（raw alpha 已有，但当前更像 pocket / router，执行与成本还要细化）
- 主题标签：mean-reversion / event-driven / behavioral / retail-flow / downside-panic / volume-spike / bounce / 5m / 15m / repo / cost
- 证据类型：GitHub repo 研究说明 + 本地 public-data portability probe

## 1. 这次看了什么

看的是 **Jason Zhan (2026)** 的 GitHub 仓 **`JingitngZhan/HDM-research`**。repo 的 headline 是“识别零售交易者可预测错误并反向交易”，底层用了 Hyperliquid 交易级数据、账户行为画像、双检验零售账户筛选，再把信号逐版迭代到当前的 **`momentum extreme + volume filter`**。作者给出的主口径很强：六个月回测里约 `79%` 胜率、`1.35%` 最大回撤，并提到两次 look-ahead bias 修正后才留下当前版本。

但对我们 desk，更值钱的不是“完整零售识别工程”本身，而是 repo 已经把 base alpha 说得很直白：**零售更容易在动量极端、而且参与度升高时犯错。**

## 2. 核心结论

- **一句话核心结论：** 这条线在 Binance 公共 `5m/15m` 迁移口径下不是“逢大涨大跌都反手”，而是明显更像 **只接 downside panic、别急着 short upside spike**。
- **一句话证明方式：** 我把 repo 的 `momentum extreme + volume filter` 翻成 Binance USDⓈ-M 公共 K 线代理事件：`|ret_z|>=1.5` 且 `quote_volume_z>0`，再比较“急跌后做 bounce”与“急涨后做 short fade”的未来收益。
- 全样本双边反手是弱的：`15m` 全事件 next `2/4/8` bars 仅约 `-0.84 / -4.45 / -6.81 bps` gross；`5m` 全事件 next `3/6/12` bars 约 `-3.78 / -7.03 / -4.75 bps`，说明**不能把 repo 粗暴翻成对称 fade 策略**。
- 但 downside 子桶明显更像样：当 `15m` 事件满足 **`ret_z<=-2` 且 `volume_z>=1`** 时，做 long bounce，next `2/4` bars 约 **`+5.21 / +5.27 bps` gross**，胜率约 **`60.0% / 58.1%`**。
- 再往“更可交易”的 core pocket 收缩到 **`BTC/ETH/SOL/LTC`**，结果更厚：`15m` downside panic bounce next `2/4` bars 约 **`+8.89 / +10.29 bps gross`**，粗扣 `8bps` 后仍约 **`+0.89 / +2.29 bps net`**；同一口径 `top1-per-ts` 也还有约 **`+9.16 / +8.52 bps gross`**。
- `5m` 更像 child-execution 口袋：同样 core4 + downside only + `z2 & vol_z>=1`，top1 router 在 next `12` bars 约 **`+7.97 bps gross`**，已经接近单腿 `8bps` 成本线，但还不够厚。
- 相反，**upside spike short-fade 明显不行**：`15m` 的 `z2 & vol_z>=1` 子桶 next `2/4/8` bars 约 **`-7.39 / -12.41 / -9.92 bps`**，说明这条线至少当前不该被写成对称 long/short 版本。

## 3. 为什么和当前项目有关

这条线和 desk 的直接关系在于：它补的是**事件驱动均值回复 raw alpha**，而且是可讲清 entry/exit 的那种，不是纯解释型行为金融故事。

换成人话：
- 市场短时间跌得很急，
- 同时成交突然放大，
- 这更像“有人在慌里慌张地追着砍”，
- 下一小段反而更值得测 bounce，而不是继续追空。

它也顺手给了一个很重要的负面结论：**不要把“零售犯错”理解成所有极端都该反手。** 这轮 public-data probe 里，能迁移出来的是 downside panic-bounce，不是 upside spike short。

## 3.5 策略拆解（必填）

- 方向属性：单资产 / 事件驱动 / 逆势均值回复
- 基础 alpha：downside momentum extreme × participation spike → short-horizon panic bounce
- regime：更适合高参与、短时过冲、被动去风险释放后的局部窗口
- filter / veto：`ret_z<=-2`、`volume_z>=1`；当前先 veto upside short-fade 版本
- risk / sizing / execution overlay：优先做 core liquid names；`15m` 母信号 + `5m` child execution；单事件 time-stop，必要时加 EMA/VWAP 回收确认

## 4. 可复刻的最小实验

- **研究假设：** downside panic 比 upside spike 更容易在接下来 `30m~60m` 里均值回复。
- **可计算定义：** 在 `15m` 上定义事件 `ret_z<=-2 & volume_z>=1`；下一根开盘做多，固定持有 `2/4/8` 根；先在 `BTC/ETH/SOL/LTC` 上做，再看是否扩到其余 liquid majors。
- **最小回测切口：** Binance USDⓈ-M，`15m` 近 `60d`；child 层再用 `5m` 看 `12` bars 内分批退出是否优于母信号直接持有。
- **先看两件事：** `net_after_8bps` 是否稳定为正；以及 upside short-fade 被 veto 后，trade count 是否仍够用。

## 5. 风险与保留意见

- repo 原始证据来自 Hyperliquid 交易级账户数据；这轮只是用 Binance 公共 K 线做 portability check，不是严格 reproduction。
- 当前 pocket 明显有**方向非对称**，所以别偷懒做成 symmetric fade。
- `core4` 结果比全市场好，说明容量与标的选择很关键；若硬扩到更杂的山寨币，edge 会被稀释。
- 现在最像样的是 raw alpha 母体，不是最终 production 壳；后续还要补 child execution、止损、timeout、去重与成本梯度。

## 6. 来源

- Jason Zhan. (2026). *HDM-research*. GitHub repository.
- Repo URL: https://github.com/JingitngZhan/HDM-research
- Readable URL: https://github.com/JingitngZhan/HDM-research/blob/main/README.md
- 相关理论背景（repo 内引用）：Shefrin & Statman (1985), Barber & Odean (2000), Imas (2016), Kahneman & Tversky (1979)
- 本地实验产物：
  - `reports/artifacts/quant_digests/2026-04-19_hdm_retail_extreme_fade_events.csv`
  - `reports/artifacts/quant_digests/2026-04-19_hdm_retail_extreme_fade_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_hdm_retail_extreme_fade_downside_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_hdm_retail_extreme_fade_symbol_summary.csv`
