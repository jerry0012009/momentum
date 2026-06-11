# Rank 303 — realized-skewness cross-section fade first verdict = keep_P1

- 时间：2026-04-03 04:50 UTC
- 对象：`research/quant_digests/2026-04-03_0254_realized-skewness-xs-reversal-alpha.md`
- 类型：fresh intake first verdict
- 结论：`keep_P1`
- 新分配 Rank：`303`

## 这轮只回答一个问题

这条 `realized-skewness cross-section fade`，是否足够独立于现有的：
- `past-hour MAX / lottery-fade`
- 普通 `lagged-return XS reversal`
- 通用 `market-maker style short-term reversal`

如果只是旧 reversal / lottery 壳换皮，就不该占新的 survivor 槽位；如果它确实提供了新的 raw-alpha 主语，就应保留到 `P1` 做唯一一次便宜诚实 follow-up。

## 本轮判断

我的判断是：**够独立，先给 `keep_P1`，但还没到直接 `P2`。**

原因不是“skewness 听起来高级”，而是它和现有家族的核心统计对象不同：

1. **它不是 `MAX` 的简单重命名。**
   - `MAX` 盯的是单根极端上冲；
   - `realized skewness` 盯的是整段 return 分布右尾是否系统性更肥。
   - 因此它不是“最近有没有一根梦幻长阳”的同义句，而是“最近这段走势是不是整体更彩票化”的更平滑代理。

2. **它也不是普通 `lagged-return reversal` 的直接平移。**
   - `lagged-return` 排的是过去累计涨跌幅；
   - `realized skewness` 排的是路径分布形状。
   - 两者确实都可能指向“追涨后回吐”，但一个在看方向/幅度，另一个在看 payoff shape；digest 里也明确把最关键的后续实验写成“先做与 `ret_24h` 的相关性 / 增量 IC / 双变量回归对照”，说明它的独立性问题可被干净检验，而不是只能讲故事。

3. **它有清楚、可 desk 化的最小实验壳。**
   - `15m` 主测、`5m` 次测；
   - `4h / 8h / 24h` rolling window；
   - `long low-skew / short high-skew`；
   - top/bottom quantile、固定持有、显式成本压力测试；
   - 只依赖 OHLCV，可直接进最小 public-data 路径。

4. **它补的是“distribution-shape XS fade”这条主语，而不是再加一个 gate。**
   这点很关键。现有池里虽然已有 `lottery/MAX` 与多条 XS reversal，但还没有一条把“分布右偏 / 彩票化”明确写成 **比单根极值更平滑** 的独立 raw-alpha 主语。

## 为什么现在还不给 P2

虽然主语成立，但目前证据仍停在：
- 文献 headline + repo skeleton；
- 尚未完成对 `lagged-return` / `MAX` 的 clean-room 去重；
- 尚未验证 short-cycle 下它在 liquid perp universe 里到底是独立 alpha，还是只是旧 reversal/lottery 因子的 companion feature。

按 policy，这种状态更适合：
- **先 `keep_P1`**；
- 把唯一一次 survivor follow-up 用在最关键的去重题上：
  **`realized skewness` 对 `ret_24h` 与 `MAX` 是否仍有独立增量。**

## survivor follow-up 的唯一合理方向

若下一轮给它 survivor 跟进，最应该做的是一件事：

> 在 liquid perp `15m` universe 上，做 `-rank(realized_skew)` vs `-rank(ret_24h)` vs `-rank(MAX)` 的 clean-room 对照，回答它到底是独立 sleeve，还是只适合作为 multi-factor 里的次级 feature。

如果这一步回答不出独立增量，就应按 policy 收口，不再拖。

## 本轮产出的系统认知变化

> `Rank 303 / realized-skewness cross-section fade` 的 fresh intake first verdict = `keep_P1`：它与现有 `MAX`/普通 `lagged-return reversal` 的区别在于，主语是“整段收益分布右偏/彩票化”的横截面回吐，而不是单根极值或累计涨跌幅；`15m` 优先的最小实验壳与 public-data 复现路径都已清楚，因此进入 survivor 槽位，等待唯一一次对 `ret_24h` 与 `MAX` 去重的 clean-room follow-up。
