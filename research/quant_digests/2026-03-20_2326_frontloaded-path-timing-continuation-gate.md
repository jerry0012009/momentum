# 别把同样 1h 净位移都当同质量：`front-loaded path timing` 比 `late burst` 更像 15m continuation gate
- 时间：2026-03-20 23:26 UTC
- 类型：论文 + Binance 公共数据快检
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/path-shape/timing/front-loaded/late-burst/continuation/filter/paper/crypto/15m
- 证据类型：论文证据 + 本地最小复核

## 1. 这次看了什么
这次主看 **Jiang, Kelly, Xiu (2023)** 的 *（Re-)Imag(in)ing Price Trends*。它最值钱的地方，不是逼我们把 15m desk 直接改成图像模型，而是提醒一件更朴素的事：**同样都是“过去 1 小时涨了/跌了这么多”，路径形状本身也可能有信息。**

沿着这个思路，我这轮没有去抄论文 headline，而是拎出一个更适合当前三条收口线的小分支：**同样 4 根 15m K 线形成的净位移里，这段 move 是“前半段先走完、后半段只是续推”，还是“最后两根突然 late burst 冲出来”？** 这个 `path timing` 很像可直接塞进 `V3 final-verdict / breakout-short follow-up`、`Fib retest_hold`、`EMA / PSAR raw alpha` 的廉价过滤层。

## 2. 核心结论
- **一句话核心结论：** 对 15m 来说，**同样 1h 净位移下，前半段先走、后半段续推的 `front-loaded path`，比“最后 30 分钟才突然冲出来”的 `late burst` 更像可跟随 continuation。**
- **一句话说明它怎么证明：** Jiang et al. 给出“价格形状不该被压成单一收益率”的研究方向；我再用 `BTC/ETH/SOL` perpetual 近 180d 的 15m 公共行情，做了一个只看“同 endpoint、不同 path timing”的轻量快检。
- 本地快检口径：每个币取最近 **180d** 15m K 线；只保留 `4-bar net return` 落在各自 **绝对值前 25%**、且 4 根里至少 **3 根方向一致** 的事件；再算 `late_share = 最近 2 根同向贡献 / 4 根同向贡献`。
- 合并 `BTC/ETH/SOL` 后，`front-loaded`（`late_share < 0.35`）与 `late burst`（`late_share > 0.65`）的 **1h 净位移中位数几乎相同**（**0.96% vs 0.99%**），但后续表现明显不同：
  - 全样本 **下一根同向率**：`front-loaded` **49.44%** vs `late burst` **44.80%**（`n=2923` vs `3214`，+**4.64pct**）
  - 全样本 **未来 2 根净继续同向率**：**50.02%** vs **46.20%**（+**3.82pct**）
  - 下行事件（更贴近 `breakout-short follow-up`）**未来 2 根净继续下行率**：**51.80%** vs **46.16%**（`n=1419` vs `1770`，+**5.64pct**）
  - 上行事件 **下一根继续上行率**：**47.54%** vs **42.11%**（`n=1504` vs `1444`，+**5.43pct**）
- 直白翻译成人话：**不是“走得越猛越该追”，而是“如果大部分 move 都挤在最后两根 15m 才突然完成，它更像临门一脚的加速，后续反而更容易不稳”。**

## 3. 为什么和当前项目有关
- 对 `V3 final-verdict / breakout-short follow-up`：`late burst` 下破更像“已经冲过头的最后一脚”，适合做 **continuation veto / size-down**，而不是默认追空。
- 对 `Fibonacci confirmation / retest_hold`：如果上冲主要集中在最后两根 15m，先别把它当高质量 hold，**更像该等回踩确认**，而不是把强冲本身误读成稳态 continuation。
- 对 `EMA / PSAR raw alpha focus`：这层不需要替代主触发，只要作为 **path-shape overlay** 接在原信号后面，就能更诚实地区分“顺滑趋势推进”与“末端突然拉扯”。
- 这比继续抠某个固定参数更值得：它直接服务三条收口线，而且不要求新数据源、不要求复杂模型，**只靠公开 K 线就能先做最小实验**。

## 4. 可复刻的最小实验
- 研究假设：在 15m setup 触发时，**`front-loaded` 路径比 `late burst` 路径更容易延续；把 `late burst` 当 veto / size-down，会改善 post-break follow-up 质量。**
- 一个可计算定义（15m，触发前 4 根）：
  - `sign = sign(close_t / close_t-4 - 1)`
  - `aligned_ret_i = max(sign * ret_i, 0)`
  - `late_share = (aligned_ret_{t-1} + aligned_ret_t) / sum(aligned_ret_{t-3:t})`
  - 分桶：`front_loaded < 0.35`，`mid 0.35~0.65`，`late_burst > 0.65`
- 最小回测切口：`BTC/ETH/SOL`，近 **120~180d**，15m，分别叠到三条线当前触发器上：
  1. baseline
  2. `late_burst_veto`
  3. `front_loaded_only`
  4. `late_burst_size_mult = 0.5`
- 最该先看 4 个指标：`post_cost_return`、`false_follow_ratio`、`trade_count`、`MAE<1R 占比`。
- **下一步怎么测（本轮明确动作）**：
  1. 先只把这层加到 `breakout-short follow-up`，验证 `late_burst_veto` 是否降低 false follow；
  2. 再在 `Fib retest_hold` / `EMA continuation` 上测它更适合做 `veto` 还是 `size-down`；
  3. 若样本外仍保留方向差异，再考虑把 4 根窗口扩成 `6 根`，检查是否只是短窗巧合。

## 5. 风险与保留意见
- Jiang et al. 的主场景不是 15m crypto perpetual；这里是**借它的“shape matters”思想**，不是声称论文已直接验证本 desk 规则。
- 当前快检只做了方向继续率，不是完整成本后回测；能不能活过手续费与滑点，仍要靠正式策略口径复核。
- `late_share` 阈值（0.35/0.65）是起步值，不该直接生产化。
- 这个特征可能部分在代理“是否过度冲刺 / 是否临近 exhaustion”，所以后续要和已有 `MAX(5m)`、`event clock`、`volume confirmation` 做去重检查。

## 6. 来源
1. Jiang, J., Kelly, B., & Xiu, D. (2023). *(Re-)Imag(in)ing Price Trends*. *The Journal of Finance*.
- DOI: https://doi.org/10.1111/jofi.13268
- Readable URL: https://onlinelibrary.wiley.com/doi/full/10.1111/jofi.13268
- OpenAlex metadata / abstract mirror: https://api.openalex.org/works/https://doi.org/10.1111/jofi.13268
- Repo URL: N/A（论文）

2. 本地最小复核（公开可得数据）
- 数据源：Binance USDⓈ-M Futures 公共 K 线 API（公开可得）
- 更新频率：15m
- 复核口径：`BTCUSDT/ETHUSDT/SOLUSDT`，近 180d，比较同等 `4-bar net move` 下的 `front-loaded` vs `late burst`
- 结果文件：`reports/artifacts/literature/tmp_path_timing_backloaded_quickcheck_180d.csv`
- Repo URL: N/A（本地脚本化统计）
