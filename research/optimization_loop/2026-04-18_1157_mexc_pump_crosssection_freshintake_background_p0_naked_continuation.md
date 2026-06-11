# bot3 auto execution — MEXC pump cross-sectional continuation fresh intake

- 时间：2026-04-18 11:57 UTC
- 执行小点：cycle_plan item1
- 对象：`research/quant_digests/2026-04-18_1140_mexc-pump-crosssection-continuation-alpha.md`
- 动作：fresh intake first-verdict + 最小 honesty / execution realism blocker

## Verdict
`短窗 price burst × volume burst cross-sectional continuation` 的 Binance majors portability 已显示裸 `1m/3m/5m` 续涨不成立（全样本 `-0.16/-0.58/-0.65bps`，q75 `-0.09/-1.68/-0.64bps`），`10m` 仅 `+0.36/+0.94bps` gross、远低于最小成本；它最多是 delayed-follow-through router/veto 线索，不足以作为新的 event-driven front object 保留，本轮 fresh intake 直接收口 `background/P0`。

## 最小证据
- repo 提供的是实时 pump scanner / attention-burst 胚子，不是完整可交易策略。
- Binance Spot majors `1m` portability probe 中，top burst 裸 continuation 不成立：全样本 next `1/3/5m` gross 约 `-0.16 / -0.58 / -0.65bps`。
- q75 强 burst 子样本也未改善成可交易续涨：next `1/3/5m` gross 约 `-0.09 / -1.68 / -0.64bps`。
- next `10m` 虽略转正（全样本 `+0.36bps`、q75 `+0.94bps`），但远低于最小真实摩擦 / 滑点 / spread 成本。

## Honesty / execution realism blocker
裸追异动榜首不是可诚实承接的 front object；唯一可能用途是把该线索降级为 `delayed-follow-through router / veto`，例如 burst 后等待 pullback/hold 或后续 order-flow 扩张确认。但当前小点的 success criterion 要求若裸 `1m/3m/5m` 主信号站不住且成本厚度不足，则直接 `background/P0`。

## Runtime 写回
- Fresh intake latest_result / latest_result_record 已更新到本 verdict。
- Background pool 已追加该对象。
- cycle_plan item1 已标记 `done`。

## 尾部执行状态
- homepage publish（`publish_homepage_index.sh`）异步任务最终 `SIGKILL` 失败；按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件摘要发送成功（`[momentum-bot3-auto] MEXC异动续涨首判收口P0`）。
