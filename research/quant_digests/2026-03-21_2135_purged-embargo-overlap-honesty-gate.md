# 别把 15m OOS 当真：先过 `purged + embargo` 的 interval-overlap honesty gate
- 时间：2026-03-21 21:35 UTC
- 类型：GitHub 仓库 + 经典方法论文 + 本地快检
- 主题标签：breakout-short / fibonacci / retest_hold / EMA / PSAR / purged-cv / embargo / label-leakage / OOS / honesty-gate
- 证据类型：论文证据 + 工程实现 + 本地数据快检

## 1) 这次看了什么
我这轮不是再找一个新 trigger，而是补一层更直接服务三条收口线的“评估诚实门”：看 `CombinatorialPurgedCV`（skfolio）和 Purged/Embargo 方法怎么防止时间重叠泄漏，并用本地 15m trade log 做了最小快检。

## 2) 核心结论
- **一句话核心结论：** 对我们这种 `signal -> hold N bars` 的 15m 策略，先不处理 train/test 区间重叠，再漂亮的 OOS 都可能偏乐观。
- **一句话证明方式：** 我直接用本地三条 archetype 的已落地交易区间（`signal_ts ~ exit_ts`）做重叠统计，结果显示随机切分时重叠非常高，而 `purged + embargo` 能把这块泄漏显式扣掉。
- 本地快检（`reports/artifacts/scout_rank70_fast_entry_slow_exit_handoff_15m/trade_log.csv`，`baseline_exit`）显示：
  - 随机 80/20 切分下，train 与 test 标签区间重叠均值：
    - `breakout_short` **44.5%**
    - `fib_retest_long` **38.8%**
    - `ema_psar_long` **50.5%**
  - 若改用时间分块 + purged/embargo（10 folds, test=2 folds, embargo=8 bars=120min），平均 purge 比例为：
    - `breakout_short` **2.55%**（额外 embargo **0.73%**）
    - `fib_retest_long` **5.39%**
    - `ema_psar_long` **1.69%**
- 这说明：**泄漏不是抽象风险，而是可量化且 setup 不对称的风险**；`fib_retest_hold` 的重叠敏感性在这组数据里最高。

## 3) 为什么和当前项目有关
这轮和三条收口线是直接相关，不是“统计洁癖”：
- `V3 final-verdict / breakout-short follow-up`：很多 verdict 都是事件后若干根 K 的路径判决，若 train/test 区间重叠，容易把“同一段波动结构”重复学习。
- `Fibonacci confirmation / retest_hold`：回踩确认天然有 clustered signals，最容易出现标签区间互相覆盖。
- `EMA / PSAR raw alpha focus`：raw edge 本来就薄，少量泄漏就可能把 OOS 符号翻正，导致错误晋级。

所以这一刀的价值是：在继续收口前，先保证“我们看到的 OOS 改善”不是评估口径送的。

## 4) 可复刻的最小实验（下一步怎么测）
**研究假设**：三条线里，凡是带 `hold 8 bars` 或更长管理窗的规则，如果不用 purged/embargo，OOS 会系统性偏乐观。

**最小可计算定义**：
- 每笔信号对应一个标签区间：`[signal_ts, exit_ts]`
- overlap 定义：train 区间与任一 test 区间相交
- purge：删除 overlap 的 train 样本
- embargo：删除 test 结束后 `H`（默认 8 bars）内的 train 样本

**最小回测切口**：
- 资产：BTC/ETH/SOL
- 周期：15m（必要时补 5m 作为 entry confirm）
- 候选：每条线先固定 20~50 个变体（不要先上百）
- 统一执行：`next-bar open + no-overlap + 6/10/15 bps`

**先看 2 个指标**：
1. `OOS Sharpe / Calmar` 在 random split vs purged split 的降幅
2. `winner retention`（random split Top-N 在 purged split 还能留几条）

**入池门槛建议（第一版）**：
- 仅在 purged/embargo 评估下仍为正且 trade count 过线的候选，才允许进下一轮 final-verdict 讨论。

## 5) 风险与保留意见
- Purged/embargo 只能让评估更诚实，**不会**把坏 alpha 变好。
- `embargo_size` 必须跟最大持仓窗、特征延迟窗口一致；写太小仍会漏，写太大会过度砍样本。
- 若候选本来就稀疏，purged 后方差会显著变大，需要同步看 trade count 与窗口稳定性。

## 6) 来源
- **López de Prado, M. (2018). _Advances in Financial Machine Learning_. Wiley.**
  - Readable URL: `https://www.oreilly.com/library/view/advances-in-financial/9781119482086/`
  - 备注：Purged K-Fold / Embargo / CPCV 的方法母体。
- **Bailey, D. H., Borwein, J., López de Prado, M., & Zhu, Q. J. (2015). _The Probability of Backtest Overfitting_. SSRN / Journal of Computational Finance.**
  - DOI: `https://doi.org/10.2139/ssrn.2326253`
  - Readable URL: `https://ssrn.com/abstract=2326253`
- **skfolio maintainers (2026). _CombinatorialPurgedCV_ docs + repo.**
  - Readable URL: `https://skfolio.org/generated/skfolio.model_selection.CombinatorialPurgedCV.html`
  - Repo URL: `https://github.com/skfolio/skfolio`
- **mlfinlab docs (Hudson & Thames). Purged/Embargo + CPCV implementation note.**
  - Readable URL: `https://random-docs.readthedocs.io/en/latest/implementations/cross_validation.html`
- **本地快检产物**：
  - `reports/artifacts/literature/purged_embargo_overlap_quickcheck_2026-03-21.csv`
  - `reports/artifacts/literature/random_split_overlap_benchmark_2026-03-21.csv`
