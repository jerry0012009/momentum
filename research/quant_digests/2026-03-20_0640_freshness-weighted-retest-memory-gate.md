# 别把 `retest_count` 当永久加分：`freshness-weighted bounce memory` 更像 Fib retest / breakout follow-up 的时效门
- 时间：2026-03-20 06:40 UTC
- 类型：论文
- 主题标签：breakout-short/fibonacci/retest-hold/ema/psar/support-resistance/retest-count/freshness/decay/regime/filter/paper/crypto/5m/15m
- 证据类型：论文证据

## 1. 这次看了什么
这轮主看 **Ken Chung, Anthony Bellotti (2021)** 的论文 *Evidence and Behaviour of Support and Resistance Levels in Financial Time Series*（arXiv）。

我这次不拿它当“又一篇 S/R 有效性论文”，而是专门抽它更适合 desk 的旁支：
**同样是“之前反复回踩/反弹过”的线位，越新鲜越有用，越陈旧越该降权。**

## 2. 核心结论
- **一句话核心结论**：`retest_count` 不是永久资产，必须乘上 `freshness`（时效）才能用于 5m/15m 的确认层。
- **一句话证明方式**：论文在 EURUSD/LLOY/BRENT 分钟级数据上，做了“历史反弹次数 vs 再次反弹概率”+“时间衰减（macro + micro）”双层检验，并用打乱收益与 AR(1) 模拟做反证。

可直接复用的 3 个数据点：
1. 样本规模（分钟级）：EURUSD `372,607`、LLOY `127,606`、BRENT `307,678`。
2. EURUSD 上，`bprev=1` 的反弹记忆约在 `~350min` 附近衰减到 0.5；`bprev=4` 能拖到 `~900min`（说明“触碰次数”和“时效”是交互项，不是二选一）。
3. 置换检验里，大多数配置下原始序列相对打乱序列的优势概率 `Λ>0.95`，说明这不是纯随机游走能稳定复现的假象。

## 3. 为什么和当前项目有关
这题比继续抽象地讨论“多一次 retest 是否更好”更值，因为它直接给三条收口线补一个缺口：
- `V3 final-verdict / breakout-short follow-up`：同一水平位的“历史有效”应有保质期；过期后不该再当 continuation 证据。
- `Fibonacci confirmation / retest_hold`：`retest_count>=2` 若发生在很久以前，不应与“刚发生的 2 次回踩”同权。
- `EMA / PSAR raw alpha focus`：EMA/PSAR 触发可保留，但若叠加的是“过期线位记忆”，会把 gate 变成噪声放大器。

## 4. 可复刻的最小实验（先做这个）
**研究假设**：在 15m 上，把确认层从 `count-only` 改成 `count × freshness`，能降低假确认并改善成本后质量。

1. 资产/周期/样本：`BTC, ETH, SOL perpetual`，`15m`（执行可加 5m），先跑近 `180d`。  
2. 定义：
   - `touch_count`: 最近 W 根内同侧有效触碰次数（如 W=96）。
   - `age_min`: 距离最近一次有效触碰的分钟数。
   - `freshness = exp(-age_min / tau)`，`tau ∈ {180, 360, 720}`。
   - `memory_score = touch_count * freshness`。
3. 三臂对照：
   - A: baseline（现有 breakout/fib/ema-psar）；
   - B: baseline + `touch_count>=k`（旧口径）；
   - C: baseline + `memory_score>=q`（新口径）。
4. 先看 2 个指标：
   - `post-cost expectancy`；
   - `false-follow / false-hold rate`（入场后 4~8 bars 内失效占比）。

## 5. 风险与保留意见
- 论文不是 crypto 样本，且以传统市场分钟数据为主；迁移前要做 OOS + 成本敏感性。
- 文中 S/R 发现算法是启发式 rolling min/max，不是订单簿驱动；在 perp 上可能漏掉 microstructure 级别线位。
- `tau` 过短会过度丢样本，过长又退化回 count-only；必须做网格 + 稳定性检查。

## 6. 来源
1. Chung, K., & Bellotti, A. (2021). *Evidence and Behaviour of Support and Resistance Levels in Financial Time Series*. arXiv (q-fin.ST).
   - DOI: N/A
   - Readable URL: https://arxiv.org/abs/2101.07410
   - PDF URL: https://arxiv.org/pdf/2101.07410.pdf
   - Repo URL: N/A
2. Garzarelli, F., Cristelli, M., Pompa, G., Zaccaria, A., & Pietronero, L. (2014). *Memory effects in stock price dynamics: evidences of technical trading*. Scientific Reports, 4, 4487.
   - DOI: https://doi.org/10.1038/srep04487
   - Readable URL: https://www.nature.com/articles/srep04487
   - Repo URL: N/A