# 2026-04-07 21:50 UTC · Rank 27 breakout-bar taker-imbalance neckline confirmation · first verdict

## 本轮执行小点
- target: `research/park_reframe/2026-04-06_0606_rank27-park-reframe.md`
- action: 判断 `breakout-bar taker-imbalance neckline confirmation` 是否已足够从原 `Rank 27` 的 park residual 独立成新的 raw alpha intake，还是仍只是旧 `neckline / breakout / confirmation` 家族的实现细化
- success_criterion: 必须给出明确 first verdict：若对象把 `neckline break + taker-imbalance confirm` 的独立触发、执行边界与相对旧 breakout/retest 家族的区别压清，则写成 `keep_P1`；若主要仍是旧 neckline / breakout 家族的局部改写，则明确写成 `background / P0`

## 读取到的关键上下文
1. 原始 `Rank 27` clean replication 已明确失败点：`raw breakout`、`neckline_confirm`、`neckline_confirm_plus_retest_hold` 都没有形成跨资产、成本后可保留的 pocket；问题核心是旧的确认层写法不够成立。
2. `Rank 27` 的唯一自然单轴 reframe 已经在 `Rank 27b = ATR-scaled retest zone + bounce reclaim` 上被诚实消费过；而且此前两次低频复核（`2026-03-23`、`2026-03-30`）都已明确：不要把同一条旧 neckline/retest 血缘继续细切出平行分支。
3. 这次 `breakout-bar taker-imbalance confirmation` 虽然看起来换了 confirmation modality，但主语仍是同一个 `pattern-complete neckline breakout`，只是把 `post-break retest_hold` 换成 `breakout-bar flow confirm`。
4. 该改写没有把对象推进成新的 raw alpha skeleton；它仍依附于旧的 chart-pattern/neckline breakout 家族，且本质上还是在修补原 Rank 27 的 confirmation layer，而不是提出一个独立的新 pocket。

## 本轮判断
### first verdict
- 结论：`background / P0`

### 为什么不是 `keep_P1`
- 它没有脱离原 `Rank 27` 的语义边界：依旧是 `double-bottom/top + neckline breakout` 主体，只是把确认方式从回踩改成 order-flow。
- 这类修改更像旧 family 的 confirmation modality 替换，而不是足以独立编号、独立 intake 的新 raw alpha。
- 在 `Rank 27b` 已消费过唯一自然 rescue 之后，再把 `27c` 写成另一条平行 confirmation 分支，会让同一条旧 rank 的 residual 被拆成多条近义再包装，违反当前 policy 对 park residual 的诚实收口要求。
- 若 breakout 主题后续真的还能活，更像应在更上位的 event-driven / microstructure breakout family 里重新宿主化，而不是继续作为 `Rank 27` 血缘下的新 intake。

## 会改变系统认知的话
`breakout-bar taker-imbalance neckline confirmation` 仍只是旧 `Rank 27` neckline/breakout family 的 confirmation modality 改写，未形成独立新 intake，因此本轮 first verdict 收口为 `background / P0`。

## runtime write-back
- `cycle_plan[4]` 应写为 `done`
- `cycle_plan[4].result` 应写入上述 first verdict 句子
- `Background pool.latest_parked` 更新为同一句，表示最新被诚实收口的对象仍回到背景池

## 产出
- log: `research/optimization_loop/2026-04-07_2150_rank27_breakoutbar_takerimbalance_first_verdict_background.md`
