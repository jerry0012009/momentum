# Rank 336 / liquidity-split last-day return cross-sectional — survivor follow-up = background/P0

- Time: 2026-04-05 01:42 UTC
- Target: `Rank 336 / liquidity-split last-day return cross-sectional`
- Slot: Surviving candidate
- Verdict: `background/P0`

## Why this changes system belief

`Rank 336` 的唯一 survivor follow-up 已经把这条线最关键的问题收口了：

> 在我们当前真正可交易的 `liquid-major perp` desk 上，`24h rank` 这条线留下来的确是 **continuation 倾向**；但这次 follow-up 仍然**没有**把它收成一个足够 admission 的、带清晰治理边界的独立对象。

换句话说，新增认知不是“这条线彻底错了”，而是：

1. **方向判断并没有被推翻**：现有 `15m` portability 证据仍支持 liquid bucket 更像 winner-follow，而不是 loser-bounce。
2. **成本后也不是立刻归零**：已有本地 probe 显示 `mom_liq` 在 `15m / 24h formation / 1h hold` 下即使计入单边 `4~8bps` 成本，仍保留正 Sharpe 与正累计收益。
3. **但 admission 所需的唯一 decisive blocker 这轮并未被解决**：当前并没有新的 clean-room 证据把这条 edge 从 `BTC/market leader projection` 中剥离出来，也没有把“到底哪条 liquid-major bucket rule 才是 desk 可写进治理的正式边界”收成单一规则。

因此，这轮 follow-up 的最诚实结论不是 `promote_P2`，而是：

> `Rank 336` 进一步确认了“liquidity split 会改写 `ret_24h` 的信号符号，liquid-major desk 更该先看 continuation”这条研究纪律；但它仍更像 **family-level framing / sign-router discipline**，而不是已经够资格进入 admission 的独立 `P2` 对象。

## Evidence used this round

### A. 与同 family 的最近 clean-room 证据并读

我把 `Rank 336` 与刚在前几天诚实收口的同 family 对象一起核对：

- `Rank 300 / liquidity-split lagged-return sign-flip alpha`
- `research/quant_digests/2026-04-02_2319_liquidity-split-lagged-return-alpha.md`
- `reports/artifacts/quant_digests/liquidity_split_tail_reversal_20260325/summary.json`

这些材料已经给出当前 desk 最关键的迁移事实：

- broad loser-bounce 在 liquid perp desk 上不是主线；
- 高流动性 bucket 的 winner-follow 才是活着的那一侧；
- 但真正稳定、可写进治理的 cutoff / bucket rule 仍未收口。

`Rank 336` 虽然叙事更聚焦在“last-day return + liquidity split”，但 survivor 轮要求的不是再证明一遍 family 方向，而是回答：

> 这条线是否已经足够独立、足够治理化，值得升到 `P2 admission`？

当前答案仍然是否定的。

### B. 成本后的 liquid-major continuation 仍有生命迹象，但这不是本轮 blocker 的解

已有 `2026-04-02` digest 中的本地 Binance USDⓈ-M `15m` probe 给出：

- `mom_liq` gross Sharpe `3.02`
- 单边 `4bps` 后 Sharpe `2.70`
- 单边 `8bps` 后 Sharpe `2.38`

这足以支持：

> `liquid-major continuation` 不是纯论文词藻，至少在 `15m` 执行层上有正向 portable 痕迹。

但这一步并**没有**直接回答当前 survivor 轮要求补的第二半：

- 这些收益里有多少只是 `BTC beta / market leader drift`？
- 如果做严格 beta-neutral 或 market-neutral 处理后，还剩多少 truly cross-sectional edge？
- 该 edge 的 governance 边界是 top-20% liquidity、top decile，还是更窄的 majors 白名单？

### C. 因为缺的不是“再来一点同方向证据”，而是“单一可迁移治理规则”

按当前 policy，survivor 只有一次 follow-up 预算；这次预算不能再被用来重复“high-liquidity continuation 似乎活着”。

本轮真正该回答的是：

> 现有材料是否已经足够把 `Rank 336` 升成一个可 admission 的 `P2` 主体？

答案仍然是否定的，原因有二：

1. **beta / leader projection 仍未被干净剥离**
   - 当前 digest 只把这件事列成要测事项，没有新的 clean-room 结果。
   - 因而还不能说这是一条已经脱离 market drift 的独立 XS alpha。

2. **bucket governance 仍未收成单一规则**
   - 我们知道不该再把全市场混成一个 loser-bounce 结论；
   - 也知道 liquid side 更像 continuation；
   - 但还不知道 admission 时到底该写成怎样的正式对象：`top liquidity quintile`、`majors whitelist`、还是其他更窄定义。

在这种状态下继续把它留在前排，只会重复 `Rank 300` 已经暴露过的同类问题。

## Exit decision

因此本轮不做 `promote_P2`。

`Rank 336` 的唯一 survivor follow-up 最诚实的收口是：

> 它成功强化了一个应保留在研究体系里的系统认知——**任何 `ret_24h` / short-term XS momentum-reversal 题目，在进入主池前都必须先过 liquidity split，且 liquid-major desk 默认更该先验 continuation**；但它仍未把 beta-neutral 独立性与正式 bucket rule 收成 admission 所需的单一治理对象，因此 survivor 预算用尽后应回到 `background/P0`。

## Runtime action taken

- `Rank 336` 从 `Surviving candidate slot` 移出
- survivor follow-up budget 用尽，本轮收口为 `background/P0`
- 释放 survivor 前排锁
- 当前 `cycle_plan` 第 1 项完成；后续 pending fresh intake 才重新成为合法前排动作
