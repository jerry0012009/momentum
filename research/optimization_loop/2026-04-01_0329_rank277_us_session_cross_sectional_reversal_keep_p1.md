# Rank 277 — US session window cross-sectional reversal — keep_P1

- 时间：2026-04-01 03:29 UTC
- 执行轮次：bot3 13m auto loop
- 对象：`research/quant_digests/2026-04-01_0226_us-session-cross-sectional-reversal-alpha.md`
- 新分配 Rank：`277`
- 本轮动作：fresh intake first verdict
- 结论：`keep_P1`

## 为什么这轮不是 P0
这条线已经不是“美股时段会影响 crypto”这种叙事层想法，而是具备可审计 raw alpha skeleton 的完整对象：

1. **session 边界明确**
   - morning window：`09:30–10:00 ET` 信号，随后固定持有窗退出
   - close window：`15:30–16:00 ET` 信号，随后固定持有窗退出
2. **横截面构造明确**
   - 做多最近 `30m` 横截面最差的一组
   - 做空最近 `30m` 横截面最好的一组
   - dollar-neutral / tail-bucket 结构清楚
3. **执行骨架明确**
   - `15m` 排名生成信号
   - `30m~120m` 固定持有
   - universe / liquidity filter / cost ladder 都有明确口径
4. **source 证据不是空口**
   - repo 给出 gross alpha 与 gross SR
   - fee + spread 后 pocket 仍未被打穿
   - 真正杀死净值的是 impact，而不是 signal 本体不存在

因此它已经满足“形成可审计 raw alpha skeleton”的前排门槛，不应直接回 `background/P0`。

## 为什么这轮也不直升 P2
当前最关键的诚实缺口还没补：

- source 主证据来自 **Binance spot 横截面**，不是当前更想迁移的 liquid perp shell；
- repo 的 full-cost 结果明确显示：在原始 spot 中小币横截面容量假设下，impact 足以把净值打穿；
- 目前成立的命题仍然只是：**若迁到更液体 perp universe、降低 legs/participation、改成 maker/mixed execution，可能还能留下 after-cost pocket**。

这还不是 `P2 admission` 该依赖的现实证据，只能算明确且便宜的 survivor follow-up 方向。

## 本轮改变系统认知的一句话
`Rank 277` 不是“美股时段风格切换”的宽泛叙事，而是一条已经具备 session window、cross-sectional loser/winner、固定持有与成本骨架的 intraday reversal raw alpha；但它当前仍缺最小 liquid-perp replication，因此先 `keep_P1`。

## 唯一合法 follow-up（survivor budget = 1）
下一步只能做一次决定性检查，直接回答：

**把这条 US open/close window cross-sectional reversal 迁到 liquid perp shell 后，是否至少有一个 window 能在现实成本下保留可迁移的 after-cost pocket？**

建议最小检查口径：
- universe：liquid perp majors / upper-mid caps
- windows：`09:30–10:00 ET` 与 `15:30–16:00 ET`
- hold：`30m / 45m / 60m / 90m`
- cost：maker / mixed / taker 三档
- 目标：不是继续讲 gross，而是直接决定 `promote_P2` 还是诚实回背景
