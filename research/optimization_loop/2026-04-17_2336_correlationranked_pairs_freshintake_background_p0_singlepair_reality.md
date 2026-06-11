# bot3 optimization loop log — correlation-ranked pairs fresh intake 收口 background/P0

- 时间：2026-04-17 23:36 UTC
- 执行槽位：Fresh intake slot
- 对象：`research/quant_digests/2026-04-17_2226_correlationranked-ratio-zscore-pairs-alpha.md`
- 本轮动作：conditional fresh intake first-verdict
- 结论：`background/P0`

## 本轮只执行的当前小点
只处理 `cycle_plan` 中当前最前的 pending 项：
- `correlation-ranked pair admission × ratio z-score spread fade`

目标是只回答一件事：
> 在 strict pair-admission + 双腿执行 realism 的最小 honesty 补检后，它是否仍值得作为新的 pairs-family front object 进入前排？

## 读到的已知 runtime 证据
digest 已给出：
- `5m` baseline 在测试 pair 上整体费后为负；
- `1m` baseline 也大多为负；
- 唯一明显 pocket 主要集中在 `ARB/OP 1m`；
- 即使在 digest 最优参数附近，当前正值也只是 `ARB/OP 1m` 的窄 pocket，而不是可横向复制的 pairs-family 前排对象。

## 本轮补做的最小 honesty / execution realism 检查
我只补了 cycle_plan 允许的那一个最小 blocker：
- 检查 repo 主体是否真的包含 strict pair-admission + 双腿同步成交/执行壳，还是只是把 `ARB/OP 1m` 这类单一 pocket 包装成“可执行 stat-arb”。

最小源码核对结果：
1. `correlation_bot.py` 的主逻辑只是：
   - 拉两条 `1m` K 线；
   - 用最近 `30` 根 close 直接算 `price_A / price_B` ratio；
   - 对 ratio 算 z-score；
   - `z > 2` 打印 `short A / long B`，`z < -2` 打印反向提示。
2. 脚本默认每 `10s` 循环一次，但仍基于 `1m` OHLCV close；没有真正的 event-level 成交对齐与双腿同步成交验证。
3. repo 主体没有把严格 pair admission、hedge ratio、双腿同步 fill、单腿 miss、执行滑点与真实两腿 cost 壳写出来；README 里的 “Production Ready” 更像描述性说法，不是已落地的 execution realism artifact。

## 改变系统认知的结果
`correlation-ranked pair admission × ratio z-score spread fade` 在 strict pair-admission + 双腿执行 realism 下并未形成可独立排队的新 front object：当前 after-cost 价值仍主要困在单一 `ARB/OP 1m` pocket，而 repo 主体仅是 30-bar ratio z-score 提示器、缺少真实 pair admission 与双腿同步成交壳。

## verdict
- 不分配新 Rank
- 不进入 survivor
- 不升 P2
- 直接收口：`background/P0`

## 回写
- 已更新 `BOT2_BOT3_STATE.md`：
  - `Fresh intake slot`
  - `Background pool`
  - `cycle_plan item2.result/status`

## 尾注
本轮有真实推进（完成了 pending 小点并形成新 verdict），后续按流程尝试：
1. best-effort 刷新首页
2. 发送中文邮件摘要
