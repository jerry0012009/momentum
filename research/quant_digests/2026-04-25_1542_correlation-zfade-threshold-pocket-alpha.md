# 别把这个相关性 stat-arb 小仓只读成“Z-score 教学脚本”：对 short-cycle crypto desk，更该先回答的是「high-corr pair ratio z-score fade × threshold escalation」这条 raw alpha 在 `5m/15m` 上还有没有 pocket
- 时间：2026-04-25 15:42 UTC
- 类型：GitHub / repo
- 主题类型：raw alpha
- 基础 alpha：高相关交易对的价格比值短时偏离历史均值后，后续更容易向均值回归；交易上对应 long laggard / short leader 的 spread fade
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但默认要带成本 veto；taker 四腿口径下不应直接裸上）
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / correlation / zscore / threshold-escalation / 5m / 15m / repo / public-data / cost / risk
- 证据类型：工程经验 + public-data portability probe

## 1. 这次看了什么
这次看的是 2026 GitHub repo：ApexQuant-Dev, **Binance Correlation & Stat-Arb Suite**（`binance-correlation-stat-arb`）。repo 很小，核心文件只有 `README.md`、`correlation_bot.py`、`phase1_data_fetch_correlation.py`；主想法也很直白：先用 rolling correlation 找高相关 pair，再对价格比值做 rolling z-score，`|z| > 2` 时做均值回复。

- Authors / Year / Title / Venue：ApexQuant-Dev (2026), *Binance Correlation & Stat-Arb Suite*, GitHub repo
- Repo URL：<https://github.com/ApexQuant-Dev/binance-correlation-stat-arb>
- Readable URL：<https://raw.githubusercontent.com/ApexQuant-Dev/binance-correlation-stat-arb/main/README.md>
- 关键源码：
  - <https://raw.githubusercontent.com/ApexQuant-Dev/binance-correlation-stat-arb/main/correlation_bot.py>
  - <https://raw.githubusercontent.com/ApexQuant-Dev/binance-correlation-stat-arb/main/phase1_data_fetch_correlation.py>

## 2. 核心结论
- **一句话核心结论**：这不是“又一个 pairs 教材”那么简单；真正值得 desk 先测的是 **高相关 pair 的极端 ratio 偏离，在 `5m/15m` 上是否能留下可交易 pocket**，而不是先追求复杂 cointegration 包装。
- repo 原版信号很朴素：`1m`、`30` 根 lookback、ratio z-score、`|z|>2` 即提示反向配对；优点是**极易复现**，缺点是**没有认真处理成本、持有窗、仓位和 pair admission**。
- 我用 Binance USDⓈ-M 公共数据做最小 portability probe（`SOL/AVAX`、`LINK/UNI`、`ARB/OP`、`APT/SEI`、`ETH/BTC`，约 `18000` 根 `5m`）后发现：pooled 平均 **gross 约 `+2.24 bps/笔`**、胜率约 **`57.2%`**，但按四腿 taker 粗扣 **`16 bps`** 后平均 **net 约 `-13.76 bps/笔`**，说明**裸 `|z|>2` pair fade 在 taker 口径下明显不够厚**。
- 但 pocket 不是完全没有。参数 sweep 后，`LINK/UNI` 在 `15m`、`lookback=96`、`corr>0.7`、`|z|>3`、`max_hold=12 bars` 时，平均 **gross 约 `+12.29 bps/笔`**、胜率 **`73.3%`**、交易数 **`60`**；若按较乐观 **`12 bps`** 总成本，平均 **net 约 `+0.29 bps/笔`**，但按 **`16 bps`** 仍是 **`-3.71 bps/笔`**。
- 另一个可留样本 pocket 是 `LINK/UNI 5m`：`lookback=144`、`|z|>3`、`max_hold=12 bars`，平均 **gross 约 `+14.32 bps/笔`**、胜率 **`65.2%`**、交易数 **`69`**；在 **`12 bps`** 口径下还有 **`+2.32 bps/笔`**，但在 **`16 bps`** 下仍略负。

## 3. 为什么和当前项目有关
这篇东西和当前 `momentum` 主线有关，不是因为它“证明了 pair trading 永远有效”，而是因为它提供了一条**足够轻量、可快速做 first verdict 的 pairs/stat-arb raw alpha**：

1. **数据公开可得**：只要 Binance perp klines 就能起步；
2. **规则可写得很清楚**：pair selection、entry、exit、timeout、成本 veto 都能直接落成；
3. **和最近 desk intake 互补**：最近虽然已经看了很多 cointegration / PCA / basket stat-arb，但这条更像 **“先把最朴素的 high-corr ratio fade 跑一遍，看边有没有厚到值得继续上更复杂模型”**；
4. **对 `1m/3m/5m/15m` 都友好**：它不是只能活在日频论文里的慢信号。

## 3.5 策略拆解（必填）
### Base alpha
- 若两条高度相关的币在短窗内突然出现相对错位，且错位幅度已经到历史分布尾部，那么后续更容易发生 **leader 回落 / laggard catch-up**，表现为 spread/ratio 回归。

### Entry
- 先做 pair admission：最近 `lookback` 根 log-return correlation `> 0.7`；
- 计算 `ratio = price_A / price_B` 的 rolling z-score；
- `z > +z_th`：做 **short A / long B**；
- `z < -z_th`：做 **long A / short B**；
- 对 short-cycle desk，更值得先测的不是 repo 的默认 `|z|>2`，而是 **`|z|>2.5 / 3.0` 的 threshold escalation**。

### Exit
- 第一优先：z-score 回到 `0` 附近即平；
- 第二优先：`max_hold` 到时强平；
- 当前 probe 里较像样的 pocket 多出现在 **`8~12 bars`** 的 time stop，而不是极短 `1~3 bars`。

### Sizing
- 先用最简单的 dollar-neutral 或 beta-lite notional（两腿名义金额相等）；
- 后续再补 rolling vol scaling / residual-vol targeting，先别一上来就过拟合 hedge ratio。

### Risk
- 若 rolling corr 在持仓中掉到阈值以下，或 ratio 继续向不利方向扩张到更高分位，可直接 kill；
- 单 pair 限仓，避免多个高度同质的 L1 pair 同时堆满。

### Cost
- 这是这条线的生死点。repo 几乎没认真处理成本，但真实 pair 交易至少要想清楚：
  - 四腿 taker 的总费用/滑点口径；
  - maker-first 是否可行；
  - 是否只在 `gross edge > cost + safety buffer` 时入场；
  - 是否要限制在流动性更好的 pair pocket（例如 `LINK/UNI`、`SOL/AVAX` 这类 sector 同类）。

## 4. 它是怎么证明这件事的
repo 本身的证明强度很弱，更多是**一个可复现的工程骨架**：
- `correlation_bot.py` 直接把 signal 写成 ratio z-score 偏离；
- `phase1_data_fetch_correlation.py` 先做 correlation matrix，等于告诉你“先做 pair admission，再做交易”；
- 真正的证据强度来自我补做的 public-data probe：
  - `5m` pooled baseline：5 组 pair 共 **`2075` 笔**，平均 **gross `+2.24 bps/笔`**，但 **net16 `-13.76 bps/笔`**；
  - `15m LINK/UNI` pocket：`lookback=96`、`|z|>3`、`max_hold=12`，**gross `+12.29 bps/笔`**；
  - `5m LINK/UNI` pocket：`lookback=144`、`|z|>3`、`max_hold=12`，**gross `+14.32 bps/笔`**。

## 5. 对当前 desk 的可复现启发
最值得借的不是 repo 的代码质量，而是它的**研究顺序**：
1. 先只看公开数据能不能找到高相关 pair；
2. 再用最朴素的 ratio z-score 做 raw-alpha first verdict；
3. 如果粗糙版本都没 gross edge，就别急着上 Johansen / Kalman / OU fancy 外壳；
4. 如果只有少数 pocket 存活，就把它读成 **“thresholded pair router”**，不是 always-on stat-arb 引擎。

## 6. 最小实验怎么做
建议直接做一个很小但诚实的 `5m/15m` 实验：
- universe：`SOL/AVAX`、`LINK/UNI`、`ARB/OP`、`APT/SEI`、`ETH/BTC`
- pair admission：rolling correlation `> 0.7`
- signal：rolling ratio z-score，分别测 `|z|>2 / 2.5 / 3`
- exit：`z` 过零 or `8/12 bars` timeout
- cost ladder：`8 / 12 / 16 bps` 三档
- 评估：trade count、gross/net bps、pair-by-pair pocket、同 bar 多 pair 冲突

## 7. 下一步怎么测
下一步别继续泛泛讲“相关性 stat-arb”，直接测这 4 件事：
1. **maker-first 版本**：只对 `LINK/UNI`、`SOL/AVAX` 做 post-only / queue-limited 模拟，看看能不能把总成本从 `16 bps` 压到 `<=12 bps`；
2. **残差化版本**：把单纯 ratio 改成 `beta-adjusted residual`，比较是否能稳定抬高极端阈值 pocket 的 gross；
3. **shared gate**：加入 sector-relative volume shock 或 funding divergence，看是否能把 `|z|>3` 的 entry 再压缩到更厚的子样本；
4. **portfolio 层**：若同一时点多组 pair 同时亮灯，先做 conflict netting，避免把同一板块的同向风险叠满。

## 8. 风险与边界
- 这条线目前更像 **raw alpha 候选 + 完整策略壳**，还不是“已证明可直接 taker 实盘”的稳态策略；
- correlation 本身不等于可交易配对关系，极端市况下会一起崩；
- 当前最该警惕的是：看起来 win rate 不低，但实际上 edge 很薄，**稍微多一点费率/滑点就全没了**。

## 9. 本地实验产物
- `reports/artifacts/quant_digests/2026-04-25_correlation_pair_zfade_probe_summary.csv`
- `reports/artifacts/quant_digests/2026-04-25_correlation_pair_zfade_probe_trades.csv`
- `reports/artifacts/quant_digests/2026-04-25_correlation_pair_zfade_sweep.csv`
