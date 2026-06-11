# bot3 optimization loop — Deribit term-skew fresh intake first verdict

- 时间：2026-04-18 05:43 UTC
- 对象：`research/quant_digests/2026-04-17_1936_deribit-termskew-riskreversal-alpha.md`
- 动作：fresh intake first-verdict + 最小 honesty / execution realism 检查
- 结论：`background/P0`

## 本轮只回答一个问题
这条 `near-vs-far risk-reversal term-skew spread` 是否已经值得作为新的 options RV front object 保留？

## 已有正面证据
原 digest 已经给出两点：
1. repo 的交易主语明确，不是泛泛“偏度故事”，而是同标的、相近 log-moneyness、不同 expiry 的四腿 skew term-spread；
2. Deribit live snapshot 里，`24APR26` 对 `29MAY26/26JUN26` 的 RR spread 在某一时刻确实同时出现了 `RR_spread > 0` 与 `RR_spread_price > 0`。

这足以说明：这条线不是纯叙事，机制上存在一个可描述的 options relative-value raw alpha 候选。

## 最小 honesty / execution realism blocker
但本轮按 policy 只允许做最小、最便宜、最能改变结论的一次 blocker 检查。对这条线，唯一合适 blocker 不是继续讲机制，而是问：

> 现有证据是否已经超出“单次盘口快照碰巧为正”，足以支撑 short-cycle desk 节奏下的多腿可成交与 half-life 现实？

答案是否定的，原因很直接：

1. **当前可见正 edge 仍主要来自单次 live snapshot。**
   digest 展示的是某一时刻 `24APR26` vs `29MAY26/26JUN26` 的正 spread；但还没有一张最基本的 event/markout 表去证明这样的正 edge 会在多个时点重复出现，而不是偶发报价扭曲。

2. **没有最小 time-to-half-reversion / markout 序列。**
   digest 自己也把下一步定义成要记录 `1m/3m/5m/15m/30m` markout、`time-to-half-reversion`、fee-adjusted expectancy。这说明决定性证据尚未生成；目前还不能回答这个 edge 在 desk 可接受的持有窗口里是否真的回归。

3. **四腿 execution realism 仍未闭合。**
   repo 虽然有 margin pre-check，但当前没有给出：
   - 四腿同步/分步成交的 legging loss 分布；
   - top-of-book size 是否足够支撑最小成交单位；
   - quote 一跳后正 edge 是否仍保留；
   - 多腿 taker/maker 混合成交后的净边际是否仍为正。
   在 options 多腿场景里，`RR_spread_price > 0` 的单次盘口静态快照，本身不足以证明真实可拿到该边际。

4. **对 short-cycle front slot 来说，证据厚度还不够。**
   这条线若要保留到 `keep_P1`，至少要能把 survivor blocker 收敛成单一 `fillability / half-life` 轴，并已有初步可复算样本。现在连最基础的 repeated markout panel 都没有，因此前排保留会把未验证厚度的 options 多腿快照错当成 queue-facing 对象。

## first verdict
本轮 first verdict 直接收口：

> `near-vs-far risk-reversal term-skew spread` 当前仍主要停留在单次 Deribit live snapshot 正 edge 与 repo 执行雏形，缺少能证明多腿可成交性与 half-life 的重复 markout / legging-loss 证据，因此不诚实保留为新的 front object，直接收口 `background/P0`。

## 为什么不是 keep_P1
不是因为机制一定错，而是因为按当前 runtime 约束，front slot 需要的是**能很快收敛成单一 decisive blocker 的对象**。这条线目前同时缺：
- repeated markout；
- half-life；
- four-leg fillability；
- legging-loss。

它还没有缩到一个已经足够薄、足够便宜、足够决定性的 survivor blocker，因此不应占用前排。

## 回写 runtime 的系统认知变化
- `cycle_plan` item1 完成并写成 `done`
- 当前 fresh intake 不保留为 `keep_P1`
- 对象移入 `Background pool`
- 本轮没有产生新的 survivor / P2 / P3

## 尾部动作执行状态（异步回执）
- 首页刷新（`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`）：进程被系统 `SIGKILL` 终止（非阻断尾部失败，不回滚本轮 verdict/state/log）。
- 中文邮件摘要（`send_text_email.py`）：发送成功（code 0）。
