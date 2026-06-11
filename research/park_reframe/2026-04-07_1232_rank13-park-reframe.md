# 2026-04-07 12:32 UTC — Rank 13 park reframe review

- source rank: `Rank 13 / partial-moment asymmetry TSMOM gate`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## 1) 原 Rank 为什么会 park
原 Rank 13 被 park，核心不是“上行/下行波动不对称”这个主题完全没信息，而是它被写成 **standalone sign-momentum + partial-moment guard** 后，结果已经被审计得很硬：

- `2026-03-17_0038_rank13-asymmetry-tsmom-park.md` 的 clean replication 显示，primary `pm_guard_100 @ 6bps/side` 只有“少亏一点”，没有转成像样 alpha：
  - `mean_total_return ≈ -71.90%`
  - `positive_asset_ratio = 0/3`
  - `mean_max_drawdown ≈ -75.70%`
- 时间、参数、跨标的、成本四类稳定性一起 fail，不是某一个小参数没调对。

所以原 Rank 13 被否掉的，是“把 partial-moment asymmetry 当成独立 15m crypto sign-momentum rescue line”这层写法；这个审计结论本轮不动。

## 2) 它更像 hard park 还是 soft park
本轮仍判作 **soft park，但已明显偏硬**。

原因：
- soft 的部分在于，主题本身并非彻底无信息；
- 偏硬的部分在于，原 rank 最诚实的 residual 其实早已被 `Rank 13b` 吸收，当前已经很难再从原对象里切出第二条同样诚实的新窄轴。

## 3) 有没有“可救信号”
有，但不是新的。

唯一还能成立的可救信号，仍然只是此前已经写明的那条：
- 把 partial-moment / semivariance 主题降级成 **shared directional veto / sizing overlay**；
- 也就是既有的 `Rank 13b`：`RS+/RS- realized-semivariance directional veto / sizing overlay`。

本轮重看 `docs/RECENT_PAPER_SEEDS.md`、`research/quant_digests/INDEX.md` 与已有 park-reframe 记录后，没有看到新的 decisive evidence 能把 Rank 13 再诚实切出 `Rank 13c`：
- 最近新增的 momentum / tail-risk / cross-sectional 线索，更像新的 raw-alpha family 或更上位的 routing / shell；
- 它们没有提供一条比 `Rank 13b` 更窄、且仍然属于原 Rank 13 宿主的唯一主修改轴。

## 4) 最值得改的唯一一刀是什么
**没有新的唯一一刀。**

更准确地说：
- 原 Rank 13 最值得改的唯一一刀，早就已经在 `Rank 13b` 里定义完了；
- 本轮没有出现足够新的证据，支持再从原对象里切出第二条不重复、不越界的新轴。

因此，这轮最诚实的回答不是继续 draft，而是明确：
**`Rank 13b` 已经消费了原 Rank 13 唯一诚实的单轴 residual。**

## 5) 是否值得形成新的 derived hypothesis
**不值得。**

原因很简单：
1. 原 `park` 审计已经清楚；
2. 唯一自然 residual 已被既有 `Rank 13b` 占用；
3. 近期新证据没有把这条 residual 进一步收窄成新的、独立的唯一主修改轴；
4. 再写 `Rank 13c`，大概率只是把 shared overlay 主题换壳重复排班。

## 6) 本轮结论
- 原 rank 为什么 park：standalone sign-momentum + partial-moment guard 在收益、回撤、时间、参数、跨标的、成本上一起失败；
- 更像 hard 还是 soft：`soft park，但已明显偏硬`；
- 有没有可救信号：`有，但仅剩既有 Rank 13b 那条 shared directional veto / sizing overlay residual`；
- 最值得改的唯一一刀：`无新增；原唯一诚实修改轴已被 Rank 13b 消费`；
- 是否值得形成新的 derived hypothesis：`不值得`；
- 本轮最终结论：`keep_park`。

## 7) 对队列的含义
- 保留 `Rank 13b` 作为既有 queue-only derived hypothesis；
- 本轮不新增 `Rank 13c`；
- 默认不改 `docs/TODO.md` 顶部排班，也不向 bot2 / bot3 分配新任务。

## 8) Git / 提交
- 本轮只做最小文档更新；未做 git commit。
- 原因：按 brief，本轮以低频审计记录为主；若工作区存在无关脏文件，不应混提。