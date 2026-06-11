# Rank 428 / fib-MACD shallow pullback continuation survivor follow-up -> background/P0
- 时间：2026-04-20 01:28 UTC
- 对象：`Rank 428 / fib-MACD shallow pullback continuation (15m long-only zone1~2 fixed-bracket sleeve)`
- 轮次角色：bot3 当前 cycle_plan 第 2 项（survivor 唯一 follow-up）

## 本轮只回答的 blocker
在 survivor 已固定的唯一合法 spec——`15m long-only + shallow zone1~2 + repo 原始 1% TP / 1.5% SL + 12-bar timeout + next-bar entry`——下，这条 pocket 在最近月份厚度与最小 timeout / child-entry realism 口径里，是否仍足够值得升级到 `P2`，还是本质上只是少数 TP 命中的稀疏 bracket pocket。

## 复核口径
只复核现有事件产物 `reports/artifacts/quant_digests/2026-04-19_fibmacd_pullback_probe_events.csv`，不扩新 spec：
- 固定对象：`15m`、`long-only`、`zone1~2`
- 固定执行：`signal -> next bar open` 入场（已是最小 child-entry realism）
- 固定退出：`TP=1% / SL=1.5% / max_hold=12`
- 固定成本：`8bps` roundtrip

## 结果
筛到 survivor 固定对象后只剩 **6 笔**：

### 按月份
- `2026-02`: `n=5`，`gross_mean≈+52.86bps`，`net8≈+44.86bps`，其中 `3` 笔 TP、`2` 笔 timeout
- `2026-03`: `n=1`，`gross_mean=+100bps`，`net8=+92bps`
- `2026-04`: **`n=0`**（当前 recent month 没有新的 zone1~2 long 命中）

### 按 symbol
- 正样本只来自 `ETH/SOL/DOGE/ADA` 各 `1` 笔 TP
- `LTC` 是唯一重复样本，但 `2` 笔都以 timeout 结束，`net8≈-30.81/-20.87bps`

### timeout / exit realism
- `4` 笔 TP 都在 `<=6 bars` 内完成，说明 pocket 若成立，确实表现为很快命中的 continuation burst
- 但两笔没能快速延续的样本都直接落成 timeout 负收益；这不是“慢一点也行”的厚尾策略，而是**必须迅速续走才成立**的低频 bracket pocket
- 用更短的 `<=4 bars` 观察时，只剩 `5` 笔可解析样本，其中还有 `1` 笔尚未在更短时限内完成，进一步说明样本厚度极薄，当前不能把它当成已闭合的稳定 alpha

## 结论
**Rank 428：survivor 唯一 follow-up 已诚实收口；当前 fixed-spec pocket 仍有局部正边际，但 recent 月份厚度没有闭合，且全部可用正收益只来自 4 笔快速 TP，`2026-04` 又没有新增命中，因此它不足以升级到 `P2`，本轮直接转入 `background/P0`。**

## 为什么不是 promote_P2
1. `P2 admission` 需要至少开始回答时间稳定性 / execution realism，而当前唯一 pocket 在 fixed spec 下只有 `6` 笔，且最近月份 `2026-04` 没有新增命中，厚度不够。
2. 可用正收益几乎等价于“命中后要在前几根 bar 很快到 TP”；一旦没有快速续走，当前样本直接退化成 timeout 负值，说明它还像稀疏 bracket pocket，不像已能承接 admission 的稳健 sleeve。
3. survivor 预算只有这一次；本轮补完唯一最便宜、最能改变结论的时间稳定性 / timeout realism 检查后，仍不能把 blocker 收敛成一个值得继续前排消耗资源的单一 admission 问题。

## 本轮 verdict
- `survivor follow-up = drop_to_background`
- `Rank 428` 移出 `Surviving candidate slot`
- 保留背景证据，后续仅允许人工 reopen；不自动回前排
