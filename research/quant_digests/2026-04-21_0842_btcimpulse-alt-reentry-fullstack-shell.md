# 别把这个 vectorized backtester 只读成“回测引擎”：对 short-cycle desk，更该先回答的是「BTC impulse × alt own-move confirmation/reentry × BTC-fail exits」这条完整 raw alpha 壳有没有净边
- 时间：2026-04-21 08:42 UTC
- 类型：2024/2026 GitHub repo source audit（`README.md` + `config.example.json` + `vectorized_backtest.py` + `main_runner.py` + GitHub metadata）+ Binance USDⓈ-M public-data portability probe（8 个 liquid majors，`5m/15m`，90d）
- 主题类型：raw alpha
- 基础 alpha：BTC 短窗快速上冲后，部分 alt 会出现滞后/同步延续；若 alt 自己也有最小正动量确认，则做多 alt，并用 BTC 反向下跌、take-profit、time-cap 做退出
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / leader-laggard / btc-impulse / altcoin-continuation / reentry / state-machine / dynamic-leverage / fear-greed / BTC-fail-exit / Binance USDⓈ-M / 5m / 15m / repo / public-data / cost / risk
- 证据类型：repo 工程壳 + public-data quick probe

## 1. 先回答：这篇东西的 base alpha 是什么
一句话：**BTC 出现短窗强上冲时，alt basket 不是同时完成定价；如果 alt 自己也刚开始动，下一段更可能继续跟随，而不是立刻均值回归。**

这不是纯 filter。它有完整的 raw alpha 壳：
- **entry**：BTC impulse 触发 `BE / BEL / SP_BE`，或 alt 自身 reentry 触发 `R / R2 / SP_R`；
- **confirmation**：`asset_minimum_enable` 要求 alt 自己在短窗内至少有一点正动量，避免“BTC 拉、alt 完全不跟”也硬追；
- **exit**：BTC 反向下跌 / BTC panic / take-profit / cooldown；
- **sizing/risk**：按 entry reason 选择不同 leverage，并可按 Fear & Greed 高低情绪切换参数。

它和之前那些“BTC lead-lag 论文摘要”不完全重复：这里的新增价值不是再证明 BTC 会 lead alt，而是 repo 把它写成了 **可执行状态机**：entry taxonomy、own-asset confirmation、BTC-fail exit、fear-state parameter override、daily entry cap、red-alert re-arm 都在代码里。

## 2. repo 里真正值得拆的策略骨架
这次看的仓库是 **AArt1552 / Vectorized-Crypto-Backtester**。README 写得比较泛，但核心在 `vectorized_backtest.py` 和 `config.example.json`。

GitHub 元数据：
- repo：<https://github.com/AArt1552/Vectorized-Crypto-Backtester>
- 创建时间：2024-06-21
- 最近 push：2026-04-21
- 语言：Python
- stars/forks：`1 / 0`
- 描述：altcoin strategies driven by Bitcoin price action and quantitative analysis

代码里能拆出 6 类入场：
- `SP_BE`：BTC 在 `1` 根内上涨 `1%`，且 alt 最小正动量确认；
- `BE`：BTC 在 `2` 根内上涨 `1%`，且 alt 最小正动量确认；
- `BEL`：BTC 在 `3` 根内上涨 `1.4%`，且 alt 最小正动量确认；
- `SP_R`：alt 自己在 `2` 根内上涨 `2%`；
- `R`：alt 自己在 `3` 根内上涨 `2%`；
- `R2`：alt 自己在 `5` 根内上涨 `2.3%`。

默认 `config.example.json` 里还有几层风险/执行壳：
- `asset_minimum_enable=true`，`asset_minimum_pct_to_entry=0.125%`，用于 BTC-led entry 的 alt 自身确认；
- `take_profit_dynamic=true`，基础 TP 触发 `2.5%`；
- `fixed_fee=0.001`，也就是单边 `10 bps` 的保守费率口径；
- BTC exit：例如 `BTC 15 bars 跌 2.25%`、`BTC 3 bars 跌 2%`、`BTC 20 bars 跌 4% panic`；
- Fear & Greed：高/低情绪下切换 BTC trigger、reentry trigger 和 leverage；
- red-alert：离场后若 alt 再跌一段又从低点反弹，可 re-arm。

这是一条“完整策略壳”，不是单个指标。

## 3. 我做的最小 public-data 快检
为了不把 repo 直接当信号，我做了一个可复现的简化 probe：

- 数据：Binance USDⓈ-M public klines；
- 标的：`ETH/SOL/BNB/XRP/DOGE/LINK/AVAX/ADA` vs `BTC`；
- 时间：最近约 `90d`；
- 周期：`5m / 15m`；
- 方向：只测 repo 主体的 long-alt shell；
- 入场：保留 `SP_BE / BE / BEL / SP_R / R / R2`，并保留 `asset_minimum` 作为 BTC-led entry 的确认；
- 出场：保留 BTC-fail exits 与 TP；额外加一个 desk 侧 `8h time-cap`，避免没有 red-alert/fear-index 复刻时仓位无限拖着；
- 成本：按 repo `fixed_fee=0.001` 粗扣单边 `10 bps`，round-trip proxy 为 `20 bps`；
- 未复刻：Fear & Greed 参数切换、dynamic leverage 的资金曲线、red-alert auto-entry、逐笔 maker/taker 成本。

所以这不是“repo 完整复跑”，而是一个最小可迁移问题：**BTC impulse + alt own-move confirmation 这条核心 alpha，在 5m/15m 上是否已经有足够厚的 gross edge？**

本地 artifacts：
- `reports/artifacts/quant_digests/probe_btc_led_alt_reentry_2026-04-21.py`
- `reports/artifacts/quant_digests/btc_led_alt_reentry_probe_combo_2026-04-21.json`
- `reports/artifacts/quant_digests/btc_led_alt_reentry_probe_summary_2026-04-21.json`
- `reports/artifacts/quant_digests/btc_led_alt_reentry_probe_trades_2026-04-21.csv`

## 4. quick probe 结果：有信号密度，但默认成本口径下还不够厚
合并 8 个 liquid majors 后：

- `5m`：`455` 笔，gross 平均 `-12.78 bps/trade`；扣 `20 bps` round-trip fee proxy 后，net proxy `-32.78 bps/trade`，净胜率 `44.4%`。
- `15m`：`669` 笔，gross 平均 `+1.36 bps/trade`；扣费后 net proxy `-18.64 bps/trade`，净胜率 `43.5%`。

先别看 net，先看 gross：`15m` 已经从 `5m` 的明显负 gross 变成接近持平 / 小正 gross，说明这条 BTC-led alt continuation 壳 **不是完全没有结构**。但按 repo 自带的 `10 bps` 单边成本，它仍然不够厚。

出场结构也说明了问题：
- `5m`：`time_cap 241`、`take_profit 107`、`btc_exit 93`、`btc_panic 6`、`btc_exit_long 8`；
- `15m`：`time_cap 344`、`take_profit 163`、`btc_exit 103`、`btc_panic 28`、`btc_exit_long 31`。

也就是说，大量仓位不是靠 TP 或 BTC-fail exit 清掉，而是拖到 `8h time-cap`。这对 short-cycle desk 是个坏信号：**entry 能抓到事件，但 payoff / exit 壳还没把事件转成高周转净边。**

## 5. 单币 pocket：AVAX / ETH 值得优先留，但不是“直接上线”
最接近可用的是：
- `15m AVAX`：`89` 笔，gross `+17.36 bps/trade`，扣 `20 bps` 后 net proxy `-2.64 bps/trade`；
- `15m ETH`：`80` 笔，gross `+9.59 bps/trade`，扣费后 `-10.41 bps/trade`；
- `5m AVAX`：`54` 笔，gross `+5.56 bps/trade`，扣费后 `-14.44 bps/trade`；
- `5m SOL`：`54` 笔，gross `+2.19 bps/trade`，扣费后 `-17.81 bps/trade`。

这几个 pocket 说明：
1. 不该全市场等权扫；
2. 需要 symbol router；
3. 如果真实执行能做到 maker-heavy 或更低费率，`15m AVAX` 这类 pocket 才有继续测的价值；
4. 但如果必须 taker 追价、且滑点明显，这条壳现在不够。

## 6. 对 desk 的判断
### 判断 1：它合格地进入 raw alpha 素材池
原因很简单：base alpha、entry、exit、sizing、cost 全能说清楚。它不是“Fear & Greed overlay”，Fear & Greed 只是参数切换层；alpha 本体是 **BTC impulse → alt continuation / reentry**。

### 判断 2：短周期主战场更像 `15m`，不是 `5m`
按这轮 quick probe，`5m` 太噪，BTC 上冲后 alt 的跟随窗口经常不够覆盖成本；`15m` 虽然仍未过成本，但 gross 结构明显好一些。对 desk 来说，下一轮应该先测 `15m entry + 1m/3m execution`，而不是纯 `5m close-to-close`。

### 判断 3：repo 里最该偷的不是 leverage，而是 “BTC-fail exit”
很多 leader-laggard 策略只写入场，不写退出。这个仓库有一个朴素但实用的退出思想：**只要 BTC 这个 leader 反向跌破阈值，alt continuation 的前提就坏了。**

这可以迁移给其他 raw alpha：
- BTC-led alt momentum；
- XS momentum top basket；
- liquidity-sweep continuation；
- funding-boundary continuation short。

## 7. 下一步怎么测
1. **分拆 entry reason**：单独测 `SP_BE / BE / BEL / SP_R / R / R2`，不要混在一起；重点看是不是 `SP_BE` 与 `BE` 在 15m 贡献了大部分可用 edge。
2. **把 execution 改成 15m signal + 1m/3m fill**：15m 收盘确认后，不要下一根 15m close 追；用 1m/3m 的回撤限价、spread gate 和超时撤单模拟。
3. **成本敏感性**：跑 `2 / 4 / 8 / 20 bps` round-trip 四档；如果只有 `2 bps` 才活，那它更像 maker/低费账户专属。
4. **symbol router**：先保留 `AVAX/ETH/SOL`，再加 liquidity / spread / beta-to-BTC 过滤，避免 ADA/DOGE 这类拖累 pocket。
5. **复刻 Fear & Greed 分层**：不是拿 FNG 当 15m 主信号，而是看高/低情绪下 BTC impulse 的跟随半衰期是否不同；若不同，再把它用作参数选择器。
6. **重写 exit**：当前 time-cap 太多；要测试 `partial TP + BTC fail-fast + alt trailing stop`，目标是把 time-cap 占比从约一半压到三分之一以下。

## 8. 结论
这篇 repo 值得保留为 **raw alpha / 完整策略壳**：它把 BTC-led alt continuation 从“BTC 拉，山寨跟”这种口头说法，拆成了可测的 entry taxonomy、own-alt confirmation、BTC-fail exit 和成本参数。

但 first probe 也很清楚：
- `5m` 版本不行；
- `15m` gross 有一点结构，但按 repo 的 `20 bps` round-trip cost 仍未过线；
- 下一轮不要先调 leverage，应该先做 **entry reason ablation + 15m signal / 1m execution + symbol router + lower-cost sensitivity**。

如果能在 `15m AVAX/ETH/SOL` 上把执行成本压到低双位 bps 以内，并把 time-cap 仓位减少，这条壳才有资格进入更正式的 walk-forward。

## 9. 来源
- Author / Owner：AArt1552
- Year：2024 repo，2026 active push
- Title：**Vectorized-Crypto-Backtester - Fast Backtesting for Crypto Strategies**
- Venue：GitHub repository
- DOI：无
- Readable URL：<https://github.com/AArt1552/Vectorized-Crypto-Backtester>
- Repo URL：<https://github.com/AArt1552/Vectorized-Crypto-Backtester>
- GitHub metadata API：<https://api.github.com/repos/AArt1552/Vectorized-Crypto-Backtester>
- Source audit files：
  - `README.md`
  - `config.example.json`
  - `vectorized_backtest.py`
  - `main_runner.py`
