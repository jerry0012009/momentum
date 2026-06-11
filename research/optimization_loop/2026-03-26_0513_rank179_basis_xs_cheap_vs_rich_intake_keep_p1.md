# Rank 179 / basis-xs-cheap-vs-rich-alpha — fresh intake 首判（keep_P1）

- Time: 2026-03-26 05:13 UTC
- Target: `research/quant_digests/2026-03-26_0321_basis-xs-cheap-vs-rich-alpha.md`
- Slot before action: `Fresh intake slot`
- Verdict: `keep_P1` → 进入 `Surviving candidate slot`
- Assigned Rank: `179`

## 本轮只回答的一句话
`long cheap basis / short rich basis` 这条横截面 carry / relative-value 骨架值得保留到 survivor，因为论文摘要与 desk 最小快检都同向支持它是一个可独立成策的 basis 本体；但当前证据仍主要停留在 `perp premium proxy`、短样本与粗成本口径，暂不足以直接升到 `P2`。

## 为什么这次首判是 keep_P1，而不是直接 park
1. **alpha 本体足够明确**
   - 不是把 basis 再降格成 breakout / crowding 的附属 filter。
   - 当前真正被保留的对象就是：按横截面 basis 排名，做 `long cheap basis / short rich basis` 的 market-neutral spread。

2. **paper side 与 desk side 至少方向一致**
   - 论文摘要明确把 basis 放在比 momentum 更强的位置，且更像 daily 级别而不是拖到 monthly 的长周期故事。
   - digest 内本地快检在 Binance perp `premiumIndex` proxy 上，也给出同方向结果：`16-bar signal + 32-bar hold` 的 non-overlap gross 约 `+14.36 bps/trade`，胜率约 `60.9%`。

3. **它已经是完整策略骨架，不是只有叙事**
   - entry：basis 排名
   - expression：bottom-2 vs top-2 等权 spread
   - hold：当前更像 `4h signal / 8h hold`
   - overlay：funding / OI / beta-neutral 都可以作为后续 admission 检查，而不是先把 alpha 本体混掉

## 为什么这次还不直接升 P2
- 当前最强证据仍来自 **15.6 天、8 币池、perp premium proxy** 的短样本快检；这足够回答“值不值得保留一次”，但还不足以回答 admission。
- 成本生存线并不宽：若组合 round-trip 成本接近 `12 bps`，净边只剩大约 `+2.36 bps`；若到 `16 bps` 就会翻负。
- 还没完成最关键的诚实 follow-up：
  1. `perp premium proxy` 与更接近真 basis 的口径是否同号；
  2. sign stability 是否稳，不是短样本偶然翻对；
  3. beta-neutral / sector-neutral 后净边是否仍在；
  4. 持有期到底是 `4h~8h carry spread` 还是被重叠样本放大的假厚边。

## 对 runtime 的直接影响
- 新对象获得正式 durable identity：`Rank 179`
- `Fresh intake slot` 本轮首判完成
- `Surviving candidate slot` 切换为 `Rank 179 / basis-xs-cheap-vs-rich-alpha`
- 后续唯一合法 follow-up 应继续围绕：
  - `long cheap basis / short rich basis` 这条 cross-sectional carry / relative-value 骨架
  - 重点验证这是不是 proxy / 短样本 / 粗成本下看起来成立，而不是已经足够 admission 的厚净边

## 单句结果（供 state / cycle_plan 回写）
`Rank 179 / basis-xs-cheap-vs-rich-alpha` 首判为 `keep_P1`：值得保留的是 `long cheap basis / short rich basis` 这条横截面 carry / relative-value 骨架，而不是继续把 basis 降格成别的策略拥挤 gate。