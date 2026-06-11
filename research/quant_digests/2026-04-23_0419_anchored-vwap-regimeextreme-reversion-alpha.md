# 别把这份 2026 多策略仓里的 AVWAP 只读成美股 confluence 组件：对 short-cycle crypto desk，更该先拆的是「swing-anchored VWAP 偏离 × 5m/15m 极端回归」这条 raw alpha
- 时间：2026-04-23 04:19 UTC
- 类型：GitHub repo audit + Binance USDⓈ-M public-data portability probe（`BTC/ETH/SOL`，`5m` 主执行、`15m` regime，近约 `17d`）
- 主题类型：raw alpha
- 基础 alpha：价格若相对最近 swing 锚点的 AVWAP 偏离过远，短时间内更容易向该锚定公平价回归
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / mean-reversion / anchored-vwap / regime-extreme / single-asset / 5m / 15m / repo / public-data / cost / risk
- 证据类型：工程经验 + public-data portability probe

## 1. 这次看了什么
看的是 `ridopark/oh-my-opentrade`（2026）README。仓库主线很大，但对我们最有价值的不是它的 LLM debate 或 dark-pool 拼装，而是其中一句很短但很 desk 化的话：**AVWAP = anchored VWAP mean reversion from 5m/15m regime extremes**。这句话本身已经足够拆成一条可独立测试的 raw alpha。

## 2. 核心结论
- 这条线的 base alpha 很清楚：**价格偏离最近“有意义的成交量加权公平价”太远时，容易往回拉**；AVWAP 不是确认器而已，也可以直接当回归锚。
- 对 short-cycle desk，最适合先测的不是 repo 里的整套 confluence，而是 **`recent swing anchor -> AVWAP -> deviation extreme -> reclaim/timeout exit`** 这一条最小壳。
- 我用 Binance USDⓈ-M `BTC/ETH/SOL` 近约 `5000` 根 `5m` bars 做 quick probe：当价格相对最近 `48` 根内 swing 锚点 AVWAP 偏离超过 `35bps`，且 `5m RSI` 极端、`15m` 不在强趋势失控段时入场；未来 `12` 根内先回到 AVWAP 就平，否则 time-stop。结果 pooled 共 `74` 笔，**gross 约 `+0.52 bps/笔`，胜率 `59.5%`，粗扣 `8 bps` 后约 `-7.48 bps/笔`**。
- 但 broad major 负，并不等于这条线没用：**BTC 单独 bucket 有 pocket**，`22` 笔里 gross 约 `+8.78 bps/笔`、粗扣 `8 bps` 后约 `+0.78 bps/笔`；ETH / SOL 在这套“粗锚点 + taker 假设”下为负，说明可交易性高度依赖 anchor 选择和 execution。
- 一句话核心结论：**AVWAP 偏离回归像一条真实存在的 raw alpha 壳，但目前更像 BTC / maker-first / 精细 anchor 的 pocket，不像可直接全池平推的通用信号。**
- 一句话证明方式：**repo 给出策略骨架，我再用公开 Binance `5m/15m` 数据把它压缩成最小入场-出场规则做 portability probe，看成本后还剩不剩。**

## 3. 为什么和当前项目有关
这条线和我们之前把 anchored VWAP 当 shared confirmation 的读法不同：那一轮更像“确认脊柱”，这轮则是把 **AVWAP 本身升成 raw alpha 的公平价锚**。它直接补的是 desk 当前需要的 mean reversion 素材池，而且天然适配 `5m` 触发、`15m` 只做 regime gate 的研发节奏。

## 3.5 策略拆解（必填）
- 方向属性：逆势 / 单资产均值回复
- 基础 alpha：相对 recent swing-anchor AVWAP 的过度偏离会向锚定公平价回归
- regime：`15m` 不处于强趋势失控段；更偏 balance / reversal，而非 breakout acceleration
- filter / veto：`5m RSI` 极端、偏离幅度阈值、可加更严格的 anchor 质量筛选（volume rotation / session event / swing significance）
- risk / sizing / execution overlay：固定 time-stop、AVWAP reclaim exit、maker-first 回补、极端趋势 veto、ATR 或 deviation-scaled sizing

## 4. 可复刻的最小实验
- 研究假设：`5m` 上，当价格离最近有效 AVWAP 太远，而 `15m` 又不是强单边时，下一小段更容易回归 AVWAP。
- 一个可计算定义：最近 `48` 根内取最新显著 swing high/low 作 anchor；计算 anchored VWAP；当 `close/AVWAP-1` 超过 `±35~60 bps`，且 `5m RSI` 进入极端区、`|15m trend_z| < 2` 时反向入场。
- 最小回测切口：先只测 `BTCUSDT` perp，`5m` bars，样本先跑最近 `60~120d`；`entry=next open`，`exit=first AVWAP reclaim or 12 bars timeout`。
- 最该先看哪 1~2 个指标：**成本后 bps/笔**、**reclaim-before-timeout 比例**。如果 reclaim 率高但成本后仍负，优先改 execution 与 anchor 质量，而不是先加更多指标。

## 5. 风险与保留意见
- 当前 probe 只用了“最近窗口极值”当粗糙 anchor，离 repo 文里更像“swing highs / volume rotations / weekly opens”那种有语义的 anchor 还差一层。
- pooled 结果在 taker `8 bps` 假设下明显不够厚，说明这条线若要活，**要么靠更好的 anchor，要么靠 maker-first / queue placement**。
- AVWAP 回归很怕“趋势段里继续走远”；因此它更像 **balance/reversal pocket alpha**，不能伪装成全天候抄底摸顶机。

## 6. 来源
- ridopark. (2026). *oh-my-opentrade*. GitHub repository.
- Repo URL: `https://github.com/ridopark/oh-my-opentrade`
- Readable URL: `https://github.com/ridopark/oh-my-opentrade`
- 本地 probe artifacts:
  - `reports/artifacts/quant_digests/2026-04-23_avwap_regimeextreme_probe_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-23_avwap_regimeextreme_probe_trades.csv`
