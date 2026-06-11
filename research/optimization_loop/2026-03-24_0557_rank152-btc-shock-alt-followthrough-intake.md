# 2026-03-24 05:57 UTC · Rank 152 / BTC 5m shock → alt basket delayed follow-through fresh intake

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 本轮路径：`Scout`
- 本轮范围：只做 **1 个主点 + 1 个紧邻子点**

## 0. 顶板判路
- `Paper / 待开启自动运行 = empty`
- authoritative `Next 3 bot3 runs` 明确：`Run 1 = fresh intake`
- 因此本轮不再继续 `interrupt / reserve / diagnostic anchor / autonomous monitoring` 历史遗留动作
- 当前合法主动作：认领 1 条新的 raw alpha / repo / paper 候选，并压成 `trade on / trade off + honesty gate + 下一轮最小 decisive verdict`

## 1. 为什么本轮选 Rank 152
这轮最有杠杆的新鲜候选不是再补一个 shared gate，而是把 05:54 UTC 新 digest 里的 **`BTC 5m shock -> alt basket delayed follow-through`** 正式纳入 Scout：
- 它是完整的 **standalone raw alpha**，不是附属 filter；
- entry / exit / regime / sizing / cost 假设已经齐，能直接进入 desk 缩版 first verdict；
- 它补的是当前桌面稀缺的 **cross-market / leader-laggard intraday** 家族；
- 它比继续维护 `Rank 140/145` 之类旧 interrupt/reserve 遗留更符合顶板的新成功定义。

## 2. 本轮主点
### 主点
- **`Rank 152 / BTC 5m shock -> alt basket delayed follow-through`**

reader-facing 定义：
> 当 BTC 在 `5m` 内先发生足够大的单边冲击时，不把它拿去给旧策略当 shared gate，而是直接交易随后 `15m~30m` 的 alt basket 延迟反应；熊市更像补跌 short，牛市更像踩踏后修复 long。

### 使用证据
- digest：`research/quant_digests/2026-03-24_0554_btc-5m-shock-alt-followthrough-raw-alpha.md`
- reader-facing page：`reports/site/reading/quant_digests/2026-03-24_0554_btc-5m-shock-alt-followthrough-raw-alpha.html`
- repo anchor：`mamipour/lead-lag-trader`
- theory anchor：`Cross-Market Intraday Time-Series Momentum`（SSRN, 2023）

## 3. 最小 intake 结论
这条线现在最诚实的口径是：
- **`fresh intake admitted / keep_P1 / raw-alpha candidate`**

原因：
1. **有独立策略骨架**：不是只会给旧策略当 veto/filter；
2. **有明确下一步**：可以直接缩成 `BTC + 6 followers` 的三臂 first verdict；
3. **有新家族价值**：补的是 cross-market lead-lag，不是老的 breakout/EMA 近亲；
4. **但当前仍缺本地 clean replication**：仓库自报结果强，但尚未经过 desk 的 next-bar-open + cost/breadth 诚实守门。

因此值得进入 active Scout，但本轮不能越级升 `P2`。

## 4. 紧邻子点
### 紧邻子点：下一轮最小 decisive verdict 应该怎么收紧？
结论：**只允许做 1 次 desk 缩版三臂 first verdict，不允许扩成大而全全篮子复刻。**

冻结口径：
- leader：`BTCUSDT`
- followers：`ETH / SOL / BNB / XRP / DOGE / ADA`
- arms：`bear_short` / `bull_dipbuy` / `dual_regime`
- formation shock grid：`-0.4 / -0.6 / -0.8 / -1.0 / -1.2%`
- execution：`signal bar close -> next bar open`
- holding：`15m / 30m`
- costs：`4 / 8 / 12 bps round-trip`
- first verdict 指标：`event_count / hit_rate / mean_net_bps / cross-asset breadth`

这样做的意义：
- 先回答它是不是 **真的能活过成本与 breadth**；
- 避免一上来就把 19 币篮子、venue mismatch、participation cap 全缠在一起，导致这轮又只留下“以后再说”。

## 5. 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 1/3`
- `cross_asset_stability = 1/3`
- `cost_trade_stability = 1/3`
- `deployability = 2/3`
- `recommended_action = keep_P1`
- `why_now = 顶板要求回到 fresh intake；这条线是新鲜、独立、可直接做 first verdict 的 raw alpha，不该再被 shared-gate 读法稀释。`
- `main_weakness = 目前仍主要依赖仓库自报回测，且存在 basket 成本与跨 venue 微观结构错配风险。`

### hard-fail flags
- `repo_self_report_not_local_clean_replication`
- `venue_mismatch_binance_backtest_vs_kraken_paper`
- `basket_execution_cost_may_dominate`
- `not_ready_for_P2`

## 6. 本轮交付
- 日志：`research/optimization_loop/2026-03-24_0557_rank152-btc-shock-alt-followthrough-intake.md`
- source intake：`reports/artifacts/literature/scout_rank152_btc_shock_alt_followthrough_source_intake_card.csv`
- reader-facing page（沿用本轮新 digest）：`reports/site/reading/quant_digests/2026-03-24_0554_btc-5m-shock-alt-followthrough-raw-alpha.html`

## 7. 一句话结论
`Rank 152` 值得进入 active Scout，但当前最诚实的位置仍是 **keep_P1 的新 raw-alpha 候选**；下一轮只配拿一次缩版三臂 first verdict 来回答它到底是 `park / keep_P1 / promote_P2`。
