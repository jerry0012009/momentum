# 别把 OI bot 只读成“情绪仪表盘”：更该先拆的是「crowded perp positioning reversal × OI/taker/CVD/RSI confluence」这条 raw alpha 壳

- 时间：2026-04-21 20:20 UTC
- 类型：GitHub repo source audit + Binance USDⓈ-M public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：perp 仓位拥挤/解杠杆后的短周期反转；用 funding 极端、OI 变化、taker buy/sell pressure、CVD/RSI 与 L/S ratio 做入场确认
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（repo 有 entry / TP / SL / size / cooldown，但没有显式手续费、滑点与冲击成本）
- 主题标签：open-interest / funding / taker-imbalance / cvd / rsi / crowding / mean-reversion / liquidation-proxy / 5m / 15m / repo / public-data
- 证据类型：工程经验 + public-data quick probe / 待严格回测

## 1. 这次看了什么

看 `ksingh8/crypto-oi-strategy`：一个 2026 年创建、仍在更新的 Binance futures paper-trader。它把 OI、funding、RSI、global long/short ratio、taker buy/sell ratio、CVD 与 4H EMA trend gate 合成 0–100 分，分数达标且至少 2 个信号同向才开仓；默认还有固定仓位、TP/SL、冷却与最多 1 笔持仓。

## 2. 核心结论

- **base alpha 很清楚**：不是“看 OI 就追趋势”，而是当永续合约一侧拥挤、OI/taker/CVD 显示新仓或解杠杆压力时，押后续几根 `5m/15m` 的挤压或反转。
- repo 的完整度比普通指标包高：`README.md` 写了 funding 阈值、RSI 阈值、score gate、`SIGNAL_INTERVAL=5m`、`TP_PCT=1.5`、`SL_PCT=0.8`；`strategy.py` 进一步加入 4H EMA50/200 gate、taker pressure 与 CVD divergence。
- 我用 Binance 公开接口做了一个简化 portability probe（8 个 liquid majors，近 `500` 根 `5m/15m`）：`5m` 共 `17` 个信号，next `3/6/12` bars 平均约 `+0.17 / -0.78 / -6.30 bps`；`15m` 共 `20` 个信号，next `3/6/12` bars 平均约 `-9.33 / -7.53 / +7.66 bps`。
- 1.5% TP / 0.8% SL 的粗 bracket：`5m` 平均约 `-6.30 bps`、win rate `41.2%`；`15m` 平均约 `+2.16 bps`、win rate `35.0%`。样本很小，不能当结论，但说明这条壳更像**高选择性 router / event trigger**，不是无脑高频常开机。
- symbol pocket 很明显：`15m SOLUSDT` 在这次窗口里 `n=5`、bracket 平均约 `+83.0 bps`，而 `BNB/DOGE/LINK` 同口径偏弱；下一步应优先测 cross-symbol admission，而不是先调 score 参数。

## 3. 为什么和当前项目有关

`momentum` 最近已经补了不少 trend、pairs、funding、basis 与 grid raw alpha；这条补的是**仓位拥挤/清算代理数据驱动的短周期反转 alpha**。它的好处是所有关键数据都来自公开 Binance futures endpoints，天然能落到 `1m/3m/5m/15m`，并且可以服务两类 desk 组件：

- 作为 standalone event-driven mean-reversion / squeeze alpha；
- 作为已有 breakout / momentum 策略的 execution veto：当 taker spike 过热或 CVD 反向时，少追最拥挤的一侧。

## 3.5 策略拆解（必填）

- 方向属性：逆势为主，夹带 squeeze continuation；属于 perp positioning / crowding alpha。
- 基础 alpha：`funding/OI/taker/CVD/RSI` 多信号显示一侧拥挤或被迫平仓后，价格在短窗口内回归或挤压延续。
- regime：repo 用 `4H EMA50 > EMA200` / `<` 做大方向 gate；desk 可改成 `15m/1h trend + realized-vol percentile`。
- filter / veto：至少 2 个 distinct signals 同向；RSI 极端；taker ratio 过热时忽略；L/S ratio 动量辅助确认。
- risk / sizing / execution overlay：固定 size、单 symbol 最多 1 笔、TP/SL、SL cooldown；desk 必须补 maker/taker fee、slippage ladder、盘口深度与 funding settlement 边界。

## 4. 可复刻的最小实验

- 研究假设：`funding crowded side + OI acceleration/unwind + taker/CVD confirmation` 的信号，在 `15m` 上比 `5m` 更容易覆盖成本；`5m/3m` 更适合做 child execution。
- 可计算定义：复刻 repo score，但先只保留 5 个公开字段：`funding_rate`、`openInterestHist` 10-bar ROC/accel、`globalLongShortAccountRatio` 6-bar momentum、`takerlongshortRatio` vs 60-bar baseline、RSI14。
- 最小切口：Binance USDⓈ-M `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`，`5m/15m`，至少 90 天；next-open entry；`1.5% TP / 0.8% SL` 与 fixed hold `3/6/12` bars 双口径。
- 先看指标：`gross bps/trade`、`net bps/trade`（2/4/8 bps 单边 ladder）、trade count、symbol positive ratio、funding extreme vs non-extreme 分组。

## 5. 风险与保留意见

这类信号最大的坑是**把公开衍生品数据当成方向预测器**：OI 上升可能是趋势加仓，也可能是对冲；funding 极端可能持续很久；taker spike 可能是趋势启动而不是衰竭。repo 本身是 paper trader，不含真实成交、手续费、滑点和盘口容量；另外源码里有部署/通知相关默认配置，不能直接照搬到生产环境。当前 probe 只有近 `500` 根 bar，样本不足，只能作为 intake 证据。

## 6. 来源

- ksingh8. (2026). *OI Strategy — Crypto Futures Paper Trader*. GitHub repo.
- Repo URL: <https://github.com/ksingh8/crypto-oi-strategy>
- README: <https://raw.githubusercontent.com/ksingh8/crypto-oi-strategy/master/README.md>
- Strategy source: <https://raw.githubusercontent.com/ksingh8/crypto-oi-strategy/master/backend/strategy.py>
- Binance public endpoints used: `/futures/data/openInterestHist`, `/futures/data/globalLongShortAccountRatio`, `/futures/data/takerlongshortRatio`, `/fapi/v1/fundingRate`, `/fapi/v1/klines`
- Probe artifact: `reports/artifacts/quant_digests/2026-04-21_oi_crowding_probe.csv`
