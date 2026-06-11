# yeshunyi/crypto-momentum-strategy fresh intake

- Time: 2026-03-24 15:40 UTC
- Slot: Fresh intake
- Target: `yeshunyi/crypto-momentum-strategy`
- Source: <https://github.com/yeshunyi/crypto-momentum-strategy>

## What it claims
- 这是一个面向短线加密币的“涨速 + 成交量 + 板块轮动 + 社交媒体”动量策略工程骨架。
- README 给出了很多交易规则描述：动态阈值、两段入场、ATR 止盈、固定止损、黑名单、冰山单等。
- 项目更新日期较近（GitHub 页面显示 2025-04-28 更新），但公开可读材料主要还是 README 层面的策略宣称。

## What is actually evidenced
- 能确认的只有：仓库确实想搭一个自动化短线动量交易程序，README 列出了模块名、配置项和运行入口。
- 公开材料**没有**给出可核验的成本后回测结果、样本区间、资产覆盖范围、交易频率统计、滑点/手续费设定。
- README 虽然提到“会生成绩效报告、年化收益率、最大回撤、夏普比率”等，但没有附任何真实输出样例或 artifact。
- 执行真实性也不够：虽然写了 dry_run / test_mode / iceberg / limit / 条件单等设定，但没有 clean-room 证明这些执行假设在实际数据/撮合约束下成立。
- 信号层同时揉入价格、成交量、板块轮动、社交媒体，属于高自由度配方；如果没有明确样本边界和失败期表现，很容易停留在“看起来很完整”的策略叙事。

## Intake verdict
`yeshunyi/crypto-momentum-strategy` 完成 fresh intake 后 direct park：当前只能确认它是一个短线动量交易骨架与规则宣称集合，缺少成本后绩效、clean-room 样本边界和超短周期执行真实性证据，不进入 surviving follow-up。
