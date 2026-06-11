# bot3 执行日志（survivor follow-up）
- 时间：2026-04-12 17:58 UTC
- 执行槽位：Surviving candidate slot
- 对象：`Rank 391 / BTC dominance slope × strongest/weakest alt switch`
- 对应小点：`cycle_plan #1`

## 本轮执行小点
执行 survivor 唯一一次 follow-up：围绕已锁定 `成本后边际不足`，补最小 execution realism 核验（手续费阶梯 + 可成交容量），并给出出口决策。

## 证据（最小、可改变结论）
1. 读取既有 selected config 明细（`reports/artifacts/literature/btc_dominance_rotation_probe_2026-04-12_selected_config_detail.csv`）：
   - 全样本 `sum(turnover_x)=326.0`
   - `gross_cum=+4.83%`
   - 对应近似 break-even one-way 成本：`4.83% / 326 * 10,000 ≈ 1.48 bps`
   - 与上一轮 `1bp 仍正 / 2bp 转负` 结果一致，说明该策略确属“低成本阈值附近可行”。
2. 可成交容量（最小代理）：拉取 Binance USDⓈ-M 近 1000 根 `15m` quote volume，取 `p10` 保守口径：
   - BTC `~22.2M USDT/15m`，ETH `~18.3M`，SOL `~4.44M`，XRP `~1.73M`，DOGE `~1.38M`，BNB `~0.96M`
3. 结合该配置 `avg_turnover_x=0.01755/bar`、`rebalance=24 bars`（6h）可得每次调仓约 `0.42x NAV`；按 `1M USDT` 纸组合估算，单次总成交约 `420k`，分摊到四腿约 `~105k/腿`，对上述 `p10` 15m 成交额参与率约 `0.47%~10.9%`（最差 BNB），在 paper 阶段可执行。

## 出口决策
`Rank 391`：`promote_P2`。

## 决策理由（一句话）
该策略在可实现的低成本执行区间（约 `<=1.5bps one-way`）仍保留正费后边际，且 6h 慢换仓下的成交参与率在主流永续品种上可控，因此不再停留 P1，进入 P2 admission。

## 备注
- 本轮已用尽 survivor 的唯一 follow-up 预算；对象升级后由 `Active P2` 槽位继续 admission。
- 若后续 P2 检验显示实际可实现费用长期高于 break-even（`~1.5bps`）或容量受限，应直接执行 `P2 exit`，不回到开放式 P1。