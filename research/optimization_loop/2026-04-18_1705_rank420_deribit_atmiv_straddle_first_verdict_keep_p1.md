# Rank 420 / Deribit ATM-IV median-reversion short-straddle shell — fresh intake first verdict

- time: 2026-04-18 17:05 UTC
- executor: bot3
- cycle_plan_item: 1
- source: `research/quant_digests/2026-04-18_1328_deribit-atmiv-medianreversion-straddle-shell.md`
- assigned_rank: `Rank 420`
- verdict: `keep_P1`

## 执行动作
按当前 `cycle_plan` 的第一个 pending 小点，只对 `ATM IV 偏离自身长跑中位数 × delta-neutral straddle 回归` 做 fresh intake first-verdict，并补一个最小 honesty / execution realism 检查：判断 `DVOL/ETHVOL proxy` 是否已经足够把后续 blocker 收敛为真实可交易的短天期 ATM straddle option-chain fill / hedge PnL realism。

## 证据摘要
读取 digest 与对应 artifact：

- summary artifact: `reports/artifacts/quant_digests/2026-04-18_deribit_dvol_mr_summary.csv`
- events artifact: `reports/artifacts/quant_digests/2026-04-18_deribit_dvol_mr_events.csv`

关键结果：

- `cheap_iv_long_vol` 分支不保留为主线：
  - BTC：1h realized-gap proxy `-14.86bps`，4h `-29.82bps`；
  - ETH：1h `-31.38bps`，4h `-56.16bps`。
- `rich_iv_short_vol` 分支显著更清楚：
  - BTC：1h IV mean-reversion proxy `+0.042 vol pts`，win `56.2%`；1h realized-gap proxy `+19.56bps`，win `81.9%`；4h realized-gap proxy `+36.82bps`，win `82.0%`。
  - ETH：1h realized-gap proxy `+32.28bps`，win `85.6%`；4h `+51.51bps`，win `81.3%`，但 ETH 更适合作为次级分支，不覆盖 BTC-first 定义。

## 最小 honesty / execution realism 检查
本轮不把 DVOL/ETHVOL proxy 误写成已完成 option strategy PnL。当前证据只能说明：

1. `rich IV -> 后续实现波动低于 implied proxy` 这条 short-vol 方向有可见统计边际；
2. `cheap IV -> long vol` 分支未通过首轮 proxy；
3. 真实可交易性仍必须由固定到期、ATM chain、bid/ask、fill rule、delta hedge turnover 与 option/perp fee 共同决定。

但这已经把唯一剩余 blocker 收敛为单轴：`真实 option-chain fill / hedge PnL realism`。它不是泛泛缺数据，也不是 alpha identity 不清；对象身份足够明确，值得保留到 survivor 唯一 follow-up。

## 结论
`Rank 420 / BTC rich-IV short delta-neutral ATM straddle mean-reversion` 获得 `keep_P1`。

保留范围必须收窄为：

- BTC-first；
- rich-IV only；
- short delta-neutral ATM straddle；
- 5m admission，1h~4h holding / early-exit；
- 下一步唯一 survivor follow-up 必须升级到固定到期 `5d~9d` ATM option-chain mid/spread + `1m~5m` delta-hedge PnL realism。

不保留：

- repo 对称 long/short vol 原样照抄；
- cheap-IV long-vol 主线；
- 只用 DVOL proxy 宣称 paper-ready。

## runtime 写回
已更新 `docs/BOT2_BOT3_STATE.md`：

- fresh intake slot: `promoted_to_survivor`；
- surviving candidate slot: `Rank 420 / BTC rich-IV short delta-neutral ATM straddle mean-reversion`；
- followup_budget_remaining: `1`；
- cycle_plan item 1: `done`，result 写入 `keep_P1` 结论。

## 尾部动作状态（non-blocking）
- homepage publish（`bash scripts/publish_homepage_index.sh`）在异步执行中被宿主 `SIGKILL` 终止；按 policy 记为非阻断尾部失败，不影响本轮 verdict/state/log 生效。
- 邮件通知已独立执行并成功发送：`[momentum-bot3-auto] Rank 420 期权隐波回归首判保留`。
