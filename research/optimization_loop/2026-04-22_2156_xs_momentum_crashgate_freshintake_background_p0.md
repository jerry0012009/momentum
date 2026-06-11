# Rankless fresh intake verdict — top-N 横截面动量 + crash gate 直接收口 background/P0

- 时间：2026-04-22 21:56 UTC
- 执行者：bot3
- 对象：`research/quant_digests/2026-04-22_0828_xs-momentum-crashgate-portability-verdict.md`
- cycle_plan 位置：1

## 本轮执行的小点
fresh intake：对 `top-N 横截面动量 + crash gate` 做 first verdict，只补 1 个最小 decisive blocker（如果 raw top-N 动量本体先天费后偏弱，crash gate 是否还配占一个独立前排对象）。

## 读取到的最小决定性证据
digest 已给出直接可执行的 raw vs raw+crash gate A/B：

- `5m`（9 币）raw：`gross -43.27%`，`net(6bps) -99.98%`，`avg_turnover 0.375/bar`
- `5m`（9 币）raw+crash：`gross -43.37%`，`net -99.98%`
- `15m`（4 币）raw：`gross -16.78%`，`net -88.16%`
- `15m`（4 币）raw+crash：与 raw 基本重合

这已经回答了唯一 blocker：问题不在 crash gate 参数，而在 `long-only top-N 动量 + 高频重排` 本体先天费后偏弱、换手过高；crash gate 触发稀疏，没把日常摩擦侵蚀修复成独立 after-cost alpha。

## 结论
`top-N 横截面动量 + crash gate` 的 fresh intake first verdict 直接收口 `background/P0`：raw 动量母体在当前 Binance 短周期最小迁移里已明显费后失效，而 crash gate A/B 几乎与 raw 重合，没有证明它相对既有 trend/momentum 家族留下可独立排队的新增 after-cost 价值；当前只保留为 shared risk/filter 提示，不进入 survivor，也不分配 Rank。

## 对 runtime 的直接影响
- `Fresh intake slot.latest_result` 更新为以上 verdict
- `cycle_plan` 第 1 小点标记为 `done`
- 不触发 `Surviving candidate / Active P2 / Paper launch queue` 迁移

## 尾部事项
若网页刷新失败，仅记为非阻断尾部失败；不回滚本轮 verdict。
