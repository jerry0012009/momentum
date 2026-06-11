# 别把 EMA/PSAR 都当 15m 同层入场键：`EMA(RSI)` 分层判势 + Downtrend 禁多，更像三条收口线共用 veto gate
- 时间：2026-03-18 19:56 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/regime/filter/veto/crypto/15m
- 证据类型：论文证据（全文）

## 1. 这次看了什么
看了 **Naganjaneyulu G, Prashanth G, Revanth M, A. V. Narasimhadhan (2023)** 的论文 **Multi Indicator based Hierarchical Strategies for Technical Analysis of Crypto market Paradigm**。它不是再找“更神的 EMA 参数”，而是把指标做了角色分层：先判市场状态，再决定哪些信号可以交易。

## 2. 核心结论
- 一句话核心结论：**比继续调入场参数更值得先测的，是“先判势、再放行、再否决”的层级 gate。**
- 论文里单指标结果是 EMA 最好（文中给到利润百分比 **394.13%**）；但分层后 **MIHS(EMA7)=437.48%**，再加“下跌阶段禁多”约束后 **MIHCS(EMA7)=701.77%**（样本：BTC 2018–2022）。
- 最可复用的不是 headline 收益，而是那条规则骨架：`EMA(RSI)>60` 视为 Uptrend、`<40` 视为 Downtrend；在 Downtrend 把反向买入信号直接 veto。
- 这和我们 desk 当前三条收口线更贴，因为它本质是 **regime + veto**，不是再造一个新 alpha：
  - `V3 breakout-short follow-up`：避免在反弹噪声里提前做多；
  - `Fibonacci retest_hold`：只在允许的 regime 里承认 hold；
  - `EMA / PSAR raw alpha focus`：把 PSAR 更明确地放到下行防守/退出角色。
- 一句话证明方式：**作者用 BTC 历史样本，把单指标与分层策略做回测对照，展示“加层级约束后，组合路径更稳”。**

## 3. 为什么和当前项目有关
这轮值得做它，是因为它直接回答了我们正在收口的共同痛点：
**不是信号不够多，而是缺“什么时候不该让这些信号上桌”的统一判势闸门。**

## 4. 可复刻的最小实验
**研究假设**：在 15m crypto 里，给现有三条收口线加 `EMA(RSI)` regime + downtrend long-veto，会优先降低假确认/反向亏损，并改善成本后表现。

**一个可计算定义（最小版）**：
- `rsi14 = RSI(close,14)`，`ema_rsi7 = EMA(rsi14,7)`；
- `regime_up: ema_rsi7 > 60`；`regime_down: ema_rsi7 < 40`；其余视为 `regime_chop`；
- gate：
  - Long 类信号（Fib retest_hold、EMA continuation long）仅在 `regime_up` 放行；
  - `regime_down` 下忽略 PSAR/RSI 的逆势 BUY（veto）；
  - breakout-short follow-up 在 `regime_down` 优先，`regime_chop` 降权或禁做。

**最小回测切口**：
- 标的：BTCUSDT、ETHUSDT、SOLUSDT perpetual
- 周期：15m
- 样本：近 180d
- 执行：next-bar open、no-overlap、成本 6/10/15 bps per side

**先看 3 个指标**：
1. `false-long rate`（尤其在 downtrend）
2. `post-cost return`
3. `trade-count retention`（防止全靠砍交易数“变好看”）

## 5. 风险与保留意见
- 论文样本是 BTC 2018–2022，且未直接对应 15m + 实盘成本口径；百分比不可直接平移到当前 desk。
- 文中分层阈值（60/40、45/55）在 15m 上可能更敏感，必须做阈值邻域稳定性，不要单点参数崇拜。
- 暂未见作者公开可直接复刻的官方仓库；首轮应按“规则复写 + 小样本诚实检验”推进。

## 6. 来源
1. **Naganjaneyulu G, V. S. S. K. R., Prashanth G., Revanth M., & Narasimhadhan, A. V. (2023).** *Multi Indicator based Hierarchical Strategies for Technical Analysis of Crypto market Paradigm*. International Journal of Electrical and Computer Engineering Systems, 14(7), 765–780.
   - DOI: https://doi.org/10.32985/ijeces.14.7.4
   - Readable URL: https://ijeces.ferit.hr/index.php/ijeces/article/view/2517
   - PDF URL: https://ijeces.ferit.hr/index.php/ijeces/article/view/2517/322
   - Repo URL: N/A（论文页未提供官方公开代码仓库）
2. Crossref metadata（用于 DOI/期刊元数据核验）
   - URL: https://api.crossref.org/works/10.32985/ijeces.14.7.4

## 7. 下一步怎么测
先做一个单改动 A/B：**只在现有三条收口线上叠加 `regime + downtrend long-veto`**，不改原始 entry/exit。若它不能在保留主要交易数的前提下明显压低 `false-long rate`，就不继续占用收口预算。