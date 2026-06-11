# Limited Attention seed 在 intake 阶段直接 park：保留机制备忘，不进入当前 fast-lane

## 为什么这次选这个
- 先按 `TRADING DESK BOARD` 检查：`EMA` 当前仍是 `waiting_not_due`，本轮不应在 `Run 1` 空转。
- 当前 active Scout 里，`Rank 17 / Rank 2 / Rank 29` 都属于 `P3 continuity`，且这轮没有真实 `append/review need`；继续围着它们转只会撞上当日 hard cap。
- `Rank 30~37` 的当前允许动作基本都已消耗并已有 `park` 或更清楚 verdict。
- 因此本轮按 `Run 2 / Scout Fast Lane` 走 **fresh intake**，并先把 `docs/RECENT_PAPER_SEEDS.md` 里剩下那条 `Limited Attention Theory of TSMOM` 诚实过掉：如果连当前 desk 需要的最小 clean-room 入口都给不出来，就直接 park，不让它继续占预算。

## 做了什么改动
1. 新增中文 digest：
   - `research/quant_digests/2026-03-17_1730_limited-attention-tsmom-not-fastlane.md`
   - 结论：这条线当前更像机制解释，不像可直接复现的 `paper / repo based 15m crypto` fast-lane 候选。
2. 新增 source-intake 卡：
   - `reports/artifacts/literature/scout_rank38_limited_attention_source_intake_card.csv`
   - 明确写清：若继续推进需要额外 `attention proxy`，这会把当前轮次带离默认 fast lane。
3. 更新索引：
   - `research/quant_digests/INDEX.md`
4. 更新权威板：
   - `docs/TODO.md`
   - 新增 `Rank 38 limited-attention theory of TSMOM / mechanism note -> park / mechanism note only`
   - 同时在 `Next 3 bot3 runs` 顶部补充：这条剩余本地机制 seed 已做完 intake-stage hard verdict，不再算“尚未处理的本地快筛候选”。

## 验证 / 证据
- desk 侧验证：重新核对了 `TODO.md` 顶部 `Next 3 bot3 runs`，当前 `Run 1` 仍不是 due-now；本轮走 `Run 2 / Scout Fast Lane` 合规。
- 候选侧验证：这条 seed 在当前 source-intake 阶段就暴露出硬问题：
  1. 论文更像机制解释，不是现成交易配方；
  2. 若要翻成当前 desk 可执行规则，至少要额外引入一层 `attention proxy`；
  3. 当前本地 fast-lane 没有冻结好的 proxy 数据源；
  4. 因此它甚至早于成本/稳定性问题：在不新增 proxy 假设的前提下，还不能诚实写成可直接复用本地 `15m` cache 的 `trade on / trade off`。
- 本轮 hard verdict：
  - `Rank 38 / limited-attention theory of TSMOM` = **`park / mechanism note only`**
  - 不进入 `clean replication queue`
  - 不进入 `paper candidate pool`

## 风险 / 边界
- 这不是否认 attention 机制可能有用；更准确地说，它当前只适合作为未来 `external-data / regime-gate` 方向的理论备忘。
- 只有当 desk 未来明确要引入可审计的 attention proxy（如搜索、新闻、社交、机构覆盖等）时，这条线才值得重开。
- 本轮没有新开外部数据链，没有扩写新大框架，也没有把这条线误升格成 `paper candidate`。

## 下一步建议
- 若下一轮仍需 `fresh intake`，默认优先认领：
  1. 更接近执行层、能直接落到 `paper / repo based 5m / 15m crypto` 的新 source；
  2. 若本地 seeds 暂时耗尽，再从 `validated shortlist / 既有 repo 邻近实现` 中挑一条能直接做最小 clean replication 的候选。
- 不建议在当前窗口继续重开 `Rank 38`；它已经完成这轮最重要的工作：**被诚实地排除出当前 fast lane。**

## Commit hash
- 未提交。

## 未提交原因
- 当前 git 工作区存在大量与本轮无关的脏文件与未跟踪产物；为避免混提，本轮只留下可审计产物、日志与邮件，不做 selective commit。
