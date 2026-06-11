# Rank 304 — EMA trend shell × OBV caution veto × ATR trailing stop first verdict = keep_P1

- 时间：2026-04-03 05:43 UTC
- 对象：`research/quant_digests/2026-04-03_0445_ema-obv-caution-atr-trend-alpha.md`
- 类型：fresh intake first verdict
- 结论：`keep_P1`
- 新分配 Rank：`304`

## 这轮只回答一个问题

这条 `EMA trend shell × OBV caution veto × ATR trailing stop`，到底是不是值得单列推进的新 raw alpha，还是只是把常见的单资产 EMA 趋势跟随、量能确认、ATR 止损这些熟悉部件重新打包。

如果它没有独立主语，就不该占新的 survivor 槽位；如果它确实提出了一个清楚、可检验的 `trend core + caution veto` 结构，就应该先保留到 `P1` 做唯一一次便宜诚实 follow-up。

## 本轮判断

我的判断是：**够独立，先给 `keep_P1`，但还没到直接 `P2`。**

关键不在于 `EMA` 本身新不新，而在于它把组件关系讲清楚了：

1. **alpha 本体是趋势延续，不是假装预测。**
   - `Close > EMA` 是方向本体；
   - `Volume > Vol_MA` 是最小流动性/确认；
   - 这部分虽然常见，但主语明确，不是东拼西凑的投票系统。

2. **真正值得 intake 的新增主语，是 `caution veto` 而不是“再加一个 filter”。**
   - digest 里最像独立贡献的部分不是均线，而是：
     - `price-up / OBV-weak` 背离时先别追；
     - `swing extension / ATR` 过热时先别追；
     - 只有当 `ADX` 足够强时才 override。
   - 这不是普通“多加个指标提高胜率”的空话，而是在回答一个更 desk 化的问题：
     **短周期趋势单最伤的不是抓不到趋势，而是追在局部拉伸末端；这个 veto 层是否能专门少做这类坏单。**

3. **它是完整策略壳，不只是 signal。**
   - entry / veto / override / sizing / trailing stop / cost stress 都在；
   - 只依赖 OHLCV 派生指标，天然适合快速下沉到 `15m / 5m` 做 clean-room；
   - 这让它不只是“可以借一个组件”，而是已经构成一条可直接 desk 化的最小母策略。

4. **它相对现有单资产 trend / breakout 家族，新增点是“追单否决层的结构化表达”。**
   - 普通趋势壳常见；
   - ATR 止损也常见；
   - 但这份对象把 `OBV divergence + stretch caution + ADX override` 明确组织成一个 `allow / veto / override` 决策层，这个结构值得单列验证，而不是直接当成旧 EMA 跟随的实现细节略过。

## 为什么现在还不给 P2

虽然对象清楚，但当前证据仍不够直接升 `P2`：

1. **现有 headline 主要来自 daily BTC walk-forward。**
   这足以说明作者在认真做 OOS，但还不等于 short-cycle desk 口径已经成立。

2. **最近一个 OOS fold 明显翻车。**
   这说明它不是稳定 production alpha，至少还需要先回答 regime / short-cycle 迁移是否成立。

3. **参数卫生存在疑点。**
   `risk_per_trade` 的打印值和搜索空间不一致，意味着 sizing 参数不能照抄；这更适合先做 clean-room 结构验证，而不是直接 admission。

## survivor follow-up 的唯一合理方向

如果下一轮给它 survivor 跟进，唯一高杠杆问题应该是：

> 在 liquid-perp `15m / 5m` 口径下，`OBV caution veto + swing/ATR stretch veto + ADX override` 是否真的改善普通 EMA 趋势壳的尾部伤害，而不是只让 trade 变少。

最小对照应是：
- baseline：`EMA trend shell`
- variant：`EMA trend shell + caution veto`

只需要重点看：
- trade count 是否下降；
- worst-decile trade loss / adverse excursion 是否改善；
- max DD 是否因 veto 层而明显收敛；
- trailing stop 是否比简单 `EMA cross-down` 更能保住 trend leg。

如果这一步答不出明确增量，它就应按 policy 收口，不再拖长。

## 本轮产出的系统认知变化

> `Rank 304 / EMA trend shell × OBV caution veto × ATR trailing stop` 的 fresh intake first verdict = `keep_P1`：它相对普通单资产 EMA trend / breakout 家族的新增主语，不是“又一个均线趋势壳”，而是把 `OBV divergence + swing/ATR stretch` 明确组织成一个专门拦截追涨末端坏单的 `caution veto` 层，并允许 `ADX` 强趋势 override；对象已具备 `15m/5m` clean-room 复现路径与完整策略壳，因此进入 survivor 槽位，等待唯一一次对 baseline EMA 壳是否真能改善尾部亏损的便宜诚实检查。
