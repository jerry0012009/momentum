# 2026-03-20 09:42 UTC · Rank 23 park reframe review

- source rank: `Rank 23 / volatility regime mid-band / cost-survival gate`
- final verdict: `keep_park`
- original verdict kept: `park / evidence pool`
- park type: `soft park`
- touched scope: `Rank 23` only

## 为什么这轮看 Rank 23
- 按 `bot6` 规则，这轮只处理 1 条已 `park` rank。
- `Rank 23` 当前仍在 `Rank 1~37` 范围内，且最近 `7` 天没有被 `bot6` park-reframe 复盘过。
- 它还有一条看起来最自然的“可救轴”——把 standalone vol/regime 读法降级成 shared vol gate；但这条救法在后续新证据里其实已经被近邻实验基本消费，适合低频复核一次后收口。

## 原 rank 为什么 park
原始 `Rank 23` 的 clean replication 与 Light Stability Pack 已经把核心问题讲得很清楚：
- 主变体 `rv_midband_q20_80` 虽比 `baseline_mtf` 少亏，但在 `BTC/ETH/SOL 120d 15m`、`next-bar open + no-overlap`、`6bps/side` 下仍是**全资产为负**；
- 时间稳定性 `0/3` 正 bucket；
- 参数邻域没有形成可升格 pocket，最佳近邻也仍明显为负；
- 成本一抬升继续恶化，没显示出真正的 `cost survival`。

翻成人话：`只做中间 realized-vol 区间` 这件事，最多算“少亏一点”，不够构成当前 desk 需要的 shared 生存门，所以原 verdict 被如实压回 `park / evidence pool`。

## 它更像 hard park 还是 soft park
我把它归为 **`soft park`**，不是 `hard park`。

原因：
- `vol / cost-survival` 这个主题本身没死，它仍然是合理的风险/环境层问题；
- 原失败更像 **角色错位 + 迁移后没有形成 desk 级统一 uplift**，而不是“realized vol 永远没信息”；
- 但它又不够软到值得现在立刻再派生，因为**最自然的窄救法已经被新证据亲自跑过一遍**。

## 现有证据里有没有“可救信号”
有，但很弱，而且已经被后续实验基本消费：
- `2026-03-18` 的 quant digest 明确给出过最自然的一刀：把它改写成 **`realized-vol mid-band / no-high-vol-extreme` shared allow/deny gate**，而不是 standalone alpha；
- 这个想法随后已经被 queue-facing 新线 **`Rank 72 / realized-vol mid-band cost-survival gate`** 接手做了 source intake 与最小 clean replication；
- `Rank 72` 的结果显示：`EMA` 那条 setup 看似改善，但主要是靠 retention 砍到约 `20%` 左右；`Fib` 没被救活，`breakout_short` 仍为负；整体更像**强裁样本**，不是诚实的 shared 生存门升级。

所以，`可救信号` 不是没有，而是已经被更诚实、更新的一次近邻实验消耗过了，而且结果不足以支持再起一条 `Rank 23b`。

## 最值得改的唯一一刀是什么
如果只从主题上讲，最自然的唯一一刀仍然是：
- **把 standalone volatility regime gate 降级成 shared realized-vol allow/deny gate。**

但关键点在于：
- 这刀**已经被 Rank 72 实际代打过**；
- 而且代打结果没有形成 desk 级 honest uplift。

因此，对 `bot6` 这轮来说，最值得改的一刀不是“再写一个 23b”，而是：
- **承认这条唯一主修改轴已经被消费，当前不再重复派生。**

## 是否值得形成新的 derived hypothesis
**不值得。**

结论原因：
1. 原 `park` 不是因为“还没想到 gate 角色”，而是因为想到之后也已经被近邻新线实测过；
2. 目前看不到比 `shared realized-vol gate` 更自然、同时又足够窄的单一修改轴；
3. 如果继续硬派生，很容易滑向多轴改写（换 vol 定义、换 regime classifier、换 setup-specific 口径、换 blackout 规则），这不符合 `bot6` 的职责边界；
4. 当前最诚实的审计写法应该是：**保留 Rank 23 的 soft-park 属性，但不新增 23b。**

## 本轮结论（按固定问题回答）
1. **原 rank 为什么 park？**
   - 因为 `rv_midband` 只是 relative-better-but-still-negative：跨资产、时间、参数、成本四个角度都不够诚实。
2. **更像 hard park 还是 soft park？**
   - `soft park`。
3. **有没有可救信号？**
   - 有，主要是“降级成 shared realized-vol gate”；但这条信号已被 `Rank 72` 近邻实验基本消费。
4. **最值得改的唯一一刀是什么？**
   - 把 standalone vol/regime gate 改成 shared realized-vol allow/deny gate；但这刀已被验证过且未通过。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得。

## 对 queue 的最小写回口径
- 保留 `Rank 23 = park / evidence pool` 的审计意义；
- 本轮只补一条 recently reviewed 记录；
- 不新增 `Rank 23b`，也不改 `TODO` 顶部排班。

## 相关证据锚点
- `research/optimization_loop/2026-03-17_0503_rank23-clean-replication-park.md`
- `research/quant_digests/2026-03-18_2136_realized-vol-midband-cost-survival-gate.md`
- `research/optimization_loop/2026-03-19_0013_rank72-source-intake.md`
- `research/optimization_loop/2026-03-19_0032_rank72-midband-clean-replication.md`

## Git / 提交
- 本轮只做最小必要文件改动。
- 未做 commit；原因是当前工作区长期存在较多无关脏文件，本轮按要求避免混提。