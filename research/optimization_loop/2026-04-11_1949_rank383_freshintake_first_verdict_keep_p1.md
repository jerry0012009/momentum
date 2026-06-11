# Rank 383 fresh intake first-verdict（past-hour MAX overvaluation XS fade）

- 时间：2026-04-11 19:49 UTC
- 执行槽位：Fresh intake slot
- 对象：`research/quant_digests/2026-04-11_1258_pasthour-max-overvaluation-xs-fade-alpha.md`
- 新分配 Rank：**383**

## 本轮动作
按统一 lag1+成本口径读取该 intake 已给出的 Binance majors perp portability probe（5m/15m、top/bottom k、分档 friction）并做 first-verdict 收口。

## 关键结论（改变系统认知）
`past-hour MAX overvaluation XS fade` 在 `15m` 横截面下具备可迁移正边际（`0.25~0.5bp` 仍为正），但对摩擦极敏感；在 `1bp` taker-ish 假设下已转负，因此本轮结论为：**Rank 383 keep_P1（进入 survivor 唯一 follow-up）**。

## 唯一 decisive blocker（按要求三选一）
- **成本后净边际**：当前证据显示 edge 仅在低成本执行档可存活，尚未证明可在更保守成交假设下稳定保边。

## 槽位写回
- Fresh intake：该对象 first-verdict 完成并获得 formal Rank 383。
- Surviving candidate：接管为 `Rank 383`，后续仅允许 1 次最小、便宜、能改变层级的 follow-up。
