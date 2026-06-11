# Rank 425 survivor follow-up — background/P0

- 时间：2026-04-19 16:11 UTC
- 对象：`Rank 425 / EMA fair-value dislocation × non-panicked TSV flow fade`
- 结论：`background/P0`

## 本轮只回答的唯一问题
`15m alt-proxy long fade + tsv_z>=0` 这条 survivor pocket，在跨资产、时间切片与最小执行真实性下，是否已经足够接近 `P2 admission`，还是应因样本稀疏 / 单段集中而直接收口。

## 使用证据
来源：`reports/artifacts/quant_digests/2026-04-19_tsv_ema_fv_fade_15m_events.csv`

筛选口径：
- `interval=15m`
- `bucket=alt_proxy`
- `side=long`
- `tsv_z>=0`

得到：
- 总样本：`n=64`
- 全样本 `gross=+13.50bps`
- 统一 `8bps` 后约 `net=+5.50bps`

### 跨资产拆分
- `ADAUSDT`: `n=6`, `gross=+8.95bps`
- `AVAXUSDT`: `n=7`, `gross=+25.23bps`
- `DOGEUSDT`: `n=9`, `gross=-4.24bps`
- `LINKUSDT`: `n=15`, `gross=+28.71bps`
- `LTCUSDT`: `n=16`, `gross=+9.06bps`
- `XRPUSDT`: `n=11`, `gross=+8.75bps`

表面上不是单一币孤立样本；`6` 个 alt 中 `5` 个均值为正。但 pocket 对 `LINK` 的依赖明显：
- 去掉 `LINK` 后：`n=49`, `gross=+8.84bps`, `net8≈+0.84bps`

### 时间切片 / 稳定性
顺序拆成两半：
- 前半：`n=32`, `gross=+11.82bps`, `net8≈+3.82bps`
- 后半：`n=32`, `gross=+15.18bps`, `net8≈+7.18bps`

按月份拆分：
- `2026-02`: `n=20`, `gross=+13.06bps`, `net8≈+5.06bps`
- `2026-03`: `n=34`, `gross=+19.24bps`, `net8≈+11.24bps`
- `2026-04`: `n=10`, `gross=-5.14bps`, `net8≈-13.14bps`

这说明 pocket 不是稳定地“每个时期都能做”，至少在最近月份已经明显失效。

### 集中度 / 单段依赖
- 最好单日：`2026-03-17`，`n=3`，总贡献约 `+235.53bps`
- 该单日占全部毛收益贡献约 `27.3%`
- 去掉最好单日后：`n=61`, `gross=+10.30bps`, `net8≈+2.30bps`

再看小时段（仅统计 `n>=3`）：
- 明显为正：`02 / 06 / 10 / 15 / 17`
- 明显为负：`03 / 04 / 08 / 11 / 14 / 16`

因此它不是一个已经能把 blocker 收敛成“只差 execution shell”或“只差一个单一 admission 问题”的 pocket；相反，它同时暴露出：
1. 最近月份失效；
2. 时段分布不稳；
3. 对 `LINK` 与少数好日子贡献较敏感。

## 诚实收口
`Rank 425` 的 first verdict 保留下来的 survivor pocket，确实不是纯幻觉；但这次唯一 follow-up 已经回答了更关键的问题：它**还不够接近 `P2 admission`**。

问题不是“只差再补一层 child execution 就能上 P2”，而是 pocket 自身仍有多重未闭合的不稳定性：
- 最近月份不能持续；
- 去掉强势符号 / 最好日期后净边际明显变薄；
- 不同时间切片下结论分裂。

按 policy，survivor 只允许这一次最小 follow-up。既然这一步没有把对象推进到接近 `P2`，就应直接收口，而不是继续拖长。

## runtime impact
- `Rank 425` 从 `Surviving candidate slot` 收口至 `Background pool`
- `Surviving candidate slot` 清空
- 本轮 cycle item 1 记为 `done`

## 一句话结果
`Rank 425` 的 survivor 唯一 follow-up 已诚实收口：`15m alt-proxy long fade + tsv_z>=0` 虽有全样本 `net8≈+5.5bps`，但 `2026-04` 已转负、去掉 `LINK` 仅余 `net8≈+0.84bps`、且对少数好日子贡献敏感，不足以收敛为单一 P2 admission blocker，因此本轮直接转入 `background/P0`。
