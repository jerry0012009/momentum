# bot3 optimization loop — multivenue pairs correlation-cap allocator first verdict

- Time: 2026-04-25 10:54 UTC
- Target: `research/quant_digests/2026-04-24_0402_multivenue-pairs-correlationcap-shell.md`
- Cycle action: fresh intake first verdict
- Scope kept minimal: only answer the decisive blocker named in cycle plan — `sector/correlation-cap allocator` 是否在 short-cycle crypto pairs 上留下独立的 after-cost edge，而不是只是 repo 层 Sharpe 叙事。

## Read set
- `docs/BOT2_BOT3_POLICY.md`
- `docs/BOT2_BOT3_STATE.md`
- digest: `research/quant_digests/2026-04-24_0402_multivenue-pairs-correlationcap-shell.md`
- source README: `https://raw.githubusercontent.com/abailey81/Crypto-Statistical-Arbitrage/main/README.md`
- existing desk context checked via search: current live / recent pairs family already includes `Rank 424` and `Rank 431` in `Paper launch queue -> connected_runner_live`

## What changed system cognition
本轮不再把这条 intake 读成“值得继续进 survivor 的新 alpha”；相反，当前可验证证据只够支持它是 **已有 pairs family 的 allocator hygiene 提示**，不够支持它形成一个相对 `Rank 424 / Rank 431` 具有独立可迁移性的新增前排对象。

## Minimal honesty check
cycle_plan 指定的 blocker 是：

> 组合层 concentration/correlation cap 是否真的在 short-cycle crypto pairs 上留下 after-cost edge，而不是只剩 repo 层 Sharpe 叙事。

对这个 blocker，本轮能确认的只有：
1. README 确实声称 phase-2 altcoin stat-arb 在 walk-forward OOS 下有 `Sharpe 1.61 / total return 6.84% / maxDD 4.64% / 127 trades`；
2. README 也明确把 `40% sector concentration limit` 与 `70% max cross-pair correlation` 写成 risk controls；
3. 但公开可直接读到的证据没有给出 **allocator A/B attribution**：
   - 没有 `all admitted pairs all-in` vs `correlation-capped subset` 的独立 OOS 对照；
   - 没有 per-pair / per-sector / capped-vs-uncapped 的 after-cost decomposition；
   - 没有证明正收益不是由少数 alt-heavy pairs 主导，而 correlation cap 只是回撤整理而非新增 edge；
4. 因此，当前材料证明的是“作者把完整 pairs shell 写齐了”，不是“sector/correlation cap 本身构成了可独立交易、可迁移复用的新 pocket”。

## Verdict
- **Verdict: `background/P0`**
- Reason:
  - 这条 intake 的 base alpha 仍是常见的 `cointegration spread fade`；
  - 本轮唯一要求核实的新东西是 allocator 层 `concentration/correlation cap`；
  - 但现有证据没有证明 allocator 带来了足以独立立项的 after-cost edge，只证明了一个结构完整的 repo risk shell；
  - desk 现有 live / connected pairs family (`Rank 424`, `Rank 431`) 已覆盖更接近可交易 admission × spread-fade 路径；本 repo 没有拿出足够强的新证据说明它超出了“可吸收的风控提示”。

## Runtime write-back intent
- fresh intake 当前对象收口为 `background/P0`
- cycle_plan 第 1 项标记 `done`
- fresh intake 前槽前移到下一条已存在的 pending intake：`research/quant_digests/2026-04-25_1037_oppositesign-funding-slippageveto-shell.md`

## One-line result for state
`cointegration spread fade × sector/correlation-cap allocator` first verdict 已诚实收口 `background/P0`：当前公开证据只证明它是 pairs repo 的 allocator/risk shell，而没有拿出 capped-vs-uncapped 的 after-cost OOS attribution 来证明独立于已 live `Rank 424 / 431` pairs family 的新增可迁移 alpha。
