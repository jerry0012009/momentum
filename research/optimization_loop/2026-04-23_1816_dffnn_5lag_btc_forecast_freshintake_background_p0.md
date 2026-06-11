# DFFNN 5lag BTC forecast fresh intake -> background/P0
- 时间：2026-04-23 18:16 UTC
- 对象：`research/quant_digests/2026-04-23_1428_dffnn-5lag-btc-forecast-alpha.md`
- 动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮最小 decisive blocker
把论文里的「最近 5 根 5m 价格 -> 下一根价格预测」压成最小诚实交易复刻后，它没有留下可独立排队的 after-cost forecast-to-trade pocket；留下的是一个接近零信息含量的 forecasting baseline，而不是可交易 raw alpha。

## 最小复刻方法
- 数据：`BTCUSDT__365d__5m__perp.csv`
- walk-forward：90d 训练 + 30d 测试滚动
- 特征：最近 5 根 `5m` 收益率 lag（对原论文 5-lag price 的数值稳定替代）
- 模型：`LinearRegression` / `Ridge(alpha=1)` / `MLPRegressor(16x16)`
- 交易化：预测未来 `1/2/3` 根收益；阈值 `2/4/6/8 bps`；成本 `4/8 bps`
- artifact：`reports/artifacts/dffnn_5lag_btc_forecast_first_verdict/summary_metrics.csv`

## 关键结果
### 1) 预测层本身几乎没有可用信息量
- linear: hold1/2/3 相关系数分别 `-0.0040 / -0.0046 / -0.0023`
- ridge: hold1/2/3 相关系数分别 `+0.0004 / +0.0008 / +0.0019`
- mlp: hold1/2/3 相关系数分别 `-0.0001 / +0.0009 / -0.0050`

这些值都贴近 `0`，说明近一年 BTC perp 的 5-lag 价格路径对下一根 5m 可交易收益几乎没有稳定可抽取的预测力。

### 2) 阈值化后没有稳健 after-cost pocket
- `linear / hold1 / th=2bps / cost=4bps`: `1484` 笔，`avg net = -4.39 bps/笔`
- `linear / hold2 / th=8bps / cost=4bps`: `49` 笔，`avg net = -0.49 bps/笔`
- `mlp / hold2 / th=6bps / cost=4bps`: `11617` 笔，`avg net = -3.73 bps/笔`
- `ridge` 在 `2~8bps` 全阈值下都几乎不给出交易，说明信号幅度本身就不足以跨过现实摩擦门槛。

### 3) 仅存的正数 pocket 都是小样本 lucky-run，不满足 keep_P1
表面上最好的两个组合：
- `linear / hold1 / th=4bps / cost=4bps`: `185` 笔，`avg net = +1.69 bps/笔`
- `linear / hold3 / th=8bps / cost=4bps`: `34` 笔，`avg net = +4.63 bps/笔`

但它们都被单月集中度击穿：
- `hold1 / th4 / cost4` 的主要盈利几乎全来自 `2025-10`(`+466 bps`) 与 `2026-02`(`+312 bps`)，而 `2025-11`/`2025-12` 已转负；
- `hold3 / th8 / cost4` 只有 `34` 笔，其中 `14` 笔盈利集中在 `2025-10`，`2025-11` 与 `2025-12` 已不稳，成本升到 `8bps` 后只剩 `+0.63 bps/笔` 的薄边际。

因此，这些正数更像稀疏高阈值 lucky window，而不是非单月份、可独立排队的 forecast-to-trade pocket。

## verdict
`DFFNN 5lag BTC forecast` 完成 fresh intake first verdict：近一年 BTC 5m perp walk-forward 下，5-lag 价格预测基线的预测相关性近乎为零，阈值化后只有少量单月集中 lucky-run 正数，未留下非单模型幸运窗、非单月份 lucky-run 的 after-cost tradable pocket，因此收口 `background/P0`，只保留为 forecasting baseline 参考，不进入 survivor。
