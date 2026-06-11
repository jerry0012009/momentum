# Rank 335 — dual momentum breakout expansion first verdict keep_P1

- 时间：2026-04-04 22:45 UTC
- 对象：`research/quant_digests/2026-04-04_1920_dual-momentum-breakout-expansion-alpha.md`
- 轮次角色：bot3 auto execution
- 对应 cycle_plan：第 2 项（fresh intake first verdict）
- 最终结论：`keep_P1`
- 正式 Rank：`335`

## 为什么这一步成立
这条对象已经能被清楚拆成一条独立的 raw alpha 主语：

> `20-bar breakout + 20/60-bar dual momentum + ATR expansion + bull-regime gate`

关键不是“组合层把一堆弱信号包起来”，而是 entry 本体已经在讲一件完整的事：
- `breakout` 负责确认脱离前高；
- `20/60-bar momentum` 负责确认不是随机刺穿，而是趋势在加速；
- `ATR expansion` 负责确认不是低波动假突破；
- `bull regime` 负责把它限制在顺趋势环境里。

因此它不是纯 wrapper，也不是只靠 portfolio ranking 才能定义出来的壳子。

## 对 cycle_plan 关心的三件事的判定
### 1) breakout + acceleration + expansion 主体是否成立
成立。对象主语足够具体，且 entry / exit / risk / cost shell 都已在 repo 里给出，不是半成品想法。

### 2) `1h regime -> 15m execution` 迁移面是否成立
成立。digest 已给出最小 portability probe，并明确显示：
- 这条线在 `1h` 上比裸 `15m` 更自然；
- 更适合作为 `1h` 上层 trend/regime sleeve，再落到 `15m` 做触发/执行；
- 因此 desk 版迁移路径是清楚的，不需要额外猜策略主语。

### 3) `portfolio ranking / correlation gate` 是否只是外层 wrapper
本轮判定：**更像放大器，不是定义性前提**。

理由：
- isolated sleeve probe 已经能展示出局部可用性（例如 `1h ETH`、`15m BTC`），说明不是完全离开组合壳就失真；
- 但跨币铺开后结果明显分化，说明它不是 broad-universe 裸跑 alpha，而是需要 universe discipline 的 trend sleeve；
- 所以 ranking / correlation gate 更像“决定该把信号给谁、别让相关性一起拖垮”的组合放大层，而不是 signal existence 的唯一来源。

## 这一步改变了什么系统认知
`Rank 335` 不应被归类为“必须依赖乐观组合包装才看起来成立的 breakout 伪 alpha”；更准确的定位是：

> 一个 **majors-first / ranking-aware** 的趋势组件候选，适合进入 survivor 阶段做唯一一次便宜 follow-up，去验证它在 `BTC/ETH` 或 top-N 选择下，是否能把 raw alpha 本体进一步收口到 `P2`。

## runtime 回写
- `Fresh intake slot` 更新为：`Rank 335 / dual momentum breakout expansion`
- `Fresh intake latest_result` 更新为：first verdict = `keep_P1`
- `Surviving candidate slot` 更新为：`Rank 335 / dual momentum breakout expansion`
- `followup_budget_remaining` 更新为：`1`
- `cycle_plan[2]` 更新为：`done`

## 下一步（留给后续轮次，不在本轮执行）
如果后续要用 survivor 唯一 follow-up，最便宜且最有决策力的方向应优先是：
- 固定 `1h regime -> 15m execution` 架构；
- 限定 `BTC/ETH` 或 top-N ranking；
- 直接判断这条 majors-first / ranking-aware trend sleeve 是否足以进入 `P2`，还是只能说明“需要 portfolio 包装才不难看”。
