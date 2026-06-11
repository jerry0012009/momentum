# 别把这份 2025/2026 GitHub repo 继续写成“4h reversal-vs-momentum 教学图”：对 desk 更该先测的是「skip-last-bar 的 8h~16h XS momentum」raw alpha
- 时间：2026-03-30 20:55 UTC
- 类型：2025 GitHub 仓库（2026-03 更新）+ notebook 复跑 + Binance US 公共 `4h` 复核
- 主题类型：raw alpha
- 基础 alpha：**横截面 lagged momentum**——先**跳过最近 1 个 `4h` bar**，再按更早的 `8h~16h` 相对强弱做多强、做空弱，持有下一段 `4h`
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是（但 repo 原样没有成本层，且原 universe 很窄；需要我们按 perp 口径重写）
- 主题标签：raw-alpha/cross-sectional/momentum/lagged-momentum/skip-last-bar/reversal-contamination/market-neutral/relative-strength/binance/4h/15m/5m/1m/3m/repo/public-data/cost
- 证据类型：repo README + notebook 公式 + 本地复跑数值

## 1) 这次看了什么
先回答 base alpha：**这次的 base alpha 不是“4h 反转 vs 24h 动量”的泛泛现象描述，而是一个更可执行的旁支：跳过最近那根最容易反打的 bar，只交易更早一段横截面强弱的延续。**

主看对象：`kunal14901/crypto-reversal-momentum-analysis`。
它 headline 写的是“研究 4h 到 24h 的 reversal / momentum 转换”，但对我们 desk 真正值钱的不是 headline 本身，而是 notebook 里一句很实在的话：

> **first 4-hour bar often exhibits the strongest reversal effects**，所以把组合 **lag 一根 4h bar**，动量效果会明显变强。

这就把一个“现象总结”翻成了一个可测的策略骨架：
- 别追最近 1 根 bar；
- 用更早的 `8h~16h` 横截面强弱做 rank-demeaned-normalized 多空；
- 持有下一段 `4h`；
- 看它能否迁移到 `15m/5m` 的短周期决策时钟里。

## 2) 核心结论
- **一句话核心结论：** 这份 repo 最值得 intake 的不是“短窗反转、长窗动量”的教科书表述，而是 **`skip-last-bar` 之后，`8h~16h` 横截面 momentum 变成可直接测试的 raw alpha**。  
- **一句话原因：** 最近一根 `4h` bar 明显带着 reversal contamination；把它剥掉以后，原本混在一起的短反转噪声和更早的 continuation 被干净地分开了。

3 个关键数据点（按 repo notebook 逻辑本地复跑）：
1. **不跳过最近 bar 时**，Sharpe 曲面是：`4h -2.10`、`8h -0.44`、`12h +0.55`、`16h +0.92`、`20h +1.21`、`24h +0.17`。也就是说，**最近 4h 本身更像反转噪声源**。  
2. **跳过最近 1 根 `4h` bar 后**，Sharpe 变成：`4h +0.80`、`8h +1.63`、`12h +1.46`、`16h +1.48`、`20h +0.55`、`24h +0.64`。最可搬运的 pocket 明显落在 **`8h~16h`**。  
3. **粗略成本包络并不离谱，但绝不算免费**：我按复跑权重估了 mean gross turnover / rebalance，`8h/12h/16h` 大约是 **`0.97 / 0.81 / 0.70`**；对应每 `4h` 平均 alpha 大约 **`3.29 / 3.07 / 3.07 bps`**，粗略 break-even one-way cost 约 **`3.4 / 3.8 / 4.4 bps`**。这说明它不是那种一上成本就立即归零的玩具，但也远没到可以无脑实盘。

## 3) 为什么和当前 desk 直接相关
这条东西和我们最近几轮学习进展是接得上的：
- 最近 desk 已经反复看到，**“最近一脚”** 经常最脏：无论是 shock-reversal、OFI、panic bounce 还是短窗 relative-value，**最新 bar 往往更像噪声/拥挤/反打层**；
- 这份 repo 给的不是新奇特特征，而是一个很容易落地的 **decontamination trick**：**把最近 bar 拿掉，再看 continuation**；
- 这使它不是“又一个泛化 momentum 综述”，而是一个能直接补进 raw alpha 素材池的 **结构性实现细节**。

更重要的是，它和我们已有那类 `24h stale return` 卡片不一样：
- 不是单资产时间序列动量；
- 不是整段 lookback 一把抓；
- 而是 **cross-sectional relative-strength + explicit recent-bar exclusion**；
- 真正的命题是：**recent bar 多半承载 reversal，earlier block 才承载 continuation。**

## 3.5) 策略拆解（必填）
- 方向属性：cross-sectional / momentum / market-neutral / relative-strength
- 基础 alpha：剔除最近 1 根 `4h` bar 后，更早的 `8h~16h` 横截面强弱对下一段 `4h` 仍有延续性
- entry：
  - 在每个决策时点，计算各币过去 `N` 个 `4h` bar 的平均收益（`N=2/3/4` 对应 `8h/12h/16h`）；
  - **跳过最近 1 根 `4h` bar**，即信号用 `avg_ret.shift(2)` 对齐下一期收益；
  - 对截面做 rank → demean → normalize，形成 dollar-neutral / gross-normalized 多空权重；
  - 做多排名高者，做空排名低者。
- exit：默认持有下一段 `4h` 后全部平掉，再滚动更新组合
- sizing：rank-demeaned-normalized，保证截面净敞口接近 0、gross ≈ 1
- risk / veto：
  - universe 最少做流动性与可交易性过滤；
  - 最近 bar 若出现极端 jump / funding shock / listing 异常，可再加 veto；
  - 单币权重上限、防止小样本 universe 中单币过重
- cost：按每次 rebalance 的 gross turnover 显式扣减；当前复跑显示这条线大致只能承受 **几 bps one-way** 的级别

## 4) Repo 层最关键的诚实判断
### 4.1 值钱的不是 headline，而是“recent-bar contamination”这句注释
repo 的表面信息很普通：
- `4h` 数据；
- `2020-01-01` 到 `2022-12-31`；
- universe 只有 `BTC/ETH/ADA/BNB/XRP/DOT/MATIC` 这 7 个币；
- notebook 用的是很标准的 `rank → demean → normalize` 横截面做法。

但它真正给我们的 intake 价值，是把一个常见现象说清楚了：
- **plain 版本里，最近 bar 的 reversal 会污染 continuation；**
- **lag 一根 bar 后，真正能留下来的 continuation pocket 才露出来。**

### 4.2 这也是它和“generic 24h momentum”最大的区别
`24h stale return` 的叙事通常是：过去一段涨了，接下来还会涨。  
这份 repo 的叙事更细：
- **最近那一小段可能不该算进来；**
- continuation 不是均匀分布在整段 lookback 上；
- 真正有用的，是 **“去掉最新噪声后”的 lookback block**。

这对短周期 desk 很重要，因为它决定了你要不要：
- 追刚拉完的 winner；
- 还是等一小段 cooling-off 后，再按 earlier strength 去做多空排序。

## 5) 本地复跑口径与读数
### 5.1 复跑口径
- 数据源：`Binance US` 公共 `4h` K 线（按 repo notebook API 路径复刻）
- 样本期：`2020-01-01` ~ `2022-12-31`
- 标的：`BTCUSDT / ETHUSDT / ADAUSDT / BNBUSDT / XRPUSDT / DOTUSDT / MATICUSDT`
- 权重：rank-demeaned-normalized
- plain 组合：`avg_ret.shift(1) * next_ret`
- lagged 组合：`avg_ret.shift(2) * next_ret`
- 年化换算：`sqrt(252 * 24 / 4)`

### 5.2 plain vs lagged Sharpe
| lookback | plain Sharpe | lagged Sharpe |
|---|---:|---:|
| 4h | -2.10 | +0.80 |
| 8h | -0.44 | +1.63 |
| 12h | +0.55 | +1.46 |
| 16h | +0.92 | +1.48 |
| 20h | +1.21 | +0.55 |
| 24h | +0.17 | +0.64 |

最直接的 takeaway：**别把这条线理解成“越长越动量”**。对 desk 更值钱的是：
- `8h~16h` 是比较干净的 continuation pocket；
- `20h+` 没继续变强，说明并不是简单的 longer-lookback-is-better；
- **关键动作是 recent-bar exclusion，不是无脑拉长窗口。**

### 5.3 粗略成本包络（只做一阶 sanity check）
| lookback | mean turnover / rebalance | mean alpha / 4h | 粗略 break-even one-way cost |
|---|---:|---:|---:|
| 8h | 0.97 | 3.29 bps | 3.4 bps |
| 12h | 0.81 | 3.07 bps | 3.8 bps |
| 16h | 0.70 | 3.07 bps | 4.4 bps |

这里必须强调：
- 这只是 **repo 口径 + 窄 universe + spot-like 公共数据** 下的一阶估计；
- 不是 Binance Futures 净值结论；
- 但至少告诉我们，这条线**值得做下一轮 perp transfer**，不是那种连第一步都不用走的伪 alpha。

## 6) 为什么这轮值得它，而不是继续补别的 headline alpha
因为它满足这轮 intake 偏好里的一个很关键点：
- **不是继续抄论文 headline；**
- 而是从 repo 里抽出一个更适合我们 desk 的旁支实现细节；
- 而且这个细节直接服务于 raw alpha 本体，不只是 filter/overlay。

更直白地说：
- headline：`reversal vs momentum across horizons`
- 真正可执行的 branch：`skip-last-bar → 8h~16h XS momentum`

这正是该进入素材池的东西。

## 7) 最小实验怎么搬到 `1m / 3m / 5m / 15m`
### 方案 A：先做 `15m` 的 HTF-feature / LTF-execution
这是我最建议的第一步。

- 数据：Binance USDⓈ-M perp，large-cap + 高成交额 universe
- 决策频率：`15m`
- 信号：
  - 计算过去 `16h→4h`、`12h→4h`、`8h→4h` 三段 cumulative return（都**排除最近 `4h`**）
  - 对截面做 rank-demean-normalize
- 持有：下一个 `1h`（4 个 `15m` bar）或 `45m`（3 个 `15m` bar）
- 风险：inverse-vol / ADV cap / 单币权重上限
- 成本：按实际 gross turnover 扣 taker / maker-taker 混合成本

核心目的不是“一步到位复制 4h repo”，而是验证：
> **在更细执行时钟下，recent-bar exclusion 还能不能把 continuation 留住。**

### 方案 B：做真正短周期开窗缩放版
如果要更贴近 `5m/3m/1m`：
- 可以把结构缩成 **“跳过最近 1 个 holding window，再看更早 2~4 个 holding window 的相对强弱”**；
- 例如 `5m` 上：
  - 跳过最近 `15m` 或 `20m`
  - 用更早 `40m~80m` 的 cross-sectional strength 排序
  - 持有下一段 `10m~20m`

这里不要死抠“必须等比例缩成 1 bar / 2 bar / 4 bar”；我们真正要测的是**结构关系**，不是字面时长。

## 8) 下一步怎么测（直接可执行）
1. **先做 perp transfer，不要继续停留在 repo 原始 spot-like universe。** 选 `Binance USDⓈ-M` 的大中盘可交易池，按成交额 / volume / open interest 做 admission。  
2. **第一轮只测 `8h/12h/16h` 三档 lagged 版本。** plain 版本已经告诉我们 recent-bar contamination 很重，没必要从最差的地方再重复一遍。  
3. **显式扣成本并记录 turnover。** 最少给 `0 / 2 / 4 / 6 bps one-way` 四档；如果 `8h~16h` 在 `4bps` 左右还有 pocket，才值得升优先级。  
4. **加一个“recent shock veto”对照。** 若最近 `4h` 里出现 funding jump、单根极端收益、异常成交放大，则暂停该币入选，验证是否能进一步去噪。  
5. **做 universe 扩展与 survivorship 清洗。** repo 只有 7 个币，而且缺失值处理很粗；下一轮必须用真实可交易 universe 重新看这个命题是否还成立。  
6. **把它和现有 XS 家族做横向赛马。** 至少对照：`24h stale return`、`bucket-neutral loser reversal`、`basis/funding XS carry`，看它到底是在补充，还是在重复已有素材。

## 9) 风险与保留意见
- repo universe 太窄，只有 7 个币，结论很容易受个别资产影响；
- notebook 默认 `pct_change()` 的缺失值处理并不 production-grade；
- 当前结果没有真正把 perp funding、冲击成本、挂吃单占比建进去；
- 因为策略本质是横截面多空，**universe 质量** 比单币策略更关键；
- 所以这轮结论是：**值得进入 raw alpha 素材池并做 perp transfer**，不是“已经验证可实盘”。

## 10) 来源
1. **Kunal Raj (repo owner, created 2025-07-07; updated 2026-03-25). _crypto-reversal-momentum-analysis_. GitHub repository.**  
   - Repo URL: https://github.com/kunal14901/crypto-reversal-momentum-analysis
2. **Notebook (directly inspected and locally reproduced)**  
   - README: https://raw.githubusercontent.com/kunal14901/crypto-reversal-momentum-analysis/main/README.md  
   - Notebook: https://raw.githubusercontent.com/kunal14901/crypto-reversal-momentum-analysis/main/Reversal_and_Momentum_in_Cryptocurrency_Trading.ipynb
3. **Literature lineage / readable companion**  
   - Wen, Qian, Aharon, and Li (2022). *Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both?* North American Journal of Economics and Finance. DOI: https://doi.org/10.1016/j.najef.2022.101733

## 11) 本地产物
- `reports/artifacts/quant_digests/skip_lastbar_xs_momentum_20260330/summary.json`
- `reports/artifacts/quant_digests/skip_lastbar_xs_momentum_20260330/sharpe_profile.csv`
- `reports/artifacts/quant_digests/skip_lastbar_xs_momentum_20260330/turnover_cost_envelope.csv`
