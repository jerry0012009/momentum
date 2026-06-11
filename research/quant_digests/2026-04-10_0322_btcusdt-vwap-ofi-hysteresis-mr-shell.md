# 别把这份 BTC perp repo 只读成 2 天 tick 实验：对 short-cycle desk，更该先测的是「VWAP 偏离 × OFI 纠偏 × 5m hysteresis mean-reversion shell」
- 时间：2026-04-10 03:22 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `src/signals.py` + `src/backtest.py` + `src/data.py`）+ Binance USDⓈ-M `BTCUSDT 1m` 近约 `60d` portability probe
- 主题类型：raw alpha
- 基础 alpha：`BTCUSDT perp` 在分钟级 `VWAP / rolling z-score / RSI / 快慢均线` 过度偏离后，未来 `5~15m` 更容易回归；`OFI / trade intensity` 更像确认与否决层，而不是 alpha 本体
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：mean-reversion / microstructure / VWAP / OFI / RSI / BTC / perp / 1m / 3m / 5m
- 证据类型：工程经验 + public-data portability probe

先回答 base alpha：**这不是 filter，而是单资产、超短周期、可直接下单的 raw alpha——本体就是“分钟级过冲后的均值回归”。**

## 1. 这次看了什么
看的是 `mengrenman/btcusdt-perp-signals`。repo 很克制：只做 `BTCUSDT` 永续，目标持有期就是 `5~15m`。源码里把 8 个分钟级信号拼成一个完整壳：`z-score MR`、`Bollinger MR`、`VWAP MR`、`OFI`、`trade intensity`、`RSI MR`、`MA cross`、`volume momentum`；默认权重里 `VWAP` 占 `20%`，`z-score / OFI` 各 `15%`，其余各 `10%`，再做 `EMA(5)` 平滑，并用 `entry=0.15 / exit=0.05` 的 hysteresis 生成仓位。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 最值得 intake 的，不是“1m maker scalp 很酷”，而是 **一套可复现的 BTC perp 超短周期均值回归完整策略壳**；而且对我们 desk，更可迁移的版本其实是**放慢到 `5m` 重平衡**。
- **一句话证明方式：** repo 自己先用两天、约 `2.3M` 笔原始成交做 tick→1m 研究；我再用 Binance 公共 `1m` perp kline（含 `trade_count` 与 `taker_buy_volume`）做近约 `60d / 86,400` 根 portability probe，看 IC、分桶和成本后壳是否还活着。
- repo README 给的原始结论并不空：最佳单因子 `5m` IC 大约在 `0.10~0.12`，加权 composite 胜过单因子，粗略 break-even transaction cost 约 `0.75 bps` round-trip，且 `1~3m` 重平衡优于更慢频率。
- 但把它搬到更长窗口的公共数据后，**alpha 还在，强度下降**：我这边 `5m` rank-IC 前几名是 `RSI MR 0.0585`、`MA cross 0.0572`、`VWAP MR 0.0554`，composite 约 `0.0488`；说明能 transfer，但没到“随便 taker 都能吃”的程度。
- 真正更像 desk branch 的，是 **VWAP 偏离这条母线**：按 `VWAP MR` 十分位分桶，最差桶未来 `5m` 约 `-0.43 bps`、最好桶约 `+0.77 bps`；未来 `15m` 约从 `-0.37 bps` 拉到 `+1.00 bps`，方向很干净。
- 更关键的是**节奏选择**：public-data probe 里，composite 若每 `1m` 改仓，gross 约 `+22.1%`，但 break-even 只有 `0.39 bps` round-trip，`0.5 bps` 成本后已经转负；`3m` 版只在 `0.5 bps` 下勉强剩 `+1.5%`。**反而 `5m` hysteresis shell 最像可交易版本**：gross 约 `+51.8%`，break-even 约 `1.09 bps` round-trip，`0.5 bps` 成本后约 `+27.9%`，`1.0 bps` 之后仍约 `+4.1%`。

## 3. 为什么和当前项目有关
这轮最值钱的点，不是又多了一个“BTC 均值回归”标题，而是给当前素材池补了一块**真正面向 `1m/3m/5m` 的完整 microstructure raw alpha 壳**：
- 它补的是我们最近 trend / pairs / funding 之外的 **单资产高强度反转 alpha**；
- 它天然适合做更快频的实验，不必硬塞进 `15m` 趋势框架；
- 它还顺手回答了一个很实盘的问题：**不是越快越好，慢一点反而更能穿过成本。**

## 3.5 策略拆解（必填）
- 方向属性：逆势 / 单资产 mean reversion
- 基础 alpha：分钟级价格相对 `VWAP / rolling mean / RSI / short MA` 的过度偏离，未来 `5~15m` 回归
- regime：高噪音但未进入单边失控趋势的分钟级环境更友好
- filter / veto：`OFI`、`trade intensity`、最小成交活跃度、成本门槛
- risk / sizing / execution overlay：`EMA(5)` 平滑、`0.15/0.05` hysteresis、`3~5m` 重平衡、maker-first 或仅在预估 round-trip < `1bp` 时放宽 taker

## 4. 可复刻的最小实验
- 研究假设：BTC perp 的分钟级过冲在下一段 `5~15m` 会回归，但只有当**重平衡频率放慢**且**交易成本受控**时，alpha 才能留下来。
- 一个可计算定义：直接照 repo 生成 `composite`；若 `signal > 0.15` 做多、`signal < -0.15` 做空，`|signal| < 0.05` 平仓；先比较 `1m / 3m / 5m` 三种改仓节奏。
- 最小回测切口：`BTCUSDT` Binance USDⓈ-M `1m`，先跑近 `60~90d`，成本阶梯至少测 `0.5 / 1.0 / 2.0 bps` round-trip。
- 最该先看：`break-even round-trip bps` 与 `cost-after return`；其次看 `VWAP MR` / `composite` 的 decile spread 是否还单调。
- 本轮产出的 portability artifacts：
  - `reports/artifacts/literature/btcusdt_perp_signal_ic_2026-04-10.csv`
  - `reports/artifacts/literature/btcusdt_perp_signal_shell_probe_2026-04-10.csv`
  - `reports/artifacts/literature/btcusdt_perp_signal_buckets_2026-04-10.csv`

## 5. 风险与保留意见
- 这是 **单币 alpha**，不是可立即扩容的多资产组合。
- 我的 portability probe 用的是公共 `1m` kline 代理，不是完整 L2 / queue / tick-by-tick 成交簿；真实实盘很可能比这里更吃执行。
- repo 原始样本只有约两天，容易高估信号强度；我补的 `60d` 只能说明“没马上死”，还不算严格 OOS。
- 单边大趋势、新闻冲击、流动性真空时，均值回归会被连续踩踏；因此它更像 **fast alpha sleeve**，不是全天候主引擎。

## 6. 来源
- Mengren Man. (2026). *BTCUSDT Perpetual Futures: Short-Horizon Signal Research*. GitHub repository.
  - Repo URL: `https://github.com/mengrenman/btcusdt-perp-signals`
  - Readable URL: `https://github.com/mengrenman/btcusdt-perp-signals`
- Key files:
  - `https://github.com/mengrenman/btcusdt-perp-signals/blob/main/README.md`
  - `https://github.com/mengrenman/btcusdt-perp-signals/blob/main/src/signals.py`
  - `https://github.com/mengrenman/btcusdt-perp-signals/blob/main/src/backtest.py`
  - `https://github.com/mengrenman/btcusdt-perp-signals/blob/main/src/data.py`
  - `https://github.com/mengrenman/btcusdt-perp-signals/blob/main/notebooks/03_signal_research.ipynb`
