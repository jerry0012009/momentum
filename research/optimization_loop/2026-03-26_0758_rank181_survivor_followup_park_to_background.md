# Rank 181 / okx-deribit-near-expiry-call-spread-arb survivor follow-up -> park_to_background

- 时间：2026-03-26 07:58 UTC
- 对象：`Rank 181 / okx-deribit-near-expiry-call-spread-arb`
- 执行动作：survivor 唯一一次 cheap but decisive follow-up
- 结论：`park_to_background`

## 本轮只回答一个问题
`T-180m ~ T-30m` 结算前窗口里、`DTE<=7d` 且优先 `0~3d` 的 OKX-Deribit `same expiry / same strike / same option type` BTC call premium spread，是否已经显示出足以把 `Rank 181` 升到 `P2` 的稳定过成本 pocket？

答案：**没有。`Rank 181` 用完 survivor 预算后应收口为 `park_to_background`。**

## 这次收口依据
本轮可用的最小诚实证据来自前一轮 intake 已产出的共同合约 snapshot：

- artifact：`reports/artifacts/quant_digests/okx_deribit_near_expiry_call_arb_20260326/near_expiry_common_calls_snapshot.csv`
- summary：`reports/artifacts/quant_digests/okx_deribit_near_expiry_call_arb_20260326/snapshot_summary.csv`

关键事实只有三条：

1. `45` 个共同近到期 BTC call 合约里，`0` 个穿过双边 top-of-book 成本。
2. 全样本 `median |premium diff| = 2.3067%`，但 `median roundtrip spread = 15.1894%`，说明多数表面价差只是被 options 自身宽盘口放大。
3. 最接近目标 pocket 的 next-day / near-ATM 样本是 `2026-03-27 72000C`：
   - `premium diff = -8.6875%`
   - `roundtrip spread = 10.4347%`
   - `edge_minus_spread = -1.7472%`
   也就是即便落到 `DTE≈1d`、较接近 ATM 的 bucket，当前仍未穿过 top-of-book 成本。

## 为什么这一步不能升 P2
要让 survivor 升进 `P2`，至少要看到一个足够具体、值得继续 admission 的可交易 pocket。

但这次 follow-up 没有给出这样的 pocket：

- `0~3d` 没有出现明确过成本样本；
- near-ATM / slightly OTM bucket 也没证明自己能稳定覆盖双边 spread；
- 当前能说的仍只是“也许结算事件附近会更好”，而不是“已经找到值得 admission 的窄对象”。

这不满足 survivor 的“唯一一次便宜决定性检查”要求。继续保留只会把 `P1` 拖成长待观察，而不是改变系统认知。

## 为什么也不该硬升 P2 再看
`P2` 的默认任务是 admission，不是替 `P1` 补“也许有 pocket”的探索。若在尚未出现任何过成本 pocket 的情况下硬升：

- admission 会立刻卡在 `effectiveness / realism`；
- 后续大概率只是继续重复同一条 `DTE / liquidity / settlement-window` 维度；
- 这正是 policy 明确不鼓励的低杠杆拖延。

因此更诚实的处理是：**把 `Rank 181` 作为一条曾被看过、但未证明可交易 pocket 的 options cross-venue raw alpha 记入后台，而不是继续占用前排 survivor 槽位。**

## 对系统认知的更新
**Rank 181：唯一 survivor follow-up 已收口为 `park_to_background`；截至当前共同合约 snapshot，`DTE<=7d`、优先 `0~3d` 的 OKX-Deribit same-contract BTC call premium spread 仍未在结算前 pocket 内证明自己能稳定穿过 top-of-book 成本，因此不足以升入 `P2`。**
