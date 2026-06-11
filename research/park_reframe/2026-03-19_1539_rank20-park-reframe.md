# 2026-03-19 15:39 UTC · Rank 20 park reframe review

## Scope
- Source rank: `Rank 20 price-volume divergence breakout filter`
- Original verdict stays: `park / evidence pool`
- This round only asks: **should Rank 20 derive one narrower reframe hypothesis, without overturning the original park?**

## Read set
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- recent reframe logs:
  - `research/park_reframe/2026-03-19_1334_rank5-park-reframe.md`
  - `research/park_reframe/2026-03-19_1111_rank19-park-reframe.md`
- needed evidence:
  - `research/optimization_loop/2026-03-17_0326_rank20-price-volume-divergence-park.md`
  - `research/quant_digests/2026-03-19_0706_volume-price-interaction-admission-layer.md`
  - `research/quant_digests/2026-03-19_1241_impulse-volume-small-body-retest-hold-gate.md`

## Why this rank
- It is within `Rank 1~37` and currently parked.
- It has **not** been reviewed by `bot6` in the recent 7-day reframe queue.
- The original failure was concentrated but interpretable: the standalone `price-volume divergence breakout filter` did **not** improve the baseline momentum family, yet the failure looks more like a **role problem** than a proof that price-volume interaction has zero information.
- New nearby evidence now points to one narrow reframe that keeps the original theme but strips the overclaim: **stop asking divergence warning itself to be the strategy; test volume-price interaction only as a shared admission layer for existing continuation / retest setups.**

## 1) 原 rank 为什么 park？
Rank 20 被 park，核心不是“量价关系这个主题彻底没信息”，而是它在原 clean replication 里被写成了一个 **standalone breakout filter family**，而且结果不够诚实：

- baseline `baseline_mtf_momentum @ 6bps/side`
  - `mean_total_return≈-38.69%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈570.7`
- 主变体 `pvd_break24_delta0.5_warn3 @ 6bps/side`
  - `mean_total_return≈-39.22%`
  - `positive_asset_ratio=0/3`
  - `mean_trades≈552.0`
- 也就是说，它不仅没把 baseline 拉回 admission 线，反而还略差。

Light Stability Pack 也没有留下正 pocket：
- 时间稳定性：`bucket_1≈-10.84% / bucket_2≈-18.85% / bucket_3≈-15.32%`，`0/3 positive buckets`
- 参数稳定性：最不差邻域 `pvd_break20_delta0.5_warn3≈-37.86%`，仍明显为负
- 跨资产：`BTC≈-52.19% / ETH≈-45.27% / SOL≈-20.21%`，`0/3 positive`
- 成本生存：`6 -> 10 -> 15 -> 20bps` 持续恶化（约 `-39.22% -> -61.37% -> -77.93% -> -87.29%`）

翻成人话：
- 不是“样本太少所以先别下判断”；
- 而是 **把 volume divergence warning 直接写成 breakout 交易家族的主过滤器后，跨时间、跨参数、跨资产、跨成本一起不成立**；
- 所以原 `park` verdict 必须保留。

## 2) 它更像 hard park 还是 soft park？
**更像 `soft park`。**

原因：
- 作为 standalone `price-volume divergence breakout filter`，这条线已经被审计消费；
- 但它的问题更像 **角色放错层级**：
  - 原 Rank 20 其实在问“背离 warning 能不能直接把 breakout family 救活”；
  - 新旁证更像在说，真正可能有用的不是那种二元 `warning`，而是更宽一点、但也更诚实的 **price × volume interaction admission layer**。

换句话说：
- 原 Rank 20 版本该停；
- 但“量价交互先决定 setup 要不要放行”这个主题，还没被同一条审计完全消费掉。

## 3) 有没有“可救信号”？
**有。**

可救信号不在继续调 `break_window / delta / warn_count` 这些原 Rank 20 邻域，而在最近旁证给出的 **角色降级 + 表达升级**：

1. 原 Rank 20 已经证明：
   - `divergence warning` 这种负向过滤写法太窄；
   - 它既没明显砍掉假突破，也没把 baseline 拉回可交易区间。
2. 2026-03-19 的 `volume-price interaction` digest 给出的新旁支更集中：
   - 别把量、价各自单阈值化；
   - 更值得先测的是 `price thrust × volume participation × wick/body absorption` 这种交互 admission。
3. 同日的 `impulse-volume anchor + small-body retest` digest 又补了一个很关键的边界：
   - 量价信息未必要当“直接收益增强器”；
   - 它更像在回答 **这次回踩 / 延续的质量够不够诚实**。

更直白地说：
- Rank 20 最值得留下的，不是“背离 warning 本身能拯救 breakout”；
- 而是“volume-price interaction 也许该先做 shared admission / hold-quality layer，而不是主策略过滤器”。

## 4) 最值得改的唯一一刀是什么？
**唯一最值得改的一刀：把 Rank 20 从 standalone `price-volume divergence breakout filter`，降级成 `volume-price interaction` shared admission layer。**

也就是：
- 不再根据“是否出现 divergence warning”直接决定一整套 breakout family；
- 只把量价交互分数，当作现有 `breakout-short / Fib retest_hold / EMA-PSAR continuation` 的 shared allow/deny/sizing gate；
- 第一轮优先测 interaction admission，而不是顺手偷带新 exit / regime / microstructure 叠层。

为什么这算一刀而不是多轴大改：
- 核心主题没变，仍是 `price-volume relationship`；
- 数据仍是已有公开 OHLCV / volume；
- 只改了它的 **表达角色**：从“背离过滤器本身就是主判断”改成“量价交互只负责 admission / veto / sizing”。

## 5) 是否值得形成新的 derived hypothesis？
**值得。结论：`derived_hypothesis_drafted`。**

理由：
- 原 `park` 结论完整保留，尤其“Rank 20 这版 divergence warning 过滤器并没有成立”这一点不翻案；
- 原始失败集中在写法过窄、角色过重，而不是彻底否定量价交互主题；
- 新 digest 提供了一个只改角色、不改主题的窄 reframe：**不再让 divergence warning 直接开/关策略，而是把更宽、更可解释的 volume-price interaction 降级成 shared admission layer。**

## 6) trade on / trade off 结论
### Proposed derived hypothesis
- `proposed_rank`: `Rank 20b`
- `source_rank`: `Rank 20`
- `single modification axis`: `demote standalone price-volume divergence breakout filter into a volume-price interaction shared admission layer`
- `trade on`: `不再根据“breakout 时是否出现 divergence warning”直接判整条策略；而是在固定 15m setup 上，用 volume-price interaction score（第一轮优先可解释线性版：price thrust × relative-volume participation - wick/body absorption penalty）只做 shared allow/deny/sizing gate：interaction 强时优先放行 breakout-short follow-up 与 EMA/PSAR continuation，对 Fib retest_hold 则只先做 admission / half-size，不偷带新 trigger。第一轮只测 baseline vs single-volume threshold vs interaction-admission vs interaction-sizing。`
- `trade off`: `放弃“price-volume divergence warning 本身就是 standalone breakout filter”的原 Rank 20 读法，换取更诚实的量价交互 admission 角色；代价是它不再是独立策略，而且若 interaction 阈值过紧，可能只是靠砍单美化结果，因此第一轮必须只测 interaction 层本身，不偷带新 exit / second-layer regime / order-flow stack。`
- `why now`: `原 Rank 20 clean replication 已很清楚地证明：把 divergence warning 直接写成 breakout filter family 后，跨资产、跨时间、跨参数、跨成本一起不成立；但 2026-03-19 新增的 volume-price interaction digest 与 impulse-volume retest digest 又共同说明，量价信息更可能存活在 shared admission / hold-quality 层，而不是原 Rank 20 那种二元 warning 过滤器里。`
- `suggested_initial_state`: `source intake / clean replication next`

## Final verdict for this round
- `verdict`: `derived_hypothesis_drafted`
- `original_rank_verdict_kept`: `park`
- `park_type_read`: `soft park`

## Minimal audit note
This round does **not** reopen Rank 20 itself.
It keeps the original `park` intact. The only new move is a narrower role downgrade: **`Rank 20b = stop treating price-volume divergence warning as the strategy filter itself, and test volume-price interaction only as a shared admission layer for existing lanes.`**

## Git
- 本轮只做最小必要文档改动；未做 commit。
- 原因：工作区存在大量无关脏文件与未跟踪文件，当前不适合安全地 selective commit。
