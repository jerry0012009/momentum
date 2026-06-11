# 别把这份 2025/26 mean-reversion repo 只读成“oversold bounce 教程”：对 short-cycle desk，更该先测的是「高量 1h 下跌冲击 → 反弹」这条 raw alpha——但 recent perp 迁移版基本只剩 BTC 还站得住
- 时间：2026-04-15 09:12 UTC
- 类型：2025/2026 GitHub repo source audit（`README.md` + `src/strategy.py` + `src/backtester.py` + `results/performance_metrics.json` + GitHub API metadata）+ Binance USDⓈ-M `15m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**当 major coin 在最近 `1h` 内出现“价格急跌（<= -2%）+ 成交量显著放大（>= 1.5x 过去 24h 平均 1h 成交量）”的联立冲击时，随后 `1~24h` 更容易出现反弹；但 recent Binance perp 迁移版显示，这条 edge 不能再被读成“所有 major 通吃”，而更像 BTC 主导、alts 需要更深 shock 才可能成立的 event-driven mean reversion。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha / single-asset / event-driven / mean-reversion / downside-shock / volume-confirmation / btc / eth / sol / perpetual / binance / 15m / 1h / 2h / 4h / 8h / 24h / repo / public-data / cost / risk
- 证据类型：repo 源码 + public-data portability probe

## 1. 这次看了什么
先回答 base alpha：**不是“RSI oversold 会反弹”这种泛化说法，而是更窄、更可计算的一条 event alpha——“高量急跌后的短期 bounce”。**

主材料是 2025 年末创建、2026 年初更新的 GitHub repo：
- **Author：** Skylar Shi
- **Year：** 2025/2026
- **Title：** *crypto-stat-arb*
- **Venue：** GitHub
- **DOI：** N/A
- **Readable URL：** <https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/README.md>
- **Repo URL：** <https://github.com/skylarshi123/crypto-stat-arb>
- **GitHub API URL：** <https://api.github.com/repos/skylarshi123/crypto-stat-arb>

repo 自己把假设写得很直白：
- `1h return <= -2%`
- `1h volume / 24h avg 1h volume >= 1.5x`
- long-only
- 测试 `4h / 8h / 12h / 24h` 持有期
- round-trip 成本按 `40 bps` 处理（代码里是 `20 bps/side`）
- 标的：`BTC / ETH / SOL / AVAX`

repo 报告给出的 headline 很猛：
- `24h` 为最佳持有期
- `34.33%` total return
- `72.7%` win rate
- `8.2%` max drawdown
- `22` 笔交易
- 研究窗口约 `20` 个交易日、`2,884` 个小时样本

但对我们 desk 真正重要的不是“这组回测数好不好看”，而是：

> **它给了一条很干净的 raw alpha 母式：先要求 downside shock 足够大，再要求成交量确认这不是普通噪声 bar，最后赌的是接下来几个小时到一天的反弹。**

这条 alpha 本体是可以一句话说清的，所以它确实属于 raw alpha，而不是 filter / overlay。

## 2. 核心结论
### 2.1 repo 最值得 intake 的，不是“24h 持有最优”，而是这条 event alpha 的 admission 逻辑
如果只把它读成“又一个均值回归策略”，会错过它真正有用的部分。

它最值钱的不是 exit，而是 **entry 的双条件联立**：
1. **先有明显下跌冲击**——不是随便回调一下；
2. **再要量能确认**——不是冷清市场里自己滑下去；
3. **然后才去赌 bounce。**

翻成人话就是：

> **先找“被砸得够明显、同时市场真的在交换筹码”的时刻，再去做短期反弹。**

这和很多只靠单一 RSI / Bollinger oversold 的壳不一样。它本质上是在用成交量把“普通回落”和“panic flush / forced unwind”分开。

### 2.2 但这条线对 short-cycle desk 的真正价值，不是“照抄 multi-major 24h hold”
repo 的实现更像一个 demo-quality baseline：
- 有 entry
- 有固定持有期扫描
- 有成本建模

但还缺很多 production 级部件：
- 没有更细的 admission 分层
- 没有明确 sizing 方案
- 没有 trend / liquidation / funding 级别的 veto
- 也没有解释“为什么 4 个币应该共用同一阈值”

所以 desk 化的正确读法不是：

> **“太好了，四个 major 都能拿来统一做高量急跌反弹。”**

而是：

> **“这是一条值得保留的 raw alpha 母线，但阈值、标的范围和持有期都必须重标定。”**

## 3. Binance USDⓈ-M `15m` portability probe：first verdict
我用本地已有 public-data cache 做了一个最小迁移版：
- 数据：
  - `reports/artifacts/rank32b_regime_5y_quarterly/cache_15m/BTCUSDT__365d__15m__perp.csv`
  - `reports/artifacts/rank32b_regime_5y_quarterly/cache_15m/ETHUSDT__365d__15m__perp.csv`
  - `reports/artifacts/rank32b_regime_5y_quarterly/cache_15m/SOLUSDT__365d__15m__perp.csv`
- 口径：
  - 用 `15m` 数据重采样成 `1h` 信号时钟；
  - 当某个 `1h` bar 满足 `ret_1h <= -2%` 且 `vol_ratio >= 1.5x` 时，**在下一根 `15m` 开盘价入场**；
  - 持有 `1h / 2h / 4h / 8h / 24h`；
  - 同一标的不重叠持仓；
  - 成本梯度看 `4 / 8 / 12 bps` round-trip。

### 3.1 先说一句最重要的话
> **recent Binance perp 上，这条线不能再被当成“通用 majors bounce shell”；它现在更像 BTC 有效、ETH/SOL 失效，或者至少要用更深 shock 才能救回来的事件型 alpha。**

### 3.2 BTC：这条线还活着，而且 `1~2h` 就有可观 bounce
`BTCUSDT` 在最近 `365d` 里只触发了 `33` 次信号，但质量不差：

- **`1h` 持有：**
  - `33` 笔
  - 平均 gross：`+21.4 bps`
  - gross 胜率：`63.6%`
  - `8 bps` 成本后平均仍有 **`+13.4 bps`**
- **`2h` 持有：**
  - `33` 笔
  - 平均 gross：**`+33.6 bps`**
  - 中位数：`+44.7 bps`
  - gross 胜率：`60.6%`
  - `8 bps` 成本后平均 **`+25.6 bps`**
- **`8h` 持有：**
  - `31` 笔
  - 平均 gross：`+46.1 bps`
  - gross 胜率：`58.1%`
- **`24h` 持有：**
  - `29` 笔
  - 平均 gross：`+38.5 bps`
  - gross 胜率：`55.2%`

这说明对 BTC 来说：
- bounce **不是必须等到 24h 才出现**；
- 更 desk-friendly 的 `1~2h` 持有期已经有明显正向期望；
- `8h` 虽然平均更高，但它已经更接近 swing pocket，而不是我们最偏好的 short-cycle 执行壳。

### 3.3 ETH / SOL：repo 那套固定阈值迁过来基本直接失效
同样的规则在 `ETHUSDT / SOLUSDT` 上最近 `365d` 基本不成立：

- `ETHUSDT`
  - `1h`：平均 gross `-9.3 bps`
  - `2h`：`-7.6 bps`
  - `4h`：`-57.5 bps`
  - `8h`：`-29.1 bps`
  - `24h`：`-34.3 bps`
- `SOLUSDT`
  - `1h`：平均 gross `-5.0 bps`
  - `2h`：`-20.4 bps`
  - `4h`：`-55.4 bps`
  - `8h`：`-36.3 bps`
  - `24h`：`-21.4 bps`

这很关键，因为它直接否定了一个懒惰读法：

> **“既然 repo 在几个 major 上都能做，那我直接复制到 majors perp basket 就行。”**

至少在 recent Binance perp 口径下，不行。

### 3.4 量能确认不是越高越好：BTC 也出现了 panic saturation
对 `BTCUSDT` 的 `2h` 持有结果按 `vol_ratio` 分桶后，出现了很有意思的非单调性：

- `3x~5x` 量能桶：平均 **`+69.1 bps`**
- `5x+` 极端量能桶：平均 **`-16.7 bps`**
- `2x~3x`：平均 `-68.9 bps`
- `1.5x~2x`：平均很高，但样本只有 `2` 个，不能当真

这意味着：

> **volume confirmation 不是“越大越稳”，而是存在一个更像“真 flush、但没进入事故区”的甜蜜点。**

对于 BTC，这个甜蜜点目前更像 `3x~5x`，而不是 `5x+` 的极端 panic。

### 3.5 ETH / SOL 不是完全没有 bounce，而是 repo 阈值太松
如果把 `ETH / SOL` 的 `2h` forward return 按 shock 深度分桶，会看到另一个非常重要的细节：

- `ETHUSDT`
  - `2~3%` shock：平均 `-14.9 bps`
  - `3~4%` shock：平均 `-64.8 bps`
  - `4~6%` shock：平均 **`+33.0 bps`**（样本 `7`）
  - `6%+` shock：平均 **`+500.4 bps`**（样本 `3`）
- `SOLUSDT`
  - `2~3%` shock：平均 `-42.9 bps`
  - `3~4%` shock：平均 `-17.0 bps`
  - `4~6%` shock：平均 **`+10.7 bps`**（样本 `12`）
  - `6%+` shock：平均 **`+181.4 bps`**（样本 `3`）

所以更准确的结论不是“ETH / SOL 没有反弹”，而是：

> **对更高 beta 的 major alt，`-2%` 这种 repo 阈值太松了，很多时候只是普通波动，不足以构成可交易的过冲事件。**

这正是 short-cycle desk 最需要知道的东西：**事件阈值必须按资产个性重标定。**

## 4. 为什么这东西和现有素材池不重复
表面上看，这轮也属于 mean reversion / shock fade 家族，似乎和前面已经写过的跳跌反转、oversold confluence 有亲缘关系；但它仍然有新增量，原因在于它补的是下面三件事同时成立的那块空位：

1. **alpha 母线极其干净：**
   不是多指标打分，而是一个明确的 event definition：`downside shock × volume confirmation`。

2. **它把“有没有筹码交换”放进了 alpha 本体：**
   volume 在这里不是装饰性的 filter，而是 event 有效性的关键组成。

3. **它直接暴露出“major-specific thresholding”这个研究问题：**
   BTC、ETH、SOL 并不应该共用同一套 `-2% + 1.5x` 阈值。

换句话说，这篇真正扩充的不是“又一个 bounce idea”，而是：

> **如何把“看起来一样的急跌”拆成可交易事件和不可交易噪声。**

## 4.5 策略拆解（必填）
- **方向属性：** 单资产 / event-driven / long-only mean reversion
- **基础 alpha：** 高量下跌冲击后，短周期价格更容易反弹
- **regime：** 这版 repo 没有显式 regime 层；但 recent 迁移结果暗示，不同资产实际上隐含了不同“有效 shock”阈值
- **filter / veto：** 最重要的不是再叠 RSI，而是 **shock 深度、volume bucket、以及是否进入极端 panic 区**
- **risk / sizing / execution overlay：** repo 只有固定持有期和成本建模；short-cycle 版本还需要补充 sizing、trend veto、以及事件后的 child execution

## 5. 可复刻的最小实验
### 5.1 最值得先做哪一版
我会把这条线先降维成两个子课题，而不是直接拿 repo 全量复制：

1. **BTC-only shock bounce baseline**
   - 因为 recent 迁移版里，BTC 是唯一已经明显过线的 major
2. **ETH / SOL deeper-shock rescue**
   - 因为数据提示它们不是没 bounce，而是 `-2%` 过于宽松

### 5.2 最小实验口径
先从最简单、最 desk-friendly 的版本开始：
- 市场：Binance USDⓈ-M majors perpetuals
- 主时钟：`15m`
- 信号时钟：`1h`
- 信号定义：
  - `ret_1h <= threshold_asset`
  - `1h_vol / avg_24h_1h_vol >= vol_threshold`
- 执行：next `15m` open 进场
- 持有：`1h / 2h / 4h`
- 成本：`4 / 8 / 12 bps` round-trip

### 5.3 第一轮最该测什么
1. **BTC 阈值细化**
   - `ret_1h <= -2% / -2.5% / -3%`
   - `vol_ratio` 分别试 `1.5x / 2x / 3x`
   - 重点看 `2h` 持有是否仍最稳

2. **ETH / SOL 资产特异阈值**
   - 不要再用 `-2%`
   - 直接测 `-4% / -5% / -6%`
   - 验证 deeper-shock rescue 是否能把 expectancy 拉回正值

3. **极端 panic veto**
   - BTC 上先验证 `5x+` 量能是否应直接 veto
   - 因为当前样本显示最极端量能未必最好，可能意味着趋势性事故而不是单纯 overreaction

4. **事件后的执行形态**
   - next `15m` open
   - next `5m` TWAP / 分批
   - signal 后等待 `1` 根 `5m` 再进
   - 看看是不是存在“让第一脚 knife 再飞一下”会更好

### 5.4 下一步怎么测
- **第一步：** 先只做 `BTCUSDT`，固定 `1h signal -> next 15m open -> hold 2h`，把阈值网格和成本梯度扫完整。
- **第二步：** 对 `ETH / SOL` 单独做 deeper-shock grid，不再共用 BTC 阈值。
- **第三步：** 在 BTC 上加入最便宜的两个 veto：`5x+ volume panic veto` 与 `trend-continuation veto`，看能否把坏事件过滤掉。
- **第四步：** 再决定这条线是升格成独立 raw alpha，还是降级成“所有 oversold / jump-reversal 书的 shared admission module”。

## 6. 风险与保留意见
- repo 自带的回测窗口很短，headline 数字漂亮，但 **样本量与市场阶段覆盖都有限**。
- recent Binance perp 迁移版已经明确提示：**这不是可直接拿去做 multi-major 的现成策略。**
- ETH / SOL 的正向 pocket 目前主要集中在更极端 shock，上样本很少，容易过拟合。
- `5x+` 极端量能在 BTC 上反而变差，说明最危险的不是“没信号”，而是**把事故当 oversold 接刀**。
- 这条线现在更像 **BTC event alpha + alt rescue hypothesis**，还不能被包装成稳定组合书。

## 7. 本轮产出文件
- 研究笔记：`research/quant_digests/2026-04-15_0912_volumeconfirmed-1h-downshock-bounce-alpha.md`
- portability artifacts：
  - `reports/artifacts/quant_digests/highvol-shock-bounce_probe_20260415_0910/summary.csv`
  - `reports/artifacts/quant_digests/highvol-shock-bounce_probe_20260415_0910/event_forward_returns.csv`
  - `reports/artifacts/quant_digests/highvol-shock-bounce_probe_20260415_0910/trade_list_no_overlap.csv`
  - `reports/artifacts/quant_digests/highvol-shock-bounce_probe_20260415_0910/meta.json`

## 8. 来源
1. **Skylar Shi. (2025/2026). _crypto-stat-arb_. GitHub repository.**
   - Repo URL: <https://github.com/skylarshi123/crypto-stat-arb>
   - Readable URL: <https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/README.md>
   - Key files:
     - <https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/src/strategy.py>
     - <https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/src/backtester.py>
     - <https://raw.githubusercontent.com/skylarshi123/crypto-stat-arb/main/results/performance_metrics.json>
   - GitHub API metadata: <https://api.github.com/repos/skylarshi123/crypto-stat-arb>

2. **Zaremba, A., Bilgin, M. H., Long, H., Mercik, A., & Szczygielski, J. J. (2021). _Up or down? Short-term reversal, momentum, and liquidity effects in cryptocurrency markets_. International Review of Financial Analysis, 78, 101908.**
   - DOI: `10.1016/j.irfa.2021.101908`
   - Readable URL: <https://ideas.repec.org/a/eee/finana/v78y2021ics1057521921002349.html>

## 9. 一句话结论
**这条 raw alpha 该保留，但别再把它当“所有 major 都能统一做的高量急跌反弹”：recent short-cycle perp 版目前更像 BTC 专属母线，ETH/SOL 要先做 deeper-shock rescue，才有资格进入下一轮。**
