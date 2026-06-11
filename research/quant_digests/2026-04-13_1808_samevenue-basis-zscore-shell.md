# 别把这份 2025 delta-basis repo 只读成课程级全流程工程：对 short-cycle desk，更该先拆的是「same-venue spot↔perp basis z-score fade」这条完整 raw alpha 壳——但 repo 默认成本位会把它直接打穿

- 时间：2026-04-13 18:08 UTC
- 类型：2025 GitHub repo source audit（`README.md` + `src/config.yaml` + `src/signals/threshold_strategy.py` + `src/signals/position_manager.py` + `src/backtest/backtest_engine.py` + `src/backtest/portfolio.py` + `src/backtest/execution_simulator.py` + `src/backtest/funding_calculator.py` + `FINAL_SUMMARY.md`）+ Binance public `1h/15m` portability probe
- 主题标签：raw-alpha/relative-value/carry/basis/spot-perpetual/delta-neutral/mean-reversion/zscore/same-venue/binance/bybit/btc/eth/1h/15m/5m/repo/public-data/cost/risk
- 证据类型：源码规则 + repo 自带结果摘要 + 公共数据 first verdict

- 主题类型：raw alpha
- 基础 alpha：**当 perpetual 相对 spot 的 basis 明显偏离其自身滚动均值时，做 basis 收敛：perp 明显偏贵就 `long spot + short perp`，perp 明显偏便宜就做反向腿，赚的是 spread 回归加上 funding 辅助，而不是赌单边方向。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = same-venue spot↔perp basis mean reversion。**

这份 repo 值得收进素材池，不是因为它“工程做得完整”这么空泛，而是因为它确实把一条 **relative-value / carry / basis raw alpha** 写成了完整可执行壳：

- basis 偏离够大才开仓；
- 回到均值附近就平；
- 极端继续扩张就止损；
- 同时显式计入 funding、fee、slippage、position sizing。

翻成人话：
- 不是押 BTC 下一根涨还是跌；
- 而是押 **perp 和 spot 这两条腿的相对错位会回去**；
- perp 太贵就空 perp、买 spot；
- perp 太便宜就反过来；
- 收益来源是 basis 压缩，不是裸方向。

所以它不是 filter，也不是 overlay；它本体就是一条 **可独立回测的 raw alpha**。

## 2. 这次看了什么

### 主来源（repo）
- **Author / Owner：** GitHub owner `mariamlulu`
- **Year：** 2025
- **Title：** *Delta Basis Trading System*
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** <https://github.com/mariamlulu/delta-basis-trading>
- **Repo URL：** <https://github.com/mariamlulu/delta-basis-trading>
- **GitHub metadata：**
  - created: `2025-10-30T10:20:01Z`
  - pushed: `2025-10-30T10:25:33Z`
  - description: `Delta-neutral spot ↔ perpetual basis mean-reversion system for crypto (BTC/ETH) — backtest + reporting.`

### 本轮自建 probe 产物
- 规则快检脚本：`reports/artifacts/quant_digests/2026-04-13_delta_basis_binance_probe.py`
- 汇总：`reports/artifacts/quant_digests/delta_basis_binance_probe_summary_2026-04-13.csv`
- 成本阶梯：`reports/artifacts/quant_digests/delta_basis_binance_probe_costladder_2026-04-13.csv`
- 逐笔明细：`reports/artifacts/quant_digests/delta_basis_binance_probe_detail_2026-04-13.csv`

## 3. 一句话核心结论 + 一句话证明方式

### 一句话核心结论
> **这份 repo 最有价值的地方，是把 `same-venue basis z-score fade` 写成了完整 raw-alpha 壳；但 public-data first verdict 很清楚：gross edge 只有个位数十分之一 bps/笔，8 bps round-trip 就全灭，repo 默认 40 bps 成本位更是直接判死。**

### 一句话证明方式
> **证明不是靠 README 口号，而是靠源码参数 + Binance public spot/perp/funding `180d` 快检：BTC/ETH 在 `1h` 与 `15m` 上的平均每笔 `gross+funding` 只剩 `0.35 ~ 0.78 bps`，而 `8 bps` round-trip 后四个 bucket 的平均净值全部落到 `-7.2 ~ -7.65 bps/笔`。**

## 4. 为什么这轮仍值得写，而不是跳去别的 funding/basis 题材

这个问题必须先回答，不然就会跟今天早些时候的 funding/basis digest 混成一类。

这轮仍值得写，原因是它补的是另一件事：

1. **它不是“funding + spread 的 rich-perp 单边 admission”，而是更原始、更对称的 basis MR 完整壳。**
   - 之前那类题材更多是在回答：什么时候 `short perp + long spot` 更像正期望；
   - 这份 repo 则是把 **basis 偏离本身** 当核心 alpha，再把 funding 作为持有期现金流并入。

2. **它把完整策略外壳拆得非常直白。**
   - data → processing → signal → execution → funding → performance 全是独立模块；
   - 很适合拿来做“短周期 desk 该保留哪一层、该扔哪一层”的解剖。

3. **它的自带结果很诚实。**
   - repo 自己的 `FINAL_SUMMARY.md` 直接写：`4,140` 笔交易、`97%` max drawdown、`$58,304` fees+slippage、`0%` win rate；
   - 这反而比只贴漂亮净值的 repo 更值得看，因为它让我们可以清楚回答：
     > 这条线的问题究竟出在 alpha 本体，还是出在成本与落地方式？

## 5. repo 真正提供了什么

## 5.1 核心配置已经是一条完整策略定义
`src/config.yaml` 给的默认参数非常清楚：

- **资产：** `BTC/USDT`, `ETH/USDT`
- **交易所：** `binance`, `bybit`
- **频率：** `1h`
- **样本长度：** `180d`
- **lookback：** `336h`
- **entry：** `|z| >= 2.0`
- **exit：** `|z| < 0.5`
- **stop：** `|z| > 4.0`
- **max hold：** `336h`
- **notional_fraction：** `0.5`
- **perp_leverage：** `3x`
- **funding_interval：** `8h`
- **cost：** maker `2 bps`、taker `5 bps`、slippage `5 bps/side`

只看配置就知道：
这不是随手写个 z-score notebook，
而是一条已经明确了 **entry / exit / sizing / risk / cost** 的策略壳。

## 5.2 信号逻辑很朴素，但足够可复现
`src/signals/threshold_strategy.py` 的逻辑就是：

- `|z| >= z_entry` 开仓
- `|z| < z_exit` 平仓
- `|z| > z_stop` 止损

而且注释写得很清楚：
- **正 z-score**：`perpetual > spot`，预期 basis 向下回归，因此做 `long spot + short perp`
- **负 z-score**：`perpetual < spot`，预期 basis 向上回归，因此做反向腿

翻成人话：
> **它不是在找趋势确认，而是在赌“偏得太远就会往回收”。**

## 5.3 组合层和风险层并没有偷懒
`src/backtest/portfolio.py` / `src/signals/position_manager.py` 里至少把下面几件事写实了：

- 每个资产同一时刻只允许一笔 open position；
- 仓位大小按 `NAV × notional_fraction` 算；
- 至少保留 `10%` cash buffer；
- position 生命周期单独跟踪 `fees_paid / funding_payments / pnl`；
- 到点可触发 `time_exit`。

这意味着它不是单纯“找信号”，而是真把资金占用、持有时长、组合管理也纳进来了。

## 5.4 成本与 funding 被当成一等公民
`src/backtest/execution_simulator.py` 和 `src/backtest/funding_calculator.py` 的价值在于：

- 双腿都显式计 fee / slippage；
- perpetual 腿 funding 按 `8h` 结算；
- backtest 不是 gross-only 幻觉。

也正因为如此，repo 最终才会老老实实得出一组很难看的结果。

## 5.5 repo 自己的结论其实已经在提醒我们“别把 gross 当 alpha”
`FINAL_SUMMARY.md` 给出的 6 个月回测摘要非常刺眼：

- `4,140` trades executed
- `97%` max drawdown
- `Sharpe ≈ 0`（文中写成 `-0.000`）
- `0%` win rate
- `Total Costs = $58,304`

所以这份 repo 最适合 desk 的读法不是：
> “basis MR 不存在。”

而是：
> **“这条壳存在，但 broad same-venue taker 版大概率只是在给成本打工。”**

## 6. 我做的 public-data portability probe：结果很直白

## 6.1 数据与口径
我没有直接照抄 repo 的内部数据文件，而是用公开 API 重做了一版最小实验：

- **数据源：** Binance public spot klines + USDⓈ-M perpetual klines + fundingRate
- **公开性：** 完全公开 REST
- **样本：** 最近 `180d`
- **资产：** `BTCUSDT`, `ETHUSDT`
- **频率：** `1h` 与 `15m`
- **信号：** 尽量镜像 repo 默认参数
  - lookback `336h`
  - entry `|z| >= 2`
  - exit `|z| < 0.5`
  - stop `|z| > 4`
  - max hold `336h`
  - next-bar open 执行
- **PnL 近似：**
  - `basis_bps` 的收敛收益
  - 加上 funding 现金流
  - 再跑 `8 / 16 / 24 / 40 bps` round-trip 成本阶梯

## 6.2 先记最重要的 6 个数

### 数 1：`1h BTC` 平均每笔 `gross+funding = 0.51 bps`
- trades：`138`
- win rate（gross+funding）：`65.2%`
- median hold：`3` bars

这很关键：
**命中率不算差，但单笔 edge 小得离谱。**

### 数 2：`1h ETH` 是四个 bucket 里最好的，也只有 `0.78 bps/笔`
- trades：`132`
- win rate：`67.4%`
- median hold：`3` bars

ETH 比 BTC 好一点，但也只是“gross 还活着”，离可交易还远。

### 数 3：压到 `15m` 后，频率上来了，edge 没跟着来
- `BTC 15m`：`454` 笔，`0.40 bps/笔`
- `ETH 15m`：`398` 笔，`0.35 bps/笔`
- 两者 median hold 都是 `3` bars（约 `45m`）

也就是说：
> **把这套 z-score 壳直接翻译到 `15m`，并不会自动变成更适合 short-cycle desk 的高频 alpha，只会把原本就很薄的 gross 切得更碎。**

### 数 4：`8 bps` round-trip 后四个 bucket 全灭
- `BTC 1h`：`-7.49 bps/笔`
- `ETH 1h`：`-7.22 bps/笔`
- `BTC 15m`：`-7.60 bps/笔`
- `ETH 15m`：`-7.65 bps/笔`

这里没有“个别币还能勉强过线”的侥幸，**四个 bucket 全部为负。**

### 数 5：repo 默认 `40 bps` round-trip 成本位几乎等于直接宣判失败
- `BTC 1h`：`-39.49 bps/笔`
- `ETH 1h`：`-39.22 bps/笔`
- `BTC 15m`：`-39.60 bps/笔`
- `ETH 15m`：`-39.65 bps/笔`

这跟 repo 自带 summary 里的巨大成本损耗是同方向的。

### 数 6：funding 有帮助，但帮得很有限
平均每笔 funding 贡献大约是：
- `BTC 1h`：`+0.10 bps`
- `ETH 1h`：`+0.21 bps`
- `BTC 15m`：`+0.03 bps`
- `ETH 15m`：`+0.05 bps`

所以这条线不是“funding 一加就复活”，而是：
> **funding 只是把一个极薄的 basis MR gross 稍微抬高了一点点，远远抬不过广义 taker 成本。**

## 7. 这条线对 short-cycle desk 的正确定位

我现在对它的判断是：

### 7.1 它是 raw alpha，而且是 complete shell
这点不用含糊：
- base alpha 清楚；
- entry / exit / sizing / risk / cost 都清楚；
- 不该把它降级成 filter 或 overlay。

### 7.2 但它不是 broad same-venue taker fast lane
这也必须钉死：
> **same-venue、双腿都按 taker 近似去做的 broad basis-zscore fade，不是我们现在该直接上线的主线。**

### 7.3 更合理的 desk 读法是“保留壳，缩窄场景”
如果还想沿这条线继续挖，最合理的方向不是再调几个 z-score 参数，而是把适用场景主动缩窄：

1. **只保留 rich-perp 一侧**
   - 即先测 `long spot + short perp`；
   - 因为 `perp cheap` 分支往往需要 spot short / borrow plumbing，落地难度更高。

2. **把 `1h` 当 admission 层，`15m / 5m` 当 execution 层**
   - 不要把 `15m` 当重新发现 alpha 的主频；
   - 而是当更细的进出场时点层。

3. **改成 low-friction / maker-first 版本**
   - 这条线最大的问题不是“完全没回归”，而是“回归太薄”；
   - 若不能把摩擦从 `8~40 bps` 大幅砍下来，几乎没有讨论价值。

4. **优先转向 cross-venue 而非 same-venue**
   - same-venue spot/perp basis 更容易被 funding 和微小搬砖压平；
   - 真要继续，下一步更像 cross-venue executable spread，而不是同所双腿 taker。

## 8. 下一步怎么测（必须项）

不要继续泛泛地说“basis 可能有用”。下一轮最小实验应该直接这样做：

### 8.1 最小实验 A：`1h admission × 5m/15m execution`
**研究假设**
- 若把 repo 的 `1h` basis-zscore 只当慢 admission，而不是直接按 `1h` next-open 执行，则 rich-perp 一侧在 `5m/15m` 上可能存在更低滑点的 close-out pocket。

**具体动作**
1. `1h` 上保留：`z >= 2` 的 rich-perp 触发；
2. 只做 `long spot + short perp` 单边；
3. `15m` 上等 basis 开始缩窄、或 microstructure 失衡转弱时进；
4. `5m` 上只优化 exit，不重新找入场；
5. 成本先跑 `2 / 4 / 6 / 8 bps`。

### 8.2 最小实验 B：加 shared gate，而不是再瞎调 z-score
优先加两类 gate：
1. **funding sign / magnitude gate**：只在正 funding 且 perp 明显偏贵时开 rich-perp 一侧；
2. **liquidity / spread gate**：只在 top-depth 足够厚、双腿 BBO 不太散时开。

### 8.3 最该先看的 3 个指标
1. `8 bps` 后仍为正的 **surviving trade ratio**
2. **entry-to-close realized slippage** 是否显著低于 bar-close 近似
3. rich-perp 单边版本的 **gross+funding per trade** 能否稳定抬到 `> 4 bps`

如果这三条里第一条都过不了，就别再给它加更复杂的模型层了。

## 9. 最后一行结论

> **这份 2025 delta-basis repo 值得收进研究池，不是因为它证明了 same-venue basis MR 很赚钱，而是因为它把这条 raw alpha 的完整壳和失败方式都写得足够清楚：alpha 本体不是零，但 broad taker 版 edge 只有 `0.35~0.78 bps/笔`，一上 `8 bps` 成本就全灭。对 short-cycle desk，真正该继续测的是 `1h admission × 5m/15m maker-first execution` 或直接转向 cross-venue richer pocket。**
