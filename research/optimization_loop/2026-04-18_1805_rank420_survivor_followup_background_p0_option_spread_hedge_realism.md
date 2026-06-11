# 2026-04-18 18:05 UTC — Rank 420 survivor follow-up: option-chain spread / hedge realism failed

- executor: bot3
- cycle_plan_item: 1
- target: `Rank 420 / BTC rich-IV short delta-neutral ATM straddle mean-reversion`
- action: survivor 唯一 follow-up
- verdict: `background/P0`
- artifact: `reports/artifacts/optimization_loop/2026-04-18_rank420_option_chain_snapshot.json`

## 本轮只执行的小点
按 `BOT2_BOT3_POLICY.md` 与 `BOT2_BOT3_STATE.md`，当前最前 pending 小点是 `Rank 420` 的 survivor 唯一 follow-up。它必须把上一轮的 `DVOL proxy` 升级到固定到期 `5d~9d`、ATM option-chain mid/spread 与 `1m~5m` delta-hedge PnL realism，并直接输出 `promote_P2` 或 `background/P0`。

## 最小可交易检查
本轮拉取 Deribit 公开 BTC option chain snapshot，限制为 `5d~9d` 到期并按现货价附近 ATM strike 配对 call/put straddle。

关键 snapshot（2026-04-18 18:11 UTC）：

- BTC index: `75832.15`
- 最近 ATM expiry: `24APR26`，DTE ≈ `5.58d`
- `76000` strike ATM straddle:
  - straddle mid ≈ `$3063.62`
  - call+put bid/ask spread ≈ `$151.66`
  - spread ≈ `4.95%` of straddle mid
  - spread ≈ `20.0bps` of underlying
  - net delta ≈ `-0.020`
- 旁边 `75000` strike 虽有更窄 `10bps underlying` spread，但已带 `+0.183` net delta，不能作为最干净的 ATM delta-neutral straddle proxy；若强行用它，还需要更多 perp hedge，进一步抬高 hedge-turnover 成本。

## 与上一轮 proxy edge 的对照
上一轮 fresh intake 的 strongest BTC `rich-IV short-vol` proxy 是：

- 1h realized-gap proxy: `+19.56bps`，win `81.9%`
- 4h realized-gap proxy: `+36.82bps`，win `82.0%`

但真实可交易 straddle 的最低 friction 不是零：

1. 最干净 ATM straddle 当前单次 call+put bid/ask 已约 `20bps underlying`；
2. short straddle 开仓/平仓若不能全程 maker，round-trip spread drag 仍会接近或超过 1h proxy edge；
3. option fee、perp hedge fee、1m~5m hedge turnover 与滑点尚未计入；
4. short-vol jump tail / event-window loss 也没有在 DVOL realized-gap proxy 中被充分扣除；
5. 当前没有历史 option-chain mid/spread + executed hedge PnL 序列能证明这些成本后仍稳定为正。

因此，上一轮所谓“唯一 blocker = option-chain fill / hedge PnL realism”在本轮没有被通过，反而被最小 snapshot 检查实质性击中：可交易摩擦已经处在与 strongest proxy 1h edge 同量级甚至更高的位置。

## 结论
`Rank 420` 不升 `P2`。

本轮 survivor 唯一 follow-up 输出 `background/P0`：

> `Rank 420 / BTC rich-IV short delta-neutral ATM straddle mean-reversion` 完成 survivor 唯一 follow-up 后未通过真实 option-chain fill / hedge PnL realism；当前 BTC `5d~9d` ATM straddle 最窄可用 spread 已基本吃掉 DVOL proxy 的 1h short-vol 边际，叠加 hedge turnover / option fee / jump tail 后不能诚实升级到 P2。

## runtime 写回
已更新 `docs/BOT2_BOT3_STATE.md`：

- `Fresh intake slot` 置为 `empty_after_survivor_followup`；
- `Surviving candidate slot` 置为 `none`，`followup_budget_remaining: 0`；
- `Background pool.latest_parked` 追加 `Rank 420` 的 P0 收口结论；
- `cycle_plan` item1 写入 `result` 并置为 `done`。

## 尾部动作状态（non-blocking）
- homepage publish：已独立执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`；进程在宿主侧异常终止（SIGKILL），按 policy 记为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件摘要：已独立执行并成功发送
  - `python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] Rank 420 期权链路真实摩擦未过" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-18_1805_rank420_survivor_followup_background_p0_option_spread_hedge_realism.md`
