# Rank 187 / BTCUSDT 15m late-session path-shape swing — 第二轮 P2 admission（time stability）

- Time: 2026-03-26 19:57 UTC
- Target: `Rank 187 / BTCUSDT 15m late-session path-shape swing`
- Step type: second `P2 admission`
- Verdict: `keep_P2`

## 本轮只回答的问题
对冻结后的 canonical pocket `h32_k3`（`BTCUSDT 15m`、前 `8h` partial-day path shape、`60d lookback`、`k=3`、`predicted-max timing exit`），只回答它的 **time stability** 是否已经弱到应直接 `drop_to_background`，还是仍足够继续留在 `P2`。

## 本轮方法
只使用已冻结的 canonical trade ledger：

- `reports/artifacts/quant_digests/bitcoin_intraday_curve_shape_20260326_1633/selected_variant_trades.csv`

对 `variant = h32_k3` 的 `18` 笔交易做最小时间切片：
1. 按月份拆分 `2026-01 / 2026-02 / 2026-03`
2. 按自然周查看是否被单一周包办
3. 检查 trade 是否存在跨日重叠导致虚假聚集（结果：这 18 笔本身已天然 non-overlap）
4. 统一按 `6bps round-trip` 口径看净厚度

## 结果
### 1) 这条 edge 不是“只有一周赢钱”的假稳定
`18` 笔交易分布在 `8` 个自然周，且本身已是 non-overlap ledger，不存在同一时间段重叠堆叠把稳定性虚增的问题。

周度上，正收益并不只来自单一周：
- `2026-02-09/15`: `2` 笔，gross `+0.632%/trade`
- `2026-02-16/22`: `2` 笔，gross `+0.553%/trade`
- `2026-02-23/03-01`: `2` 笔，gross `+1.687%/trade`
- `2026-03-02/08`: `4` 笔，gross `+2.038%/trade`
- `2026-03-09/15`: `2` 笔，gross `+0.736%/trade`

说明它当然有厚薄差，但不是只靠某一天或某一周单点爆赚撑住全样本。

### 2) 但 time stability 也没有强到可直接写成“稳定 through time”
按月份拆分后，画像很清楚：

- `2026-01`: `6` 笔，gross `-1.173%/trade`，扣 `6bps` 后约 `-1.233%/trade`
- `2026-02`: `5` 笔，gross `+1.602%/trade`，扣 `6bps` 后约 `+1.542%/trade`
- `2026-03`: `7` 笔，gross `+1.051%/trade`，扣 `6bps` 后约 `+0.991%/trade`

也就是说：
- **它不是全程平滑稳定**；
- 但也 **不是一拆时间就整体坍塌**；
- 更诚实的表述是：`Rank 187` 目前呈现出“`2026-01` 弱、`2026-02` 与 `2026-03` 明显转正”的 regime-skewed 稳定性，而不是纯随机噪声。

### 3) 这足够支持继续 `keep_P2`，但不足以单凭 time stability 升 `P3`
如果本轮看到的是：
- 只有单一周在赚钱；或
- 去掉重叠后 edge 大幅塌掉；或
- `2026-02 / 2026-03` 一拆开也都翻负；

那就该直接 `drop_to_background`。

当前并不是这样。当前更像：
- `2026-01` 确实是负样本包袱；
- 但后两个月不是偶然漏出一笔，而是连续多周都还有同向正值；
- 因此它还没弱到该在这一轮被直接判死。

## 本轮之后的唯一剩余 blocker
既然 `effectiveness + cross-asset` 与 `time stability` 都已回答，下一步不该再扩 admission 轴。

当前唯一剩余 blocker 应收敛到：
- **`honesty / execution realism`**

原因是 `Rank 187` 真正决定能不能进 `P3` 的，不再是“它最近几周有没有赚钱”，而是：
- 这个 `predicted-max timing exit` 是否能被诚实地落成 paperable 的执行近似；
- 若改成更可执行的固定退出 / next-bar executable approximation，是否仍保留足够 launch-worth 的厚度。

## 本轮结论（一句话）
**Rank 187 / BTCUSDT 15m late-session path-shape swing 的第二轮 `P2 admission` 维持 `keep_P2`：canonical `h32_k3` 的 `18` 笔交易分散在 `8` 个自然周、ledger 本身已 non-overlap，虽 `2026-01` 明显为负，但 `2026-02` 与 `2026-03` 在成本后仍连续为正，因此当前 time stability 还不足以把它直接打回 background；下一轮必须收口到唯一剩余 blocker `honesty / execution realism` 做出口决策。**
