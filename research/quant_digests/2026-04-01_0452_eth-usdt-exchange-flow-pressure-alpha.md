# 别把链上 exchange flow 只当情绪看板：这篇 2025 arXiv 更该先测的是「ETH 进所卖压 × USDT 进所干火药」ETH 短周期 flow-pressure raw alpha

- 时间：2026-04-01 04:52 UTC
- 类型：2025 arXiv 全文 PDF（本地全文抽取）
- 主题类型：raw alpha
- 基础 alpha：当 **ETH 净流入交易所** 明显走强，而 **USDT 净流入交易所** 没有同步走强时，代表“可卖出的 ETH 在进场，但可立即接盘的稳定币干火药没同步进场”，后续 `1h~6h` 的 ETH 更容易走出负收益；对 desk 来说，更适合先测成 **`ETH_inflow_z - USDT_inflow_z` 的 directional raw alpha**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/external-data/onchain/exchange-netflow/eth/usdt/flow-pressure/directional/continuation/ethereum/binance-perpetual/15m/5m/3m/1m/paper/public-labels/cost
- 证据类型：2025 arXiv 全文证据 + 本地表格抽取 + 公开链上标签可近似复现

先把 **base alpha** 说清楚：**这篇东西的 base alpha 不是“链上情绪变好了/变坏了”，而是“交易所 ETH 净流入（卖压供给）对后续 ETH 收益有稳定负预测力”。** 论文 headline 是 `ETH inflow -> ETH future return down`；但对我们 desk，更值得先偷的旁支，是把它改写成 **`ETH 卖压流入` 对 `USDT 干火药流入` 的相对强弱**，做成更适合 `1m/3m/5m/15m` 执行的短周期 directional 策略。

## 1. 这次看了什么
主线材料是：

- **Yeguang Chi, Qionghua (Ruihua) Chu, Wenyan Hao (2025), _Return and Volatility Forecasting Using On-Chain Flows in Cryptocurrency Markets_**
- Venue：arXiv working paper (`econ.EM`)
- DOI：`https://doi.org/10.48550/arXiv.2411.06327`
- Readable URL：`https://arxiv.org/abs/2411.06327`
- PDF URL：`https://arxiv.org/pdf/2411.06327`
- Repo URL：无

论文研究的是 **BTC / ETH / USDT 的交易所净流入**，看它们能不能预测后续 BTC、ETH 的收益和波动。样本期是 `2017-12-16 ~ 2023-01-20`，频率直接就是我们关心的 **intraday `1h / 2h / 3h / 4h / 6h`**。

对我们最值钱的，不是“链上数据也有信息”这句空话，而是两条可直接拼成交易骨架的方向：
- **ETH 净流入交易所 -> 后续 ETH 收益持续偏负**（这条是主 raw alpha）
- **USDT 净流入交易所 -> 后续 BTC / ETH 在 `1h~2h` 偏正**（这条更像 confirm / veto / 对照腿）

所以与其把论文照搬成单变量回归，不如直接做一个 desk 版本的 **flow-pressure spread**：
`pressure_spread = z(ETH_exchange_net_inflow) - λ * z(USDT_exchange_net_inflow)`
当它很高时，含义是 **卖盘弹药进场 > 接盘干火药进场**，先测做空 ETH perp。

## 2. 核心结论
- **最硬的主结论是 ETH 净流入对 ETH 收益的负预测力。** 论文 Table 2 Panel B 显示，在双变量模型下，ETH 净流入对 ETH 后续收益在 `1h / 2h / 3h / 4h / 6h` 全部为负且显著，系数分别约为：`-0.017`、`-0.0083`、`-0.010`、`-0.014`、`-0.027`。
- **论文给的量纲解释很激进，但方向非常清楚。** 作者写法是：`US$1m` 的 ETH 净流入预测下一小时 ETH 收益约 `-1.70%`；这个经济量级未必能直接照抄进实盘，但“ETH 进所 = 后续偏空”这件事在各 intraday 窗口上是稳定的。
- **USDT 净流入是天然对照腿。** 在 ETH 回归里，USDT 净流入对后续 ETH 收益在 `1h` 和 `2h` 为正且显著；作者给的量级解释是 `US$100m` USDT 净流入对应下一小时 ETH 收益约 `+0.11%`。
- **对 desk 最该偷的不是单独看 ETH inflow，而是看“ETH 卖压流入”有没有被 USDT 买盘流入对冲。** 论文没直接测试这个 spread，但它已经把两条相反方向的流量轴给出来了；这正好允许我们把论文主结论拆成一个更可交易的短周期 raw alpha。
- **波动率结论可以当 sizing 辅助，不该喧宾夺主。** ETH 净流入还负向预测 ETH 后续波动，2 小时双变量模型系数约 `-0.37`；这更像告诉我们“卖压后可能先跌、再趋稳”，适合服务于持有期和止盈设计，而不是替代方向 alpha 本身。

## 3. 为什么和当前项目有关
这篇对当前 intake 值钱，原因很直接：

1. **它补的是 raw alpha 素材池里目前相对少的一类：公开链上流量 -> 短周期方向。** 最近 digest 里 microstructure / pairs / xsec 已经很多，但“可映射到 `1m/3m/5m/15m` 的 on-chain directional alpha”还不算多。
2. **它不是低频宏观故事硬装成 5m。** 论文本身就是 `1h~6h` intraday 口径，离我们现在的执行层只差聚合与触发，而不是差一个时间尺度革命。
3. **它还能给已有 raw alpha 做共享 gating。** 即使最终发现净边不够独立，`ETH inflow` 也很可能可以当成已有 breakout / momentum / continuation 的 veto：卖压很重时别去接多。
4. **它天然适合“signal 慢、execution 快”的 desk 分工。** 信号更新可以 `15m`，执行仍可用 `1m/3m/5m` 分批进出，不需要把自己骗成超高频。

## 3.5 策略拆解（必填）
- 方向属性：单资产 directional / 外部数据驱动
- 基础 alpha：`ETH_exchange_net_inflow` 越强，后续 `1h~6h` ETH 相对越弱；desk 版优先测 `ETH_inflow_z - λ·USDT_inflow_z`
- regime：优先放在 ETH perp 流动性充足、交易所转账活动稳定、不是极端链上拥堵或重大分叉事件的窗口
- filter / veto：若 `USDT` 同时极端净流入，削弱或取消 ETH 空头；若当期 basis / funding 已极端偏空，也降低追空冲动
- risk / sizing / execution overlay：`15m` 更新 flow z-score，`1m/3m` TWAP 入场；持有 `1h/2h/4h` 三档；按近 `24h` realized vol 反比分配；显式计入 taker/maker 成本、funding、极端事件滑点

## 4. 可复刻的最小实验
**研究假设：** 当 ETH 净流入交易所显著高于其自身历史分位，且没有被 USDT 净流入同步抵消时，后续 `4~16` 根 `15m` bar 的 ETHUSDT perp 收益偏负。

**数据源 / 公开性 / 更新频率：**
- **论文原始供应商没有明确披露，严格 paper-level 全复刻存在歧义。**
- 但对 desk 的最小实验，可以用 **公开链上标签 + 公开链上转账数据** 自行聚合：
  - `ETH`：流入已知 CEX 热钱包 / 充值归集地址的 ETH 数量
  - `USDT`：流入同类地址的 ERC-20 USDT 数量
- **公开性：** 地址标签公开、链上转账公开；难点在于标签覆盖度与地址维护，而不是数据本体拿不到
- **更新频率：** 原始数据接近区块级；研究上建议先聚合成 `15m`，再映射到 `1m/3m/5m` 执行层

**最小口径：**
- 标的：`ETHUSDT` perpetual，先只做单资产，不急着扩 cross-asset
- 信号：
  - `z_eth = zscore(15m ETH_exchange_net_inflow, lookback=30d)`
  - `z_usdt = zscore(15m USDT_exchange_net_inflow, lookback=30d)`
  - `pressure_spread = z_eth - 0.5 * z_usdt`
- 入场：每 `15m` bar close，若 `z_eth >= 2` 且 `pressure_spread >= 1.5`，下一根开始分 `1m/3m` 做空
- 出场：固定持有 `1h / 2h / 4h` 三档；或当 `pressure_spread < 0` 提前平仓
- 风控：单次风险预算 `25~40bp NAV`；若 funding 已落到过去 30d 最差 `5%` 分位，减半或 veto
- 成本：先用 taker `4~6bp` round-trip 压测，再测 maker-in / taker-out

**最该先看 4 个数：**
1. top-decile / top-5% / top-1% `pressure_spread` 事件的费后收益；
2. 仅 `ETH inflow` 单变量 vs `ETH-USDT spread` 双变量，谁更稳；
3. 牛市 / 震荡 / 下跌 regime 分层后是否只在单边恐慌里有效；
4. 事件后 path 是“立刻跌完”还是“1~4 bar 漂移”，决定执行该偏 aggressor 还是分批。

## 5. 风险与保留意见
- **论文系数量级可能偏不现实，先信方向、别先信幅度。** 像 `US$1m ETH inflow -> -1.70% next-hour return` 这种经济量级，放到大样本实盘里很可能被地址口径、单位缩放、聚合方式放大了；MVP 应先验证排序 / 分位有效性。
- **标签覆盖是第一大工程风险。** 若只拿到少量公开热钱包，信号会更 noisy；但这不影响先做“极端事件版”验证。
- **链上流量与交易所内部分账未必一一对应。** 有些充提只是内部调仓、归集、托管搬运，不是立即交易意图；所以必须做事件清洗和地址白名单维护。
- **这条线容易和极端 news / liquidation 事件缠在一起。** 若不做事件日历和异常链上活动剔除，回测很容易把“新闻冲击”误认成“净流入 alpha”。

## 6. 来源
- **Chi, Y., Chu, Q. (R.), & Hao, W. (2025). _Return and Volatility Forecasting Using On-Chain Flows in Cryptocurrency Markets_. arXiv working paper.**
  - Venue：arXiv (`econ.EM`)
  - DOI：`https://doi.org/10.48550/arXiv.2411.06327`
  - Readable URL：`https://arxiv.org/abs/2411.06327`
  - PDF URL：`https://arxiv.org/pdf/2411.06327`
  - Repo URL：无
- **Binance Developers. USDⓈ-M Futures Kline / funding / mark price APIs.**
  - Readable URL：`https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data`
- **公开链上标签 + 转账明细（用于 desk 版最小复现）**
  - 数据源定义：公开可见的 ETH / USDT 转入已标注交易所地址的链上转账
  - 公开性：公开可得，但标签维护需要工程整理
  - 更新频率：区块级，可聚合到 `15m`

## 7. 下一步怎么测（必须）
1. **先别复刻全文回归，先做事件分位版。** 只测 `z_eth` 和 `pressure_spread` 的 top `10% / 5% / 1%` 事件，看看 ETH perp 在后续 `1h/2h/4h` 是否稳定偏负。
2. **把 `ETH inflow` 与 `USDT inflow` 拆开再合并。** 单变量若有效但双变量更稳，说明论文最适合我们的不是 headline，而是 `flow-pressure spread` 这个 desk 分支。
3. **做 path 研究，而不只看终点。** 事件后第 `1/2/4/8/16` 根 `15m` bar 的累计路径，要先搞清楚“立即砸、还是缓慢漂移”，再定执行风格。
4. **最后才做 strategy 化。** 若费后净边成立，再补 funding/basis veto、事件日历剔除、地址白名单维护，把它升级为可直接并入现有 ETH directional book 的组件。