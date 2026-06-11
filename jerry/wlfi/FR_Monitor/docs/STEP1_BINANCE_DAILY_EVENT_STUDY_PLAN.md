# Step 1 — Binance 日线 K 线 + Funding 单事件研究计划

> 日期：2026-05-10  
> 目标：用已有 Binance 历史日线 K 线与 funding 数据，先做最小可复现的单事件研究，找出后续值得深入的事件模板。  
> 输入：`/root/clawd/jerry/momentum/reports/artifacts/rank154_long_history/daily_panel.pkl`  
> 输出：`reports/artifacts/binance_daily_event_study_v0/`

---

## 0. 为什么先做日线版本

当前本地 Binance archive 面板已经存在，覆盖多年、多 symbol，并且已经避免了“用今天流动性排名回看历史”的未来污染问题。

这个面板是日线级别，因此 Step 1 先做 **daily event study**，不强行做 1h/4h。1h/4h 后续可以在拿到分钟/小时 K 线后升级。

---

## 1. 核心研究问题

第一版只回答四个问题：

1. **涨幅榜事件**：日内大涨后，未来 1/3/5/10 天是继续趋势，还是均值回归？
2. **跌幅榜事件**：日内大跌后，未来 1/3/5/10 天是继续下跌，还是反弹？
3. **Funding extreme**：高正 funding / 高负 funding 后，未来价格与 funding-adjusted return 怎么走？
4. **组合事件**：`top_gainer + high_funding`、`top_loser + negative_funding` 是否比单独事件更厚？

---

## 2. 历史 universe 口径

每个历史日期单独构造 universe：

- `is_eligible == True`；
- `trail_quote_volume_30d` 非空；
- `listing_days >= 30`；
- 当天按 `trail_quote_volume_30d` 取 TopN，默认 Top100；
- 不使用当前 ticker 排名，不引入今天信息。

---

## 3. 事件定义 v0

### E1：Top Gainer 1D

```text
当日 close/前日 close - 1 位于当日 universe Top K
```

默认：Top20。

### E2：Top Loser 1D

```text
当日 close/前日 close - 1 位于当日 universe Bottom K
```

默认：Bottom20。

### E3：Positive Funding Extreme

```text
carry_raw = 当日最后一笔 settled funding rate
funding_per_hour_est = carry_raw / (24 / funding_count)
funding_per_hour_est 位于当日 universe Top K
```

默认：Top20。

### E4：Negative Funding Extreme

```text
funding_per_hour_est 位于当日 universe Bottom K
```

默认：Bottom20。

---

## 4. 每条事件记录字段

每条事件是一行：

```text
event_date
symbol
tags
ret_1d
ret_3d
ret_5d
carry_raw
funding_rate_sum
funding_count
funding_interval_est_hours
funding_per_hour_est
listing_days
trail_quote_volume_30d
fwd_ret_1d / 3d / 5d / 10d
fwd_funding_sum_1d / 3d / 5d / 10d
long_total_ret_1d / 3d / 5d / 10d
short_total_ret_1d / 3d / 5d / 10d
mae_long_5d / mfe_long_5d
mae_short_5d / mfe_short_5d
```

解释：

- `long_total_ret`：价格收益 - 持有期间 funding sum。因为正 funding 是多头付空头。
- `short_total_ret`：做空价格收益 + 收到的 funding sum。
- `mae/mfe`：只用日收盘路径估计，不是精确盘口/日内风险。

---

## 5. 第一版输出

脚本：

```text
scripts/build_binance_daily_event_study.py
```

输出：

```text
reports/artifacts/binance_daily_event_study_v0/events_v0.csv
reports/artifacts/binance_daily_event_study_v0/summary_by_tag_v0.csv
reports/artifacts/binance_daily_event_study_v0/combo_summary_v0.csv
reports/artifacts/binance_daily_event_study_v0/yearly_summary_v0.csv
reports/artifacts/binance_daily_event_study_v0/manifest_v0.json
```

---

## 6. 解读规则

第一轮不训练模型，只看分布：

- 样本数是否足够；
- 未来收益均值/中位数；
- win rate；
- MAE 是否过大；
- 年度是否稳定；
- 加 funding 后多空哪边更真实；
- 组合标签是否明显优于单标签。

如果没有组合标签比单标签明显更强，就不要急着做 live radar。先继续改事件定义。
