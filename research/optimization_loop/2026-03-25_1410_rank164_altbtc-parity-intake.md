# 2026-03-25 14:10 UTC — Rank 164 / ALTBTC synthetic-cross parity mean reversion fresh intake

本轮只执行 `cycle_plan` 中当前第一个 pending 小点：认领 1 个新的 fresh intake，并在最小公开证据 + 本地快检口径下直接回答 `park / keep_P1`。

## 本轮认领对象
- **Rank 164 / ALTBTC synthetic-cross parity mean reversion**
- 来源底稿：`research/quant_digests/2026-03-25_1350_altbtc-synthetic-cross-parity-meanreversion.md`

## 为什么这条是合法 fresh intake
- 当前 `Paper launch queue = none`、`Active P2 = none`、`Surviving candidate = none`，前排没有更高优先级的合法执行对象。
- 该对象尚未进入当前 runtime 槽位，属于新的 raw alpha 认领。
- 它不是旧 background 候选的自动 reopen，而是基于当日新 digest 的新 intake。

## 最小公开证据
底稿已经给出完整且可独立复现的 raw-alpha 骨架：
- base alpha：`ln(ALTBTC) - ln(ALTUSDT/BTCUSDT)` 的 parity spread 偏离后回归；
- 论文地基：Mallik 2022 用 `ETHBTC` 证明这类 spread 存在显著偏离与快速回归；
- desk 化扩展：不把 headline 只读成 `ETHBTC`，而是扩成更厚尾的 `ALTBTC` universe；
- 本地公共数据快检：`DOGEBTC / ADABTC / LTCBTC` 的偏离厚度明显高于 `ETHBTC`，且后续 `1~3 bar` 回归幅度仍可见。

## 最小本地快检结论（沿用已生成的当日 artifact）
- `ETHBTC 5m/15m` 的回归依然存在，但厚度只有约 `4~5 bps` 量级，太接近成本生死线；
- `DOGEBTC 5m`：`|z|>=2` 事件平均偏离约 `73.2 bps`，后续 `3 bar` 平均回归约 `56.6 bps`；
- `ADABTC 5m`：平均偏离约 `28.9 bps`，后续 `3 bar` 平均回归约 `29.6 bps`；
- `LTCBTC 5m`：平均偏离约 `16.8 bps`，后续 `3 bar` 平均回归约 `18.0 bps`；
- 因而当前最诚实的读法不是“ETHBTC 论文可直接交易”，而是：**synthetic-cross parity 这条 raw alpha 成立，且更值得继续看厚尾 `ALTBTC` 交叉，而不是成熟主对。**

## First verdict
**`Rank 164 / ALTBTC synthetic-cross parity mean reversion = keep_P1`。**

原因：
1. 这是独立、清晰、可直接落成 entry/exit/risk/cost 的 raw alpha，不是 filter 冒充本体；
2. 已有论文地基 + 本地公共数据最小快检双重支撑；
3. 当前 evidence 已足以说明“值得给 1 次 survivor follow-up”，但还不够直接进 `P2`，因为最关键的真钱 blocker 还没被 honest 地清掉。

## 唯一需要的下一步 blocker
唯一高杠杆 blocker 是：

**三腿真实执行口径下，这条 parity 回归在 `best bid/ask + 三腿 round-trip 成本 + 残余 BTC 暴露` 后是否仍能存活。**

翻成人话：
- 现在已经知道 close-based / kline-based spread 会回；
- 但真钱能不能留住净边，关键不在“再多看几个 symbol”，而在 **order-book / quote 口径 + 三腿真实成本**；
- 所以下一手若要做，只应做这一个 decisive follow-up，而不是开放式继续补 paper/repo 摘要。

## 本轮会改变系统认知的一句话
`Rank 164 / ALTBTC synthetic-cross parity mean reversion` 不是又一条泛泛 stat-arb 想法，而是已有论文地基与本地快检支撑的 `keep_P1` fresh intake；真正决定它能否继续升级的唯一 blocker 已收敛到三腿真实执行成本生存线。
