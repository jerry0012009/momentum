# 别把这份 2026 多 edge crypto repo 只读成“9 个点子拼盘”：对 short-cycle desk，更该先拆的是「venue/leg divergence × lagging-leg catch-up」这条 raw alpha——但 Binance same-venue majors 迁移版目前只有 BTC `15m` 勉强接近成本线

- 时间：2026-04-14 22:33 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `crypto_alpha/edges/cross_exchange_divergence.py` + `crypto_alpha/backtest/crypto_runner.py` + `crypto_alpha/config.py`）+ Binance Spot / USDⓈ-M `5m/15m` public-data portability probe
- 主题标签：raw-alpha/relative-value/cross-venue/spot-perp/divergence/catch-up/mean-reversion/momentum-divergence/single-leg-directional/binance/5m/15m/repo/public-data/cost/risk
- 证据类型：源码规则 + repo 回测口径 + public-data first verdict

- 主题类型：raw alpha
- 基础 alpha：**当 perp 相对 spot（或主 venue 相对次 venue）的价格比率偏离滚动公允区间，且其中一条腿的短窗涨跌速度明显跑快/跑慢时，下一小段时间更容易出现 lagging leg catch-up 或 overextended leg 回摆；落地交易时表现为对 perp 做单腿方向性 fade / catch-up。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = venue / leg divergence reversion with short-horizon catch-up.**

翻成人话：
- 不是传统的“两个腿长期 cointegration，所以逢偏离就配对”；
- 也不是单纯把 funding / basis 当 carry 指标；
- 它更像是在赌：**两个本该更同步的价格腿，短时间没走齐；下一小段时间，慢腿会补动作，快腿会回一点。**

所以这轮主题应该归类成：
- `raw alpha`
- 更具体是 `relative-value / divergence / catch-up`
- 不是 filter，也不是 regime overlay。

## 2. 这次看了什么

### 主来源（repo）
- **Author / Owner：** GitHub owner `mahimn01`
- **Year：** 2026
- **Title：** `trading-algo`
- **Venue：** GitHub repository
- **DOI：** N/A
- **Readable URL：** https://github.com/mahimn01/trading-algo
- **Repo URL：** https://github.com/mahimn01/trading-algo
- **GitHub metadata：**
  - created: `2025-12-24T05:15:34Z`
  - pushed: `2026-04-14T20:13:19Z`
  - updated: `2026-04-14T20:21:46Z`

### 本轮重点审的源码
- `README.md`
- `crypto_alpha/edges/cross_exchange_divergence.py`
- `crypto_alpha/backtest/crypto_runner.py`
- `crypto_alpha/config.py`

### 本轮自建 portability probe 产物
- 脚本：`reports/artifacts/quant_digests/2026-04-14_ced_portability_probe.py`
- 汇总：`reports/artifacts/quant_digests/ced_portability_probe_summary_2026-04-14.csv`
- 信号快照：`reports/artifacts/quant_digests/ced_portability_probe_signals_2026-04-14.csv`

## 3. repo 真正提供了什么，不要被“9-edge system”这个外壳带偏

## 3.1 README 已经给了一个很重要的先验：CED 是 9 个 edge 里少数活着的
README 直接写了 crypto 这条线的结果：
- **9-edge 组合 Sharpe：`+0.277`**
- 9 条 edge 里只有 3 条 standalone 为正：
  - **IMC：`+0.72`**
  - **CED：`+0.40`**
  - **PBMR：`+0.33`**

这点很重要，因为它说明：
> **CED 不是 README 里凑数的配角，而是 repo 作者自己回测里“少数没死掉”的 edge 之一。**

也就是说，哪怕最后 desk 不直接照搬，它也值得做 intake。

## 3.2 `cross_exchange_divergence.py` 给出的其实是一条很清楚的完整策略壳
这条 edge 的信号逻辑不复杂，但很可执行：

### A. 比率偏离（主成分）
- 看 `perp / spot` 或 `primary / alt venue` 的价格比率；
- 在 rolling window 内算均值和标准差；
- 当当前 ratio 的 **z-score 超过阈值** 时，认为一条腿明显“跑快了”。

默认参数：
- `lookback = 72`
- `entry_z = 1.8`
- `exit_z = 0.5`

翻成人话：
> **腿间价差偏得够远，才值得上。**

### B. 动量背离（辅助确认）
源码还额外看了一个很 desk-friendly 的东西：
- `momentum_window = 12`
- `momentum_divergence_threshold = 0.02`
- 比较两条腿在这个窗口上的 ROC 差值。

这层意思不是“再叠一个指标”，而是：
> **如果一条腿最近明显跑得比另一条腿快，那它更像 overextended；慢腿更像 catch-up 候选。**

### C. 成交量权重
repo 没有把信号写成纯价差教科书，而是加了：
- perp vs spot 的 volume ratio
- 把 volume ratio 压成 `0.5 ~ 1.5` 的权重

翻成人话：
> **谁那边更活跃，谁那边的偏离更值得认真看。**

### D. 交易实现：不是 delta-neutral 两腿，而是对 perp 做单腿方向
这是这轮最值得 desk 明确记住的点：
- 这条 edge 在 `get_vote()` 里输出的是 `LONG / SHORT / STRONG_LONG / STRONG_SHORT`；
- 真正执行时，交易对象是 **perp 这一腿**；
- spot 或 alt exchange 更多是 **reference leg**，不一定真的拿去对冲。

这使它跟很多“spot-perp basis carry”不一样：
> **它不是收租壳，而是一个 reference-driven directional catch-up / fade 壳。**

## 3.3 entry / exit / sizing / cost 在 repo 里是完整闭环，不只是一个 notebook 公式
我这轮把“是否可直接落地完整策略”记成 `是`，原因是 repo 不只给了一个 signal 函数，而是把整条链补齐了：

### entry / exit
在 edge 里写死了：
- `abs(z) > 1.8` 才开；
- `abs(z) < 0.5` 平；
- 也允许冲突信号时减仓/退出。

### sizing / risk
`crypto_runner.py` 和 controller config 里给了完整壳：
- `max_position_pct = 0.30`
- `max_gross_exposure = 3.0`
- `max_leverage = 5.0`
- `maintenance_margin_ratio = 0.03`
- `max_drawdown = 0.25`
- `daily_loss_limit = 0.05`

### execution / cost
repo runner 明确采用：
- **next-bar-open execution**
- maker `2 bps`
- taker `5 bps`
- slippage `5 bps`
- backward-only data lookup

也就是说，这不是“概念能看懂但不能落地”的材料；
它已经是 **完整策略壳**，只是还没证明一定适合我们当前 Binance short-cycle lane。

## 4. 这条 alpha 对 desk 的正确理解，不是“又一个 basis MR”

如果只看 `perp/spot ratio`，很容易把它误读成旧的 basis mean reversion。
但我觉得这轮更值得留下来的，是它和传统 basis shell 的区别：

1. **basis MR 更像静态偏离回归；CED 更强调“谁先跑、谁后补”。**
2. **basis 壳常常是两腿对冲；CED 在 repo 里是 reference-driven 单腿方向。**
3. **CED 更适合真正的 cross-venue / proxy-leg / information-lag 场景；same-venue spot-perp 反而可能太紧。**

所以 desk 化后，我会把它记成：

> **`divergence × catch-up`，而不是简单的 `basis z-score fade`。**

## 5. 我做的 Binance public-data probe：重点不是“它能不能勉强赚”，而是“它到底迁移到哪里更像样”

## 5.1 最小实验口径
- **数据源：** Binance Spot `api/v3/klines` + Binance USDⓈ-M `fapi/v1/klines`
- **公开性：** 完全公开
- **频率：** `5m / 15m`
- **symbol：** `BTCUSDT / ETHUSDT / SOLUSDT`
- **样本：** 各腿最近 `1000` 根 bar
- **信号映射：** 复刻 repo 的 ratio z-score + momentum divergence + volume weighting
- **执行：** next-bar-open 单腿 perp 进出
- **离场：** `|z| < 0.5` 或反向信号
- **成本阶梯：** 先看 gross，再粗扣 `4 / 8 bps` round-trip

这不是 production backtest，只是回答一句：
> **repo 这条 edge，搬到我们最容易拿到的同 venue spot/perp majors 上，先长什么样？**

## 5.2 先记 5 个最重要的数据点

### 数 1：repo 内部证据并不弱——CED standalone Sharpe 是 `+0.40`
这说明它至少不是纯故事。
但要注意：
- README 的 published crypto result 与 `run_9edge_backtest.py` 下载器默认 `1h` timeframe 强相关；
- 同时 `config.py` 又把 live-ish `bar_size` 写成了 `5m`。

所以更准确的解读是：
> **repo 证明了这条 edge 在其内部宇宙里有生存力，但“5m 直接可迁移”仍然需要我们自己验。**

### 数 2：当前最像样的 pocket 只有 **BTC `15m`**
在我这轮 public probe 里，最好的是：
- **BTCUSDT `15m`**
- `53` 笔 trade
- **avg gross `+3.94 bps / trade`**
- hit rate **`47.2%`**
- avg hold **`2.57` bars**（大约 `38` 分钟）

翻成人话：
> **它不是高胜率壳，而是低命中但单笔盈亏比还凑合的 pocket。**

### 数 3：但 BTC `15m` 一扣成本就几乎归零
同一个 BTC `15m` pocket：
- 粗扣 `4 bps` round-trip 后，**avg net 约 `-0.06 bps`**
- 粗扣 `8 bps` 后，**avg net 约 `-4.06 bps`**

也就是说：
> **它离“可交易”不是十万八千里，但还没过线。**

### 数 4：ETH / SOL 在 same-venue majors 口径下明显不行
`15m` 上：
- ETH：**`-18.28 bps / trade`**
- SOL：**`-15.62 bps / trade`**

`5m` 上三者更是全负：
- BTC：`-5.50 bps`
- ETH：`-12.84 bps`
- SOL：`-4.25 bps`

这点很关键，因为它告诉我们：
> **如果只在 Binance same-venue spot/perp majors 上抄这条 edge，大概率是在做一条过紧、过薄、被费用吃掉的假迁移。**

### 数 5：在当前 same-venue majors 测试里，动量背离这一层几乎没额外贡献
我额外对比了：
- `z-score only`
- `z-score + momentum divergence combo`

结果几乎一样。
这说明：
> **在 Binance same-venue spot/perp majors 这组数据里，真正有信号负载的仍是 ratio 偏离；ROC 背离没有明显额外信息增益。**

这反而是个好线索：
- 不是说 momentum divergence 这个 idea 错；
- 更可能是 **same-venue spot/perp 太同步，背离层根本不够肥**；
- 真正该去找的是 **更“不同用户群 / 不同流动性 / 不同信息速度”的腿。**

## 6. 这轮为什么仍值得进素材池

如果只看本轮 Binance majors first verdict，这条线当然还不够上 production。
但它仍值得进池，原因有三层：

### 6.1 它补的是一个和现有 basis / pairs 稍微错开的 raw alpha 壳
我们已经积累了不少：
- basis MR
- funding carry
- pairs spread fade
- lead-lag ranking

而这条 CED 更像：
- **单腿 directional**
- **reference-leg 驱动**
- **venue / leg 信息不同步**

也就是它卡在：
> **“不是纯配对，不是纯 carry，也不是纯单边 breakout”的中间地带。**

### 6.2 它给了一个很有用的 desk 提示：same-venue majors 不是它的最佳落点
这轮负结果本身也很值钱，因为它帮我们少走弯路：
- 不要再把它当“又一个 Binance spot-perp basis 小壳”；
- 更像要去找：
  - Binance vs OKX / Bybit / Hyperliquid
  - mark vs oracle
  - proxy asset vs listed perp
  - session / event 驱动的临时腿间不同步

### 6.3 它是“可直接继续深挖”的 repo，不是只能写综述的 paper
源码已经写清了：
- signal
- exit
- risk
- cost
- next-bar-open

所以它适合做下一步复现，不只是做阅读笔记。

## 7. 对当前 short-cycle desk 的 first verdict

我的判断是：

> **`mahimn01/trading-algo` 里最值得单独 intake 的 crypto branch 之一，就是 CED 这条 `venue/leg divergence × lagging-leg catch-up` raw alpha；但如果把它机械迁移到 Binance same-venue spot/perp majors，当前只有 BTC `15m` 勉强接近成本线，ETH / SOL 和全部 `5m` 版本都明显不过线。**

更短一点说：

> **alpha 本体是对的，但当前 lane 选错了。**

不是这条结构没价值，
而是：
- **腿选得太近**，
- **差价太薄**，
- **费用太重**。

## 8. 下一步怎么测

我会把下一轮明确压成 5 个最小实验，而不是继续在 same-venue majors 上硬抠：

### 8.1 先把 reference leg 从“同 venue spot”换成“真正不同步的腿”
优先顺序：
1. Binance perp vs OKX / Bybit perp
2. Binance perp vs Hyperliquid perp
3. perp mark vs oracle / index
4. proxy asset vs perp（例如 ETF proxy / commodity proxy / themed token proxy）

核心不是“多接几个数据源”，而是：
> **要让两条腿真的有不同的信息速度和不同的用户群。**

### 8.2 保留 `15m` 作为主研究 lane，别再优先压 `5m`
当前 first verdict 很清楚：
- `5m` 全面太薄；
- `15m` 至少 BTC 还能看到接近成本线的 gross。

所以更合理的 desk 路径是：
> **`15m signal -> 1m/5m execution`，而不是直接把信号也做成 `5m`。**

### 8.3 给“背离层”加 freshness / event gate
下一轮建议只在以下场景才允许 CED 开仓：
- funding settlement 前后
- 美股开盘 / 宏观数据发布时间段
- 某一腿近 `N` bar realized vol / volume 突然抬升
- 两条腿更新时间差显著扩大

这样才能真正测到“信息传播滞后”，而不是平静时段里的小抖动。

### 8.4 把 signal 拆成 2 个 branch 分别测
不要继续把所有东西揉成一个黑盒：
1. **ratio z-score branch**
2. **momentum-divergence branch**

因为本轮结果已经暗示：
- 在 same-venue majors 里，branch 2 没什么增量；
- 但换到 cross-venue / proxy-leg 后，它可能才真正有用。

### 8.5 补 maker/taker 非对称执行，而不是只用 round-trip 粗成本
如果下一轮某个 pocket gross 只有 `4~8 bps` 这个量级，
那就必须更认真地区分：
- 开仓 maker / 平仓 taker
- 双边 taker
- maker miss 后追单
- 不同 venue 的最小 tick / 最小 notional / funding side effect

不然很容易把一个“刚好能活”的 edge 误杀，或者把一个“其实死了”的 edge 错判成可行。

## 9. 来源

### Repo / code
- `mahimn01` (2026), **trading-algo**. GitHub repository.
  - Repo URL: https://github.com/mahimn01/trading-algo
  - Readable URL: https://github.com/mahimn01/trading-algo
  - Raw README: https://raw.githubusercontent.com/mahimn01/trading-algo/main/README.md
  - Raw edge file: https://raw.githubusercontent.com/mahimn01/trading-algo/main/crypto_alpha/edges/cross_exchange_divergence.py
  - Raw runner: https://raw.githubusercontent.com/mahimn01/trading-algo/main/crypto_alpha/backtest/crypto_runner.py
  - Raw config: https://raw.githubusercontent.com/mahimn01/trading-algo/main/crypto_alpha/config.py

### 本轮本地产物
- `reports/artifacts/quant_digests/2026-04-14_ced_portability_probe.py`
- `reports/artifacts/quant_digests/ced_portability_probe_summary_2026-04-14.csv`
- `reports/artifacts/quant_digests/ced_portability_probe_signals_2026-04-14.csv`
