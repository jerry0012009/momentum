# 别把这篇 2026 Frontiers pairs 论文只读成 DNN/LSTM 比赛：对 short-cycle desk，更该先拆的是「dynamic cointegration gate × percentile-threshold spread fade」这条 raw alpha——但 first verdict 更像 low-friction pocket，不是现成 production shell

- 时间：2026-04-14 18:44 UTC
- 类型：2026 Frontiers 开放获取论文全文抽取（HTML full text + Table 2/3/4/5）+ Binance Spot `5m/15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**co-integrated crypto spread mean reversion；DNN/LSTM ensemble 只是 spread score / thresholding layer，不是 alpha 本体。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/dynamic-cointegration/percentile-threshold/zscore/dnn/lstm/binance-spot/5m/15m/paper/fulltext/public-data/cost/risk
- 证据类型：open-access paper + public-data first verdict

## 1. 这次看了什么
主来源是 Frontiers 开放获取论文：
- **Authors：** Johannes Tshepiso Tsoku, Katleho Makatjane
- **Year：** 2026
- **Title：** *Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs*
- **Venue：** *Frontiers in Applied Mathematics and Statistics*
- **DOI：** <https://doi.org/10.3389/fams.2026.1749337>
- **Readable URL：** <https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/full>
- **PDF URL：** <https://public-pages-files-2025.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/pdf>
- **Repo URL：** N/A

这篇 paper 真正值得 desk intake 的，不是“DNN、LSTM、ensemble 谁分数更高”这层比赛，而是它把一条相对清楚的 raw alpha 骨架摆出来了：**先做 dynamic cointegration / half-life admission，再对 spread 用 percentile threshold 或 score threshold 做回归交易。**

## 2. 核心结论
- **一句话核心结论：** 这篇 paper 真正可复用的不是“上深度学习就更强”，而是 **`dynamic cointegration gate × thresholded spread fade`** 这条 pairs / stat-arb raw alpha；ML ensemble 更像二层 score 平滑器，不该被误读成 alpha 本体。
- **一句话证明方式：** 证明来自两层：一层是 paper 全文里 Table 2/3/4/5 已把 `Johansen vector -> spread -> threshold breach -> BUY/SELL/HOLD` 的骨架写清楚；另一层是我用 Binance Spot `5m/15m` 对 `ETH/BNB`、`ETH/LTC` 做 public quick check，发现这条线在低摩擦口袋里还有一点 gross，但离“现成 production shell”还差成本与 admission 两道门。
- **paper 里最可用的部分很清楚**：Table 2 用第一协整向量构 spread；正文明确写 `score < lower threshold -> Buy`、`score > upper threshold -> Sell`；Table 5 说明它是按 threshold breach 出 `BUY / SELL / HOLD`，不是简单见极值就冲。
- **headline 反而没那么该先学**：Table 3 确实显示 Dynamic Ensemble 在 `MSE/RMSE/MAE` 上最好（例如 `MSE 0.012124 < 0.017667 / 0.019226`），但 LSTM 的 `MAPE = 1.490429%` 反而最低，说明 paper 自己也不是“一个模型全赢”；更像是 **spread alpha 已经存在，模型只是在帮你重新排序信号质量。**
- **paper 的交易层成绩不算差，但别照单全收**：Table 4 报 `Sharpe = 1.3662`、`Sortino = 1.1411`、`avg P/L per trade = 0.0111`、`MDD = -0.2875`。但正文同时又写“共 `113` 个信号，其中 `81` 胜、`32` 负（`71.68%`）”，和 Table 4 的 `hit rate = 0.5821` 明显对不上；再加上数据段写的是 `2018-01-02 ~ 2025-10-31` 共 `2842` 个 Yahoo 日频观测、`BTC/ETH/LTC/XRP` 六对，而 Figure/Table 又切成 `ETH/BNB/LTC/XRP/USDT` 宇宙，**这篇 paper 可读，但不能把所有数字当“可直接复刻的唯一真相”。**
- **我自己的 short-cycle first verdict 更保守**：最近 `60d` Binance Spot 快检里，`ETH-LTC 15m + fixed z-score` 是最接近能用的一档，约 `135` 笔、`avg gross +2.10 bps/笔`、`gross hit rate 54.8%`，但扣 `2 bps` 也只剩 `+0.10 bps/笔`，扣 `8 bps` 后变成 `-5.90 bps/笔`；`ETH-BNB 5m + quantile threshold` 约 `374` 笔、`avg gross +0.35 bps/笔`，也远扛不住广义 taker 成本。

## 3. 为什么和当前项目有关
这轮仍值得写，原因不是“又来一篇 pairs 文”，而是它补的是一个更精确的 intake 视角：

1. **base alpha 很清楚**：就是 co-integrated spread mean reversion，本体是 raw alpha，不是 filter；
2. **旁支比 headline 更贴 desk**：对 `1m/3m/5m/15m`，先学 `admission + thresholding`，比先学 DNN/LSTM 架构更划算；
3. **适合当前研究节奏**：全文可拿到，方法能快速改写成 `first verdict / friction ladder / admission check`；
4. **还能顺手提醒一个重要坑**：很多“AI pairs paper”里，真正可搬的是 spread 定义和开平仓逻辑，不是最后那层模型包装。

## 3.5 策略拆解（必填）
- 方向属性：**relative-value / pairs / market-neutral / mean reversion**
- 基础 alpha：**动态协整关系成立时，spread 偏离长期均衡后向中枢回归**
- regime：**rolling cointegration / half-life admission；只在关系仍然稳定时交易**
- filter / veto：**upper/lower percentile threshold 或 fixed z-score；极端但不满足阈值结构时继续 HOLD**
- risk / sizing / execution overlay：**dollar-neutral 对冲、median/mean exit、镜像 stop、max-hold、maker/taker 成本阶梯**

## 4. 可复刻的最小实验 + 下一步怎么测
### 本轮最小实验
我没有直接复刻 paper 的 DNN，而是先把更 desk 化的骨架抽出来做快检：
- **市场：** Binance Spot
- **pairs：** `ETHUSDT-BNBUSDT`、`ETHUSDT-LTCUSDT`
- **频率：** `5m / 15m`
- **样本：** 最近 `60d`
- **formation：** rolling `7d` beta / spread / quantile / half-life
- **admission：** half-life 需落在可交易区间（`5m: 1~96 bars`，`15m: 1~48 bars`）
- **entry：**
  - `quantile shell`: spread 跌破 `q10` 做 long spread，涨破 `q90` 做 short spread
  - `zscore shell`: `|z| >= 2` 开仓
- **exit：** 回到 `q50`；或 `max_hold = 6h`；或触发 mirrored stop
- **cost ladder：** `2 / 4 / 8 bps`

### 本轮产物
- 脚本：`reports/artifacts/quant_digests/2026-04-14_frontiers_dynamic_cointegration_probe.py`
- 汇总：`reports/artifacts/quant_digests/frontiers_dynamic_cointegration_probe_summary_2026-04-14.csv`
- 明细：`reports/artifacts/quant_digests/frontiers_dynamic_cointegration_probe_detail_2026-04-14.csv`

### 先记 4 个最重要的数据点
1. **`ETH-LTC 15m + fixed z-score`**：`135` 笔，`avg gross +2.10 bps/笔`，`gross hit rate 54.8%`；`2 bps` 后只剩 `+0.10 bps/笔`，已经是本轮最接近“低摩擦可活”的口袋。  
2. **`ETH-BNB 5m + quantile threshold`**：`374` 笔，`avg gross +0.35 bps/笔`，比同 pair 的 `5m z-score`（`-0.28 bps/笔`）更像样，说明 percentile gate 在某些 fast pair 上确实可能比固定 z-score 更稳。  
3. **但这不是通用结论**：`ETH-LTC` 上反过来是 `15m z-score > 15m quantile`，说明 paper 的 percentile threshold 不是“万能升级件”。  
4. **成本依旧是硬门槛**：本轮 `8 bps` 后所有 bucket 全负，所以它更像 **maker-ish / low-friction pocket candidate**，不是你现在就能 broad taker 化的 production shell。

### 下一步怎么测
1. **先把 pair admission 做成主角，不要先把 DNN 当主角。**
   - 在 `20~30` 个 liquid majors / liquid alts 上，按日或按 `4h` 做 `ADF / half-life / hedge stability` 选对，再把 `5m/15m` 当执行层。
2. **做 `1h admission × 5m/15m execution`。**
   - 这篇 paper 真正像样的部分是“关系先成立再交易”；下一轮别继续裸 rolling 全时段开仓。
3. **把 threshold 视为可替换组件，而不是宗教。**
   - 同一 admission 下同时跑 `q10/q90`、`z=2.0`、`vol-scaled threshold`，比较谁在不同 pair 上更稳。
4. **如果要上 ML，优先预测“该不该开仓 / 哪个 threshold 该用”，而不是直接预测裸价。**
   - 也就是把 ML 放在 score-quality / regime-selection 层，而不是重新发明 spread alpha。

## 5. first verdict
我的判断是：

> **这篇 2026 Frontiers paper 值得进 raw alpha 素材池，但 intake 的正确姿势不是“去抄 DNN ensemble”，而是先吸收 `dynamic cointegration admission × thresholded spread fade` 这条骨架。**

更短一点说：

> **alpha 本体是 spread 回归；ensemble 只是二层打分器。当前 `5m/15m` transfer 说明这条线不是没有 edge，但更像低摩擦口袋，不是拿来广义 taker 化的完整策略。**

## 6. 来源
- Tsoku, J. T., & Makatjane, K. (2026). *Deep learning-based pairs trading: real-time forecasting of co-integrated cryptocurrency pairs*. Frontiers in Applied Mathematics and Statistics.
  - DOI: <https://doi.org/10.3389/fams.2026.1749337>
  - Readable URL: <https://www.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/full>
  - PDF: <https://public-pages-files-2025.frontiersin.org/journals/applied-mathematics-and-statistics/articles/10.3389/fams.2026.1749337/pdf>
  - OpenAlex: <https://openalex.org/W7126164242>
- Local public-data probe artifacts:
  - `reports/artifacts/quant_digests/2026-04-14_frontiers_dynamic_cointegration_probe.py`
  - `reports/artifacts/quant_digests/frontiers_dynamic_cointegration_probe_summary_2026-04-14.csv`
  - `reports/artifacts/quant_digests/frontiers_dynamic_cointegration_probe_detail_2026-04-14.csv`
