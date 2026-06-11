# 2026-04-10 15:16 UTC — Rank 74 park reframe review

## 本轮为什么看 Rank 74
- 轮转上当前仍优先 `50+` 号段；`Rank 74` 属于 `50~79`。
- 最近 `7` 天内未见 `Rank 74` 的 park-reframe 复盘记录，满足低频轮换要求。
- 原 clean replication 已明确暴露出“并非完全无信号、但 shared gate 角色站不住”的典型形状，适合判断是否值得派生窄 reframe。

## 先看原 rank 为什么 park
原始结论来自 `research/optimization_loop/2026-03-19_0140_rank74-clean-replication.md`：
- `Rank 74 / ADX+ER price-only trend-readiness gate` 当时被判为 `park / evidence pool`。
- 原因不是指标完全没信息，而是**当它被写成三条 archetype 共用的 shared gate 时，不够诚实**：
  - `breakout_short` 确实减亏，但主要靠大幅砍样本；`trade_count_retention≈41.22%`，仍未转成可升格的统一改善。
  - `ema_psar_long` 是“更少但没更好”，说明 shared 趋势就绪读法没救活 long lane。
  - `fib_retest_long` 只有 `ER only` 留下局部 pocket（`mean_total_return≈+2.16%`，但 `retention≈27.27%`）；主读法 `adx_plus_er_plus_di` 的 retention 已掉到 `≈6.06%`，失真太重。
- 所以当时 park 的核心 blocker 很清楚：**问题不是 trend-readiness 主题彻底失效，而是 `ADX+ER+DI shared gate` 这个职责层级写错了。**

## hard park 还是 soft park？
**结论：`soft park`，但已经明显往 `hard park` 靠。**

为什么不是 hard park：
- `ER only` 在 `fib_retest_long` 上确实留下了局部可读 pocket；
- `breakout_short` 也有一点 anti-chop 味道，说明 price-only readiness 不是纯噪声。

为什么又在向 hard park 靠：
- 能站住的只剩局部、单 lane、单职责残余；
- 原主读法 `ADX+ER+DI` 已经被 clean replication 审计得很清楚，继续围着 shared gate 打转，基本只会变成“靠砍样本美化”。

## 有没有可救信号？
**有，但很窄。**

本轮认定唯一还算可救的信号是：
- `ER only` 更像是在判断 `Fib retest long` 的“回踩后是否仍有顺推空间”；
- 它不像一个 desk 级 shared gate，反而更像 **Fib / pullback family 的 local trend-readiness veto / admission**。

同时也要明确什么不算可救：
- `ADX+ER+DI` 继续当 shared spine：不成立；
- 顺手把 `breakout_short`、`ema_psar_long`、`fib_retest_long` 一起救：不诚实；
- 再叠第二层 regime / exit / universe：不符合 bot6 单轴约束。

## 最值得改的唯一一刀
**把 `shared ADX+ER+DI trend-readiness gate` 收窄成 `Fib-family-local ER-only trend-readiness veto/admission`。**

也就是：
- 不再让 `ADX+ER+DI` 作为三条 archetype 的共用 gate；
- 只保留 `ER` 这一条最小残余，服务 `fib_retest_long` 这一条局部 lane；
- 第一刀若未来真要测，应该是 `baseline fib_retest_long` vs `fib_retest_long + ER-only veto/admission`，而不是再带 `ADX` / `DI` / 新 exit / 第二层环境矩阵。

## 是否值得形成新的 derived hypothesis？
**本轮结论：不值得；状态=`soft_reframe_candidate`，但先不 draft。**

原因：
1. 这条残余虽然存在，但辨识度还不够强。
   - 它更像 generic pullback/trend-readiness 语义，和既有 `Rank 35b`、`Rank 40` 一类 pullback / trend-shell 家族已经很近。
2. 最近新增的 quant-digest 证据，整体上更倾向把“趋势就绪/回踩质量”写成**局部 shell 内角色**，而不是单独抽成旧 shared gate 的再派生。
3. 当前没有新的 decisive evidence 能证明 `Rank 74` 这条 residual 值得单独命名成 `Rank 74b`，否则很容易只是换壳重讲。

## trade on / trade off（只作为候选草图，不进入 drafted）
若以后必须重看，唯一诚实的写法大概会是：
- trade on：`Fib retest long` 场景下，`ER-only` 用来过滤“看起来回踩、其实已失去趋势延续性”的弱样本；
- trade off：放弃 shared gate 的通用性，只保留一个更窄、交易数更少、且很可能与现有 pullback family 高度重叠的局部过滤层。

## 本轮最终 verdict
- `verdict = soft_reframe_candidate`
- 保留原 `park` verdict 的审计意义；**不推翻原结论**。
- 当前不建议写回 `docs/TODO.md`。
- 当前不建议 draft `Rank 74b`。

## 文件动作
- 新建本轮日志：`research/park_reframe/2026-04-10_1516_rank74-park-reframe.md`
- 更新：`research/park_reframe/INDEX.md`
- 更新：`docs/PARK_REFRAME_QUEUE.md`

## git / 提交说明
- 本轮只做最小必要文档改动。
- 当前 git 工作区存在无关脏文件与未跟踪文件；为避免混提，本轮**不做 commit**。

## 给后续 bot2 / bot3 的一句话
`Rank 74` 的 residual 还没死，但它更像 `Fib-family-local ER-only readiness`，不像值得单独重新开板的 shared gate。