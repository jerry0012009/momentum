# 别把 local Hurst 直接硬搬成 `H<0.5` 开仓 veto：对 short-cycle desk，更该先测的是「fast-reversion pocket rank × spread mean reversion」，而不是把它当万能绿灯
- 时间：2026-04-10 18:57 UTC
- 类型：2024 *Mathematics* 论文（OpenAlex abstract + DOI metadata）+ 2025 companion paper 元数据 + Binance USDⓈ-M `5m` portability probe
- 主题类型：raw alpha
- 基础 alpha：**pairs / stat-arb 的 spread mean reversion；`local Hurst` 在这篇材料里不是 alpha 本体，而是用来识别“这次 spread 更可能较快回中线”的 entry-time admission / fast-reversion pocket。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（作为 pairs shell 的 admission layer 可以独立落地，但单独把 `H<0.5` 当硬开关，当前 desk probe 不支持直接照搬）
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/local-hurst/anti-persistence/fast-reversion-pocket/admission-layer/binance/perpetuals/5m/paper/public-data/cost/risk
- 证据类型：论文证据（主论文摘要级）+ companion paper 元数据 + public-data portability probe

> 先回答一句：**这篇东西的 base alpha 是什么？**
>
> **base alpha = spread 偏离后的 pairs mean reversion。**
> `local Hurst` 在这里服务的是 **“这次回归会不会来得更快”**，所以它更像 `entry-time admission / pocket rank`，不是另起一条独立 alpha。

## 1. 这次看了什么，为什么这轮值得写
这轮主看的是：

1. **Grande, Borondo, Losada, Borondo (2024). _Anti-Persistent Values of the Hurst Exponent Anticipate Mean Reversion in Pairs Trading: The Cryptocurrencies Market as a Case Study_. *Mathematics*.**
   - DOI：`10.3390/math12182911`
   - DOI URL：`https://doi.org/10.3390/math12182911`
   - Readable URL：`https://www.mdpi.com/2227-7390/12/18/2911`
   - OpenAlex 摘要核心：作者把 **local Hurst exponent** 当作开仓信号，主张 **`H < 0.5` 的 anti-persistent spread 会更快回到均值**；他们还写到，把 `H<0.5` 纳入 pairs strategy 后，回测结果是盈利的。
2. **Ramos-Requena, José Pedro & Bağcı, Mahmut (2025). _Analysis Pairs Trading Strategy Applied to the Cryptocurrency Market_. *Computational Economics*.**
   - DOI：`10.1007/s10614-025-11149-y`
   - DOI URL：`https://doi.org/10.1007/s10614-025-11149-y`
   - Readable URL：`https://link.springer.com/article/10.1007/s10614-025-11149-y`
   - 摘要页可见核心：作者使用 **generalized Hurst exponent (GHE)** 做 crypto pairs trading，并与 `Distance / Correlation / Cointegration` 对比。

这轮值得写它，不是因为它给了一个全新的 pairs 本体，而是因为它回答的是一个很 desk 的问题：

> **spread 已经偏离了，那这次回归会不会来得足够快，快到能覆盖成本？**

这和当前素材池直接相关，因为它补的是 **pairs alpha 的 admission / 快速回归识别层**，而且能很快压到 `5m` 最小实验。

## 2. 一句话核心结论
### 论文给的结论
**别只看 spread 有没偏离；更该优先做那些 `local Hurst` 显示 anti-persistent、也就是更像“很快回去”的那批 trade。**

### 我这轮给 desk 的结论
**这条读法值得保留，但不要直接把论文里的 `H<0.5` 硬搬到 Binance `5m` majors futures 上当开仓绿灯。**
在我这轮 `5m` portability probe 里，**简单 local-H proxy 的 hard veto 非但没明显改善，反而大幅缩小样本、且整体净值更差**。更合理的 desk 读法是：

- 把 `local Hurst` 当 **relative pocket rank / pair-specific admission feature**；
- 不要一上来就把它当 **跨 pair 通用、跨 estimator 通用、跨市场结构通用** 的绝对阈值。

## 3. 论文真正值钱的点，不在“又一个 Hurst 指标”，而在“快回归 trade”的识别
OpenAlex 摘要里最关键的 3 句话，其实已经够支撑 intake：

1. **作者关注的是“mean reversion will happen quickly”**，因为持仓拖太久，手续费会吃掉 edge；
2. 他们提出把 **local Hurst exponent** 当作开仓信号；
3. 他们声称 **anti-persistent 的 Hurst 值对应的 spread，显著更快回到均值**。

翻成人话就是：

- 不是所有 spread 偏离都一样；
- 真正值钱的是那些 **很快 recross** 的偏离；
- `local Hurst` 被作者拿来做的，本质上是 **快回归机会识别**。

这点跟一般 pairs 文章只讲 `cointegration + z-score` 很不一样，因为它直接切中 short-cycle 的痛点：

> **你不只是要“最终会回归”，你要的是“尽快回归”。**

## 4. 这条线和 4/6 那篇 GHE digest 有什么不同
这轮不是简单重复 `2026-04-06_0115_ghe-pair-selection-spread-meanreversion-alpha.md`。

那篇的重心是：
- **GHE / Hurst 用于 pair formation / pair ranking**；
- 问题是“哪一对更值得先放进 active pairbook”。

这篇的重心则是：
- **local Hurst 用于这次具体 entry 是否值得做**；
- 问题是“同一条 pairs alpha 上，这一次 spread 偏离是不是更像快回归 pocket”。

所以它更像一个 **entry-time fast-reversion gate**，不是 pairbook construction note 的重写。

## 5. 我做的 `5m` portability probe：先看 hard gate 能不能直接搬
### 5.1 实验设置
我用 Binance USDⓈ-M 公共 `5m` 数据，对 4 个 majors pair 做了一个第一轮 desk probe：

- pair：`ETHUSDT-SOLUSDT`、`XRPUSDT-ADAUSDT`、`ADAUSDT-DOGEUSDT`、`BTCUSDT-ETHUSDT`
- 数据窗：近约 `20d`
- hedge：rolling `288` bars beta
- spread：`log(Pa) - beta * log(Pb)`
- entry：`|z| >= 2`
- exit：回到中线或 `24` 根 `5m` time-stop
- 成本：每笔 spread 先粗扣 `8bps`
- local-H proxy：用 entry 前 `96` 根 `5m` spread 窗口做简化 Hurst 估计
- 两个版本：
  1. **baseline**：裸 spread MR
  2. **gate**：只做 `H < 0.45`

### 5.2 第一眼结果：把 `H<0.45` 当硬 gate，样本直接被砍没了
本地结果文件：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/hurst_pairs_5m_baseline_small_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/hurst_pairs_5m_gate045_small_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/hurst_pairs_5m_compare_small_2026-04-10.csv`

组合层面最重要的数字：

- **baseline**：`200` 笔，平均每笔约 **`-3.45bps`**
- **H<0.45 gate**：只剩 **`6` 笔**，平均每笔约 **`-16.70bps`**

也就是说，**按这套简化 estimator + majors futures `5m` 口径，论文里的绝对阈值式 hard veto 没有直接迁移成功。**

pair 级别上也很 mixed：
- `XRPUSDT-ADAUSDT`：gate 后只剩 `1` 笔，但单笔 `+30.94bps`，说明可能存在 pocket；
- `ETHUSDT-SOLUSDT`：gate 后只剩 `3` 笔，平均反而掉到 `-29.19bps`；
- `BTCUSDT-ETHUSDT`：直接筛到 `0` 笔。

所以这轮不能诚实地说“`H<0.5` 一上就能救 pairs”。

## 6. 第二眼结果：如果不用绝对阈值，而看相对 bucket，会发生什么
为避免把论文直接误杀，我又做了一个更 desk 化的检查：

> **不问 `H<0.5` 对不对，而问“同一批 entry 里，local H 更低的 trade，是否至少更快回归 / 更赚钱？”**

对应本地文件：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/local_hurst_pairs_5m_entry_trades_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/local_hurst_pairs_5m_global_bucket_summary_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/local_hurst_pairs_5m_pair_bucket_summary_2026-04-10.csv`

全样本按 entry-H 三分桶后，结果是：

- **low-H bucket**：`67` 笔，胜率 `40.30%`，平均 **`-1.98bps`**
- **mid-H bucket**：`66` 笔，胜率 `36.36%`，平均 **`-16.78bps`**
- **high-H bucket**：`67` 笔，胜率 `52.24%`，平均 **`+9.63bps`**

这说明一个不太讨喜但很重要的事实：

> **在这套 majors futures `5m` quick probe 里，简单 local-H proxy 的相对排序，甚至更像“高 H 更好”，而不是论文想表达的“低 H 更快回归”。**

pair 级别里也能看到这种反差：
- `ETHUSDT-SOLUSDT`：high-H bucket 平均约 **`+23.05bps`**，low-H bucket 约 **`-15.74bps`**
- `ADAUSDT-DOGEUSDT`：high-H bucket 平均约 **`+21.22bps`**，low-H bucket 约 **`+5.68bps`**
- `XRPUSDT-ADAUSDT`：三档都偏弱，但 high-H 仍相对最好

这轮结论非常明确：

**如果 desk 要碰这条线，第一步不是照抄 `H<0.5`，而是先回答“你的 estimator / 你的市场 / 你的 pair universe 里，local H 到底在排序什么”。**

## 7. 给当前项目的最值钱读法
### 7.1 这条线仍然值得保留，但要换读法
这条线不是废了，而是应该从：

- **“绝对阈值 hard gate”**

改读成：

- **“pair-relative fast-reversion rank”**
- **“time-stop / hold-budget 的辅助变量”**
- **“pairbook 内部排序特征，而不是全市场统一红绿灯”**

### 7.2 为什么这比继续补一个抽象 filter 更有价值
因为它服务的仍然是一个完整 raw alpha：

- alpha 本体：spread mean reversion
- 这篇 paper 提供的增量：**哪次偏离更像值得做、而且值得尽快做**

所以它不是纯解释型材料，也不是脱离交易壳的宏观状态变量；它是一个 **raw alpha admission component**。

## 8. Desk 版最小可落地改写
如果要把这篇东西改成更适合我们 desk 的版本，我会建议这样写：

### A. 不先用绝对阈值，改成 pair 内分位排序
- 对每个 pair 单独估 `local H`
- 不先写死 `H<0.5`
- 改成：
  - `entry_z` 触发后，只有当 `H` 落在该 pair 自身历史的较优分位（如底部/顶部 `30%`，取决于经验方向）才开

### B. 把 H 先用在 hold-budget，而不是 entry veto
- `H` 指向“快回归 / 慢回归”的概率时，先拿它调：
  - `time-stop`
  - `take-profit band`
  - `size-down / size-up`
- 这样比一刀切 veto 更稳，因为它减少了 estimator 失配带来的误杀

### C. 把 H 和 HL / cointegration 稳定性一起看
更像 desk 版本的组合是：
- `cointegration / ADF`：先保证不是纯噪音
- `half-life`：保证不是慢到没法做
- `local H`：再做快回归 pocket 排序

## 9. 下一步怎么测
这轮最该做的不是继续争论 H 理论，而是把它压进一个清晰 A/B/C/D：

### A = baseline pairs MR
- corr / cointegration 选 pair
- `|z| >= 2` 开仓
- `z -> 0` 或 time-stop 退出

### B = A + absolute H gate
- 测 `H < {0.40, 0.45, 0.50}`
- 明确回答：是不是只是样本被筛没了

### C = A + pair-specific H percentile rank
- 每个 pair 内按 rolling H percentile 做 gate
- 比较它是否优于绝对阈值

### D = A + H-informed hold budget
- 不 veto 开仓
- 只用 `H` 改 `time-stop / target / size`

最小实验建议：
- universe：Binance 前 `20~30` 个高流动 perp
- bar：`5m` 为主，`15m` 只做确认
- walk-forward：`train 45d / test 14d`
- pair 选择禁止 test 反选
- 成本：`8 / 12 / 16 bps` 三档
- 输出：
  - net bps / trade
  - avg holding bars
  - stop-out ratio
  - gate 后 trade-count retention
  - per-pair contribution

## 10. 风险与保留意见
1. **主论文在本环境里仍是摘要级证据。**
   - 这轮是高质量 intake + portability probe，不是论文逐表 faithful replication。
2. **本地用的是简化 local-H proxy，不是论文原始全部实现。**
   - 这正是为什么这轮该先回答“可迁移吗”，而不是宣称“论文错了 / 我们对了”。
3. **这轮样本只覆盖 4 个 majors futures pair、近约 20 天。**
   - 它够回答“能不能直接硬搬”这个问题；
   - 但还不够回答“这条线最终值不值得做”。
4. **当前结果更像一个否定式结论：**
   - `local Hurst` 值得继续保留；
   - 但 **不要把 `H<0.5` 直接当 desk 级固定门槛。**

## 11. 这轮给 Jerry 的一句话建议
**这篇 paper 可以进素材池，但优先级不是“立刻照抄 `H<0.5` 开仓”，而是“把 `local H` 当 pairs MR 的 fast-reversion pocket rank / hold-budget feature，再做 pair-specific walk-forward”。**

## 12. 来源
### 论文 / 元数据
1. Grande, M., Borondo, F., Losada, J. C., & Borondo, J. (2024). *Anti-Persistent Values of the Hurst Exponent Anticipate Mean Reversion in Pairs Trading: The Cryptocurrencies Market as a Case Study*. *Mathematics*.
   - DOI: `10.3390/math12182911`
   - DOI URL: `https://doi.org/10.3390/math12182911`
   - Readable URL: `https://www.mdpi.com/2227-7390/12/18/2911`
2. Ramos-Requena, J. P., & Bağcı, M. (2025). *Analysis Pairs Trading Strategy Applied to the Cryptocurrency Market*. *Computational Economics*.
   - DOI: `10.1007/s10614-025-11149-y`
   - DOI URL: `https://doi.org/10.1007/s10614-025-11149-y`
   - Readable URL: `https://link.springer.com/article/10.1007/s10614-025-11149-y`

### 本地实验产物
- `/root/clawd/jerry/momentum/reports/artifacts/literature/hurst_pairs_5m_baseline_small_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/hurst_pairs_5m_gate045_small_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/hurst_pairs_5m_compare_small_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/local_hurst_pairs_5m_entry_trades_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/local_hurst_pairs_5m_global_bucket_summary_2026-04-10.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/local_hurst_pairs_5m_pair_bucket_summary_2026-04-10.csv`
