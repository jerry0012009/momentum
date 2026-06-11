# 别把 risk-managed momentum 只当“低波动防身”：这篇 2025 FRL 对 desk 更该先测的是「短窗 XS momentum × inverse-vol scaling」完整策略，但当前 15m transfer 仍不过线
- 时间：2026-03-27 10:16 UTC
- 类型：论文
- 主题类型：overlay
- 基础 alpha：cross-sectional momentum（同一时点做多近期赢家、做空近期输家），这里再叠加 inverse-vol / risk-managed sizing。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：overlay/cross-sectional/momentum/risk-managed/inverse-volatility/sizing/wml/market-neutral/binance/perpetual/15m/5m/1m/3m/paper/external-data/cost
- 证据类型：论文摘要 + publisher section snippets（abstract-only / weak-to-medium evidence）+ Binance Futures 公共 `15m` 最小快检

## 1. 这次看了什么
这次主线看的是 **Ao Yang (2025), _Cryptocurrency market risk-managed momentum strategies_**, 发表在 **Finance Research Letters**。

这篇东西和我们前几天已经 intake 过的 **Han / Kang / Ryu (2024)**《Time-Series and Cross-Sectional Momentum in the Cryptocurrency Market》衔接得很顺：前一篇更像在问 **plain crypto momentum 到底有没有、尤其 XS 那支有多脆弱**；这一篇则是在问 **如果 plain XS momentum 本体不够稳，用 Barroso & Santa-Clara (2015) 式的 risk-managed scaling，能不能把它变成更像完整策略的东西**。

一句话先说：**base alpha 很清楚，就是横截面动量 WML；risk management 不是另起炉灶，而是给这个 raw alpha 加一个 inverse-vol sizing 外壳。**

## 2. 核心结论
- **一句话核心结论**：这篇 2025 FRL 想告诉我们的不是“低波动更安全”，而是 **在论文的周频 crypto 横截面里，inverse-vol risk scaling 能把 plain WML 做得更像能落地的完整策略；但搬到我们关心的 `15m` perp 后，它并不会自动救活短周期 edge。**
- **一句话它是怎么证明的**：论文用 crypto 横截面周频回测 + transaction cost / short-sale constraint / 不同 formation-holding 的 robustness 做证明；我这轮再用 Binance Futures 公共 `15m` 数据做了一个 short-cycle transfer check。

论文摘要页和 section snippets 给出的关键数字很明确：
- conventional momentum 的平均 **weekly return 从 `3.18%` 提到 `3.47%`**；
- annualized **Sharpe 从 `1.12` 提到 `1.42`**；
- 论文强调 crypto 和 equity 的区别在于：这里的改进**主要来自收益增强，而不是像股票那样主要靠防 momentum crash**；
- 文中还给了两个很有用的辅助数字：平均 scaling weight 大约 **`1.14`**（对比 equity 文献里约 `0.9`），excess kurtosis 从 **`63.89` 降到 `47.32`**，说明它不是简单“缩风险”，而更像在 crypto 里**愿意在较低估计波动时放大原始 WML 仓位**。

所以它对 desk 最有价值的地方，是把一个原本偏研究型的 `WML` 排名信号，推进成 **`signal + sizing + robustness`** 的完整策略骨架。

## 3. 为什么和当前项目有关
这篇主题虽然按字段该归为 `overlay`，但它不是那种“脱离 alpha 本体的共享风控建议”，而是：
- 明确服务于一个**已有 raw alpha 家族**：`cross-sectional momentum`；
- 而且已经给出**完整策略定义**：formation / holding / long-short construction / risk scaling / friction robustness；
- 正好承接我们最近的学习进展：
  - 已经 intake 了很多 `pairs / stat-arb / XS reversal / relative value`；
  - 也已经看过 plain crypto momentum 在 realistic assumptions 下并不总是好看；
  - 现在需要知道：**若 raw alpha 本体一般，inverse-vol / risk-managed sizing 能不能把它从“研究概念”推进成“可部署策略”。**

换句话说，这篇不是在和 raw alpha 抢位置，而是在回答一个更现实的问题：**“如果我真想保留 XS momentum 这条支线，应该怎么把它做完整？”**

## 3.5 策略拆解（必填）
- 方向属性：`overlay`
- 基础 alpha：`cross-sectional momentum`（做多近期赢家、做空近期输家）
- 是否完整策略：**是**。因为它不只给 rank signal，还给了 `holding / rebalancing / volatility scaling / robustness`。
- 论文主口径（可读到的 section snippet）：
  - **formation**：`2-week`
  - **holding**：`1-week`
  - **组合**：按 formation return 把币种分成 quintiles，**long Winner / short Loser**，构成 **value-weighted WML**
  - **risk layer**：对 WML 叠加 `risk-managed` / `inverse-vol` 类型的 scaling
- desk 化翻译：
  - `raw alpha`：短窗横截面赢家-输家排序
  - `overlay`：不是固定 1x 下 WML，而是按最近 realized vol 调整 gross exposure
  - `risk/execution`：如果估计波动高，就缩；如果估计波动低，就放；但前提是 **原始 WML 至少别先是负的**

## 4. 可复刻的最小实验
### 4.1 论文可直接搬的最小骨架
如果先不纠结论文全文拿不到的细节，最小可复现实验已经够清楚：
1. 选一组可做多空的 liquid crypto universe；
2. 用过去一个 formation window 的横截面收益排序；
3. long top bucket / short bottom bucket，形成 WML；
4. 再用 rolling realized vol 对 WML gross exposure 做 inverse-vol scaling；
5. 比较 plain WML 与 risk-managed WML 的 return / Sharpe / tail risk / cost 后存活率。

### 4.2 我这轮 short-cycle transfer check
为了看它和当前 desk 的 `15m` 是否真有关系，我做了一个最小迁移，不是照抄论文周频，而是直接往 intraday 压：
- **数据源**：Binance Futures 公共 `15m klines`
- **公开性**：完全公开可得，无需私有数据
- **币种**：`BTC / ETH / SOL / XRP / BNB / DOGE / ADA / LINK / LTC / AVAX` 十个主流 USDT perpetual
- **样本**：`2026-01-23 22:15 UTC ~ 2026-03-27 10:00 UTC`
- **short-cycle 映射口径**：
  - formation = `32` 根 `15m`（约 `8h`）
  - holding = `8` 根 `15m`（约 `2h`）或 `16` 根 `15m`（约 `4h`）
  - 每次 rebalance 取横截面 top / bottom quintile-ish（10 个币时即 top 2 / bottom 2）
  - plain 版：等权 long winners / short losers
  - risk-managed 版：对 WML 用 trailing realized vol 做 scaling（clip 到 `0.5x~1.5x`，避免极端爆表）

### 4.3 快检结果
结果挺诚实，而且对 desk 很有用：
- **`8h formation / 2h hold` plain WML**：平均每次换仓约 **`-0.33 bps`**，累计约 **`-3.28%`**；
- 同口径 **risk-managed WML**：平均约 **`-1.53 bps`**，累计约 **`-11.53%`**；
- **`8h formation / 4h hold` plain WML**：平均约 **`-0.90 bps`**；risk-managed 后约 **`-2.65 bps`**；
- 更短的 **`4h / 2h`** 口径也没活：plain 约 **`-2.02 bps`**，risk-managed 后约 **`-3.08 bps`**；
- 整个 quick grid 里，risk-managed 版的平均 weight 大约都在 **`1.10~1.13x`**，说明最近这段样本里它多数时候是在**加杠杆一个已经偏负的短窗 WML**，自然越放越亏。

### 4.4 desk 化解释
这组结果传达的不是“risk-managed momentum 没用”，而是更精确的两句话：
1. **inverse-vol sizing 不能把一个当前已经不成立的短周期 XS momentum 硬救活**；
2. 如果未来真要把它搬进 `1m/3m/5m/15m`，先得找到 **plain WML 仍有残余 edge 的 pocket**，然后 scaling 才值得上。

## 5. 可以怎么直接落成完整策略 / 规则
如果真要把它写成策略，不要只写“低波放大，高波缩小”，而要写成完整流水线：

1. **signal 层**
   - 每 `1h / 2h / 4h` 做一次横截面排名；
   - 使用 `4h/8h/24h` formation 的 past return；
   - long top quantile / short bottom quantile。

2. **portfolio 层**
   - 默认 market-neutral；
   - 单币权重先 equal-weight，后续再看是否要改成 liquidity-cap 或 inverse-vol within leg。

3. **risk-managed 层**
   - 对整个 WML spread 做 scaling，而不是对单腿各自瞎缩放；
   - `target_gross ~ target_vol / realized_vol(WML)`；
   - 设 clip，例如 `0.5x ~ 1.5x`，防止在极低波时无上限加大。

4. **execution / cost 层**
   - 一定要先跑 friction ladder：`1/2/4/6 bps`；
   - 若 alpha 只在 `0~1 bps` 手续费下活，就不要当主线；
   - 尽量放到高流动、低 funding 干扰、maker 更容易成交的币组。

5. **go/no-go 规则**
   - 先看 plain WML 是否 > 0；
   - 再看 scaling 后 Sharpe / drawdown 是否改善；
   - 如果 plain 已经负，risk-managed 还继续给正向 gross，那本质上是在**更聪明地放大错误方向**。

## 6. 风险与边界
- **证据强度要诚实**：这轮外部材料能直接拿到的是 ScienceDirect 摘要页、RePEc 摘要与 publisher section snippets，**不是全文可读版本**；所以这篇目前只能算 `abstract-only / weak-to-medium evidence`，不是最高证据等级。
- 论文主结论是**周频** crypto 横截面，不是为 `15m` 设计的；我这轮 short-cycle 映射只是在测“能不能 transfer”，不是替代原论文。
- 我这轮 quick check 采用的是 **non-overlapping 15m WML transfer** 与一个 desk 化 scaling 版本，不保证和论文实现完全同口径；但对当前任务已经足够回答：**短周期能不能先活下来。**
- 当前样本只有最近约两个月，且多为空头/震荡混合环境；若要更认真判断，至少要再拉长到多个 regime。

## 7. 下一步怎么测
1. **先找 plain XS momentum 的幸存 pocket，再谈 risk-managed**
   - 先按 universe 分层：`top-10 liquidity`、`mid-cap`、`alts ex majors`；
   - 再按 formation / hold 网格看 plain WML 何处不再系统为负。

2. **把 momentum 与 reversal 分开测，不要混成一个“排名策略”**
   - 同一套 universe 上并排跑：`XS momentum` vs `XS reversal`；
   - 如果短周期里 reversal 明显更强，那 risk-managed momentum 就不该继续占主线资源。

3. **改成 conditionally-on 的 scaling**
   - 不是永远 `target_vol / rv`；
   - 而是只有当 plain WML 近窗 hit-rate / breadth / dispersion 同时在线时，才允许放大 gross。

4. **升级到更像 desk 的特征**
   - 不只用 past return 排名；
   - 加入 `funding dispersion / quote-volume breadth / taker flow breadth / beta-neutral residual return`，看看 risk-managed 是否更适合服务这些“更干净的 XS alpha”。

5. **成本一定要和仓位联动**
   - 一旦 scaling 把 gross 拉高，成交成本与滑点不再线性；
   - 所以回测里不能只放固定费率，至少要加一个随 gross / participation 上升的 impact proxy。

## 8. 来源
- Yang, Ao (2025). *Cryptocurrency market risk-managed momentum strategies*. **Finance Research Letters**. DOI: `10.1016/j.frl.2025.107879`
- DOI URL: https://doi.org/10.1016/j.frl.2025.107879
- Readable URL: https://www.sciencedirect.com/science/article/pii/S1544612325011377
- RePEc abstract page: https://ideas.repec.org/a/eee/finlet/v85y2025ipas1544612325011377.html
- Alternate readable abstract mirror: https://colab.ws/articles/10.1016/j.frl.2025.107879
- Repo URL：未见官方 repo
- 方法母体：Barroso, P.; Santa-Clara, P. (2015). *Momentum has its moments*.

## 9. 本地产物
- 快检目录：`reports/artifacts/quant_digests/crypto_risk_managed_xs_momentum_20260327/`
- 关键文件：
  - `summary.json`
  - `grid_summary.json`
  - `wml_15m_8h4h_timeseries.csv`
