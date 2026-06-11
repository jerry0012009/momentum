# Rank 412 fresh intake 首判（Binance listing announcement × cross-venue catch-up）

- 时间：2026-04-15 08:18 UTC
- 执行器：bot3
- 对象：`research/quant_digests/2026-04-15_0152_binance-listing-poloniex-catchup-alpha.md`
- 轮次动作：cycle_plan #3（conditional fresh intake）

## 本轮最小执行
按当前轮要求，仅对该对象做 fresh intake 首判，口径聚焦：
1) 统一 `t+2` 成交映射与成本阶梯可行性（4/6/8bps）下是否仍可能保留可交易 pocket；
2) 事件到交易映射是否存在 delayed confirmation / replay leakage 风险。

## 结论（改变系统认知）
`Rank 412 / Binance listing announcement × cross-venue catch-up shell` 首判为 **`keep_P1`**：该对象具备可执行的事件触发骨架（公开公告触发、外部 venue 可交易腿、分钟级风控出场）且 raw alpha 机制清晰，但当前证据仍停留在工程与事件研究层，尚未给出统一 `t+2 + 4/6/8bps` 下的事件级净收益回放，因此暂不升 `P2`。

## honesty / execution realism 最小核查
- 发现的关键 realism 风险：repo 使用公告轮询触发，天然存在 detection latency；若回放用“公告发布时间”直接当可成交时点，容易高估收益。
- 本轮判定：该风险尚未被反证，故不得给 `promote_P2`。

## 唯一 survivor follow-up blocker
在统一事件样本上完成一轮 **timestamp-faithful 回放**（公告首次可见时间戳为 `t0`，入场最早 `t0+2m`，并施加 `4/6/8bps` 成本阶梯 + 最小流动性门槛），验证 `1m/3m/5m` 窗口净 alpha 是否仍为正；若不能转正则直接 `background/P0`。

## 本轮落地
- fresh intake 正式分配新 Rank：`412`
- 已回写 runtime：`cycle_plan #3` -> `done`，并写入本结论
