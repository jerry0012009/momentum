# Volume-weighted cross-sectional momentum × abnormal-volume repeat gate
- 时间：2026-04-21 04:49 UTC
- 类型：GitHub / repo
- 主题类型：raw alpha
- 基础 alpha：横截面 relative-strength 动量——做多“短窗收益明显高于长窗基线、且成交额也同步放大”的币
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：cross-sectional / momentum / volume / abnormal-volume / router / Binance / 15m / 5m
- 证据类型：工程经验 + 公开市场数据快速 portability probe

## 1. 这次看了什么
看的是 `tim7park/Crypto-Stat-Arb-CX-Momentum-x-Volume`（2025-10）。它不是在讲“某个币突破了没有”，而是在做一件更适合 desk 扩素材池的事：**每天/每个 bar 在一组币里，挑出“涨得快、而且量也是真的在跟”的那一簇**。

## 2. 核心结论
- 这份 repo 的 base alpha 很清楚：**cross-sectional momentum with flow confirmation**，不是 filter 伪装成 alpha。
- 它的信号骨架可直接抄：`短窗均值收益 - 长窗均值收益` 再除以长窗波动，得到风险标准化动量；随后再乘 `短窗/长窗 quote volume 比值`。
- 真正有意思的旁支不是“只看量放大”，而是 **AVR（abnormal volume ratio）连续命中**：最近 5 个 bar 里，至少 3 个 bar 的成交额 > 自身 20-bar 中位数的 2 倍，才允许入池。这个规则很像“持续资金流确认”，比单次 volume spike 更适合拿来做 router。
- 我用 Binance USDⓈ-M 10 个 liquid majors 做了一个轻量 `15m/5m` portability probe：
  - `15m`、近 `75d`、`short=3 / long=60 / lag=1`：全篮子 gross `mean = +0.186 bps/bar`、`cum = +13.07%`、`Sharpe ≈ 2.00`；但平均换手折成 `4 bps` 单边成本约 `0.326 bps/bar`，说明**全篮子直接 taker 化不够厚**。
  - 同一套 `15m` raw score 若只做 strongest-only top1 router，命中约 `998` 次，next `2/4/8` bars 平均约 `+2.80 / +6.37 / +9.04 bps gross`，这就更像可落地的 parent signal。
  - `5m`、近 `25d`：全篮子 gross `mean = +0.065 bps/bar`、`cum = +4.57%`、`Sharpe ≈ 2.63`；top1 next `3/6/12` bars 约 `+0.70 / +1.43 / +0.35 bps gross`，说明 **5m 更适合 child execution，不像 15m 那样够资格当主信号**。

## 3. 为什么和当前项目有关
这篇最值钱的地方，不是又给了一个“趋势因子”，而是给了一个**横截面 raw alpha + flow gate** 的完整骨架：
- raw alpha：相对强弱动量
- 增强层：quote-volume tilt
- 准入层：AVR repeated-hit gate

这正好补当前 desk 不该只围着单资产 breakout / panic-bounce 转的缺口。更重要的是，它天然适合 `15m parent selection -> 5m child execution` 的短周期研发结构。

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值（long strongest bucket）
- 基础 alpha：短窗动量相对长窗基线的加速
- regime：默认无硬 regime；可后续叠加市场 breadth / BTC trend gate
- filter / veto：AVR repeated-hit gate（最近 5 bar 至少 3 次异常放量）
- risk / sizing / execution overlay：当前 repo 只有 `tanh` 压缩 + 横截面归一化；成本、止损、容量、child execution 仍需自己补

## 4. 可复刻的最小实验
- 研究假设：在 liquid majors 里，**“收益加速 + 持续异常成交额”** 比单纯追涨更有信息量。
- 可计算定义：
  - `score = sqrt(3) * (mu_3 - mu_60) / sigma_60 * (qvol_3 / qvol_60)`
  - 仅保留 `score > 0`
  - `AVR = qvol / rolling_median(qvol, 20)`；若最近 5 bar 中 `AVR > 2` 至少出现 3 次，则允许交易
- 最小回测切口：Binance USDⓈ-M，`BTC/ETH/SOL/XRP/BNB/DOGE/ADA/LINK/SUI/AVAX`，先做 `15m` 近 `90d` top1 router；`5m` 只做 child execution A/B。
- 先看 2 个指标：`gross edge after simple cost ladder`、`router hit-rate / post-entry 2~8 bars path`。

## 5. 风险与保留意见
- 这份 repo 原始结果是日频、且偏 long-only；直接迁到短周期后，**全篮子换手成本会先把 edge 吃掉**。
- AVR repeated-hit 可能在 news / listing / funding 边界时把“真趋势启动”和“短时拥挤冲顶”混在一起，需要再配一个波动或 CLV veto。
- 目前 probe 只做了 liquid majors、gross、无 funding / fee / slippage；它更像 admission check，不是 final verdict。

## 6. 来源
- tim7park. (2025). *Crypto-Stat-Arb-CX-Momentum-x-Volume*. GitHub repo.  
  Repo URL: `https://github.com/tim7park/Crypto-Stat-Arb-CX-Momentum-x-Volume`
- GitHub API metadata（created/pushed at 2025-10-27）:  
  `https://api.github.com/repos/tim7park/Crypto-Stat-Arb-CX-Momentum-x-Volume`
- Binance USDⓈ-M Futures Klines API（本次 portability probe 数据源）:  
  `https://fapi.binance.com/fapi/v1/klines`
