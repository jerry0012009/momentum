# Step 1 Binance Daily Event Study v0 — 第一轮发现

> Generated: 2026-05-10  
> Script: `scripts/build_binance_daily_event_study.py`  
> Input: `/root/clawd/jerry/momentum/reports/artifacts/rank154_long_history/daily_panel.pkl`  
> Output dir: `reports/artifacts/binance_daily_event_study_v0/`

---

## 1. 样本与验证

- 样本行数：99,654 events
- 日期范围：2021-10-29 到 2026-04-30
- symbol 数：442
- 每日 universe：历史当日 `trail_quote_volume_30d` Top100，且 `is_eligible=True`、`listing_days>=30`
- 每日事件：
  - `top_gainer_1d`：当日涨幅 Top20
  - `top_loser_1d`：当日跌幅 Bottom20
  - `funding_extreme_positive`：小时归一 funding Top20
  - `funding_extreme_negative`：小时归一 funding Bottom20
- 已修正并验证：
  - 没有同时 high funding + negative funding 的不可能标签；
  - 没有同时 top gainer + top loser 的不可能标签；
  - forward funding 使用 t+1...t+h 真实未来区间求和，避免 rolling 写法混入过去行。

---

## 2. 单标签结果

核心口径：`price_5d_mean` 是事件后 5 天价格收益；`long_total_5d_mean` = 价格收益 - 持有期 funding；`short_total_5d_mean` = -价格收益 + 持有期 funding。

```text
tag                         events   price_5d_mean   price_10d_mean   long_total_5d   short_total_5d   short_5d_win
funding_extreme_negative     30469       -0.50%          -0.95%           +0.09%          -0.09%          54.44%
funding_extreme_positive     32860       -0.28%          -0.66%           -0.39%          +0.39%          55.32%
top_gainer_1d                32860       -0.54%          -0.91%           -0.39%          +0.39%          55.91%
top_loser_1d                 32860       -0.46%          -0.90%           -0.31%          +0.31%          54.98%
```

第一眼结论：

1. 这批日线事件整体不是“追涨 continuation”，更像事件后 5-10 天有系统性回落/负漂移。
2. 单纯高正 funding 后，价格不是继续涨，反而 5d/10d 均值为负；做空端含 funding 后更好。
3. 单纯低/负 funding 后，价格也偏负，但因为负 funding 对多头有利，long_total 被 funding 拉到接近 0。
4. `top_gainer_1d` 不是追涨信号；粗看更像之后短空/回落信号。

---

## 3. 组合标签结果

按 5d price return 排序：

```text
combo                                      events   price_5d   price_10d   long_total_5d   short_total_5d   5d win(price>0)   median MAE long 5d
negative funding + top_loser                7411    -0.62%     -1.26%        +0.22%          -0.22%          42.58%            -5.28%
negative funding + top_gainer               7493    -0.59%     -1.05%        +0.32%          -0.32%          41.79%            -5.75%
top_loser only                             18450    -0.56%     -0.94%        -0.61%          +0.61%          45.25%            -4.62%
top_gainer only                            17875    -0.55%     -0.82%        -0.60%          +0.60%          44.24%            -4.81%
positive funding + top_gainer               7492    -0.46%     -0.97%        -0.59%          +0.59%          43.79%            -5.49%
positive funding + top_loser                6999    -0.01%     -0.43%        -0.11%          +0.11%          44.77%            -5.14%
```

更具体的判断：

- `top_gainer + high positive funding` 没有表现成“拥挤继续冲”，而是事件后 5d 平均 -0.46%，做空加 funding 约 +0.59%。
- `top_gainer + negative funding` 反而更差，5d -0.59%，但这里多头能收 funding，所以 long_total 变成 +0.32%。这类更像“价格回落但 funding 补贴多头”，不是干净方向 alpha。
- `top_loser + positive funding` 是最不差的组合，5d 基本持平。这可能意味着：大跌但 funding 仍高的币，空头 edge 不明显，甚至有 squeeze/承接风险。
- 所有组合的 5d close-path MAE 中位数约 -4.6% 到 -5.8%，风险不薄；注意这是日收盘路径，真实日内 MAE 会更大。

---

## 4. 年度稳定性

全事件聚合年度：

```text
year   events   price_5d_mean   5d win   short_total_5d
2021    3714      -1.24%        38.96%      +1.34%
2022   22495      -1.76%        42.50%      +1.64%
2023   22128      +1.13%        50.15%      -1.16%
2024   22353      +0.63%        48.80%      -0.50%
2025   22052      -1.32%        39.89%      +1.03%
2026    6912      -1.56%        38.72%      +0.68%
```

这说明：

- 2021/2022/2025/2026 明显偏事件后回落；
- 2023/2024 偏反向，事件后继续上涨/市场 beta 更强；
- 所以不能直接拿全样本均值上 live，必须加 regime filter 或改为“事件候选 + 二级筛选”。

---

## 5. 当前可执行结论

我不建议基于 v0 直接做 live。v0 的价值是把大方向缩小了：

1. **不要优先追涨。** 日线 top gainer 在这个历史口径下没有给出追涨 edge。
2. **高 funding 更像拥挤风险，不像 continuation。** 高正 funding 后做空端比做多端更像有收益，但收益厚度还不够覆盖小币滑点/爆拉风险。
3. **单事件不够，下一步要做条件化。** 必须把事件再拆：年龄、成交额分层、涨幅大小分层、是否新高、是否连续多日上涨、funding 分位、市场 regime。
4. **控盘币机会可能存在，但不是“涨跌榜前列就上”。** 日线榜单只能给候选，真正的机会大概率在二级形态：比如连续拉盘后 funding 过热、成交额异常、但价格开始失速。

---

## 6. 下一步建议 v1

优先做三件小事：

1. **事件分桶**：
   - listing age：30-90d、90-180d、180-365d、1y+
   - 当日涨跌幅：Top20 里再按幅度分桶
   - funding_per_hour 分位：Top5/Top10/Top20，而不是只 Top20

2. **加入形态过滤**：
   - 是否接近 20d high；
   - 前 3d 是否连续上涨；
   - 当日是否放量；
   - 事件后第 1 天是否失速，作为进入做空/回落的确认。

3. **把日线升级到小时线/分钟线的局部样本**：
   - 不必全市场多年小时线；
   - 先只下载 v0 里最典型的 200-500 个事件的 1h/1m K 线；
   - 看入场时点、日内 MAE、止损是否现实。

我的倾向：Step 1.1 不做大规模 IC mining，先围绕 `top_gainer/high funding/event reversal` 这条线做条件化事件研究，因为它最贴近你说的“控盘币/榜单币”方向，也最容易变成 radar。
