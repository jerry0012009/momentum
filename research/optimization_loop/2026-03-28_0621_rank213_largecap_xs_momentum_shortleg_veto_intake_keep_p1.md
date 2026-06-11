# Rank 213 / large-cap XS momentum × short-leg jump veto intake keep P1

- Time: 2026-03-28 06:21 UTC
- Target: `research/quant_digests/2026-03-28_0447_largecap-xs-momentum-shortleg-veto-alpha.md`
- Action: fresh intake first verdict
- Verdict: `keep_P1`
- Rank: `213`

## What changed
这条对象留下来的不是“再讲一次 generic risk-managed momentum”，而是一个更具体的 crypto 实施命题：**large-cap XS momentum 的 first failure mode 可能不是 alpha 本体全坏，而是 short leg 被少数 single-name jump / squeeze 集中打穿；因此真正值得 desk 化保留的是 `XS momentum raw alpha + short-leg concentration control` 这条骨架。**

## Why it is not P2 yet
1. digest 自带的最小 transfer proxy 已经给出一个很硬的负面事实：在 `12` 个 liquid majors、`24h formation -> 2h hold`、Binance perp `15m` 口径下，plain WML gross 约 `-5.64 bps/rebalance`，加 `short-leg jump veto` 后也只是到 `-5.41 bps/rebalance`，按 `4 bps` 成本近似后仍约 `-7.46 bps/rebalance`，说明当前这个最易落地的 majors pocket 本体并不活。
2. veto 实际只在约 `1.27%` 的换仓触发，说明这组样本里真正主导亏损的并不是 paper 指向的 short-leg jump concentration；因此不能把“略微减亏”包装成 admission-ready 证据。
3. 论文的关键风险源来自更宽的 `top-30` 周频 universe，而不是当前极蓝筹的 `12` 个 majors / 近 7 周短样本；现有证据还不足以证明这条 desk 对象已经跨过 effectiveness / stability / realism 的 `P2` 门槛。

## Why it still deserves keep_P1
1. 主题本体清楚且独立：这不是单纯的 vol-scaling 论文复读，而是一条**可明确拆成 raw alpha 与组合防爆层**的 cross-sectional momentum 线索。
2. digest 已经把下一步高杠杆问题写得足够具体：把 universe 扩到更接近论文 failure mode 的 `25~40` 个可交易 perp，并并排比较 `jump veto / single-name weight cap / strategy-level inverse-vol`，直接观察 left-tail 和 short-leg concentration 诊断项是否真的改善。
3. 这给了它一个唯一且诚实的 survivor follow-up 方向：**不是继续在 majors 15m 上抠小数点，而是验证 short-leg jump concentration 是否只在更宽、更躁的 alt-perp bucket 才是 decisive blocker。**

## Minimal honest next follow-up
若进入 survivor，唯一一次便宜 follow-up 应直接回答：
- 把 universe 放宽到更接近论文风险源的 `25~40` 个 liquid perp 后，plain XS momentum 是否出现可保留的 gross / net pocket；
- `short-leg jump veto`、`single-name weight cap`、`strategy-level inverse-vol` 三者里，是否有任一规则能在成本后真实改善 left tail，而不只是名义减亏；
- 若 short-leg concentration 诊断项仍不极端，则应直接收口转 background，不再把这篇 paper 的周频 crash story 硬套到短周期 desk 对象上。

## Runtime implication
- 正式分配 `Rank 213`。
- 层级定性为 `P1`，**不直接升 `P2`**。
- 由于当前 `Surviving candidate slot` 为空，这条对象应占据 survivor 槽位，并保留 **1 次** 最小 decisive follow-up 预算。

## Result sentence
`Rank 213 / large-cap XS momentum × short-leg jump veto` fresh intake 完成并保留为 `keep_P1`：当前 `12` 个 liquid majors 的 `15m` proxy 显示 plain WML 与 jump-veto 版都明显为负、veto 触发也极少，因此它还不能升 `P2`；但“short-leg single-name jump concentration 是否只在更宽 alt-perp universe 才是真实 blocker”仍是一个清晰且值得保留一次 survivor 检查的 desk 问题。
