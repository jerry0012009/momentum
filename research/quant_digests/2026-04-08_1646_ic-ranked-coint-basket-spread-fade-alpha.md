# 别把这份 Cornell CFEM repo 只读成 pairs 课程项目：对 short-cycle desk，更该先测的是「IC-ranked coint pair basket × margin-capped spread fade」
- 时间：2026-04-08 16:46 UTC
- 类型：GitHub / repo source audit + public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：cointegrated spread mean reversion（协整价差回归）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：pairs / stat-arb / relative-value / mean-reversion / cointegration / zscore / market-neutral / 15m / 5m
- 证据类型：工程经验 + 公共数据 portability probe

## 1. 这次看了什么
看的是 `Jim-Shao/CryptoPairTrading`：一个 2025–2026 的 Cornell CFEM 项目（repo 描述写明 *Sponsored by Hummingbot*）。本轮重点审了 `main.py`、`trade.py`、`export_after_signal_test.csv`、`output_chain.csv`，再把 repo 里更像 desk 可交易的 liquid-major pair，粗口径迁到 Binance USDⓈ-M `15m/5m` 做 portability probe。

## 2. 核心结论
- **一句话核心结论：** 这份 repo 真正值钱的不是“又一个 z-score pairs”，而是把 **pair admission → signal → sizing → stop → portfolio kill-switch** 串成了一条完整 market-neutral 壳。
- **一句话证明方式：** 证据来自源码里完整参数与风控链条，再加上我用公开 `15m/5m` perp 数据做的简化迁移测试，能直接看到哪一段是 alpha、哪一段是成本门槛。
- repo 默认不是盲做相关性，而是先用 `output_chain.csv / export_after_signal_test.csv` 做 shortlist，再在交易层要求协整通过；源码里 `top_n=100`、`train_len` 网格是 `7/15/30` 天（按 `1h` bar 写成 `7*24/15*24/30*24`）、`entry_k=2.0/2.25/2.5`、`exit_k=0/0.5`、`reset_len=5` 天。
- 风控和落地是完整的：`stop_loss_pct=2%`、`margin_per_pair=15%`、组合 `deactivate_equity_ratio=85%`，并显式写了 `fee_rate=4 bps`、`margin_rate=20%`、stop-loss 冷却期与协整失效重检逻辑。
- repo 自带 shortlist 里，液态 majors 也能挑出像样 pair：例如 `ETH/SOL` 的 `Best IC=-0.6523`、`AVAX/NEAR` 的 `Best IC=-0.5437`，说明它想抓的不是“高相关一起涨跌”，而是**信号后收益更容易向均值回归的 pair**。
- 但我把这套思路粗暴迁到 Binance USDⓈ-M 后，**15m 还能看到 gross alpha，5m 明显更吃成本**：`ETH/SOL` 在 `15m` 简化口径下约 `24` 笔、毛 `+13.16 bps/笔`，`AAVE/UNI` 约 `34` 笔、毛 `+14.69 bps/笔`；可一旦按四腿 taker-taker `16 bps` roundtrip 扣成本，两者都只剩约 `-2.84 / -1.31 bps/笔`。`5m` 的 `ETH/SOL` 更是只有约 `+9.00 bps/笔` 毛利，已经明显不够。

## 3. 为什么和当前项目有关
这条线和 desk 现在的价值很直接：它不是单币 breakout，也不是纯 filter，而是**可以独立成完整策略的 raw alpha**。对当前素材池来说，它提供的是一条能跟单币 trend / momentum 互补的 **market-neutral / relative-value** 线路，而且源码里已经把：
- pair admission
- entry/exit
- 仓位上限
- 成本参数
- kill-switch

这些 desk 真正在意的部件都拆出来了，适合直接搬进 `1m/3m/5m/15m` 复现框架。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / stat-arb / market-neutral
- 基础 alpha：协整价差偏离后的均值回归
- regime：只在 pair 仍通过协整检验、且 shortlist IC 仍有效时开机
- filter / veto：`pval_alpha=0.05`（失败可放宽到 `0.15`）、`entry_k / exit_k`、止损、冷却期、组合权益跌破阈值停机
- risk / sizing / execution overlay：单 pair 保证金占用 `15%`、手续费显式建模 `4 bps`、组合级 `85%` deactivation、固定 beta spread + 定期 reset

## 4. 可复刻的最小实验
**研究假设：** repo 里 “IC shortlist + 协整 gate” 这层 admission，能把 `15m` perp pairs 的毛利保住到接近可交易，而不是任意找 pair 都能做。

**可计算定义：**
1. 先在 top-liquid perp universe 上复刻 repo 的 shortlist 思路，至少保留 `Best IC` 或等价的 post-signal IC 排序；
2. 对 shortlist pair 计算 `spread_t = log(P2_t) - beta * log(P1_t)`；
3. `zscore(spread)` 超过 `±2` 入场，回到 `±0.5` 内平仓；再对比是否需要 `|z|>=2.5` 才值得做。

**最小回测切口：**
- 资产：先做 `ETH/SOL`、`AVAX/NEAR`、`AAVE/UNI`
- 周期：先 `15m`，再看 `5m`
- 样本：最近 `3~6` 个月 Binance / OKX perp

**最该先看：**
- `gross bps / trade` 与 `breakeven cost`
- `positive pair ratio`（不是只看单一最好 pair）

## 5. 风险与保留意见
- repo 主口径是 `1h`；直接压到 `5m` 很容易把本来够用的 spread edge 压成纯手续费贡献者。
- 我这次 portability probe 还是简化版，没有完整复刻 repo 的 IC shortlist 生成、cooldown、组合并发与更细的 fee/fill 逻辑，所以只能说明“毛 alpha 大小”和“成本崖”大概在哪。
- pairs 最大风险不是信号本身，而是**admission 漂移**：pair 关系失效、beta 漂移、单腿流动性塌陷，都会让看起来漂亮的 z-score 变成假均值回归。

## 6. 来源
- Jim Shao. (2025/2026). *CryptoPairTrading* (Cornell CFEM Project Sponsored by Hummingbot). GitHub.
  - Repo URL: `https://github.com/Jim-Shao/CryptoPairTrading`
  - Readable URL: `https://github.com/Jim-Shao/CryptoPairTrading`
- Source audit files:
  - `README.md`
  - `main.py`
  - `trade.py`
  - `export_after_signal_test.csv`
  - `output_chain.csv`
- Local portability probe note:
  - `/root/clawd/tmp_research/jim_pairs_portability_probe_notes_20260408.txt`
