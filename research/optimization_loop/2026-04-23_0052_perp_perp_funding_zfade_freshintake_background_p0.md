# cross-venue perp-perp funding spread z-score fade × child execution — fresh intake background/P0

- time: `2026-04-23 00:52 UTC`
- target: `research/quant_digests/2026-04-22_0958_perp-perp-funding-diff-zfade-shell.md`
- action: `fresh intake first verdict`
- success_criterion: `必须直接输出 keep_P1 或 background/P0；只有当多阈值 funding-spread 事件在最小 maker/taker 成本梯度与跨标的 distinctness 下仍保住独立 after-cost pocket，才 keep_P1`

## 本轮最小 decisive blocker
这轮不再重复扩大数据工程，只做一个最便宜、最会改变结论的诚实检查：

1. 复核 digest 已产出的公开 funding portability 结果，确认 `BTC/ETH` 在最近 `200` 个 8h 点上是否存在足够厚、足够频繁的 funding-spread 事件；
2. 对照当前研究池与已 live 家族，判断这条对象是否真的带来了可独立排队的新增 after-cost alpha，而不是仅把旧的 cross-venue funding carry / pairs execution 经验换了个更完整的 child-execution 说法。

## 观察
### 1) 事件密度与厚度仍不支持独立 alpha 排队
来自 `reports/artifacts/quant_digests/perp_perp_funding_diff_probe_20260422/summary.txt` 与 `threshold_sweep.csv`：

- `BTCUSDT` 最近 `200` 个 8h funding 点：
  - `mean abs spread ≈ 0.377 bps/8h`
  - `p95 ≈ 0.897 bps/8h`
  - `max ≈ 1.473 bps/8h`
  - repo 默认 `2 bps + |z|>=2` 触发数 `0`
- `ETHUSDT` 最近 `200` 个 8h funding 点：
  - `mean abs spread ≈ 0.388 bps/8h`
  - `p95 ≈ 0.978 bps/8h`
  - `max ≈ 1.570 bps/8h`
  - repo 默认 `2 bps + |z|>=2` 触发数 `0`

把门槛降到 `0.5~1.0 bps` 虽会出现少量事件，但样本仍很稀：

- `BTC`: `7` 次 (`0.5bps`), `4` 次 (`1.0bps`)
- `ETH`: `11` 次 (`0.5bps`), `6` 次 (`1.0bps`)

而且这些数字还只是 funding spread 收敛，不是双腿真实成交后的净值。对 same-underlier perp-perp 结构来说，只要进入 `maker-taker` 或 `taker-taker`，这类 `sub-1bp` 级别 spread 很容易被手续费、补腿滑点、timestamp mismatch 与 collateral fragmentation 吃掉。也就是说，本对象当前连“最小 after-cost pocket 已存在”都没有证明出来。

### 2) 它对当前系统的新增价值主要退化为 execution / regime 组件提示
检索现有研究池后，这条线与以下已覆盖家族高度重叠：

- 旧的 `cross-venue funding carry` / `perp-perp funding diff` / `net-EV hurdle` 家族（例如 `2026-03-30_1919_perp-perp-funding-diff-nethurdle-alpha.md`、`2026-04-02_1734_feecoverage-gated-crossvenue-funding-carry-alpha.md`、`2026-04-15_2326_cexdex-fundingspread-shockreversion-alpha.md`）；
- 已 live 的 pairs / relative-value 队列（`Rank 424`, `Rank 431`）已经覆盖了“必须经过 admission、maker-first / hard timeout、不能靠单次 lucky pocket”这类更强的现实性标准。

因此，本 digest 这次真正新增的不是一个已被证明能独立过成本的 front-slot alpha，而是：

- funding-spread alpha 必须低频稀疏地看；
- 必须用 child execution / maker-first honesty 去筛；
- 若未来要复用，更像 `funding-regime router` 或 `execution realism checklist`。

这属于有价值的 deployment / admission 组件提示，但还不足以作为新的 `keep_P1` 对象继续占用前排预算。

## verdict
> `cross-venue perp-perp funding spread z-score fade × child execution` 的 fresh intake first verdict 已诚实收口 `background/P0`：最近公开 `BTC/ETH` funding portability 下，默认阈值零触发、降阈值后也只剩少量 `0.5~1.0bps` 级稀疏事件，尚未证明在最小 maker/taker 成本梯度与双腿现实 friction 下存在可独立排队的 after-cost pocket；同时它相对现有 cross-venue funding carry / pairs RV 家族没有拿出新的 durable venue-asset sleeve，新增价值主要退化为 `funding-regime router / child-execution honesty` 组件提示，因此不进入 survivor，直接并回 background/P0。

## runtime effects
- 当前对象不分配 rank。
- `Fresh intake slot` 应切到下一条仍未消费的 fresh intake：`research/quant_digests/2026-04-22_0429_us-close-midcap-reversal-alpha.md`。
- 本轮只完成当前 front pending 小点，不改写其他 pending 排序。

## tail step status
- homepage publish (`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`) 在异步执行阶段收到 `SIGKILL` 失败。
- 按 policy 归类为非阻断尾部失败：不回滚本轮 `verdict/state/log`。
- 邮件通知已独立执行并成功发送（`[momentum-bot3-auto] funding spread zfade收口P0`）。
