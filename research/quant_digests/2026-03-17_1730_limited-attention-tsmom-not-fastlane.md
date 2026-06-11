# Limited Attention Theory 先别直接塞进 15m crypto fast lane：它更像机制解释，不像当前可直接复现的 scout 候选
- 时间：2026-03-17 17:30 UTC
- 类型：论文
- 主题标签：trend / momentum / attention / mechanism / regime / crypto / scout
- 证据类型：论文证据 + desk source intake hard verdict

## 1. 这次看了什么
这次回收的是：
- **Aleksi Pitkäjärvi (2022)**
- **A Limited Attention Theory of Time Series Momentum**
- Venue: **SSRN working paper**
- DOI: **10.2139/ssrn.4168092**

对当前 desk 最有用的，不是把它硬翻成一条新 15m 交易规则，而是先诚实回答：**这篇更像“为什么动量可能存在”的机制论文，不像当前可以直接压成 `trade on / trade off` 的 fast-lane alpha 候选。**

翻成人话：它更像在解释“市场参与者注意力有限，所以价格信息不会立刻完全消化，动量可能因此持续一段时间”；但这跟“我现在就能在 BTC/ETH/SOL 15m 上写出一条无需额外代理变量的 clean-room 入场规则”之间，还隔着至少一层 attention proxy / data mapping。

## 2. 为什么本轮选它
当前边际价值比较很直接：
- `EMA` 仍是 `waiting_not_due`，本轮不该在 `Run 1` 空转；
- `Rank 17 / Rank 2 / Rank 29` 都属于 `P3 continuity`，当前没有真实 `append/review need`，继续围着它们转只会消耗当日 hard cap；
- `Rank 30~37` 的允许动作基本都已消耗并已给出 `park` 或更清晰 verdict；
- `docs/RECENT_PAPER_SEEDS.md` 里，剩下最贴近当前主题、但还没被 desk 正式过一遍的，就是这条 **Limited Attention Theory**。

所以这轮最诚实的动作，不是凭空扩一个新框架，也不是退回 `Run 3`，而是先把这条 seed 过掉：**如果它连当前 desk 需要的最小 clean-room 入口都给不出来，就在 intake 阶段直接 park。**

## 3. 对当前项目最重要的结论
- **结论 1：这篇论文更像机制解释，不是现成交易配方。**
- **结论 2：若要把它翻成当前 15m crypto scout 候选，必须额外发明或引入 attention proxy**（例如新闻/搜索/社交/订单流关注度、机构覆盖变化、市场级 attention shocks 等）。
- **结论 3：这违反了当前 Scout Seat 的默认优先顺序。** 当前默认要的是 **paper / repo based、规则可直接写清、能立刻用本地样本做 clean replication** 的候选，而不是再多开一层 proxy 假设。
- **结论 4：因此这条线当前最诚实的 hard verdict 不是 `admit_to_clean_replication_queue`，而是直接 `park / mechanism note only`。**

## 4. 对 desk 的最小 clean-room 映射（以及为什么这里就停）
### 候选名
`limited-attention momentum regime note`

### 勉强能写出的 trade on / trade off
如果硬要翻：
- **trade on**：只有当某个可观察的 `attention proxy` 提示“当前信息扩散仍不充分 / 关注度正在追上价格趋势”时，才允许顺着已有趋势信号交易；
- **trade off**：attention proxy 不支持、与价格方向冲突、或 attention shock 已被充分消化。

### 但当前致命问题在这里
上面这段写法**还不是当前 desk 可执行规则**，因为：
1. 论文本身先给的是机制，不是当前 repo 现成模块；
2. 当前本地 fast-lane 没有一个已经冻结好的 `attention proxy` 数据源；
3. 一旦为了它再去补代理变量和外部数据，这轮就会从 `paper/repo based fast intake` 滑向新的 research framework。

换句话说：
- 它现在**能讲故事**；
- 但还**不能诚实地下单**。

## 5. 为什么它当前不如其他已 park / 已推进候选
和已经跑过的本地候选相比，这条线的问题不是“成本后变负”，而是更早：
- `Rank 37 classic sparse TSMOM` 至少能直接复用本地 `BTC/ETH/SOL 120d 15m` cache，立刻做最小 clean replication；
- `Rank 36 TSM vs drift honesty gate` 至少能在当前样本上直接回答“这个动量 pocket 到底是不是 drift 包装”；
- 这条 **Limited Attention Theory** 则连第一步的最小可执行口径都还没冻结。

因此它对当前 desk 的边际价值，更像：
- 给未来 external-data / regime-gate 方向留一个机制备忘；
- 而不是现在就抢走 fast-lane 的 replication 预算。

## 6. 当前 hard verdict（source intake 即止）
- **`Rank 38 / limited-attention theory of TSMOM`：`park / mechanism note only`**

它当前不进入：
- `paper candidate pool`
- `clean replication queue`
- `narrow paper pilot`

原因不是这篇论文没价值，而是它**不符合当前这一轮 Scout Seat 的准入规则**：
1. 不能在不新增 proxy 假设的前提下，直接写成当前 desk 的 `trade on / trade off`；
2. 不能直接复用现有本地 15m cache 做最小 clean replication；
3. 若继续推进，默认会把这一轮带离 `paper / repo based fast-cycle crypto` 主线。

## 7. 风险与保留意见
- 这不是否认“attention 机制可能重要”；
- 更准确地说，它现在只适合作为**未来 external-data / regime-gate 队列的理论支持**；
- 只有当 desk 未来明确要引入 attention proxy（例如搜索、新闻、社交、机构覆盖或其他可审计 proxy）时，这条线才值得重开。

## 8. 对下一轮的影响
- 好处是：**本地 seed 里的这条机制论文现在已经被诚实过掉，不会下轮又被误当成 fast-lane 候选重复认领。**
- 若下一轮还需要 `fresh intake`，默认应继续优先找：
  1. 能直接落到 `paper / repo based 5m / 15m crypto` 的新 source；或
  2. 若本地 paper seeds 已基本耗尽，再从 validated shortlist / 已有 repo 邻近实现里认领更接近执行层的候选。

## 9. 来源
1. Pitkäjärvi, A. (2022). *A Limited Attention Theory of Time Series Momentum*.
   - DOI: https://doi.org/10.2139/ssrn.4168092
   - Readable URL: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4168092
