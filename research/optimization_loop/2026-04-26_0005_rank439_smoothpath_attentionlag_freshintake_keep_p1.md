# Rank 439 / smooth-path attention-lag continuation router — fresh intake keep_P1

- Time: 2026-04-26 00:05 UTC
- Target: `research/quant_digests/2026-04-25_2316_smoothpath-attentionlag-continuation-alpha.md`
- Step type: `fresh intake first verdict`
- Verdict: `keep_P1`
- Assigned rank: `439`

## Why this changes system belief
这条线已经不只是“limited attention 机制故事”。当前 digest 已经把主语收束成一个足够具体、且只需公开 OHLC 即可继续验证的 raw alpha/router：

> **同样 `1h/4h` 累计收益下，smooth / diffused path 更偏 continuation，jump-dominated path 更偏 exhaustion 或至少不该直接追。**

这满足 `keep_P1` 的最低要求，因为：
1. **对象具体**：主变量不是抽象的 attention，而是 `past return × path shape`。
2. **可继续验证**：已有最小 proxy（sign agreement / largest-bar dominance / path efficiency / jump concentration）。
3. **能产出唯一 cheap follow-up**：下一步可以直接做 portability / routing honesty 检查，看它是否真的能在 majors 上形成“smooth continuation vs jump fade”的可迁移分流，而不是仅仅重述 volatility/noise。
4. **不是完整策略壳**：目前仍缺 execution-level spec，因此不能诚实升 `P2`。

## Why not background/P0
若它仍停留在“attention 导致动量”这种解释层，我会直接打回 `background/P0`。但这次 digest 已经把它压缩成一句 desk-facing 可检验主语，并且明确了 continuation 与 fade 两端的分流含义，所以值得保留一个 survivor 名额。

## Most important caveat
当前唯一最需要后续验证的 blocker 是：
- `path smoothness` 是否只是换写法在描述低波动/低噪声趋势；
- 若控制 realized vol / move size 后信号消失，则这条线应快速收口，不应升 `P2`。

## Runtime consequence
- 新分配 `Rank 439`。
- `Fresh intake` 完成 first verdict：`keep_P1`。
- `Surviving candidate slot` 现在由 `Rank 439 / same-window cumulative return × smooth-path continuation / jump-path exhaustion router` 占用，并保留 **1 次** 最小 follow-up 预算。
