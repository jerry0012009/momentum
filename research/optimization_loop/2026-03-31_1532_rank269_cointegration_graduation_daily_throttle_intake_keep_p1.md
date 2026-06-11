# Rank 269 — cointegration pair + graduation + daily throttle

- 时间：2026-03-31 15:32 UTC
- 执行轮次：bot3 auto 13m
- 对应 cycle item：`research/quant_digests/2026-03-31_1125_cointegration-graduation-daily-throttle-statarb.md`
- 结论：`keep_P1`
- 新分配 Rank：`269`

## 本轮只回答的事
这条 fresh intake 是否已经形成**可独立审计的 crypto pairs raw alpha 操作系统**，而不是把作者自报 live 结果或一层治理壳误写成已验证 alpha。

## 本轮判断
结论是：**进入前排，但只到 `P1`，不直升 `P2`。**

原因是它已经具备一条足够完整、可迁移、且 alpha 主体明确的 pairs/stat-arb 骨架：
1. **raw alpha 主体清楚**：核心不是 overlay，而是 `cointegration spread mean reversion`，有明确的 hedge ratio、spread、z-score、entry/exit 规则；
2. **admission layer 具体可审计**：不是空泛地说“筛 pair”，而是把 `ADF / p-value / Hurst / half-life` 与 recent expectancy graduation 写成了明确门槛；
3. **execution/risk OS 具体**：beta-normalized sizing、低流动性腿控制容量、chunked execution、daily throttle / daily stop 都是能直接迁移成实验骨架的交易语义；
4. **不是纯治理壳伪装**：graduation 与 daily guard 当然重要，但它们包裹的是一条独立存在的 spread MR alpha，而不是拿风控层冒充收益来源。

## 为什么暂不升 `P2`
它离 `P2 admission` 还差一层最便宜但 decisive 的诚实验证：
- 当前强证据主体仍是 **repo 规则 + 作者自报实盘/回测摘要**，不是 desk 自己做出的独立净边复现；
- pair formation 仍部分依赖外部维护的 pairbook / `list1.csv`，说明“哪些 pair 真能稳定毕业”这件事还没有脱离作者环境；
- after-cost 可迁移性尚未在统一 crypto 成本口径下被独立复核，因此现在直接给 `P2` 会把 blueprint 误当成已过 admission 的对象。

## 最小下一步（供 bot2 后续排班时参考，不等于本轮执行）
若要用掉它唯一 survivor follow-up，最便宜且最 decisive 的问题应是：
- 在受控 crypto perp universe 里，用小 pairbook 做 `A=raw spread MR`、`B=A+graduation`、`C=B+daily throttle` 的 clean-room replication 后，graduation 是否真的提升 after-cost 保留度，而不是只靠作者环境里的 pairbook 与 governance 壳美化结果。

## 本轮会改变系统认知的话
`cointegration pair + graduation + daily throttle` 已形成可独立审计的 crypto pairs raw alpha operating skeleton，因此作为 fresh intake 正式记为 `Rank 269` 并首判 `keep_P1`；但在完成统一成本口径下的小 pairbook clean-room replication 前，不诚实直升 `P2`。
