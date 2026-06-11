# 别把 Passivbot 只读成“马丁格尔网格机器人”：对 short-cycle crypto desk，更该先拆的是「volatility-forager × contrarian grid bounce capture」这条完整 raw alpha 壳

- 时间：2026-04-21 21:54 UTC
- 类型：GitHub repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：`高近期波动合约里，短时价格冲击更容易出现小幅反弹/回吐；用分层限价网格吃这个 bounce`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：mean-reversion / grid / market-making / volatility-selection / forager / trailing / risk / cost / 5m / 15m
- 证据类型：工程经验 + repo source audit + public-data quick probe

## 1. 这次看了什么

这次看的是高星开源仓 `enarjord/passivbot`：它不是预测趋势的 bot，而是明确写成 contrarian market maker，在 perp 上用 grid / trailing entry / trailing close、EMA band、wallet exposure limit、auto-unstuck、hard-stop 等组件管理仓位。最值得 desk intake 的不是“马丁格尔”标签，而是 **Forager 选币 + 波动自适应网格 + 小幅反弹止盈** 这一条完整 raw alpha 壳。

## 2. 核心结论

- Base alpha 很清楚：先选近期最“会动”的合约，再在冲击后反向提供流动性，赌下一小段会有可吃的反弹/回吐。
- repo 的完整度很高：entry 有 EMA band / grid spacing / trailing threshold，exit 有 TP grid / trailing close，sizing 有 `wallet_exposure_limit / n_positions`，risk 有 auto-unstuck 与 equity hard stop。
- 我做了一个保守 transfer probe：10 个 Binance liquid majors，`5m/15m` 最近各 1500 根；用 rolling normalized range 选 top3，再用 `|ret_z| > 1.75` 反向开仓，`5m` 15bps TP / 40bps SL / 6 bar timeout，`15m` 25bps TP / 60bps SL / 4 bar timeout。
- 结果不支持“全池无脑网格”：`5m` 全池 `316` 笔，gross `-2.96 bps/笔`，粗扣 `8 bps` 后 `-10.96 bps/笔`；`15m` 全池 `351` 笔，gross `-6.62 bps/笔`，net `-14.62 bps/笔`。
- 但有一个可继续拆的 pocket：`LINKUSDT 15m` `31` 笔，gross `+7.99 bps/笔`，胜率 `77.4%`，扣 `8 bps` 后约 `-0.01 bps/笔`，说明这条线不是不能做，而是必须转成 **symbol/router + maker-first + 更严格 shock admission**。

## 3. 为什么和当前项目有关

`momentum` 现在缺的不是又一个“漂亮网格”，而是能拆成完整策略组件的 raw alpha 壳。Passivbot 给了一个值得复用的工程拆法：把“反向吃小回弹”拆成 `选币 / 初始入场 / 加仓间距 / 止盈网格 / trailing close / stuck 处理 / 总风险上限`，这比只测一个 RSI 超卖更接近实盘可控。

## 3.5 策略拆解（必填）

- 方向属性：逆势 / 单币 mean reversion / maker-first market making
- 基础 alpha：高波动合约在短时冲击后出现局部 bounce / retracement
- regime：优先高 normalized range、但不能是单边崩盘；需要成交额和可挂单深度足够
- filter / veto：low-volume prune、Forager volatility rank、EMA readiness、极端趋势日 veto、funding / news shock veto
- risk / sizing / execution overlay：wallet exposure cap、grid spacing 随波动放宽、TP grid、trailing close、auto-unstuck、equity hard stop、maker-first 限价执行

## 4. 可复刻的最小实验

下一步不要直接复刻完整 Passivbot，而是测一条干净 baseline：

- 假设：`volatility top-k` 合约里，`ret_z < -z` 后的 long bounce 与 `ret_z > z` 后的 short pullback 是否有成本后边。
- 定义：`forager_score = rank(mean(log(high/low), 48 bars))`；只交易 top1/top3；entry 用下一根开盘或 maker-limit mid-pullback；exit 用 `TP = 0.3~0.6 × recent_rr`、`SL = 1.5~2.5 × TP`、timeout `3~8 bars`。
- 切口：Binance USDⓈ-M `1m/3m/5m/15m`，先测 `LINK/AVAX/DOGE/ADA/SOL` 这类更会动的币，再和 `BTC/ETH` 分开统计。
- 指标：每笔 gross / net、TP hit rate、SL first rate、持仓时长、maker fill 假设下的 cost ladder。

## 5. 风险与保留意见

这类策略最大风险是“均值回复假设在趋势崩盘里失效”。repo 的 auto-unstuck 能让权益曲线更平滑，但它本质上是在受控范围内承认亏损，不是免费午餐。当前 quick probe 已经说明：如果用 taker 成本和粗糙 shock rule，全池不成立；只有在特定币种、maker-first、严格 admission 下才可能接近可做。

## 6. 来源

- enarjord. `passivbot` — Trading bot running on Bybit, OKX, Bitget, GateIO, Binance, Kucoin and Hyperliquid. GitHub repo.
- Repo URL: https://github.com/enarjord/passivbot
- Relevant docs: `README.md`, `docs/configuration.md`, `docs/risk_management.md`
- Local probe artifacts:
  - `reports/artifacts/quant_digests/passivbot_forager_grid_probe_2026-04-21.py`
  - `reports/artifacts/quant_digests/passivbot_forager_grid_probe_summary_2026-04-21.csv`
  - `reports/artifacts/quant_digests/passivbot_forager_grid_probe_trades_2026-04-21.csv`
