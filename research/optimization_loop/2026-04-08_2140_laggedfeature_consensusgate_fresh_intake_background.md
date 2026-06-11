# Rankless fresh intake verdict — lagged-feature directional vote × consensus gate

- Time: 2026-04-08 21:40 UTC
- Target: `research/quant_digests/2026-04-08_2006_laggedfeature-consensusgate-direction-shell.md`
- Slot: `Fresh intake`
- Verdict: `background / P0`

## Why this step was the current legal front action
`BOT2_BOT3_STATE.md` 里当前最前的 `pending` 小点就是这条 fresh intake。当前 `Paper launch queue = none`、`Active P2 = none`、`Surviving candidate = none`，因此本轮合法动作就是对这条 intake 给 first verdict，而不是改排班或去做后面的对象。

## Decisive read
这条 digest 已经把论文的主要可迁移信息说清楚了：
1. 论文真正贡献是把 `directional forecast -> consensus gate -> costed trading shell` 串起来；
2. 但本地 short-cycle portability probe（ETHUSDT 15m、近 120d、6 个快特征投票）已经给出负的毛 bps/trade；
3. 当前新增信息主要仍是“agreement gate 可以减少低质量交易”的 admission / veto 教训，而不是一个已经被压成独立 raw alpha 主语的 short-cycle 机会。

## Why it does NOT earn keep_P1
要进 `keep_P1`，这里至少需要证明：`multi-feature directional vote × consensus gate` 本身在 short-cycle 上提供了不被既有 breakout / trend / regime / admission family 吸收的独立 queue-facing 增量。

当前没有做到，原因很直接：
- **主语不够独立**：digest 自己也把它定位成“directional strategy shell”，且明确建议服务于已有 breakout / trend / microstructure directional alpha；这更像 admission layer，不像独立 raw alpha。
- **短周期 portability 没站住**：唯一本地 probe 还是负的毛收益，说明“共识门槛”本身不足以构成独立 edge。
- **增量更像过滤器，不像新边**：它改善的是何时不做，而不是为什么这笔交易本身有独立可赚的预测优势。

## Result sentence for runtime
`lagged-feature directional vote × consensus gate` 当前新增信息仍主要是“agreement gate 可作为 directional shell 的 admission / veto 层”，本地 15m naive portability probe 也未显示独立 edge，因此本轮 fresh intake 收口为 `background / P0`，不进入 survivor / P2。
