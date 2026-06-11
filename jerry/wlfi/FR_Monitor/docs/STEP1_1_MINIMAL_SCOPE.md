# Step 1.1 最小可控研究范围

> 日期：2026-05-10
> 目标：在不扩大复杂度的前提下，验证三个关键问题。

---

## 0. 保持“可控”的原则

这一步不做大而全研究，不新增小时/分钟线，不做全市场 IC/IR 挖掘。  
我们只基于已有的 Binance 日线面板，做一次最小版本的状态化事件研究。

---

## 1. 最小范围

### 1.1 Universe

当日 eligible 的 symbol 中，按当天 `quote_volume` 取 Top 150。

这样做的好处：

- 比 30d trailing Top100 更容易捞到“今天突然放量”的币；
- 但仍然保持在单日 universe，不用今天信息回看历史；
- 范围可控，不会爆炸。

### 1.2 事件类型

只做两类，先把逻辑吃透：

1. `top_gainer_1d`
2. `top_loser_1d`

每类每天取 **Top 15**，不要做 20/50/100 全展开。

### 1.3 状态拆分

对每一个事件再拆成三类：

1. `new`：前一天不在同类榜单
2. `streak2`：昨天已在同类榜单，今天继续
3. `streak3_plus`：已连续 3 天及以上

这能直接回答你提的问题：  
“连续涨两天算几个事件”→ 我们明确拆开，不混在一起。

### 1.4 观察重点

第一轮只看几个关键口径：

- `fwd_ret_1d`
- `fwd_ret_3d`
- `fwd_ret_5d`
- `long_total_ret_5d`
- `short_total_ret_5d`
- `mae_long_5d`
- `mfe_long_5d`

第一轮不做大量形态工程，只先比较：

- new vs streak2 vs streak3_plus
- top gainer vs top loser

---

## 2. 第一版不做什么

为了保持可控，Step 1.1 **不先做**：

- 当日成交额 Top200 + 30d Top100 双轨合并
- 动量/反转形态分类器
- 连续放量/缩量形态
- MA 回归特征
- 小时/分钟线补采
- 多因子 IC 挖掘

这些都放到 Step 1.2 或 1.3。

---

## 3. 为什么这样做

因为我们当前最需要的是回答一个非常具体的问题：

> “首次进入涨跌榜” 和 “持续留在涨跌榜” 是不是同一类事件？

如果答案是“不是”，后面才值得继续做形态研究。  
如果答案是“差不多”，我们就不应该在 streak 上面再浪费太多时间。

---

## 4. 产物

脚本：

```text
scripts/build_binance_daily_event_study_v1.py
```

输出：

```text
reports/artifacts/binance_daily_event_study_v1/events_v1.csv
reports/artifacts/binance_daily_event_study_v1/streak_summary_v1.csv
reports/artifacts/binance_daily_event_study_v1/type_summary_v1.csv
reports/artifacts/binance_daily_event_study_v1/manifest_v1.json
```

解读页：

```text
reports/site/paper/binance_daily_event_study_v1.html
```
