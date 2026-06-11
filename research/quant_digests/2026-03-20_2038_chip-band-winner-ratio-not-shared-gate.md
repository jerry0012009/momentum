# 别把 `winner ratio / cost band reclaim` 直接升成 15m 的 shared retest gate：它现在更像 assumptions-sensitive evidence，不够诚实地服务 Fib / EMA
- 时间：2026-03-20 20:38 UTC
- 类型：本地仓库因子 + 本地 clean replication 复盘
- 主题标签：fibonacci/retest-hold/ema/psar/chip-distribution/winner-ratio/cost-band/reclaim/assumption-sensitivity/filter/repo/crypto/15m
- 证据类型：仓库代码（工程证据）+ 本地 clean replication

## 1. 这次看了什么
这轮不再找一个新的 headline alpha，而是把 `momentum` 仓库里还没写进 digest 的旁支想法单独拎出来：
**`chip_distribution.py` 里的 `cost_p50 / avg_cost band + winner_ratio`，能不能当 `Fib retest_hold / EMA continuation` 的确认层？**

更直白地说：回踩后重新站回某条线，不只问“价格站回去了没有”，还问一句：**按估算的成本带看，浮盈筹码有没有重新占优，套牢压力有没有真的缓下来？**

## 2. 核心结论
- **一句话核心结论：** 这条线现在还不配升成 15m shared gate；它只在宽松的 `synthetic shares` 假设下看起来像有用，一旦把换手/持仓假设收紧，edge 很快塌掉。
- **一句话证明方式：** 我直接复用仓库里的 clean replication 脚本，在 `BTC/ETH/SOL 120d 15m` 上对比 `raw_baseline`、`chip_cost_reclaim`、`chip_cost_reclaim_plus_winner_ratio`，并强制做三档 `synthetic shares / turnover anchor` 敏感度检查。

关键数据点（聚合，`6 bps/side`）：
1. **主 pocket 只活在宽松假设里**：`chip_cost_reclaim` 在 `conservative anchor` 下 `mean_total_return ≈ +18.14%`、`positive_asset_ratio = 3/3`、`mean_trades ≈ 101`。
2. **一旦 shares 假设收紧，结论直接翻脸**：同一主变体在 `aggressive anchor` 下掉到 `mean_total_return ≈ -18.62%`、`positive_asset_ratio = 1/3`、`mean_trades ≈ 406.7`。
3. **再加 `winner_ratio` 恢复门并没有救活鲁棒性**：`conservative` 下虽然仍为正（`≈ +11.80%`），但交易数从 `101` 降到 `59`；`neutral / aggressive` 仍没有变成可 shared 的稳定过滤层。

翻成人话：
- “价格重新站回估算成本带” 这个想法本身不蠢；
- 但当前 15m 版本最大的风险，不是信号不够花，而是**它太依赖你怎么编 `shares / turnover` 这件事**；
- 所以它更像一个**研究证据池里的候补过滤器**，不是现阶段该接到三条收口线默认流程里的共享开关。

## 3. 为什么和当前项目有关
- **Fibonacci confirmation / retest_hold**：这条线最直接。它试图把“守住回踩”从几何位置，升级成“成本带 reclaim + 套牢压力缓和”的更强定义。
- **EMA / PSAR raw alpha focus**：也能当 continuation 过滤层——不是问 EMA 有没有上穿，而是问上穿时市场里“站在浮盈一侧的人”是否真的开始变多。
- **为什么这轮值得写，而不是继续抄一条泛 breakout 小技巧？** 因为它直接回答了一个当前会改变 desk judgment 的问题：**holder-structure 这类读法到底值不值得进 15m 默认确认层。** 当前答案是：**概念值得保留，默认 shared 不值得。**

## 4. 可复刻的最小实验（下一步怎么测）
### 研究假设
如果把 `shares` 的近似从拍脑袋常数，升级成**公开可得的 perp OI / turnover proxy**，那么 `cost band reclaim` 可能保留一部分 honest uplift；否则它大概率只是 assumptions-driven 幻觉。

### 一个可计算定义（先冻最小版）
- `A`：现有 `fib_retest_hold_long` 或 `ema_psar_long` baseline；
- `B`：`A + close reclaims cost_p50/avg_cost band`；
- `C`：`B + winner_ratio re-expands above threshold`；
- `shares proxy` 首轮只允许三档：`OI-based`、`dollar-volume rolling proxy`、`fixed synthetic shares`，不再继续自由调参。

### 最小回测切口
- 资产：`BTC / ETH / SOL` perpetual
- 周期：`15m` 主评估，必要时 `5m` 只做执行细化
- 样本：近 `180d`
- 执行：`next-bar open`、`no-overlap`
- 成本：`6 / 10 / 15 bps per side`

### 先看哪 2 个指标
- `anchor sensitivity`（不同 shares proxy 下 uplift 能不能保住）
- `false_reclaim_ratio`（别只是把稀疏度提上去）

## 5. 风险与保留意见
- 当前 `chip distribution` 不是链上真实持仓账本，而是 `volume / shares` 的递推估计；
- 若 `shares` 代理本身不稳，整个 winner/trapped 叙事就容易变成参数故事；
- 这轮 clean replication 固定的是 `BTC/ETH/SOL 120d 15m` 本地 cache，还不是 desk 三条线的正式生产口径；
- 因此本轮结论不是“筹码结构无用”，而是：**在当前公开数据和当前建模口径下，它还不够诚实，不能直接升成 shared gate。**

## 6. 来源
1. **Jerry / momentum repo. (2026). _chip_distribution.py: cost-basis chip distribution estimation_. Local repository factor module.**
   - Authors: Jerry / momentum factor engine
   - Year: 2026
   - Title: `chip_distribution.py`
   - Venue: Local repo / factor module
   - DOI: `N/A`
   - Readable URL: `https://jp.jerrypsy.top/momentum/factors/scout_rank34_chip_distribution_15m/report.html`
   - Repo URL: `src/momentum/factors/chip_distribution.py`
2. **Jerry / momentum repo. (2026). _CHIP_DISTRIBUTION.md_. Local repository documentation.**
   - Authors: Jerry / momentum docs
   - Year: 2026
   - Title: `CHIP_DISTRIBUTION.md`
   - Venue: Local repo / docs
   - DOI: `N/A`
   - Readable URL: `https://jp.jerrypsy.top/momentum/factors/scout_rank34_chip_distribution_15m/report.html`
   - Repo URL: `docs/CHIP_DISTRIBUTION.md`
3. **Jerry / momentum repo. (2026). _build_rank34_chip_distribution_clean_replication.py_. Local clean replication script.**
   - Authors: Jerry / momentum research pipeline
   - Year: 2026
   - Title: `build_rank34_chip_distribution_clean_replication.py`
   - Venue: Local repo / research script
   - DOI: `N/A`
   - Readable URL: `https://jp.jerrypsy.top/momentum/factors/scout_rank34_chip_distribution_15m/report.html`
   - Repo URL: `scripts/build_rank34_chip_distribution_clean_replication.py`

---
快检/复盘文件：
- `reports/artifacts/scout_rank34_chip_distribution_15m/overall_summary.csv`
- `reports/artifacts/scout_rank34_chip_distribution_15m/asset_summary.csv`
- `reports/artifacts/scout_rank34_chip_distribution_15m/assumption_sensitivity_summary.csv`
- `reports/site/factors/scout_rank34_chip_distribution_15m/report.html`
