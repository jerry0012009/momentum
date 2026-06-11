# 2026-04-21 20:04 UTC — Rank 9 park reframe review

## 为什么本轮选 Rank 9
- 本轮严格限定在 `Rank 1~37` 的已 `park` 条目内。
- `Rank 9` 上次 bot6 park-reframe 是 `2026-04-12 14:01 UTC`，已超过最近 `7` 天窗口。
- 它同时满足两点：
  1. 原 `park` 结论已经很清楚，适合做一次低频复核；
  2. 4 月 21 日又出现了新的 trend/raw-alpha 旁证（如 `triple EMA stack × RSI veto × ATR bracket`、`Tenkan/Kijun cross`），正好可以回答：这些新证据是在继续支持旧 `Rank 9` 的 shared-veto residual，还是进一步说明它的主题应外流到新的完整 trend shell / raw-alpha 宿主。

## 本轮补读
- `docs/TODO.md`
- `docs/PARK_REFRAME_QUEUE.md`
- `docs/RECENT_PAPER_SEEDS.md`
- `research/quant_digests/INDEX.md`
- `research/park_reframe/INDEX.md`
- `research/optimization_loop/2026-03-16_2241_regime-switch-stack-intake.md`
- `research/optimization_loop/2026-03-16_2300_regime-switch-clean-replication-park.md`
- `research/optimization_loop/2026-04-09_0817_rank9b_fresh_intake_background_absorbed.md`
- `research/park_reframe/2026-04-12_1401_rank9-park-reframe.md`
- `research/quant_digests/2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md`
- `research/quant_digests/2026-04-21_1548_ichimoku-tenkankijun-cross-feetrap.md`

## 1) 原 Rank 为什么 park？
原 `Rank 9` 被 park，不是因为 `EMA(RSI)` / regime 主题完全没信息，而是因为它被写成了一条 **standalone regime-switch indicator-stack entry**。

`2026-03-16 23:00 UTC` clean replication 的 authoritative blocker 仍然成立：
- 最不差的 `regime_gate_only` 在 `6bps/side` 下也只是 `mean_total_return≈-10.28%`，相对 baseline 只是少亏；
- `constrained_no_buy` 没有形成更诚实的净边；
- `regime_plus_psar_rsi` 直接退化到 `0 trade`；
- 时间、参数、跨标的、成本/交易数四项稳定性一起 fail。

所以原 rank 真正被审计掉的是：
**“把 regime-switch stack 当成一条独立可承压的交易骨架”** 这层读法。

## 2) 它更像 hard park 还是 soft park？
本轮判断：**仍是 soft park，但比 4 月 12 日那轮更接近 hard park with consumed residual。**

原因：
- 仍算 soft，是因为 `EMA(RSI)` / state-language 本身没有被证伪；
- 但更接近 hard，是因为后续新证据没有把旧 `Rank 9` 重新拉回 queue-facing residual，反而继续说明：这类信息更自然地活在新的 **trend raw-alpha / parent-state shell** 里；
- 且既有 `Rank 9b` 已在 `2026-04-09` fresh intake first verdict 中被明确收口为 `background / P0`，说明旧 rank 唯一自然 residual 已被 family 吸收，而不是仍有待展开的独立对象。

## 3) 现有证据里有没有“可救信号”？
有，但没有新的、仍属于旧 `Rank 9` 的可救信号。

保留下来的 residual 仍只是一条老答案：
- `EMA(RSI)` 更像 **shared asymmetric regime veto / allow-deny layer**；
- long-side continuation / retest 在 `ema_rsi7 > 60` 一类 uptrend 区间里更自然；
- short-side setup 在 `ema_rsi7 < 40` 一类 downtrend 区间里更自然；
- 中性区更像 abstain / veto / half-size，而不是直接当 entry stack。

但 4 月 21 日的新旁证并没有替它长出第二条旧-rank residual：
- `2026-04-21_1358_tripleema-rsi-atr-stack-alpha.md` 更像在说：`EMA stack` 是 **base trend alpha**，`RSI` 只是不过热 veto；
- `2026-04-21_1548_ichimoku-tenkankijun-cross-feetrap.md` 更像在说：快慢中线翻面本身才是 raw alpha，而更慢的确认层只配降级成 filter / parent state。

这两条都在把主题往 **新的完整 trend shell / raw-alpha 宿主** 上推，而不是在支持旧 `Rank 9` 再细分出 `Rank 9c`。

## 4) 最值得改的唯一一刀是什么？
如果仍只允许改一刀，答案不变：

**把 standalone regime-switch stack，降级成 `EMA(RSI)`-based asymmetric shared regime veto。**

也就是既有 `Rank 9b`。

本轮没有看到第二条同样诚实、且仍属于旧 `Rank 9` 的主修改轴：
- 若沿着 4 月 21 日的新证据走，主语已经变成新的 `trend raw alpha`；
- 若继续写 shared veto，本质上又只是把 `Rank 9b` 重写一遍。

## 5) 是否值得形成新的 derived hypothesis？
**不值得。**

本轮最终结论：`keep_park`

原因：
1. 原 `park` verdict 的审计意义完全保留；
2. 旧 Rank 9 唯一诚实 residual 仍只到既有 `Rank 9b`；
3. `Rank 9b` 又已在 `2026-04-09` 被 runtime 收口为 `background / P0 / family absorbed`；
4. 4 月 21 日新 digest 继续说明 `RSI veto / parent-state` 这类信息若还有价值，更像新的 trend-shell / raw-alpha 宿主的一部分，而不是足以再诚实派生旧 `Rank 9` 的 `Rank 9c`。

## 模板化回答（简版）
- 原 rank 为什么 park：因为 standalone regime-switch entry stack 在收益与稳定性上都不成立。
- 更像 hard 还是 soft：`soft park`，但已更接近 `hard park with consumed residual`。
- 有没有可救信号：有，但仍只剩既有 `Rank 9b` 那条 residual，而且已被 runtime 收口为 `background / P0`。
- 最值得改的唯一一刀：仍只是 `standalone stack -> EMA(RSI) asymmetric shared veto`。
- 是否值得形成新的 derived hypothesis：**否**。

## 最终结论
- verdict: **`keep_park`**
- note: 原 `park` 保留；4 月 21 日新增的 triple-EMA / Ichimoku 旁证继续说明 regime / RSI 这类信息更适合做新 trend-shell 的 parent-state / veto 层，而不是支持旧 `Rank 9` 再诚实派生 `Rank 9c`。

## 文件/执行备注
- 本轮只做最小必要写回：本日志、`research/park_reframe/INDEX.md`、`docs/PARK_REFRAME_QUEUE.md`。
- 默认不改 `docs/TODO.md` 顶部排班。
- 工作区存在无关脏文件；本轮不做 selective commit。
