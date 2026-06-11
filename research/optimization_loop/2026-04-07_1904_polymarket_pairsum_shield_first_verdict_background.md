# Polymarket pair-sum shield · fresh intake first verdict = background / P0

- Time: 2026-04-07 19:04 UTC
- Target: `research/quant_digests/2026-04-07_1129_polymarket-pairsum-shield-maker-alpha.md`
- Action: fresh intake first verdict
- Verdict: `background / P0`

## 为什么这次不升 `keep_P1`
这条材料表面上把主语写成了 **`complementary-outcome sub-par spread × Binance latency shield`**，看起来像是 prediction-market 里的一条独立 relative-value 线；但和当前库里已经 intake 过的 Polymarket 家族放在一起看，它更像是 **旧的 complementary-outcome / binary mispricing / external-fast-market shield** 的一次实现细化，而不是一个足够新的 raw alpha 主语。

更具体地说：

1. **pair-sum `< 1` 本体并不新**
   - 这条线的核心仍然是：`UP + DOWN < 1` 时买入互补结果，等待到期兑付 `$1`。
   - 这本质上还是 prediction-market 里的 **binary complementary-outcome mispricing**，属于旧家族，不是新的 market structure pocket。

2. **Binance 在这里主要是 execution shield，不是新的 alpha 来源**
   - digest 自己也承认：Binance 不是方向 alpha 本体，只是在单腿成交后做撤单/保护。
   - 这说明新增内容更多是 **风险壳与执行细化**，而不是把对象推进成一个与既有 Polymarket 线正交的新主语。

3. **相对 `Rank 355`，它没有给出更强的独立性**
   - `Rank 355` 之所以能 `keep_P1`，关键在于它交易的是 **同一事件族内部相邻 horizon 的 term-structure spread**，主语独立于旧的 lag/continuation 家族。
   - 本条不是这种“新结构”；它还是围绕单一 binary 互补腿的错价与补腿风险展开。

4. **repo 默认把 `spread_capture_enabled` 关掉，反而削弱了“这是一条可独立前排保留的新主线”**
   - 这至少说明作者自己默认运行时并不优先押这条 pair-sum spread capture。
   - 在没有公开 `both-filled rate / one-leg loss / post-fee realized pocket` 证据前，把它再升成 survivor，只会重复旧 prediction-market mispricing 家族的开放式拖延。

## 这轮真正改变的系统认知
> `complementary-outcome sub-par spread × Binance latency shield` 没有提供独立于既有 Polymarket complementary-outcome / binary mispricing 家族的新 raw alpha 主语；Binance 部分主要是 execution shield，因此本轮诚实首判为 `background / P0`。

## 与已有前排对象的边界
- **不是 `Rank 355` 的同类新分支**：`Rank 355` 是 adjacent-horizon term structure relative-value；本条不是。
- **也不值得作为新的 survivor 占坑**：当前新增信息主要是 `partial_fill_timeout / cancel_time_remaining / exposure cap` 这类执行参数，而不是独立 pocket 被压清。
- **最合适的位置**：保留为 prediction-market execution/reference 素材，但不进入前排。
