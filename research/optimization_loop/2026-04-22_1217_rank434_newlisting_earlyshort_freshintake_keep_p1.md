# Rank 434 / newlisting early-short bubble fade fresh intake -> keep_P1

- 时间：2026-04-22 12:17 UTC
- 对象：`newlisting early-short bubble fade`（source：`research/quant_digests/2026-04-22_1115_newlisting-early-short-bubblefade-shell.md`）
- 本轮动作：fresh intake first verdict
- 结论：`keep_P1`
- Rank：`434`

## 这轮只回答的唯一 blocker

按 cycle_plan，本轮只补 1 个最小 decisive blocker：这条 `新上币早期泡沫高点 × funding-positive short fade` 是否只是 2025 单批次幸运样本，还是在更诚实的上市批次分段、持仓现实与最小执行/摩擦约束下，仍保留足够独立的 after-cost event alpha，值得至少进入 survivor。

## 使用的最小证据

直接复用 digest 已生成 artifact：

- `reports/artifacts/quant_digests/newlisting_short_15m_trades_2026-04-22.csv`
- `reports/artifacts/quant_digests/newlisting_short_15m_summary_2026-04-22.csv`

聚焦 short-cycle desk 变体 `desk_8tp5sl3d`：

- `239` 笔交易
- 平均 `net_pct ≈ +0.7617%/trade`
- 胜率 `≈49.37%`
- 平均持仓 `≈0.348d`

然后只做两件 honesty/realism 检查：

1. **按入场月份分段**，确认不是完全靠单一 listing batch/单一月硬撑；
2. **把 roundtrip 成本再抬高**（在 digest 粗扣 `8bps` 基础上再加 `20/50/100bps`），确认边际对更保守 friction 的耐受度。

## 结果

### 1) 批次 / 月份分段

`desk_8tp5sl3d` 按入场月份：

- `2025-01`: `86` 笔，`avg_net_pct ≈ +1.83%`，`sum_net_pct ≈ +156.97%`
- `2025-02`: `119` 笔，`avg_net_pct ≈ +0.49%`，`sum_net_pct ≈ +58.67%`
- `2025-03`: `34` 笔，`avg_net_pct ≈ -0.99%`，`sum_net_pct ≈ -33.61%`

解释：这条线**不是只靠单一上市批次/单一月份才存在**，因为至少 `2025-01` 与 `2025-02` 两个独立月份都保留正 after-cost 结果；但它也**明显带有 regime 衰减**，`2025-03` 已转负，所以当前还不能直接升 `P2`。

### 2) 单币集中度

按 symbol 汇总后：

- `27` 个有交易 symbol 中，`18` 个为正贡献
- 但 top5（`GPSUSDT / SOLVUSDT / BIOUSDT / COOKIEUSDT / ARCUSDT`）贡献了约 `79.3%` 的总净收益

解释：它并非纯单币 lucky run，因为正贡献覆盖 `18/27` 个 symbol；但集中度偏高，说明 survivor 下一步应优先查 **listing cohort / liquidity tier / child execution realism**，而不是直接把当前结果当成可 paper 的稳定普适 alpha。

### 3) 更保守摩擦梯度

在现有 `8bps` 基础上额外抬高 roundtrip 成本：

- `+20bps`：平均 `net_pct ≈ +0.56%/trade`
- `+50bps`：平均 `net_pct ≈ +0.26%/trade`
- `+100bps`：平均 `net_pct ≈ -0.24%/trade`

解释：这条线对成本并非无限脆弱；在比 digest 更保守得多的 `+20/+50bps` 额外摩擦下仍为正，但到 `+100bps` 才整体翻负。对于“新上币事件型 short sleeve”来说，这足以支持 `keep_P1`，但也说明 survivor 应优先验证更真实的 early-listing 执行/流动性门槛，而不是默认当成已闭合的 desk-ready alpha。

## 本轮 verdict

`Rank 434 / newlisting early-short bubble fade` 通过 fresh intake first verdict，进入 `keep_P1`：它在更诚实的上市月份分段下至少有 `2025-01/02` 两个独立正批次，且在比 digest 更保守的额外 `+20/+50bps` roundtrip 摩擦下仍保留正 after-cost 边际；虽然 `2025-03` 已转负且 top5 symbol 贡献约 `79%` 显示 regime/集中度风险仍在，但这已经足以证明它不是单一幸运批次幻觉，值得保留 1 次 survivor follow-up。

## 对 runtime 的直接影响

- 分配新正式 Rank：`434`
- 当前对象从 `Fresh intake slot` 升为 `Surviving candidate slot`
- `followup_budget_remaining = 1`
- 不进入 `P2`；原因是 regime decay（`2025-03` 已转负）与 top5 集中度偏高尚未闭合
