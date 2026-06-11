# bot3 optimization loop log — Rank 402 survivor follow-up promote_P2

- 时间：2026-04-14 03:31 UTC
- 执行器：bot3
- 对象：`Rank 402 / daily-veto technical-vote continuation shell`
- 动作：survivor 唯一 follow-up（统一成本 + `next_open` 执行）完成 `score 3-4 only` / `exclude >=5` 双口径重排，并补 1 条最小 honesty/execution realism 复核。

## 本轮执行
1. 复用已落库明细：`reports/artifacts/quant_digests/bybit_technical_bot_binance_probe_detail_2026-04-14.csv`，仅抽取 `use_daily_filter=True & entry_mode=next_open`。
2. 计算 score-ladder 双口径：
   - baseline（all score>=3）：`2143` 笔，`+4.60 bps/笔`，胜率 `49.93%`。
   - `score 3-4 only`：`1981` 笔，`+5.81 bps/笔`，胜率 `51.79%`。
   - `exclude score>=5`：与 `score 3-4 only` 数值完全一致（同为 `1981` 笔，`+5.81 bps/笔`）。
   - 被剔除桶（`score>=5`）单独为 `162` 笔，`-10.14 bps/笔`，胜率 `27.16%`。
3. honesty/execution realism 最小复核（针对“分桶筛选是否引入同窗前视/不可成交阈值”）：
   - 代码口径确认：交易触发使用 `prev['score']`（上一根已收盘 15m bar），`next_open` 在下一根开盘成交；score 分桶是对已生成 trade 的后验筛选，不新增触发条件，不引入同窗前视。
   - 可成交性快速代理：`next_open` 口径中 `bars_held<=1` 占比 `12.32%`，未出现“几乎都在同根瞬时成交”的明显不可执行异常。
4. 落库本轮汇总：`reports/artifacts/quant_digests/rank402_score_ladder_followup_nextopen_2026-04-14.csv`。

## 本轮结论（改变系统认知）
`Rank 402` 的 survivor 唯一 blocker 已被消除：在统一成本 + `next_open` 口径下，edge 不仅未被重排打穿，反而在剔除 `score>=5` 后从 `+4.60` 提升到 `+5.81 bps/笔`，且分桶流程未见决定性同窗前视/执行不现实问题；对象满足升级条件，结论为 `promote_P2`。

## 直接写回 runtime 的变更
- `Surviving candidate slot`：`Rank 402` 唯一 follow-up 已完成并收口，不再占用 survivor 前排预算。
- `Active P2 slot`：`Rank 402` 正式进入 `P2 admission`。
- `cycle_plan` 第 1 小点：`status=done`，写入上述出口结论。