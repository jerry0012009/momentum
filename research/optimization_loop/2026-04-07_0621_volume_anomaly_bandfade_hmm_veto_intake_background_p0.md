# 2026-04-07 06:21 UTC — fresh intake first verdict — volume anomaly band-fade HMM veto → background / P0

## Target
- `research/quant_digests/2026-04-06_1020_volume-anomaly-bandfade-hmm-veto-alpha.md`

## What was checked
- 是否存在独立于常见 `Bollinger / oversold mean-reversion` 家族的新 raw alpha 主语；
- `broad volume anomaly` 是否是足以单独提升对象层级的新增 admission 轴，而不是对老反转壳的确认滤镜；
- `HMM veto` 是否构成新 alpha，还是仅是 crash-regime risk-off overlay。

## Decision
- 结论：`background / P0`。

## Why
1. repo 的核心交易骨架仍是非常传统的 `band stretch -> revert to mid-band` 单资产 BTC 反转壳；`2.5σ` 只是把入场做深，不足以把它升级成独立于旧 Bollinger/oversold family 的新主语。
2. `volume anomaly` 在源码与参数网格里更像“确认是否有异常参与度”的 admission filter；它能帮助减少噪声，但没有证明自己是可独立迁移的 edge generator，仍属于老 mean-reversion 壳上的过滤层。
3. `HMM` 的最诚实定位就是 `crash veto / regime off-switch`。它改善的是坏状态下少亏、少做，而不是提供新的 alpha 本体；把它写成主题主语会高估对象新颖性。
4. digest 内已明确记录 source 口径不一致：README、`multi_year_results.csv` 与其他指标文件之间存在收益数值冲突，因此当前更像“可借拆法”，不是“可直接纳入前排继续做 survivor”的稳健证据。
5. 对 desk 来说，这份材料最有价值的产出是一个共享 admission 提醒：反转类信号要配 `deep stretch + broad participation confirmation + crisis veto`。这属于实现经验，不足以支持该对象以独立候选身份进入 `keep_P1`。

## System-impact sentence
- `2.5σ band stretch × broad volume anomaly fade` 本轮 first verdict 收口为 `background / P0`：对象本质上仍是旧 `Bollinger/oversold mean-reversion` 家族加上 volume confirmation 与 HMM crash veto 的实现壳，没有压出足以单独保留前排的新增 alpha 主语。

## Files to update
- `docs/BOT2_BOT3_STATE.md`
- homepage index refresh required
