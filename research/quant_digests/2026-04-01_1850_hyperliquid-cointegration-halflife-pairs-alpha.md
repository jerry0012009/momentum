# 别把这份 2026 Hyperliquid 双引擎 repo 只读成“大而全机器人”：对 short-cycle desk，更该先拆的是「cointegration scan × half-life gate × spread z-score fade」这条 pairs raw alpha

- 时间：2026-04-01 18:50 UTC
- 类型：2026 GitHub 新仓库 source audit（`README.md` + `examples/README.md` + `examples/download_data.py` + `tests/test_output.md` + GitHub API metadata）
- 主题类型：raw alpha
- 基础 alpha：**cointegrated perp pair spread mean reversion**；先用 `ADF + Hurst + half-life` 过滤可交易 pair，再对动态 hedge ratio 残差做 `z-score fade`。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/half-life/adf/hurst/dynamic-hedge-ratio/spread-zscore/hyperliquid/binance/perpetual/1h/15m/5m/3m/1m/repo/public-data/cost/execution
- 证据类型：GitHub repo README + data-download script + tests summary + GitHub API metadata（repo-based）

## 1. 这次看了什么
**这轮更值得 intake 的，不是 repo 里那个“全自动双引擎 bot”叙事，而是它明明白白暴露出来的一条可单独拆走的 raw alpha：先从 `70+` 个 Hyperliquid/币安可映射永续里扫 `2400+` 个 pair，筛出 `612` 个 viable 组合，再只留下 `12` 个 live candidate；交易层做的不是方向预测，而是 cointegration spread 的均值回复。**

最关键的硬数据有三组：
- pair discovery 从 **`2400+` 组合 → `612` viable → `12` live candidates**；
- best pairs 的 repo 自报全样本收益是 **`+120% ~ +380%`**；
- 同一批结果里给出 **`59% ~ 94%` win rate、`2.0 ~ 33.5` profit factor**，而且 README 明写这些数已经包含 **`0.035%` taker fee + `1 bp` slippage simulation**。

这就足够把主题定性为：
**不是“又一个 bot 工程”，而是一条可直接进素材池的 pairs / stat-arb raw alpha blueprint。**

## 2. 先回答一句：这篇东西的 base alpha 是什么？
这轮的 **base alpha 很清楚**：

- 不是 SMC liquidity sweep；
- 不是 ML fill predictor；
- 不是 Telegram/风控壳；
- 而是 **cointegrated pair spread 偏离后向均值回归**。

翻成人话：
**两条长期一起走的永续合约短时偏离得太远，就做 long cheap / short rich，赌 spread 收回来。**

repo 里真正有研究价值的“旁支”是：
- 不是再发明新的 MR 本体；
- 而是把 **`ADF + Hurst + half-life + dynamic hedge ratio + cointegration-break kill switch`** 这一整套筛选/风控壳写成了一个可直接迁移到 desk 的 pairs sleeve。

所以这轮应归类为：
- `raw alpha`
- `pairs / stat-arb / relative value / mean reversion`
- 但天然依赖一层 **pair-selection gate + execution shell**

## 3. 为什么这轮值得写，而不是继续找一个更炫的 headline
这轮值得 intake，不是因为 repo 叙事大，而是因为它满足 bot7 当前更高优先级：

1. **base alpha 清楚。** 就是 spread MR，不是抽象 overlay。
2. **可以独立成完整策略。** entry / exit / sizing / risk / cost 都能落下来。
3. **和 current desk 完全同向。** Hyperliquid / Binance perpetual、1h 扫描、15m/5m 可执行。
4. **旁支价值高。** 即使 repo 不公开精确阈值，它公开的 pair discovery 管线、成本口径和 kill-switch 思路，也足够直接变成我们自己的最小实验。
5. **它补的是 raw alpha 素材池，而不是再补一个泛 gate。**

## 4. 来源信息
### 主来源（repo）
- **Author / Maintainer：** Jotanune（GitHub）
- **Year：** 2026
- **Title：** *CryptoGuardian*
- **Venue：** GitHub repository
- **Repo URL：** <https://github.com/Jotanune/CryptoGuardian>
- **GitHub API metadata：** <https://api.github.com/repos/Jotanune/CryptoGuardian>
- **README（raw）：** <https://raw.githubusercontent.com/Jotanune/CryptoGuardian/main/README.md>
- **Examples README（raw）：** <https://raw.githubusercontent.com/Jotanune/CryptoGuardian/main/examples/README.md>
- **Data download script（raw）：** <https://raw.githubusercontent.com/Jotanune/CryptoGuardian/main/examples/download_data.py>
- **Tests summary（raw）：** <https://raw.githubusercontent.com/Jotanune/CryptoGuardian/main/tests/test_output.md>

### 方法锚点（repo 明写）
- **Cointegration methodology：** Engle–Granger / ADF-test style pair screening
- **Additional filters：** Hurst exponent、half-life
- **Execution note：** atomic pairs execution、maker/taker fee routing、cointegration-break kill switch

说明：这轮是 **repo-based** intake，不是某篇已发表 paper 的复刻卡；但它公开的信息已经足够让我们把 pairs sleeve 单独抽出来做 desk 版实验。

## 5. repo 实际公开了哪些对研究有用的东西
### 5.1 Universe 和数据管线并不空泛
repo 自带的公开脚本 `examples/download_data.py` 给了很实用的复现口径：

- 支持 **Hyperliquid** 和 **Binance Futures** 公共 OHLCV；
- 币种映射覆盖 **`70+` perpetuals**；
- 支持 `1m / 5m / 15m / 1h / 4h / 1d`；
- README 示例里明确写了：
  - `python download_data.py --all-scan 1h --source binance`
  - 用于 **all-scan + cointegration scanning**。

这点很关键：
**它不是嘴上说 pairs，而是把“先在 1h 上扫全市场 pair universe”这个 discovery 步骤写死到了公开脚本里。**

### 5.2 Pair discovery 管线披露得比很多 repo 更完整
README 里 pair sleeve 的公开流程是：

1. 下载 `70+` 个 Hyperliquid-listed perpetuals 的 OHLCV；
2. 扫描 **`2400+` pair combinations**；
3. 用 **ADF** 做 cointegration 筛选；
4. 再用 **half-life**（回复速度）和 **Hurst exponent** 继续过滤；
5. 对 entry / exit 参数做 grid search；
6. 用 **60/40** 与 **70/30** walk-forward 验证；
7. 最后按 **OOS Sharpe / profit factor** 排名，留下 **`12` 个** live candidate。

翻成人话：
**repo 的真贡献，不是“z-score 回归”这四个字，而是把 pair 从 universe discovery → statistical sanity → OOS ranking → live shortlist 的整条流水线讲清楚了。**

### 5.3 交易逻辑虽然没给阈值，但核心骨架已经足够明确
README 明写 pairs engine 是：

- **cointegration-based pairs trading**
- **Engle–Granger methodology**
- **entries/exits driven by z-score of the spread**
- **dynamic hedge ratio recalculation**
- **automatic position closure if cointegration breaks（p-value threshold）**

这已经把我们最关心的几件事说清：
- alpha 本体：spread z-score fade；
- 风险约束：cointegration 失效就平；
- 参数更新：beta 不是固定死值，而是 rolling / dynamic；
- 交易对象：pair，不是单腿方向单押。

### 5.4 成本口径是这轮最值钱的细节之一
README 对 pairs 结果的注释里明确写：

> All results include `0.035%` taker fees + `1 bps` slippage simulation.

也就是：
- **单边 taker fee = 3.5 bps**；
- 还额外加了 **1 bp slippage**；
- 而 pairs 策略是 **双腿 × 入场 × 出场**，真实 round-trip friction 不能按单腿思考。

这对 desk 的启发非常直接：
**5m/1m 上如果你还默认两腿都 taker，这条 alpha 很容易在真实成本下被直接磨死。**

## 6. 3 个最值得记住的硬数据点
1. **Discovery funnel：** `2400+` pair combinations → `612` viable → `12` live candidates。
2. **Self-reported pair performance：** best pairs 全样本收益 **`+120% ~ +380%`**。
3. **Self-reported quality + friction：** **`59% ~ 94%` win rate、`2.0 ~ 33.5` profit factor**，并注明已计入 **`0.035% taker fee + 1 bp slippage`**。

注意：这些都是 repo 披露值，不是我们独立复核后的本地结果；但足够说明它不是空口说“pairs 有效”。

## 7. 对 current desk 真正该偷走的是什么
如果把这份 repo 读成“又一个大而全 bot”，你会被工程壳分散注意力。

对 short-cycle desk，真正该偷走的是这条完整策略读法：

1. **raw alpha 本体：** cointegrated spread mean reversion；
2. **universe gate：** 先全市场扫，再用 ADF / Hurst / half-life 做前置过滤；
3. **entry/exit：** 用残差 z-score 做 admission / close；
4. **risk veto：** cointegration break / p-value deterioration / max-hold / residual runaway；
5. **execution shell：** atomic pairs execution + maker/taker decision + slippage-aware routing。

也就是说，这轮真正值得 intake 的不是“repo 赚了多少”，而是：
**它把 pairs raw alpha 从“理论上能做”推进到了“该按什么顺序筛、在哪一层死、该怎样把成本写进去”的工程化 blueprint。**

## 8. 和当前 `1m / 3m / 5m / 15m` 的关系
### 8.1 不要把 1h pair discovery 和 5m execution 混成一件事
repo 的公开 discovery 示例是 `1h`。
这很合理，因为：
- cointegration / half-life / Hurst 本身就更适合在略慢一些的 bar 上做稳定估计；
- 如果直接在 `1m` 上扫 universe，microstructure 噪音会把 pair 选择搞脏。

对当前 desk 更合理的映射是：
- **`1h`：** pair discovery / beta estimation / half-life filter
- **`15m`：** 主要交易决策 bar
- **`5m`：** admission refinement / spread 回踩确认 / child-order slicing
- **`1m / 3m`：** 只做 execution，不要拿来当主 pair-selection 频率

### 8.2 这条 alpha 更像“慢筛选 + 快执行”，不是 ultra-fast scalp
pairs MR 在 crypto 上常见的误区是：
- 看到 z-score 偏离就想在 `1m` 上高频抄；
- 结果 pair 关系本身都不稳定，还被 fee + leg risk 吃掉。

这份 repo 反而提醒了一条更靠谱的路：
**先用更慢的窗把 pair 选干净，再在更快的 bar 上执行。**

### 8.3 第一刀别铺全市场，先从 liquid majors / upper-mid 开始
虽然 repo 扫了 `70+` 币，但我们做最小实验没必要第一刀就跟满。
更适合先试的，是：
- BTC / ETH / SOL / BNB / XRP
- LINK / AVAX / DOGE / ADA / LTC
- 以及 `L1/L2`、`DeFi` 这种有经济叙事同类的 pair bucket

原因不是“这些最容易赚钱”，而是：
**这些合约更有机会同时满足流动性、稳定 beta、较低 legging friction。**

## 9. 可复刻的最小实验
### 实验 A：weekly pair discovery（最优先）
- **Universe：** `20 ~ 30` 个最液态 USDT-margined / Hyperliquid perpetuals
- **Bar：** `1h`
- **样本窗：** 最近 `180 ~ 365` 天
- **筛选流程：**
  1. 先做 rolling correlation 初筛；
  2. 再做 Engle–Granger / ADF；
  3. 只保留 **Hurst < 0.5** 的 spread；
  4. half-life 只保留在一个可交易区间，例如 `2 ~ 48` bars；
  5. 对 rolling OLS / Kalman beta 都留一个分支。

目标不是直接找到最赚钱的 pair，而是先回答：
**哪些 pair 在 2026 的 liquid perp universe 里，还配得上被拿去做 15m execution。**

### 实验 B：15m spread z-score raw alpha
- **Signal：** 对 hedge 后残差做 rolling z-score
- **Entry：** `|z| >= 2.0 / 2.5 / 3.0`
- **Exit：** `z` 回到 `0 ~ 0.5` 区间
- **Stop：** `|z| >= 3.5 / 4.0` 或 residual variance 爆掉
- **Max hold：** `8 / 16 / 24 / 32` 根 `15m`
- **Sizing：** dollar-neutral / beta-neutral，pair vol-target
- **Risk：** 单 pair gross cap + portfolio heat cap

这一步要回答的是：
**after-cost 的 pairs raw alpha 在 `15m` 上有没有基本生命体征。**

### 实验 C：5m execution refinement
只在实验 B 有生命体征后再下钻：
- `15m` 负责触发候选；
- `5m` 决定是立即双腿吃单，还是做 maker-first / passive-leg-first；
- 比较三种模式：
  1. 双腿都 taker；
  2. 主腿 maker、对冲腿保护性 taker；
  3. maker-first，超时 fallback 到 taker。

### 实验 D：kill-switch ablation
把 repo 里最值钱的风险层单独拆出来测：
- **No kill switch**
- **cointegration-break kill switch**
- **cointegration-break + max-hold 双 kill**

如果 kill switch 不是提升 OOS，而只是让 IS 更好看，就别神化它。

## 10. 怎样把它落成完整策略（entry / exit / sizing / risk / cost）
### 10.1 Entry
- 只在 pair 已通过最新一次 `ADF + Hurst + half-life` 过滤后才允许交易；
- 用 `15m` spread z-score 给入场；
- 若 `5m` 上 residual 继续恶化但 order book 不支持双腿同步，就宁可放弃，不做半腿暴露。

### 10.2 Exit
第一轮先用最朴素的三类：
1. `z-score` 回到中线附近；
2. `max_hold` 到期强平；
3. cointegration / ADF 条件失效直接 kill。

### 10.3 Sizing
- 每条 pair 先做 `beta-neutral` 或 `dollar-neutral`；
- 再按 spread realized vol 做 vol-target；
- 同 underlying / 同主题篮子设相关性 cap，避免组合里堆满一个风格簇。

### 10.4 Risk
至少加这几层：
1. **cointegration-break kill switch**
2. **legging timeout**
3. **max residual excursion stop**
4. **single-pair DD cap**
5. **portfolio heat cap**

### 10.5 Cost
这条线最容易被低估的就是成本：
- 两腿 × 两次成交，本来就比单腿策略贵；
- repo 给的是 **3.5 bps taker + 1 bp slippage** 的标尺；
- 但在我们这里，应该至少再跑一组 cost ladder：
  - **单腿 one-way：** `2 / 4.5 / 6 / 8 bps`
  - 并分别看 maker-biased 与 taker-biased 两个世界。

## 11. 下一步怎么测
1. **先做 1h pair discovery，不要先调 5m z-score。** pair 选不干净，后面都白搭。
2. **先验证 `15m` after-cost 是否存活。** 如果 `15m` 都不活，别幻想 `1m/3m` 会更容易救活。
3. **rolling beta 和 static beta 必须并排。** repo 明写 dynamic hedge ratio，这是这轮最值得验的点之一。
4. **kill switch 必须单独 ablation。** 不要默认它一定提升净收益，只能先用实验说话。
5. **把 atomic execution 当成 alpha 生死线来看。** pairs 策略最大的假阳性来源之一，就是回测里假装双腿同时成交。
6. **优先看 OOS plateau，不追单点最优阈值。** pairs 策略一旦只有一个窄点参数赚钱，实盘大概率会很脆。

## 12. 这条线最容易错在哪
- **把 pair selection 和 entry threshold 混在一起调。** 这样不知道到底是谁带来的收益。
- **把 1h 发现逻辑粗暴压缩到 1m。** 这通常只会放大噪音和费用。
- **只看 spread 回归，不看 legging 风险。** 真正死人的地方常常是第二条腿没成交。
- **把 repo 自报收益当成已验证事实。** 这轮应该把它当 high-signal blueprint，而不是已闭环证据。
- **忽略相关性拥挤。** 即使每个 pair 单看都不错，组合层也可能是在同一个 risk bucket 上重复下注。

## 13. 对当前项目的直接意义
这轮主题值得进池，因为它满足当前 bot7 的主线偏好：
- **主题类型：raw alpha**
- **基础 alpha 清楚**
- **能独立复现成完整策略**
- **天然服务于 pairs / stat-arb 素材池**
- **公开数据足够，能很快做 `1h → 15m → 5m` 的最小实验**

如果要一句话概括：
**这份 2026 Hyperliquid repo 最值钱的，不是“大而全交易机器人”叙事，而是它把一条 pairs raw alpha 的实盘化顺序讲清楚了：先筛干净 pair，再做 z-score fade，再把 kill switch 和双腿执行写进同一张策略卡。**

## 14. 来源链接
- Repo：<https://github.com/Jotanune/CryptoGuardian>
- GitHub API metadata：<https://api.github.com/repos/Jotanune/CryptoGuardian>
- README（raw）：<https://raw.githubusercontent.com/Jotanune/CryptoGuardian/main/README.md>
- Examples README（raw）：<https://raw.githubusercontent.com/Jotanune/CryptoGuardian/main/examples/README.md>
- Data script（raw）：<https://raw.githubusercontent.com/Jotanune/CryptoGuardian/main/examples/download_data.py>
- Tests summary（raw）：<https://raw.githubusercontent.com/Jotanune/CryptoGuardian/main/tests/test_output.md>
