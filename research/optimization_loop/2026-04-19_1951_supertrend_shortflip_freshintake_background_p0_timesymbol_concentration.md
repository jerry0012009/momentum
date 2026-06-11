# 2026-04-19 19:51 UTC — supertrend short-flip fresh intake -> background/P0

## 执行小点
- target: `research/quant_digests/2026-04-19_0446_supertrend-volgate-shortflip-router-alpha.md`
- action: fresh intake first verdict
- success_criterion: 直接输出 `keep_P1` 或 `background/P0`

## 本轮最小检查
只补 1 条最小 honesty / execution-realism blocker：检查 digest 中看起来最像 pocket 的 `15m top1 short`，是否其实依赖单一时间段或少数币种硬撑。

使用产物：
- `reports/artifacts/quant_digests/2026-04-19_supertrend_flip_router_summary.csv`
- `reports/artifacts/quant_digests/2026-04-19_supertrend_flip_15m_events.csv`

## 关键结果
### digest 已给出的表面 pocket
- `15m top1 short`: `n=237`
- `gross≈+9.17bps/trade`
- `net8≈+1.17bps/trade`
- `median gross≈+1.78bps`
- 但 `median net≈-6.22bps`

这已经说明它不是厚 pocket，而是均值靠右尾支撑。

### 本轮最小复核：short-only top1
对 `15m` 所有 short 事件按同一时间戳只保留 score 最高的一档，得到：
- `n=330`
- `gross≈+7.64bps/trade`
- `net8≈-0.36bps/trade`

说明一旦把“只在 mixed top1 router 里挑出 short”换成更直接、更诚实的 short-only top1 读法，费后已经不再为正。

### 月份拆分
- `2026-02`: `n=59`, `net8≈+56.52bps/trade`
- `2026-03`: `n=172`, `net8≈-11.05bps/trade`
- `2026-04`: `n=99`, `net8≈-15.68bps/trade`

正边际几乎全部来自 `2026-02`，最近两个月已经转负，不满足“非单一时间片硬撑”的 fresh intake 保留标准。

### 币种拆分（short-only top1）
费后主要贡献集中在少数 alt：
- `AVAXUSDT`: `n=42`, `net8≈+27.96bps`
- `LTCUSDT`: `n=37`, `net8≈+16.66bps`
- `XRPUSDT`: `n=33`, `net8≈+13.64bps`
- `DOGEUSDT`: `n=32`, `net8≈+5.65bps`
- `ADAUSDT`: `n=30`, `net8≈+5.19bps`

而几个核心大币为负：
- `BTCUSDT`: `n=37`, `net8≈-21.09bps`
- `ETHUSDT`: `n=25`, `net8≈-29.83bps`
- `SOLUSDT`: `n=35`, `net8≈-28.86bps`
- `LINKUSDT`: `n=19`, `net8≈-12.27bps`

这说明可见 alpha 更像少数 alt / 少数时期的薄 pocket，而不是已可独立承接的稳健 `ATR trend flip short router`。

## 结论
`ATR-adjusted trend flip × vol gate × strongest short flip router` 的 first verdict 已诚实收口：`15m top1 short` 表面仅薄正且 median 为负，short-only top1 复核与月份/币种拆分显示 `2026-03/04` 已转负、正收益集中在 `2026-02` 与 AVAX/LTC/XRP 等少数 alt，因此当前不足以作为 survivor 保留，本轮直接记为 `background/P0`。
