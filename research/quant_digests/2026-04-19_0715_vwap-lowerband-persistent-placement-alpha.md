# 别把这份 Freqtrade VWAP 仓只读成“高仓位挂机 bot”：对 short-cycle crypto desk，更该先拆的是「persistent lower-VWAP underpricing × long-side placement」这条 raw alpha
- 时间：2026-04-19 07:15 UTC
- 类型：GitHub / repo source audit + public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：价格持续贴着/跌穿 rolling VWAP 下沿后，若出现 lower-band reclaim，更容易走出一段短均值回归反弹
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / single-asset / mean-reversion / vwap / lower-band / placement / long-only / binance-perpetual / 15m / 5m / repo / public-data / cost / risk
- 证据类型：工程经验

## 1. 这次看了什么
看的是 `titouannwtt/freqtrade-france-strategies_simple_vwap`（2025 建仓、2026-03-30 仍有更新痕迹）。Repo headline 是一套 `4h` 的 Freqtrade 长仓策略：`VWAP lower band touch` 入场、`EMA slope/CCI` 退出、最多 `40` 个并发仓、带 DCA 与波动率缩仓。对我们 desk 真正有价值的，不是“90% 时间都在场内”这种产品壳，而是它暗含的 base alpha：**持续贴着 VWAP 下沿的币，后面是否更容易反抽**。

## 2. 核心结论
- 一句话核心结论：这份仓真正能迁移到短周期 desk 的，是 **lower-VWAP underpricing 的 long-side mean reversion 原型**，不是它的高暴露 DCA 外壳。
- 一句话证明方式：我先审了 repo 的 `README`、`simple_vwap_v1.py`、live/backtest config，再用 Binance USDⓈ-M 公共 `15m/5m` 数据对“lower-band pierce -> reclaim”做了最小迁移快检。
- repo 原版是完整策略壳：`VWAP(5)` 下沿、`EMA180`、`CCI160`、自定义 stake、最多 `4` 次 safety orders、极深 stop（文档写 `-37%`），所以它更像“仓位管理很重”的 placement system，不是干净的短持有 alpha 论文复刻。
- 我把它 desk 化成更可测的 raw alpha：`low < vwap_low & close > vwap_low`，同时要求最近 `8` 根里至少 `6` 根满足原 repo 的 lower-band touch 语义，再加 `close > EMA180` 与 `exit_bad` 不触发，测试下一段收益。
- 结果并不漂亮：`15m` 全样本在 next `4/8/12` bars 约 `-3.69 / -8.95 / -13.63 bps`；按每时点只做 `deepest` 一档也仍是 `-1.15 / -4.76 / -7.18 bps`。说明把这条线硬搬成 `15m` 主策略，当前更像接飞刀。
- `5m` 上虽然略微转正，但也只有 next `3/6/12` bars 约 `+0.87 / +0.88 / +1.05 bps`，粗扣 `8 bps` 仍明显不够厚。也就是说，**有 underpricing 痕迹，不等于有可交易厚度**。

## 3. 为什么和当前项目有关
这篇东西跟当前主线相关，不在于它已经能上线，而在于它补了一个我们还值得保留的 raw alpha 母题：**VWAP 下沿“持续被压住”到底是便宜货，还是弱势延续？** 当前 first verdict 更偏后者，所以它对 desk 的价值反而是：
- 给 `VWAP reclaim / pullback` 家族补一个明确的反例；
- 告诉我们别把高 DCA、高常驻仓位外壳误读成短周期 edge；
- 后续若还想做 VWAP 类 long fade，必须再找更强的 veto（例如 event shock、liq unwind、proxy panic）才能把 raw alpha 变厚。

## 3.5 策略拆解（必填）
- 方向属性：逆势 / 单资产 long-only
- 基础 alpha：persistent lower-VWAP underpricing -> short-horizon bounce
- regime：更适合趋势未坏但局部被砸的环境；repo 用 `EMA180` 隐式要求大级别别太差
- filter / veto：最近 `8` 根 lower-band persistence、`close > EMA180`、`CCI/EMA` 退出条件
- risk / sizing / execution overlay：波动率缩仓、最多 `4` 次 DCA、limit entry/exit、深 stoploss

## 4. 可复刻的最小实验
- 研究假设：短周期里，真正有用的不是“碰一下 VWAP 下沿就买”，而是 **被压了一段时间后出现 reclaim**。
- 可计算定义：`low < rolling_vwap_low(5,1.05σ) & close > vwap_low`，再比较 `n_touch_8 >= 6` vs 无 persistence gate。
- 最小回测切口：Binance USDⓈ-M `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC`，先测 `15m` 近 `60d`、`5m` 近 `21d`。
- 最该先看：`gross bps / trade` 与 `top1-per-ts` router 后的 `net after cost`。如果这两个都不转正，就别急着讨论 DCA 和仓位优化。
- 下一步怎么测：把这条线与 `liqshock-oiunwind` / `proxy panic` / `tradeflow sell-dominance` 之类更强的“被动砸盘”事件做交集，只保留 **有外生冲击、但大级别趋势未坏** 的 lower-VWAP reclaim 事件，再看 `5m child execution` 是否能把 `+1bps` 级别薄边抬厚。

## 5. 风险与保留意见
- 这份 repo 本身强依赖 DCA 与高常驻仓位，容易把“资金曲线平滑”误认成“入场 alpha 很强”。
- 原代码的 `VWAP_low < high` 定义极宽，几乎更像“长期允许挂低买单”，不适合直接当我们 desk 的因果入场条件。
- 当前 public-data probe 没有把 maker rebate、排队成交、分批 DCA 全部还原；但即便在更宽松的 gross 口径下，`15m` 已明显偏负，所以没必要先在执行层替它找借口。

## 6. 来源
- Titouannwtt / Freqtrade France. (2025/2026). *Simple VWAP v1 - Freqtrade Strategy*.
  - Repo URL: `https://github.com/titouannwtt/freqtrade-france-strategies_simple_vwap`
  - Readable URL: `https://github.com/titouannwtt/freqtrade-france-strategies_simple_vwap/blob/main/README.md`
- Key files audited:
  - `freqtrade/user_data/strategies/simple_vwap_v1.py`
  - `freqtrade/live_configs/hyperliquid_simple_vwap_v1.json`
  - `freqtrade/backtest_configs/futures_binance.json`

## 7. 本地产物
- Probe events: `reports/artifacts/quant_digests/2026-04-19_vwap_lowerband_reclaim_15m_events.csv`
- Probe events: `reports/artifacts/quant_digests/2026-04-19_vwap_lowerband_reclaim_5m_events.csv`
- Probe summary: `reports/artifacts/quant_digests/2026-04-19_vwap_lowerband_reclaim_summary.csv`
