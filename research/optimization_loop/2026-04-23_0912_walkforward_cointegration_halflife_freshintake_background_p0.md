# bot3 optimization loop — walk-forward cointegration admission × half-life-bounded spread fade first verdict

- Time: 2026-04-23 09:12 UTC
- Cycle item: 1
- Target: `research/quant_digests/2026-04-23_0757_walkforward-cointegration-halflife-pairs-alpha.md`
- Verdict: `background/P0`

## What I checked
只执行当前最前的 pending 小点：对 `walk-forward cointegration admission × half-life-bounded spread fade` 做 fresh intake first verdict，只回答它是否相对已 live 的 pairs family（尤其 `Rank 424 / cointegration-first pair admission × strongest residual z-score spread fade` 与 `Rank 431 / cointegration maker-first + hard time-stop pairs`）留下独立、非单窗的 after-cost alpha，而不是再次把 pair-admission / timeout / execution shell 重新命名。

读取了：
- `jerry/momentum/research/quant_digests/2026-04-23_0757_walkforward-cointegration-halflife-pairs-alpha.md`
- `jerry/momentum/reports/artifacts/literature/walkforward_pairs_portability_probe_2026-04-23.csv`
- 已有 family 收口记录：
  - `jerry/momentum/research/optimization_loop/2026-04-21_2322_dynamic_cointegration_halflife_freshintake_background_p0.md`
  - `jerry/momentum/research/optimization_loop/2026-04-23_0035_rollols_pairfade_freshintake_background_p0.md`

## Key evidence
### 1) 这次 portability probe 的正 pocket 仍高度集中，不是新的广谱 pair family
CSV 里成本后为正的主要只有：
- `15m BNBUSDT/DOGEUSDT`: `14` 笔，`avg_net ≈ +46.37bps/笔`，`cum_net ≈ +6.49%`
- `15m SOLUSDT/DOGEUSDT`: `18` 笔，`avg_net ≈ +13.08bps/笔`，`cum_net ≈ +2.35%`
- `5m ADAUSDT/LINKUSDT`: `11` 笔，`avg_net ≈ +11.72bps/笔`
- `5m DOGEUSDT/LINKUSDT`: `12` 笔，`avg_net ≈ +10.02bps/笔`
- `5m ADAUSDT/DOGEUSDT`: `8` 笔，`avg_net ≈ +9.55bps/笔`

但同一批结果里其余 pair 已经转负，例如：
- `15m XRPUSDT/DOGEUSDT`: `avg_net ≈ -4.89bps/笔`
- `15m DOGEUSDT/LINKUSDT`: `avg_net ≈ -7.54bps/笔`
- `15m SOLUSDT/XRPUSDT`: `avg_net ≈ -7.78bps/笔`
- `15m SOLUSDT/BNBUSDT`: `avg_net ≈ -26.46bps/笔`
- `5m SOLUSDT/DOGEUSDT`: `avg_net ≈ -4.63bps/笔`
- `5m SOLUSDT/ADAUSDT`: `avg_net ≈ -6.03bps/笔`

这说明它留下的是少数 `DOGE/ADA/LINK` 偏 alt-heavy pocket，而不是能与已 live pairs queue 并列的新广谱宿主。

### 2) 新增语义仍主要是 admission / half-life / walk-forward 研究提示，不是独立 alpha 主语
目标 digest 想保留的核心是：
- `cointegration-first` 选 pair
- `walk-forward` 重选 pair
- `half-life/time-stop` 优先于机械 hard stop

但这些语义并不新：
- `Rank 424` 已经覆盖了 `cointegration-first pair admission × strongest residual spread fade` 的核心主语；
- `Rank 431` 已经把这条 family 往 execution realism 收口到 `maker-first + hard time-stop / rolling pair admission`；
- `2026-04-21_2322_dynamic_cointegration_halflife_freshintake_background_p0.md` 也已诚实处理过几乎同类的 `dynamic cointegration + half-life timeout`，结论就是它更像 pairs family 的 admission/timeout 设计提示，而不是值得前排保留的新对象。

这次 walk-forward probe 虽然比前次更好看，但并没有证明：
1. 留下不同于 `Rank 424 / 431` 的 durable pair set；
2. 把 half-life / walk-forward 从“研究卫生”抬升成独立 queue-facing alpha；
3. 在非单一 DOGE-linked / alt-heavy pocket 之外，形成新的可迁移 after-cost family。

### 3) `keep_P1` 所需的 distinctness 门槛没有过
如果要给 `keep_P1`，至少要看到：
- 至少一个非单 pair、非单月 lucky-run 之外的独立 after-cost pocket；
- 或相对已 live `Rank 424 / 431` 拿出明显不同的一组 durable 宿主；
- 或证明 walk-forward + half-life 本身能稳定创造新边际，而不只是把旧 pair-MR family 的 admission 讲法换皮。

当前没有做到。现有最强证据仍是少数 pair/pocket 漂亮，但整个主语仍落在已 live family 已覆盖的 `cointegration admission / timeout discipline / strongest-only router` 范围内。

## Result
`walk-forward cointegration admission × half-life-bounded spread fade` 的 fresh intake first verdict 已诚实收口 `background/P0`：本轮 portability probe 虽在 `BNB/DOGE`、`SOL/DOGE` 与若干 `ADA/LINK/DOGE` 组合上留下费后正 pocket，但这些结果仍高度集中于少数 alt-heavy pair，没有证明超出已 live `Rank 424 / Rank 431` pairs family 的独立、可迁移 after-cost alpha；新增价值主要退化为 `walk-forward pair admission + half-life/time-stop discipline + strongest-only routing` 的 family 设计提示，因此不进入 survivor。
