# 别把 `mm-live` 只读成“做市工程模板”：对 short-cycle crypto desk，更该先拆的是「OFI/Kalman fair-value skew × maker markout」这条 microstructure raw alpha 壳

- 时间：2026-04-22 16:34 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `signals/fair_value.py` + `signals/imbalance.py` + `strategy/quoting.py` + `research/markout.py`）+ Binance USDⓈ-M public L2 REST probe（`BTC/ETH/SOL`，约 `45s × 0.5s`）
- 主题类型：raw alpha
- 基础 alpha：盘口买卖量失衡 / microprice 偏移能预测下一小段 mid-price drift；交易上不追市价单，而是把 fair value 往优势方向 skew，并用 maker quote 捕获半价差 + 短 horizon markout
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/order-flow-imbalance/kalman-fair-value/microprice/avellaneda-stoikov/market-making/markout/binance-perpetual/1m/3m/repo/public-data/cost/risk
- 证据类型：repo 规则骨架 + public L2 first probe

## 1) 这次看了什么

这轮主来源是一个 2026 新仓：

- **Authors**：Aliipou
- **Year**：2026（repo 创建时间 2026-03-23）
- **Title**：mm-live
- **Venue**：GitHub repository
- **DOI**：N/A
- **Readable URL**：<https://github.com/Aliipou/mm-live>
- **Repo URL**：<https://github.com/Aliipou/mm-live>
- **关键源码**：
  - <https://raw.githubusercontent.com/Aliipou/mm-live/main/src/mm_live/signals/fair_value.py>
  - <https://raw.githubusercontent.com/Aliipou/mm-live/main/src/mm_live/signals/imbalance.py>
  - <https://raw.githubusercontent.com/Aliipou/mm-live/main/src/mm_live/strategy/quoting.py>
  - <https://raw.githubusercontent.com/Aliipou/mm-live/main/src/mm_live/research/markout.py>

repo 的可复用点不是“又一个 A-S 做市公式”，而是把信号链写得很完整：`fair_value = Kalman(mid) + alpha × imbalance`，再用 Avellaneda-Stoikov 的 reservation price / half-spread，把 quote 向订单流优势方向 skew；最后用 markout 检验成交后 `100ms~30s` 中价是否继续对自己有利。

## 2) 先回答一句：base alpha 是什么？

> **base alpha = L2 order-flow imbalance / microprice 对短 horizon mid-price drift 的方向预测。**

所以它不是纯 execution overlay。它有可交易表达：当 OFI / microprice 指向上行时，提高 fair value、收紧 ask / 放宽 bid；指向下行时反过来。收益来源不是市价追涨，而是 **maker fill 后的正 markout + 半价差捕获**。

## 3) first probe：盘口失衡确实有短 horizon 方向性，但 edge 只有微结构级别

我用 Binance USDⓈ-M 公共 depth REST 做一个很小的 feasibility probe：`BTC/ETH/SOL`，每 `0.5s` 抓 top20 depth，约 `90` 个 snapshot / symbol，计算：

- `top_imb = (best_bid_size - best_ask_size) / sum`
- `depth_imb = top10 bid/ask size imbalance`
- `micro_dev_bps = (microprice - mid) / mid`
- 下一 snapshot 的 `mid return bps`

对应文件：
- `reports/artifacts/quant_digests/mm_live_ofi_markout_summary_2026-04-22.csv`
- `reports/artifacts/quant_digests/mm_live_ofi_markout_detail_2026-04-22.csv`

最有信息量的数字：

| symbol | signal | n | corr(next) | highQ - lowQ next bps | median spread bps |
|---|---:|---:|---:|---:|---:|
| BTCUSDT | depth_imb | 89 | `0.289` | `+0.362` | `0.013` |
| ETHUSDT | depth_imb | 89 | `0.166` | `+0.411` | `0.042` |
| SOLUSDT | top_imb | 89 | `0.313` | `+0.569` | `1.138` |

**人话结论**：这个信号在 `0.5s` 级别能看到方向性，但单次差异大多是 `0.3~0.6 bps`。它不适合伪装成 `5m/15m` 方向主信号；更适合做 `1m/3m` child execution / maker-first alpha sleeve：只在父策略允许交易时，用 OFI 决定挂哪边、挂多近、是否撤单。

## 4) 如何落成完整策略（entry/exit/sizing/risk/cost）

- **Entry / quote admission**：父层先给可交易方向或中性做市许可；子层要求 `|depth_imb|` 或 `|micro_dev_bps|` 进入 top quantile，才允许主动 skew。
- **Quote placement**：沿用 repo 的 A-S 框架：`reservation = fv - qγσ²T`，`delta` 随 vol regime 放大；OFI 为正时 fair value 上调，同时 quote 更偏向不被 adverse selection pick off。
- **Exit**：不是 K 线固定 hold，而是 fill 后做 markout 监控；若 `100ms/500ms/1s` markout 连续为负，立即降 size / widen / 暂停。
- **Sizing**：按 inventory cap + realized vol + recent markout quality 缩放；不做 “98% 仓位” 这类方向策略仓位。
- **Risk**：高波动、深度骤降、spread 扩大、连续负 markout 时 kill-switch；单 symbol inventory 硬上限。
- **Cost**：必须 maker-first；若退化成 taker 追单，这条 edge 基本会被费用和滑点吃掉。

## 5) 为什么这条线值得进研究池

最近 digest 已经有不少 `15m` parent alpha：pairs、basis、cross-sectional、mean reversion、breakout。它们共同的问题是：gross edge 常有，但成本后容易被吞。`mm-live` 这类材料的价值在于补一个可复用的 **child execution alpha**：不是帮我们决定“买哪个币”，而是帮已经通过 admission 的交易更便宜、更少被打穿地成交。

## 6) 下一步怎么测（明确动作）

1. **把 probe 从 REST 升级成 WebSocket**：至少采 `BTC/ETH/SOL/AVAX/LINK`，`1h`，100ms/500ms/1s/5s markout。
2. **做 fill simulator**：用 post-only bid/ask 规则模拟排队成交，不只看 mid drift；统计 fill rate、markout、cancel ratio。
3. **接到现有 parent alpha**：选 2 条已有 `15m` 策略（例如 xs momentum router + pair fade），比较 `next-open/taker` vs `OFI maker child` 的 slippage / net PnL。
4. **建立 kill-switch 阈值**：若过去 N 笔 `avg_markout < -0.3 × half_spread`，自动 widen 或停机。
5. **成本阶梯**：分别按 maker rebate / maker 0 / taker fallback 三档，确认 edge 是否只存在于 maker 成交。

## 7) 结论一句话

**`mm-live` 值得收进池子，但不要把它当新的 15m 方向信号；它更像一条可复现的 microstructure raw alpha：用 OFI/Kalman fair value 预测极短 horizon drift，再把这个预测转成 maker quote skew、markout 风控和 child execution 降成本组件。**
