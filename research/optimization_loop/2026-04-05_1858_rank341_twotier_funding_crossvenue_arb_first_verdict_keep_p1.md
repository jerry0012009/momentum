# Rank 341 / two-tier funding-rate cross-venue arb — fresh intake first verdict = keep_P1

- Time: 2026-04-05 18:58 UTC
- Source: `research/quant_digests/2026-04-05_1606_twotier-funding-rate-crossvenue-arb-alpha.md`
- Verdict: `keep_P1`
- Layer change: `fresh intake -> Surviving candidate slot`

## Why this is not just old funding carry wording

这条对象和现有 funding 家族**有重叠，但不是同一句话重复写**。

它和旧对象的区别在于：

1. **不是单 venue spot-perp carry**
   - 不同于 `2026-03-27_1050_okx-positive-funding-positive-premium-carry.md` 那条 `spot-perp + premium alignment` 读法；
   - 本对象是 **同 underlier、跨 perp venue 的 funding differential**，alpha 兑现路径是 `venue A 收 / venue B 付得更少` 的 cross-venue carry，而不是 spot/perp basis 收敛。

2. **不是只讲异步 funding clock 的执行细节**
   - 不同于 `2026-03-31_1302_async-funding-clock-carry-alpha.md` 那条 `HL 1h × Bybit 8h` 的 clock-normalized carry；
   - 本对象新增的主语是 **two-tier market structure**：`CEX lead -> DEX lag`，也就是 venue hierarchy / leader-lagger 结构，而不只是“不同 funding 结算时钟要归一化”。

3. **论文把最小执行壳讲清了**
   - state definition：统一成 `8h equivalent funding bps`；
   - venue pairing：明确指出显著机会主要在 `CEX-DEX`；
   - holding clock：关键不是 headline spread，而是 `spread × duration` 能否撑过成本；
   - exit realism：`spread < 0` forced exit + reversal risk + round-trip cost 都已经写进 source。

## First-verdict judgment

当前证据足以支持它进入 `P1`，原因不是“paper 说 APY 很高”，而是它已经具备一个**最小但诚实的可执行壳**：

- 明确的 mispricing state：同 symbol 跨 venue 的 normalized funding spread；
- 明确的 venue hierarchy：优先 `CEX-DEX`，不是胡乱配对；
- 明确的持有逻辑：必须把持续时间当作 admission gate，而不是只看瞬时 spread；
- 明确的 fee realism：source 已经正面承认多数机会会被 `round-trip cost + reversal risk` 吃掉；
- 明确的最小 clean-room 方向：`spread threshold × persistence gate × CEX-lead gate`。

因此它**不是**“抽象概念套利叙事”；它已经留下 desk 可落地的第一轮验证路径。

## Why not promote P2 immediately

还不该直接进 `P2`，因为当前 source 虽然把策略壳讲清了，但还没有回答下面这些 admission 级问题：

1. `CEX-DEX` 的 alpha 是否在 majors 上也成立，还是主要依赖尾部 illiquid names；
2. `spread × duration` 在 realistic fee / slippage / transfer friction 下到底从多少 bps 开始才过 break-even；
3. `CEX lead` 是否真的能提高净胜率，而不是只是解释市场结构；
4. 不同 holding clock（12h/24h）下，reversal-before-breakeven 比例是否过高。

这些问题更像 survivor 那唯一一次 follow-up 要回答的内容，而不是 first verdict 直接越级替它回答。

## Next honest survivor question

若下一轮给它 survivor 唯一一次 follow-up，最值得补的不是再泛泛复述 funding paper，而是：

> 把 `CEX-DEX spread arb` 压成 `BTC/ETH/SOL/BNB/XRP × 20/30/40bps × persistence / sign-flip / CEX-lead` 的最小 admission clean-room，直接回答它在 majors 与 realistic cost 下到底还能不能留下独立 alpha 壳。

## Result sentence for runtime

`Rank 341 / two-tier funding-rate cross-venue arb` 已完成 fresh intake first verdict：对象不是旧 funding carry 的换壳复述，而是把 `CEX lead -> DEX lag` 的两层 market structure、`spread × duration` admission 与 `CEX-DEX` pairing 压成了 distinct 的 cross-venue carry 壳，因此先 `keep_P1` 并进入 survivor 槽位。