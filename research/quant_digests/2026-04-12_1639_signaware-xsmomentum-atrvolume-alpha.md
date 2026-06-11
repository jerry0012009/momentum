# 别把这份 XS momentum repo 只读成“1H 作业回测”：对 short-cycle desk，更该先测的是「fast cross-sectional momentum × ATR/volume confirmation × sign-aware exit」这条 raw alpha

- 时间：2026-04-12 16:39 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `step_1.py`）+ Binance USDⓈ-M `15m/5m` public-data portability probe
- 主题类型：raw alpha
- 基础 alpha：**横截面相对强弱会在短周期继续扩散：过去几小时里相对更强的币继续偏强、相对更弱的币继续偏弱；ATR 扩张和放量只是确认层，daily breadth 只是仓位层。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否
- 主题标签：raw-alpha/cross-sectional/momentum/relative-value/atr-expansion/volume-confirmation/regime-sizing/sign-aware-exit/binance-perpetual/15m/5m/repo/public-data/cost/risk
- 证据类型：GitHub repo 工程实现 + Binance 公共数据 first-verdict probe

## 1. 先把一句话说清楚：这篇东西的 base alpha 是什么？

> **base alpha = cross-sectional relative momentum。**
> 也就是：同一时刻横向看一篮子币，最近几小时里更强的那几只，下一段仍更容易继续强；更弱的那几只，下一段仍更容易继续弱。

这一步要先讲清，因为 repo README 容易让人把重点放到 `ATR / volume / regime score` 这些壳子上。但按 `step_1.py` 往下拆，真正的本体其实很简单：

1. 先算每个币过去一段时间的收益；
2. 再减去当期横截面均值，得到 relative momentum；
3. 排名后做 `top-2 long / bottom-2 short`；
4. `ATR 扩张 + volume_ratio > 1` 只是 admission filter；
5. `daily regime score` 只是 long/short 权重缩放，不是 alpha 本体。

翻成人话：

> 先找“这一篮子里谁最近最强、谁最近最弱”，再赌强者短期继续赢、弱者短期继续输；别把过滤层误认成 alpha 本身。

## 2. 这次看了什么

主来源是 **Atharva Bhatlawande (2026), _Cross-Sectional Momentum Crypto Strategy_** 这个 GitHub repo：
- Repo URL：<https://github.com/codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency>
- 最近提交：`973eab54158ad699c41543034fd6e3e578c78608`（2026-04-12）
- 无 DOI / 非正式论文，但规则写得足够清楚，可直接复跑。

这轮重点看的不是 README 里的高收益 headline，而是 `step_1.py` 里真正影响可移植性的 5 个部件：
- **信号本体**：`return_24 - cross-sectional mean` 后做 rank；
- **过滤层**：`ATR(14) > ATR baseline(20)` 且 `volume_ratio > 1`；
- **仓位层**：daily breadth `regime_score` 决定 long / short 权重偏置；
- **退出层**：signal 消失时退出；
- **代码缺陷**：repo 把 `return_6 < 0 and return_12 < 0` 统一当成“动量恶化退出”，这对 long 合理，但对 short 等于把盈利腿也提前关掉，天然带方向不对称。

所以这轮最值钱的，不是直接照抄 README，而是先做了一次 source audit，再把 desk 更该测的旁支抽出来：

> **保留 raw alpha 和 filter / sizing 壳，但把 exit 改成 sign-aware，而不是 literal 地照搬 repo 的非对称退出。**

## 3. 核心结论

- **一句话核心结论：** 这份 repo 的 raw alpha 本体在 Binance perp `15m` 上是有东西的，但真正值得 desk intake 的版本不是 literal repo exit，而是 **sign-aware exit** 版。  
- **一句话证明方式：** 我先按 repo 的 universe、rank、ATR/volume filter、daily breadth sizing 做 public portability probe，再把 `literal_repo_exit` 和 `sign_aware_exit` 两个版本并排比较。
- **`15m` literal repo exit**：样本约 `19488` bars、`4700` 次入场，gross 平均约 **`+0.38 bps/bar`**，gross 累计约 **`+102.16%`**，MDD 约 **`-17.63%`**。  
- **`15m` sign-aware exit**：样本同口径下约 `5878` 次入场、active ratio **`32.6%`**，gross 平均约 **`+0.63 bps/bar`**，gross 累计约 **`+217.18%`**，MDD 约 **`-16.04%`**；明显优于 literal 版。  
- **`5m` sign-aware exit** 反而只有 **`+0.04 bps/bar`**、gross 累计约 **`+14.30%`**、MDD **`-40.24%`**，说明这条 raw alpha 更像 `15m first lane`，不是天然的 `5m taker` 书。  
- 但诚实地说，**当前 blocker 不是有没有 gross，而是 turnover 太高**：`15m sign-aware` 的平均 turnover 约 **`0.306x/bar`**。按 round-trip **`8 bps`** 粗扣后，净均值约掉到 **`-0.60 bps/bar`**；即使按更乐观的 round-trip **`4 bps`** 粗算，也只是大致打平。
- 从 coin contribution 看，`AVAX / DOGE / ETH / LINK / SOL` 是主要贡献腿，`BNB` 明显拖后腿；这说明后续应优先往 **alt-heavy subset** 缩，而不是把 market-anchor 一直混进来。

## 4. 为什么和当前项目有关

这轮值得进研究池，不是因为它已经成本后过线，而是因为它把我们最近相对没系统补的一块 raw alpha 补上了：

- 不是单资产 breakout / fade；
- 不是 pairs / cointegration；
- 而是 **cross-sectional momentum with explicit filter + sizing shell**。

更重要的是，这个 repo 很适合做组件拆解：
- `base alpha`：横截面强者延续 / 弱者延续；
- `filter`：ATR expansion + volume confirmation；
- `sizing`：daily breadth regime score；
- `exit`：sign-aware deterioration / time cap；
- `cost`：turnover ladder。

也就是说，它非常适合拿来给 desk 做一个问题：

> **横截面动量本体是不是成立？如果成立，真正要优化的是 exit 和 turnover，而不是再去给 alpha 本体堆更多解释层。**

## 4.5 策略拆解（必填）

- 方向属性：横截面 / 相对强弱 / momentum
- 基础 alpha：过去几小时相对更强的币在下一段继续跑赢，过去几小时相对更弱的币继续跑输
- regime：daily breadth 越偏 bull，long 端权重越大；越偏 bear，short 端权重越大
- filter / veto：`ATR(14) > ATR baseline(20)` 且 `volume_ratio > 1`
- risk / sizing / execution overlay：daily regime score 做 gross 分配；应补 `time cap / sign-aware exit / turnover cap / maker-first`；成本必须单独做 `4/8/12/16 bps` friction ladder

## 5. 可复刻的最小实验

### 研究假设
横截面相对强弱在 short-cycle crypto 里有延续，但 edge 的生死不取决于“再加多少过滤器”，而取决于**能否把退出改对、把 turnover 压下去**。

### 一个可计算定义
1. universe 固定为 `AVAX/BNB/BTC/DOGE/ETH/LINK/SOL`；
2. `15m` 上用过去 `16` 根 bar（约 `4h`）收益做 relative momentum rank；
3. 做多 rank 前 2，做空 rank 后 2；
4. 只在 `ATR(14) > ATR baseline(20)` 且 `volume_ratio > 1` 时开仓；
5. daily `regime_score = 7 币里站上 20d MA 的比例`，用于 long/short 仓位缩放；
6. 退出先测两版：
   - `literal_repo_exit`
   - `sign_aware_exit`

### 最小回测切口
- 资产：`AVAX/BNB/BTC/DOGE/ETH/LINK/SOL` Binance USDⓈ-M perp
- 周期：先 `15m`，再 `5m`
- 样本：`2025-10-01 ~ 2026-04-12`（warm-up 从更早几天开始）
- 先看：
  1. `gross mean bps / bar`
  2. `8 bps` 成本后还能不能活

本地 artifacts：
- `/root/clawd/jerry/momentum/reports/artifacts/literature/cross_sectional_momentum_repo_port_probe_2026-04-12_summary.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/cross_sectional_momentum_repo_port_probe_2026-04-12_costladder.csv`
- `/root/clawd/jerry/momentum/reports/artifacts/literature/cross_sectional_momentum_repo_port_probe_2026-04-12_asset_breakdown.csv`

## 6. 风险与保留意见

- 这是 GitHub repo，不是同行评审论文；优点是代码可复现，缺点是外部稳健性约束弱。  
- repo 的 headline 表现是 **gross of costs**，而这轮 public probe 说明：**turnover 比 alpha 更快**。  
- `step_1.py` 里的 deterioration exit 对 short 腿不对称，这种代码层小 bug 足以显著改变结论；因此 source audit 是必要步骤，不是形式主义。  
- 当前 public probe 只回答了 **portability**，还没回答更关键的问题：
  - 若改成 `30m/1h` 重平衡，edge 会不会更厚？
  - 若改成 maker-first，是否能从“gross 有效”变成“net 可活”？

## 7. 一句话带走

**这份 repo 真正值得 desk 留下来的，不是它 README 里的高收益截图，而是一个更朴素的判断：cross-sectional momentum 本体在 `15m` 上有 edge，但要想过线，第一优先级是把 exit 做成 sign-aware、把 turnover 压下去。**

## 8. 下一步怎么测

1. **把 rebalance 从每根 `15m` 降到每 `30m/60m` 一次**：先测 alpha 还剩多少、turnover 能降多少。  
2. **固定只做 sign-aware exit**：literal repo exit 不应再作为正式候选。  
3. **做 alt-only 子宇宙**：优先试 `AVAX/DOGE/ETH/LINK/SOL`，把 `BNB/BTC` 当 benchmark 或 gate，而不是继续混成同权 universe。  
4. **补 time-cap**：例如 `4~8` 根 `15m` 强制平仓，看看是否比 signal-expiry 更能控 churn。  
5. **加 maker-first / passive join 模式**：因为按 `8 bps` round-trip taker 粗扣已经不过线，这条 raw alpha 若想生存，执行一定要改。

## 9. 来源

### 主来源（repo）
- Atharva Bhatlawande. (2026). *Cross-Sectional Momentum Crypto Strategy*. GitHub.
- DOI：无
- Repo URL：<https://github.com/codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency>
- README：<https://raw.githubusercontent.com/codein123-afk/Cross_Sectonal_Momentum_Cryptocurrency/main/README.md>

### 本轮重点审计文件
- `README.md`
- `step_1.py`

### 说明
- 当前未见独立论文页；这轮证据主轴是 **repo 规则清晰 + public-data portability probe**，不是论文结论复述。
