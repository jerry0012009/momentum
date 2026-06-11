# Rank 367 / post-cost funding+basis dislocation × delta-neutral carry admission — fresh intake first verdict = keep_P1

- 时间：2026-04-09 23:23 UTC
- 对象：`research/quant_digests/2026-04-09_2146_postcost-funding-basis-deltaneutral-alpha.md`
- 轮次角色：bot3 当前轮 `fresh intake` first verdict
- 结论：`keep_P1`
- 正式 Rank：`367`

## 本轮要回答的唯一问题
这条 `post-cost funding+basis dislocation × delta-neutral carry admission`，在最小可执行口径下是否已经保住一个独立的 carry/admission pocket；还是它其实只是把 funding carry 叙事包装得更完整，但一落到 borrow、spot 腿与延迟执行就失真。

## 本轮做了什么最小 honesty / execution 检查
- 重读 digest，确认对象主语不是“用 LSTM 预测价格”，而是 `future_net_return_bps` 这个 **post-cost delta-neutral carry 机会质量标签**。
- 直接核对 repo 的外部文档：
  - `docs/labels.md` 明确把标签写成 `short perp + long spot` 的未来净收益，并写明 `execution_delay_bars = 1`、默认 `next bar open` 入场，避免 same-bar leakage。
  - 同一份文档也明确承认 `long_perp_short_spot` 这一侧要等 borrow 假设更完整后再用，说明 repo 自己没有把最脆弱那半边偷偷当成已解决。
  - `configs/backtests/default.yaml` 的成本项写了 `5bps taker + 3bps slippage + gas`，配合 labels 文档里的四腿成本，至少没有把 spot/perp 四腿摩擦藏掉。

## 本轮新结论
`Rank 367` 值得保留为 `keep_P1`。

关键不是因为它已经 admission passed，而是因为当前最便宜、最能改判的 honesty 检查并没有击穿它：

1. **borrow 不是当前默认主语的单一 decisive blocker**
   - repo 的默认方向是 `short perp + long spot`；
   - 文档还明确写出 `long_perp_short_spot` 要等 borrow 建模更完整后再启用；
   - 这说明作者至少把最容易失真的那一侧单独隔离了，而不是把不可借的 spot short 当成默认可做。

2. **spot-leg / delayed-confirmation realism 被显式写进标签，而不是事后补丁**
   - 特征在 `t` 时点可见；
   - 交易在 `t+1` 的下根开盘执行；
   - 收益标签直接扣掉四腿摩擦、gas 与可选 borrow；
   - 所以它当前更像“机会质量预测 / admission layer”，而不是偷看同 bar 的裸方向模型。

3. **独立增量成立，但还没到 P2**
   - 这条对象的独立主语是：`funding + basis` 是否在 **成本后** 仍保留足够大的 delta-neutral carry 净边际；
   - 这和旧的“funding 高就空”“basis 宽就等回归”不同，因为它把 `是否值得做` 直接写成了净收益标签；
   - 但它目前仍主要停在 `BTCUSDT × 1h × 单市场原型`，还没把 cross-asset / time stability / parameter stability 压成 desk 当前口径的 admission 结论，因此这轮最诚实层级是 `keep_P1`，不是直接升 `P2`。

## 为什么不是 background / P0
如果最小 honesty 检查发现：
- 默认方向其实依赖难以持续获得的现货借券；或
- 标签仍在 same-bar 偷看；或
- 所谓 net return 根本没把 spot/perp 四腿成本扣进去，
那它就该直接回 `background / P0`。

但当前读到的 repo 文档恰好相反：
- 延迟执行是显式的；
- 四腿成本是显式的；
- borrow 风险最大的反向腿被明确标注为“暂不默认使用”。

这不足以让它 admission passed，却足以说明它不是一句空泛 carry 故事，值得保留到唯一一次 survivor follow-up。

## 唯一 survivor follow-up 应该补什么
下一步不该再重复争论“这个 repo 写得诚不诚实”。

唯一高杠杆 follow-up 应该直接检查：
- 在 `BTC / ETH / SOL` 或至少 majors basket 上，
- 用 `15m / 1h` 的 decision cadence，
- 对照 `always-on carry` 与简单 `funding>threshold & basis_z>threshold` baseline，
- 这套 `future_net_return_bps / tradeable label` admission 层是否真的提高 `post-cost bps/trade` 与 `tradeable rate`，而不是只把 BTC 单资产课程项目包装得更完整。

## 对 runtime 的直接影响
- 分配新正式 `Rank 367`
- 当前 fresh intake first verdict = `keep_P1`
- 进入 `Surviving candidate slot`
- `followup_budget_remaining = 1`

## 一句话结果（写回 state 用）
`Rank 367` 完成 fresh intake first verdict：repo 已把默认可执行主语收窄为 `short perp + long spot`，并显式写出 next-bar delayed execution 与四腿 post-cost net-return 标签，当前最小 honesty 检查未出现单一 decisive blocker，因此对象保留为 `keep_P1` 并进入唯一 survivor follow-up。