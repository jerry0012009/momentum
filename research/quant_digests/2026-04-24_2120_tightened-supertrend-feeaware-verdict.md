# 别把这个 `tightened-supertrend-alpha` 仓只读成“完整可上线趋势系统”：对 short-cycle crypto desk，更该先回答的是「dual SuperTrend convergence × EMA50 × ATR bracket」这条 raw alpha 壳在 liquid majors 上成本后还剩多少

- 时间：2026-04-24 21:20 UTC
- 类型：2024 GitHub repo source audit（`README.md` + `src/strategy.py` + `docs/METHODOLOGY.md`）+ Binance Spot public-data portability probe（`BTC/ETH/SOL/BNB`，`15m`，近 `60d`）
- 主题类型：raw alpha
- 基础 alpha：**快 SuperTrend 翻向后，如果慢 SuperTrend 同向、价格站在 EMA50 同侧、且当前不是高波动噪音区，那么接下来几根 `15m` bar 更可能继续顺势，而不是立刻回吐。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/single-asset/trend/momentum/supertrend/ema50/atr/vol-filter/bracket-exit/15m/repo/public-data/cost/risk
- 证据类型：repo source + public API portability probe

## 1. 这次看了什么
主线材料：
- **GitHub handle：** `jaswanthobbu645-hub`
- **Year：** 2024（README 自述 `Last Updated: April 2024`）
- **Title：** *Tightened SuperTrend Alpha Strategy*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/jaswanthobbu645-hub/tightened-supertrend-alpha>
- **Repo URL：** <https://github.com/jaswanthobbu645-hub/tightened-supertrend-alpha>

这份 repo 最像会被短周期 desk 直接拿来试跑的那类材料：
- entry 讲得很完整；
- exit / sizing / risk / cost 也都写了；
- README 甚至直接给出 `Sharpe 1.84 / 314 trades / +11.74% / MaxDD 8.3%`。

但这轮真正重要的不是复述这些数字，而是先把 **base alpha** 讲清楚：

> **这不是“SuperTrend 指标很强”这么泛，而是“快线先翻向，慢线与 EMA50 再确认，赌后续 5~20 根 `15m` bar 还有一小段顺势延续”。**

翻成人话：
- 先等短期趋势刚刚转多/转空；
- 再要求中期趋势别唱反调；
- 再用 ATR 和时间止损把它包成一个完整 trend shell。

所以它属于很标准的 **single-asset trend / momentum raw alpha**，不是 filter，也不是纯 overlay。

---

## 2. 从 repo 里真正该保留什么
### 2.1 能直接抄成策略骨架的部分
`README.md` 与 `src/strategy.py` 里最值钱的是这套完整壳：
- **Entry**：
  - `ST fast(8, 2.5)` flip
  - `ST slow(18, 2.0)` 同向确认
  - `close > EMA50`（做多）/ `< EMA50`（做空）
  - `ATR% < 3%`
  - `volume > 1.2 × SMA20`
- **Exit**：
  - `1.8 × ATR` stop
  - `3.5 × ATR` take profit
  - fast ST trailing stop
  - `20 bars` time stop（约 `5h`）
- **Sizing / risk**：
  - `2.5% capital at risk`
  - 低波动加仓、高波动跳过
  - daily loss limit / max heat 这些组合层想法也写了

这比“只有一个信号、剩下全靠你脑补”的 repo 好很多。

### 2.2 但也要明确两处 source-audit 红旗
第一，**README 写得比实际仓内容丰满得多**。README 声称有 `backtest.py / indicators.py / risk_manager.py / results/` 等完整结构，但当前可见仓里实际文件远少于这份目录树。

第二，README 反复提到 **fee-adjusted edge / 1h bias / Monte Carlo / walk-forward**，但当前 `src/strategy.py` 里真正落地的，主要还是：
- 双 SuperTrend
- EMA50
- ATR 止盈止损
- volume filter
- same-timeframe backtest loop

也就是说：
> **它更像“一个值得拆的完整策略壳”，而不是“已被充分审计的可直接相信业绩”。**

---

## 3. 为什么和当前项目有关
这轮值得写，不是因为它已经证明自己能赚钱，而是因为它刚好补了我们素材池里一个常见空缺：

> **“结构完整、看起来很像能上线的趋势壳”，在 liquid majors 的成本后到底还能不能活。**

它服务的是 raw alpha 素材池，而不是 filter 池：
- 方向属性：**顺势 / single-asset trend**
- 信号本体：**fast flip 后的 continuation**
- overlay：ATR bracket、vol skip、volume confirmation

这对当前 desk 的价值有两层：
1. **正面价值**：给出一份很清楚的 trend shell 组件表；
2. **负面价值**：提醒我们别把“指标 confluence 很完整”误当作“成本后肯定活”。

---

## 3.5 策略拆解（必填）
- 方向属性：顺势 / 单资产趋势
- 基础 alpha：`fast SuperTrend flip -> slow SuperTrend + EMA50 confirm -> short-horizon continuation`
- regime：低到中等波动环境（`ATR% < 3%`）
- filter / veto：volume > `1.2 × SMA20`；高波动直接 veto
- risk / sizing / execution overlay：`1.8 × ATR` 止损、`3.5 × ATR` 止盈、fast ST trailing、`20 bars` time stop、risk-per-trade sizing、成本门槛

---

## 4. 本轮最小 public-data portability probe（Binance Spot，`15m`，近 60 天）
### 4.1 数据口径
- 数据源：Binance Spot public API `api/v3/klines`
- 周期：`15m`
- 样本：最近约 `60d`
- universe：`BTCUSDT / ETHUSDT / SOLUSDT / BNBUSDT`
- 成本口径：**round-trip 10 bps**（`4bps × 2 taker fee + 1bps × 2 slippage`）
- 产物：
  - `reports/artifacts/quant_digests/2026-04-24_tightened_supertrend_probe_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-24_tightened_supertrend_probe_detail.csv`
  - `reports/artifacts/quant_digests/2026-04-24_tightened_supertrend_probe_diag.csv`

### 4.2 关键结果
先给 5 个最值钱的数据点：

1. **4 个 liquid majors 成本后全部为负。**
2. pooled 口径共 **430 笔**，**胜率仅 `34.7%`**。
3. pooled 平均 **gross `-1.37 bps/笔`**，扣成本后 **net `-11.37 bps/笔`**。
4. 4 个币里相对最接近可做的是 **SOL**，但也只有 **`-3.26 bps/笔`**；BTC 为 **`-8.65 bps/笔`**。
5. 这套信号并不是“几乎不触发”——`60d` 内信号数量并不少，问题在于 **边太薄 + 胜率不够**，不是“没有样本”。

按币看：
- `BTCUSDT`：`112` 笔，win rate `35.7%`，avg net `-8.65 bps/笔`
- `ETHUSDT`：`121` 笔，win rate `31.4%`，avg net `-17.78 bps/笔`
- `SOLUSDT`：`104` 笔，win rate `37.5%`，avg net `-3.26 bps/笔`
- `BNBUSDT`：`93` 笔，win rate `34.4%`，avg net `-15.36 bps/笔`

另外，`probe_diag` 里能看到一个很有用的现实细节：
- volume filter 并没有把策略砍到“几乎不交易”，各币 `vol_pass_rate` 仍约 `25%~27%`；
- 真正的问题更像是：**dual-ST + EMA50 这条 continuation 本体，在当前 liquid-major 15m 上不够厚。**

一句话核心结论：
> **这条 raw alpha 壳“逻辑完整但边不厚”，更适合当 trend-shell 反例素材，而不是直接搬进实盘候选池。**

一句话说明它怎么证明：
> **不是靠 README 自报业绩，而是靠 repo 规则逐条翻译后，在 Binance 公共 `15m` 上按统一成本口径做了最小可复现回放。**

---

## 5. 为什么这轮仍值得进研究池
因为当前 bot7 的目标不是只收“正 verdict”，而是收 **可复现、能帮我们少走弯路** 的 alpha 素材。

这篇的真正价值是：
- **base alpha 很清楚**；
- **完整策略骨架齐全**；
- **transfer 检验明确失败**；
- 后续如果要救，也知道该救哪一层，不用再从零拆。

比起再写一篇“某指标组合看起来不错”，这种材料更像可审计的 desk 知识：
- 哪个部件可能有用；
- 哪个完整壳当前不够厚；
- 下一轮该怎么缩窄搜索空间。

---

## 6. 下一步怎么测
最该先做的不是继续原样跑更多币，而是做 **三步缩窄实验**：

1. **先测 flip 事件本体，而不是整套 confluence**
   - 比较：`fast ST flip` vs `fast+slow` vs `fast+slow+EMA50`
   - 看是谁把 trade frequency 降了，但没把 avg net 提起来。

2. **把 volume filter 改成“状态分桶”，不要只做 hard gate**
   - 比较 `volume z-score` 分位，看 edge 是否只在极端放量段存在。

3. **只在更干净的 regime 开机**
   - 例如先叠加：`BTC 1h realized vol` 中低分位、或 `15m` path-smoothness / ADX 更高时才跑；
   - 如果这样仍不能把 `SOL` 从 `-3.26 bps/笔` 拉到正区，就别再围绕这条线内循环。

如果要做最小 desk 版复现，我会优先测：
- `BTC / SOL`
- `15m` 主周期
- 事件窗 `next 4 / 8 / 12 bars`
- friction ladder `4 / 8 / 10 / 12 bps`

先回答一个很实盘的问题：
> **edge 是被成本吃掉，还是信号本体就已经不够厚。**

---

## 7. 风险与保留意见
- 这轮 probe 用的是 Binance Spot，而 repo 更像可用于 futures / paper trading 的壳；venue 差异会影响结果。
- 我按 repo 可见代码复刻了核心逻辑，但 README 里一些更高级的说法（如 fee-adjusted edge、1h bias、walk-forward）在当前可见源码中并不充分，因此**不能把 README 业绩当成已核验事实**。
- 这类趋势壳有一个常见问题：在图上看起来很顺，但在 liquid majors 上往往因为 **entry 太晚、stop 太宽、成本固定**，最后变成“有方向、没边际”。

---

## 8. 来源
- `jaswanthobbu645-hub`. (2024). *Tightened SuperTrend Alpha Strategy*. GitHub repository.
- Repo URL: <https://github.com/jaswanthobbu645-hub/tightened-supertrend-alpha>
- Readable URL: <https://github.com/jaswanthobbu645-hub/tightened-supertrend-alpha>
- Source files audited:
  - <https://github.com/jaswanthobbu645-hub/tightened-supertrend-alpha/blob/main/README.md>
  - <https://github.com/jaswanthobbu645-hub/tightened-supertrend-alpha/blob/main/src/strategy.py>
  - <https://github.com/jaswanthobbu645-hub/tightened-supertrend-alpha/blob/main/docs/METHODOLOGY.md>
