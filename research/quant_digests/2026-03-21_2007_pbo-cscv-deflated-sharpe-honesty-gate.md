# 别把三条 15m 收口线的“best backtest Sharpe”当真：PBO(CSCV) + Deflated Sharpe Ratio 更像 shared honesty gate
- 时间：2026-03-21 20:07 UTC
- 类型：GitHub 仓库 + 论文（方法论）
- 主题标签：breakout-short / fibonacci-confirmation / retest_hold / EMA / PSAR / model-selection / backtest-overfitting / CSCV / PBO / deflated-sharpe / PSR / MinTRL
- 证据类型：论文证据 + 工程实现（可复刻）

## 1) 这次看了什么
- GitHub：`esvhd/pypbo`（Python 实现：PBO、OOS 低于阈值概率、Performance Degradation、PSR/DSR/MinTRL 等统计量）
- 论文母体：Bailey / Lopez de Prado 系列（PBO、PSR Efficient Frontier、Deflated Sharpe 等）

## 2) 核心结论（给 desk 的一句话）
**当我们同时在 breakout-short / Fib retest_hold / EMA-PSAR 上扫很多“确认层/过滤层/参数组合”时，最危险的不是某个规则本身，而是“从一堆候选里挑到一个看起来最强的那条”——PBO(CSCV) + DSR 能把这个挑选偏差量化成一个可落地的 shared honesty gate。**

## 3) 这对当前三条收口线为什么直接有用
我们这阶段的工作方式本质是：
- 给三条线分别提出一堆 **可枚举的变体**（阈值、窗口、确认时窗、multi-bar 组合、对称/非对称等）；
- 然后再用 15m/5m 的回测去挑“看起来最稳/最好”的那条。

问题在于：**当候选很多时，最大 Sharpe/最大 PnL 的那条，往往只是“碰巧适配了样本噪声”**。
- 这会直接拖慢 `V3 final-verdict / breakout-short follow-up` 的收口（我们会在很多“看似有效但 OOS 崩掉”的 verdict 上反复）。
- 也会让 `Fibonacci confirmation / retest_hold` 变成“参数炼丹”（0.5/0.618/0.786、容差、确认窗）而不是可迁移骨架。
- 对 `EMA / PSAR raw alpha focus` 更致命：裸 alpha 本来就 edge 薄，任何选择偏差都足以把它从“看似可用”推到“实盘归零”。

所以这不是“与三条线无关的统计洁癖”，而是一个 **加速收口** 的工具：把候选搜索/选择这一环变得更诚实。

## 4) 可复刻的最小实验（建议今天就能开跑）
目标：给任意一条收口线的候选集合，加一个统一的“选择偏差体检”。

### 4.1 实验对象（先选一个 family，别贪多）
建议从 **最容易产生大量变体** 的地方切：
- `retest_hold`：Fib zone 深度（38-62/62-79）、容差、confirmWindow/entryWindow、是否要求 re-break、是否要求 small-body、是否要 volume dry-down 等。
或
- `breakout-short final-verdict`：outside-close→reentry、body-zone re-entry、sign-flip density、failed-bounce band 等（每个都有阈值/窗口）。

把这些变体做成一个候选集：
- 例如 **K=50~300 条**规则（够用，别上千）。

### 4.2 数据口径（最小可复现）
- 频率：15m（主），可附带 5m（用于“确认层是否依赖更低 TF”）
- 资产：先 BTCUSDT / ETHUSDT / SOLUSDT（与当前 digest 体系一致）
- 样本：至少 12 个月；更好是 24~36 个月
- 回测产物：对每条规则输出一条 **逐 bar 策略收益序列**（净值变化），对齐成 `rtns_df`：
  - 行=index=timestamp
  - 列=每个规则（variant）

### 4.3 用 pypbo 跑 PBO（CSCV）
核心想法（CSCV）：把全样本切成 S 个等份（例如 S=16），枚举一组 in-sample 组合与 out-of-sample 组合：
1) 每次用一组 IS 子样本挑“IS 指标最好的规则”；
2) 再看它在对应 OOS 子样本里的排名；
3) 如果经常出现“IS 第一、OOS 很差”，说明你是在被选择偏差喂糖。

最小代码（repo README 给的接口骨架）：
```python
import pypbo as pbo
import pypbo.perf as perf
import numpy as np

def metric(x):
    # annualized sharpe（这里的年化系数你要按 15m 频率改）
    return np.sqrt(365*24*4) * perf.sharpe_iid(x)

pbox = pbo.pbo(rtns_df, S=16, metric_func=metric, threshold=1, n_jobs=4,
              plot=True, verbose=False, hist=False)
```

### 4.4 先看哪些指标（别一次看十个）
1) **PBO（越低越好）**：
   - 可先把门槛设得很朴素：`PBO < 0.2` 才允许进入下一轮精炼；`0.2~0.4` 标记为“高风险候选”；`>0.4` 直接淘汰。
2) **Performance Degradation / P(OOS below threshold)**：
   - 设一个“最低可接受 Sharpe / Calmar / hitrate”阈值，看 OOS 低于阈值的概率。
3) （可选）**Deflated Sharpe Ratio (DSR)**：
   - 当你比较的候选很多、且收益分布偏厚尾时，DSR 比裸 Sharpe 更诚实。

### 4.5 最小验收标准（把“下一步怎么测”落到可执行）
- 用同一套候选集 K：
  - 在 BTC/ETH/SOL 三个币上分别跑 PBO
  - 再做一个 pooled（把三个币的收益拼接或做等权组合收益）跑 PBO
- 产出一个表：每个规则的
  - IS 指标（Sharpe/Calmar 等）
  - PBO
  - OOS degradation
  - DSR / PSR（如能算）
- 下一步只保留：
  - `PBO` 低 + `trade count` 足够 + 成本后仍过线 的 5~20 条规则

> 这一步的意义：**先把“选择偏差风险”降到可控，再继续讨论哪条确认层更像真 edge**。

## 5) 风险与保留意见
- 这是“挑选过程的诚实度”工具，不会自动把烂 alpha 变好 alpha。
- PBO/DSR 对输入的收益序列很敏感：
  - 必须是 **净收益（含成本）**，否则会把交易频率高的确认层误判为强；
  - 必须保证无 lookahead（尤其你们近期在抓 `closed-bar HTF context`，这里要保持一致）。
- CSCV 分片 S 的选择会影响结果：
  - S 太小 → 估计粗；S 太大 → 每片样本太短（15m 下波动很大）。建议从 8/16/20 做敏感性。
- 对 crypto 这种厚尾 + regime 快切换市场：
  - metric 可能不该只用 Sharpe；可以加一个“尾部惩罚版指标”（例如 downside deviation / maxDD 惩罚）。

## 6) 来源（尽量可直接访问）
### GitHub 仓库
- esvhd. `pypbo` — Probability of Backtest Overfitting in Python.
  - Repo URL: https://github.com/esvhd/pypbo
  - Raw README: https://raw.githubusercontent.com/esvhd/pypbo/master/README.md

### 论文 / Working Paper（母体方法）
- Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. J. (2015). *The Probability of Backtest Overfitting*. Journal of Computational Finance (Risk Journals).
  - DOI (SSRN): https://doi.org/10.2139/ssrn.2326253
  - Readable URL: https://ssrn.com/abstract=2326253
- Bailey, D. H., & López de Prado, M. (2012). *The Sharpe Ratio Efficient Frontier*. Journal of Risk.
  - DOI (SSRN): https://doi.org/10.2139/ssrn.1821643
  - Readable URL: https://ssrn.com/abstract=1821643
- Bailey, D. H., Borwein, J. M., López de Prado, M., & Zhu, Q. J. J. (2014). *Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance*. Notices of the AMS.
  - DOI (SSRN): https://doi.org/10.2139/ssrn.2308659
  - Readable URL: https://ssrn.com/abstract=2308659
- Bailey, D. H., & López de Prado, M. (2014). *The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality*. Journal of Portfolio Management.
  - Readable URL (SSRN): https://ssrn.com/abstract=2460551

---

### 附：落地建议（给我们的工程队列）
- 把 `PBO/DSR check` 作为每条 digest 进入“可继续收口”的统一门槛：
  - 没过 → 只记录为“想法/假设”；
  - 过了 → 才进入更重的 OOS/多币/成本梯度验证。
