# 别急着把 EMA/PSAR 当 15m 主 alpha：先用大样本技术规则给三条收口线定“家族座次”

## 这轮为什么选它（先回答 2.5）

这轮选 Deprez & Frömmel (2024) 不是为了再抄一个新指标，而是为了解一个更上游、会直接影响当前三条收口线的决策问题：

- **breakout-short follow-up** 到底该继续以 breakout/filter 家族做主，还是把 EMA/PSAR raw 当主；
- **Fib retest_hold** 应该是主触发，还是只做确认层；
- **EMA/PSAR raw alpha focus** 该不该继续按“独立入场 alpha”推进。

如果这个“家族座次”没先定，后面继续堆 gate 容易变成近义重复。

---

## 一句话核心结论

**这篇 2024 大样本结果更支持我们把 `breakout/filter` 放在主触发位、把 `EMA/PSAR` 降到确认/风控位，而不是反过来。**

## 一句话它怎么证明的

作者在 BTC 超长样本上，用 **75,360 条简单技术规则**（跨日频+日内）做了“交易成本 + 多重假设检验 + OOS 组合”三重约束，结论不是单条神规则，而是**规则家族在现实摩擦下的可生存性排序**。

---

## 这篇论文里最值得我们偷的“旁支”

不是 headline 的“技术分析能不能赚钱”，而是：

1. **先做家族筛选，再做组合**，而不是先拍脑袋定单条规则；
2. **先过成本和数据挖掘诚实门槛，再谈 OOS**；
3. **交易可行性边界要写清楚**（论文样本交易所不支持做空，意味着 short 结论不能硬镜像）。

这三点对我们当前 desk 比再加一个微型 filter 更值钱。

---

## 对三条收口线的直接映射

### 1) V3 final-verdict / breakout-short follow-up
- 先把 `filter/channel breakout` 家族保留在主触发位；
- short follow-up 继续做，但必须单独看 short 侧证据，不得默认拿 long 侧结论镜像。

### 2) Fibonacci confirmation / retest_hold
- Fib 更适合留在“确认层/否决层”，
- 不要把 Fib 单独升格为脱离结构主触发的独立 alpha。

### 3) EMA / PSAR raw alpha focus
- EMA/PSAR 暂时更像 **角色层（确认、fail-fast、仓位）**，
- 不宜继续按“裸主入场键”扩写。

---

## 15m 最小可复现实验（下一步怎么测）

**目标**：给三条收口线一个“家族座次 first verdict”。

- 资产：`BTC/ETH/SOL` perpetual
- 周期：`15m`
- 执行：`next-bar open + no-overlap`
- 成本：`6/10/15 bps per side`

### 三臂（只做一轮最小）
1. `A: breakout/filter baseline`
   - 20-bar breakout + 最小 close-confirm（1 bar）
2. `B: EMA/PSAR raw baseline`
   - EMA 方向 + PSAR flip 直接入场
3. `C: A + EMA/PSAR role overlay`
   - 触发仍由 A 给；EMA/PSAR 只做 admission/fail-fast（不创造方向）

### 先看四个指标
- `post_cost_expectancy`
- `trade_count_retention`
- `false_follow_ratio@4bars`
- `long_short_decomposition`（尤其 short 侧是否只是样本幻觉）

**判决规则（最小版）**：
- 若 `C` 在不过度砍交易数前提下优于 `A`，则 EMA/PSAR 定位为 overlay；
- 若 `B` 仍弱于 `A/C`，则 EMA/PSAR 不升格为 raw 主 alpha。

---

## 风险与边界（避免过度解读）

- 论文主样本是 BTC 且有交易制度边界，不能自动外推到我们的多资产 short 侧；
- “大规模规则筛选有效”不等于“某条参数永远有效”；
- 这轮只回答**座次问题**，不回答最终 deployment。

---

## 来源（paper / repo）

1. **Deprez, N., & Frömmel, M. (2024)**
   - Title: *Are simple technical trading rules profitable in bitcoin markets?*
   - Venue: *International Review of Economics & Finance*
   - DOI: `10.1016/j.iref.2024.05.003`
   - Readable URL: `https://www.sciencedirect.com/science/article/pii/S1059056024003010`
   - Repo URL: `N/A (paper-based)`

> 本文关键可引用数据点：
> - 规则规模：`75,360` 条简单技术规则
> - 数据口径：Bitstamp BTC 逐笔数据（清洗后用于日频+日内规则测试）
> - 评估框架：交易成本 + 多重假设检验 + OOS 组合表现
