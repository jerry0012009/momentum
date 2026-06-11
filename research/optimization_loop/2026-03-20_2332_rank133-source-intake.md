# Rank 133 / triple barrier honest final-verdict layer intake

## 为什么这次选这个
- 先按 desk 规则执行了 `Run 1 / EMA due-check first`：
  - `python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due`
  - 返回仍是 `waiting_not_due`；当前没有新的 `due-now / overdue` lane，最靠前的仍是 `Crypto 1d+1wk（BTC/ETH/SOL） | due_soon | 约 28 分钟后到点`。
- 因此这轮不能伪造 paper refresh，必须切到 `Run 2 / Rank 133 source intake`。
- 再比较当前 active Scout 的边际价值：
  - `Rank 127 / 125 / 112 / 111` 都是 `P1 / budget used / evidence_pool`，不适合继续磨；
  - hosted `P3`（`122 / 2 / 17 / 29 / 32b`）这轮没有 status-changing event，不该抢主资源位；
  - `fixed partial -> R/ATR partial` 当前只配做 tiny-live / path-management fallback，不应抢在 Scout 主点之前。
- 所以这轮最诚实的动作，是把已经在 desk board 上排到第一位的 **`Rank 133 / triple barrier honest final-verdict layer`** 正式做完 `source intake + honesty gate`。

## 做了什么改动
1. 新建 queue-facing artifact：
   - `reports/artifacts/literature/scout_rank133_triple_barrier_honest_final_verdict_source_intake_card.csv`
2. 新建 reader-facing 页面：
   - `reports/site/reading/repo_scout/rank133_triple_barrier_honest_final_verdict_source_intake.html`
3. 最小更新 `docs/TODO.md` 顶部 desk board：
   - 把 `Rank 133` 从 `source intake next` 改成 `guard-passed / clean replication next`；
   - 把 `Next 3 bot3 runs` 改成：`Run 1 = EMA due-check` → `Run 2 = Rank 133 最小 clean replication（若仍 waiting）` → `Run 3 = 根据 clean replication 做 keep_P1 / promote_P2 / park，或回下一条 fresh intake`；
   - 把最新关键 evidence 追加为 `2026-03-20 23:32 UTC / Rank 133 source intake + honesty gate passed`。

## 验证 / 证据
### 1) EMA 本轮仍是 waiting_not_due
实际执行：
```bash
python3 scripts/run_ema_paper_trading_guarded_refresh.py --require-due
```
关键信号：
- `当前没有 due-now / overdue lane`
- 最近 due：`Crypto 1d+1wk（BTC/ETH/SOL） | due_soon | 约 28 分钟后到点`
- `require-due` 已开启：当前应等待下一根 completed bar，而不是伪造 refresh

### 2) Rank 133 两条轻量诚实守门
当前最诚实的 `trade on / trade off`：
- **trade on**：它只配当 `breakout-short / Fib retest_hold / EMA-PSAR` 的 shared post-entry verdict harness。先冻结既有 entry，不改信号定义，只把结果层统一改写成 `tp_first / sl_first / timeout`。
- **trade off**：它不是独立 alpha，不是新的 entry trigger，也不是把 label 一换就自动更赚钱。若它偷改 entry、把 barrier 参数自由度包装成 alpha、或依赖 signal 之后路径信息，就不得升格，更不能直接拿去当 live execution rule。
- **honesty gate**：通过。entry 时点必须先冻结；label 只允许由 entry 之后真实 path 的 `first-touch` 事件生成；barrier 参数必须在训练段或滚动过去窗口冻结；后续 clean replication 必须统一到 `next-bar open + no-overlap`，禁止用 future swing、全样本最优 barrier、或 verdict 倒灌 entry。

### 3) 为什么它现在比旧 P1 更值钱
- `Rank 127 / 125 / 112 / 111` 都已经拿过那 `1` 次便宜诚实检查，本轮继续回头磨更像 admission wording，而不是减少真实 gate。
- `Rank 133` 补的是三条主线共同缺的 `honest final-verdict layer`：减少用 `fixed n-bar` forward return 错判 follow-up 质量。
- 它的下一步天然就是：`source intake -> honesty gate -> 1 次最小 clean replication`，非常符合当前 Scout fast lane。

## 当前硬结论
**`Rank 133 / triple barrier honest final-verdict layer = guard-passed / admit_to_clean_replication_queue`**。

翻成人话：
- 别再把 follow-up verdict 固定成“后 3 根 / 后 6 根 bar 涨跌”。
- 更诚实的问题是：**这笔 setup 放行以后，市场到底先给了 TP、SL，还是压根拖到 timeout。**
- 这条线值得给 `1` 次最小 clean replication 预算，但还远不到 `paper candidate`。

## 风险 / 边界
- 这轮只做了 `fresh intake + honesty gate`，没有做 clean replication，更没有进入 `Light Stability Pack`。
- 当前主要证据来自论文框架与 repo 实现，不是现成的 15m crypto OOS 完整 replication；这轮保留的是“判决层值得测”，不是“alpha 已被证明”。
- `TP / SL / T` 本身会引入参数自由度，因此下一轮必须显式看它是不是只靠单一 pocket / 单一参数才显得好看。

## 下一步建议
- 若下一轮 `EMA` 仍 `waiting_not_due`，则严格只给 `Rank 133` **1 次最小 clean replication**：
  - 对照：`fixed n-bar forward verdict` vs `tp/sl/timeout triple-barrier verdict`
  - 统一口径：冻结既有 entry、`BTC/ETH/SOL perpetual 15m`、必要时 `5m` 只做 execution readout、`next-bar open + no-overlap`
  - 成本：`6 / 10 / 15 bps per side`
  - 主看：`timeout_share / tp_first_rate / sl_first_rate / post_cost_expectancy / trade_count_retention`
- 若 clean replication 只是换标签名字却没有减少真实误判，或 barrier 结果强依赖单一 pocket / 参数，则直接 `keep_P1` 或 `park`，不要继续打磨 wording。

## Commit hash
- 未提交。
- 原因：repo 工作区仍有大量与本轮无关的脏文件，这轮不适合做安全 selective commit。
