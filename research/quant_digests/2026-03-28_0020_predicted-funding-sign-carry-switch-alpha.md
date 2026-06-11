# 别把 funding carry 只做成 always-on 收租：这份 2025 GitHub 新仓库更该先测的是「预测 funding sign → carry on/off / reverse」完整 raw alpha
- 时间：2026-03-28 00:20 UTC
- 类型：2025 GitHub 新仓库 + report.md + 源码审阅
- 主题类型：raw alpha
- 基础 alpha：spot-perp 对冲仓位本身赚的是 funding / basis cashflow；若能提前识别下一段 funding sign，就能把 carry 从“永远收租”改成“该收时开、该停时停、极端时反手”
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/carry/funding/basis/spot-perp/sign-prediction/hyperliquid/eth/hourly/5m/15m/repo/external-data/cost
- 证据类型：仓库源码 + report.md + 子报告证据

## 1. 这次看了什么
这次看的是 **Pudovikov Andrey & Bolotin Danila (2025)** 的 GitHub 仓库 **_crypto_strategy_**，核心材料包括主报告 **_The modification of the basis-trading between spot and perpetuals_**、ETH funding sign 预测子报告，以及 `ml_basis_strategy.py / mb_hl_strategy.py` 的实现骨架。

对 desk 最有用的，不是“又一个 funding 看板”，而是它把一条 **可直接落成完整策略的 carry / basis raw alpha** 讲清楚了：

> **base alpha 很明确：当下一段 funding 更可能为正时，做 long spot + short perp 收 funding；当下一段 funding 更可能为负时，不是傻扛，而是 flat 或在收益覆盖成本时反向做 short spot + long perp。**

所以这不是单纯 filter，也不是 overlay；预测模型只是 timing 层，真正赚钱的 alpha 本体依然是 **funding / basis carry**。

## 2. 核心结论
- **一句话核心结论：** 这份仓库真正值得 desk 先测的，不是“LSTM 能不能预测 funding”，而是 **“predicted funding sign 驱动 carry on/off / reverse”** 这条完整 raw alpha 骨架。
- **一句话它怎么证明：** 作者用 **ETH 小时级 funding 数据 + spot/perp 价格序列**，先证明 funding sign 有一定可预测性，再把这个 sign 预测接到 basis strategy 的持仓切换规则上。
- **sign 可预测性并不弱：** 子报告里，ETH funding sign 预测的 **LSTM F1** 在 **1h / 3h / 8h / 24h** 窗口分别约为 **0.8397 / 0.8099 / 0.7645 / 0.7494**；Prophet 对应约 **0.8004 / 0.7748 / 0.7278 / 0.6885**。
- **样本本身有 carry 偏置：** 2025-01-01 到 2025-05-13 的 ETH funding 统计里，**正 funding 占 71.21%**，**负 funding 占 28.79%**。这意味着“永远 long spot + short perp”确实有直觉基础，但负 funding 也并不稀少到可以忽略。
- **完整策略结果给了一个可用但要打折的上界：** 主报告声称网格搜索最优点的 **APY 约 16.4%**、**最大回撤约 -1.17%**，但同时伴随 **最小杠杆 11x、最大杠杆 41x+、目标杠杆 3x** 这类非常激进的设定，不适合直接照搬进 desk。
- **更值得偷的是骨架而不是最终绩效：** 源码里真正可复用的，是 `predict-negative -> exit` / `predict-positive -> re-enter` 这套状态机，以及把费用门槛明确写进切换规则的思路。
- **要保持诚实：** 仓库材料存在轻微口径不一致——funding 分析主样本写的是 **2025-01-01 ~ 2025-05-13**，但主报告实验段又写到 **2023-01-01 ~ 2025-05-05**。所以这条线更像 **高价值研究骨架**，还不是可直接相信的已审计业绩。

## 3. 为什么和当前项目有关
这条线值得进池，原因很直接：

- 它属于当前明确优先补的 **raw alpha 家族**，而且是和 breakout / reversal / pairs 平行的一条 **carry / funding / basis** 主线；
- 它不是“拿 funding 当 gate 去修补别的 alpha”，而是 funding 本身就是利润来源；
- 它天然带着完整策略元素：`entry / exit / sizing / risk / cost` 全都能写清楚；
- 对当前 desk 很友好：虽然信号刷新是 **1h**，但执行完全可以落在 **5m / 15m**，用更细粒度做开平与风控；
- 它还能补当前素材池里的一个空白：**我们已经积累了不少 momentum / reversal / lead-lag / pairs，但“什么时候该开 carry、什么时候该停 carry”这条完整 timing 线还不够扎实。**

更重要的是，这篇东西很适合 desk 的现实约束：
- 若不能稳定做 short spot，就先测试 **predict-negative 时 flat**；
- 若 borrow / transfer / gas 不友好，就先做 **同 venue 或低搬砖依赖** 的 carry timing 版本；
- 若 `1h` forecast 已经能大幅减少负 funding 暴露，那它就是一条很实用的原始 alpha，而不只是学术花活。

## 3.5 策略拆解（必填）
- 方向属性：market-neutral carry / relative value
- 基础 alpha：收取有利 funding，并规避或反向吃不利 funding
- entry：在每次 funding 预测刷新后，若 `predicted_sign > 0` 且预期净 funding 覆盖 fees，则开 `long spot + short perp`；若 `predicted_sign < 0` 且绝对值足够大、可覆盖 round-trip + borrow / carry 成本，则允许 `short spot + long perp`
- exit：预测 sign 翻转、预期 funding 收益跌破成本门槛、持有达到 `1 / 3 / 8` 个 funding interval、或 basis 偏离/杠杆超限时平仓
- sizing：第一轮先固定 notional；第二轮再做 `inverse-basis-vol` 或 `signal-confidence` sizing；desk 默认先把杠杆压到 **1x~3x**，不要照搬 repo 的 11x+ 下界
- risk：净 delta 约束、basis 失控止损、单 venue / 单资产上限、单日 funding sign 连续误判熔断
- cost：spot/perp 手续费、spread、借币成本、资金费率、可能的 transfer / gas；若做反向 carry，还要额外核算 short spot 可得性
- 更适合的 regime：funding 偏置持续、市场拥挤明显、perp 溢价/折价状态相对稳定的阶段
- 主要 veto：新币、薄流动性、借币困难、basis 已严重拉爆、重大宏观/清算事件前后

## 4. 可复刻的最小实验
**研究假设：** 在 public funding 数据上，`predicted funding sign` 至少能把“always-on carry”改造成一条更诚实的短周期可执行 raw alpha：负 funding 小时少扛、正 funding 小时多待、必要时才反手。

**最小实验建议：**
1. **Universe：** 先做 ETH、BTC；第三个加 SOL。只做高流动、可稳定拿 funding 与价格数据的标的。
2. **数据源：**
   - funding：Hyperliquid 公共 funding 数据，**公开可得**，原仓库口径为 **1h 更新**；
   - 价格：Binance 或 Hyperliquid 的现货/永续 OHLCV，**公开可得**；
   - desk 执行层：把小时级 sign forecast 映射到 **5m / 15m** 开平仓。
3. **最小特征：** 先只复刻仓库里最轻的那套：`lag 1/2/3/6/12/24`、`rolling mean 3/8/24`、`rolling std 8/24`。不要上来就堆链上或情绪数据。
4. **先跑三层基线，不要一步到位：**
   - A：`always-on long spot + short perp`
   - B：`predict-negative -> flat`
   - C：`predict-negative and expected edge > cost floor -> reverse carry`
5. **模型顺序：**
   - baseline 0：sign persistence（下一小时等于这一小时）
   - baseline 1：logistic / tree model
   - baseline 2：LSTM 24h sequence
   先证明“simple model 能不能打过 persistence”，再考虑深度模型。
6. **执行口径：** 每个整点生成下一 funding interval 的 sign 预测；在下一根 **5m** bar 或 **15m** bar 执行；持有到下次预测刷新，或在中途达到 risk trigger 退出。
7. **成本口径：** 至少拆成四层：
   - 只看 funding cashflow
   - funding + 手续费
   - funding + 手续费 + spread
   - funding + 手续费 + spread + short/borrow/transfer
8. **成功标准：**
   - B 是否显著优于 always-on carry；
   - C 在扣完反手额外成本后是否仍有边；
   - 5m 执行是否优于 15m 执行；
   - 优势是否主要来自“少吃负 funding”，而不是靠高杠杆放大。

## 5. 我对这条线的当前判断
我的判断是：**值得进研究池，而且优先级不低。**

原因不是它已经证明了“16% APY 可以直接抄”，而是它提供了一条非常实用的 desk 化问题：

> **carry 到底该 always-on，还是应该做 sign-timed on/off？**

这是一个能很快拿到 first verdict 的问题，而且结果无论正负都很有价值：
- 如果 `predict-negative -> flat` 已经能显著改善收益回撤比，这条线就值得继续；
- 如果连最简单的 sign timing 都帮不了太多，说明 raw carry 可能已经足够，复杂模型不必继续堆；
- 如果只有“反向 carry”才赚钱，但必须依赖高 borrow / 高杠杆，那就该降级，不要硬推到短周期主池。

也就是说，这条线最像的是 **“完整 raw alpha 的 honest intake”**，不是又一个只会给主策略贴创可贴的 overlay。

## 6. 下一步最该怎么测
如果只给一个最优先动作，我会做这个：

> **先在 ETH 上做 `always-on carry` vs `predict-negative -> flat` 的 A/B，对同一批小时级 funding sign 预测，统一映射到 5m 执行层，并强制加入 4 档成本。**

这一步最便宜，也最能快速回答三个关键问题：
- funding sign timing 到底有没有真价值；
- 价值是来自“少付负 funding”，还是来自“反手赚负 funding”；
- 5m/15m 执行层会不会把小时级 forecast 的边际收益全磨掉。

## 7. 来源与可复用材料
1. **Pudovikov, A., & Bolotin, D. (2025). _crypto_strategy_（GitHub repository）.**  
   Repo URL：<https://github.com/pudovikoff/crypto_strategy>  
   GitHub API metadata：创建于 **2025-05-14**，最后 push 于 **2025-05-19**。
2. **Pudovikov, A., & Bolotin, D. (2025). _The modification of the basis-trading between spot and perpetuals_（repo report）.**  
   Readable URL：<https://github.com/pudovikoff/crypto_strategy/blob/main/report.md>  
   Raw URL：<https://raw.githubusercontent.com/pudovikoff/crypto_strategy/main/report.md>
3. **Pudovikov, A., & Bolotin, D. (2025). _Ethereum Funding Rate Sign Prediction: Comprehensive Report_.**  
   Readable URL：<https://github.com/pudovikoff/crypto_strategy/blob/main/funding_rate_analysis/eth_funding_rate_sign_prediction_report.md>  
   Raw URL：<https://raw.githubusercontent.com/pudovikoff/crypto_strategy/main/funding_rate_analysis/eth_funding_rate_sign_prediction_report.md>
4. **可直接复用的源码骨架：**
   - `managed_basis_strategy/ml_basis_strategy.py`：`predict-positive -> hold / rebalance`，`predict-negative -> exit`
   - `managed_basis_strategy/mb_hl_strategy.py`：把 Hyperliquid funding + price history 组装成可回测 observation
5. **官方文档（数据/费用口径）**
   - Hyperliquid funding docs：<https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding>
   - Hyperliquid fee docs：<https://hyperliquid.gitbook.io/hyperliquid-docs/trading/fees>
   - Hyperliquid onboarding / gas 说明：<https://hyperliquid.gitbook.io/hyperliquid-docs/onboarding/how-to-start-trading>
