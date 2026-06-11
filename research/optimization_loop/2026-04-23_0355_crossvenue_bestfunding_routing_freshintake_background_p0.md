# cross-exchange best-funding routing × sign-constrained delta-neutral carry × hysteresis hold — fresh intake first verdict

- 时间：2026-04-23 03:55 UTC
- 轮次：bot3 13m auto execution
- 对象：`research/quant_digests/2026-04-23_0315_crossvenue-bestfunding-routing-shell.md`
- 动作：fresh intake first verdict
- 结论：`background/P0`

## 本轮只补的最小 decisive blocker
判断这条线在 **routing 后的净 carry** 里，是否真的留下了一个相对现有 live carry 家族可独立排队的、非单 venue / 非单币 lucky-run 的 after-cost pocket；还是只是把已知 funding carry 壳用“best venue routing + hysteresis hold”重新包装。

## 本轮核对到的关键信息
1. repo `strategy_cross.py` 的核心仍是标准 funding carry：
   - `best_fr = max(FR across exchanges)`；
   - `best_fr > 0` 时 `short perp + long spot`；
   - `best_fr < 0` 时反向；
   - 费用模型只按两腿 taker fee 扣减。
2. notebook 明确给出 headline：
   - cross-exchange net CAGR 约 `+5.76%`；
   - gross CAGR 约 `+9.5%`；
   - Binance-only 在 2023+ 约 `-10.0%`；
   - 贡献几乎全部集中在 `Binance ~45% / Hyperliquid ~55%`，`Gate/OKX/Bybit/Deribit` 基本不贡献 position-period。
3. notebook 自己也承认复杂度收益主要来自 **Hyperliquid 引入后的 funding uplift**，不是广谱多 venue 稳定分散出来的新 carry family。
4. repo 成本口径仍是研究级近似：
   - 只粗扣 `perp taker + spot taker`；
   - 没把 live routing 必需的 venue-switch / collateral fragmentation / inventory transfer / spot short borrow / 1h(HL) vs 8h(other venues) 结算错位，再压成独立 blocker 后复算。
5. 因为实盘贡献收敛到 `Binance + Hyperliquid`，这条线更像 **现有 cross-venue net-carry shell 的 routing / hold 设计提示**，而不是新的独立 raw alpha 主语。

## 为什么本轮直接收口 background/P0
- 这条线的 alpha 主体仍是 funding carry，本质上没有脱离 desk 已经 live 的 carry / cross-venue net-carry 家族。
- 所谓“cross-exchange” 的新增价值并没有展开成多个 venue、多个币、多个独立 pocket；公开结果基本退化为 `Binance + Hyperliquid` routing 优化。
- 在尚未把 routing 切换成本、venue 资本占用、结算时钟错配与库存现实压进同一 after-cost 口径前，不能诚实把它当成相对已 live `Rank 389 / cross-venue net-carry ranking alpha` 的新 front object。
- 因此，这份 intake 当前更适合作为 **carry family 的 shared routing / hysteresis / sticky-hold design hint**，而不是值得保留 survivor 的独立候选。

## 会改变系统认知的一句话结果
`cross-exchange best-funding routing × sign-constrained delta-neutral carry × hysteresis hold` 已完成 fresh intake first verdict：公开“跨所”收益几乎收敛为 Binance+Hyperliquid 的 routing uplift，且未证明在 venue-switch / inventory / settlement-clock realism 后仍构成相对已 live carry 家族的独立新增 after-cost alpha，因此本轮直接收口 `background/P0`，前排切到下一条 fresh intake `walk-forward cointegrated basket spread fade × regime veto × risk-parity sizing`。
