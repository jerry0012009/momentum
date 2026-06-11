# 别把《Time Series Momentum: Is It There?》误读成当前 15m crypto scout fast lane 候选
- 时间：2026-03-17 18:45 UTC
- 类型：论文 / source intake hard verdict
- 主题标签：trend / momentum / validation / honesty-gate / scout
- 证据类型：论文证据 + 执行层映射判断

## 1. 这次为什么重看它
当前 `Paper Seat / EMA` 处于 `waiting_not_due`，而本地 `paper / repo based 5m / 15m crypto` fast-lane shortlist` 已被连续多轮快速消化。按 desk 规则，这一轮仍应先从 `docs/RECENT_PAPER_SEEDS.md`、`research/quant_digests/INDEX.md`、`validated_alpha_shortlist_2026-03-10.md` 里再认领 1 条旧 seed，看它是不是还能诚实进入当前 `Scout Seat`。

`Huang, Li, Wang, Zhou (2020) / Time series momentum: Is it there?` 确实值得重看，但它真正回答的是：**别把“策略赚钱”直接误认成“简单 past-return sign 已被证明有稳定 alpha”。** 这更像验证/反证层，而不是现成执行模板。

## 2. 对当前 desk 最重要的结论
### 结论一：这不是当前 fast lane 需要的“可冻结执行模板”
这篇论文的价值，在于拆分：
- `简单 TSM 信号`
- `历史漂移基线（TSH-like）`
- `仓位缩放 / 风险层`

它适合拿来做 **honesty gate / baseline audit**，不适合直接当作当前 15m crypto 的新候选模板。因为如果把它塞进 fast lane，默认下一步会变成：
1. 重新定义 `TSM_N`
2. 重新定义 `TSH_like`
3. 再做等权 / vol-scaled A/B
4. 再回答和当前结构/回抽主线到底怎么衔接

这本质上是在开一条**验证框架线**，而不是认领一条现成 candidate。

### 结论二：它不是坏 source，但更像“研究校验器”
这篇论文没有明显 `lookahead / repaint / leakage` 低级问题；问题不在作弊，而在**用途错位**：
- 它最擅长回答“你是不是把策略收益错看成信号 alpha 了”
- 不擅长直接给当前 desk 一个 `trade on / trade off / exit / hold / no-overlap` 已冻结好的执行规范

### 结论三：当前最诚实 verdict 应是 `park / validation-context only`
对当前 desk 来说，更直白的读法是：
- 它可以继续当 `TSM vs drift / baseline honesty` 的学术背书
- 也能帮助解释为什么 `Rank 36 / Rank 37` 这种线要先过诚实门
- 但它**不该冒充成新的 fast-lane scout candidate**

## 3. hard verdict
**`park / validation-context only`**

更直白地说：
- 这是好的“别自欺”论文
- 不是当前最适合推进到 `clean replication -> Light Stability Pack -> paper candidate` 的 source

## 4. 对当前排班的影响
这轮把一条仍未正式写回 authoritative board 的旧 seed 也完成了 intake-stage 定性。结果是：
- 它没有补出新的 `paper / repo based 5m / 15m crypto` fast-lane 候选
- 它只加强了“当前本地剩余 seeds 主要是验证 / 机制 / 长周期母论文，不是现成执行模板”这一判断

因此，只要后续没有新的合格本地 source 被明确点名，`EMA waiting_not_due` 的下一优先动作就可以更诚实地回退到 `Run 3 / tiny-live plumbing`，而不是继续假装本地 fast lane 还有新模板没处理。

## 5. 来源
- Huang, D., Li, J., Wang, L., & Zhou, G. (2020). *Time series momentum: Is it there?* Journal of Financial Economics, 135(3), 774-794.
- DOI: https://doi.org/10.1016/j.jfineco.2019.08.004
- Readable URL: https://www.sciencedirect.com/science/article/pii/S0304405X19301953
- 关联旧摘要：`research/quant_digests/2026-03-11_1328_time-series-momentum-is-it-there.md`
