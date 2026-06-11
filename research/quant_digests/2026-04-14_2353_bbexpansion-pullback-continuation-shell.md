# BB 扩张 breakout × pullback reversal continuation shell
- 时间：2026-04-14 23:53 UTC
- 类型：GitHub / repo source audit + public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：高波动顺势突破后，不追第三脚，而是等回踩均线再做同向 continuation
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：trend / momentum / breakout / pullback / Bollinger / ATR / multi-timeframe / 15m / 5m
- 证据类型：工程证据 + public-data portability probe

## 1. 这次看了什么
先回答 base alpha：**这不是“布林带指标教程”，而是一条多周期顺势 raw alpha——先抓 `15m` 的方向性波动扩张，再用 `5m` 的均线回踩 + reversal candle 做低追价的 continuation entry。**

主材料是 2026 GitHub repo `Epsilon-Fund/Epsilon-Quant-Research` 里的 `topics/momentum/strategies/bb_breakout_wf/bb_breakout.py`。源码把逻辑拆得很清楚：高周期先要求 **连续两根大实体同向 bar + BB 宽度扩张 + SMA slope 同向**；低周期再等 **价格回踩均线附近、但不能 overshoot、且 pullback 过程不能太暴力**，最后由 reversal pattern 触发入场，止损放前 swing，高度 desk-friendly。

## 2. 核心结论
- **一句话核心结论：** 值得 intake 的不是“布林带突破”四个字，而是这套 **`breakout setup` 与 `pullback entry` 分层** 的 skeleton；它比单纯追 breakout 更适合短周期 desk 做低追价 continuation。
- **一句话证明方式：** 我先审 repo 源码的状态机，再把它 desk 化成 `15m setup -> 5m entry`，用 Binance USDⓈ-M 公开数据做 2026 YTD portability probe。
- 本地 probe（`2026-01-01 ~ 2026-04-14`）对 `BTC/ETH/SOL/BNBUSDT` 的结果很分化：`BNB` 平均约 `+12.83 bps/笔`、`BTC` `+7.44 bps/笔`、`SOL` `+3.39 bps/笔`、`ETH` `-4.81 bps/笔`。
- 四资产合并共 `148` 笔，平均 gross 约 `+4.59 bps/笔`；粗扣 `4 bps` roundtrip 后只剩 `+0.59 bps/笔`，说明它**不是全市场通吃的 broad taker shell**，更像 `BTC/BNB` selective pocket。
- `BNB` 最像当前可继续追的 pocket：`30` 笔、hit rate `70%`、即使扣 `6 bps` 仍约 `+6.83 bps/笔`；`BTC` 也还能勉强存活，但 `ETH` 已经明显不过线。
- repo 自带 `wf_fold_results.csv` 还有一个审计提醒：有些 fold 出现 **`test_return` 非零但 `test_trades = 0`** 的口径不一致，所以这轮更该信任**源码逻辑骨架**，不要直接信 README/导出的收益截图。

## 3. 为什么和当前项目有关
最近 intake 很多是 pairs / XS / stat-arb，这条线正好补回 **trend / continuation raw alpha** 素材池，而且它不是“裸 breakout”，而是更 desk 化的 **高周期 setup + 低周期 child execution**。这对 `1m/3m/5m/15m` 研发很有用，因为它天然能拆成：方向层、等待层、否决层、止损层，而不是一团条件 if-else。

## 3.5 策略拆解（必填）
- 方向属性：顺势
- 基础 alpha：directional volatility breakout 之后的 pullback continuation
- regime：BB 宽度扩张 + SMA slope 同向
- filter / veto：回踩 bar 不能过大、价格不能穿均线太深、setup 超时失效
- risk / sizing / execution overlay：前 swing 止损 + `1R` target；当前真正的瓶颈是**资产筛选与成本**，不是再多加几个形态词

## 4. 可复刻的最小实验
- 研究假设：`15m` 上出现“连续两根大波动同向 bar + BB 扩张”后，`5m` 上首次温和回踩均线并出现 reversal candle，后续更容易继续走出一段同向 drift。
- 最小口径：Binance USDⓈ-M `BTC/BNB/ETH/SOL`，样本先用 `2026-01-01 ~ now`；setup 在 `15m`，entry/exit 在 `5m`。
- 先固定本轮参数邻域：`breakout_atr_mult 1.2~1.5`、`pullback_bps 30~60`、`max_child_bars 12~24`。
- **下一步怎么测：** 不要先继续调 trigger，先做 `asset admission`——把交易限制到 `BTC/BNB`，再看 `4 bps / 6 bps` 下的 `avg net bps`、`positive week ratio`、`target-rate vs time-exit-rate` 是否稳定；若只在 `time` 出场赚钱，说明更像 drift sleeve，不像高确定性 breakout shell。

## 5. 风险与保留意见
- 这条线目前最大的风险不是“没有信号”，而是 **edge 高度资产选择性**；ETH 已经给了反例。
- 当前 probe 还没纳入 maker/microstructure 优化，若实际执行不是 taker，BTC/BNB 可能更好；反过来，若遇到滑点放大，SOL 也会很快掉到线下。
- repo bundled 输出口径不一致，意味着后续若真要复现原仓 walk-forward，必须先单独审 performance accounting。

## 6. 来源
- Epsilon Fund. (2026). *Epsilon-Quant-Research*. GitHub repo.  
  Repo URL: `https://github.com/Epsilon-Fund/Epsilon-Quant-Research`
- Denislav Dantev. (2026, repo file header). *bb_breakout.py* (`topics/momentum/strategies/bb_breakout_wf/bb_breakout.py`).  
  Readable URL: `https://github.com/Epsilon-Fund/Epsilon-Quant-Research/blob/main/topics/momentum/strategies/bb_breakout_wf/bb_breakout.py`
- Epsilon Fund. (2026). *wf_fold_results.csv* (`topics/momentum/outputs/wf_fold_results.csv`).  
  Readable URL: `https://github.com/Epsilon-Fund/Epsilon-Quant-Research/blob/main/topics/momentum/outputs/wf_fold_results.csv`

## 7. 本地产物
- Probe 脚本：`reports/artifacts/quant_digests/2026-04-14_bbexpansion_pullback_probe.py`
- Summary：`reports/artifacts/quant_digests/bbexpansion_pullback_probe_summary_2026-04-14.csv`
- Cost ladder：`reports/artifacts/quant_digests/bbexpansion_pullback_probe_costladder_2026-04-14.csv`
- Trades：`reports/artifacts/quant_digests/bbexpansion_pullback_probe_trades_2026-04-14.csv`
