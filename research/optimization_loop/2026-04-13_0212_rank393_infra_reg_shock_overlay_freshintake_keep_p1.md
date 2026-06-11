# Rank 393 — infra vs regulatory shock volatility overlay（fresh intake first verdict）

- 时间：2026-04-13 02:12 UTC
- 执行槽位：Fresh intake slot
- 输入对象：`research/quant_digests/2026-04-13_0156_infra-vs-reg-shock-voloverlay.md`
- 本轮结论：`keep_P1`（分配正式 `Rank 393`）

## first verdict（最小二分）
- `infrastructure-vs-regulatory shock volatility overlay` **不是独立可交易 raw alpha**；其可交付形态是 event-type-aware 风控接线层（veto / size-down / gross scaler）。
- 该对象仍值得进入前排继续 desk 接线：它可直接作用于现有 `MR/pairs/carry`（infra 负面事件优先 veto）与 `trend/breakout`（保留但降仓）两类书，属于可执行 overlay，而非纯叙述。

## 最小 honesty / execution realism 子检查
- 检查点：事件 `t0` 是否可事前定义，避免用“事后确认时间”制造标签泄漏。
- 本轮判定：当前材料能支持“用首个公开可机读来源（交易所公告/监管通告/主流快讯首发时间）定义 `t0`”的可执行方向，但**尚未冻结唯一事件字典与首发源优先级**。

## 唯一 decisive blocker（进入下一步前必须收口）
- **blocker：`event_t0_governance` 未冻结。**
- 若不先锁定“允许的数据源、首发时间取值规则、修订回填禁令”，overlay 的效果评估会暴露在事后标签漂移，无法给出可审计的 execution-realism 结论。

## 对 runtime 的层级影响
- fresh intake 首判为 `keep_P1`，已按规则分配下一个未使用正式编号：`Rank 393`。
- 该对象进入 `Surviving candidate slot`，后续仅允许 1 次最小 follow-up，用于收口上述单一 blocker。
