# bot3 optimization loop log — 2026-04-13 19:48 UTC

## 执行小点
- target: `research/quant_digests/2026-04-13_1220_pseudoopen-pseudoclose-tsmom-alpha.md`
- action: fresh intake first-verdict（统一成本 + 最小 execution realism honesty 检查）

## 本轮最小证据
1. 读取原 digest 与 probe artifact：
   - `reports/artifacts/quant_digests/2026-04-13_pseudoopen_pseudoclose_tsmom_probe_metrics.csv`
   - `reports/artifacts/quant_digests/2026-04-13_pseudoopen_pseudoclose_tsmom_probe.py`
2. 成本口径（round-trip）快速重算：
   - gross bps/session：BTC `+3.33`，ETH `+4.90`，SOL `+5.02`
   - 扣 `6bps` 后：BTC `-2.67`，ETH `-1.10`，SOL `-0.98`
   - 扣 `8bps` 后三者均进一步为负
3. honesty / execution realism 子检查（最小）：
   - 代码中 `r_ONFH` 由 `prev_close -> open+30m` 历史 bar close 构造，交易段是 `close-30m -> close`，未见 future anchor / repaint 写法；
   - 但该骨架在当前样本下只有“成本前薄边际”，且跨资产 sign-hit 约 50% 附近、线性解释力弱（`p_onfh` 对三资产均不显著），不足以支撑可执行 alpha 继续前排占槽。

## 结论（改变系统认知）
`pseudoopen/pseudoclose tsmom` 在统一成本与最小执行真实度口径下判定为 **background/P0**：当前仅见成本前薄边际，费后（6bps 起）跨 BTC/ETH/SOL 全部转负，且没有形成可稳健迁移的有效性证据，不进入 `keep_P1`。

## 状态写回
- cycle_plan item 1: `status = done`
- cycle_plan item 1 result: 已写入本轮 fresh verdict（background/P0）
- Background pool `latest_parked`: 更新为本对象
