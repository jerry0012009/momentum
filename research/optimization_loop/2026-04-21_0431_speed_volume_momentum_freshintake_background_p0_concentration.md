# speed-volume momentum fresh intake -> background/P0

- 时间：2026-04-21 04:31 UTC
- 对象：`价格涨速 + 成交量放大 × mid-vol regime continuation`
- 类型：fresh intake first verdict
- 结论：`background/P0`

## 本轮执行的小点
按 `cycle_plan` 第 3 项，对 `research/quant_digests/2026-04-20_1856_speed-volume-momentum-shell-alpha.md` 做 fresh intake first verdict；只补 1 个最小 decisive blocker：统一 `8bps` 与 recent 月份切片后，检查 digest 中 `mid-vol` pocket 是否仍不是少数大波段/少数事件驱动，并比较 `strongest_only` 是否明确劣于受控 `mid-vol` admission。

## 读取到的现成 artifact
- `reports/artifacts/quant_digests/2026-04-20_dynamic_speed_volume_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-20_dynamic_speed_volume_probe_events.csv`

## 最小 honesty / decisive blocker 复核
### 1) strongest_only 明显劣于 mid-vol admission
summary 已给出：
- `strongest_only`：`n=123`，`3/6/12 bars ≈ -7.21 / -7.03 / -11.89 bps gross`
- 统一按 round-trip `8bps` 后，对应约 `net8 ≈ -15.21 / -15.03 / -19.89 bps`

这说明“涨得最快的一档继续追”本身不是 pocket；digest 里最像样的只剩 `mid-vol` 受控 admission。

### 2) mid-vol pocket 统一 `8bps` 后虽然表面仍正，但只存在于单月单批事件
从 events 复核：
- `mid-vol` 全部只有 `23` 个事件，且 **全部集中在 `2026-02`**；最近没有 `2026-03/04` 的可复现样本
- `fwd_6 gross ≈ +130.55bps`，扣 `8bps` 后 `net8 ≈ +122.55bps`
- 但 `fwd_6` 的 `median net8 ≈ -24.87bps`，`win rate ≈ 47.8%`

也就是说，均值并不是由广谱稳定的小正收益支撑，而是被少数大赢家拉起来。

### 3) 去掉少数最好日期后，mid-vol 立刻翻成明显负值
按 `fwd_6 net8` 聚合到交易日后：
- top1 day 贡献占总净收益约 `147.9%`
- top3 day 基本吃掉全部正收益（mid-vol 总共也只分布在 3 个交易日）
- 去掉 top1 day 后：剩余 `14` 个事件，`avg net8 ≈ -96.39bps`
- 去掉 top2 day 后：剩余 `13` 个事件，`avg net8 ≈ -106.82bps`

这已经满足“少数大波段/少数事件驱动”的 blocker，不再是可前排保留的 continuation alpha。

## verdict
`价格涨速 + 成交量放大 × mid-vol regime continuation` 的 fresh intake first verdict 已诚实收口：`strongest_only` 在统一 `8bps` 下本身明显费后为负；表面最强的 `mid-vol` pocket 虽保留高均值，但全部 `23` 个样本只出现在单一 `2026-02` 月份，且 `fwd6` 的 `median net8≈-24.87bps`、去掉 top1 day 后 `avg net8≈-96.39bps`，说明收益主要由少数大波段/少数日期拉动，未通过“不是少数事件驱动”的 decisive blocker，因此本轮直接收口 `background/P0`。
