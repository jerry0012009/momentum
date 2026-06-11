# intraday mom/reversal regime switch fresh intake -> background/P0

- 时间：2026-04-21 23:54 UTC
- 对象：`research/quant_digests/2026-04-21_2332_intraday-momrev-regimeswitch-alpha.md`
- 轮次动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮只做的最小 decisive blocker
直接用 Binance USDⓈ-M 公共 `5m` K 线，对 `BTCUSDT / ETHUSDT / SOLUSDT` 近约 `120d` 做统一口径快检：

- `r_past`: 最近 `15m` 收益（`t-3 -> t`）
- `r_future`: 未来 `20m` 收益（`t -> t+4`）
- `jump_flag`: 当前 `1bar abs(ret)` > 过去 `60` 根的 rolling `p90`
- `low_liq_flag`: 当前 `quote_volume` < 过去 `60` 根的 rolling `p10`
- `stress regime = jump OR low_liq`
- 三套对照：
  1. `always momentum`: 顺 `sign(r_past)`
  2. `always reversal`: 反 `sign(r_past)`
  3. `state-routed hybrid`: `normal` 用 momentum，`stress` 用 reversal
- 成本：统一粗扣 `8bps roundtrip`

## 结果摘要
### BTCUSDT
- `always momentum`: `mean net ≈ -8.57bps/trade`
- `always reversal`: `mean net ≈ -7.43bps/trade`
- `hybrid`: `mean net ≈ -8.30bps/trade`
- `stress bars`: `8244`，`normal bars`: `26291`

### ETHUSDT
- `always momentum`: `mean net ≈ -8.64bps/trade`
- `always reversal`: `mean net ≈ -7.36bps/trade`
- `hybrid`: `mean net ≈ -8.34bps/trade`
- `stress bars`: `8137`，`normal bars`: `26398`

### SOLUSDT
- `always momentum`: `mean net ≈ -8.95bps/trade`
- `always reversal`: `mean net ≈ -7.05bps/trade`
- `hybrid`: `mean net ≈ -8.53bps/trade`
- `stress bars`: `8106`，`normal bars`: `26429`

## 为什么这一步已经足够决定 first verdict
进一步看 gross 分层，`normal` 与 `stress` 并没有出现论文想要的“同一 recent-return 信号被 router 真正分流成 continuation vs reversal”的结构：

- BTC：`normal` 下 momentum gross `≈ -0.57bps`，stress 下 momentum gross `≈ -0.58bps`；两边都更接近薄 reversal，而不是正常时 continuation、异常时 reversal
- ETH：`normal` 下 momentum gross `≈ -0.65bps`，stress 下 momentum gross `≈ -0.63bps`
- SOL：`normal` 下 momentum gross `≈ -0.97bps`，stress 下 momentum gross `≈ -0.89bps`

也就是说：

1. `state-routed hybrid` 没有在统一成本后优于 `always momentum` 与 `always reversal`；
2. `normal` 与 `stress` 两个 regime 的方向并没有被分开，反而都只留下极薄、几乎同号的 reversal 倾向；
3. 这点薄 gross 远低于 desk 最小现实摩擦，且没有形成“至少两个非单一币/单窗支撑的 after-cost pocket”。

## verdict
`recent-return continuation × jump/liquidity/event regime switch` 这条 fresh intake first verdict 诚实收口 `background/P0`：当前最小公开复核里，`jump + low-liquidity` router 没有把 `BTC/ETH/SOL 5m` 的 recent-return 信号分流成“正常 continuation / 异常 reversal”的独立 after-cost alpha，反而 normal 与 stress 两边都只剩同号、极薄且费后显著为负的 reversal 倾向；因此它更适合作为“别默认裸 momentum”的研究提醒，而不是值得保留 survivor 的新 front object。

## tail execution status
- homepage publish (`bash scripts/publish_homepage_index.sh`)：异步进程最终 `SIGKILL`（非阻断尾部失败；不影响本轮 verdict/state/log 生效）。
- email notify (`send_text_email.py`)：发送成功。
