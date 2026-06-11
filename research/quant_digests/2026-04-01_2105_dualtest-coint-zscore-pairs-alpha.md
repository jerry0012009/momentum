# 别把这份 2026 新 repo 只读成“daily pairs 修 bug”：对 short-cycle desk，更该先测的是「ADF+Johansen 双检验 × rolling beta spread z-score fade」这条 pairs raw alpha
- 时间：2026-04-01 21:05 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `stat_arbitrage_improved.py` + GitHub API metadata）
- 主题类型：raw alpha
- 基础 alpha：cointegrated pair spread mean reversion；先用 `ADF + Johansen` 双检验筛 pair，再对 rolling beta / alpha 定义的 spread 做 `z-score fade`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/pairs/stat-arb/relative-value/mean-reversion/cointegration/adf/johansen/dual-test/rolling-beta/spread-zscore/walk-forward/binance/bybit/okx/1h/15m/5m/3m/1m/repo/public-data/cost
- 证据类型：repo-based source audit + 方法锚点

## 1. 这次看了什么
这次主看的是 **julia136 (2026)** 的 GitHub 仓库 **Statistical-Arbitrage-in-Crypto-Currencies**。repo 表面上是一个 daily crypto pairs 回测修正版，但真正值得 desk intake 的，不是“日频配对作业”本身，而是它把一条可独立拆走的 raw alpha 骨架写得相当清楚：

- **12 个月 in-sample** 做 pair selection；
- **每 6 个月** 重选一次 pair；
- 交易层用 **90 天 rolling OLS** 估计 `beta / alpha`；
- **`|z| > 1` 入场、`|z| <= exit_threshold` 出场、`|z| > 3` 止损**；
- 成本默认按 **10 bps one-way** 扣减，并把 turnover 明确写进净收益。

repo 最有价值的地方不是“spread 会回归”这句老话，而是它明确想解决 **false-positive cointegration**：pair 不是只看 ADF，而是先过 **Engle-Granger ADF**，再过 **Johansen trace**，尽量把“看起来像配对、其实只是同涨同跌”的假关系先挡在交易前面。

## 2. 核心结论
- 这篇东西的 **base alpha 很清楚**：就是 **cointegrated spread mean reversion**，不是纯 filter，也不是泛风险壳。
- 对当前 desk 来说，最该偷走的不是日频参数，而是 **“双检验 pair admission”** 这一层：先筛掉假 cointegration，再让 z-score fade 真正进入 OOS。
- repo 里有 3 个值得保留的工程动作：
  1. **walk-forward 重选 pair**，而不是一劳永逸固定组合；
  2. **rolling hedge ratio**，而不是永远拿静态 beta；
  3. **把 stop-loss 和 turnover cost 写进策略壳**，而不是只看毛收益。
- 但它也有两个必须先审计再复用的点：
  1. 代码里如果双检验后一个 pair 都没留下，会 **静默回退到 ADF-only**；这对 desk 来说不能当成默认安全行为。
  2. repo 注释声称已经修好 spread direction consistency，但 `adf_for_pair()` 里的残差定义与 `gen_signals()` 里的 spread 公式仍存在 **口径不一致风险**；这一层不能盲抄，必须自己重写并 unit-test。

一句话说：**这轮真正值得进入素材池的，不是“又一个 pairs repo”，而是“用双检验减少假 pair，再把 spread MR 留给短周期执行层”这条更稳的 raw alpha 读法。**

## 3. 为什么和当前项目有关
最近 intake 已经有不少 pairs / stat-arb / relative-value 主题，但更偏向：
- half-life gate
- wide-band entry
- parameter plateau
- cluster residualization

这轮补的是另一个同样关键、但更基础的缺口：**pair 是怎么被批准进入交易池的。**

它和当前学习进展的关系很直接：
- `momentum` 项目原生学习地图还偏 trend / breakout / ATR / volume；
- 而 bot7 当前任务要求持续补齐 **可独立复现的 raw alpha 素材池**；
- 这篇 repo-based intake 虽然不是最新论文，但它给的是 **pairs 家族更可复用的 admission shell**，正好能服务后续多条 pairs raw alpha 的 clean replication。

翻成人话：**不是再找一条新花样，而是把“哪些 pair 根本不该交易”先讲清楚。**

## 3.5 策略拆解（必填）
- 方向属性：pairs / stat-arb / relative value / market-neutral
- 基础 alpha：长期共动 pair 的短时偏离会回归均值；交易对象是 hedge 后 spread，而不是单腿方向
- regime：只在流动性足够、pair 关系仍稳定的币对上启用；优先 liquid majors / upper-mid perp universe
- filter / veto：`ADF + Johansen` 双检验、rolling beta 重新估计、cointegration break 失效即下线、禁止“无 pair 时自动退回 ADF-only”
- risk / sizing / execution overlay：beta-neutral / gross-normalized sizing、`|z| > 3` stop、max-hold、双腿成本门槛、maker/taker leg routing

## 4. 可复刻的最小实验
- 研究假设：**短周期 pairs raw alpha 是否会主要死在“pair 选错”，而不是死在 z-score 本体。**
- 数据：Binance / Bybit / OKX 公开 perpetual klines；先用 `1h` 做 pair discovery，再在 `15m` 执行，必要时用 `5m` 细化下单。
- universe：先取 `15 ~ 25` 个最液态 USDT perp，排除稳定币、包装资产和明显叙事错位币。
- pair selection：
  1. rolling `45 ~ 90` 天 `1h` 窗口；
  2. 只保留 **ADF p-value < 0.05 且 Johansen trace > 5% critical value** 的 pair；
  3. **不允许 silent fallback 到 ADF-only**；
  4. 先按行业/叙事 bucket（L1、L2、DeFi、meme）分层做，别第一刀就全市场乱扫。
- 信号：
  1. `15m` 上用 rolling `96 / 144 / 192` bar 估 beta；
  2. 统一自己重写 spread 定义，确保回归方向与残差方向一致；
  3. `|z| >= 2.0 / 2.5` 入场，`|z| <= 0.5` 出场，`|z| >= 3.0 / 3.5` 止损。
- sizing / risk：pair 内 beta-neutral，跨 pair 做 gross cap；单 pair 加 `max_hold = 16 / 24 / 32` 根 `15m`。
- 成本：先做 **pair round-trip `12 / 20 / 32 bps` friction ladder**，不要只看单腿 fee。
- 验证：
  1. `ADF-only` vs `ADF+Johansen` OOS 对照；
  2. 正收益 pair 占比；
  3. turnover、平均持有时长、止损触发率；
  4. `15m` 触发后换到 `5m` 执行，净收益是否还能保住。

## 5. 先测什么，不先测什么
先测 **“双检验 shortlist 是否比 ADF-only 更稳”**，而不是先卷最优 z-score 阈值。因为如果 pair admission 本身是脏的，后面所有 entry / exit 调参都只是在脏地基上抹墙。

也不要一上来照抄 repo 的 daily 节奏：
- 不要先用 `6` 个月重平衡；
- 不要先扫几百个币；
- 不要先把 `1m` 当 pair discovery 主频。

更合理的第一刀是：**慢一点选 pair，快一点执行 trade。**

## 6. 风险与误区
- **频率迁移风险**：repo 本体是 daily，直接映射到 `1m/3m/5m/15m` 不能默认成立，必须重新估窗口和成本。
- **双检验样本长度问题**：Johansen 在很短样本上并不神；它应该是 gate，不是神谕。
- **公式口径风险**：spread / residual 定义若不统一，回测结果会被 quietly 污染。
- **交易实现风险**：pairs 策略的真实 friction 不只是 fee，还包括双腿 legging risk、funding、盘口深度与同步成交。
- **过度自信风险**：如果一个窗口里一个 pair 都没有，不代表“市场错了”；很多时候只代表 **这段时间根本没有干净 pair**。

## 7. 来源与复现线索
### 主来源（repo）
- Julia136 (GitHub, 2026), *Statistical-Arbitrage-in-Crypto-Currencies*, GitHub repository, DOI: N/A, Readable URL: <https://github.com/julia136/Statistical-Arbitrage-in-Crypto-Currencies>, Repo URL: <https://github.com/julia136/Statistical-Arbitrage-in-Crypto-Currencies>
- README（raw）：<https://raw.githubusercontent.com/julia136/Statistical-Arbitrage-in-Crypto-Currencies/main/README.md>
- Strategy code（raw）：<https://raw.githubusercontent.com/julia136/Statistical-Arbitrage-in-Crypto-Currencies/main/stat_arbitrage_improved.py>
- GitHub API metadata：<https://api.github.com/repos/julia136/Statistical-Arbitrage-in-Crypto-Currencies>

### 方法锚点（经典地基，非本轮主来源）
- Engle, Robert F.; Granger, Clive W. J. (1987), *Co-integration and Error Correction: Representation, Estimation, and Testing*, *Econometrica*, DOI: <https://doi.org/10.2307/1913236>, Readable URL: <https://www.jstor.org/stable/1913236>
- Johansen, Søren (1991), *Estimation and Hypothesis Testing of Cointegration Vectors in Gaussian Vector Autoregressive Models*, *Econometrica*, DOI: <https://doi.org/10.2307/2938278>, Readable URL: <https://www.jstor.org/stable/2938278>

## 8. 一句话带走
如果把这份材料变成 desk 可测策略，我会把它定义成：**“用 ADF+Johansen 双检验先守住 pair admission，再把 spread z-score fade 下放到 15m/5m 执行层”的 pairs raw alpha 壳，而不是一份可以直接照抄的 daily 回测作业。**
