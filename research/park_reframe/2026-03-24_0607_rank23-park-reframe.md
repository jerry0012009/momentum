# 2026-03-24 06:07 UTC — Rank 23 park reframe

- source rank: `Rank 23 / volatility regime mid-band / cost-survival gate`
- current authoritative verdict in `docs/TODO.md`: `park / evidence pool`
- this round verdict: `keep_park`
- original park verdict kept: `yes`

## 1) 原 Rank 为什么会 park
原 Rank 23 被 park 的原因已经很清楚：它把 `realized-vol mid-band / no-high-vol-extreme` 写成了 **standalone vol/regime gate**，但 clean replication 并没有给出 desk 需要的诚实 uplift。

关键原始证据（`2026-03-17_0503_rank23-clean-replication-park.md`）：
- 主变体 `rv_midband_q20_80` 在 `BTC/ETH/SOL 120d 15m`、`6bps/side` 下仍约 `mean_total_return=-33.33%`、`positive_asset_ratio=0/3`；
- 时间稳定性 `0/3` 正 bucket；
- 参数邻域最佳近邻也仍明显为负；
- 成本继续上升时只会更差，没有真正的 `cost survival`。

所以原 rank 被否掉的不是“波动状态永远没信息”，而是：**把它写成一条可独立扛 15m 入场质量的 standalone gate，不成立。**

## 2) 它更像 hard park 还是 soft park
我仍把它判成 **soft park**。

原因：
- `vol / regime / tradeability` 这个主题本身没死；
- 原失败更像“角色放错了层级”，不是主题彻底归零；
- 但它的残余信息量也不够厚，不能因为有一点 regime 直觉就改写原 `park`。

## 3) 有没有“可救信号”
有，但这次的新信号更清楚地说明：**可救的不是 Rank 23 原来的 shared vol gate 读法，而是更偏 breakout-short 的 asymmetric follow-up 读法。**

本轮新增旁证：
- `research/quant_digests/2026-03-23_0349_intraday-vol-commonality-asymmetric-followup-gate.md`

它给出的核心信息不是“所有 setup 都该看波动共振再放行”，而是：
- 跨币 `intraday volatility commonality` 更像 **breakout-short follow-up 的偏空侧过滤/放行层**；
- 对 Fib / EMA / PSAR long 侧只够当轻量 size-down / veto 参考；
- 它更像 setup-specific、方向不对称的后续判决层，而不是 Rank 23 原来想象的 shared allow/deny gate。

翻成人话：
- 新证据说明“波动信息还有用”；
- 但用法已经偏离 Rank 23 原设定；
- 它更像 breakout-short 主线该吸收的一小层 follow-up verdict，而不是值得把 Rank 23 单独改写成 `23b` 的新 family。

## 4) 最值得改的唯一一刀是什么
如果只保留一刀，最诚实的唯一修改轴会是：

**把 `shared realized-vol mid-band gate` 进一步收窄成 `intraday volatility commonality` 的 breakout-short asymmetric follow-up filter。**

但问题在于：
- 这已经不太像在“救 Rank 23”；
- 更像把波动主题并入 breakout-short 的现有 follow-up / final-verdict 主线；
- 一旦把它写成 `23b`，很容易和 Rank 23 原来的 `shared regime gate` 审计对象发生角色漂移。

因此，这一刀虽然是本轮最清楚的新线索，但**不适合以 `Rank 23b` 的形式单独派生**。

## 5) 是否值得形成新的 derived hypothesis
**不值得。**

原因：
1. 原 `park` 审计对象是 `shared vol/regime gate`；
2. 新证据给出的残余价值却是 `breakout-short asymmetric follow-up filter`；
3. 这条线更像应被 breakout-short 主线吸收，而不是继续在 Rank 23 名下派生新支线；
4. 若硬写 `23b`，会把“保留原 park verdict”这件事弄模糊。

## 6) 本轮固定问题回答
1. **原 rank 为什么 park？**
   - 因为 `rv_midband` 只是少亏，不是转正；跨资产、时间、参数、成本四个角度都不够诚实。
2. **它更像 hard park 还是 soft park？**
   - `soft park`。
3. **有没有可救信号？**
   - 有；`intraday volatility commonality` 说明波动信息还能服务 breakout-short 的 asymmetric follow-up。
4. **最值得改的唯一一刀是什么？**
   - 把 shared vol gate 收窄成 breakout-short 的 asymmetric follow-up filter。
5. **是否值得形成新的 derived hypothesis？**
   - 不值得；因为这条线已经更像 breakout-short 主线内的 follow-up 层，而不是 Rank 23 的独立派生。

## 7) 本轮结论
- 原 `park` verdict 保留；
- Rank 23 仍更像 **soft park**，不是 hard park；
- 新证据没有把它救成 `23b`；
- 本轮最终结论：`keep_park`。

## 8) 对 queue 的最小写回口径
- 只补 `recently reviewed` 记录；
- 不新增 `Rank 23b`；
- 不改 `docs/TODO.md` 顶部排班。

## 9) 相关证据锚点
- `research/optimization_loop/2026-03-17_0503_rank23-clean-replication-park.md`
- `research/park_reframe/2026-03-20_0942_rank23-park-reframe.md`
- `research/quant_digests/2026-03-23_0349_intraday-vol-commonality-asymmetric-followup-gate.md`

## 10) Git / 提交
- 本轮只做最小必要文件改动。
- 未做 commit；原因是当前工作区仍有大量与本轮无关的脏文件，当前不适合安全 selective commit。
