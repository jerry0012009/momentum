# Rank 280 — StandX OBI fair-value shift × inventory skew × min-spread floor — fresh intake first verdict = keep_P1

- 时间：2026-04-01 12:13 UTC
- 执行轮次：bot3 13m auto loop
- 对象：`research/quant_digests/2026-04-01_0556_standx-obi-maker-liquidity-provision-alpha.md`
- 槽位：Fresh intake
- 结论：`Rank 280` / `keep_P1`

## 本轮真正改变系统认知的话
`OBI z-score fair-value shift × inventory skew × min-spread floor` 已形成可审计的 maker microstructure raw alpha skeleton，因此本轮正式记为 `Rank 280` 并首判 `keep_P1`；但当前证据仍停留在 repo source audit，尚未脱离 venue-specific queue/fill / latency 假设，必须先完成公共 L2 quote-placement A/B 与 conservative fill/markout replication，才有资格谈 `P2`。

## 为什么这条线够保留到 P1
这条线不是空泛的“做市基础设施叙事”，而是已经把可审计对象收口得比较清楚：
1. **base alpha 清楚**：`OBI` rolling z-score 不是用来装饰做市框架，而是直接把 quote center 从 `mid` 推到 `fair_price = mid + c1 * alpha`；真正要验证的是“围绕 OBI-shifted fair value 挂单”是否比“围绕 raw mid 挂单”更少吃 adverse selection。
2. **执行壳也清楚**：`inventory skew`、`min_half_spread_bps`、`maker/taker fee`、`latency_ns`、`gap flatten` 都被明确写成策略边界，而不是事后补的风险说明。
3. **transfer path 清楚**：最小诚实复验不需要先复刻整个 StandX 场地，只需要在 `BTCUSDT` 这类主流 perp 上拿公共 `L2 + trades`，做 `raw-mid` vs `OBI-shifted fair value` 的 quote-placement A/B，并优先看 `post-fill 1s/5s markout` 与 conservative fill 下的净改善。
4. **它回答的是 maker alpha 是否存在**，不是“做市系统能不能跑起来”；因此目前更像一条值得保留的一次前排候选，而不是应该直接丢回 background 的纯基础设施壳。

## 为什么现在还绝不能直升 P2
还差的不是措辞，而是最关键的一道 honesty / execution 关：
1. **没有独立本地 PnL 复核**。当前材料主要来自 repo source audit，还没有本项目口径下的 clean-room replication。
2. **queue / fill / cancel latency 风险过大**。这类策略最容易把回放成交想得太乐观；只要离开 venue-specific queue model，edge 可能大幅收缩。
3. **latency 假设仍偏乐观**。repo 里的 `1ms` / `100ms step` 更像理想研究环境，不应直接偷渡成本项目的部署现实。
4. **真实 first follow-up 必须更窄**：只回答“OBI-shifted quote 是否比 raw-mid quote 在公共 L2 上留下更好的 markout / 更少 adverse selection，并在 conservative fill 下仍可能过线”，而不是继续沉迷完整做市框架、Optuna 参数或 venue 细节。

## 合法的下一次且仅一次 survivor follow-up
若后续继续这条线，唯一高杠杆 follow-up 应直接回答：
- 在 `Binance / Bybit` 公共 `L2 + trades` 上，
- 固定 `looking_depth / spread floor / skew` 的小网格，
- 用 conservative fill / cancel 口径比较 `raw-mid` 与 `OBI-shifted fair value` 两套 maker quote，
- 先看 `post-fill 1s/5s markout` 与 adverse-selection 改善，再看是否留下不依赖 rebate / 乐观 queue model 的 after-cost pocket。

若这一步只能在乐观 fill 假设下成立，就应诚实回 `background/P0`；若即使保守口径也能稳定改善 markout，再考虑升 `P2`。

## 运行槽位含义
为了保持前排槽位合法：
- 本轮新 intake 获得正式 `Rank 280` 后，占据新的 survivor 合法身份；
- `Rank 279` 因唯一 survivor follow-up 已用尽且当前停在数据前置条件 blocked，不应继续占用 survivor 前排，后续只应在人工明确 `reopen` 时回到前排。

## 操作性备注
本轮研究结论、日志与 runtime state 已可回写；但若当前会话无法调用 shell / python 执行器，则首页刷新脚本与邮件脚本需要在具备可用 exec 的运行面再次执行。
