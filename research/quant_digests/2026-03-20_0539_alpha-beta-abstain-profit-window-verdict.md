# 别让 15m 的 final verdict 被“高准确率”绑架：`双阈值 abstain + 按收益选窗口` 更适合 breakout-short / Fib retest / EMA-PSAR
- 时间：2026-03-20 05:39 UTC
- 类型：论文 + 代码仓库
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/abstain/threshold/window-selection/profitability/regime/filter/crypto/15m
- 证据类型：论文证据 + 工程实现

## 1) 这次看了什么
主看 Parente, Rizzuti, Trerotola (2024) 的加密交易论文与配套代码。它真正可迁移到我们 desk 的旁支，不是“再训一个 MLP”，而是两件更快落地的机制：
1) **双阈值标签/过滤（α, β）**；
2) **先按收益选窗口，不按准确率选窗口**。

## 2) 一句话核心结论
对 5m/15m 来说，`小波动不做 + 过大冲击也不追 + 用 PnL 而非 accuracy 选窗口`，比继续在单一信号上微调参数，更能直接服务三条收口线的收敛。

## 3) 它怎么证明这件事（关键数据点）
- 数据：402 个 USDT 交易对，4h K，2017-08-17 ~ 2022-12-04，约 150 万样本。
- 标签机制：
  - `|R| <= α` 或 `|R| >= β` → Hold（不交易）；
  - 仅在 `α < |R| < β` 且方向明确时给 Buy/Sell。
- 阈值设定：`α=0.038`（85 分位），`β=0.24`（99.7 分位），且 β 随 forward window 增大按 10% 递增。
- 关键反常识：**最高准确率并非最高收益**。按准确率最优是 `(backW=5, forW=1, Acc=0.72)`；但按收益选出来的是 `(5,2)`（文中回测模型）。
- 回测（含 0.1% 费率）在 10% stop-loss 下给出较高 ROI（长周期）：ETH 165.91、BTC 61.22、ALGO 36.18；说明“窗口与阈值的交易语义”比单看分类分数更重要。

## 4) 对三条收口线的直接映射
- `V3 final-verdict / breakout-short follow-up`：
  把 `|预期位移|>=β` 作为 **shock/chase veto**（避免末端追空）；`|预期位移|<=α` 作为 **chop veto**。
- `Fibonacci confirmation / retest_hold`：
  回踩后若位移仍落在 `α` 内，视作“没走出来”，不计确认；若一根冲到 `β` 外，默认不追，等二次确认。
- `EMA / PSAR raw alpha focus`：
  先保留原始触发，再叠一层 `α-β` admission/veto，减少“信号有了但交易质量很差”的样本。

## 5) 最小可复现实验（5m/15m，先做这个）
1. 资产：BTC/ETH/SOL perpetual；周期：15m（可加 5m 作为执行层）。
2. 对每条候选信号（breakout-short / fib retest / ema-psar），计算 `k` 根前瞻收益绝对值 `|R_{t→t+k}|`（含手续费口径，先用 6~10 bps 往返近似）。
3. 用训练段分位数定阈值：`α = p85(|R|)`，`β = p99.5~p99.7(|R|)`；并测试 `k=1,2,3`。
4. 只比较三组：
   - baseline（无 gate）
   - `α` gate（去低位移）
   - `α+β` gate（去低位移 + 去冲击追单）
5. verdict 指标优先级：`净收益/回撤/交易次数衰减/成本后 Sharpe`；**不以 accuracy 排名做最终决策**。

## 6) 风险与边界
- 论文原始频率是 4h，不可直接照搬到 15m；阈值必须按 15m 分布重估。
- β 过紧会错过趋势延续，过松会放大追单；要用 OOS + 成本敏感性一起定。
- 该层是 filter/overlay，不是主信号替代品。

## 7) 来源（paper / repo）
1. Parente, M., Rizzuti, L., & Trerotola, M. (2024). *A profitable trading algorithm for cryptocurrencies using a Neural Network model*. Expert Systems with Applications, 238, 121806.
   - DOI: https://doi.org/10.1016/j.eswa.2023.121806
   - Readable URL: https://www.sciencedirect.com/science/article/pii/S0957417423023084
2. Parente, M., Rizzuti, L., & Trerotola, M. (2023). *CryptoTrading.zip* (software archive).
   - DOI: https://doi.org/10.6084/m9.figshare.22953377.v1
   - Repo URL (code mirror): https://github.com/fovi-llc/CryptoTrading
   - Figshare URL: https://figshare.com/articles/software/CryptoTrading_zip/22953377
